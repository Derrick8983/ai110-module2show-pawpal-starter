# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
Make a plan for the day for a pet
Add different pets by names
Make scedule for a pet
- Briefly describe your initial UML design.
The system has six classes: Pet and CareTask are dataclasses that store pet profiles and care activities. PetOwner tracks the owner's time budget and task list, while CareTaker handles delegated tasks. Scheduler applies a priority-based strategy to select tasks within the time limit, producing a DailyPlan that holds the final schedule and reasoning.


- What classes did you include, and what responsibilities did you assign to each?

PetOwner
Attributes
name
available_time_per_day
preferences
maybe contact/reminder preference later
Methods
update_preferences()
set_available_time()
view_daily_plan()

CareTask
Attributes
name
duration
priority
Methods
edit_task()

Scheduler
Attributes
tasks
time_limit
Methods
generate_plan()

DailyPlan
Attributes
tasks_selected
total_time
Methods
display_plan()

**b. Design changes**

- Did your design change during implementation? Yes
- If yes, describe at least one change and why you made it.
ladded a pet_name field to CareTask so tasks can be traced back to their pet, updated add_pet () to automatically pull in a pet's default tasks when it's added to the owner, and removed the redundant max_minutes from Scheduler so the owner's time_available_minutes is the single time constraint used when building a plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
