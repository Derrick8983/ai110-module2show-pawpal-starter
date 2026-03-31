"""
PawPal+ Logic Layer
Backend classes for pet care scheduling.
"""

from dataclasses import dataclass, field
from copy import copy as _copy
from datetime import date, timedelta
from typing import List, Optional
import uuid


# ---------------------------------------------------------------------------
# Dataclasses — simple data-holding objects
# ---------------------------------------------------------------------------

@dataclass
class CareTask:
    name: str
    task_type: str          # e.g. "walk", "feed", "meds", "groom", "enrichment"
    duration_minutes: int
    priority: int           # 1 (highest) – 5 (lowest)
    completed: bool = False
    pet_name: Optional[str] = None
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_time: Optional[int] = None          # minutes from midnight (e.g. 480 = 8:00 AM)
    recurrence: Optional[str] = None          # None | "daily" | "weekly"
    recurrence_days: List[int] = field(default_factory=list)  # 0=Mon … 6=Sun (weekly only)
    scheduled_date: Optional[date] = None     # the date this instance is due

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self, from_date: date) -> Optional["CareTask"]:
        """Return a fresh copy of this task scheduled for its next occurrence.

        - "daily"  → next day after from_date.
        - "weekly" → next matching weekday in recurrence_days after from_date
                     (if recurrence_days is empty, treats every day as valid).
        - non-recurring → returns None.
        """
        if self.recurrence == "daily":
            next_date = from_date + timedelta(days=1)
        elif self.recurrence == "weekly":
            days = sorted(self.recurrence_days) if self.recurrence_days else list(range(7))
            current_wd = from_date.weekday()
            future = [d for d in days if d > current_wd]
            days_ahead = future[0] - current_wd if future else 7 - current_wd + days[0]
            next_date = from_date + timedelta(days=days_ahead)
        else:
            return None

        clone = _copy(self)
        clone.task_id = str(uuid.uuid4())[:8]
        clone.completed = False
        clone.scheduled_date = next_date
        return clone

    def to_dict(self) -> dict:
        """Return a dictionary representation of this task."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "task_type": self.task_type,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "completed": self.completed,
            "pet_name": self.pet_name,
            "start_time": self.start_time,
            "recurrence": self.recurrence,
            "recurrence_days": self.recurrence_days,
        }


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age_years: int
    weight_lbs: float
    tasks: List[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet by task ID."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_default_tasks(self) -> List[CareTask]:
        """Return a baseline list of tasks based on species."""
        defaults = []
        if self.species.lower() == "dog":
            defaults = [
                CareTask("Morning Walk", "walk", 30, 1, pet_name=self.name),
                CareTask("Feeding", "feed", 10, 1, pet_name=self.name),
                CareTask("Evening Walk", "walk", 20, 2, pet_name=self.name),
            ]
        elif self.species.lower() == "cat":
            defaults = [
                CareTask("Feeding", "feed", 10, 1, pet_name=self.name),
                CareTask("Litter Box", "groom", 5, 2, pet_name=self.name),
                CareTask("Playtime", "enrichment", 15, 3, pet_name=self.name),
            ]
        self.tasks.extend(defaults)
        return defaults

    def get_pending_tasks(self) -> List[CareTask]:
        """Return all incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> List[CareTask]:
        """Return all completed tasks for this pet."""
        return [t for t in self.tasks if t.completed]


# ---------------------------------------------------------------------------
# Regular classes — objects with richer behavior
# ---------------------------------------------------------------------------

class PetOwner:
    def __init__(
        self,
        name: str,
        email: str,
        time_available_minutes: int,
        preferences: Optional[List[str]] = None,
    ):
        self.name = name
        self.email = email
        self.time_available_minutes = time_available_minutes
        self.preferences: List[str] = preferences or []
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet and automatically load its default tasks."""
        self.pets.append(pet)
        if not pet.tasks:
            pet.get_default_tasks()

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_tasks(self) -> List[CareTask]:
        """Return all tasks across every pet."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return a pet by name, or None if not found."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None


