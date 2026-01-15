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

## Why SQL Matters: Reducing Hallucinations

Large language models hallucinate. Claude might confidently report that a function is on line 50 when it's actually on line 200. It might "remember" that you prefer tabs when you actually said spaces. It might fabricate an API endpoint that doesn't exist in your codebase.

Sift's SQL-powered design directly addresses this problem.

When Claude searches your codebase with `sift_search`, it gets back real results from a real database—not a vague recollection that might be wrong. The results include exact file paths, exact line numbers, and exact content. There's no room to confabulate.

When Claude reads a file with `sift_read`, it sees actual content with line numbers. When it edits with `sift_edit`, the tool returns an error if the target text doesn't exist or isn't unique. These aren't polite suggestions—they're hard failures that force confrontation with reality rather than proceeding on false assumptions.

The memory system works the same way. When you tell Claude you prefer early returns, that preference is stored as a structured record that can be queried later—not as a fuzzy impression that might drift over time. When Claude is unsure what you said about your authentication system, it can run `sift_memory_search` and get back exactly what was recorded, not what it thinks it remembers.

This is the difference between asking someone to recall a conversation from last week versus looking at a transcript. The transcript might be less convenient, but it's accurate.

SQL doesn't make Claude incapable of mistakes, but it provides a way to verify. Every search result, every memory query, every file read produces concrete, auditable output. When Claude says "I found 5 files matching your query," you can see those 5 files. When it says "you told me to always use UTC timestamps," there's a record you can check.

The machine-readable nature of these tools creates accountability.

## Installation

### Quick Install (Recommended)

Interactive installers that prompt for each step:

**Using Python (no dependencies):**
```bash
curl -fsSL https://github.com/edwardedmonds/sift-releases/releases/latest/download/sift-setup.py -o /tmp/sift-setup.py && python3 /tmp/sift-setup.py
```

**Using Bash (requires jq for hooks):**
```bash
curl -fsSL https://github.com/edwardedmonds/sift-releases/releases/latest/download/sift-setup.sh -o /tmp/sift-setup.sh && bash /tmp/sift-setup.sh
```

The installer will prompt before each step:
1. Install binary to `~/.local/bin`
2. Register sift as MCP server with Claude Code
3. Configure optional hooks (auto-format C/C++, block sensitive files)

Existing hooks are preserved—the installer skips hook configuration if hooks already exist.

### Manual Install

**Step 1: Download**

| Platform | Command |
|----------|--------|
| Linux x86_64 | `curl -LO https://github.com/edwardedmonds/sift-releases/releases/latest/download/sift-linux-x86_64` |
| macOS Apple Silicon | `curl -LO https://github.com/edwardedmonds/sift-releases/releases/latest/download/sift-darwin-arm64` |
| macOS Intel | `curl -LO https://github.com/edwardedmonds/sift-releases/releases/latest/download/sift-darwin-x86_64` |

**Step 2: Install**
```bash
chmod +x sift-*
mkdir -p ~/.local/bin
mv sift-* ~/.local/bin/sift
```

**Step 3: Add to Claude Code**
```bash
claude mcp add --scope user sift -- sift --mcp
```

**Step 4: Verify**
```bash
~/.local/bin/sift --version
```

> **Note:** Add `~/.local/bin` to your PATH if not already. Sift creates a `.sift/` database in each project directory, so memories and indexes are project-specific.

### Try It Out

Start Claude Code in any directory:
```bash
claude
```

**Test memory:**
```
Remember that I prefer early returns over nested if statements
```

Start a new session and ask:
```
What do you know about my preferences?
```

## Tools

### Memory

