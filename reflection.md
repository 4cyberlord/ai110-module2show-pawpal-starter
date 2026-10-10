# PawPal+ Project Reflection

## 1. System Design

### a. Initial design

The system uses four core classes. `Owner` manages a household and preferences; `Pet` stores identity details and its task list; `Task` represents one dated care activity; and `Scheduler` is the coordination layer that queries tasks across all pets. The three essential actions are adding a pet, scheduling a care task, and viewing a prioritized daily plan.

### b. Design changes

The final `Task` gained `due_date`, `duration_minutes`, `priority`, and `frequency`. These fields make a task usable for daily planning instead of just being a label and time. Persistence was kept outside the model as `save_to_json`/`load_from_json`, preserving a clean separation between domain behavior and file I/O.

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and priorities

The scheduler considers date, completion state, pet, time, priority, recurrence, and duration. The primary plan ranks priority before time so medication and other urgent care cannot be hidden below routine tasks; a chronological view is also available for an actual timeline.

### b. Tradeoffs

Conflict detection treats only identical start times as conflicts. This rule is simple, transparent, and inexpensive, but it does not warn about partially overlapping intervals. The next-slot algorithm does use duration, which supplies a practical stepping stone toward richer overlap handling.

## 3. AI Collaboration

### a. How AI was used

AI support was used to turn the scenario into a class model, propose Mermaid notation, scaffold dataclasses, and outline test cases. Prompts around recurrence and sorting helped focus on Python's `timedelta` and sorted key functions.

### b. Judgment and verification

An overly clever scheduling approach that mixed persistence, UI state, and business rules was avoided. Persistence is intentionally isolated and every algorithm was verified by a test or the CLI demo rather than trusting generated code without execution.

## 4. Testing and Verification

### a. What was tested

Tests cover status changes, task addition, chronological sorting, filtering, recurring task creation, conflict warnings, and JSON round-tripping. These validate both basic model integrity and the scheduling behaviors a user relies on.

### b. Confidence

Confidence level: ★★★★☆ (4/5). Core paths pass automatically. Future tests should cover invalid input in the UI, interval-overlap warnings, multiple recurrence completions, and a larger household with many tasks.

## 5. Reflection

### a. What went well

The logic stays compact because dataclasses map naturally to the real-world objects, while `Scheduler` keeps cross-pet algorithms in one discoverable place.

### b. What could improve

A future version should support editing/deleting tasks, calendar integrations, and full overlap detection with user-configurable buffers.

### c. Key takeaway

Good AI collaboration begins with a clear model and ends with human review plus executable verification; generated code is a starting point, not proof of correctness.
