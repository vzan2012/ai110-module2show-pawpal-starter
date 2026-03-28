import streamlit as st
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    Priority, Species, TaskStatus,
    DailyPlan, ScheduledTask
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Session state initialization


def initialize_session_state():
    """Initialize session state variables"""
    if "owner" not in st.session_state:
        st.session_state.owner = None
    if "pet" not in st.session_state:
        st.session_state.pet = None
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if "scheduler" not in st.session_state:
        st.session_state.scheduler = Scheduler()
    if "daily_plan" not in st.session_state:
        st.session_state.daily_plan = None
    if "available_hours" not in st.session_state:
        st.session_state.available_hours = 8.0


initialize_session_state()


def create_or_update_owner(name: str, available_hours: float):
    """Create or update Owner in session state"""
    if st.session_state.owner is None or st.session_state.owner.owner_name != name:
        st.session_state.owner = Owner(name, available_hours)
    else:
        st.session_state.owner.available_hours_per_day = available_hours


def create_or_update_pet(name: str, species_str: str):
    """Create or update Pet in session state"""
    species_map = {"dog": Species.DOG,
                   "cat": Species.CAT, "other": Species.OTHER}
    species = species_map.get(species_str.lower(), Species.OTHER)

    if st.session_state.pet is None or st.session_state.pet.pet_name != name:
        st.session_state.pet = Pet(name, species)
        st.session_state.tasks = []
    else:
        st.session_state.pet.species = species


st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("👤 Owner & Pet Info")
col1, col2 = st.columns(2)

with col1:
    owner_name = st.text_input(
        "Owner name", value="Jordan", key="owner_name_input")
    available_hours = st.slider(
        "Available hours per day", 1.0, 12.0, 8.0, 0.5, key="hours_slider")

with col2:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
    species = st.selectbox(
        "Species", ["dog", "cat", "other"], key="species_select")

create_or_update_owner(owner_name, available_hours)
create_or_update_pet(pet_name, species)

st.info(f"✅ Owner: **{st.session_state.owner.owner_name}** | Pet: **{st.session_state.pet.pet_name}** ({st.session_state.pet.species.value})")

st.markdown("### 📋 Tasks")
st.caption("Add tasks for your pet. These will be scheduled automatically.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input(
        "Task title", value="Morning walk", key="task_title_input")
with col2:
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20, key="duration_input")
with col3:
    priority = st.selectbox(
        "Priority", ["low", "medium", "high"], index=2, key="priority_select")

if st.button("➕ Add task"):
    priority_map = {"low": Priority.LOW,
                    "medium": Priority.MEDIUM, "high": Priority.HIGH}
    new_task = Task(task_title, duration, priority_map[priority])
    st.session_state.tasks.append(new_task)
    st.session_state.pet.add_task(new_task)
    st.success(f"Added: {task_title}")
    st.rerun()

if st.session_state.tasks:
    st.write(f"**Current tasks** ({len(st.session_state.tasks)} total):")
    task_data = []
    for task in st.session_state.tasks:
        task_data.append({
            "Task": task.task_name,
            "Duration": f"{task.duration_minutes} min",
            "Priority": task.priority.value.upper(),
            "Status": task.status.value
        })
    st.table(task_data)

    if st.button("🗑️ Clear all tasks"):
        st.session_state.tasks = []
        st.session_state.pet.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("🎯 Generate Daily Schedule")
st.caption(
    "Click below to create an optimized schedule based on priorities and time constraints.")

if st.button("✨ Generate Schedule", type="primary"):
    if not st.session_state.tasks:
        st.error("❌ Please add at least one task before generating a schedule.")
    else:
        st.session_state.daily_plan = st.session_state.scheduler.generate_daily_plan(
            st.session_state.owner,
            st.session_state.pet,
            st.session_state.available_hours
        )
        st.success("✅ Schedule generated successfully!")

if st.session_state.daily_plan is not None:
    plan = st.session_state.daily_plan
    st.markdown("---")
    st.subheader("📅 Today's Schedule")
    st.info(f"**{plan.description}**")

    if plan.get_schedule():
        st.markdown("#### Scheduled Tasks:")
        for i, scheduled_task in enumerate(plan.get_schedule(), 1):
            task = scheduled_task.get_task()
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{i}. {task.task_name}**")
                    st.caption(scheduled_task.get_reasoning())
                with col2:
                    st.metric("Time", scheduled_task.get_time_slot())
                with col3:
                    priority_colors = {Priority.HIGH: "🔴",
                                       Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}
                    st.metric("Priority", priority_colors.get(
                        task.priority, "?"))

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tasks", len(plan.get_schedule()))
        with col2:
            hours_used = plan.total_time_used / 60
            st.metric("Time Used", f"{hours_used:.1f}h")
        with col3:
            remaining = st.session_state.available_hours - \
                (plan.total_time_used / 60)
            st.metric("Remaining", f"{remaining:.1f}h")
    else:
        st.warning("⚠️ No tasks fit in the available time.")