class CareTaker:
    def __init__(
        self,
        name: str,
        role: str,               # e.g. "vet", "groomer", "dog walker"
        contact: str,
        specialties: Optional[List[str]] = None,
    ):
        self.name = name
        self.role = role
        self.contact = contact
        self.specialties: List[str] = specialties or []
        self.assigned_tasks: List[CareTask] = []

    def assign_task(self, task: CareTask) -> None:
        """Assign a care task to this caretaker."""
        if task not in self.assigned_tasks:
            self.assigned_tasks.append(task)

    def get_assigned_tasks(self) -> List[CareTask]:
        """Return all tasks assigned to this caretaker."""
        return self.assigned_tasks

    def complete_task(self, task_id: str) -> None:
        """Mark an assigned task as complete by task ID."""
        for task in self.assigned_tasks:
            if task.task_id == task_id:
                task.mark_complete()
                break


class DailyPlan:
    def __init__(self, plan_date: Optional[date] = None):
        self.date: date = plan_date or date.today()
        self.tasks: List[CareTask] = []
        self.reasoning: str = ""

    def add_task(self, task: CareTask) -> None:
        """Add a task to this plan."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this plan by its ID."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def total_time_used(self) -> int:
        """Return the sum of all task durations in minutes."""
        return sum(t.duration_minutes for t in self.tasks)

    def sort_by_time(self) -> List[CareTask]:
        """Return tasks sorted by start_time; tasks with no start_time come last."""
        timed = sorted(
            [t for t in self.tasks if t.start_time is not None],
            key=lambda t: t.start_time,
        )
        untimed = [t for t in self.tasks if t.start_time is None]
        return timed + untimed

    def filter_by_pet(self, pet_name: str) -> List[CareTask]:
        """Return only tasks that belong to the named pet."""
        return [t for t in self.tasks if t.pet_name == pet_name]

    def filter_by_status(self, completed: bool) -> List[CareTask]:
        """Return tasks matching the given completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def detect_conflicts(self) -> List[tuple]:
        """Return pairs of tasks whose scheduled time windows overlap.

        Only tasks that have a start_time are considered. A conflict occurs
        when task B starts before task A finishes.
        """
        timed = sorted(
            [t for t in self.tasks if t.start_time is not None],
            key=lambda t: t.start_time,
        )
        conflicts = []
        for i, a in enumerate(timed):
            a_end = a.start_time + a.duration_minutes
            for b in timed[i + 1:]:
                if b.start_time < a_end:
                    conflicts.append((a, b))
                else:
                    break  # timed is sorted; no further overlaps possible with a
        return conflicts

    def get_summary(self) -> str:
        """Return a human-readable summary of the plan, ordered by start time."""
        if not self.tasks:
            return "No tasks scheduled for today."
        lines = [f"Daily Plan for {self.date} ({self.total_time_used()} min total):"]
        for task in self.sort_by_time():
            status = "✓" if task.completed else "○"
            pet = f" [{task.pet_name}]" if task.pet_name else ""
            if task.start_time is not None:
                h, m = divmod(task.start_time, 60)
                time_str = f" @{h:02d}:{m:02d}"
            else:
                time_str = ""
            lines.append(
                f"  {status} {task.name}{pet}{time_str}"
                f" — {task.duration_minutes} min (priority {task.priority})"
            )
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\n⚠ Conflicts detected:")
            for a, b in conflicts:
                lines.append(f"  '{a.name}' overlaps with '{b.name}'")
        if self.reasoning:
            lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)


@dataclass
class Conflict:
    task_a: "CareTask"
    task_b: "CareTask"
    same_pet: bool          # True when both tasks belong to the same pet

    def __str__(self) -> str:
        scope = "same-pet" if self.same_pet else "cross-pet"
        a_time = _fmt_time(self.task_a.start_time)
        b_time = _fmt_time(self.task_b.start_time)
        return (
            f"[{scope}] '{self.task_a.name}' ({self.task_a.pet_name} @{a_time}) "
            f"overlaps '{self.task_b.name}' ({self.task_b.pet_name} @{b_time})"
        )


def _fmt_time(minutes: Optional[int]) -> str:
    """Convert minutes-from-midnight to HH:MM, or '--:--' if None."""
    if minutes is None:
        return "--:--"
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"


