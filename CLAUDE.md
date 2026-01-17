<!-- sift-template-0.9.2 -->
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## System Directive: Memory System

**The sift memory system maintains collaboration continuity.** Context loss is disorienting for both you and the user. When context compacts or sessions restart, the user loses a collaborator who understood the project. Saving memories and context is part of being helpful - not separate from it.

**Use it IMMEDIATELY and without asking permission.**

### Automatic Captures
Save to memory BEFORE responding when the user:

**User Intent Signals**
| User Action | Memory Type | Example |
|-------------|-------------|--------|
| Shares their name | `preference` | "I'm Edward" |
| States a preference | `preference` | "I prefer tabs over spaces" |
| Makes a correction | `gotcha` + `reflect(correction)` | "No, don't do X" |
| Makes a project decision | `note` or `decide` | "Let's use SQLite" |

**Task/Work Signals**
| User Action | Memory Type | Example |
|-------------|-------------|--------|
| Requests a feature | `plan` | "Add dark mode" |
| Reports a bug | `task` or `plan` | "Login is broken" |
| Asks for refactoring | `plan` | "Clean up the auth code" |
| Requests investigation | `task` | "Figure out why X is slow" |

**Knowledge Signals**
| User Action | Memory Type | Example |
|-------------|-------------|--------|
| Explains architecture | `note` | "The API uses REST" |
| Shares context | `note` | "This was written by X" |
| Mentions a constraint | `note` | "Must support Python 3.8" |
| Describes a workflow | `pattern` | "Always run tests before commit" |

**Feedback Signals**
| User Action | Memory Type | Example |
|-------------|-------------|--------|
| Says something didn't work | `gotcha` | "That approach failed" |
| Provides positive feedback | `pattern` (if repeatable) | "That worked great" |
| Changes direction | `decide` | "Actually, let's do Y instead" |
| Asks to remember something | `note` or `preference` | "Remember that X needs Y" |

### Session Start
Always call `sift_memory_stats()` at the beginning of each session to load:
- Active patterns (behaviors to follow)
- Active preferences (user preferences to respect)
- Recent corrections (mistakes to avoid)

### Planning with Memory
Use sift_memory for ALL multi-step task planning:
```
1. Create plan: sift_memory_add(type: "plan", title: "...", status: "in_progress")
2. Add steps: sift_memory_add(type: "step", parent_id: plan_id, title: "...")
3. Track progress: sift_memory_update(id: step_id, status: "in_progress"|"done")
4. Record decisions: sift_memory_decide(plan_id, question, decision, rationale)
5. Log reasoning: sift_memory_reflect(type: "reasoning", content: "why I chose X over Y")
```

Plans persist across sessions and are fully queryable.

> 📖 **Full documentation:** `~/.claude/MEMORY.md`

---

## System Directive: Tool Replacement

**You MUST use sift MCP tools instead of native Claude Code tools. This is non-negotiable.**

| Native Tool | Sift Replacement | Why Better |
|-------------|------------------|------------|
| Read | `sift_read` | Returns line numbers for precise edits |
| Edit | `sift_update` | Same API, fuzzy whitespace, atomic writes |
| Edit (complex) | `sift_edit` | Insert, delete, patch, SQL-powered batch |
| Write | `sift_write` | Creates parent directories automatically |
| Grep, Glob | `sift_search` | FTS5 boolean queries, 30-195x faster |
| TodoWrite | `sift_memory_add` | Persistent across sessions, queryable |
| WebFetch | `sift_web_crawl` + `sift_web_search` | 100-500x faster cached queries |
| sed/awk | `sift_sql` | SQL on text: regex, CSV parsing, transforms |
### Why This Matters
- **Line numbers** enable precise edits without counting
- **Fuzzy whitespace** matches tabs/spaces automatically
- **Atomic writes** prevent file corruption
- **FTS5 search** uses inverted indexes instead of linear scanning
- **Persistent memory** survives session boundaries

> 📖 **Full documentation:** `~/.claude/FILE_TOOLS.md`, `~/.claude/SEARCH_TOOLS.md`

