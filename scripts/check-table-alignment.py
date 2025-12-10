#!/usr/bin/env python3
"""
Check and optionally fix table alignment in Quarto Markdown files.

All vertical pipes (|) in tables must align across all rows for readability.
This script checks for misaligned tables and can optionally fix them.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def find_tables(content: str) -> List[Tuple[int, str, int]]:
    """
    Find all tables in markdown content.
    
    Returns list of (start_line, table_content, end_line) tuples.
    """
    lines = content.split('\n')
    tables = []
    in_table = False
    table_start = None
    table_lines = []
    
    for i, line in enumerate(lines, 1):
        # Check if line looks like a table row (contains |)
        if '|' in line and not line.strip().startswith('```'):
            if not in_table:
                in_table = True
                table_start = i
                table_lines = [line]
            else:
                table_lines.append(line)
        else:
            if in_table:
                # End of table - need at least 2 lines (header + separator)
                if len(table_lines) >= 2:
                    tables.append((table_start, '\n'.join(table_lines), i - 1))
                in_table = False
                table_lines = []
    
    # Handle table at end of file
    if in_table and len(table_lines) >= 2:
        tables.append((table_start, '\n'.join(table_lines), len(lines)))
    
    return tables


def check_table_alignment(table_content: str) -> Tuple[bool, List[str]]:
    """
    Check if all pipes in a table are aligned.
    
    Returns (is_aligned, issues) tuple.
    """
    lines = table_content.split('\n')
    if len(lines) < 2:
        return True, []
    
    # Find all pipe positions in each line
    pipe_positions = []
    for line in lines:
        positions = [m.start() for m in re.finditer(r'\|', line)]
        pipe_positions.append(positions)
    
    # Check if all lines have same number of pipes
    num_pipes = len(pipe_positions[0])
    for i, positions in enumerate(pipe_positions[1:], 1):
        if len(positions) != num_pipes:
            return False, [f"Line {i+1}: Different number of pipes ({len(positions)} vs {num_pipes})"]
    
    # Check if pipes align across rows
    issues = []
    for pipe_idx in range(num_pipes):
        expected_pos = pipe_positions[0][pipe_idx]
        for line_idx, positions in enumerate(pipe_positions[1:], 1):
            if positions[pipe_idx] != expected_pos:
                issues.append(f"Line {line_idx+1}: Pipe {pipe_idx+1} at position {positions[pipe_idx]}, expected {expected_pos}")
    
    return len(issues) == 0, issues


def fix_table_alignment(table_content: str) -> str:
    """
    Fix table alignment by aligning all pipes.
    
    This is a simplified version - full implementation would need to:
    1. Parse table cells
    2. Calculate column widths
    3. Pad cells appropriately
    4. Reconstruct table
    
    For now, this reports that manual fixing is needed.
    """
    # This is complex to implement correctly, so we'll just report
    # that manual fixing is needed for now
    return table_content


def check_file(file_path: Path, fix: bool = False) -> Tuple[int, int]:
    """
    Check a single file for table alignment issues.
    
    Returns (num_tables, num_issues) tuple.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}", file=sys.stderr)
        return 0, 0
    
    tables = find_tables(content)
    num_issues = 0
    
    for start_line, table_content, end_line in tables:
        is_aligned, issues = check_table_alignment(table_content)
        if not is_aligned:
            num_issues += 1
            print(f"❌ {file_path}:{start_line}-{end_line}: Table alignment issues:")
            for issue in issues:
                print(f"   {issue}")
            if fix:
                # For now, just report that manual fixing is needed
                print(f"   ⚠️  Manual fixing required for table alignment")
    
    return len(tables), num_issues


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check table alignment in Quarto Markdown files"
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Files to check (default: all .qmd files in sessions/)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix alignment (currently reports manual fix needed)'
    )
    parser.add_argument(
        '--sessions-dir',
        default='sessions',
        help='Directory containing session files (default: sessions)'
    )
    
    args = parser.parse_args()
    
    # Find files to check
    if args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        sessions_dir = Path(args.sessions_dir)
        if not sessions_dir.exists():
            print(f"❌ Sessions directory not found: {sessions_dir}", file=sys.stderr)
            sys.exit(1)
        files_to_check = list(sessions_dir.rglob('*.qmd'))
        # Also check includes
        includes_dir = Path('_includes')
        if includes_dir.exists():
            files_to_check.extend(includes_dir.glob('*.qmd'))
    
    if not files_to_check:
        print("No files to check", file=sys.stderr)
        sys.exit(1)
    
    total_tables = 0
    total_issues = 0
    
    for file_path in files_to_check:
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}", file=sys.stderr)
            continue
        
        num_tables, num_issues = check_file(file_path, fix=args.fix)
        total_tables += num_tables
        total_issues += num_issues
    
    print(f"\n📊 Summary: {total_tables} tables checked, {total_issues} alignment issues found")
    
    if total_issues > 0:
        print("\n💡 Tip: Align all pipes (|) across all rows for better readability")
        sys.exit(1)
    else:
        print("✅ All tables are properly aligned")
        sys.exit(0)


if __name__ == '__main__':
    main()
