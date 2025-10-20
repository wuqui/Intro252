#!/usr/bin/env bash
# Post-render script to generate PDF versions of RevealJS slides using decktape
# CI-only: called in GitHub Actions after `quarto render`

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Generating PDFs from RevealJS slides ==="
echo "Project root: $PROJECT_ROOT"

cd "$PROJECT_ROOT/_site"

count=0
for html_file in sessions/*/slides.html; do
  [ -e "$html_file" ] || continue

  dir=$(dirname "$html_file")
  pdf_file="$dir/slides.pdf"

  echo "Processing: $html_file -> $pdf_file"
  npx -y decktape reveal \
    --chrome-arg=--no-sandbox \
    --chrome-arg=--disable-setuid-sandbox \
    --fragments \
    "$html_file" \
    "$pdf_file"

  if [ $? -eq 0 ]; then
    echo "✓ Generated: $pdf_file"
    count=$((count + 1))
  else
    echo "✗ Failed to generate: $pdf_file"
  fi
done

if [ $count -eq 0 ]; then
  echo "No slides.html files found to process."
else
  echo "=== PDF generation complete: $count file(s) processed ==="
fi


