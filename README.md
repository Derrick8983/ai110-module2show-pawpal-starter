# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

### Priority-based scheduling
The `Scheduler` selects tasks greedily from highest to lowest priority until the owner's available time is exhausted. Three strategies are supported — `"priority"` (by priority number), `"shortest_first"` (by duration), and `"balanced"` (priority first, duration as tiebreaker) — controlled by the `strategy` parameter at construction time.

### Sorting by time
`Scheduler.sort_by_time(tasks)` performs a stable sort of any task list by `start_time` (stored as minutes from midnight, e.g. `480` = 08:00). Tasks with no `start_time` are appended at the end. `DailyPlan.get_summary()` calls this automatically so every printed schedule reads chronologically regardless of insertion order.

### Filtering by pet or completion status
`Scheduler.filter_tasks(tasks, pet_name, completed)` applies up to two independent filters in one pass. Either argument can be omitted to skip that axis. Matching tasks for a single pet, only pending work, or a specific pet's completed tasks all use the same method:
```python
scheduler.filter_tasks(tasks, pet_name="Luna", completed=False)
```

### Daily and weekly recurrence
`CareTask` carries `recurrence` (`"daily"` / `"weekly"`) and `recurrence_days` (list of weekday ints, 0 = Monday). Before building a plan, `Scheduler.expand_recurring_tasks(tasks, plan_date)` drops tasks not due on that date. When a recurring task is marked done, `Scheduler.complete_recurring_task(task, from_date)` marks it complete and returns a fresh clone with a new `task_id`, `completed=False`, and `scheduled_date` set to the next valid occurrence date.

### Conflict detection
`Scheduler.detect_conflicts(tasks)` sorts timed tasks by `start_time` and sweeps forward to find every pair whose windows overlap (`task_b.start_time < task_a.start_time + task_a.duration_minutes`). Each result is a `Conflict` dataclass with `task_a`, `task_b`, and a `same_pet` boolean so callers can separately surface double-booked single-animal conflicts from simultaneous multi-pet demands.

### Plan explanation
After selecting tasks, `Scheduler.explain_plan(plan)` writes a plain-English summary of how many tasks were chosen, their names, total time, and which strategy was used. This is stored in `DailyPlan.reasoning` and printed at the bottom of every schedule.

---

## Smarter Scheduling

The scheduling logic in `pawpal_system.py` goes beyond a basic priority sort. Four capabilities were added to `CareTask`, `DailyPlan`, and `Scheduler`:

### Sort by time
`Scheduler.sort_by_time(tasks)` orders any list of `CareTask` objects by their `start_time` (minutes from midnight). Tasks without a `start_time` are placed at the end. `DailyPlan.get_summary()` uses this automatically so the printed schedule always reads chronologically.

### Filter by pet or status
`Scheduler.filter_tasks(tasks, pet_name=None, completed=None)` narrows a task list by one or both criteria. Pass a pet name, a completion flag (`True`/`False`), or both together:

```python
# Buddy's pending tasks only
scheduler.filter_tasks(tasks, pet_name="Buddy", completed=False)
```

### Recurring tasks
`CareTask` now has `recurrence` (`"daily"` or `"weekly"`) and `recurrence_days` (list of weekday ints, 0 = Monday) fields. `Scheduler.expand_recurring_tasks(tasks, plan_date)` filters the task list to only those due on a given date before building the plan. When a recurring task is completed, `Scheduler.complete_recurring_task(task, from_date)` marks it done and returns a fresh copy scheduled for the next occurrence.

### Conflict detection
`Scheduler.detect_conflicts(tasks)` returns a list of `Conflict` objects for any tasks whose time windows overlap. Each `Conflict` carries a `same_pet` flag so you can distinguish a double-booked single animal from two pets needing simultaneous attention:

```python
conflicts = scheduler.detect_conflicts(owner.get_tasks())
same_pet  = [c for c in conflicts if c.same_pet]
cross_pet = [c for c in conflicts if not c.same_pet]
```

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

python -m pytest
platform linux -- Python 3.12.1, pytest-9.0.2, pluggy-1.6.0
rootdir: /workspaces/ai110-module2show-pawpal-starter
plugins: anyio-4.11.0
collected 9 items                                                                                                                                   

tests/test_pawpal.py .....
5 stars