class Scheduler:
    def __init__(self, strategy: str = "priority"):
        self.strategy = strategy   # "priority" | "shortest_first" | "balanced"

    def expand_recurring_tasks(
        self, tasks: List[CareTask], plan_date: date
    ) -> List[CareTask]:
        """Filter tasks to those that should run on plan_date.

        - Non-recurring tasks are always included.
        - "daily" tasks are included every day.
        - "weekly" tasks are included only when plan_date's weekday (0=Mon, 6=Sun)
          appears in recurrence_days (or recurrence_days is empty, meaning every day).
        """
        result = []
        for task in tasks:
            if task.recurrence is None:
                result.append(task)
            elif task.recurrence == "daily":
                result.append(task)
            elif task.recurrence == "weekly":
                if not task.recurrence_days or plan_date.weekday() in task.recurrence_days:
                    result.append(task)
        return result

    def complete_recurring_task(
        self,
        task: CareTask,
        from_date: Optional[date] = None,
    ) -> Optional[CareTask]:
        """Mark task complete and return the next occurrence if it recurs.

        Args:
            task:       The task to complete.
            from_date:  The reference date for computing the next occurrence.
                        Defaults to today.

        Returns:
            A new CareTask instance for the next occurrence, or None if the
            task does not recur.
        """
        task.mark_complete()
        return task.next_occurrence(from_date or date.today())

    def detect_conflicts(self, tasks: List[CareTask]) -> List[Conflict]:
        """Return all pairs of tasks whose scheduled time windows overlap.

        Only tasks with a start_time are evaluated. Each returned Conflict
        carries a same_pet flag so callers can distinguish:
          - same-pet conflicts  (owner double-booked for one animal)
          - cross-pet conflicts (two animals need attention simultaneously)
        """
        timed = sorted(
            [t for t in tasks if t.start_time is not None],
            key=lambda t: t.start_time,
        )
        conflicts = []
        for i, a in enumerate(timed):
            a_end = a.start_time + a.duration_minutes
            for b in timed[i + 1:]:
                if b.start_time >= a_end:
                    break  # sorted order — no more overlaps possible with a
                conflicts.append(
                    Conflict(
                        task_a=a,
                        task_b=b,
                        same_pet=(a.pet_name == b.pet_name),
                    )
                )
        return conflicts

    def generate_plan(self, owner: PetOwner, tasks: Optional[List[CareTask]] = None) -> DailyPlan:
        """Build and return a DailyPlan within the owner's time_available_minutes."""
        plan = DailyPlan()
        all_tasks = tasks if tasks is not None else owner.get_tasks()
        active = self.expand_recurring_tasks(all_tasks, plan.date)
        pending = [t for t in active if not t.completed]
        sorted_tasks = self.prioritize_tasks(pending)
        for task in sorted_tasks:
            if plan.total_time_used() + task.duration_minutes <= owner.time_available_minutes:
                plan.add_task(task)
        plan.reasoning = self.explain_plan(plan)
        return plan

    def filter_tasks(
        self,
        tasks: List[CareTask],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[CareTask]:
        """Return tasks matching all supplied criteria.

        Args:
            tasks:      The task list to filter.
            pet_name:   If given, keep only tasks whose pet_name matches.
            completed:  If True, keep only completed tasks.
                        If False, keep only pending tasks.
                        If None, keep all regardless of status.
        """
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def sort_by_time(self, tasks: List[CareTask]) -> List[CareTask]:
        """Return tasks sorted by start_time; tasks with no start_time come last."""
        timed = sorted(
            [t for t in tasks if t.start_time is not None],
            key=lambda t: t.start_time,
        )
        untimed = [t for t in tasks if t.start_time is None]
        return timed + untimed

    def prioritize_tasks(self, tasks: List[CareTask]) -> List[CareTask]:
        """Return tasks sorted according to the current strategy."""
        if self.strategy == "priority":
            return sorted(tasks, key=lambda t: t.priority)
        elif self.strategy == "shortest_first":
            return sorted(tasks, key=lambda t: t.duration_minutes)
        elif self.strategy == "balanced":
            # Sort by a combined score: weight priority heavily, break ties by duration
            return sorted(tasks, key=lambda t: (t.priority, t.duration_minutes))
        return tasks

    def check_constraints(self, plan: DailyPlan, owner: PetOwner) -> bool:
        """Return True if the plan fits within the owner's available time."""
        return plan.total_time_used() <= owner.time_available_minutes

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return a natural-language explanation of why tasks were chosen."""
        if not plan.tasks:
            return "No tasks could be scheduled within the available time."
        task_names = ", ".join(t.name for t in plan.tasks)
        total = plan.total_time_used()
        return (
            f"Selected {len(plan.tasks)} task(s) ({task_names}) totaling {total} minutes, "
            f"ordered by '{self.strategy}' strategy."
        )
