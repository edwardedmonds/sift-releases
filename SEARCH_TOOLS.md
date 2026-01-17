<!-- sift-template-0.9.2 -->
# Search Tools

Fast full-text search across your codebase using FTS5.

---

## 1. WHEN TO USE

**sift_search REPLACES native Grep and Glob tools:**

| Feature | sift_search | Grep/Glob |
|---------|-------------|-----------|
| Speed | 30-195x faster | Baseline |
| Boolean queries | AND, OR, NOT, NEAR | Limited |
| Auto-indexing | Yes | No |
| Persistent index | Yes (.sift/workspace.db) | No |

**Always use sift_search for codebase searches.**

The workspace index auto-initializes on first use. Use `sift_workspace` only for manual maintenance.

---

## 2. TOOL REFERENCE

### sift_search

Full-text search with FTS5 boolean queries.

| Parameter | Type | Description |
|-----------|------|-------------|
| `pattern` | string | FTS5 search pattern (see syntax below) |
| `files` | string | Glob filter (e.g., "*.c", "src/**/*.h") |
| `sql` | string | Custom SQL query (advanced) |
| `literal` | boolean | Exact substring match instead of FTS5 |
| `head_limit` | integer | Max results (default: 100, 0 = unlimited) |
| `context` | integer | Context lines before/after (like grep -C) |
| `show_function` | boolean | Include function name (C/C++ only) |
| `stats` | boolean | Include execution time |

**FTS5 Pattern Syntax:**

| Pattern | Matches |
|---------|---------|
| `foo` | Lines containing "foo" |
| `foo AND bar` | Lines with both "foo" and "bar" |
| `foo OR bar` | Lines with "foo" or "bar" |
| `foo NOT bar` | Lines with "foo" but not "bar" |
| `NEAR(foo bar, 5)` | "foo" within 5 words of "bar" |
| `foo*` | Prefix match: "foo", "foobar", etc. |
| `"exact phrase"` | Exact phrase match |

**Note:** FTS5 strips special characters like `--flag`. Use `literal: true` for exact substring matching.

### sift_workspace

Manage the workspace index (usually not needed).

| Parameter | Type | Description |
|-----------|------|-------------|
| `action`* | enum | `init`, `status`, `refresh`, `rebuild` |
| `directory` | string | Directory to index (default: cwd) |

**Actions:**
- `init` - Create index (auto-done by sift_search)
- `status` - Show index info (file count, last update)
- `refresh` - Update changed files incrementally
- `rebuild` - Full reindex (use if index is corrupted)

---

## 3. EXAMPLES

### Basic search
```json
{"pattern": "TODO"}
```

### Search with file filter
```json
{"pattern": "malloc AND free", "files": "*.c"}
```

### Proximity search
```json
{"pattern": "NEAR(error handle, 5)"}
```

### Show function context (C/C++)
```json
{"pattern": "mutex", "files": "*.c", "show_function": true}
```

### Exact substring (special characters)
```json
{"pattern": "--verbose", "literal": true}
```

### Custom SQL query
```json
{
  "sql": "SELECT f.filepath, l.line_number, l.content FROM search_fts s JOIN lines l ON s.rowid = l.line_id JOIN files f ON l.file_id = f.file_id WHERE s.content MATCH 'error' ORDER BY f.filepath LIMIT 20"
}
```

### Check index status
```json
{"action": "status"}
```

### Refresh after external changes
```json
{"action": "refresh"}
```

---

## 4. TIPS

**First search is slower** - it builds the index. Subsequent searches use the cached index.

**Index location:** `.sift/workspace.db` in the project root.

**When to refresh:**
- After external tools modify files
- If search results seem stale
- Usually not needed (auto-refreshes on directory mtime changes)

**SQL schema for custom queries:**
```sql
-- Tables
files(file_id, filepath, line_count, mtime)
lines(line_id, file_id, line_number, content)
search_fts(content)  -- FTS5 virtual table, rowid = line_id
```
