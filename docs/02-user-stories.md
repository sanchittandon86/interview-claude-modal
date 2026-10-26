# 2. User Stories

**Generate:** Translated the five business functionalities into 9 user stories across three roles — Seller (US-1 Add Product, US-2 Update Product), Buyer (US-3 Search, US-4 Filter, US-5 Ranking, US-6 Facets, US-7 Recommendations), and Platform (US-8 Capture Events, US-9 Store & Provide Events to ML). Each story included concrete acceptance criteria.

**Validate:** Checked against:
- **Coverage** — Pass. All five business-problem functionalities mapped to at least one story.
- **Clarity & Specificity** — Partial. US-8 originally bundled six event types into one vague acceptance criterion, making it hard to verify each type independently.
- **Relevance** — Pass. No story introduced functionality beyond the business problem (no checkout, payments, reviews).

**Refinement:** Split US-8's single criterion into six explicit per-event-type lines (search, click, product_view, scroll, time_spent, add_to_cart) — same scope, finer granularity, re-validated as Pass.

**Outcome:** 9 finalized user stories, each with concrete acceptance criteria, used directly to drive test-case design in the next phase. No functionality was added beyond what the business problem specified.
