#!/usr/bin/env bash
# Rebuild the CV PDF from _cv/cv.html using headless Chrome.
set -euo pipefail
cd "$(dirname "$0")/.."
google-chrome --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=10000 \
  --print-to-pdf=assets/Documents/Paudel_Priyanka_CV.pdf \
  "file://$PWD/_cv/cv.html"
echo "Wrote assets/Documents/Paudel_Priyanka_CV.pdf"
