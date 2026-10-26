"""
Executable test cases for US-1 through US-9, mapped 1:1 to the TC-x.x IDs
defined during test-case generation. Run with: pytest tests/test_platform.py
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ecommerce_platform import (
    EventCaptureService,
    EventStore,
    ProductCatalog,
    ProductNotFoundError,
    RecommendationService,
    SearchService,
    SellerInventoryService,
    ValidationError,
)


@pytest.fixture
def catalog():
    return ProductCatalog()


@pytest.fixture
def inventory(catalog):
    return SellerInventoryService(catalog)


@pytest.fixture
def search(catalog):
    return SearchService(catalog)


@pytest.fixture
def event_store():
    return EventStore()


@pytest.fixture
def events(event_store):
    return EventCaptureService(event_store)


# ---------------------------------------------------------------------------
# US-1: Add New Product
# ---------------------------------------------------------------------------

def test_TC_1_1_add_product_with_all_required_details(inventory, search):
    product = inventory.add_product(
        seller_id="SEL-1", name="Denim Jacket", category="Apparel > Jackets",
        price=59.99, stock_quantity=10,
    )
    assert product.product_id is not None
    results = search.search("denim")
    assert product.product_id in [p.product_id for p in results]


def test_TC_1_2_missing_required_product_details(inventory):
    with pytest.raises(ValidationError):
        inventory.add_product(
            seller_id="SEL-1", name="", category="", price=19.99, stock_quantity=10,
        )


def test_TC_1_3_missing_stock_quantity(inventory):
    with pytest.raises(ValidationError):
        inventory.add_product(
            seller_id="SEL-1", name="Bluetooth Speaker", category="Electronics > Audio",
            price=39.99, stock_quantity=None,
        )


def test_TC_1_4_verify_searchability_after_save(inventory, search):
    product = inventory.add_product(
        seller_id="SEL-1", name="Running Sneakers", category="Footwear > Sneakers",
        price=74.50, stock_quantity=45,
    )
    results = search.search("sneakers")
    assert any(p.product_id == product.product_id for p in results)


# ---------------------------------------------------------------------------
# US-2: Update Existing Product
# ---------------------------------------------------------------------------

def test_TC_2_1_update_details_of_existing_product(inventory, search):
    product = inventory.add_product("SEL-1", "Old Name", "Apparel > Shirts", 20.0, 5)
    inventory.update_product(product.product_id, name="New Name")
    results = search.search("New Name")
    assert any(p.product_id == product.product_id and p.name == "New Name" for p in results)


def test_TC_2_2_update_stock_quantity_of_existing_product(inventory, catalog):
    product = inventory.add_product("SEL-1", "Candle Trio", "Home > Decor", 24.99, 200)
    inventory.update_product(product.product_id, stock_quantity=0)
    assert catalog.get(product.product_id).stock_quantity == 0


def test_TC_2_3_update_non_existent_product(inventory):
    with pytest.raises(ProductNotFoundError):
        inventory.update_product("PRD-9999-DOES-NOT-EXIST", name="Ghost Product")


def test_TC_2_4_verify_reflection_timing(inventory, catalog):
    product = inventory.add_product("SEL-1", "Dinnerware Set", "Home > Kitchen", 64.99, 30)
    original_updated_at = product.updated_at
    inventory.update_product(product.product_id, price=49.99)
    refreshed = catalog.get(product.product_id)
    assert refreshed.price == 49.99
    assert refreshed.updated_at >= original_updated_at


# ---------------------------------------------------------------------------
# US-3: Search Products by Query
# ---------------------------------------------------------------------------

def test_TC_3_1_search_with_matching_query(inventory, search):
    inventory.add_product("SEL-1", "Wireless Headphones", "Electronics > Audio", 129.99, 8)
    results = search.search("headphones")
    assert len(results) >= 1


def test_TC_3_2_search_with_no_matches(inventory, search):
    inventory.add_product("SEL-1", "Candle Trio", "Home > Decor", 24.99, 200)
    results = search.search("flying hoverboard shoes")
    assert results == []


def test_TC_3_3_search_with_empty_query_string(inventory, search):
    inventory.add_product("SEL-1", "Candle Trio", "Home > Decor", 24.99, 200)
    results = search.search("")
    assert isinstance(results, list)
    assert len(results) >= 1


# ---------------------------------------------------------------------------
# US-4: Filter Search Results
# ---------------------------------------------------------------------------

def test_TC_4_1_apply_single_filter_to_search(inventory, search):
    inventory.add_product("SEL-1", "Blue Jacket", "Apparel > Jackets", 59.99, 10, {"color": "Blue"})
    inventory.add_product("SEL-1", "Red Jacket", "Apparel > Jackets", 59.99, 10, {"color": "Red"})
    results = search.search("jacket", filters={"color": "Blue"})
    assert all(p.attributes.get("color") == "Blue" for p in results)
    assert len(results) == 1


def test_TC_4_2_apply_multiple_filters_to_search(inventory, search):
    inventory.add_product("SEL-1", "Sneaker A", "Footwear > Sneakers", 70.0, 10, {"color": "White", "size": "7"})
    inventory.add_product("SEL-1", "Sneaker B", "Footwear > Sneakers", 70.0, 10, {"color": "White", "size": "8"})
    results = search.search("sneaker", filters={"color": "White", "size": "7"})
    assert len(results) == 1
    assert results[0].attributes["size"] == "7"


def test_TC_4_3_apply_filter_with_no_matching_results(inventory, search):
    inventory.add_product("SEL-1", "Sneaker A", "Footwear > Sneakers", 70.0, 10, {"color": "White"})
    results = search.search("sneaker", filters={"color": "Purple"})
    assert results == []


def test_TC_4_4_remove_an_applied_filter(inventory, search):
    inventory.add_product("SEL-1", "Sneaker A", "Footwear > Sneakers", 70.0, 10, {"color": "White"})
    inventory.add_product("SEL-1", "Sneaker B", "Footwear > Sneakers", 70.0, 10, {"color": "Black"})
    filtered = search.search("sneaker", filters={"color": "White"})
    assert len(filtered) == 1
    unfiltered = search.search("sneaker", filters={})
    assert len(unfiltered) == 2


# ---------------------------------------------------------------------------
# US-5: View Ranked Search Results
# ---------------------------------------------------------------------------

def test_TC_5_1_results_ordered_by_relevance(inventory, search):
    inventory.add_product("SEL-1", "denim", "Apparel > Jackets", 10.0, 1)
    inventory.add_product("SEL-1", "denim jacket extended", "Apparel > Jackets", 10.0, 1)
    results = search.search("denim")
    assert results[0].name == "denim"  # exact match ranks first


def test_TC_5_2_consistent_ranking_on_repeat_query(inventory, search):
    inventory.add_product("SEL-1", "Item A", "Home > Kitchen", 10.0, 1)
    inventory.add_product("SEL-1", "Item B", "Home > Kitchen", 10.0, 1)
    first_run = [p.product_id for p in search.search("item")]
    second_run = [p.product_id for p in search.search("item")]
    assert first_run == second_run


def test_TC_5_3_ranking_with_single_result(inventory, search):
    inventory.add_product("SEL-1", "Unique Widget", "Home > Kitchen", 10.0, 1)
    results = search.search("unique widget")
    assert len(results) == 1


# ---------------------------------------------------------------------------
# US-6: Navigate via Facets
# ---------------------------------------------------------------------------

def test_TC_6_1_facets_presented_for_search_context(inventory, search):
    inventory.add_product("SEL-1", "Blue Jacket", "Apparel > Jackets", 59.99, 10, {"color": "Blue"})
    inventory.add_product("SEL-1", "Red Jacket", "Apparel > Jackets", 59.99, 10, {"color": "Red"})
    results = search.search("jacket")
    facets = search.get_facets(results)
    assert set(facets["color"]) == {"Blue", "Red"}


def test_TC_6_2_select_a_facet_value(inventory, search):
    inventory.add_product("SEL-1", "Blue Jacket", "Apparel > Jackets", 59.99, 10, {"color": "Blue"})
    inventory.add_product("SEL-1", "Red Jacket", "Apparel > Jackets", 59.99, 10, {"color": "Red"})
    narrowed = search.search("jacket", filters={"color": "Blue"})
    assert len(narrowed) == 1
    assert narrowed[0].attributes["color"] == "Blue"


def test_TC_6_3_facets_with_no_applicable_options(search):
    results = search.search("nonexistent query with no products")
    facets = search.get_facets(results)
    assert facets == {}


# ---------------------------------------------------------------------------
# US-7: View Personalized Recommendations
# ---------------------------------------------------------------------------

class _MockMLClient:
    def __init__(self, recommended):
        self._recommended = recommended

    def get_recommendations(self, user_id, session_id):
        return self._recommended


def test_TC_7_1_display_recommendations_for_account_session():
    service = RecommendationService(_MockMLClient(["PRD-A", "PRD-B"]))
    displayed = service.get_recommendations_for_display("USR-1", "SESS-1")
    assert displayed == ["PRD-A", "PRD-B"]


def test_TC_7_2_display_matches_ml_system_output_exactly():
    ml_output = ["PRD-C", "PRD-A", "PRD-B"]  # deliberately unsorted
    service = RecommendationService(_MockMLClient(ml_output))
    displayed = service.get_recommendations_for_display("USR-1", "SESS-1")
    assert displayed == ml_output  # order/content untouched by the platform


def test_TC_7_3_no_recommendations_returned():
    service = RecommendationService(_MockMLClient([]))
    displayed = service.get_recommendations_for_display("USR-1", "SESS-1")
    assert displayed == []


# ---------------------------------------------------------------------------
# US-8: Capture User Interaction Events
# ---------------------------------------------------------------------------

def test_TC_8_1_search_event_logged(events, event_store):
    events.capture_search("USR-1", "SESS-1", "QRY-1")
    logged = event_store.get_events_for_ml(session_id="SESS-1")
    assert len(logged) == 1
    assert logged[0].event_type == "search"
    assert logged[0].user_id == "USR-1" and logged[0].session_id == "SESS-1"


def test_TC_8_2_click_event_logged(events, event_store):
    events.capture_click("USR-1", "SESS-1", "PRD-1")
    logged = event_store.get_events_for_ml(session_id="SESS-1")
    assert logged[0].event_type == "click"
    assert logged[0].product_id == "PRD-1"


def test_TC_8_3_product_view_event_logged(events, event_store):
    events.capture_product_view("USR-1", "SESS-1", "PRD-1")
    logged = event_store.get_events_for_ml(session_id="SESS-1")
    assert logged[0].event_type == "product_view"


def test_TC_8_4_scroll_event_logged(events, event_store):
    events.capture_scroll("USR-1", "SESS-1", "PRD-1", metadata={"scroll_depth_percent": 65})
    logged = event_store.get_events_for_ml(session_id="SESS-1")
    assert logged[0].event_type == "scroll"
    assert logged[0].metadata["scroll_depth_percent"] == 65


def test_TC_8_5_time_spent_event_logged(events, event_store):
    events.capture_time_spent("USR-1", "SESS-1", "PRD-1", duration_seconds=24)
    logged = event_store.get_events_for_ml(session_id="SESS-1")
    assert logged[0].event_type == "time_spent"
    assert logged[0].metadata["duration_seconds"] == 24


def test_TC_8_6_add_to_cart_event_logged(events, event_store):
    events.capture_add_to_cart("USR-1", "SESS-1", "PRD-1", quantity=2)
    logged = event_store.get_events_for_ml(session_id="SESS-1")
    assert logged[0].event_type == "add_to_cart"
    assert logged[0].metadata["quantity"] == 2


def test_TC_8_7_rapid_sequential_events(events, event_store):
    events.capture_scroll("USR-1", "SESS-1", "PRD-1")
    events.capture_click("USR-1", "SESS-1", "PRD-1")
    events.capture_product_view("USR-1", "SESS-1", "PRD-1")
    logged = event_store.get_events_for_ml(session_id="SESS-1")
    assert len(logged) == 3
    assert len({e.event_id for e in logged}) == 3  # all distinct, none dropped/merged
    assert [e.event_type for e in logged] == ["scroll", "click", "product_view"]


# ---------------------------------------------------------------------------
# US-9: Store and Provide Events to Recommendation System
# ---------------------------------------------------------------------------

def test_TC_9_1_captured_events_are_persisted(events, event_store):
    events.capture_click("USR-1", "SESS-1", "PRD-1")
    assert len(event_store.get_events_for_ml()) == 1


def test_TC_9_2_stored_events_retrievable_by_ml_system(events, event_store):
    events.capture_click("USR-1", "SESS-1", "PRD-1")
    events.capture_click("USR-2", "SESS-2", "PRD-2")
    ml_fetched = event_store.get_events_for_ml(user_id="USR-1")
    assert len(ml_fetched) == 1
    assert ml_fetched[0].user_id == "USR-1"


def test_TC_9_3_high_volume_event_persistence(events, event_store):
    for i in range(2000):
        events.capture_scroll("USR-1", "SESS-1", "PRD-1", metadata={"scroll_depth_percent": i % 100})
    logged = event_store.get_events_for_ml(session_id="SESS-1")
    assert len(logged) == 2000
    assert len({e.event_id for e in logged}) == 2000  # no loss, no duplicate IDs
