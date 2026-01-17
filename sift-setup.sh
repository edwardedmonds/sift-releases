#!/bin/bash
# sift-setup.sh - Install Sift and configure Claude Code hooks
#
# Usage: bash <(curl -fsSL https://...sift-setup.sh)
#    or: ./sift-setup.sh

set -e

# Get the newest release tag (works with prereleases)
REPO="edwardedmonds/sift-releases"
get_latest_tag() {
    curl -fsSL "https://api.github.com/repos/$REPO/releases" 2>/dev/null | \
        grep -m1 '"tag_name":' | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/'
}

LATEST_TAG=$(get_latest_tag)
if [[ -z "$LATEST_TAG" ]]; then
    echo "Error: Could not determine latest release"
    exit 1
fi

RELEASE_URL="https://github.com/$REPO/releases/download/$LATEST_TAG"
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
INSTALL_DIR="$HOME/.local/bin"

# Prompt helper - reads from /dev/tty to work with piped scripts
prompt() {
    local question="$1"
    local default="${2:-y}"
    local answer
    
    if [[ "$default" == "y" ]]; then
        printf "%s [Y/n] " "$question" >/dev/tty 2>/dev/null || printf "%s [Y/n] " "$question"
    else
        printf "%s [y/N] " "$question" >/dev/tty 2>/dev/null || printf "%s [y/N] " "$question"
    fi
    
    if read -r answer </dev/tty 2>/dev/null; then
        : # got input from tty
    else
        # No tty available, use default
        echo "(auto: $default)"
        answer="$default"
    fi
    
    answer="${answer:-$default}"
    # lowercase for comparison (portable)
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    
    [[ "$answer" == "y" || "$answer" == "yes" ]]
}

echo "Sift Installer"
echo "=============="
echo "Release: $LATEST_TAG"
echo

# Detect platform
OS=$(uname -s)
ARCH=$(uname -m)

case "$OS-$ARCH" in
    Linux-x86_64)
        BINARY="sift-linux-x86_64"
        ;;
    Darwin-arm64)
        BINARY="sift-darwin-arm64"
        ;;
    Darwin-x86_64)
        BINARY="sift-darwin-x86_64"
        ;;
    *)
        echo "Error: Unsupported platform: $OS-$ARCH"
        echo "Supported: Linux x86_64, macOS ARM64, macOS x86_64"
        exit 1
        ;;
esac

echo "Detected platform: $OS $ARCH"
echo

# Step 1: Install binary
echo "Step 1: Install Sift binary"
echo "---------------------------"

DEST="$INSTALL_DIR/sift"

if [[ -f "$DEST" ]]; then
    echo "  Sift already installed at $DEST"
    if prompt "  Reinstall?" "n"; then
        DO_INSTALL=1
    else
        echo "  Skipped."
        DO_INSTALL=0
    fi
else
    if prompt "  Install to $DEST?"; then
        DO_INSTALL=1
    else
        echo "  Skipped."
        DO_INSTALL=0
    fi
fi

if [[ "$DO_INSTALL" == "1" ]]; then
    mkdir -p "$INSTALL_DIR"
    echo "  Downloading $BINARY..."
    curl -fsSL "$RELEASE_URL/$BINARY" -o "/tmp/$BINARY"
    chmod +x "/tmp/$BINARY"
    mv "/tmp/$BINARY" "$DEST"
    echo "  ✓ Installed binary"
    "$DEST" --version 2>/dev/null | grep -E "Version|version" | sed 's/^/    /' || true
    
    if ! command -v sift &> /dev/null; then
        echo "  Note: Add $INSTALL_DIR to your PATH"
    fi
fi
echo

# Step 1b: Install templates to ~/.claude/
echo "Step 1b: Install documentation templates"
echo "----------------------------------------"
CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"

if [[ -f "$CLAUDE_DIR/CLAUDE.md" ]]; then
    echo "  Templates already installed."
    if prompt "  Reinstall?" "n"; then
        DO_TEMPLATES=1
    else
        echo "  Skipped."
        DO_TEMPLATES=0
    fi
else
    DO_TEMPLATES=1
fi

if [[ "$DO_TEMPLATES" == "1" ]]; then
    echo "  Downloading templates to $CLAUDE_DIR/..."
    curl -fsSL "$RELEASE_URL/CLAUDE.md" -o "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null || true
    curl -fsSL "$RELEASE_URL/MEMORY.md" -o "$CLAUDE_DIR/MEMORY.md" 2>/dev/null || true
    curl -fsSL "$RELEASE_URL/FILE_TOOLS.md" -o "$CLAUDE_DIR/FILE_TOOLS.md" 2>/dev/null || true
    curl -fsSL "$RELEASE_URL/SEARCH_TOOLS.md" -o "$CLAUDE_DIR/SEARCH_TOOLS.md" 2>/dev/null || true
    curl -fsSL "$RELEASE_URL/WEB_TOOLS.md" -o "$CLAUDE_DIR/WEB_TOOLS.md" 2>/dev/null || true
    curl -fsSL "$RELEASE_URL/REPO_TOOLS.md" -o "$CLAUDE_DIR/REPO_TOOLS.md" 2>/dev/null || true
    curl -fsSL "$RELEASE_URL/SQL_TOOLS.md" -o "$CLAUDE_DIR/SQL_TOOLS.md" 2>/dev/null || true
    echo "  ✓ Installed templates"
fi

# Seed memory database with tool documentation
# (sift binary auto-migrates sift.db -> memory.db on first access)
if command -v sift &> /dev/null; then
    sift --seed-tools 2>/dev/null || true
