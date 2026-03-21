"""
PawPal+ System Tests
Unit tests for core scheduling functionality using pytest.
Run with: python -m pytest tests/test_pawpal.py -v
"""

import pytest
from pawpal_system import (
    Owner, Pet, Task, Scheduler, Priority, Species,
    TaskStatus, DailyPlan, ScheduledTask
)


class TestTask:
    """Test Task class functionality"""

    def test_task_creation(self):
        """Verify task can be created with correct attributes"""
        task = Task("Morning walk", 20, Priority.HIGH)
        assert task.task_name == "Morning walk"
        assert task.duration_minutes == 20
        assert task.priority == Priority.HIGH
        assert task.status == TaskStatus.PENDING

    def test_task_completion(self):
        """Verify that calling mark_completed() changes task status to COMPLETED"""
        task = Task("Breakfast", 10, Priority.MEDIUM)

        # Initially should be PENDING
        assert task.status == TaskStatus.PENDING

        # After marking complete
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED

    def test_task_skip(self):
        """Verify that calling mark_skipped() changes task status to SKIPPED"""
        task = Task("Playtime", 30, Priority.HIGH)

        task.mark_skipped()
        assert task.status == TaskStatus.SKIPPED

    def test_task_reset(self):
        """Verify that calling reset() returns task to PENDING status"""
        task = Task("Walk", 20, Priority.MEDIUM)
        task.mark_completed()

        task.reset()
        assert task.status == TaskStatus.PENDING

    def test_get_priority(self):
        """Verify get_priority() returns correct priority"""
        task = Task("Task", 15, Priority.HIGH)
        assert task.get_priority() == Priority.HIGH

    def test_get_duration(self):
        """Verify get_duration() returns correct duration"""
        task = Task("Task", 25, Priority.LOW)
        assert task.get_duration() == 25


class TestPet:
    """Test Pet class functionality"""

    def test_pet_creation(self):
        """Verify pet can be created with correct attributes"""
        pet = Pet("Mochi", Species.DOG)
        assert pet.pet_name == "Mochi"
        assert pet.species == Species.DOG
        assert len(pet.get_all_tasks()) == 0

    def test_task_addition(self):
        """Verify that adding a task to a Pet increases that pet's task count"""
        pet = Pet("Whiskers", Species.CAT)
        initial_count = len(pet.get_all_tasks())

        task = Task("Nap", 20, Priority.LOW)
        pet.add_task(task)

        # Task count should increase by 1
        assert len(pet.get_all_tasks()) == initial_count + 1
        assert task in pet.get_all_tasks()

    def test_add_multiple_tasks(self):
        """Verify adding multiple tasks"""
        pet = Pet("Buddy", Species.DOG)

        task1 = Task("Walk", 20, Priority.HIGH)
        task2 = Task("Eat", 10, Priority.MEDIUM)
        task3 = Task("Play", 30, Priority.HIGH)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        assert len(pet.get_all_tasks()) == 3

    def test_remove_task(self):
        """Verify removing a task decreases task count"""
        pet = Pet("Max", Species.DOG)
        task = Task("Fetch", 15, Priority.MEDIUM)
        pet.add_task(task)

        assert len(pet.get_all_tasks()) == 1

        pet.remove_task("Fetch")
        assert len(pet.get_all_tasks()) == 0

    def test_get_tasks_by_priority(self):
        """Verify filtering tasks by priority"""
        pet = Pet("Luna", Species.CAT)

        high_task = Task("Important", 20, Priority.HIGH)
        medium_task = Task("Normal", 15, Priority.MEDIUM)
        low_task = Task("Optional", 10, Priority.LOW)

        pet.add_task(high_task)
        pet.add_task(medium_task)
        pet.add_task(low_task)

        high_priority_tasks = pet.get_tasks_by_priority(Priority.HIGH)
        assert len(high_priority_tasks) == 1
        assert high_priority_tasks[0].task_name == "Important"

    def test_get_pending_tasks(self):
        """Verify getting only pending tasks"""
        pet = Pet("Charlie", Species.DOG)

        task1 = Task("Task 1", 10, Priority.HIGH)
        task2 = Task("Task 2", 15, Priority.MEDIUM)
        task3 = Task("Task 3", 20, Priority.LOW)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        # All should be pending initially
        assert len(pet.get_pending_tasks()) == 3

        # Mark one as completed
        task1.mark_completed()
        assert len(pet.get_pending_tasks()) == 2


