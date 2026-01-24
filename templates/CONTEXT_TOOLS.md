<!-- sift-template-0.12.0-alpha-alpha-alpha -->
# Context Preservation Tools

Preserve conversation history across context window compactions. Two-tier architecture: hot storage (context.db) for active sessions, cold storage (context_archive.db) for archived verbatim.

---

## 1. ARCHITECTURE

### Storage Tiers

| Tier | Database | Contains | Query Speed |
|------|----------|----------|-------------|
| Hot | `.sift/context.db` | Active sessions, messages, tool calls | Fast (FTS5) |
| Cold | `.sift/context_archive.db` | Archived verbatim conversations | Archive retrieval |

### Data Flow

```
Active conversation → sift_context_save → context.db (hot)
                                              ↓
                              sift_context_synthesize → summary stored
                                              ↓
                              sift_context_archive → context_archive.db (cold)
```

---

## 2. SESSION MANAGEMENT

Sessions track conversation boundaries.

### Start a Session

```
sift_context_session(action: "start", project_path: "/path/to/project")
→ Returns: {"session_id": "ctx-1705432100-12345", "started_at": ...}
```

### End a Session

```
sift_context_session(action: "end", session_id: "ctx-...")
→ Marks session ended, records end timestamp
```

### Get Current Session

```
sift_context_session(action: "current")
→ Returns most recent active session or null
```

### Get Session by ID

```
sift_context_session(action: "get", session_id: "ctx-...")
→ Returns full session details
```

---

## 3. SAVING CONTEXT

### Save a Message

```
sift_context_save(
  session_id: "ctx-...",
  type: "message",
  role: "user",           # or "assistant", "system"
  content: "message text",
  token_estimate: 150,    # optional
  context_percent: 45.5   # optional - % of context window used
)
```

### Save a Tool Call

```
sift_context_save(
  session_id: "ctx-...",
  type: "tool",
  message_id: 42,         # parent message ID
  tool_name: "sift_search",
  arguments: "{\"pattern\": \"error\"}",
  result: "{\"matches\": [...]}"
)
```

---

## 4. SEARCHING HISTORY

### Full-Text Search

```
sift_context_search(query: "authentication AND error")
→ FTS5 boolean search across all messages
```

### Filter by Session

```
sift_context_search(query: "database", session_id: "ctx-...")
→ Search within specific session
```

### SQL Query

```
sift_context_query(sql: "SELECT role, content FROM messages WHERE session_id = 'ctx-...' ORDER BY sequence")
```

Available tables:
- `sessions`: id, started_at, ended_at, project_path, summary, synthesized_at, archive_ref
- `messages`: id, session_id, role, content, timestamp, sequence, token_estimate, context_percent
- `tool_calls`: id, message_id, tool_name, arguments, result, timestamp
- `context_memory_links`: message_id, memory_id, link_type, created_at
- `compaction_events`: id, session_id, compacted_at, messages_before, messages_after, context_percent

---

## 5. CONTEXT-MEMORY LINKING

Link conversation moments to memory entries for bidirectional navigation.

```
sift_context_link(
  message_id: 42,
  memory_id: "mem-abc123",
  link_type: "created_from"   # or "referenced", "triggered_by"
)
```

This enables:
- Finding which conversation created a memory
- Finding which memories were discussed in a session
- Tracing the provenance of decisions

---

## 6. SYNTHESIS PIPELINE

Before archiving, create a summary for quick retrieval.

```
sift_context_synthesize(
  session_id: "ctx-...",
  summary: "Implemented authentication system. Key decisions: JWT over sessions, 1-hour expiry. Created 3 memories for auth patterns."
)
```

The summary is stored in the session record and remains in hot storage even after archival.

---

## 7. ARCHIVE PIPELINE

Move verbatim messages to cold storage while keeping summary accessible.

```
sift_context_archive(session_id: "ctx-...")
```

This:
1. Copies all messages/tool_calls to context_archive.db
2. Removes verbatim from context.db
3. Keeps session record with summary in context.db
4. Sets archive_ref pointing to cold storage

---

## 8. STATISTICS

```
sift_context_stats()
→ Returns: session counts, message counts, storage size, current session info
```

---

## 9. WORKFLOW EXAMPLES

### Full Session Lifecycle

```
# 1. Start session
sift_context_session(action: "start", project_path: "/home/user/project")

# 2. Save messages as conversation progresses
sift_context_save(session_id: "ctx-...", type: "message", role: "user", content: "...")
sift_context_save(session_id: "ctx-...", type: "message", role: "assistant", content: "...")

# 3. Link important moments to memory
sift_context_link(message_id: 5, memory_id: "mem-decision123", link_type: "created_from")

# 4. Before context compaction, synthesize
sift_context_synthesize(session_id: "ctx-...", summary: "Session summary...")

# 5. Archive old sessions
sift_context_archive(session_id: "ctx-...")
```

### Searching Past Work

```
# Find all discussions about authentication
sift_context_search(query: "authentication OR auth OR login")

# Find what led to a specific memory
sift_context_query(sql: "
  SELECT m.content, m.role, m.timestamp
  FROM messages m
  JOIN context_memory_links l ON m.id = l.message_id
  WHERE l.memory_id = 'mem-abc123'
  ORDER BY m.timestamp
")
```

---

## 10. TOOL REFERENCE

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sift_context_session` | Manage sessions | action* (start/end/get/current), session_id, project_path |
| `sift_context_save` | Save message/tool | session_id*, type* (message/tool), role, content, tool_name, arguments, result |
| `sift_context_save` | Save message/tool | session_id*, type*, + type-specific params |
| `sift_context_search` | FTS5 search | query*, session_id, limit |
| `sift_context_query` | SQL query | sql*, format (json/plain/csv) |
| `sift_context_link` | Link to memory | message_id*, memory_id*, link_type |
| `sift_context_synthesize` | Create summary | session_id*, summary* |
| `sift_context_archive` | Move to cold | session_id* |
| `sift_context_stats` | Database stats | (none) |
