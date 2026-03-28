# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ now includes algorithmic intelligence built on top of the core scheduling system:

- **Sorting** — Tasks are sorted chronologically by time slot using `sort_by_time()`, so the daily plan always reads in order.
- **Filtering** — Filter tasks by completion status or by pet name to get focused views of the schedule.
- **Conflict Detection** — `detect_conflicts()` checks every scheduled task pair for time overlaps and prints a warning instead of crashing, making the system safe and transparent.
- **Recurring Tasks** — Tasks marked as `DAILY` or `WEEKLY` automatically generate the next occurrence when completed, using Python's `timedelta` for accurate date calculation.

Run `python main.py` to see all features in action in the terminal.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains **41 tests** across 8 test classes:

| Area | Tests | Description |
|---|---|---|
| `Task` | 6 | Creation, completion, skipping, resetting, and getter methods |
| `Pet` | 6 | Adding/removing tasks, filtering by priority, pending-task queries |
| `Owner` | 4 | Pet management and aggregating tasks across all pets |
| `Scheduler` | 5 | Plan generation, priority ordering, time-constraint enforcement, empty-pet edge case |
| `Integration` | 2 | Full owner → pet → task → schedule workflow and task lifecycle |
| **Sorting** | **5** | `sort_by_time()` returns tasks in chronological order; handles empty lists, single items, and does not mutate the original |
| **Recurrence** | **6** | `mark_completed()` generates the correct next-occurrence date for DAILY/WEEKLY tasks, returns `None` for ONCE tasks, and leaves the new task in PENDING status |
| **Conflict Detection** | **7** | `detect_conflicts()` flags identical and overlapping slots; correctly ignores adjacent (touching) tasks; reports all pairs when multiple conflicts exist |

### Confidence Level

**5 / 5**

The scheduler's three core intelligent behaviors — chronological sorting, recurring task generation, and conflict detection — are each verified across happy paths and boundary edge cases. The greedy time-constraint fitting and priority ordering are also covered. No tests were found failing against the current implementation.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
