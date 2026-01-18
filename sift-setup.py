#!/usr/bin/env python3
"""
sift-setup.py - Install Sift and configure Claude Code hooks

Usage: curl -fsSL URL/sift-setup.py | python3
   or: python3 sift-setup.py

============================================================================
MAINTAINER NOTE: Install methods must stay in sync!

When modifying installation logic, update ALL of these:
  1. Makefile (install/uninstall targets)
  2. scripts/sift-setup.sh
  3. scripts/sift-setup.py
  4. scripts/sift-uninstall.py
  5. sift-releases repo assets

See: .github/RELEASE_CHECKLIST.md
============================================================================
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = "edwardedmonds/sift-releases"
CLAUDE_DIR = Path.home() / ".claude"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"
INSTALL_DIR = Path.home() / ".local" / "bin"

TEMPLATES = [
    "CLAUDE.md",
    "MEMORY.md", 
    "FILE_TOOLS.md",
    "SEARCH_TOOLS.md",
    "SQL_TOOLS.md",
    "WEB_TOOLS.md",
    "REPO_TOOLS.md",
    "CONTEXT_TOOLS.md",
]

HOOK_SCRIPTS = {
    "session-start.sh": '''#!/bin/bash
# session-start.sh - Unified session registration
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
if [[ -n "$SESSION_ID" ]]; then
  sift --session-start "$SESSION_ID" 2>/dev/null || true
fi
''',
    "session-end.sh": '''#!/bin/bash
# session-end.sh - Mark session as ended for consolidation tracking
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
if [[ -n "$SESSION_ID" ]]; then
  sift --session-end "$SESSION_ID" 2>/dev/null || true
fi
''',
    "pre-compact.sh": '''#!/bin/bash
# pre-compact.sh - Sync transcript to context.db before compaction
INPUT=$(cat)
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty')
if [[ -n "$TRANSCRIPT" && -f "$TRANSCRIPT" ]]; then
  sift --context-sync "$TRANSCRIPT" 2>/dev/null || true
fi
''',
}


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


def get_latest_tag() -> str:
    """Get the latest release tag from GitHub."""
    url = f"https://api.github.com/repos/{REPO}/releases"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            releases = json.loads(resp.read().decode())
            if releases:
                return releases[0]["tag_name"]
    except Exception as e:
        print(f"Error fetching releases: {e}", file=sys.stderr)
    return ""


def download_file(url: str, dest: Path) -> bool:
    """Download a file from URL to destination."""
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                shutil.copyfileobj(resp, f)
        return True
    except Exception as e:
        print(f"  Error downloading {url}: {e}", file=sys.stderr)
        return False


def detect_platform() -> str:
    """Detect platform and return binary name."""
    system = platform.system()
    machine = platform.machine()
    
    if system == "Linux" and machine == "x86_64":
        return "sift-linux-x86_64"
    elif system == "Darwin" and machine == "arm64":
        return "sift-darwin-arm64"
    elif system == "Darwin" and machine == "x86_64":
        return "sift-darwin-x86_64"
    else:
        return ""


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
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2) + "\n")


def has_hook(settings: dict, hook_type: str, pattern: str) -> bool:
    """Check if a hook matching pattern already exists."""
    hooks = settings.get("hooks", {}).get(hook_type, [])
    for hook_group in hooks:
        for hook in hook_group.get("hooks", []):
            if pattern in hook.get("command", ""):
                return True
    return False


def add_hook(settings: dict, hook_type: str, commands: list) -> bool:
    """Add hook commands if not already present."""
    if "hooks" not in settings:
        settings["hooks"] = {}
    if hook_type not in settings["hooks"]:
        settings["hooks"][hook_type] = []
    
    # Check if already configured
    for cmd in commands:
        if has_hook(settings, hook_type, cmd.split()[0] if " " in cmd else cmd):
            return False
    
    settings["hooks"][hook_type].append({
        "hooks": [{"type": "command", "command": cmd} for cmd in commands]
    })
    return True


def main():
    print("Sift Installer")
    print("==============")
    
    # Get latest release
    latest_tag = get_latest_tag()
    if not latest_tag:
        print("Error: Could not determine latest release", file=sys.stderr)
        sys.exit(1)
    
    print(f"Release: {latest_tag}")
    print()
    
    release_url = f"https://github.com/{REPO}/releases/download/{latest_tag}"
    
    # Detect platform
    binary_name = detect_platform()
    if not binary_name:
        print(f"Error: Unsupported platform: {platform.system()} {platform.machine()}")
        print("Supported: Linux x86_64, macOS ARM64, macOS x86_64")
        sys.exit(1)
    
    print(f"Detected platform: {platform.system()} {platform.machine()}")
    print()
    
    # Step 1: Install binary
    print("Step 1: Install Sift binary")
    print("---------------------------")
    
    dest = INSTALL_DIR / "sift"
    
    if dest.exists():
        print(f"  Sift already installed at {dest}")
        do_install = prompt("  Reinstall?", "n")
    else:
        do_install = prompt(f"  Install to {dest}?")
    
    if do_install:
        print(f"  Downloading {binary_name}...")
        # Download to temp file first to avoid "Text file busy" error
        temp_dest = dest.with_suffix(".tmp")
        if download_file(f"{release_url}/{binary_name}", temp_dest):
            temp_dest.chmod(0o755)
            # Remove old binary if it exists (may be running)
            if dest.exists():
                dest.unlink()
            # Move temp to final destination
            temp_dest.rename(dest)
            print("  ✓ Installed binary")
            
            # Show version
            try:
                result = subprocess.run([str(dest), "--version"], capture_output=True, text=True)
                for line in result.stdout.split("\n"):
                    if "version" in line.lower():
                        print(f"    {line.strip()}")
            except Exception:
                pass
            
            # Also install uninstall script
            print("  Downloading uninstall script...")
            uninstall_dest = INSTALL_DIR / "sift-uninstall.py"
            if download_file(f"{release_url}/sift-uninstall.py", uninstall_dest):
                uninstall_dest.chmod(0o755)
                print(f"  ✓ Installed {uninstall_dest}")
            
            # Check PATH
            if not shutil.which("sift"):
                print(f"  Note: Add {INSTALL_DIR} to your PATH")
        else:
            print("  Error: Failed to download binary")
    else:
        print("  Skipped.")
    print()
    
    # Step 2: Install templates
    print("Step 2: Install documentation templates")
    print("---------------------------------------")
    
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check for sift template marker, not just file existence
    # (CLAUDE.md may exist with user content after uninstall removes sift section)
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    has_sift_templates = False
    if claude_md.exists():
        content = claude_md.read_text()
        has_sift_templates = "<!-- begin sift-template-" in content or "<!-- SIFT_BEGIN -->" in content
    
    if has_sift_templates:
        print("  Templates already installed.")
        do_templates = prompt("  Reinstall?", "n")
    else:
        do_templates = True
    
    if do_templates:
        all_ok = True
        for template in TEMPLATES:
            print(f"  Downloading {template}...", end=" ", flush=True)
            if download_file(f"{release_url}/{template}", CLAUDE_DIR / template):
                print("✓")
            else:
                print("FAILED")
                all_ok = False
                break
        if all_ok:
            print(f"  ✓ Installed {len(TEMPLATES)} templates")
    else:
        print("  Skipped.")
    print()
    
    # Step 3: Add MCP server
    print("Step 3: Add MCP server to Claude Code")
    print("-------------------------------------")
    
    if not shutil.which("claude"):
        print("  Claude Code CLI not found.")
        print("  Run this after installing: claude mcp add --scope user sift -- sift --mcp")
    elif prompt("  Register sift as MCP server?"):
        try:
            result = subprocess.run(
                ["claude", "mcp", "add", "--scope", "user", "sift", "--", "sift", "--mcp"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("  ✓ Added sift MCP server")
            elif "already" in result.stderr.lower() or "exists" in result.stderr.lower():
                print("  ✓ MCP server already registered")
            else:
                print(f"  Error: MCP registration failed: {result.stderr.strip()}")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("  Skipped.")
    print()
    
    # Step 4: Configure hooks
    print("Step 4: Configure Claude Code hooks")
    print("-----------------------------------")
    
    # Check which hooks already exist
    settings = load_settings()
    existing = []
    missing = []
    
    for hook_type, pattern in [("SessionStart", "session-start.sh"), 
                                ("SessionEnd", "session-end.sh"),
                                ("PreCompact", "pre-compact.sh")]:
        if has_hook(settings, hook_type, pattern):
            existing.append(hook_type)
        else:
            missing.append(hook_type)
    
    if not missing:
        # All hooks configured
        print(f"  ✓ All sift hooks configured: {', '.join(existing)}")
    else:
        print("  SessionStart: inject memory context, refresh workspace index")
        print("  SessionEnd: mark session as ended for consolidation tracking")
        print("  PreCompact: save transcript to context.db before compaction")
        print()
        
        if existing:
            print(f"  Existing: {', '.join(existing)}")
            print(f"  Missing: {', '.join(missing)}")
        
        if prompt("  Configure hooks?"):
            # Install hook scripts
            hooks_dir = CLAUDE_DIR / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)
            
            for name, content in HOOK_SCRIPTS.items():
                script_path = hooks_dir / name
                script_path.write_text(content)
                script_path.chmod(0o755)
                print(f"  ✓ Installed {script_path}")
            
            # Update settings.json
            added = []
            
            if add_hook(settings, "SessionStart", [
                "~/.claude/hooks/session-start.sh",
                "sift --session-context 2>/dev/null || true",
                "sift --quarry refresh 2>/dev/null || sift --quarry init 2>/dev/null || true",
            ]):
                added.append("SessionStart")
            
            if add_hook(settings, "SessionEnd", ["~/.claude/hooks/session-end.sh"]):
                added.append("SessionEnd")
            
            if add_hook(settings, "PreCompact", ["~/.claude/hooks/pre-compact.sh"]):
                added.append("PreCompact")
            
            if added:
                save_settings(settings)
                print(f"  ✓ Added hooks: {', '.join(added)}")
        else:
            print("  Skipped.")
    print()
    
    # Step 5: Disable TodoWrite
    print("Step 5: Disable built-in TodoWrite")
    print("----------------------------------")
    print("  sift_memory provides persistent task tracking (recommended)")
    print()
    
    if prompt("  Disable TodoWrite?"):
        settings = load_settings()
        if "permissions" not in settings:
            settings["permissions"] = {}
        if "deny" not in settings["permissions"]:
            settings["permissions"]["deny"] = []
        
        deny_list = settings["permissions"]["deny"]
        added = False
        for pattern in ["TodoWrite(**)", "TodoRead(**)"]:
            if pattern not in deny_list:
                deny_list.append(pattern)
                added = True
        
        if added:
            save_settings(settings)
            print("  ✓ TodoWrite disabled")
        else:
            print("  ✓ TodoWrite already disabled")
    else:
        print("  Skipped.")
    print()
    
    print("Done! Restart Claude Code to apply changes.")


if __name__ == "__main__":
    main()
