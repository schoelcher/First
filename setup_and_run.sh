#!/usr/bin/env bash
# One-command setup + run for EquityScope
set -e

echo "==> Installing Python dependencies…"
pip install -r requirements.txt

echo "==> Installing Playwright Chromium…"
playwright install chromium

echo "==> Starting EquityScope…"
python run_dashboard.py
