#!/usr/bin/env python3
"""
Check cross-references in inf/ documentation files.

Verifies that:
- Referenced files exist
- Internal links are valid
- File paths are correct
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def find_file_references(content: str, base_dir: Path) -> List[Tuple[int, str, str]]:
    """
    Find file references in markdown content.
    
    Looks for patterns like:
    - `inf/workflows.md` (backticked)
    - `quarto/_quarto.yml` (backticked)
    - `sessions/NN_topic/NN_topic.qmd` (backticked)
    
    Returns list of (line_number, reference, type) tuples.
    """
    references = []
    lines = content.split('\n')
    
    # Pattern for file references in backticks (more precise)
    # Matches: `path/to/file.ext` but not just filenames in text
    file_pattern = r'`([a-z_]+/[^`\s\)]+\.(?:md|yml|yaml|lua|css|qmd|bib))`'
    
    for i, line in enumerate(lines, 1):
        # Only find backticked file references with paths
        for match in re.finditer(file_pattern, line):
            ref = match.group(1)
            # Only include if it starts with known directory prefixes
            if ref.startswith(('inf/', 'quarto/', 'sessions/', '_extensions/')):
                references.append((i, ref, 'backtick'))
    
    return references


def check_reference_exists(reference: str, base_dir: Path, inf_dir: Path, quarto_dir: Path) -> Tuple[bool, Optional[Path]]:
    """
    Check if a referenced file exists.
    
    Returns (exists, resolved_path) tuple.
    """
    # Resolve path based on reference type
    if reference.startswith('inf/'):
        # Reference to inf/ folder (outside quarto/)
        target = inf_dir / reference[4:]  # Remove 'inf/' prefix
    elif reference.startswith('quarto/'):
        # Reference to quarto/ folder
        target = quarto_dir / reference[7:]  # Remove 'quarto/' prefix
    elif reference.startswith('sessions/'):
        # Reference to sessions/ folder
        target = quarto_dir / reference
    elif reference.startswith('_extensions/'):
        # Reference to extensions
        target = quarto_dir / reference
    elif reference.startswith('../'):
        # Relative path from inf/ to quarto/
        target = inf_dir.parent / reference[3:]
    elif '/' in reference:
        # Assume it's relative to quarto/
        target = quarto_dir / reference
    else:
        # Just filename, check in same directory
        target = base_dir / reference
    
    return target.exists(), target if target.exists() else None


def check_file(file_path: Path, inf_dir: Path, quarto_dir: Path) -> Tuple[int, int]:
    """
    Check a single documentation file for cross-reference issues.
    
    Returns (num_references, num_issues) tuple.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}", file=sys.stderr)
        return 0, 0
    
    references = find_file_references(content, file_path.parent)
    num_issues = 0
    
    for line_num, ref, ref_type in references:
        exists, resolved_path = check_reference_exists(ref, file_path.parent, inf_dir, quarto_dir)
        if not exists:
            num_issues += 1
            print(f"❌ {file_path}:{line_num}: Broken reference: `{ref}`")
            if resolved_path:
                print(f"   Expected: {resolved_path}")
    
    return len(references), num_issues


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check cross-references in inf/ documentation files"
    )
    parser.add_argument(
        '--inf-dir',
        default='../inf',
        help='Path to inf/ directory (default: ../inf)'
    )
    parser.add_argument(
        '--quarto-dir',
        default='.',
        help='Path to quarto/ directory (default: .)'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Files to check (default: all .md files in inf/)'
    )
    
    args = parser.parse_args()
    
    inf_dir = Path(args.inf_dir).resolve()
    quarto_dir = Path(args.quarto_dir).resolve()
    
    if not inf_dir.exists():
        print(f"❌ inf/ directory not found: {inf_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find files to check
    if args.files:
        files_to_check = [Path(f).resolve() for f in args.files]
    else:
        files_to_check = list(inf_dir.glob('*.md'))
    
    if not files_to_check:
        print("No files to check", file=sys.stderr)
        sys.exit(1)
    
    total_references = 0
    total_issues = 0
    
    for file_path in files_to_check:
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}", file=sys.stderr)
            continue
        
        num_refs, num_issues = check_file(file_path, inf_dir, quarto_dir)
        total_references += num_refs
        total_issues += num_issues
    
    print(f"\n📊 Summary: {total_references} references checked, {total_issues} broken references found")
    
    if total_issues > 0:
        sys.exit(1)
    else:
        print("✅ All cross-references are valid")
        sys.exit(0)


if __name__ == '__main__':
    main()