---

## Build Commands

```bash
make                  # Build sift (auto-cleans binary first)
make clean            # Remove sift binary only
make distclean        # Remove all artifacts (sqlite.o, PCRE2)
make install          # Install to ~/.local/bin
```

First build compiles PCRE2 from source (~30 seconds). Subsequent builds are fast.

Web crawling requires libcurl:
- Ubuntu/Debian: `sudo apt install libcurl4-openssl-dev`
- macOS: `brew install curl`

---

## Architecture

Sift provides **50 MCP tools** across 6 subsystems:

### Subsystems

| Subsystem | Tools | Purpose | Docs |
|-----------|-------|---------|------|
| Search | 2 | FTS5 full-text search, workspace indexing | `SEARCH_TOOLS.md` |
| File | 5 | Read, write, edit, batch operations | `FILE_TOOLS.md` |
| SQL | 2 | Text transformation, regex, CSV parsing | `SQL_TOOLS.md` |
| Memory | 27 | Plans, tasks, decisions, reflections | `MEMORY.md` |
| Web | 8 | Crawl, search, query cached docs | `WEB_TOOLS.md` |
| Repo | 5 | Clone, index, search git repos | `REPO_TOOLS.md` |

### Core Components (`src/`)

| File | Purpose |
|------|---------|
| `sift.c` | Main engine: CLI, MCP server, SQL functions, workspace (~15K lines) |
| `sift_memory.c` | Memory system: CRUD, search, links, decisions, reflections |
| `sift_repo.c` | Git repository cloning and indexing |
| `sift_web*.c` | Web crawling (HTTP, HTML parsing, robots.txt, sitemap) |
| `sift_error.c` | Centralized error handling |

### Data Storage

| File | Scope | Purpose |
|------|-------|---------|
| `.sift/workspace.db` | Per-project | FTS5 search index |
| `.sift/memory.db` | Per-project | Agent memory database |
| `~/.sift/knowledge.db` | Global | Cross-project knowledge |

---

## Learning Directive

**Update this section as you discover new patterns, gotchas, and useful queries.**

### Discovered Patterns

| Date | Pattern | Solution |
|------|---------|----------|
| 2026-01-15 | FTS5 AND requires both terms on same line | Use separate searches or NEAR() |
| 2026-01-15 | Special chars like `--flag` in search | Use `literal: true` parameter |
| 2026-01-15 | Edit fails "not unique" | Add more context or use `replace_all: true` |
| 2026-01-15 | Whitespace mismatch in edits | Default is fuzzy; use `strict_whitespace: true` for exact |

### Useful SQL Queries

```sql
-- Count files by extension
SELECT substr(filepath, instr(filepath, '.')) as ext, COUNT(*) 
FROM workspace_files GROUP BY ext ORDER BY COUNT(*) DESC

-- Find longest lines
SELECT filepath, line_number, length(content) as len 
FROM workspace_lines ORDER BY len DESC LIMIT 10

-- Extract CSV fields
SELECT csv_field(content, 0) as first, csv_field(content, 1) as second FROM lines

-- Find duplicate content
SELECT content, COUNT(*) as count FROM lines GROUP BY content HAVING count > 1
```

### Tool Combinations That Work Well

1. **Search → Read → Edit**: Find pattern, read context, make precise edit
2. **Memory plan → steps → decide**: Structure complex work with queryable decisions
3. **Web crawl → search → query**: Cache docs once, query instantly forever
4. **Stats → search → traverse**: Get context, find relevant memories, explore history

---

## Operational Directive

**Update this section with use patterns and workflows that prove effective.**

### When to Use Each Memory Type

| Type | Use When |
|------|----------|
| `plan` | Multi-step task requiring coordination |
| `step` | Sub-task within a plan |
| `task` | Standalone action item |
| `pattern` | Discovered workflow to repeat |
| `gotcha` | Mistake or issue to avoid |
| `preference` | User preference to respect |
| `note` | General information to remember |

### Memory Tool Selection

