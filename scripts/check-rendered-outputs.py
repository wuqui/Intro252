#!/usr/bin/env python3
"""
Check that all expected rendered output files exist.
"""

import sys
from pathlib import Path


def main():
    """Main entry point."""
    site_dir = Path("_site")
    
    if not site_dir.exists():
        print("❌ _site directory not found. Run 'quarto render' first", file=sys.stderr)
        sys.exit(1)
    
    sessions = ['01_intro', '02_pragmatics', '03_phonetics', '04_phonology', '05_syntax', '07_morphology']
    
    all_ok = True
    
    # Check homepage
    if not (site_dir / "index.html").exists():
        print("❌ index.html not created")
        all_ok = False
    else:
        print("✅ index.html exists")
    
    # Check session files
    for session in sessions:
        website = site_dir / "sessions" / session / "website.html"
        slides = site_dir / "sessions" / session / "slides.html"
        
        if not website.exists():
            print(f"❌ Missing website.html for {session}")
            all_ok = False
        else:
            print(f"✅ {session}/website.html exists")
        
        if not slides.exists():
            print(f"⚠️  Missing slides.html for {session} (may be intentional)")
        else:
            print(f"✅ {session}/slides.html exists")
    
    if all_ok:
        print("\n✅ All output files generated")
        sys.exit(0)
    else:
        print("\n❌ Some output files are missing")
        sys.exit(1)


if __name__ == '__main__':
    main()
