# E-Commerce Search & Recommendations Platform

A foundational e-commerce platform focused on seller inventory management, buyer search (query, filters, ranking, facets), and interaction event capture for a black-box recommendation/ML system. The ML model itself is out of scope.

This project was built using a repeating **Generate → Validate** workflow: at every phase, a draft was produced first, then checked against explicit success metrics before moving on. Where a metric wasn't met, the draft was refined and re-checked.

## How we got here (in order)

1. [Business Problem Definition](docs/01-business-problem.md)
2. [User Stories](docs/02-user-stories.md)
3. [Test Cases](docs/03-test-cases.md)
4. [Synthetic Data](docs/04-synthetic-data.md)
5. [Implementation](docs/05-implementation.md)
6. [Test Execution](docs/06-test-execution.md)
7. [Web Dashboard](docs/07-web-dashboard.md)
8. [UI Polish & Data Integration](docs/08-ui-polish.md)

## Project Layout

```
src/ecommerce_platform/   core package (inventory, search, events, recommendations)
tests/test_platform.py    34 test cases, one per acceptance scenario
synthetic_data/           generator script + 2,000 products / 60,000 events
webapp/                   Flask dashboard and buyer/seller UI
docs/                     phase-by-phase build history (this index)
```

## Running it

```bash
./.venv/bin/python3 webapp/app.py
```
Then open `http://127.0.0.1:5000`.

## Scope

In scope: seller product add/update, buyer search with filters/ranking/facets, event capture (search, click, view, scroll, time spent, add-to-cart), event storage/handoff, and recommendation display. Out of scope: the recommendation/ML model's internal logic — treated strictly as a black box.