fi
echo

# Step 2: Add to Claude Code
echo "Step 2: Add MCP server to Claude Code"
echo "-------------------------------------"

if ! command -v claude &> /dev/null; then
    echo "  Claude Code CLI not found."
    echo "  Run this after installing: claude mcp add --scope user sift -- sift --mcp"
elif prompt "  Register sift as MCP server?"; then
    claude mcp add --scope user sift -- sift --mcp 2>/dev/null || true
    echo "  ✓ Added sift MCP server"
else
    echo "  Skipped."
fi
echo

# Step 3: Configure hooks
echo "Step 3: Configure Claude Code hooks"
echo "-----------------------------------"
echo "  Hooks provide: auto-format C/C++ files, block edits to sensitive files"
echo

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "  ⚠ jq not installed - cannot configure hooks"
    echo "  Install jq and re-run, or use sift-setup.py instead"
    echo
    echo "Done! Restart Claude Code to apply changes."
    exit 0
fi

# Check if hooks already exist
HOOKS_EXIST=0
[[ -f "$HOOKS_DIR/auto-format.sh" ]] && HOOKS_EXIST=1
[[ -f "$HOOKS_DIR/validate-edit.sh" ]] && HOOKS_EXIST=1
if [[ -f "$SETTINGS_FILE" ]] && jq -e '.hooks' "$SETTINGS_FILE" &>/dev/null; then
    HOOKS_EXIST=1
fi

if [[ "$HOOKS_EXIST" == "1" ]]; then
    echo "  Hooks already configured. Skipping to avoid overwriting."
elif prompt "  Install hooks?"; then
    mkdir -p "$HOOKS_DIR"
    
    # Write auto-format hook
    cat > "$HOOKS_DIR/auto-format.sh" << 'EOF'
#!/bin/bash
# Auto-format C/C++ files after Sift edits

read -r INPUT
FILE=$(echo "$INPUT" | jq -r '.tool_input.file // empty')

[[ -z "$FILE" || ! -f "$FILE" ]] && exit 0

EXT="${FILE##*.}"
if [[ "$EXT" == "c" || "$EXT" == "h" || "$EXT" == "cpp" || "$EXT" == "hpp" ]]; then
    if command -v clang-format &> /dev/null; then
        clang-format -i "$FILE"
    fi
fi
exit 0
EOF
    chmod +x "$HOOKS_DIR/auto-format.sh"
    
    # Write validate-edit hook
    cat > "$HOOKS_DIR/validate-edit.sh" << 'EOF'
#!/bin/bash
# Block edits to sensitive files

BLOCKED_PATTERNS=(".env" "secrets" ".git/" "node_modules/" ".ssh/" "id_rsa" "id_ed25519")

read -r INPUT
FILE=$(echo "$INPUT" | jq -r '.tool_input.file // empty')

[[ -z "$FILE" ]] && exit 0

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if [[ "$FILE" == *"$pattern"* ]]; then
        echo "Blocked: Cannot edit protected file: $FILE" >&2
        exit 2
    fi
done
exit 0
EOF
    chmod +x "$HOOKS_DIR/validate-edit.sh"
    
    echo "  ✓ Created hook scripts"
    
    # Update settings.json
    HOOKS_CONFIG='{
      "hooks": {
        "SessionStart": [{"hooks": [{"type": "command", "command": "sift --session-context 2>/dev/null || true"}, {"type": "command", "command": "sift --quarry refresh 2>/dev/null || sift --quarry init 2>/dev/null || true"}]}],
        "PostToolUse": [{"matcher": "Edit|Write|mcp__sift__sift_edit|mcp__sift__sift_update|mcp__sift__sift_write", "hooks": [{"type": "command", "command": "~/.claude/hooks/auto-format.sh"}]}],
        "PreToolUse": [{"matcher": "Edit|Write|mcp__sift__sift_edit|mcp__sift__sift_update|mcp__sift__sift_write", "hooks": [{"type": "command", "command": "~/.claude/hooks/validate-edit.sh"}]}]
      }
    }'
    
    if [[ -f "$SETTINGS_FILE" ]]; then
        UPDATED=$(jq --argjson hooks "$HOOKS_CONFIG" '. * $hooks' "$SETTINGS_FILE")
        echo "$UPDATED" > "$SETTINGS_FILE"
    else
        mkdir -p "$CLAUDE_DIR"
        echo "$HOOKS_CONFIG" | jq '.' > "$SETTINGS_FILE"
    fi
    echo "  ✓ Updated settings.json"
else
    echo "  Skipped."
fi
echo

# Step 4: Disable TodoWrite
echo "Step 4: Disable built-in TodoWrite"
echo "----------------------------------"
echo "  sift_memory provides persistent task tracking (recommended)"
echo

if ! command -v jq &> /dev/null; then
    echo "  ⚠ jq required - skipping"
elif prompt "  Disable TodoWrite?"; then
    if [[ -f "$SETTINGS_FILE" ]]; then
        UPDATED=$(jq '.permissions.deny = ((.permissions.deny // []) + ["TodoWrite(**)", "TodoRead(**)"] | unique)' "$SETTINGS_FILE")
        echo "$UPDATED" > "$SETTINGS_FILE"
    else
        mkdir -p "$CLAUDE_DIR"
        echo '{"permissions":{"deny":["TodoWrite(**)","TodoRead(**)"]}}' | jq '.' > "$SETTINGS_FILE"
    fi
    echo "  ✓ TodoWrite disabled"
else
    echo "  Skipped."
fi
echo

echo "Done! Restart Claude Code to apply changes."
