<!-- sift-template-0.12.0-alpha-alpha-alpha -->
# Web Tools

Crawl and cache documentation locally for instant search.

---

## 1. WHEN TO USE

**PREFERRED over WebFetch:**

| Approach | Use Case | Persistence |
|----------|----------|-------------|
| `sift_web_fetch` | Single page | Optional (with `db` param) |
| `sift_web_crawl` + `sift_web_search` | Multi-page docs | SQLite DB |
| `WebFetch` | One-off, no caching | None |

**Workflow for documentation sites:**
1. `sift_web_crawl` - Crawl docs once, store in database
2. `sift_web_search` - Search instantly (no network)
3. `sift_web_refresh` - Update stale pages periodically

**For single pages:** Use `sift_web_fetch` - returns structured JSON with title, content, links.

---

## 2. TOOL REFERENCE

### sift_web_crawl

Crawl a website into a searchable database.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url`* | string | Starting URL |
| `db` | string | Database path (default: sift-web.db) |
| `max_depth` | integer | Crawl depth (default: 3, 0 = unlimited) |
| `max_pages` | integer | Page limit (default: 100) |
| `delay_ms` | integer | Delay between requests (default: 100) |
| `same_domain` | boolean | Stay on seed domain (default: true) |
| `allow_external` | boolean | Follow external links (default: false) |
| `allowed_domains` | array | Domain whitelist |
| `timing_profile` | enum | `stealth`, `polite`, `aggressive` |
| `user_agent` | string | Custom User-Agent |

### sift_web_fetch
Fetch a single URL and return structured content.
| Parameter | Type | Description |
|-----------|------|-------------|
| `url`* | string | URL to fetch |
| `db` | string | Store in database for later searching |
| `extract_links` | boolean | Return discovered links (default: false) |
| `include_html` | boolean | Include raw HTML (default: false) |
| `user_agent` | string | Custom User-Agent |
| `timeout_ms` | integer | Request timeout (default: 30000) |
Returns: `{url, final_url, status_code, title, description, content, word_count, links?, html?, stored?, fetched_at}`
### sift_web_search

Search cached documentation with FTS5.

| Parameter | Type | Description |
|-----------|------|-------------|
| `db`* | string | Database path |
| `query`* | string | FTS5 query (AND, OR, NOT, phrases) |
| `limit` | integer | Max results (default: 10) |
| `offset` | integer | Skip N results (pagination) |
| `url_filter` | string | URL glob pattern |

### sift_web_query

Execute SQL on cached content.

| Parameter | Type | Description |
|-----------|------|-------------|
| `db`* | string | Database path |
| `sql`* | string | SQL query |
| `format` | enum | `plain`, `json`, `csv` |

**Schema:**
```sql
pages(url, title, description, content, status_code, fetched_at)
```

### sift_web_stats

Get database statistics.

| Parameter | Type | Description |
|-----------|------|-------------|
| `db`* | string | Database path |

Returns: page count, word count, domains, timestamps.

### sift_web_manifest

Detailed per-domain metadata.

| Parameter | Type | Description |
|-----------|------|-------------|
| `db`* | string | Database path |

Returns: page counts, word counts, crawl dates by domain.

### sift_web_refresh

Update stale pages.

| Parameter | Type | Description |
|-----------|------|-------------|
| `db`* | string | Database path |
| `max_age_days` | integer | Stale threshold (default: 7) |
| `max_pages` | integer | Max to refresh (default: 100) |
| `url_filter` | string | URL glob filter |

### sift_web_search_multi

Search across multiple databases.

| Parameter | Type | Description |
|-----------|------|-------------|
| `dbs`* | array | Database paths |
| `query`* | string | FTS5 query |
| `limit` | integer | Max results (default: 10) |
| `url_filter` | string | URL glob filter |

### sift_web_merge

Merge multiple caches.

| Parameter | Type | Description |
|-----------|------|-------------|
| `output`* | string | Output database path |
| `sources`* | array | Source database paths |
| `deduplicate` | boolean | Dedupe by hash (default: true) |

---

## 3. EXAMPLES

### Fetch single page
```json
{
  "url": "https://docs.example.com/api/auth",
  "extract_links": true
}
```
### Fetch and cache for later
```json
{
  "url": "https://docs.example.com/api/auth",
  "db": "api-docs.db"
}
```
### Crawl documentation site
```json
{
  "url": "https://docs.example.com",
  "db": "example-docs.db",
  "max_pages": 200,
  "max_depth": 3
}
```

### Search cached docs
```json
{
  "db": "example-docs.db",
  "query": "authentication AND oauth"
}
```

### Find all API endpoints
```json
{
  "db": "example-docs.db",
  "sql": "SELECT url, title FROM pages WHERE url LIKE '%/api/%'"
}
```

### Refresh stale pages
```json
{
  "db": "example-docs.db",
  "max_age_days": 7
}
```

### Search multiple doc caches
```json
{
  "dbs": ["react-docs.db", "nextjs-docs.db"],
  "query": "server components"
}
```

---

## 4. TIPS

**Timing profiles:**
- `stealth` - Slow, human-like pauses (for strict rate limiting)
- `polite` - Balanced (default)
- `aggressive` - Fast (for permissive sites)

**Database location:** Stored in current directory by default. Use absolute paths or descriptive names like `react-18-docs.db`.

**Freshness:** Use `sift_web_refresh` periodically to update docs without full re-crawl.

**Multi-project:** Keep separate databases per documentation source, use `sift_web_search_multi` to search all at once.
