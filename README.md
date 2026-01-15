# Sift

**SQL-powered MCP server for Claude Code.**

Sift provides Claude Code with fast full-text search, intelligent file editing, and persistent memory across sessions.

## Quick Start

### 1. Download

**Linux (x86_64)**
```bash
curl -LO https://github.com/edwardedmonds/sift-releases/releases/latest/download/sift-linux-x86_64
chmod +x sift-linux-x86_64
sudo mv sift-linux-x86_64 /usr/local/bin/sift
```

**macOS (Apple Silicon)**
```bash
curl -LO https://github.com/edwardedmonds/sift-releases/releases/latest/download/sift-darwin-arm64
chmod +x sift-darwin-arm64
sudo mv sift-darwin-arm64 /usr/local/bin/sift
```

**macOS (Intel)**
```bash
curl -LO https://github.com/edwardedmonds/sift-releases/releases/latest/download/sift-darwin-x86_64
chmod +x sift-darwin-x86_64
sudo mv sift-darwin-x86_64 /usr/local/bin/sift
```

### 2. Add to Claude Code

```bash
claude mcp add sift -- sift --mcp
```

### 3. Test It

Start Claude Code and ask:

> "Search for TODO comments in this codebase"

Claude will use `sift_search` to find matches 30-195x faster than grep.

## Tools

| Tool | Description |
|------|-------------|
| `sift_search` | FTS5 full-text search with boolean queries (AND, OR, NOT, NEAR) |
| `sift_read` | Read files with line numbers for accurate editing |
| `sift_edit` | Find/replace with fuzzy whitespace matching |
| `sift_write` | Create or overwrite files |
| `sift_memory_*` | Persistent agent memory across sessions |

## Features

- **Fast Search**: FTS5 indexing makes searches 30-195x faster than grep
- **Smart Editing**: Fuzzy whitespace matching prevents edit failures from tab/space differences
- **Agent Memory**: Plans, decisions, and patterns persist across Claude Code sessions
- **Web Crawling**: Index documentation sites for offline querying

## Verify Download

Each release includes `checksums.txt` with SHA256 hashes:
```bash
sha256sum -c checksums.txt
```

## License

Proprietary. Binary distribution only.
