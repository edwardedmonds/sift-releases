<!-- sift-template-0.9.2 -->
# File Tools

Read, write, and edit files with line-number precision.

---

## 1. WHEN TO USE

**These tools REPLACE native Claude Code tools:**

| Sift Tool | Replaces | Why Better |
|-----------|----------|------------|
| `sift_read` | `Read` | Returns line numbers for precise editing |
| `sift_write` | `Write` | Creates parent directories automatically |
| `sift_update` | `Edit` | Clearer error messages, same API |
| `sift_edit` | `Edit` | Multiple modes: find/replace, insert, SQL, patch |
| `sift_batch` | Multiple `Edit` | Atomic operations across files |

**Always prefer sift tools over native tools when available.**

---

## 2. TOOL REFERENCE

### sift_read

Read files with line numbers for accurate editing.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | File path to read |
| `start_line` | integer | Start from this line (1-based, default: 1) |
| `end_line` | integer | Stop at this line (default: end of file) |
| `head_limit` | integer | Limit to first N lines |
| `show_whitespace` | boolean | Visualize tabs (→) and trailing spaces (·) |

**Output format:**
```
    1: first line of file
    2: second line
    3: third line
```

### sift_write

Create or overwrite files.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | Absolute path to write |
| `content`* | string | Content to write |

Creates parent directories automatically.

### sift_update

Simple find/replace (same API as native Edit).

| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | Absolute path to modify |
| `old_string`* | string | Exact text to find |
| `new_string`* | string | Replacement text |
| `replace_all` | boolean | Replace all occurrences (default: false) |

Fails with helpful error if:
- `old_string` not found
- `old_string` found multiple times (use `replace_all: true`)

### sift_edit

Advanced editing with multiple modes.

**Mode 1: Find/Replace**
| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | File path |
| `find` | string | Text to find (literal) |
| `replace` | string | Replacement text (empty = delete) |
| `fuzzy_whitespace` | boolean | Normalize whitespace (default: true) |
| `strict_whitespace` | boolean | Exact whitespace matching |

**Mode 2: Insert**
| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | File path |
| `insert_after` | integer | Insert after this line (0 = prepend) |
| `insert_before` | integer | Insert before this line |
| `content`* | string | Content to insert |

**Mode 3: Delete**
| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | File path |
| `delete_lines` | string | Line range: "N" or "N-M" |

**Mode 4: Replace Range**
| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | File path |
| `replace_range` | object | `{start, end, content}` |

**Mode 5: Patch**
| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | File path |
| `patch` | string | Unified diff format |

**Common options:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `dry_run` | boolean | Preview without applying |
| `diff` | boolean | Return unified diff |
| `preview` | boolean | Show match count and samples |

### sift_batch

Atomic multi-operation edits.

| Parameter | Type | Description |
|-----------|------|-------------|
| `operations`* | array | Array of operation objects |
| `dry_run` | boolean | Preview without applying |

**Operation actions:**
- `delete_lines` - Remove lines
- `replace_range` - Replace line range
- `insert_after` - Add after line
- `insert_before` - Add before line
- `append` - Add to end of file
- `prepend` - Add to start of file
- `replace` - Find/replace

---

## 3. EXAMPLES

### Read specific lines
```json
{"file": "/path/to/file.c", "start_line": 100, "end_line": 150}
```

### Simple replacement
```json
{"file": "/path/to/file.c", "old_string": "foo", "new_string": "bar"}
```

### Insert after line 10
```json
{"file": "/path/to/file.c", "insert_after": 10, "content": "// New comment\n"}
```

### Delete lines 50-60
```json
{"file": "/path/to/file.c", "delete_lines": "50-60"}
```

### Replace by line range (most reliable for large changes)
```json
{
  "file": "/path/to/file.c",
  "replace_range": {"start": 100, "end": 150, "content": "new content here"}
}
```

### Atomic batch operations
```json
{
  "operations": [
    {"action": "delete_lines", "file": "old.c", "lines": "1-10"},
    {"action": "insert_after", "file": "new.c", "line": 5, "content": "// Added"},
    {"action": "replace", "file": "config.h", "find": "v1.0", "replace": "v2.0"}
  ]
}
```

---

## 4. TIPS

**Fuzzy whitespace matching** (default):
- Tabs and spaces are interchangeable
- Multiple spaces collapse to one
- Use `strict_whitespace: true` for exact matching

**Debug matching failures**:
- Use `sift_read` with `show_whitespace: true` to see actual whitespace
- Use `preview: true` to check matches before applying

**Large replacements**:
- Use `replace_range` with line numbers instead of pattern matching
- More reliable for multi-line changes
