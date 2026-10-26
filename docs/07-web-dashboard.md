# 7. Web Dashboard

## Generate

Built a Flask app (`webapp/app.py`) wiring HTTP routes and templates directly onto the existing `ecommerce_platform` services. No new business logic was added — only a presentation layer over already-validated code.

### Routes → user stories

| Route | User Story |
|---|---|
| `GET /seller`, `POST /seller/add` | US-1 |
| `GET/POST /seller/products/<id>/edit` | US-2 |
| `GET /search` | US-3, US-4, US-5, US-6 |
| `GET /product/<id>` | logs click + product_view (US-8) |
| `POST /product/<id>/add_to_cart` | US-8 (add_to_cart) |
| `POST /api/events/scroll`, `/api/events/time_spent` | US-8 (scroll, time_spent), called by client-side `events.js` |
| `GET /recommendations` | US-7, via a stubbed `DemoMLClient` (real ML model is out of scope) |
| `GET /`, `GET /api/metrics` | Real-time dashboard — polled every 3s via JS |

### Template structure

```
webapp/
  app.py
  templates/
    base.html, dashboard.html, seller_add.html, seller_products.html,
    seller_edit.html, search.html, product_detail.html, recommendations.html
  static/
    style.css, events.js
```

## Validate: Analysis & Discussion

| Metric | Result | Analysis & Discussion |
|---|---|---|
| Completeness | Pass | Every user story (US-1–US-9) is reachable through the UI — verified route-by-route against the table above. |
| Usability | Pass | Dashboard auto-refresh confirmed firing continuously in server logs (every ~3s, no errors). Validation errors render inline on the same form (HTTP 200 with error message) rather than crashing. Navigation worked end-to-end with no dead links. |
| Metric Accuracy | Pass | A controlled sequence of known actions (2 valid products + 1 deliberately invalid submission, 2 searches, 1 click/view/add-to-cart/scroll/time-spent) produced dashboard numbers matching expected counts exactly: `total_products=2`, `total_sellers=2`, `total_stock_units=10`, `out_of_stock_products=1`, `total_events=7`, `total_searches=2`. |

### Smoke test commands run
- Added product (valid + invalid cases), confirmed validation error path returns the form with an inline error.
- Updated a product, confirmed stock change persisted.
- Updated a non-existent product ID, confirmed error response.
- Searched with a query + facet filter, confirmed results narrowed correctly.
- Visited product detail (triggers click + product_view), added to cart, fired scroll/time-spent API calls.
- Fetched `/api/metrics` after each action and diffed against expected counts — zero discrepancies.

## Outcome

A working, testable UI layer verified both by scripted checks and live browser use, with zero server errors encountered during validation (only a harmless `/favicon.ico` 404, which doesn't affect functionality).
