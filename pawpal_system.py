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
class Pet:
    name: str
    species: str
    breed: str
    age_years: int
    weight_lbs: float

    def get_default_tasks(self) -> List["CareTask"]:
        """Return a baseline list of tasks common to this pet type."""
        pass


@dataclass
class CareTask:
    name: str
    task_type: str          # e.g. "walk", "feed", "meds", "groom", "enrichment"
    duration_minutes: int
    priority: int           # 1 (highest) – 5 (lowest)
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def to_dict(self) -> dict:
        """Return a dictionary representation of this task."""
        pass


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
        self.tasks: List[CareTask] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's profile."""
        pass

    def get_tasks(self) -> List[CareTask]:
        """Return all care tasks created by this owner."""
        pass


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
        pass

    def get_assigned_tasks(self) -> List[CareTask]:
        """Return all tasks assigned to this caretaker."""
        pass


class DailyPlan:
    def __init__(self, plan_date: Optional[date] = None):
        self.date: date = plan_date or date.today()
        self.tasks: List[CareTask] = []
        self.reasoning: str = ""

    def add_task(self, task: CareTask) -> None:
        """Add a task to this plan."""
        pass

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this plan by its ID."""
        pass

    def total_time_used(self) -> int:
        """Return the sum of all task durations in minutes."""
        pass

    def get_summary(self) -> str:
        """Return a human-readable summary of the plan."""
        pass


class Scheduler:
    def __init__(self, max_minutes: int, strategy: str = "priority"):
        self.max_minutes = max_minutes
        self.strategy = strategy   # "priority" | "shortest_first" | "balanced"

    def generate_plan(self, owner: PetOwner, tasks: List[CareTask]) -> DailyPlan:
        """Build and return a DailyPlan within the owner's time constraints."""
        pass

    def prioritize_tasks(self, tasks: List[CareTask]) -> List[CareTask]:
        """Return tasks sorted according to the current strategy."""
        pass

    def check_constraints(self, plan: DailyPlan) -> bool:
        """Return True if the plan fits within max_minutes."""
        pass

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return a natural-language explanation of why tasks were chosen."""
        pass