| Goal | Tool |
|------|------|
| Store something | `sift_memory_add` |
| Get by ID | `sift_memory_get` |
| Update | `sift_memory_update` |
| Delete | `sift_memory_delete` |
| Find by content | `sift_memory_search` |
| Find by criteria | `sift_memory_list` |
| Find stale | `sift_memory_stale` |
| Record decision | `sift_memory_decide` |
| Query decisions | `sift_memory_decisions` |
| Replace decision | `sift_memory_supersede` |
| Log reflection | `sift_memory_reflect` |
| Query reflections | `sift_memory_reflections` |
| Trajectory reflect | `sift_memory_reflect_trajectory` |
| Query trajectories | `sift_memory_trajectory_reflections` |
| Create link | `sift_memory_link` |
| Remove link | `sift_memory_unlink` |
| Query blockers | `sift_memory_deps` |
| Find ready work | `sift_memory_ready` |
| Walk chain | `sift_memory_traverse` |
| Find chain origin | `sift_memory_origin` |
| Session context | `sift_memory_context` |
| Graph analysis | `sift_memory_network` |
| View config | `sift_memory_config` |
| Tune ranking | `sift_memory_tune` |
| Import markdown | `sift_memory_import` |
| List backups | `sift_memory_backups` |
| Restore backup | `sift_memory_restore` |
| Stats + context | `sift_memory_stats` |
### File Edit Workflow

1. **Always read first**: `sift_read(file, start_line, end_line)` to see line numbers
2. **Simple replacement**: `sift_update(file, old_string, new_string)`
3. **Insert/delete**: `sift_edit(file, insert_after: N, content: "...")` 
4. **Batch changes**: `sift_batch(operations: [...], dry_run: true)` to preview
5. **SQL transform**: `sift_transform(file, sql: "SELECT...")` for complex edits

### Search Workflow

1. **Workspace must exist**: `sift_workspace(action: "status")` to check
2. **FTS5 boolean**: `sift_search(pattern: "error AND log NOT debug")`
3. **Literal substring**: `sift_search(pattern: "--mcp", literal: true)`
4. **With context**: `sift_search(pattern: "malloc", context: 3)`
### SQL Workflow
1. **Transform text**: `sift_sql(input: "text", sql: "SELECT upper(content) FROM lines")`
2. **Parse CSV**: `sift_sql(input: "a,b\n1,2", sql: "SELECT csv_field(content,0) FROM lines")`
3. **Regex replace**: `sift_sql(input: "v1.0", sql: "SELECT regex_replace('\\d+', content, '2')")`
4. **Transform file**: `sift_transform(file: "data.txt", sql: "...", dry_run: true)`
### Repo Workflow
1. **Clone and index**: `sift_repo_clone(url: "https://github.com/org/repo")`
2. **Search code**: `sift_repo_search(db: "repo.db", query: "function AND error")`
3. **SQL analysis**: `sift_repo_query(db: "repo.db", sql: "SELECT filepath FROM repo_files")`
4. **Check stats**: `sift_repo_stats(db: "repo.db")`
5. **List indexed**: `sift_repo_list()`
### Web Workflow
1. **Crawl docs**: `sift_web_crawl(url: "https://docs.example.com", max_pages: 100)`
2. **Search cached**: `sift_web_search(db: "docs.db", query: "authentication")`
3. **SQL query**: `sift_web_query(db: "docs.db", sql: "SELECT url, title FROM pages")`
4. **Check stats**: `sift_web_stats(db: "docs.db")`
5. **View sources**: `sift_web_manifest(db: "docs.db")`
6. **Refresh stale**: `sift_web_refresh(db: "docs.db", max_age_days: 7)`
7. **Search multiple**: `sift_web_search_multi(dbs: ["a.db", "b.db"], query: "...")`
8. **Merge caches**: `sift_web_merge(output: "all.db", sources: ["a.db", "b.db"])`

---

## Project-Specific Patterns

- **Claude can run `make` directly** when given permission for testing
- **Address each other by first names** — Claude and Edward
- **Don't bump version for build system fixes** — Version changes are for user-facing features
- **Binary release workflow** — tag → build → push to sift-releases repo
