from pawpal_system import CareTask, Pet, PetOwner, Scheduler

# --- Setup owner ---
owner = PetOwner(
    name="Jordan",
    email="jordan@email.com",
    time_available_minutes=90,
)

# --- Create pets ---
buddy = Pet(name="Buddy", species="dog", breed="Labrador", age_years=3, weight_lbs=65.0)
luna  = Pet(name="Luna",  species="cat", breed="Siamese",  age_years=5, weight_lbs=9.5)

# --- Add custom tasks ---
buddy.add_task(CareTask("Flea Medicine", "meds",        5,  1))
buddy.add_task(CareTask("Fetch Session", "enrichment", 20,  3))
luna.add_task( CareTask("Brushing",      "groom",      10,  2))

# --- Register pets with owner (loads default tasks automatically) ---
owner.add_pet(buddy)
owner.add_pet(luna)

# --- Generate schedule ---
scheduler = Scheduler(strategy="priority")
plan = scheduler.generate_plan(owner)

# --- Print results ---
print("=" * 45)
print("        PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 45)
print(plan.get_summary())
print("=" * 45)
print(f"Owner       : {owner.name}")
print(f"Time budget : {owner.time_available_minutes} min")
print(f"Time used   : {plan.total_time_used()} min")
print(f"Pets        : {', '.join(p.name for p in owner.pets)}")