[sift_memory_add](#sift_memory_add) · [sift_memory_search](#sift_memory_search) · [sift_memory_list](#sift_memory_list) · [sift_memory_update](#sift_memory_update) · [sift_memory_delete](#sift_memory_delete) · [sift_memory_decide](#sift_memory_decide) · [sift_memory_decisions](#sift_memory_decisions) · [sift_memory_supersede](#sift_memory_supersede) · [sift_memory_reflect](#sift_memory_reflect) · [sift_memory_reflections](#sift_memory_reflections) · [sift_memory_reflect_trajectory](#sift_memory_reflect_trajectory) · [sift_memory_trajectory_reflections](#sift_memory_trajectory_reflections) · [sift_memory_link](#sift_memory_link) · [sift_memory_deps](#sift_memory_deps) · [sift_memory_ready](#sift_memory_ready) · [sift_memory_stale](#sift_memory_stale) · [sift_memory_stats](#sift_memory_stats) · [sift_memory_context](#sift_memory_context) · [sift_memory_traverse](#sift_memory_traverse) · [sift_memory_origin](#sift_memory_origin) · [sift_memory_network](#sift_memory_network) · [sift_memory_config](#sift_memory_config) · [sift_memory_tune](#sift_memory_tune) · [sift_memory_backups](#sift_memory_backups) · [sift_memory_restore](#sift_memory_restore) · [sift_memory_import](#sift_memory_import)

### Search & Edit

[sift_search](#sift_search) · [sift_read](#sift_read) · [sift_edit](#sift_edit) · [sift_update](#sift_update) · [sift_write](#sift_write) · [sift_batch](#sift_batch) · [sift_transform](#sift_transform) · [sift_sql](#sift_sql) · [sift_workspace](#sift_workspace)

### Web & Repository

[sift_web_crawl](#sift_web_crawl) · [sift_web_search](#sift_web_search) · [sift_web_query](#sift_web_query) · [sift_web_stats](#sift_web_stats) · [sift_web_refresh](#sift_web_refresh) · [sift_repo_clone](#sift_repo_clone) · [sift_repo_search](#sift_repo_search) · [sift_repo_query](#sift_repo_query)

---

## Memory Tools

<a name="sift_memory_add"></a>
### sift_memory_add
Store patterns, preferences, plans, tasks, or gotchas.

Creates a new memory entry that persists across sessions. Memories are automatically tagged, indexed for search, and checked for conflicts with existing knowledge.

**Types:** `pattern` · `preference` · `plan` · `task` · `gotcha`

```
Remember that in this project we use snake_case for Python and camelCase for JavaScript
```

---

<a name="sift_memory_search"></a>
### sift_memory_search
Full-text search across all memories.

Searches memories using FTS5 full-text search with synonym expansion and relevance scoring. Supports boolean operators (AND, OR, NOT) and phrase queries.

```
What do you remember about our authentication system?
```

---

<a name="sift_memory_list"></a>
### sift_memory_list
List memories by type or status.

Returns memories filtered by type, status, or parent. Useful for seeing all active tasks, all patterns, or steps under a specific plan.

```
Show me all the gotchas you've learned about this codebase
```

---

<a name="sift_memory_update"></a>
### sift_memory_update
Update memory status, priority, or content.

Modifies an existing memory's status (open, in_progress, done), priority, title, or description.

```
Mark the authentication refactor task as complete
```

---

<a name="sift_memory_delete"></a>
### sift_memory_delete
Remove a memory.

Permanently deletes a memory and its associated decisions and links. Use for outdated or incorrect information.

```
Forget what you know about the old API endpoint format, we've changed it
```

---

<a name="sift_memory_decide"></a>
### sift_memory_decide
Record a decision for a plan.

Stores a decision with its rationale, linked to a specific plan. Decisions are queryable later so you can understand why choices were made.

```
We decided to use PostgreSQL instead of MongoDB because we need ACID transactions
```

---

<a name="sift_memory_decisions"></a>
### sift_memory_decisions
Query past decisions.

Search through recorded decisions by plan or keyword. Helps recall why past architectural choices were made.

```
What decisions have we made about the database?
```

---
<a name="sift_memory_supersede"></a>
### sift_memory_supersede
Replace a previous decision.
Updates a decision with a new one while keeping history. The old decision is marked as superseded, creating an audit trail of how thinking evolved.
```
Actually, let's use Redis instead of PostgreSQL for the session store
```
---

<a name="sift_memory_reflect"></a>
### sift_memory_reflect
Log reasoning, observations, or corrections.

Records Claude's thinking process, observations about the codebase, or lessons from corrections. Types: `reasoning`, `observation`, `correction`.

```
That's not right - we use UTC timestamps, not local time. Remember that.
```

---

<a name="sift_memory_reflections"></a>
### sift_memory_reflections
Search past reflections.

Query Claude's logged reflections to understand past reasoning or find patterns in corrections.

```
What corrections have you had to make in this project?
```

---
<a name="sift_memory_reflect_trajectory"></a>
### sift_memory_reflect_trajectory
Reflect on a chain of memories.
Records insights about how work evolved over time—patterns across chains, arc summaries, pivot points, or friction analyses. Types: `trajectory_pattern`, `arc_summary`, `pivot_point`, `friction_analysis`.
```
Looking back at the authentication work, we pivoted from JWT to sessions mid-way through
```
---
<a name="sift_memory_trajectory_reflections"></a>
### sift_memory_trajectory_reflections
Query trajectory reflections.
Search through trajectory reflections to find patterns in how work evolved. Filter by reflection type or chain segment length.
```
What trajectory patterns have you noticed in this project?
```
---

<a name="sift_memory_link"></a>
### sift_memory_link
Create dependencies between memories.

Establishes relationships between memories: `blocks` (task A blocks task B), `related`, or `parent`.

```
The database migration needs to be done before we can deploy the new API
```

---

<a name="sift_memory_deps"></a>
### sift_memory_deps
Query memory dependencies.

Shows what blocks a task or what a task is blocking. Useful for understanding work dependencies.

```
What's blocking the deployment task?
```

---

<a name="sift_memory_ready"></a>
### sift_memory_ready
Find tasks with no blockers.

Returns tasks that have no unfinished dependencies and are ready to work on.

```
What tasks can I work on right now?
```

---

<a name="sift_memory_stale"></a>
### sift_memory_stale
Find old memories that may need review.

Lists memories that haven't been accessed in a specified number of days. Useful for cleanup and review.

```
Are there any old memories we should review or clean up?
```

---

<a name="sift_memory_stats"></a>
### sift_memory_stats
Get memory database statistics.

Shows counts by type and status, active patterns, recent corrections, and database health. Called at session start to load context.

```
Give me an overview of what you remember about this project
```

---
<a name="sift_memory_context"></a>
### sift_memory_context
Generate rich session context.
Traverses the memory chain to build context: journey (origin, milestones), themes, and active work. Call at session start to understand shared history.
```
What's the context of our work together?
```
---
<a name="sift_memory_traverse"></a>
### sift_memory_traverse
Walk the memory chain.
Follows links backwards through memory history, showing how experiences connect. Returns the path with each memory and link type.
```
Show me how we got to this point in the project
```
---
<a name="sift_memory_origin"></a>
### sift_memory_origin
Find the start of a memory chain.
Traverses backwards to find the first memory in a chain. Returns the origin memory and chain length.
```
Where did this line of work begin?
```
---
<a name="sift_memory_network"></a>
### sift_memory_network
Explore memory graph structure.
Analyzes memory connections as a network. Four modes: `hubs` (most connected), `neighbors` (direct connections), `cluster` (related memories), `bridges` (connecting separate areas).
```
What are the central themes in your memory?
```
---

<a name="sift_memory_config"></a>
### sift_memory_config
View ranking weight configuration.

Shows current search ranking weights for frequency, recency, priority, and context boosting.

```
How are memory search results being ranked?
```

---

<a name="sift_memory_tune"></a>
### sift_memory_tune
Adjust search ranking weights.

Modifies how memories are ranked in search results. Requires a rationale for transparency.

```
Prioritize more recent memories in search results
```

---

<a name="sift_memory_backups"></a>
### sift_memory_backups
List memory database backups.

Shows available backups of the memory database, created automatically each session.

```
Are there any memory backups available?
```

---

<a name="sift_memory_restore"></a>
### sift_memory_restore
Restore from a backup.

Restores the memory database from a previous backup. Use if data was accidentally deleted.

```
Restore the memory database from yesterday's backup
```

---

<a name="sift_memory_import"></a>
### sift_memory_import
Import markdown plans into memory.

Converts a markdown file into a memory entry. Useful for migrating existing documentation.

```
Import the ARCHITECTURE.md file as a plan memory
```

---

## Search & Edit Tools

<a name="sift_search"></a>
### sift_search
FTS5 full-text search (30-195x faster than grep).

Searches the indexed workspace using SQLite FTS5. Supports boolean queries (AND, OR, NOT, NEAR), prefix matching, and file filtering. Auto-initializes the index on first use.

```
Find all files that mention both "authentication" and "token"
```

---

<a name="sift_read"></a>
### sift_read
Read files with line numbers.

Reads file contents with line numbers for accurate editing. Supports partial reads with start/end lines and whitespace visualization for debugging.

```
Show me the handleAuth function in auth.js
```

---

<a name="sift_edit"></a>
### sift_edit
Find/replace with fuzzy whitespace matching.

Performs find/replace operations with automatic whitespace normalization. Supports insert, delete, and patch modes. Shows visual diffs of changes.

```
Replace the hardcoded timeout of 5000 with a constant TIMEOUT_MS
```

---

<a name="sift_update"></a>
### sift_update
Simple old_string/new_string replacement.

Straightforward text replacement with clear error messages. Fails if the target string isn't found or isn't unique.

```
Change the function name from processData to processUserData
```

---

<a name="sift_write"></a>
### sift_write
Create or overwrite files.

Creates new files or completely replaces existing file contents. Creates parent directories if needed.

```
Create a new utils.js file with helper functions for date formatting
```

---

<a name="sift_batch"></a>
### sift_batch
Multiple edit operations atomically.

Executes multiple edits as a single atomic operation. All succeed or all fail, preventing partial updates.

```
Rename the "user" variable to "currentUser" in all three files
```

---

<a name="sift_transform"></a>
### sift_transform
SQL-based file transformation.

Transforms file contents using SQL queries with regex_replace, string functions, and more.

```
Convert all console.log statements to use our logger instead
```

---

<a name="sift_sql"></a>
### sift_sql
Run SQL on text input.

Executes SQL queries on piped text input. Useful for filtering, transforming, or analyzing text data.

```
Parse this CSV and show me only rows where the status is "failed"
```

---

<a name="sift_workspace"></a>
### sift_workspace
Manage the search index.

Controls the workspace index: init, status, refresh, or rebuild. The index auto-initializes on first search.

```
Refresh the search index to pick up recent file changes
```

---

## Web & Repository Tools

<a name="sift_web_crawl"></a>
### sift_web_crawl
Crawl and index a website.

Downloads and indexes a website for offline searching. Respects robots.txt, follows links, and deduplicates content. Great for documentation sites.

```
Index the React documentation so you can reference it offline
```

---

<a name="sift_web_search"></a>
### sift_web_search
Search indexed web content.

Full-text search across crawled websites. Supports boolean operators and returns relevant snippets.

```
Search the React docs for information about useEffect cleanup
```

---

<a name="sift_web_query"></a>
### sift_web_query
SQL queries on web content.

Run SQL queries directly on the web content database for advanced filtering and analysis.

```
Find all pages in the docs that mention "deprecated"
```

---

<a name="sift_web_stats"></a>
### sift_web_stats
Web database statistics.

Shows page count, word count, domains indexed, and crawl timestamps for a web database.

```
How much documentation do you have indexed?
```

---

<a name="sift_web_refresh"></a>
### sift_web_refresh
Update stale cached pages.

Re-fetches pages that are older than a specified age. Keeps documentation caches current.

```
Update any cached documentation pages older than a week
```

---

<a name="sift_repo_clone"></a>
### sift_repo_clone
Clone and index a git repository.

Clones a git repository and indexes its source code into a searchable database. Great for exploring unfamiliar codebases.

```
Clone and index the lodash repository so we can study their implementation
```

---

<a name="sift_repo_search"></a>
### sift_repo_search
Search indexed repository.

Full-text search across an indexed repository. Filter by language or file pattern.

```
Search the lodash repo for debounce implementation
```

---

<a name="sift_repo_query"></a>
### sift_repo_query
SQL queries on repository content.

Run SQL queries on indexed repository files. Query by language, line count, file path patterns.

```
Find the largest files in the indexed repository
```

---

## Verify Download

Each release includes `checksums.txt` with SHA256 hashes:
```bash
sha256sum -c checksums.txt
```

## License

Proprietary. Binary distribution only.
