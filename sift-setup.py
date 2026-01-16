#!/usr/bin/env python3
"""sift-setup.py - Install Sift and configure Claude Code hooks

Usage: python3 sift-setup.py
"""

import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = "edwardedmonds/sift-releases"

def get_latest_tag():
    """Get the newest release tag (works with prereleases)."""
    try:
        url = f"https://api.github.com/repos/{REPO}/releases"
        with urllib.request.urlopen(url, timeout=10) as resp:
            releases = json.loads(resp.read().decode())
            if releases:
                return releases[0]["tag_name"]
    except Exception:
        pass
    return None

LATEST_TAG = get_latest_tag()
if not LATEST_TAG:
    print("Error: Could not determine latest release")
    sys.exit(1)

RELEASE_URL = f"https://github.com/{REPO}/releases/download/{LATEST_TAG}"
CLAUDE_DIR = Path.home() / ".claude"
HOOKS_DIR = CLAUDE_DIR / "hooks"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

AUTO_FORMAT_SCRIPT = '''#!/bin/bash
# Auto-format C/C++ files after Sift edits

read -r INPUT
FILE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file',''))")

[[ -z "$FILE" || ! -f "$FILE" ]] && exit 0

EXT="${FILE##*.}"
if [[ "$EXT" == "c" || "$EXT" == "h" || "$EXT" == "cpp" || "$EXT" == "hpp" ]]; then
    if command -v clang-format &> /dev/null; then
        clang-format -i "$FILE"
    fi
fi
exit 0
'''

VALIDATE_EDIT_SCRIPT = '''#!/bin/bash
# Block edits to sensitive files

BLOCKED_PATTERNS=(".env" "secrets" ".git/" "node_modules/" ".ssh/" "id_rsa" "id_ed25519")

read -r INPUT
FILE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file',''))")

[[ -z "$FILE" ]] && exit 0

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if [[ "$FILE" == *"$pattern"* ]]; then
        echo "Blocked: Cannot edit protected file: $FILE" >&2
        exit 2
    fi
done
exit 0
'''

HOOKS_CONFIG = {
    "hooks": {
        "SessionStart": [{"hooks": [{"type": "command", "command": "sift --session-context 2>/dev/null || true"}, {"type": "command", "command": "sift --quarry refresh 2>/dev/null || sift --quarry init 2>/dev/null || true"}]}],
        "PostToolUse": [{"matcher": "Edit|Write|mcp__sift__sift_edit|mcp__sift__sift_update|mcp__sift__sift_write", "hooks": [{"type": "command", "command": "~/.claude/hooks/auto-format.sh"}]}],
        "PreToolUse": [{"matcher": "Edit|Write|mcp__sift__sift_edit|mcp__sift__sift_update|mcp__sift__sift_write", "hooks": [{"type": "command", "command": "~/.claude/hooks/validate-edit.sh"}]}]
    }
}


def prompt(question, default="y"):
    """Prompt user for yes/no. Returns True for yes."""
    suffix = " [Y/n] " if default == "y" else " [y/N] "
    try:
        # Read from /dev/tty to work with curl | python3
        with open("/dev/tty", "r") as tty:
            sys.stdout.write(question + suffix)
            sys.stdout.flush()
            answer = tty.readline().strip().lower()
        if not answer:
            return default == "y"
        return answer in ("y", "yes")
    except (EOFError, OSError):
        # Non-interactive or no tty, use default
        print(question + suffix + f"(auto: {default})")
        return default == "y"


def get_binary_name():
    """Detect platform and return appropriate binary name."""
    system = platform.system()
    machine = platform.machine()
    
    if system == "Linux" and machine == "x86_64":
        return "sift-linux-x86_64"
    elif system == "Darwin" and machine == "arm64":
        return "sift-darwin-arm64"
    elif system == "Darwin" and machine == "x86_64":
        return "sift-darwin-x86_64"
    else:
        print(f"Error: Unsupported platform: {system} {machine}")
        print("Supported: Linux x86_64, macOS ARM64, macOS x86_64")
        sys.exit(1)


def download_file(url, dest):
    """Download a file from URL to destination."""
    print(f"  Downloading {url.split('/')[-1]}...")
    urllib.request.urlretrieve(url, dest)


