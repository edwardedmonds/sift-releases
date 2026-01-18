#!/usr/bin/env python3
"""
sift-uninstall.py - Uninstall Sift and remove Claude Code configuration

Usage: python3 sift-uninstall.py
   or: ~/.local/bin/sift-uninstall.py

============================================================================
MAINTAINER NOTE: Install methods must stay in sync!

When modifying installation logic, update ALL of these:
  1. Makefile (install/uninstall targets)
  2. scripts/sift-setup.py
  3. scripts/sift-uninstall.py
  4. sift-releases repo assets

See: .github/RELEASE_CHECKLIST.md
============================================================================
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"
INSTALL_DIR = Path.home() / ".local" / "bin"

TEMPLATES = [
    "MEMORY.md",
    "FILE_TOOLS.md",
    "SEARCH_TOOLS.md",
    "SQL_TOOLS.md",
    "WEB_TOOLS.md",
    "REPO_TOOLS.md",
    "CONTEXT_TOOLS.md",
]

HOOK_SCRIPTS = [
    "session-start.sh",
    "session-end.sh",
    "pre-compact.sh",
]


def prompt(question: str, default: str = "y") -> bool:
    """Prompt user for yes/no answer. Reads from /dev/tty for piped scripts."""
    if default == "y":
        hint = "[Y/n]"
    else:
        hint = "[y/N]"
    
    try:
        # Try to read from /dev/tty (works when script is piped)
        with open("/dev/tty", "r") as tty:
            sys.stdout.write(f"{question} {hint} ")
            sys.stdout.flush()
            answer = tty.readline().strip().lower()
    except (OSError, IOError):
        # Fallback for systems without /dev/tty (use default)
        print(f"{question} {hint} (auto: {default})")
        answer = default
    
    if not answer:
        answer = default
    
    return answer in ("y", "yes")


def load_settings() -> dict:
    """Load settings.json or return empty dict."""
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_settings(settings: dict) -> None:
    """Save settings to settings.json."""
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2) + "\n")


def remove_sift_section(filepath: Path) -> bool:
    """Remove sift template content from file.
    
    Handles two formats:
    - New: <!-- begin sift-template-X.Y.Z --> ... <!-- end sift-template-X.Y.Z -->
    - Old: <!-- sift-template-X.Y.Z --> ... <!-- SIFT_BEGIN --> ... <!-- SIFT_END -->
    """
    if not filepath.exists():
        return False
    
    content = filepath.read_text()
    removed = False
    
    # New format: <!-- begin sift-template-X.Y.Z --> ... <!-- end sift-template-X.Y.Z -->
    pattern_new = r'<!-- begin sift-template-[\d.]+ -->.*?<!-- end sift-template-[\d.]+ -->\n?'
    new_content, count = re.subn(pattern_new, '', content, flags=re.DOTALL)
    if count > 0:
        content = new_content
        removed = True
    
    # Old format: <!-- SIFT_BEGIN --> ... <!-- SIFT_END -->
    pattern_old = r'<!-- SIFT_BEGIN -->.*?<!-- SIFT_END -->\n?'
    new_content, count = re.subn(pattern_old, '', content, flags=re.DOTALL)
    if count > 0:
        content = new_content
        removed = True
    
    # Also remove standalone old version marker if present
    pattern_version = r'<!-- sift-template-[\d.]+ -->\n?'
    new_content, count = re.subn(pattern_version, '', content, flags=re.DOTALL)
    if count > 0:
        content = new_content
        removed = True
    
    if removed:
        filepath.write_text(content)
    return removed


def main():
    print("Sift Uninstaller")
    print("================")
    print()
    print("This will remove:")
    print("  - Sift binary from ~/.local/bin/")
    print("  - Sift templates from ~/.claude/")
    print("  - Sift hooks from ~/.claude/hooks/")
    print("  - Sift hook configurations from settings.json")
    print("  - Sift MCP server registration")
    print()
    print("This will NOT remove:")
    print("  - .sift/ directories (your project data)")
    print()
    
    if not prompt("Proceed with uninstall?"):
        print("Cancelled.")
        sys.exit(0)
    
    print()
    
    # Step 1: Remove binary
    print("Step 1: Remove binary")
    print("---------------------")
    
    binary = INSTALL_DIR / "sift"
    if binary.exists():
        binary.unlink()
        print(f"  ✓ Removed {binary}")
    else:
        print(f"  Binary not found at {binary}")
    
    # Remove uninstall scripts
    for script in ["sift-uninstall.sh", "sift-uninstall.py"]:
        script_path = INSTALL_DIR / script
        if script_path.exists():
            script_path.unlink()
            print(f"  ✓ Removed {script_path}")
    print()
    
    # Step 2: Remove templates
    print("Step 2: Remove templates")
    print("------------------------")
    
    for template in TEMPLATES:
        template_path = CLAUDE_DIR / template
        if template_path.exists():
            template_path.unlink()
            print(f"  ✓ Removed {template_path}")
    
    # Handle CLAUDE.md specially - only remove sift section
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    if claude_md.exists():
        if remove_sift_section(claude_md):
            print(f"  ✓ Removed sift section from {claude_md}")
        else:
            print(f"  No sift section found in {claude_md}")
    print()
    
    # Step 3: Remove hook scripts
    print("Step 3: Remove hook scripts")
    print("---------------------------")
    
    hooks_dir = CLAUDE_DIR / "hooks"
    for hook in HOOK_SCRIPTS:
        hook_path = hooks_dir / hook
        if hook_path.exists():
            hook_path.unlink()
            print(f"  ✓ Removed {hook_path}")
    print()
    
    # Step 4: Remove hook configurations
    print("Step 4: Remove hook configurations")
    print("----------------------------------")
    
    if SETTINGS_FILE.exists():
        settings = load_settings()
        removed = []
        
        if "hooks" in settings:
            for hook_type in ["SessionStart", "SessionEnd", "PreCompact"]:
                if hook_type in settings["hooks"]:
                    del settings["hooks"][hook_type]
                    removed.append(hook_type)
        
        if removed:
            save_settings(settings)
            print(f"  ✓ Removed hooks: {', '.join(removed)}")
        else:
            print("  No hook configurations found")
    else:
        print("  No settings.json found")
    print()
    
    # Step 5: Unregister MCP server
    print("Step 5: Unregister MCP server")
    print("-----------------------------")
    
    try:
        result = subprocess.run(
            ["claude", "mcp", "remove", "--scope", "user", "sift"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  ✓ Removed sift MCP server")
        elif "not found" in result.stderr.lower() or "does not exist" in result.stderr.lower():
            print("  MCP server not registered")
        else:
            print(f"  Warning: {result.stderr.strip()}")
    except FileNotFoundError:
        print("  Claude Code CLI not found, skipping MCP removal")
    except Exception as e:
        print(f"  Warning: {e}")
    print()
    
    print("Done! Sift has been uninstalled.")
    print("Your .sift/ directories have been preserved.")


if __name__ == "__main__":
    main()
