import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date
from pawpal_system import CareTask, Pet, Scheduler, DailyPlan


def test_mark_complete_changes_status():
    """Calling mark_complete() should set completed to True."""
    task = CareTask(
        name="Morning Walk",
        task_type="walk",
        duration_minutes=30,
        priority=1,
    )
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age_years=3, weight_lbs=65.0)
    initial_count = len(pet.tasks)
    pet.add_task(CareTask(name="Fetch", task_type="enrichment", duration_minutes=20, priority=2))
    assert len(pet.tasks) == initial_count + 1


# ---------------------------------------------------------------------------
# Sorting Correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks should come back in ascending start_time order, untimed tasks last."""
    scheduler = Scheduler()
    tasks = [
        CareTask(name="Evening Meds",  task_type="meds",  duration_minutes=5,  priority=2, start_time=1080),  # 18:00
        CareTask(name="Morning Walk",  task_type="walk",  duration_minutes=30, priority=1, start_time=480),   # 08:00
        CareTask(name="Midday Feed",   task_type="feed",  duration_minutes=10, priority=1, start_time=720),   # 12:00
        CareTask(name="Anytime Bath",  task_type="groom", duration_minutes=20, priority=3),                   # no time
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)

    timed = [t for t in sorted_tasks if t.start_time is not None]
    untimed = [t for t in sorted_tasks if t.start_time is None]

    # Timed tasks must be in ascending order
    assert [t.start_time for t in timed] == sorted(t.start_time for t in timed)
    # Untimed tasks must come after all timed ones
    assert sorted_tasks.index(untimed[0]) > sorted_tasks.index(timed[-1])


def test_daily_plan_sort_by_time_chronological():
    """DailyPlan.sort_by_time() must return tasks ordered earliest to latest."""
    plan = DailyPlan(plan_date=date(2026, 4, 1))
    plan.add_task(CareTask(name="Lunch",   task_type="feed", duration_minutes=10, priority=2, start_time=720))
    plan.add_task(CareTask(name="Sunrise", task_type="walk", duration_minutes=20, priority=1, start_time=360))
    plan.add_task(CareTask(name="Dinner",  task_type="feed", duration_minutes=10, priority=2, start_time=1080))

    ordered = plan.sort_by_time()
    start_times = [t.start_time for t in ordered]
    assert start_times == sorted(start_times), f"Expected ascending order, got {start_times}"


# ---------------------------------------------------------------------------
# Recurrence Logic
# ---------------------------------------------------------------------------

def test_complete_daily_task_creates_next_day_occurrence():
    """Completing a daily recurring task via Scheduler must produce a new task
    dated exactly one day after the reference date."""
    scheduler = Scheduler()
    today = date(2026, 4, 1)
    task = CareTask(
        name="Daily Walk",
        task_type="walk",
        duration_minutes=30,
        priority=1,
        recurrence="daily",
        scheduled_date=today,
    )

    next_task = scheduler.complete_recurring_task(task, from_date=today)

    assert task.completed is True, "Original task should be marked complete"
    assert next_task is not None, "A next occurrence should be returned for a daily task"
    assert next_task.scheduled_date == today + __import__("datetime").timedelta(days=1)
    assert next_task.completed is False, "Next occurrence should start incomplete"
    assert next_task.task_id != task.task_id, "Next occurrence must have a new ID"


def test_non_recurring_task_returns_none_on_complete():
    """Completing a non-recurring task should return None (no follow-up task)."""
    scheduler = Scheduler()
    task = CareTask(name="One-time Vet Visit", task_type="meds", duration_minutes=60, priority=1)

    next_task = scheduler.complete_recurring_task(task, from_date=date(2026, 4, 1))

    assert task.completed is True
    assert next_task is None


# ---------------------------------------------------------------------------
# Conflict Detection
# ---------------------------------------------------------------------------

def test_scheduler_detects_overlapping_tasks():
    """Scheduler.detect_conflicts() should flag tasks whose time windows overlap."""
    scheduler = Scheduler()
    # Task A: 08:00–08:30 (start=480, duration=30)
    # Task B: 08:20–08:40 (start=500, duration=20) — overlaps with A by 10 min
    task_a = CareTask(name="Morning Walk", task_type="walk", duration_minutes=30, priority=1,
                      pet_name="Buddy", start_time=480)
    task_b = CareTask(name="Morning Feed", task_type="feed", duration_minutes=20, priority=1,
                      pet_name="Buddy", start_time=500)

    conflicts = scheduler.detect_conflicts([task_a, task_b])

    assert len(conflicts) == 1, f"Expected 1 conflict, got {len(conflicts)}"
    conflict = conflicts[0]
    assert {conflict.task_a.name, conflict.task_b.name} == {"Morning Walk", "Morning Feed"}


def test_scheduler_no_conflict_for_sequential_tasks():
    """Tasks that start exactly when the previous one ends should NOT conflict."""
    scheduler = Scheduler()
    # Task A: 08:00–08:30 (start=480, duration=30)
    # Task B: 08:30–09:00 (start=510) — starts right as A finishes
    task_a = CareTask(name="Walk",  task_type="walk", duration_minutes=30, priority=1,
                      pet_name="Buddy", start_time=480)
    task_b = CareTask(name="Feed",  task_type="feed", duration_minutes=30, priority=1,
                      pet_name="Buddy", start_time=510)

    conflicts = scheduler.detect_conflicts([task_a, task_b])

    assert conflicts == [], f"Expected no conflicts for sequential tasks, got {conflicts}"


def test_scheduler_conflict_flags_same_pet():
    """same_pet flag should be True when both conflicting tasks belong to the same pet."""
    scheduler = Scheduler()
    task_a = CareTask(name="Walk", task_type="walk", duration_minutes=60, priority=1,
                      pet_name="Buddy", start_time=480)
    task_b = CareTask(name="Bath", task_type="groom", duration_minutes=30, priority=2,
                      pet_name="Buddy", start_time=500)

    conflicts = scheduler.detect_conflicts([task_a, task_b])

    assert len(conflicts) == 1
    assert conflicts[0].same_pet is True
