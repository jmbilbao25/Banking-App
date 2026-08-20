"""Page 6 -- the tech stack, as actually built.

Deliberately the simplest page in the set: no arrows, no topology, no proposal.
Six horizontal bands, one per layer, each holding the real vendor marks for the
things that are in this repository right now. Every version shown is pinned
somewhere in the tree -- requirements.txt, the Dockerfile, docker-compose.bank.yml
or the Jenkinsfile -- so the page can be checked rather than believed.

Band colour reuses the set's taxonomy: grey is the customer's device, blue is on
the request path, purple holds state, green is off the request path.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exlib import Scene, SEM, LH, BODY, SUBTLE, INK, text_width

s = Scene("tech-stack")

# ---------------------------------------------------------------- geometry
X = 60            # left edge of every band
W = 1160          # band width
PAD = 20          # band inner padding
SLOTS = 5         # widest band holds five logos; all bands share the columns
BAND_H = 140
PITCH = 190       # band top to next band top, leaves room for the label above

# Shared column centres, so a two-logo band lines up with a five-logo one.
COL = [X + PAD + (W - 2 * PAD) / SLOTS * (i + 0.5) for i in range(SLOTS)]

ICON = 46
LABEL_W = 200

# Notes sit in the columns a band does not use, which keeps the sparse bands
# from looking half-finished and puts the detail next to what it describes.
NOTE_AFTER_3 = (760, 440)   # x, width -- for bands using three columns
NOTE_AFTER_2 = (545, 655)   # x, width -- for bands using two columns


def badge(col, band_y, icon_key, name, detail):
    """One logo with its name and one line of detail, centred in a column."""
    cx = COL[col]
    s.icon(icon_key, cx - ICON / 2, band_y + 28, ICON)
    ty = band_y + 28 + ICON + 8
    s.text(name, cx - LABEL_W / 2, ty, LABEL_W, 13, color=INK,
           align="center", role="stacklabel")
    s.text(detail, cx - LABEL_W / 2, ty + 13 * LH + 1, LABEL_W, 11,
           color=BODY, align="center", role="stacklabel")


def band(i, label, sem):
    """Band i, counting from zero. Returns its top y."""
    y = 200 + i * PITCH
    s.zone(X, y, W, BAND_H, label, sem)
    return y


def note(band_y, where, body):
    x, w = where
    s.text(body, x, band_y + 34, w, 12, color=BODY, align="left")


# ---------------------------------------------------------------- header
s.header(
    X, 50,
    "The Tech Stack",
    "What the QR banking app is actually built with today, layer by layer, "
    "with the versions pinned in the repository.",
    "TECH STACK  \u00b7  AS BUILT",
    "Technology stack diagram",
    w=W,
)

# ---------------------------------------------------------------- 1. browser
y = band(0, "In the browser", "external")
badge(0, y, "html5", "HTML5", "5 server-rendered pages")
badge(1, y, "css", "CSS", "one hand-written stylesheet")
badge(2, y, "javascript", "JavaScript", "vanilla, no framework")
note(y, NOTE_AFTER_3,
     "No SPA framework and no build step.\n"
     "Flask returns finished HTML; the CSS\n"
     "and JS are served as static files.\n"
     "\n"
     "The scan page pulls html5-qrcode from\n"
     "unpkg to read QR codes from the camera.")

# ---------------------------------------------------------------- 2. app tier
y = band(1, "Web and application tier", "platform")
badge(0, y, "python", "Python", "3.11 (slim base image)")
badge(1, y, "flask", "Flask", "3.0.3")
badge(2, y, "jinja", "Jinja2", "server-side templates")
badge(3, y, "gunicorn", "Gunicorn", "21.2.0, WSGI server")
badge(4, y, "nginx", "Nginx", "reverse proxy")

# ---------------------------------------------------------------- 3. data
y = band(2, "Data", "data")
badge(0, y, "sqlalchemy", "SQLAlchemy", "Flask-SQLAlchemy 3.1.1")
badge(1, y, "mysqllogo", "MySQL", "5.7, the real database")
badge(2, y, "sqlite", "SQLite", "local fallback")
note(y, NOTE_AFTER_3,
     "PyMySQL 1.1.0 is the driver, and the\n"
     "models define just two tables:\n"
     "Account and Transaction.\n"
     "\n"
     "Setting USE_SQLITE swaps in a local\n"
     "file, so the app runs with no server.")

# ---------------------------------------------------------------- 4. packaging
y = band(3, "Packaging and orchestration", "ops")
badge(0, y, "docker", "Docker", "python:3.11-slim base")
badge(1, y, "kubernetes", "Kubernetes", "Deployment, Service, Secret")
note(y, NOTE_AFTER_2,
     "Docker Compose brings up the app and MySQL 5.7\n"
     "together for local development.\n"
     "\n"
     "The Kubernetes manifests expect an ACR image and\n"
     "expose a LoadBalancer service. They are committed,\n"
     "but they are not how the app is deployed today.")

# ---------------------------------------------------------------- 5. delivery
y = band(4, "Build and delivery", "ops")
badge(0, y, "github", "GitHub", "jmbilbao25/Banking-App")
badge(1, y, "jenkinsci", "Jenkins", "declarative pipeline")
badge(2, y, "docker", "Docker Hub", "jmbilbao25/qr-banking-app")
note(y, NOTE_AFTER_3,
     "The pipeline builds the image, pushes\n"
     "it, deploys to the AWS dev host, curls\n"
     "that host until it answers, and only\n"
     "then deploys to Azure.\n"
     "\n"
     "Images are tagged with the short SHA.")

# ---------------------------------------------------------------- 6. hosting
y = band(5, "Where it runs", "platform")
badge(0, y, "aws", "AWS", "EC2 dev host")
badge(1, y, "azure", "Azure", "Container Instances (prod)")
note(y, NOTE_AFTER_2,
     "Dev is one EC2 instance running Docker Compose.\n"
     "\n"
     "Production is two Azure Container Instances, each\n"
     "with its own public DNS label, pointing at Azure\n"
     "Database for MySQL.")

# ---------------------------------------------------------------- legend
LEGEND_Y = 200 + 6 * PITCH - PITCH + BAND_H + 40   # 40px under the last band


def legend_h(x, y, items, *, size=12, swatch=15, gap=28):
    """Horizontal legend with wording specific to this page.

    The shared LEGEND wording is Azure-service oriented, which would be wrong
    here: Flask and Nginx are on the request path but are not Azure services.
    """
    cx = x
    for sem, label in items:
        s.rect(cx, y, swatch, swatch, sem, radius=3, sw=2)
        lw = text_width(label, size)
        s.text(label, cx + swatch + 7, y, lw + 4, size, color=SUBTLE,
               align="left", role="legendlabel")
        cx += swatch + 7 + lw + gap
    return cx


legend_h(X, LEGEND_Y, [
    ("external", "In the browser, not ours"),
    ("platform", "On the request path"),
    ("data", "Data and state"),
    ("ops", "Off the request path: build, package, deploy"),
])

s.text(
    "Every version here is pinned in the repository: requirements.txt, the "
    "Dockerfile, docker-compose.bank.yml and the Jenkinsfile.\n"
    "This page describes the app as built, not the Azure design proposed on "
    "pages 2 and 5. Logos belong to their respective owners.",
    X, LEGEND_Y + 42, W, 11, color="#94A3B8", align="left")

s.write("06-tech-stack.excalidraw")
