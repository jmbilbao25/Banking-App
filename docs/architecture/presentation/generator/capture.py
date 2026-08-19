"""
Walk the REAL end-to-end QR payment flow against both locally-running Flask apps
and capture screenshots for the system design deck.

Two separate browser contexts are used deliberately: in the real flow the checkout
page is on a desktop and the QR is scanned by a phone, so the bank session and the
merchant session live in different cookie jars. (It also avoids the two apps
clobbering each other's `session` cookie, which they would do on a shared host.)
"""
import json
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ECOM = "http://127.0.0.1:5000"
BANK = "http://127.0.0.1:5001"
OUT = Path("/projects/sandbox/deckbuild/shots")
OUT.mkdir(parents=True, exist_ok=True)

SCALE = 2


def shot(page, name, full=False):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=full)
    print(f"  captured {name}.png")


def api(path):
    with urllib.request.urlopen(f"{ECOM}{path}") as r:
        return json.load(r)


def new_order(page, products):
    """Drive the UI to create a fresh PENDING order; return (order_id, payment_url)."""
    for pid in products:
        page.goto(f"{ECOM}/cart/add/{pid}", wait_until="networkidle")
    page.goto(f"{ECOM}/checkout/create", wait_until="networkidle")
    order_id = page.url.rstrip("/").split("/")[-1]
    o = api(f"/api/orders/{order_id}")
    payment_url = (
        f"{BANK}/pay?order_id={order_id}&amount={o['total']}"
        f"&merchant_account=techstart-grocery&expires={o['expires_at']}"
    )
    return order_id, payment_url, o["total"]


def login(page, account_id="bob-consumer"):
    page.fill('input[name="account_id"]', account_id)
    page.fill('input[name="password"]', "password123")
    page.click('button[type="submit"], input[type="submit"]')
    page.wait_for_load_state("networkidle")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ── Context 1: shopper's desktop (merchant site) ──────────────────────
        desktop = browser.new_context(
            viewport={"width": 1280, "height": 900}, device_scale_factor=SCALE
        )
        store = desktop.new_page()

        # tall page for the checkout view so the whole QR card is in frame
        tall = desktop.new_page()
        tall.set_viewport_size({"width": 1180, "height": 1320})

        # ── Context 2: payer's phone (bank app) ───────────────────────────────
        phone = browser.new_context(
            viewport={"width": 1180, "height": 900}, device_scale_factor=SCALE
        )

        print("[1] Merchant catalog")
        store.goto(f"{ECOM}/", wait_until="networkidle")
        shot(store, "01-ecom-store")

        print("[2] Basket")
        for pid in ("p1", "p1", "p2", "p5"):
            store.goto(f"{ECOM}/cart/add/{pid}", wait_until="networkidle")
        store.goto(f"{ECOM}/cart", wait_until="networkidle")
        shot(store, "02-ecom-cart")

        print("[3] Order + QR presentment")
        store.goto(f"{ECOM}/checkout/create", wait_until="networkidle")
        order_id = store.url.rstrip("/").split("/")[-1]
        o = api(f"/api/orders/{order_id}")
        payment_url = (
            f"{BANK}/pay?order_id={order_id}&amount={o['total']}"
            f"&merchant_account=techstart-grocery&expires={o['expires_at']}"
        )
        print(f"    order_id={order_id} total={o['total']}")
        print(f"    QR payload = {payment_url}")
        tall.goto(f"{ECOM}/checkout/{order_id}", wait_until="networkidle")
        tall.wait_for_timeout(1200)
        shot(tall, "03-ecom-checkout-qr")

        print("[4] Scan -> bank login redirect")
        bank = phone.new_page()
        bank.goto(payment_url, wait_until="networkidle")
        assert "/login" in bank.url, f"expected /login, got {bank.url}"
        shot(bank, "04-bank-login")

        print("[5] Payment form")
        login(bank)
        assert "/pay" in bank.url, f"expected /pay, got {bank.url}"
        shot(bank, "05-bank-pay-form")
        amt = bank.eval_on_selector(
            'input[name="amount"]', "el => ({value: el.value, type: el.type})"
        )
        print(f"    hidden amount field = {amt}")

        print("[6] Balances before")
        acct = phone.new_page()
        acct.goto(f"{BANK}/accounts", wait_until="networkidle")
        shot(acct, "06-bank-accounts-before")

        print("[7] Settle")
        bank.click('button[type="submit"], input[type="submit"]')
        bank.wait_for_load_state("networkidle")
        shot(bank, "07-bank-success")

        print("[8] Merchant tab flips to PAID via 2s poll")
        tall.wait_for_timeout(3500)
        shot(tall, "08-ecom-checkout-paid")

        print("[9] Balances after")
        acct.goto(f"{BANK}/accounts", wait_until="networkidle")
        shot(acct, "09-bank-accounts-after")

        print("[10] Replay same QR -> duplicate guard")
        replay = phone.new_page()
        replay.goto(payment_url, wait_until="networkidle")
        shot(replay, "10-bank-replay-blocked")

        print("[11] Order history / reporting view")
        store.goto(f"{ECOM}/transactions", wait_until="networkidle")
        shot(store, "11-ecom-order-history")

        print("[12] Health endpoints used by the container probes")
        hp = phone.new_page()
        hp.goto(f"{BANK}/health", wait_until="networkidle")
        shot(hp, "12-bank-health")

        browser.close()

    print("\nAll screenshots written to", OUT)


if __name__ == "__main__":
    sys.exit(main())
