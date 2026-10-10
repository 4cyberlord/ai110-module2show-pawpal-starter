"""Command-line demonstration of PawPal+ scheduling features."""
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan", "Prefers walks before work")
    mochi, luna = Pet("Mochi", "dog", 3), Pet("Luna", "cat", 5)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    today = date.today()
    mochi.add_task(Task("Morning walk", "08:00", 30, "high", "daily", today))
    mochi.add_task(Task("Breakfast", "07:30", 10, "high", "daily", today))
    luna.add_task(Task("Give medication", "08:00", 5, "high", "daily", today))
    luna.add_task(Task("Play session", "18:00", 20, "medium", "once", today))
    scheduler = Scheduler(owner)

    print(f"PawPal+ daily plan for {owner.name} — {today:%B %d, %Y}")
    print("=" * 60)
    for pet, task in scheduler.sort_by_time():
        marker = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority]
        print(f"{task.scheduled_time} | {pet.name:<6} | {task.description:<18} | {task.duration_minutes:>3} min | {marker} {task.priority}")
    print("\nPriority-first view:")
    print(", ".join(f"{pet.name}: {task.description}" for pet, task in scheduler.prioritized_schedule()))
    print("\nConflict warnings:")
    for warning in scheduler.detect_conflicts():
        print(f"⚠️  {warning}")
    recurring = scheduler.complete_task("Mochi", mochi.tasks[0])
    print(f"\nCompleted Morning walk; next occurrence: {recurring.due_date if recurring else 'none'}")
    print(f"Next available 15-minute slot: {scheduler.next_available_slot()}")


if __name__ == "__main__":
    main()