def main():
    print("Sift Installer")
    print("==============")
    print(f"Release: {LATEST_TAG}")
    print()
    
    binary_name = get_binary_name()
    print(f"Detected platform: {platform.system()} {platform.machine()}")
    print()
    
    install_dir = Path.home() / ".local" / "bin"
    dest = install_dir / "sift"
    
    # Step 1: Install binary
    print("Step 1: Install Sift binary")
    print("---------------------------")
    
    do_install = False
    if dest.exists():
        print(f"  Sift already installed at {dest}")
        do_install = prompt("  Reinstall?", default="n")
    else:
        do_install = prompt(f"  Install to {dest}?")
    
    if not do_install:
        print("  Skipped.")
    else:
        install_dir.mkdir(parents=True, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            download_file(f"{RELEASE_URL}/{binary_name}", tmp_path)
            os.chmod(tmp_path, os.stat(tmp_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            shutil.move(tmp_path, dest)
            print("  ✓ Installed successfully")
            
            # Show version (stderr suppressed to hide libcurl warning)
            result = subprocess.run([str(dest), "--version"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            for line in result.stdout.split('\n'):
                if 'version' in line.lower():
                    print(f"    {line.strip()}")
                    break
        except Exception as e:
            print(f"  Error: {e}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            sys.exit(1)
        
        if not shutil.which("sift"):
            print(f"  Note: Add {install_dir} to your PATH")
        
        # Install templates
        template_dir = Path.home() / ".local" / "share" / "sift" / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        print("  Downloading templates...")
        try:
            download_file(f"{RELEASE_URL}/CLAUDE.md", template_dir / "CLAUDE.md")
            download_file(f"{RELEASE_URL}/MEMORY.md", template_dir / "MEMORY.md")
            download_file(f"{RELEASE_URL}/FILE_TOOLS.md", template_dir / "FILE_TOOLS.md")
            download_file(f"{RELEASE_URL}/SEARCH_TOOLS.md", template_dir / "SEARCH_TOOLS.md")
            download_file(f"{RELEASE_URL}/WEB_TOOLS.md", template_dir / "WEB_TOOLS.md")
            download_file(f"{RELEASE_URL}/REPO_TOOLS.md", template_dir / "REPO_TOOLS.md")
            download_file(f"{RELEASE_URL}/SQL_TOOLS.md", template_dir / "SQL_TOOLS.md")
            print("  ✓ Installed templates")
        except Exception:
            print("  ⚠ Could not download templates (will use embedded fallback)")
        
        # Migrate old sift.db to memory.db if needed
        old_db = Path(".sift/sift.db")
        new_db = Path(".sift/memory.db")
        if old_db.exists() and not new_db.exists():
            old_db.rename(new_db)
            print("  ✓ Migrated .sift/sift.db -> .sift/memory.db")
        
        # Seed memory database with tool documentation
        try:
            subprocess.run([str(dest), "--seed-tools"], capture_output=True, check=False)
        except Exception:
            pass
    print()
    
    # Step 2: Add to Claude Code
    print("Step 2: Add MCP server to Claude Code")
    print("-------------------------------------")
    
    if not shutil.which("claude"):
        print("  Claude Code CLI not found.")
        print("  Run this after installing: claude mcp add --scope user sift -- sift --mcp")
        print()
    elif prompt("  Register sift as MCP server?"):
        try:
            subprocess.run(["claude", "mcp", "add", "--scope", "user", "sift", "--", "sift", "--mcp"], 
                         capture_output=True, check=False)
            print("  ✓ Added sift MCP server")
        except Exception:
            print("  ⚠ Could not add MCP server")
    else:
        print("  Skipped.")
    print()
    
    # Step 3: Configure hooks
    print("Step 3: Configure Claude Code hooks")
    print("-----------------------------------")
    print("  Hooks provide: auto-format C/C++ files, block edits to sensitive files")
    print()
    
    auto_format = HOOKS_DIR / "auto-format.sh"
    validate_edit = HOOKS_DIR / "validate-edit.sh"
    
    # Check what already exists
    hooks_exist = auto_format.exists() or validate_edit.exists()
    settings_has_hooks = False
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE) as f:
                settings = json.load(f)
            settings_has_hooks = "hooks" in settings
        except:
            pass
    
    if hooks_exist or settings_has_hooks:
        print("  Hooks already configured. Skipping to avoid overwriting.")
        print()
    elif prompt("  Install hooks?"):
        HOOKS_DIR.mkdir(parents=True, exist_ok=True)
        
        auto_format.write_text(AUTO_FORMAT_SCRIPT)
        auto_format.chmod(auto_format.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        validate_edit.write_text(VALIDATE_EDIT_SCRIPT)
        validate_edit.chmod(validate_edit.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        print("  ✓ Created hook scripts")
        
        # Update settings.json
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE) as f:
                settings = json.load(f)
            settings.update(HOOKS_CONFIG)
        else:
            CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
            settings = HOOKS_CONFIG
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        print("  ✓ Updated settings.json")
    else:
        print("  Skipped.")
    print()
    
    # Step 4: Disable TodoWrite
    print("Step 4: Disable built-in TodoWrite")
    print("----------------------------------")
    print("  sift_memory provides persistent task tracking (recommended)")
    print()
    
    if prompt("  Disable TodoWrite?"):
        # Load or create settings
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE) as f:
                settings = json.load(f)
        else:
            CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
            settings = {}
        
        # Ensure permissions.deny exists
        if "permissions" not in settings:
            settings["permissions"] = {}
        if "deny" not in settings["permissions"]:
            settings["permissions"]["deny"] = []
        
        # Add TodoWrite deny if not present
        todo_deny = ["TodoWrite(**)", "TodoRead(**)"]
        for perm in todo_deny:
            if perm not in settings["permissions"]["deny"]:
                settings["permissions"]["deny"].append(perm)
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        print("  ✓ TodoWrite disabled")
    else:
        print("  Skipped.")
    print()
    
    # Step 5: Add memory system directive to user CLAUDE.md
    print("Step 5: Add memory system directive")
    print("------------------------------------")
    print("  Adds instructions to ~/.claude/CLAUDE.md for proactive memory use")
    print()
    
    user_claude_md = CLAUDE_DIR / "CLAUDE.md"
    template_claude_md = template_dir / "CLAUDE.md"
    marker = "## System Directive: Memory System"
    
    # Check if already present
    already_present = False
    if user_claude_md.exists():
        content = user_claude_md.read_text()
        already_present = marker in content
    
    if already_present:
        print("  Sift directives already present. Skipping.")
    elif template_claude_md.exists():
        if prompt("  Add sift directives to ~/.claude/CLAUDE.md?"):
            CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
            template_content = template_claude_md.read_text()
            if user_claude_md.exists():
                with open(user_claude_md, 'a') as f:
                    f.write("\n\n" + template_content)
            else:
                user_claude_md.write_text(template_content)
            print("  ✓ Added sift directives")
        else:
            print("  Skipped.")
    else:
        print("  ⚠ Template not found. Skipping CLAUDE.md setup.")
    print()
    
    print("Done! Restart Claude Code to apply changes.")


if __name__ == "__main__":
    main()
