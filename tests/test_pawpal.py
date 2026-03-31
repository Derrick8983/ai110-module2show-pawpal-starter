import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import CareTask, Pet


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
