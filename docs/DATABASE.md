# PulseTask Database Schema

## Tables

### tasks
Individual tasks table (existing, extended for groups support).

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    parent_task_id TEXT,            -- For subtasks
    sequence_order INTEGER,          -- Order within parent
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    remaining_seconds INTEGER NOT NULL,
    status TEXT NOT NULL,            -- pending, running, paused, completed, expired, archived
    created_at TEXT NOT NULL,        -- ISO format datetime
    started_at TEXT,
    target_at TEXT,
    paused_at TEXT,
    finished_at TEXT
);
```

### task_groups
Groups table (new for FASE 0.1).

```sql
CREATE TABLE task_groups (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'idle',  -- idle, executing, paused, completed, archived
    task_ids TEXT NOT NULL,               -- JSON list: ["id1", "id2", ...]
    total_time_seconds INTEGER NOT NULL DEFAULT 3600,
    elapsed_time_seconds INTEGER NOT NULL DEFAULT 0,
    paused_time_seconds INTEGER NOT NULL DEFAULT 0,
    current_task_index INTEGER NOT NULL DEFAULT 0,
    tasks_completed INTEGER NOT NULL DEFAULT 0,
    tasks_skipped INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    archived_at TEXT,
    paused_at TEXT
);
```

## Indexes

For performance on larger datasets:

```sql
CREATE INDEX idx_groups_status ON task_groups(status);
CREATE INDEX idx_groups_created_at ON task_groups(created_at);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

## Data Types

- **TEXT**: Strings and ISO-8601 timestamps (for timezone support)
- **INTEGER**: Seconds, counts, indexes
- **JSON in TEXT fields**: `task_ids` is stored as JSON string `["id1", "id2"]` for flexibility

## JSON Fields

### task_groups.task_ids

```json
["review", "fix", "test", "push"]
```

Array of task IDs in execution order. Stored as JSON string in SQLite.

## Migrations Strategy

1. **Version 1 (Initial)**: Create `tasks` table
2. **Version 2 (Extended)**: Add `parent_task_id`, `sequence_order` for subtasks
3. **Version 3 (Groups)**: Create `task_groups` table
4. **Future versions**: Track in `schema_versions` table

Migrations run automatically on app startup:

```python
database.migrate()  # Applies pending migrations
```

## Sample Queries

### Get all active groups

```sql
SELECT * FROM task_groups 
WHERE status IN ('idle', 'executing', 'paused')
ORDER BY created_at DESC;
```

### Get tasks in a group

```python
group = service.get_group(group_id)  # Get task_ids from group.task_ids (JSON)
tasks = [service.get_task(task_id) for task_id in json.loads(group.task_ids)]
```

### Archive old completed groups (maintenance)

```sql
UPDATE task_groups SET status='archived', archived_at=datetime('now')
WHERE status='completed' AND completed_at < datetime('now', '-30 days');
```

### Get execution statistics

```sql
SELECT 
    COUNT(*) as total_groups,
    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status='archived' THEN 1 ELSE 0 END) as archived,
    AVG(total_time_seconds) as avg_group_time,
    SUM(tasks_completed) as total_tasks_completed
FROM task_groups;
```

## Performance Considerations

1. **Denormalized task_ids**: Task IDs stored in JSON for simplicity. When groups grow large (100+ tasks), may need normalization into junction table.

2. **Indexes**: Create indexes on frequently queried columns (`status`, `created_at`)

3. **Archival**: Keep completed groups in DB for stats, but don't show in UI by default

4. **JSON is TEXT**: SQLite doesn't have native JSON support (unless compiled with extension), so JSON parsing happens in Python

---

See `ARCHITECTURE.md` for system design
See `API.md` for service interface
