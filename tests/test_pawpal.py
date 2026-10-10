from datetime import date, timedelta
from pawpal_system import Owner, Pet, Scheduler, Task, load_from_json, save_to_json

def household():
    owner = Owner("Ari")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    return owner, pet, Scheduler(owner)

def test_mark_complete_changes_status():
    task = Task("Feed", "08:00"); task.mark_complete()
    assert task.completed is True

def test_adding_task_increases_pet_task_count():
    _, pet, _ = household(); pet.add_task(Task("Walk", "08:00"))
    assert len(pet.tasks) == 1

def test_sort_by_time_is_chronological():
    _, pet, scheduler = household()
    pet.add_task(Task("Dinner", "18:00")); pet.add_task(Task("Breakfast", "07:00"))
    assert [task.description for _, task in scheduler.sort_by_time()] == ["Breakfast", "Dinner"]

def test_daily_completion_creates_tomorrows_task():
    _, pet, scheduler = household(); task = Task("Medication", "09:00", frequency="daily"); pet.add_task(task)
    next_task = scheduler.complete_task("Biscuit", task)
    assert task.completed and next_task and next_task.due_date == date.today() + timedelta(days=1)

def test_conflict_detection_flags_duplicate_start_times():
    owner, pet, scheduler = household(); pet.add_task(Task("Walk", "08:00"))
    second = Pet("Mittens", "cat", tasks=[Task("Medication", "08:00")]); owner.add_pet(second)
    assert scheduler.detect_conflicts() == ["Conflict at 08:00: Biscuit — Walk, Mittens — Medication"]

def test_filter_by_pet_and_status():
    owner, pet, scheduler = household(); walk = Task("Walk", "08:00"); walk.mark_complete(); pet.add_task(walk)
    owner.add_pet(Pet("Mittens", "cat", tasks=[Task("Feed", "09:00")]))
    assert [task.description for _, task in scheduler.filter_tasks(pet_name="Biscuit", completed=True)] == ["Walk"]

def test_json_round_trip(tmp_path):
    owner, pet, _ = household(); pet.add_task(Task("Feed", "07:00", priority="high")); file_path = tmp_path / "pawpal.json"
    save_to_json(owner, file_path)
    assert load_from_json(file_path).pets[0].tasks[0].description == "Feed"
