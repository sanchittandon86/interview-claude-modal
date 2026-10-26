# 4. Synthetic Data

## Generate

Created synthetic datasets covering every entity referenced by the user stories and test cases: sellers, products (seller inventory), buyers/sessions, search query logs, interaction events, and sample recommendation output. Each dataset mixed normal records with deliberate edge-case rows.

### Entity schemas

| Entity | Key fields |
|---|---|
| Seller | seller_id, name, email, joined_date |
| Product | product_id, seller_id, name, category, brand, price, currency, stock_quantity, attributes, status, created_at, updated_at |
| User/Session | user_id (nullable for guests), session_id, device_type, location, created_at |
| Search query log | query_id, user_id, session_id, query_text, filters_applied, facets_selected, results_count, ranking_order, timestamp |
| Event | event_id, event_type, user_id, session_id, product_id, query_id, metadata, timestamp |
| Recommendation | recommendation_id, user_id, session_id, recommended_products, generated_at, source |

### Illustrative edge cases seeded
- Invalid submission payloads (blank name/category, null stock quantity) — for TC-1.2/TC-1.3.
- Non-existent product reference — for TC-2.3.
- No-match and empty-string queries — for TC-3.2/TC-3.3/TC-4.3.
- Out-of-stock product (`stock_quantity: 0`) — for inventory edge cases.
- Empty recommendation set — for TC-7.3.
- Guest/anonymous session (`user_id: null`) — for US-7's account/session context.

## Validate: Analysis & Discussion

| Metric | Result | Analysis & Discussion |
|---|---|---|
| Realism | Pass | ISO-8601 timestamps, plausible pricing, varied categories (apparel, electronics, home goods), nested attribute objects for facets, realistic device/location diversity across 8 locations and 3 device types. |
| Completeness | Pass | Every field referenced across the user stories and test cases was present, including invalid/edge payloads matching their corresponding test cases. |
| Volume Adequacy | Failed initially, then Pass | The first illustrative dataset (6 products, 3 sellers, 4 users, 7 queries, ~13 events, 3 recommendations) was sufficient for functional testing but explicitly **not** sufficient for the "high-load" requirement of TC-9.3/TC-8.7. This was flagged as a gap requiring remediation. |

### Remediation: `generate_data.py`

A seeded (`random.seed(42)`), reproducible generator script was built, producing:

| Dataset | Volume |
|---|---|
| Sellers | 50 |
| Products | 2,000 (across 10 categories, each with category-appropriate attributes) |
| Users/Sessions | 3,000 (10% guest/anonymous) |
| Search query logs | 8,000 |
| Events | 60,000 total — 500 "burst" sessions × 40 rapid-fire events (100–900ms apart) + 40,000 steady-state background events |
| Recommendations | 3,000 (5% deliberately empty) |

Re-validated: Realism Pass, Completeness Pass, Volume Adequacy Pass — the burst-session pattern directly exercises TC-8.7 (rapid sequential events) and TC-9.3 (high-volume persistence) at realistic scale.

## Outcome

Output files (`sellers.json`, `products.jsonl`, `users_sessions.jsonl`, `search_queries.jsonl`, `events.jsonl`, `recommendations.jsonl`) were later loaded directly into the running Flask app via `load_synthetic_data()` (Phase 8), replacing small manually-entered demo data so the dashboard and search reflect realistic, production-like volume.
