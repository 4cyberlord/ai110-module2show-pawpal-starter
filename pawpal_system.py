"""Core domain models and scheduling logic for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
from typing import Literal

Frequency = Literal["once", "daily", "weekly"]
Priority = Literal["low", "medium", "high"]
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def _parse_time(value: str) -> time:
    """Validate and convert an HH:MM value to a time object."""
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise ValueError("time must use 24-hour HH:MM format") from exc


@dataclass
class Task:
    """A scheduled activity for one pet."""

    description: str
    scheduled_time: str
    duration_minutes: int = 15
    priority: Priority = "medium"
    frequency: Frequency = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate task fields when the task is created."""
        self.description = self.description.strip()
        if not self.description:
            raise ValueError("description cannot be empty")
        _parse_time(self.scheduled_time)
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_RANK:
            raise ValueError("priority must be low, medium, or high")
        if self.frequency not in ("once", "daily", "weekly"):
            raise ValueError("frequency must be once, daily, or weekly")

    @property
    def start_time(self) -> time:
        """Return the parsed scheduled start time."""
        return _parse_time(self.scheduled_time)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Create the next task for a recurring task, if applicable."""
        offsets = {"daily": 1, "weekly": 7}
        days = offsets.get(self.frequency)
        if days is None:
            return None
        return Task(
            description=self.description,
            scheduled_time=self.scheduled_time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=self.due_date + timedelta(days=days),
        )

    def to_dict(self) -> dict:
        """Serialize this task to JSON-compatible data."""
        return {**self.__dict__, "due_date": self.due_date.isoformat()}

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Restore a task from JSON-compatible data."""
        return cls(**{**data, "due_date": date.fromisoformat(data["due_date"])})


@dataclass
class Pet:
    """A pet whose care tasks are managed by PawPal+."""

    name: str
    species: str
    age: int | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's care list."""
        self.tasks.append(task)

    def tasks_for_date(self, target_date: date) -> list[Task]:
        """Return tasks due on the supplied date."""
        return [task for task in self.tasks if task.due_date == target_date]

    def to_dict(self) -> dict:
        """Serialize this pet to JSON-compatible data."""
        return {"name": self.name, "species": self.species, "age": self.age,
                "tasks": [task.to_dict() for task in self.tasks]}

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Restore a pet from JSON-compatible data."""
        return cls(data["name"], data["species"], data.get("age"),
                   [Task.from_dict(task) for task in data.get("tasks", [])])


@dataclass
class Owner:
    """An owner with one or more pets."""

    name: str
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"A pet named {pet.name} already exists")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name, ignoring letter case."""
        return next((pet for pet in self.pets if pet.name.lower() == name.lower()), None)

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task paired with the pet it belongs to."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def to_dict(self) -> dict:
        """Serialize this owner to JSON-compatible data."""
        return {"name": self.name, "preferences": self.preferences,
                "pets": [pet.to_dict() for pet in self.pets]}

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Restore an owner from JSON-compatible data."""
        return cls(data["name"], data.get("preferences", ""),
                   [Pet.from_dict(pet) for pet in data.get("pets", [])])


class Scheduler:
    """Organizes an owner's pet-care tasks into a clear daily plan."""

    def __init__(self, owner: Owner) -> None:
        """Connect the scheduler to an owner and their pets."""
        self.owner = owner

    def tasks_for_date(self, target_date: date | None = None) -> list[tuple[Pet, Task]]:
        """Return all tasks due on the target date, defaulting to today."""
        target_date = target_date or date.today()
        return [(pet, task) for pet, task in self.owner.all_tasks() if task.due_date == target_date]

    def sort_by_time(self, tasks: list[tuple[Pet, Task]] | None = None) -> list[tuple[Pet, Task]]:
        """Sort task pairs chronologically by their scheduled time."""
        return sorted(tasks if tasks is not None else self.tasks_for_date(), key=lambda item: item[1].start_time)

    def filter_tasks(self, *, pet_name: str | None = None, completed: bool | None = None,
                     target_date: date | None = None) -> list[tuple[Pet, Task]]:
        """Filter tasks by pet and/or completion status."""
        tasks = self.tasks_for_date(target_date)
        return [(pet, task) for pet, task in tasks
                if (pet_name is None or pet.name.lower() == pet_name.lower())
                and (completed is None or task.completed == completed)]

    def prioritized_schedule(self, target_date: date | None = None) -> list[tuple[Pet, Task]]:
        """Order open tasks by priority first and scheduled time second."""
        return sorted(self.filter_tasks(completed=False, target_date=target_date),
                      key=lambda item: (PRIORITY_RANK[item[1].priority], item[1].start_time))

    def detect_conflicts(self, target_date: date | None = None) -> list[str]:
        """Return warnings for tasks that start at the same exact time."""
        groups: dict[str, list[tuple[Pet, Task]]] = {}
        for pet, task in self.filter_tasks(completed=False, target_date=target_date):
            groups.setdefault(task.scheduled_time, []).append((pet, task))
        return [f"Conflict at {when}: " + ", ".join(f"{pet.name} — {task.description}" for pet, task in items)
                for when, items in groups.items() if len(items) > 1]

    def complete_task(self, pet_name: str, task: Task) -> Task | None:
        """Complete a task and add its next recurrence when needed."""
        pet = self.owner.get_pet(pet_name)
        if pet is None or task not in pet.tasks:
            raise ValueError("Task does not belong to the named pet")
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            pet.add_task(next_task)
        return next_task

    def next_available_slot(self, target_date: date | None = None, start_at: str = "08:00",
                            interval_minutes: int = 15) -> str:
        """Find the first unoccupied start time using task durations."""
        target_date = target_date or date.today()
        cursor = datetime.combine(target_date, _parse_time(start_at))
        occupied = [(datetime.combine(target_date, task.start_time), task.duration_minutes)
                    for _, task in self.filter_tasks(completed=False, target_date=target_date)]
        while any(start <= cursor < start + timedelta(minutes=duration) for start, duration in occupied):
            cursor += timedelta(minutes=interval_minutes)
        return cursor.strftime("%H:%M")


def save_to_json(owner: Owner, file_path: str | Path) -> None:
    """Save an owner's PawPal+ data to a JSON file."""
    Path(file_path).write_text(json.dumps(owner.to_dict(), indent=2), encoding="utf-8")


def load_from_json(file_path: str | Path) -> Owner:
    """Load an owner's PawPal+ data from a JSON file."""
    return Owner.from_dict(json.loads(Path(file_path).read_text(encoding="utf-8")))
