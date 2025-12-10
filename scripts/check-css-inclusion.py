#!/usr/bin/env python3
"""
Check CSS inclusion in rendered Quarto output files.

Verifies that exclude-styles.css is included in all rendered HTML files.
"""

import sys
from pathlib import Path
from typing import List, Tuple


def check_css_in_file(file_path: Path, expected_css: str = "exclude-styles.css") -> Tuple[bool, int]:
    """
    Check if CSS file is included in HTML file.
    
    Returns (is_included, count) tuple.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        count = content.count(expected_css)
        return count >= 1, count
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}", file=sys.stderr)
        return False, 0


def check_session_css(site_dir: Path, session: str) -> Tuple[bool, List[str]]:
    """
    Check CSS inclusion for a session's rendered files.
    
    Returns (all_ok, issues) tuple.
    """
    issues = []
    all_ok = True
    
    website_file = site_dir / "sessions" / session / "website.html"
    slides_file = site_dir / "sessions" / session / "slides.html"
    
    if website_file.exists():
        is_included, count = check_css_in_file(website_file)
        if is_included:
            print(f"✅ {session}/website.html: CSS included ({count}x)")
        else:
            print(f"❌ {session}/website.html: CSS not found (count: {count})")
            issues.append(f"{session}/website.html: CSS missing")
            all_ok = False
    else:
        print(f"⚠️  {session}/website.html: File not found")
    
    if slides_file.exists():
        is_included, count = check_css_in_file(slides_file)
        if is_included:
            print(f"✅ {session}/slides.html: CSS included ({count}x)")
        else:
            print(f"❌ {session}/slides.html: CSS not found (count: {count})")
            issues.append(f"{session}/slides.html: CSS missing")
            all_ok = False
    else:
        print(f"ℹ️  {session}/slides.html: File not found (may be intentional)")
    
    return all_ok, issues


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check CSS inclusion in rendered Quarto output files"
    )
    parser.add_argument(
        '--site-dir',
        default='_site',
        help='Path to _site directory (default: _site)'
    )
    parser.add_argument(
        '--sessions',
        nargs='*',
        default=['01_intro', '02_pragmatics', '03_phonetics', '04_phonology', '05_syntax', '07_morphology'],
        help='Sessions to check (default: all sessions)'
    )
    
    args = parser.parse_args()
    
    site_dir = Path(args.site_dir)
    
    if not site_dir.exists():
        print(f"❌ Site directory not found: {site_dir}", file=sys.stderr)
        print(f"💡 Run 'quarto render' first to generate output files", file=sys.stderr)
        sys.exit(1)
    
    print("🎨 Checking CSS inclusion in rendered files...\n")
    
    all_sessions_ok = True
    all_issues = []
    
    for session in args.sessions:
        session_ok, issues = check_session_css(site_dir, session)
        if not session_ok:
            all_sessions_ok = False
            all_issues.extend(issues)
        print()
    
    # Check homepage
    homepage = site_dir / "index.html"
    if homepage.exists():
        is_included, count = check_css_in_file(homepage)
        if is_included:
            print(f"✅ index.html: CSS included ({count}x)")
        else:
            print(f"⚠️  index.html: CSS not found (may be intentional for homepage)")
    
    print("\n" + "="*60)
    if all_sessions_ok:
        print("✅ CSS included in all session outputs")
        sys.exit(0)
    else:
        print("❌ CSS inclusion issues found:")
        for issue in all_issues:
            print(f"   - {issue}")
        print("\n💡 Tip: Re-render affected sessions with 'quarto render'")
        sys.exit(1)


if __name__ == '__main__':
    main()
