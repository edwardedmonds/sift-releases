<!-- sift-template-0.12.0-alpha-alpha-alpha -->
# SQL Tools

Process and transform text using SQL queries.

---

## 1. WHEN TO USE

**Replaces sed/awk for text processing:**

| Use Case | Tool |
|----------|------|
| Transform text data | `sift_sql` |
| Transform file in-place | `sift_transform` |
| Parse CSV/TSV | `sift_sql` with `csv_field()` |
| Regex replacements | `sift_sql` with `regex_replace()` |

---

## 2. TOOL REFERENCE

### sift_sql

Execute SQL on text input.

| Parameter | Type | Description |
|-----------|------|-------------|
| `input`* | string | Text content to query |
| `sql`* | string | SQL query using `lines` table |
| `format` | enum | `plain`, `json`, `csv`, `tsv` |
| `stats` | boolean | Include execution statistics |

**Schema:**
```sql
lines(line_number INTEGER, content TEXT)
```

### sift_transform

SQL-based in-place file transformation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file`* | string | File path to transform |
| `sql`* | string | SQL query that SELECTs `content` column |
| `dry_run` | boolean | Preview without writing |
| `diff` | boolean | Return unified diff |

---

## 3. BUILT-IN SQL FUNCTIONS

### Regex Functions

| Function | Description | Example |
|----------|-------------|---------|
| `regex_match(pattern, text)` | Returns 1 if match | `regex_match('\\d+', content)` |
| `regex_replace(pattern, text, replacement)` | Replace matches | `regex_replace('foo', content, 'bar')` |
| `regex_extract(pattern, text, group)` | Extract capture group | `regex_extract('v(\\d+)', content, 1)` |

### CSV Functions

| Function | Description | Example |
|----------|-------------|---------|
| `csv_field(line, index)` | Get field by index (0-based) | `csv_field(content, 0)` |
| `csv_field(line, index, delim)` | Custom delimiter | `csv_field(content, 1, '\t')` |
| `csv_count(line)` | Count fields | `csv_count(content)` |
| `csv_escape(text)` | Escape for CSV | `csv_escape(value)` |

### Encoding Functions

| Function | Description |
|----------|-------------|
| `base64_encode(text)` | Encode to base64 |
| `base64_decode(text)` | Decode from base64 |
| `hex_encode(text)` | Encode to hex |
| `hex_decode(text)` | Decode from hex |
| `url_encode(text)` | URL encode |
| `url_decode(text)` | URL decode |

### SQLite Built-ins

Standard SQLite functions also available:
- `upper()`, `lower()`, `trim()`, `substr()`, `length()`
- `printf()`, `replace()`, `instr()`
- `LIKE`, `GLOB` patterns

---

## 4. EXAMPLES

### Uppercase text
```json
{
  "input": "hello world",
  "sql": "SELECT upper(content) FROM lines"
}
```

### Parse CSV
```json
{
  "input": "name,age,city\nAlice,30,NYC\nBob,25,LA",
  "sql": "SELECT csv_field(content, 0) as name, csv_field(content, 1) as age FROM lines WHERE line_number > 1",
  "format": "json"
}
```

### Regex replacement
```json
{
  "input": "version: 1.0.0",
  "sql": "SELECT regex_replace('\\d+\\.\\d+\\.\\d+', content, '2.0.0') FROM lines"
}
```

### Filter lines
```json
{
  "input": "error: something failed\ninfo: all good\nerror: another issue",
  "sql": "SELECT content FROM lines WHERE content LIKE 'error:%'"
}
```

### Number lines
```json
{
  "input": "first\nsecond\nthird",
  "sql": "SELECT printf('%3d: %s', line_number, content) FROM lines"
}
```

### Transform file in-place
```json
{
  "file": "/path/to/data.txt",
  "sql": "SELECT upper(content) FROM lines ORDER BY line_number",
  "dry_run": true
}
```

### Extract version numbers
```json
{
  "input": "Release v1.2.3 is ready\nVersion v2.0.0 coming soon",
  "sql": "SELECT regex_extract('v(\\d+\\.\\d+\\.\\d+)', content, 1) as version FROM lines WHERE content LIKE '%v%'"
}
```

---

## 5. TIPS

**Order matters:** Use `ORDER BY line_number` in `sift_transform` to preserve line order.

**Output formats:**
- `plain` - One result per line
- `json` - JSON array of objects
- `csv` - CSV with header row
- `tsv` - Tab-separated

**Dry run first:** Always use `dry_run: true` with `sift_transform` before applying changes.

**Combine with sift_edit:** For complex file edits, `sift_edit` with SQL mode offers more control.
