#!/usr/bin/env python3
"""
Check version consistency across files.

Verifies that extension versions match in:
- _extensions/wuqui/exclude/_extension.yml
- _extensions/wuqui/exclude/exclude.lua (in add_html_dependency)
- inf/index.md (changelog mentions)
- inf/status-summary.md (if mentioned)
"""

import re
import sys
from pathlib import Path
from typing import Optional, List, Tuple


def extract_version_from_extension_yml(file_path: Path) -> Optional[str]:
    """Extract version from _extension.yml file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        match = re.search(r'^version:\s*([0-9]+\.[0-9]+\.[0-9]+)', content, re.MULTILINE)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def extract_version_from_lua(file_path: Path) -> Optional[str]:
    """Extract version from exclude.lua add_html_dependency call."""
    try:
        content = file_path.read_text(encoding='utf-8')
        # Look for version = "X.Y.Z" in add_html_dependency
        match = re.search(r'version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def extract_versions_from_docs(file_path: Path) -> List[Tuple[int, str]]:
    """Extract version mentions from documentation files."""
    versions = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Look for version patterns: v1.4.0, version 1.4.0, 1.4.0
        version_pattern = r'\b(v?[0-9]+\.[0-9]+\.[0-9]+)\b'
        
        for i, line in enumerate(lines, 1):
            matches = re.finditer(version_pattern, line)
            for match in matches:
                version = match.group(1).lstrip('v')  # Remove 'v' prefix if present
                versions.append((i, version))
    except Exception:
        pass
    
    return versions


def check_version_consistency(quarto_dir: Path, inf_dir: Path, check_docs: bool = True) -> Tuple[bool, List[str]]:
    """
    Check version consistency across all files.
    
    Args:
        check_docs: If True, also check documentation files for version mentions
    
    Returns (is_consistent, issues) tuple.
    """
    issues = []
    
    # Check extension files
    extension_yml = quarto_dir / '_extensions/wuqui/exclude/_extension.yml'
    extension_lua = quarto_dir / '_extensions/wuqui/exclude/exclude.lua'
    
    yml_version = None
    lua_version = None
    
    if extension_yml.exists():
        yml_version = extract_version_from_extension_yml(extension_yml)
    else:
        issues.append("Extension _extension.yml not found")
    
    if extension_lua.exists():
        lua_version = extract_version_from_lua(extension_lua)
    else:
        issues.append("Extension exclude.lua not found")
    
    # Check if versions match (this is the critical check)
    if yml_version and lua_version:
        if yml_version != lua_version:
            issues.append(f"Version mismatch: _extension.yml has {yml_version}, exclude.lua has {lua_version}")
        else:
            print(f"✅ Extension versions match: {yml_version}")
    elif yml_version:
        print(f"⚠️  Found version in _extension.yml: {yml_version} (but not in exclude.lua)")
    elif lua_version:
        print(f"⚠️  Found version in exclude.lua: {lua_version} (but not in _extension.yml)")
    
    # Check documentation files (optional, for full consistency check)
    if check_docs and inf_dir.exists():
        index_md = inf_dir / 'index.md'
        status_md = inf_dir / 'status-summary.md'
        
        if index_md.exists():
            doc_versions = extract_versions_from_docs(index_md)
            if doc_versions:
                print(f"📝 Found {len(doc_versions)} version mention(s) in inf/index.md")
                # Check if any match the extension version
                if yml_version:
                    matching = [v for _, v in doc_versions if v == yml_version]
                    if not matching:
                        issues.append(f"Extension version {yml_version} not found in inf/index.md changelog")
        
        if status_md.exists():
            doc_versions = extract_versions_from_docs(status_md)
            if doc_versions:
                print(f"📝 Found {len(doc_versions)} version mention(s) in inf/status-summary.md")
    
    return len(issues) == 0, issues


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check version consistency across files"
    )
    parser.add_argument(
        '--quarto-dir',
        default='.',
        help='Path to quarto/ directory (default: .)'
    )
    parser.add_argument(
        '--inf-dir',
        default='../inf',
        help='Path to inf/ directory (default: ../inf)'
    )
    parser.add_argument(
        '--skip-docs',
        action='store_true',
        help='Skip documentation version checks (only check extension files)'
    )
    
    args = parser.parse_args()
    
    quarto_dir = Path(args.quarto_dir).resolve()
    inf_dir = Path(args.inf_dir).resolve()
    
    if not quarto_dir.exists():
        print(f"❌ Quarto directory not found: {quarto_dir}", file=sys.stderr)
        sys.exit(1)
    
    is_consistent, issues = check_version_consistency(quarto_dir, inf_dir, check_docs=not args.skip_docs)
    
    if issues:
        print("\n❌ Version consistency issues found:")
        for issue in issues:
            print(f"   {issue}")
        sys.exit(1)
    else:
        print("\n✅ All versions are consistent")
        sys.exit(0)


if __name__ == '__main__':
    main()
