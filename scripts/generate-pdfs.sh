#!/usr/bin/env bash
# Post-render script to generate PDF versions of RevealJS slides using decktape
# CI-only: called in GitHub Actions after `quarto render`

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_DIR="${1:-$PROJECT_ROOT/_site}"

echo "=== Generating PDFs from RevealJS slides ==="
echo "Project root: $PROJECT_ROOT"
echo "Target dir: $TARGET_DIR"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Target directory not found: $TARGET_DIR"
    exit 1
fi

cd "$TARGET_DIR"

count=0
skipped=0
for html_file in sessions/*/slides.html; do
  [ -e "$html_file" ] || continue

  dir=$(dirname "$html_file")
  pdf_file="$dir/slides.pdf"

  # Skip if PDF exists and is newer than HTML file
  if [ -f "$pdf_file" ] && [ "$pdf_file" -nt "$html_file" ]; then
    echo "⊘ Skipping: $pdf_file (already up to date)"
    skipped=$((skipped + 1))
    continue
  fi

  echo "Processing: $html_file -> $pdf_file"
  npx -y decktape reveal \
    --chrome-arg=--no-sandbox \
    --chrome-arg=--disable-setuid-sandbox \
    "$html_file" \
    "$pdf_file"

  if [ $? -eq 0 ]; then
    echo "✓ Generated: $pdf_file"
    count=$((count + 1))
  else
    echo "✗ Failed to generate: $pdf_file"
  fi
done

if [ $count -eq 0 ] && [ $skipped -eq 0 ]; then
  echo "No slides.html files found to process."
else
  echo "=== PDF generation complete: $count generated, $skipped skipped ==="
fi