class TestOwner:
    """Test Owner class functionality"""

    def test_owner_creation(self):
        """Verify owner can be created"""
        owner = Owner("Jordan", 8.5)
        assert owner.owner_name == "Jordan"
        assert owner.available_hours_per_day == 8.5
        assert len(owner.get_pets()) == 0

    def test_add_pet(self):
        """Verify adding a pet to owner"""
        owner = Owner("Sarah", 8.0)
        pet = Pet("Mochi", Species.DOG)

        owner.add_pet(pet)
        assert len(owner.get_pets()) == 1
        assert pet in owner.get_pets()

    def test_remove_pet(self):
        """Verify removing a pet from owner"""
        owner = Owner("Alex", 7.0)
        pet = Pet("Whiskers", Species.CAT)

        owner.add_pet(pet)
        assert len(owner.get_pets()) == 1

        owner.remove_pet("Whiskers")
        assert len(owner.get_pets()) == 0

    def test_get_all_tasks_from_all_pets(self):
        """Verify retrieving all tasks from all pets"""
        owner = Owner("Jordan", 8.0)

        # Create two pets with tasks
        dog = Pet("Mochi", Species.DOG)
        dog.add_task(Task("Walk", 20, Priority.HIGH))
        dog.add_task(Task("Eat", 10, Priority.MEDIUM))

        cat = Pet("Whiskers", Species.CAT)
        cat.add_task(Task("Play", 15, Priority.HIGH))

        owner.add_pet(dog)
        owner.add_pet(cat)

        all_tasks = owner.get_all_tasks_from_all_pets()
        assert len(all_tasks) == 3


class TestScheduler:
    """Test Scheduler class functionality"""

    def test_scheduler_creation(self):
        """Verify scheduler can be created"""
        scheduler = Scheduler()
        assert scheduler is not None
        assert hasattr(scheduler, 'PRIORITY_WEIGHTS')

    def test_generate_daily_plan_basic(self):
        """Verify scheduler generates a daily plan"""
        owner = Owner("Jordan", 8.0)
        pet = Pet("Mochi", Species.DOG)

        pet.add_task(Task("Walk", 20, Priority.HIGH))
        pet.add_task(Task("Eat", 10, Priority.MEDIUM))

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner, pet, 8.0)

        assert isinstance(plan, DailyPlan)
        assert len(plan.get_schedule()) > 0

    def test_scheduler_priority_sorting(self):
        """Verify scheduler sorts tasks by priority (HIGH first)"""
        owner = Owner("Sarah", 5.0)
        pet = Pet("Whiskers", Species.CAT)

        # Add tasks in wrong priority order
        pet.add_task(Task("Low priority task", 10, Priority.LOW))
        pet.add_task(Task("High priority task", 15, Priority.HIGH))
        pet.add_task(Task("Medium priority task", 10, Priority.MEDIUM))

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner, pet, 5.0)

        # First scheduled task should be HIGH priority
        first_task = plan.get_schedule()[0].get_task()
        assert first_task.priority == Priority.HIGH

    def test_scheduler_respects_time_constraints(self):
        """Verify scheduler respects available time constraint"""
        owner = Owner("Alex", 1.0)  # Only 1 hour available
        pet = Pet("Buddy", Species.DOG)

        # Add tasks totaling more than 1 hour
        pet.add_task(Task("Task 1", 30, Priority.LOW))
        pet.add_task(Task("Task 2", 30, Priority.LOW))
        pet.add_task(Task("Task 3", 30, Priority.HIGH))

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner, pet, 1.0)

        # Should fit within 60 minutes
        assert plan.total_time_used <= 60

    def test_plan_no_tasks(self):
        """Verify scheduler handles pet with no tasks"""
        owner = Owner("Jordan", 8.0)
        pet = Pet("Empty", Species.DOG)

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner, pet, 8.0)

        assert len(plan.get_schedule()) == 0
        assert "No pending tasks" in plan.description


class TestIntegration:
    """Integration tests for full workflow"""

    def test_full_workflow(self):
        """Test complete workflow: create owner, pets, tasks, and generate schedule"""
        # Create owner
        owner = Owner("Jordan", 8.0, "Prefers mornings")

        # Create pets
        dog = Pet("Mochi", Species.DOG)
        cat = Pet("Whiskers", Species.CAT)
        owner.add_pet(dog)
        owner.add_pet(cat)

        # Add tasks
        dog.add_task(Task("Morning walk", 20, Priority.HIGH))
        dog.add_task(Task("Breakfast", 10, Priority.MEDIUM))
        dog.add_task(Task("Play", 30, Priority.HIGH))

        cat.add_task(Task("Breakfast", 5, Priority.MEDIUM))
        cat.add_task(Task("Play", 20, Priority.HIGH))

        # Generate schedules
        scheduler = Scheduler()
        dog_plan = scheduler.generate_daily_plan(owner, dog, 8.0)
        cat_plan = scheduler.generate_daily_plan(owner, cat, 8.0)

        # Verify
        assert len(owner.get_pets()) == 2
        assert len(owner.get_all_tasks_from_all_pets()) == 5
        assert dog_plan.total_time_used > 0
        assert cat_plan.total_time_used > 0

    def test_task_lifecycle(self):
        """Test complete task lifecycle: create, schedule, complete"""
        pet = Pet("Mochi", Species.DOG)
        task = Task("Walk", 20, Priority.HIGH)

        # Add task
        pet.add_task(task)
        assert task in pet.get_pending_tasks()

        # Mark complete
        task.mark_completed()
        assert task not in pet.get_pending_tasks()
        assert task.status == TaskStatus.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
