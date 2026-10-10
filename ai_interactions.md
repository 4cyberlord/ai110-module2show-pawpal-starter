# AI Interaction Record

## Design and implementation workflow

| Stage | Prompt or task | Files changed | Outcome and review |
|---|---|---|---|
| Architecture | Design a small OOP pet-care system with Owner, Pet, Task, and Scheduler. | `diagrams/uml.mmd`, `pawpal_system.py` | Produced a focused composition model: Owner → Pet → Task, with Scheduler referencing Owner. |
| Algorithms | Add readable sorting, filtering, recurrence, conflict detection, and an available-slot helper. | `pawpal_system.py`, `main.py` | Chose exact-time conflict warnings for readability; duration-aware logic is used for next-slot calculation. |
| Interface | Connect Streamlit forms to the model while preserving state. | `app.py` | Stored the Owner object in `st.session_state`; added optional JSON save/load. |
| Verification | Draft tests for model behavior and scheduling edge cases. | `tests/test_pawpal.py` | Tests were executed with `python -m pytest`; code was adjusted until the suite passed. |

## Prompt comparison

| Model/tool approach | Task | Useful output | Limitation | Final decision |
|---|---|---|---|---|
| AI-generated recurrence approach | Reschedule daily and weekly tasks after completion. | Suggested `timedelta`, which keeps date arithmetic correct across month boundaries. | A direct mutation approach could lose completion history. | Preserve the completed original and append a new `Task` instance for the next date. |
| Manual review | Decide conflict behavior. | Confirmed exact-time grouping is clear for an introductory project. | Does not identify every overlap. | Keep exact-time warnings and document the limitation; provide a duration-aware next-slot helper as an extension. |
