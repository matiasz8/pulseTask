# PulseTask API Reference

## TaskService

### CRUD Operations

```python
def create_task(title: str, duration_seconds: int, description: str = "") -> Task:
    """Create a new individual task."""

def get_task(task_id: str) -> Task:
    """Get task by ID. Raises ValueError if not found."""

def list_tasks() -> list[Task]:
    """List all non-archived tasks."""

def list_archived_tasks() -> list[Task]:
    """List archived tasks."""

def update_task(task: Task) -> None:
    """Update task in database."""

def delete_task(task_id: str) -> None:
    """Soft delete task (archive it)."""
```

### Execution

```python
def start_task(task_id: str) -> Task:
    """Start task execution, set status to RUNNING."""

def pause_task(task_id: str) -> Task:
    """Pause running task."""

def resume_task(task_id: str) -> Task:
    """Resume paused task."""

def complete_task(task_id: str) -> Task:
    """Mark task as COMPLETED."""

def expire_task(task_id: str) -> Task:
    """Mark task as EXPIRED (time ran out)."""
```

### Statistics

```python
def get_task_stats(task_id: str) -> TaskStats:
    """Get stats for a task (duration, time spent, etc)."""

def get_today_stats() -> DayStats:
    """Get today's statistics (tasks completed, total time, etc)."""
```

## GroupService

### CRUD Operations

```python
def create_group(
    name: str,
    task_ids: list[str],
    total_time_seconds: int = 3600,
    description: str = ""
) -> TaskGroup:
    """Create new task group."""

def get_group(group_id: str) -> TaskGroup | None:
    """Get group by ID, or None if not found."""

def list_groups(
    status: GroupStatus | None = None,
    limit: int = 50,
    offset: int = 0
) -> list[TaskGroup]:
    """List groups with optional filtering and pagination."""

def update_group(group: TaskGroup) -> None:
    """Update group in database."""

def delete_group(group_id: str) -> None:
    """Soft delete group (archive it)."""
```

### Execution

```python
def start_group_execution(group_id: str) -> TaskGroup:
    """Start executing group, set status to EXECUTING."""

def pause_group_execution(group_id: str) -> TaskGroup:
    """Pause group execution."""

def resume_group_execution(group_id: str) -> TaskGroup:
    """Resume paused group."""

def advance_to_next_task(group_id: str) -> str | None:
    """Advance to next task in group.
    
    Returns: ID of next task, or None if group is complete.
    """

def skip_task_in_group(group_id: str) -> str | None:
    """Skip current task and move to next.
    
    Returns: ID of next task after skipped task.
    """
```

### Time Tracking

```python
def update_group_elapsed_time(
    group_id: str,
    elapsed_seconds: int
) -> TaskGroup:
    """Update total elapsed time (called by timer every second)."""
```

## TaskGroup Properties

```python
# All properties are read-only computed values:

group.is_active()           # -> bool: Is group currently executing?
group.is_complete()         # -> bool: All tasks processed?
group.time_remaining_seconds() -> int: Time left for group
group.current_task_id()     # -> str | None: Currently executing task
group.progress_percent()    # -> int (0-100): Group progress %
group.has_next_task()       # -> bool: More tasks to execute?
```

## Error Handling

All service methods raise `ValueError` for invalid states or missing entities:

```python
try:
    task = service.get_task("nonexistent")
except ValueError as e:
    print(f"Task not found: {e}")

try:
    service.start_task("task_id")  # If already running
except ValueError as e:
    print(f"Invalid state: {e}")
```

## Event System (Future)

When implemented, services will emit events:

```python
service.on_task_completed += lambda task: notify(f"Task done: {task.title}")
service.on_time_expired += lambda task: alert(f"Time up: {task.title}")
service.on_group_completed += lambda group: celebrate()
```

---

See `ARCHITECTURE.md` for design overview
See `DATABASE.md` for data schema
