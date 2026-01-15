# Sift

**SQL-powered MCP server for Claude Code.**

Sift gives Claude Code persistent memory, fast search, and intelligent file editing.

## The Problem

Every time you start a new Claude Code session, Claude forgets everything. Your preferences, the patterns you've established, the decisions you've made together, the gotchas you've discovered—all gone. You end up repeating yourself, re-explaining your codebase, and watching Claude make the same mistakes you corrected yesterday.

## The Solution

Sift gives Claude a persistent memory that survives across sessions. When you tell Claude "I prefer spaces over tabs" or "always use early returns", that preference is stored and automatically loaded in future sessions. When Claude learns that a particular API is flaky or that a certain pattern causes bugs in your codebase, it remembers.

But this isn't just a key-value store. Sift's memory is **queryable**. Claude can search its memories using full-text search with boolean operators. It can find related memories, track dependencies between tasks, and even detect when new information conflicts with existing knowledge.

The memory system supports different types of knowledge:
- **Patterns**: Coding conventions and workflows ("use sift_read before sift_edit")
- **Preferences**: Your personal style choices ("prefer descriptive variable names")
- **Plans**: Multi-step implementation strategies with tracked decisions
- **Tasks**: Work items with status, priority, and dependencies
- **Gotchas**: Hard-won lessons about what doesn't work

Claude can also **reflect** on its work—recording why it chose one approach over another, noting observations about your codebase, and logging corrections when you point out mistakes. These reflections become searchable knowledge that improves future sessions.

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

Add sift globally (recommended):
```bash
claude mcp add --scope user sift -- sift --mcp
```

Or add to a specific project only:
```bash
cd your-project
claude mcp add --scope project sift -- sift --mcp
```

**Note:** Sift automatically creates a separate `.sift/` database in each project directory, so your memories and search indexes are always project-specific even when sift is installed globally.

### 3. Try It Out

Create a new directory and start Claude Code:

```bash
mkdir test-sift && cd test-sift
claude
```

**Test the memory system:**
```
Remember that I prefer early returns over nested if statements
```

```
Remember that our API rate limits to 100 requests per minute
```

Start a new session and ask:
```
What do you know about my preferences and our API?
```

**Test search and editing:**
```
Create a few Python files with different functions, then search for all function definitions
```

```
Create a config.json file with some settings, then update the timeout value to 30
```

## Tools

### Memory
| Tool | Description |
|------|-------------|
| `sift_memory_add` | Store patterns, preferences, plans, tasks, or gotchas |
| `sift_memory_search` | Full-text search across all memories |
| `sift_memory_list` | List memories by type or status |
| `sift_memory_update` | Update memory status, priority, or content |
| `sift_memory_delete` | Remove a memory |
| `sift_memory_decide` | Record a decision for a plan |
| `sift_memory_decisions` | Query past decisions |
| `sift_memory_reflect` | Log reasoning, observations, or corrections |
| `sift_memory_reflections` | Search past reflections |
| `sift_memory_link` | Create dependencies between memories |
| `sift_memory_deps` | Query memory dependencies |
| `sift_memory_ready` | Find tasks with no blockers |
| `sift_memory_stale` | Find old memories that may need review |
| `sift_memory_stats` | Get memory database statistics |
| `sift_memory_config` | View ranking weight configuration |
| `sift_memory_tune` | Adjust search ranking weights |
| `sift_memory_backups` | List memory database backups |
| `sift_memory_restore` | Restore from a backup |
| `sift_memory_import` | Import markdown plans into memory |

### Search & Edit
| Tool | Description |
|------|-------------|
| `sift_search` | FTS5 full-text search (30-195x faster than grep) |
| `sift_read` | Read files with line numbers |
| `sift_edit` | Find/replace with fuzzy whitespace matching |
| `sift_update` | Simple old_string/new_string replacement |
| `sift_write` | Create or overwrite files |
| `sift_batch` | Multiple edit operations atomically |
| `sift_transform` | SQL-based file transformation |
| `sift_sql` | Run SQL on text input |
| `sift_workspace` | Manage the search index |

### Web & Repository
| Tool | Description |
|------|-------------|
| `sift_web_crawl` | Crawl and index a website |
| `sift_web_search` | Search indexed web content |
| `sift_web_query` | SQL queries on web content |
| `sift_web_stats` | Web database statistics |
| `sift_web_refresh` | Update stale cached pages |
| `sift_repo_clone` | Clone and index a git repository |
| `sift_repo_search` | Search indexed repository |
| `sift_repo_query` | SQL queries on repository content |

## Verify Download

Each release includes `checksums.txt` with SHA256 hashes:
```bash
sha256sum -c checksums.txt
```

## License

Proprietary. Binary distribution only.
