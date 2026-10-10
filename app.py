"""Streamlit interface for PawPal+. Run with: streamlit run app.py."""
from datetime import date
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, load_from_json, save_to_json

DATA_FILE = Path(__file__).with_name("pawpal_data.json")
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.caption("A smart, priority-aware daily care planner for every pet in your home.")
with st.sidebar:
    st.header("Household")
    owner.name = st.text_input("Owner name", value=owner.name)
    owner.preferences = st.text_area("Preferences", value=owner.preferences, placeholder="e.g., Walks before 8 AM")
    if st.button("Save household", use_container_width=True):
        save_to_json(owner, DATA_FILE)
        st.success("Saved locally.")
    if st.button("Load saved household", use_container_width=True):
        if DATA_FILE.exists():
            st.session_state.owner = load_from_json(DATA_FILE)
            st.rerun()
        else:
            st.warning("No saved household found.")

add_pet, add_task, daily_plan = st.tabs(["Add a pet", "Schedule a task", "Today's plan"])
with add_pet:
    st.subheader("Add a pet")
    with st.form("pet_form", clear_on_submit=True):
        name = st.text_input("Pet name")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        age = st.number_input("Age (optional)", min_value=0, max_value=50, value=0)
        submitted = st.form_submit_button("Add pet")
    if submitted:
        try:
            owner.add_pet(Pet(name, species, age or None))
            st.success(f"{name.strip()} is now part of {owner.name}'s household.")
        except ValueError as exc:
            st.error(str(exc))
    if owner.pets:
        st.write("Current pets: " + ", ".join(f"**{pet.name}** ({pet.species})" for pet in owner.pets))

with add_task:
    st.subheader("Schedule a care task")
    if not owner.pets:
        st.info("Add a pet first, then return here to schedule care.")
    else:
        with st.form("task_form", clear_on_submit=True):
            pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])
            description = st.text_input("What needs to happen?", placeholder="Morning walk")
            columns = st.columns(3)
            with columns[0]: scheduled = st.time_input("Start time")
            with columns[1]: duration = st.number_input("Minutes", min_value=1, max_value=240, value=15)
            with columns[2]: priority = st.selectbox("Priority", ["high", "medium", "low"])
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
            due = st.date_input("Due date", value=date.today())
            submitted = st.form_submit_button("Schedule task")
        if submitted:
            try:
                owner.get_pet(pet_name).add_task(Task(description, scheduled.strftime("%H:%M"), int(duration), priority, frequency, due))
                st.success("Task scheduled.")
            except ValueError as exc:
                st.error(str(exc))

with daily_plan:
    selected_date = st.date_input("Plan date", value=date.today(), key="plan_date")
    st.subheader(f"Plan for {selected_date:%A, %B %d}")
    open_tasks = scheduler.prioritized_schedule(selected_date)
    if not open_tasks:
        st.info("No open tasks planned for this day.")
    else:
        st.caption("Tasks are ranked by priority, then start time. This keeps urgent care visible first.")
        for pet, task in open_tasks:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority]
            left, complete = st.columns([5, 1])
            with left:
                st.markdown(
                    f"{icon} **{task.scheduled_time} — {task.description}**  \n"
                    f"{pet.name} · {task.duration_minutes} min · {task.priority.title()} · {task.frequency}"
                )
            with complete:
                if st.button("Complete", key=f"{pet.name}-{id(task)}"):
                    next_task = scheduler.complete_task(pet.name, task)
                    st.success("Completed." + (f" Next due {next_task.due_date}." if next_task else ""))
                    st.rerun()
        conflicts = scheduler.detect_conflicts(selected_date)
        if conflicts:
            st.warning("Scheduling conflicts")
            for conflict in conflicts: st.write(f"⚠️ {conflict}")
        st.caption(f"Next available 15-minute start slot: {scheduler.next_available_slot(selected_date)}")
