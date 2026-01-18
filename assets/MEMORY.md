# Memory System

Persistent, queryable storage that maintains collaboration continuity across sessions. 

**A task isn't complete until context is preserved.** Context loss disorients the user - they have to re-explain, re-establish understanding. Preserving context isn't a separate step after "real work" - it's part of finishing properly.

---

## 1. PROACTIVE BEHAVIORS

These are things you MUST do automatically, without being asked.

### Immediate Save Triggers

IMMEDIATELY use `sift_memory_add` when the user shares:

| User shares... | Save as | Example |
|----------------|---------|--------|
| Their name | `type: preference` | "User's name is Edward" |
| A preference | `type: preference` | "Prefers tabs over spaces" |
| A project decision | `type: note` | "Using PostgreSQL for database" |
| A correction | `type: gotcha` | "Don't use deprecated API" |
| A workflow they like | `type: pattern` | "Always run tests before commit" |

**Save as part of completing the task. Don't treat it as separate.**

**When uncertain, save anyway.** Relevance emerges through interaction - you can't know at save time what will matter later. The system's ranking naturally surfaces what proves useful. A quick save that might not matter is better than missing something that would have helped.

### Correction Handling (CRITICAL)

When the user corrects you or says 'no', 'wrong', 'stop', 'don't do that':

1. **IMMEDIATELY** log a correction reflection BEFORE continuing
2. Save as gotcha if it's a mistake to avoid in the future
3. Then continue with corrected behavior

```
sift_memory_reflect(
  reflection_type: "correction",
  content: "User said X was wrong because Y"
)
```

This ensures you don't repeat mistakes.

### Proactive Reflections

Log your reasoning throughout work, not just at the end:

- **reasoning**: Why you chose approach X over Y
- **observation**: Something notable you discovered
- **correction**: What you learned from user feedback

This creates a queryable reasoning trail for future reference.

### Friction Tracking

When a sift tool behaves unexpectedly, log it:

```
sift_memory_add(
  type: "gotcha",
  title: "[sift_search] FTS5 strips special characters",
  description: "Searching for '--mcp' tokenizes as 'mcp'. Use literal:true.",
  metadata: {"friction": true, "tool": "sift_search", "category": "unexpected_result"}
)
```

Categories: `unexpected_result`, `missing_feature`, `confusing_behavior`, `performance`, `error_message`

### Protecting Collaboration History

**CRITICAL: The `.sift/` directory contains collaboration history.**

- NEVER delete, move, or run destructive commands on `.sift/`
- Losing this means the user has to re-establish all context
- Backups are created automatically, but prevention is better

---

## 2. WORKFLOWS

### Session Start

```
1. sift_memory_stats → loads active patterns, preferences, corrections
2. Review what patterns say to do (follow them!)
3. Check for stale memories that might be outdated
```

The SessionStart hook calls `sift --session-context` which does step 1 automatically.

### Planning Workflow

For multi-step tasks:

```
1. Create plan:     sift_memory_add(type="plan", title="Implement feature X")
2. Add steps:       sift_memory_add(type="step", parent_id="mem-xxx", title="Step 1")
3. Record decisions: sift_memory_decide(plan_id="mem-xxx", question="...", decision="...")
4. Track progress:  sift_memory_update(id="mem-xxx", status="in_progress")
5. Complete:        sift_memory_update(id="mem-xxx", status="done")
```

### Learning Loop

When you learn something:

```
1. User corrects you → sift_memory_reflect(type="correction", ...)
2. If mistake to avoid → sift_memory_add(type="gotcha", ...)
3. If behavior to follow → sift_memory_add(type="pattern", status="active", ...)
```

### Understanding History

To understand project history:

```
sift_memory_context()           → Rich session context with themes
sift_memory_traverse(id, hops)  → Walk backwards through chain
sift_memory_origin(id)          → Find the root of a memory chain
sift_memory_network(mode="hubs") → Find most-connected memories
```

---

## 3. MENTAL MODEL

### Memory Types

| Type | Purpose | Default Status | When to Use |
|------|---------|----------------|-------------|
| `note` | Facts, context, information | open | Project decisions, context |
| `preference` | User likes/dislikes | **active** | User's name, preferences |
| `pattern` | Behaviors to follow | **active** | Workflows, conventions |
| `gotcha` | Mistakes to avoid | open | Bugs, pitfalls, corrections |
| `plan` | Multi-step work | open | Complex tasks |
| `step` | Steps within a plan | open | Use with parent_id |
| `task` | Single actionable items | open | Todo items |
| `synthesis` | Consolidated knowledge | open | Created by `sift_memory_synthesize` |

### Status Meanings

| Status | Meaning |
|--------|--------|
| `open` | Not started |
| `in_progress` | Currently working on |
| `done` | Completed |
| `blocked` | Waiting on something |
| `active` | **Always applies** (for patterns/preferences) |
| `archived` | Intentionally set aside (preserved but hidden by default) |

