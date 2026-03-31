import streamlit as st
from pawpal_system import CareTask, Pet, PetOwner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — initialize once, persist across reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(strategy="priority")

# ---------------------------------------------------------------------------
# Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    time_budget = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=90)

if st.button("Save Owner"):
    st.session_state.owner = PetOwner(
        name=owner_name,
        email="",
        time_available_minutes=int(time_budget),
    )
    st.success(f"Owner '{owner_name}' saved with {time_budget} min available.")

if st.session_state.owner is None:
    st.info("Save an owner above to continue.")
    st.stop()

owner: PetOwner = st.session_state.owner

# ---------------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Buddy")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    breed = st.text_input("Breed", value="Labrador")

col4, col5 = st.columns(2)
with col4:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
with col5:
    weight = st.number_input("Weight (lbs)", min_value=0.5, max_value=300.0, value=65.0)

if st.button("Add Pet"):
    existing_names = [p.name for p in owner.pets]
    if pet_name in existing_names:
        st.warning(f"'{pet_name}' is already added.")
    else:
        pet = Pet(name=pet_name, species=species, breed=breed, age_years=int(age), weight_lbs=weight)
        owner.add_pet(pet)   # also loads default tasks
        st.success(f"Added {pet_name} with {len(pet.tasks)} default task(s).")

if owner.pets:
    st.write("**Pets:**", ", ".join(p.name for p in owner.pets))

# ---------------------------------------------------------------------------
# Add a task
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_pet = st.selectbox("For pet", [p.name for p in owner.pets])
    with col2:
        task_title = st.text_input("Task name", value="Evening walk")
    with col3:
        task_type = st.selectbox("Type", ["walk", "feed", "meds", "groom", "enrichment"])
    with col4:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)

    priority = st.slider("Priority (1 = highest, 5 = lowest)", min_value=1, max_value=5, value=2)

    if st.button("Add Task"):
        pet = owner.get_pet(task_pet)
        task = CareTask(
            name=task_title,
            task_type=task_type,
            duration_minutes=int(duration),
            priority=priority,
        )
        pet.add_task(task)   # sets pet_name automatically
        st.success(f"Added '{task_title}' to {task_pet}.")

    # Show current tasks across all pets
    all_tasks = owner.get_tasks()
    if all_tasks:
        st.write("**Current tasks:**")
        st.table([t.to_dict() for t in all_tasks])
    else:
        st.info("No tasks yet.")

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Build Schedule")

strategy = st.selectbox("Scheduling strategy", ["priority", "shortest_first", "balanced"])
st.session_state.scheduler.strategy = strategy

if st.button("Generate Schedule"):
    scheduler: Scheduler = st.session_state.scheduler
    plan = scheduler.generate_plan(owner)

    if not plan.tasks:
        st.warning("No tasks could fit within the available time.")
    else:
        st.success(f"Scheduled {len(plan.tasks)} task(s) — {plan.total_time_used()} min used of {owner.time_available_minutes} min.")
        st.markdown("### Today's Plan")
        for task in plan.tasks:
            pet_label = f" — {task.pet_name}" if task.pet_name else ""
            st.markdown(f"- **{task.name}**{pet_label} | {task.duration_minutes} min | priority {task.priority}")
        st.info(plan.reasoning)
