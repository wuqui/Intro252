#!/bin/zsh

set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$script_dir"

# Get tree file name from argument, default to trees.tex for backward compatibility
if [ "$#" -gt 0 ] && [[ "$1" == *.tex ]]; then
  tex_file="$1"
  shift  # Remove tree file from arguments
else
  tex_file="trees.tex"
fi

output_dir="output"
tree_basename=$(basename "$tex_file" .tex)

# Create output directory if it doesn't exist
mkdir -p "${output_dir}"

# Check if tree file has fragments
if grep -qE 'visible on=[0-9]+' "$tex_file"; then
  has_fragments=1
else
  has_fragments=0
fi

if [ "$#" -gt 0 ]; then
  fragments=("$@")
  has_fragments=1  # User specified fragments, so treat as fragment mode
else
  if [ "$has_fragments" -eq 1 ]; then
    # Automatically detect all fragment numbers from the tree file
    # Extract all "visible on=X" values and find the maximum
    max_frag=$(grep -oE 'visible on=[0-9]+' "$tex_file" | grep -oE '[0-9]+' | sort -n | tail -1)
    if [ -n "$max_frag" ]; then
      # Generate array of fragments from 1 to max_frag
      fragments=($(seq 1 "$max_frag"))
    else
      fragments=()
    fi
  else
    # No fragments found - compile single PNG without number suffix
    fragments=()
  fi
fi

if [ ${#fragments[@]} -eq 0 ]; then
  # No fragments mode - compile single PNG
  echo "Building tree image from ${tex_file}"
  job="${tree_basename}"
  pdflatex -interaction=nonstopmode -halt-on-error -jobname="${job}" "${tex_file}" >/dev/null
  
  # Convert PDF to PNG using pdftoppm (preferred) or ImageMagick convert
  if command -v pdftoppm &> /dev/null; then
    pdftoppm -png -r 300 "${job}.pdf" "${job}" >/dev/null
    mv "${job}-1.png" "${output_dir}/${job}.png"
  elif command -v convert &> /dev/null; then
    convert -density 300 "${job}.pdf" -quality 100 "${output_dir}/${job}.png" >/dev/null
  else
    echo "Error: Neither pdftoppm nor ImageMagick convert found. Please install one of them."
    exit 1
  fi
  
  rm -f "${job}.aux" "${job}.log" "${job}.pdf"
  echo "Done. PNG file: ${tree_basename}.png"
else
  # Fragments mode - compile multiple PNGs with number suffixes
  echo "Building tree fragments from ${tex_file}"
  
  for frag in "${fragments[@]}"; do
    job="${tree_basename}_${frag}"
    echo "  • Fragment ${frag}"
    # Create a temporary file with the fragment definition injected
    temp_tex=$(mktemp -t "${tree_basename}_${frag}.XXXXXX")
    temp_tex="${temp_tex}.tex"
    # Replace \providecommand{\currentfragment}{999} with the actual fragment number
    sed "s/\\\\providecommand{\\\\currentfragment}{999}/\\\\def\\\\currentfragment{${frag}}/" "${tex_file}" > "${temp_tex}"
    pdflatex -interaction=nonstopmode -halt-on-error -jobname="${job}" "${temp_tex}" >/dev/null
    rm -f "${temp_tex}"
    
    # Convert PDF to PNG using pdftoppm (preferred) or ImageMagick convert
    if command -v pdftoppm &> /dev/null; then
      pdftoppm -png -r 300 "${job}.pdf" "${job}" >/dev/null
      mv "${job}-1.png" "${output_dir}/${job}.png"
    elif command -v convert &> /dev/null; then
      convert -density 300 "${job}.pdf" -quality 100 "${output_dir}/${job}.png" >/dev/null
    else
      echo "Error: Neither pdftoppm nor ImageMagick convert found. Please install one of them."
      exit 1
    fi
  done
  
  rm -f "${tree_basename}"_*.aux "${tree_basename}"_*.log "${tree_basename}"_*.pdf
  echo "Done. PNG files: ${tree_basename}_${fragments[1]}.png ... ${tree_basename}_${fragments[-1]}.png"
fi 