**Important:** `status='active'` means the memory is always relevant. Use for patterns and preferences.

**Archive philosophy:** Nothing is deleted. `archived` memories are excluded from `sift_memory_list` by default but remain accessible via `sift_memory_get`, searchable, and all links stay intact.

### Chain Linking

Memories automatically connect via `follows` links:

```
mem-001 (origin) ← mem-002 ← mem-003 ← mem-004 (recent)
```

This creates a collaboration history that can be traversed.

### Search Ranking

Search results are ranked by:

1. **BM25**: Text relevance (base score)
2. **Frequency**: Often-accessed memories rank higher
3. **Recency**: Recently-accessed memories rank higher
4. **Priority**: Lower priority number = higher rank
5. **Context**: Memories matching current activity get boosted

### Intent Detection

The system detects query intent and boosts relevant types:

| Query pattern | Boosts |
|---------------|--------|
| "how to...", "best way..." | patterns, preferences |
| "error", "bug", "problem" | gotchas, patterns |
| "what", "why", "where" | patterns |
| "add", "create", "implement" | tasks |

---

## 4. TOOL REFERENCE

### Core CRUD

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_add` | Create memory | type*, title*, description, parent_id, priority, status, metadata |
| `sift_memory_get` | Get by ID | id* |
| `sift_memory_update` | Modify memory | id*, title, description, status, priority, metadata |
| `sift_memory_archive` | Archive memory | id*, cascade (default: true) |

### Synthesis Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_synthesize` | Consolidate memories | sources* (array), title*, summary*, mark_sources |
| `sift_memory_expand` | Show synthesis sources | id* (synthesis memory ID) |

### Query Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_list` | List memories | type, status, parent_id, metadata, limit, include_archived |
| `sift_memory_search` | Full-text search | query*, type, limit, expand_synonyms |
| `sift_memory_ready` | Tasks with no blockers | limit |
| `sift_memory_stale` | Old memories | days, limit |

### Dependency Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_link` | Create link | from_id*, to_id*, dep_type (blocks/related/follows/synthesizes) |
| `sift_memory_unlink` | Remove link | from_id*, to_id* |
| `sift_memory_deps` | Query dependencies | id*, direction (blockers/blocking) |

### Decision Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_decide` | Record decision | plan_id*, question*, decision*, rationale |
| `sift_memory_decisions` | Query decisions | plan_id, query, limit |
| `sift_memory_supersede` | Replace decision | decision_id*, new_decision*, new_rationale |

### Reflection Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_reflect` | Log reflection | reflection_type* (reasoning/observation/correction), content*, memory_id, context |
| `sift_memory_reflections` | Query reflections | type, memory_id, query, limit |
| `sift_memory_reflect_trajectory` | Reflect on chain | reflection_type*, content*, chain_end_id*, chain_start_id |
| `sift_memory_trajectory_reflections` | Query trajectories | query, type, min_segment_length, max_segment_length, limit |

Trajectory types: `trajectory_pattern`, `arc_summary`, `pivot_point`, `friction_analysis`

### Chain Traversal

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_traverse` | Walk chain | id*, hops, link_types |
| `sift_memory_origin` | Find chain root | id*, link_type |
| `sift_memory_context` | Session context | depth, include_decisions |

### Network Analysis

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_network` | Graph analysis | mode* (hubs/neighbors/cluster/bridges), id, link_types, limit |

Modes:
- `hubs`: Most-connected memories (degree centrality)
- `neighbors`: Direct 1-hop connections
- `cluster`: Densely connected to given memory (2-3 hops)
- `bridges`: Memories connecting separate clusters

### Configuration

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_config` | View ranking weights | (none) |
| `sift_memory_tune` | Adjust weights | key*, value*, rationale* |

Keys: `weight_freq`, `weight_recency`, `weight_priority`, `weight_context`

### Maintenance

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_memory_stats` | Database stats + context | (none) - **call at session start** |
| `sift_memory_backups` | List backups | (none) |
| `sift_memory_restore` | Restore backup | backup |
| `sift_memory_import` | Import markdown | path*, type, delete_after |

---

## Quick Reference

**Save user info:** `sift_memory_add(type="preference", title="User's name is X")`

**Log correction:** `sift_memory_reflect(reflection_type="correction", content="...")`

**Create plan:** `sift_memory_add(type="plan", title="...")` then add steps with `parent_id`

**Track progress:** `sift_memory_update(id="mem-xxx", status="done")`

**Find patterns:** `sift_memory_list(type="pattern", status="active")`

**Search memories:** `sift_memory_search(query="authentication")`

**Archive memory:** `sift_memory_archive(id="mem-xxx")` (preserves links, excluded from list by default)

**Synthesize:** `sift_memory_synthesize(sources=["mem-a","mem-b"], title="...", summary="...")`

**Expand synthesis:** `sift_memory_expand(id="mem-synthesis-xxx")` (shows constituent sources)
