# 3. Test Cases

## Generate

Wrote 34 test cases (TC-x.x), mapped 1:1 to the 9 user stories' acceptance criteria, covering normal paths, error paths, and edge cases.

### US-1: Add New Product
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-1.1 | Add product with all required details | Normal | Product is saved; appears in search/discovery |
| TC-1.2 | Missing required product details | Error | Submission fails with a clear error; product not saved |
| TC-1.3 | Missing stock quantity | Error | Submission fails with a clear error; product not saved |
| TC-1.4 | Verify searchability after save | Normal | Newly added product appears in search results |

### US-2: Update Existing Product
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-2.1 | Update details of existing product | Normal | Update succeeds; reflected in subsequent search/view |
| TC-2.2 | Update stock quantity | Normal | Updated stock reflected in subsequent search/view |
| TC-2.3 | Update non-existent product | Error | Update fails with a clear error message |
| TC-2.4 | Verify reflection timing | Normal | Updated info visible immediately (not stale) |

### US-3: Search Products by Query
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-3.1 | Search with matching query | Normal | List of matching products returned |
| TC-3.2 | Search with no matches | Edge | Empty result set, no error thrown |
| TC-3.3 | Search with empty query string | Edge | Handled gracefully, no crash |

### US-4: Filter Search Results
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-4.1 | Apply single filter | Normal | Results include only matching products |
| TC-4.2 | Apply multiple filters | Normal | Results satisfy all applied filters (AND) |
| TC-4.3 | Filter with no matching results | Edge | Empty result set, no error thrown |
| TC-4.4 | Remove an applied filter | Normal | Results re-expand accordingly |

### US-5: View Ranked Search Results
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-5.1 | Results ordered by relevance | Normal | Most relevant products appear first |
| TC-5.2 | Consistent ranking on repeat query | Normal | Identical order across repeated runs |
| TC-5.3 | Ranking with single result | Edge | Single result returned, no ranking errors |

### US-6: Navigate via Facets
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-6.1 | Facets presented for search context | Normal | Relevant facet options displayed |
| TC-6.2 | Select a facet value | Normal | Results and filters update accordingly |
| TC-6.3 | Facets with no applicable options | Edge | No facets displayed, no error thrown |

### US-7: View Personalized Recommendations
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-7.1 | Display recommendations for account/session | Normal | ML system's recommendations are displayed |
| TC-7.2 | Display matches ML output exactly | Normal | Displayed list matches ML output, unaltered |
| TC-7.3 | No recommendations returned | Edge | Empty/no-recommendations state, no error |

### US-8: Capture User Interaction Events
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-8.1 | Search event logged | Normal | Search event logged with context |
| TC-8.2 | Click event logged | Normal | Click event logged with context |
| TC-8.3 | Product view event logged | Normal | View event logged with context |
| TC-8.4 | Scroll event logged | Normal | Scroll event logged with context |
| TC-8.5 | Time-spent event logged | Normal | Duration logged with context |
| TC-8.6 | Add-to-cart event logged | Normal | Add-to-cart event logged with context |
| TC-8.7 | Rapid sequential events | Edge | Each event logged individually, none dropped/merged |

### US-9: Store and Provide Events to Recommendation System
| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| TC-9.1 | Captured events are persisted | Normal | Event persisted in storage |
| TC-9.2 | Stored events retrievable by ML system | Normal | Events retrieved successfully |
| TC-9.3 | High-volume event persistence | Edge | All events persisted, no loss |

## Validate: Analysis & Discussion

| Metric | Result | Analysis & Discussion |
|---|---|---|
| Completeness | Pass | Every user story (US-1–US-9) has at least one test case validating its primary functionality. US-8 alone has 7 (TC-8.1–8.7), one per event type plus a rapid-fire edge case. |
| Validity | Pass | Each test case simulates an action explicitly described in its story's acceptance criteria — submitting a product form, running a query, clicking a product, adding to cart. Nothing invented beyond the spec. |
| Coverage | Pass | Explicit error-handling test cases (TC-1.2, TC-1.3, TC-2.3) appear only for US-1 and US-2 — the only two stories whose acceptance criteria define a failure condition. Edge cases exist wherever a boundary condition was described (empty query, no matches, single result, empty recommendations, event bursts). No error cases were invented for stories that didn't define one, consistent with not adding functionality beyond what was defined. |

## Outcome

34 approved test cases became the executable specification. Code in later phases (`src/ecommerce_platform/`) was written specifically to satisfy these cases, and running the full suite (`tests/test_platform.py`) became the acceptance gate for "done" at every subsequent stage, including after UI changes in Phase 8.
