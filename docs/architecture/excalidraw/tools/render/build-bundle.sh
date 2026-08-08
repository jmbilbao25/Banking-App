#!/usr/bin/env bash
# Build the self-contained Excalidraw renderer used to produce PNG previews.
#
# Bundles @excalidraw/excalidraw locally and copies its real webfonts, so
# rendering does not depend on a CDN at run time and the exported text uses the
# same Nunito face the editor uses.
#
# Usage:  ./build-bundle.sh
# Then:   uv sync && uv run playwright install chromium
#         uv run python render.py ../../0*.excalidraw --scale 1
set -euo pipefail

cd "$(dirname "$0")"

command -v npm >/dev/null || { echo "npm is required (node 20+)" >&2; exit 1; }

mkdir -p build web
cd build

cat > package.json <<'JSON'
{ "name": "excalidraw-render", "private": true, "type": "module", "version": "1.0.0" }
JSON

cat > entry.js <<'JS'
import { exportToSvg } from "@excalidraw/excalidraw";
window.__exportToSvg = exportToSvg;
window.__moduleReady = true;
JS

echo "installing @excalidraw/excalidraw ..."
npm install --silent @excalidraw/excalidraw react react-dom esbuild

echo "bundling ..."
npx esbuild entry.js --bundle --format=iife --outfile=../web/bundle.js \
  --define:process.env.NODE_ENV='"production"' \
  --loader:.css=empty --loader:.woff2=empty --loader:.ttf=empty \
  --log-level=warning

echo "copying webfonts ..."
rm -rf ../web/fonts
cp -r node_modules/@excalidraw/excalidraw/dist/prod/fonts ../web/fonts

cd ..
echo "done: web/bundle.js ($(du -h web/bundle.js | cut -f1)), $(find web/fonts -name '*.woff2' | wc -l) font files"
