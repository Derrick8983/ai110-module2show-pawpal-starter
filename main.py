from pawpal_system import CareTask, Pet, PetOwner, Scheduler

# --- Setup owner ---
owner = PetOwner(
    name="Jordan",
    email="jordan@email.com",
    time_available_minutes=120,
)

# --- Create pets ---
buddy = Pet(name="Buddy", species="dog", breed="Labrador", age_years=3, weight_lbs=65.0)
luna  = Pet(name="Luna",  species="cat", breed="Siamese",  age_years=5, weight_lbs=9.5)

# --- Add tasks OUT OF ORDER (intentionally jumbled start times) ---
buddy.add_task(CareTask("Evening Walk",  "walk",       20, 2, start_time=1020))  # 17:00
buddy.add_task(CareTask("Flea Medicine", "meds",        5, 1, start_time=480))   # 08:00
buddy.add_task(CareTask("Fetch Session", "enrichment", 20, 3, start_time=900))   # 15:00
buddy.add_task(CareTask("Morning Walk",  "walk",       30, 1, start_time=510))   # 08:30

luna.add_task(CareTask("Brushing",  "groom",       10, 2, start_time=600))   # 10:00
luna.add_task(CareTask("Litter Box","groom",        5, 2, start_time=480))   # 08:00
luna.add_task(CareTask("Playtime",  "enrichment",  15, 3, start_time=780))   # 13:00

# --- Register pets (loads default tasks too) ---
owner.add_pet(buddy)
owner.add_pet(luna)

# --- Mark a few tasks done to demo status filter ---
all_tasks = owner.get_tasks()
all_tasks[0].mark_complete()   # Evening Walk → done
all_tasks[4].mark_complete()   # Brushing → done

# --- Generate schedule ---
scheduler = Scheduler(strategy="priority")
plan = scheduler.generate_plan(owner)

# ── 1. Full schedule (sorted by time via get_summary) ──────────────────────
print("=" * 50)
print("       PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 50)
print(plan.get_summary())
print(f"\nOwner      : {owner.name}")
print(f"Time budget: {owner.time_available_minutes} min")
print(f"Time used  : {plan.total_time_used()} min")

# ── 2. All tasks sorted by start time ──────────────────────────────────────
print("\n" + "=" * 50)
print("  ALL TASKS — sorted by time")
print("=" * 50)
for t in scheduler.sort_by_time(owner.get_tasks()):
    st = f"{t.start_time // 60:02d}:{t.start_time % 60:02d}" if t.start_time is not None else "--:--"
    status = "✓" if t.completed else "○"
    print(f"  {status} {st}  {t.name:<20s} [{t.pet_name}]")

# ── 3. Filter: Buddy's tasks only ──────────────────────────────────────────
print("\n" + "=" * 50)
print("  FILTER — Buddy's tasks")
print("=" * 50)
for t in scheduler.filter_tasks(owner.get_tasks(), pet_name="Buddy"):
    status = "✓" if t.completed else "○"
    print(f"  {status} {t.name}")

# ── 4. Filter: pending tasks only ──────────────────────────────────────────
print("\n" + "=" * 50)
print("  FILTER — pending tasks (all pets)")
print("=" * 50)
for t in scheduler.filter_tasks(owner.get_tasks(), completed=False):
    print(f"  ○ {t.name:<20s} [{t.pet_name}]")

# ── 5. Filter: Luna's completed tasks ──────────────────────────────────────
print("\n" + "=" * 50)
print("  FILTER — Luna's completed tasks")
print("=" * 50)
done = scheduler.filter_tasks(owner.get_tasks(), pet_name="Luna", completed=True)
if done:
    for t in done:
        print(f"  ✓ {t.name}")
else:
    print("  (none)")
