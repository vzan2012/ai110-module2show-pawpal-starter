"""
PawPal+ System - Pet Care Management and Scheduling
Core classes for managing owners, pets, tasks, and daily schedules.
"""

from dataclasses import dataclass, field
from typing import List
from enum import Enum
from datetime import datetime


class Priority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Species(Enum):
    """Supported pet species"""
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


class TaskStatus(Enum):
    """Task status tracking"""
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """Represents a pet care task"""
    task_name: str
    duration_minutes: int
    priority: Priority
    status: TaskStatus = TaskStatus.PENDING

    def get_priority(self) -> Priority:
        """Get the priority level of this task"""
        return self.priority

    def get_duration(self) -> int:
        """Get the duration in minutes"""
        return self.duration_minutes
    
    def mark_completed(self) -> None:
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
    
    def mark_skipped(self) -> None:
        """Mark task as skipped"""
        self.status = TaskStatus.SKIPPED
    
    def reset(self) -> None:
        """Reset task to pending status"""
        self.status = TaskStatus.PENDING


@dataclass
class Pet:
    """Represents a pet owned by an owner"""
    pet_name: str
    species: Species
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet"""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name"""
        self.tasks = [t for t in self.tasks if t.task_name != task_name]

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Get all tasks with a specific priority level"""
        return [t for t in self.tasks if t.priority == priority]

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks for this pet"""
        return self.tasks
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks for this pet"""
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]


@dataclass
class Owner:
    """Represents a pet owner"""
    owner_name: str
    available_hours_per_day: float
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection"""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name"""
        self.pets = [p for p in self.pets if p.pet_name != pet_name]

    def get_pets(self) -> List[Pet]:
        """Get all pets owned by this owner"""
        return self.pets
    
    def get_all_tasks_from_all_pets(self) -> List[Task]:
        """
        Retrieve all tasks from all pets.
        Used by Scheduler to access all tasks across all pets.
        """
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_all_tasks())
        return all_tasks
    
    def get_pending_tasks_from_all_pets(self) -> List[Task]:
        """Get all pending tasks from all pets"""
        all_pending = []
        for pet in self.pets:
            all_pending.extend(pet.get_pending_tasks())
        return all_pending


@dataclass
class ScheduledTask:
    """Represents a task scheduled at a specific time"""
    task: Task
    time_slot: str
    reasoning: str

    def get_task(self) -> Task:
        """Get the task object"""
        return self.task

    def get_time_slot(self) -> str:
        """Get the scheduled time slot"""
        return self.time_slot

    def get_reasoning(self) -> str:
        """Get the reasoning for this scheduling decision"""
        return self.reasoning


@dataclass
class DailyPlan:
    """Represents a daily schedule plan"""
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    total_time_used: float = 0.0
    description: str = ""

    def get_schedule(self) -> List[ScheduledTask]:
        """Get the list of scheduled tasks"""
        return self.scheduled_tasks
    
    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task to the plan"""
        self.scheduled_tasks.append(scheduled_task)
        # Update total time used
        self.total_time_used += scheduled_task.get_task().get_duration()
    
    def calculate_total_time(self) -> float:
        """Calculate total time for all scheduled tasks"""
        total = sum(st.get_task().get_duration() for st in self.scheduled_tasks)
        self.total_time_used = total
        return total


class Scheduler:
    """Orchestrates the scheduling logic to generate daily plans"""

    # Priority weighting for sorting (higher = more important)
    PRIORITY_WEIGHTS = {
        Priority.HIGH: 3,
        Priority.MEDIUM: 2,
        Priority.LOW: 1
    }

    def generate_daily_plan(
        self, owner: Owner, pet: Pet, available_time: float
    ) -> DailyPlan:
        """Generate an optimized daily plan based on constraints"""
        # Get all pending tasks for this pet
        pending_tasks = pet.get_pending_tasks()
        
        if not pending_tasks:
            plan = DailyPlan(description="No pending tasks for today.")
            return plan
        
        # Sort tasks by priority
        sorted_tasks = self._sort_tasks_by_priority(pending_tasks)
        
        # Check if all tasks fit in available time
        total_duration = sum(t.get_duration() for t in sorted_tasks)
        
        if not self._check_time_constraints(sorted_tasks, available_time):
            # Tasks don't all fit, prioritize high-priority tasks
            sorted_tasks = self._fit_tasks_to_time(sorted_tasks, available_time)
        
        # Create schedule with time slots
        plan = DailyPlan()
        current_time = 800  # Start at 8:00 AM (military/24-hour format)
        
        for task in sorted_tasks:
            start_hour = current_time // 100
            start_minute = current_time % 100
            
            end_time = current_time + task.get_duration()
            end_hour = end_time // 100
            end_minute = end_time % 100
            
            time_slot = f"{start_hour:02d}:{start_minute:02d} - {end_hour:02d}:{end_minute:02d}"
            
            reasoning = self._generate_reasoning(task)
            scheduled_task = ScheduledTask(task, time_slot, reasoning)
            plan.add_scheduled_task(scheduled_task)
            
            current_time = end_time
        
        # Generate overall plan description
        plan.description = self._generate_plan_description(pet, plan, available_time)
        
        return plan

    def _sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (HIGH → MEDIUM → LOW), then by duration"""
        return sorted(
            tasks,
            key=lambda t: (-self.PRIORITY_WEIGHTS[t.get_priority()], -t.get_duration())
        )

    def _check_time_constraints(
        self, tasks: List[Task], available_time: float
    ) -> bool:
        """Verify that tasks fit within available time (in minutes)"""
        total_time = sum(t.get_duration() for t in tasks)
        return total_time <= available_time * 60  # Convert hours to minutes

    def _fit_tasks_to_time(self, tasks: List[Task], available_time: float) -> List[Task]:
        """Select high-priority tasks that fit within available time"""
        available_minutes = available_time * 60
        selected_tasks = []
        used_time = 0
        
        for task in tasks:
            if used_time + task.get_duration() <= available_minutes:
                selected_tasks.append(task)
                used_time += task.get_duration()
        
        return selected_tasks
    
    def _generate_reasoning(self, task: Task) -> str:
        """Generate explanation for why a task was scheduled"""
        priority_text = task.get_priority().value.upper()
        return f"Scheduled based on {priority_text} priority ({task.get_duration()} min)"
    
    def _generate_plan_description(
        self, pet: Pet, plan: DailyPlan, available_time: float
    ) -> str:
        """Generate a summary description of the daily plan"""
        num_tasks = len(plan.get_schedule())
        time_used = plan.total_time_used / 60  # Convert to hours
        remaining = available_time - time_used
        
        return (
            f"Daily plan for {pet.pet_name} ({pet.species.value}): "
            f"{num_tasks} tasks scheduled. "
            f"Time allocated: {time_used:.1f}h of {available_time:.1f}h available. "
            f"Remaining: {remaining:.1f}h."
        )
