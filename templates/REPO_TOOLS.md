<!-- sift-template-0.12.0-alpha-alpha-alpha -->
# Repo Tools

Clone and index external git repositories for searchable reference.

---

## 1. WHEN TO USE

Clone external repositories to:
- Learn from other codebases
- Reference implementation patterns
- Search library source code
- Understand dependencies

**Workflow:**
1. `sift_repo_clone` - Clone and index a repo
2. `sift_repo_search` - Search the indexed code
3. `sift_repo_query` - SQL queries for analysis
4. `sift_repo_stats` - Check what's indexed

---

## 2. TOOL REFERENCE

### sift_repo_clone

Clone and index a git repository.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url`* | string | Git repository URL |
| `db` | string | Output database (default: `<repo-name>.db`) |
| `branch` | string | Branch to clone (default: default branch) |
| `depth` | integer | Clone depth (default: 1, shallow) |
| `include` | array | File patterns to include (e.g., `["*.c", "*.h"]`) |
| `exclude` | array | File patterns to exclude (e.g., `["test/*"]`) |

Creates a searchable SQLite database with FTS5.

### sift_repo_search

Search indexed repository content.

| Parameter | Type | Description |
|-----------|------|-------------|
| `db`* | string | Database path |
| `query`* | string | FTS5 query (AND, OR, NOT, phrases) |
| `limit` | integer | Max results (default: 20) |
| `files` | string | File pattern filter (e.g., `"*.c"`) |
| `language` | string | Language filter (e.g., `"c"`, `"python"`) |

### sift_repo_query

Execute SQL on repository database.

| Parameter | Type | Description |
|-----------|------|-------------|
| `db`* | string | Database path |
| `sql`* | string | SQL query |
| `format` | enum | `plain`, `json`, `csv` |

**Schema:**
```sql
repo_files(filepath, content, language, line_count, byte_size)
```

### sift_repo_stats

Get repository statistics.

| Parameter | Type | Description |
|-----------|------|-------------|
| `db`* | string | Database path |

Returns: file count, line count, language breakdown, clone metadata.

### sift_repo_list

List indexed repositories in current directory.

No parameters - scans for `*.db` files with repo structure.

---

## 3. EXAMPLES

### Clone a repository
```json
{
  "url": "https://github.com/sqlite/sqlite.git",
  "db": "sqlite-src.db",
  "include": ["*.c", "*.h"]
}
```

### Search for patterns
```json
{
  "db": "sqlite-src.db",
  "query": "mutex AND lock",
  "language": "c"
}
```

### Find largest files
```json
{
  "db": "sqlite-src.db",
  "sql": "SELECT filepath, line_count FROM repo_files ORDER BY line_count DESC LIMIT 10"
}
```

### Language breakdown
```json
{
  "db": "sqlite-src.db",
  "sql": "SELECT language, COUNT(*) as files, SUM(line_count) as lines FROM repo_files GROUP BY language ORDER BY lines DESC"
}
```

### Check index status
```json
{"db": "sqlite-src.db"}
```

---

## 4. TIPS

**Shallow clone** (default: depth=1) is fast and sufficient for searching. Use deeper clone only if you need git history.

**File filters:** Use `include` to index only relevant files (e.g., source code). This speeds up cloning and reduces database size.

**Multiple repos:** Each repo gets its own `.db` file. Use `sift_repo_list` to see what's indexed.

**Use cases:**
- "How does SQLite handle X?" → Clone and search sqlite-src.db
- "Show me Redis connection pooling" → Clone redis.db and search
- "What pattern does this library use for Y?" → Clone and explore
