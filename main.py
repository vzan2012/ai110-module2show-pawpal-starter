"""
PawPal+ Demo Script
Demonstrates the scheduling system with a realistic scenario.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Species


def print_schedule(owner: Owner, pet: Pet, plan):
    """Print a formatted daily schedule"""
    print("\n" + "="*70)
    print(f"🐾 {pet.pet_name.upper()}'s Daily Schedule ({pet.species.value.title()})")
    print("="*70)

    if not plan.get_schedule():
        print("📋 No tasks scheduled for today.")
        return

    print(f"\nPlan Summary: {plan.description}\n")
    print(f"{'Time':<15} {'Task':<25} {'Priority':<10} {'Duration':<10}")
    print("-"*70)

    for i, scheduled_task in enumerate(plan.get_schedule(), 1):
        task = scheduled_task.get_task()
        time_slot = scheduled_task.get_time_slot()
        task_name = task.task_name
        priority = task.get_priority().value.upper()
        duration = f"{task.get_duration()} min"

        print(f"{time_slot:<15} {task_name:<25} {priority:<10} {duration:<10}")
        print(f"  └─ Reason: {scheduled_task.get_reasoning()}")

    print("-"*70)
    print(
        f"Total Time: {plan.total_time_used/60:.1f} hours | Available: {owner.available_hours_per_day} hours")
    print("="*70 + "\n")


def main():
    print("\n🐾 Welcome to PawPal+ Demo 🐾\n")

    # Step 1: Create Owner
    owner = Owner(
        owner_name="Jordan",
        available_hours_per_day=8.0,
        preferences="Prefers morning activities for high-energy tasks"
    )
    print(f"✅ Owner created: {owner.owner_name}")
    print(f"   Available hours per day: {owner.available_hours_per_day}h")
    print(f"   Preferences: {owner.preferences}\n")

    # Step 2: Create Pets
    dog = Pet(pet_name="Mochi", species=Species.DOG)
    cat = Pet(pet_name="Whiskers", species=Species.CAT)

    owner.add_pet(dog)
    owner.add_pet(cat)
    print(f"✅ Pets created and added to owner:")
    print(f"   - {dog.pet_name} ({dog.species.value})")
    print(f"   - {cat.pet_name} ({cat.species.value})\n")

    # Step 3: Add Tasks to Dog (Mochi)
    print(f"Adding tasks for {dog.pet_name}...")
    dog_tasks = [
        Task("Morning walk", 20, Priority.HIGH),
        Task("Breakfast", 10, Priority.MEDIUM),
        Task("Playtime", 30, Priority.HIGH),
        Task("Afternoon walk", 20, Priority.MEDIUM),
        Task("Dinner", 10, Priority.LOW),
        Task("Evening cuddle", 15, Priority.LOW),
    ]
    for task in dog_tasks:
        dog.add_task(task)
        print(
            f"   ✓ Added: {task.task_name} ({task.priority.value}, {task.duration_minutes}min)")

    print()

    # Step 4: Add Tasks to Cat (Whiskers)
    print(f"Adding tasks for {cat.pet_name}...")
    cat_tasks = [
        Task("Breakfast", 5, Priority.MEDIUM),
        Task("Interactive play", 20, Priority.HIGH),
        Task("Grooming", 15, Priority.MEDIUM),
        Task("Dinner", 5, Priority.MEDIUM),
        Task("Lap time", 30, Priority.LOW),
    ]
    for task in cat_tasks:
        cat.add_task(task)
        print(
            f"   ✓ Added: {task.task_name} ({task.priority.value}, {task.duration_minutes}min)")

    print("\n" + "="*70)
    print("Generating Schedules...")
    print("="*70)

    # Step 5: Create Scheduler and Generate Plans
    scheduler = Scheduler()

    # Generate schedule for dog
    dog_plan = scheduler.generate_daily_plan(
        owner, dog, owner.available_hours_per_day)
    print_schedule(owner, dog, dog_plan)

    # Generate schedule for cat
    cat_plan = scheduler.generate_daily_plan(
        owner, cat, owner.available_hours_per_day)
    print_schedule(owner, cat, cat_plan)

    # Summary Statistics
    print("\n📊 SUMMARY STATISTICS")
    print("="*70)
    print(f"Owner: {owner.owner_name}")
    print(f"Total Pets: {len(owner.get_pets())}")
    print(
        f"Total Tasks Across All Pets: {len(owner.get_all_tasks_from_all_pets())}")
    print(
        f"Total Pending Tasks: {len(owner.get_pending_tasks_from_all_pets())}")
    print()

    for pet in owner.get_pets():
        print(f"{pet.pet_name}:")
        print(f"  - Total tasks: {len(pet.get_all_tasks())}")
        print(f"  - Pending tasks: {len(pet.get_pending_tasks())}")
        print(
            f"  - High priority tasks: {len(pet.get_tasks_by_priority(Priority.HIGH))}")
        print(
            f"  - Medium priority tasks: {len(pet.get_tasks_by_priority(Priority.MEDIUM))}")
        print(
            f"  - Low priority tasks: {len(pet.get_tasks_by_priority(Priority.LOW))}")

    print("="*70)
    print("✅ Demo completed successfully!\n")


if __name__ == "__main__":
    main()
