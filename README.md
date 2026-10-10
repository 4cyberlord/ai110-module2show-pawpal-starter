# PawPal+

PawPal+ is a Streamlit pet-care planner that keeps a household's feedings, walks, medication, and appointments organized. It uses a modular Python OOP backend and a stateful browser interface.

## Features

- Add an owner, pets, and dated care tasks in the UI.
- Keep data alive during the Streamlit session and optionally save/load it locally as JSON.
- Sort a daily schedule chronologically or prioritize urgent care first.
- Filter tasks by pet or completion status.
- Flag exact duplicate start times as lightweight conflict warnings.
- Complete daily or weekly tasks and automatically create their next occurrence.
- Find the next available 15-minute slot from task durations.

## Setup and run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## CLI demo

```bash
python main.py
```

Sample output:

```text
PawPal+ daily plan for Jordan
============================================================
07:30 | Mochi  | Breakfast          |  10 min | 🔴 high
08:00 | Mochi  | Morning walk       |  30 min | 🔴 high
08:00 | Luna   | Give medication    |   5 min | 🔴 high
18:00 | Luna   | Play session       |  20 min | 🟡 medium

Conflict warnings:
⚠️  Conflict at 08:00: Mochi — Morning walk, Luna — Give medication
```

## Smarter scheduling

| Feature | Method | Behavior |
|---|---|---|
| Time sorting | `Scheduler.sort_by_time()` | Orders tasks chronologically using parsed `HH:MM` times. |
| Filtering | `Scheduler.filter_tasks()` | Narrows a day's tasks by pet name and/or completion status. |
| Priority plan | `Scheduler.prioritized_schedule()` | Ranks high, medium, then low priority; ties use time. |
| Conflicts | `Scheduler.detect_conflicts()` | Returns warnings when two open tasks start at the exact same time. |
| Recurrence | `Scheduler.complete_task()` | Completes the original and adds the next daily or weekly occurrence. |
| Available slot | `Scheduler.next_available_slot()` | Finds a free 15-minute start time, accounting for duration. |

The conflict rule intentionally checks exact starts rather than all interval overlaps. It is fast and easy to explain in a lightweight care planner; the available-slot helper does account for occupied durations.

## Data persistence

The sidebar's **Save household** button writes `pawpal_data.json`; **Load saved household** restores it. The backend uses `save_to_json()` and `load_from_json()` with explicit dataclass-to-dictionary conversion, so dates remain valid ISO date values.

## Testing PawPal+

```bash
python -m pytest
```

The suite covers completion, adding tasks, chronological sorting, filtering, daily recurrence, duplicate-time conflicts, and JSON persistence.

Successful run:

```text
7 passed in 0.02s
```

## Demo walkthrough

1. Open the **Add a pet** tab and create each pet in the household.
2. Use **Schedule a task** to select a pet, add a time, duration, priority, frequency, and date.
3. Open **Today's plan** to see open tasks ordered by priority, then time.
4. Review any duplicate-time warning and the next available slot.
5. Select **Complete** to mark the task done; recurring tasks automatically receive their next due date.
6. Use the sidebar to save the household locally or restore it in a later session.

## Design

The final class diagram is in [diagrams/uml.mmd](diagrams/uml.mmd). `Owner` owns `Pet` objects, each `Pet` owns `Task` objects, and `Scheduler` organizes an owner's tasks without duplicating data.
