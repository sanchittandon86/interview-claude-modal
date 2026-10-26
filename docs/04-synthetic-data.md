# 4. Synthetic Data

**Generate:** Created realistic sample records (sellers, products, buyers/sessions, search logs, events, recommendations) with fields matching every test case, including deliberate edge-case rows (missing fields, zero stock, empty queries/results).

**Validate:** Checked against:
- **Realism** — Pass. ISO-8601 timestamps, plausible pricing/categories, nested attribute objects.
- **Completeness** — Pass. Every field referenced by any user story or test case was present.
- **Volume Adequacy** — Failed initially. The first illustrative dataset (a handful of records) couldn't support high-load/performance testing (TC-9.3's burst scenario).

**Refinement:** Built `generate_data.py`, a seeded, reproducible script producing 50 sellers, 2,000 products, 3,000 users/sessions, 8,000 search logs, 3,000 recommendations, and 60,000 events — including 500 rapid-fire "burst" sessions (40 events each, 100–900ms apart) specifically for load testing.

**Outcome:** Re-validated as Pass on all three metrics. This dataset was later loaded directly into the running web app, replacing small manually-entered demo data so the dashboard and search reflect realistic production-like volume (2,000 products, 50 sellers, 60,000+ events).
