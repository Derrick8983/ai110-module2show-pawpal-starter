"""
PawPal+ Logic Layer
Backend classes for pet care scheduling.
"""

from dataclasses import dataclass, field
from datetime import date
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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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

    def get_summary(self) -> str:
        """Return a human-readable summary of the plan."""
        if not self.tasks:
            return "No tasks scheduled for today."
        lines = [f"Daily Plan for {self.date} ({self.total_time_used()} min total):"]
        for task in self.tasks:
            status = "✓" if task.completed else "○"
            pet = f" [{task.pet_name}]" if task.pet_name else ""
            lines.append(f"  {status} {task.name}{pet} — {task.duration_minutes} min (priority {task.priority})")
        if self.reasoning:
            lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, strategy: str = "priority"):
        self.strategy = strategy   # "priority" | "shortest_first" | "balanced"

    def generate_plan(self, owner: PetOwner, tasks: Optional[List[CareTask]] = None) -> DailyPlan:
        """Build and return a DailyPlan within the owner's time_available_minutes."""
        all_tasks = tasks if tasks is not None else owner.get_tasks()
        pending = [t for t in all_tasks if not t.completed]
        sorted_tasks = self.prioritize_tasks(pending)
        plan = DailyPlan()
        for task in sorted_tasks:
            if plan.total_time_used() + task.duration_minutes <= owner.time_available_minutes:
                plan.add_task(task)
        plan.reasoning = self.explain_plan(plan)
        return plan

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
