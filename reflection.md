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
One tradeoff my scheduler makes is that it prioritizes simplicity over handling every real world time case. Right now, it mainly selects tasks based on priority, duration, and available time instead of checking for more complex overlaps or flexible scheduling windows. This makes the algorithm easier to understand, test, and maintain, but it also means the schedule is less realistic in situations where tasks could partially overlap or be moved around more dynamically. I chose to keep this simpler version because it is more readable and fits the scope of the project better.
- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable for this scenario because the app is designed for a busy pet owner who needs a quick and clear daily plan rather than a perfectly optimized schedule. A simpler approach ensures the plan is easy to generate and explain, which aligns with the goal of providing a helpful and understandable assistant rather than a highly complex scheduling system.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI mainly for design brainstorming, structuring my classes, and refining my scheduling logic. It helped me break down the problem into manageable components and suggested cleaner ways to implement task selection. The most helpful prompts were specific ones about improving logic or deciding where certain features should belong in the system.
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment I did not accept an AI suggestion was when it provided a more compact, Pythonic version of my scheduling algorithm. While it was shorter, it reduced readability. I evaluated it by comparing how easy each version was to understand and debug, and chose to keep my original version because it was clearer.
- How did you evaluate or verify what the AI suggested?



---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested behaviors such as selecting tasks within the available time, prioritizing higher priority tasks, and ensuring tasks were added correctly to the daily plan. These tests were important to confirm that the scheduler followed the intended rules and produced a valid plan.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I am fairly confident that my scheduler works correctly for standard cases. If I had more time, I would test edge cases such as tasks with equal priority, very limited available time, and handling recurring tasks more thoroughly.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
Opening the strealit at the end was very satisfying 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration, I would improve the scheduling logic to handle more realistic scenarios, such as overlapping tasks or more flexible time allocation.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that ai has gotten really good and its use cases expand each day with its effectiveness. 
