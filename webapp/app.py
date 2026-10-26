"""
Flask dashboard / web application presenting the e-commerce platform's
functionality (US-1 - US-9) through a browser UI, backed directly by the
`ecommerce_platform` package built in prior steps. No new business logic is
implemented here — this layer only wires HTTP routes/templates onto the
existing services and surfaces their state as real-time metrics.
"""

import json
import sys
import uuid
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ecommerce_platform import (  # noqa: E402
    Event,
    EventCaptureService,
    EventStore,
    Product,
    ProductCatalog,
    ProductNotFoundError,
    RecommendationService,
    SearchService,
    SellerInventoryService,
    ValidationError,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # local/demo use only

SYNTHETIC_DATA_DIR = Path(__file__).resolve().parents[1] / "synthetic_data"

# ---------------------------------------------------------------------------
# Shared in-memory service instances (same services generated in prior steps)
# ---------------------------------------------------------------------------

catalog = ProductCatalog()
inventory = SellerInventoryService(catalog)
search_service = SearchService(catalog)
event_store = EventStore()
event_capture = EventCaptureService(event_store)


def load_synthetic_data():
    """
    Seed the in-memory catalog and event store from the synthetic datasets
    generated earlier (synthetic_data/products.jsonl, events.jsonl), so the
    dashboard and search/recommendation pages reflect realistic volume
    instead of a handful of manually-entered demo records.
    """
    products_file = SYNTHETIC_DATA_DIR / "products.jsonl"
    if products_file.exists():
        with open(products_file) as f:
            for line in f:
                row = json.loads(line)
                catalog.save(Product(
                    product_id=row["product_id"],
                    seller_id=row["seller_id"],
                    name=row["name"],
                    category=row["category"],
                    price=row["price"],
                    stock_quantity=row["stock_quantity"],
                    attributes=row.get("attributes", {}),
                    created_at=row.get("created_at"),
                    updated_at=row.get("updated_at"),
                ))

    events_file = SYNTHETIC_DATA_DIR / "events.jsonl"
    if events_file.exists():
        with open(events_file) as f:
            for line in f:
                row = json.loads(line)
                event_store.persist(Event(
                    event_id=row["event_id"],
                    event_type=row["event_type"],
                    user_id=row.get("user_id"),
                    session_id=row["session_id"],
                    product_id=row.get("product_id"),
                    query_id=row.get("query_id"),
                    metadata=row.get("metadata", {}),
                    timestamp=row.get("timestamp"),
                ))


load_synthetic_data()


class DemoMLClient:
    """
    Stand-in for the black-box recommendation/ML system (explicitly out of
    scope). Returns a simple, deterministic slice of the catalog so the
    recommendations page has something real to render; this is NOT a
    recommendation algorithm.
    """

    def get_recommendations(self, user_id, session_id):
        products = catalog.all()
        return [p.product_id for p in products[:5]]


recommendation_service = RecommendationService(DemoMLClient())


def get_session_id() -> str:
    """Assign/reuse a stable per-browser session_id, as used throughout US-8/US-9."""
    if "session_id" not in session:
        session["session_id"] = f"SESS-{uuid.uuid4().hex[:8]}"
    return session["session_id"]


def get_user_id():
    """Optional buyer identifier (US-7's 'account/session'); None for guests."""
    return session.get("user_id")


# ---------------------------------------------------------------------------
# Dashboard (real-time metrics)
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    return render_template("dashboard.html", metrics=compute_metrics())


@app.route("/api/metrics")
def api_metrics():
    """Polled by the dashboard page's JS to refresh metrics without a full reload."""
    return jsonify(compute_metrics())


def compute_metrics():
    products = catalog.all()
    all_events = event_store.get_events_for_ml()
    event_counts = {etype: 0 for etype in
                     ("search", "click", "product_view", "scroll", "time_spent", "add_to_cart")}
    for event in all_events:
        event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

    return {
        "total_products": len(products),
        "total_sellers": len({p.seller_id for p in products}),
        "total_stock_units": sum(p.stock_quantity for p in products),
        "out_of_stock_products": sum(1 for p in products if p.stock_quantity == 0),
        "total_inventory_value": sum(p.price * p.stock_quantity for p in products),
        "total_events": len(all_events),
        "event_counts": event_counts,
        "total_searches": event_counts["search"],
    }


# ---------------------------------------------------------------------------
# US-1 / US-2: Seller inventory management
# ---------------------------------------------------------------------------

@app.route("/seller")
def seller_home():
    return render_template("seller_add.html", error=None)


@app.route("/seller/add", methods=["POST"])
def seller_add_product():
    form = request.form
    attributes = {}
    if form.get("attr_key") and form.get("attr_value"):
        attributes[form["attr_key"]] = form["attr_value"]

    try:
        stock_quantity = int(form["stock_quantity"]) if form.get("stock_quantity") not in (None, "") else None
        price = float(form["price"]) if form.get("price") not in (None, "") else None
        inventory.add_product(
            seller_id=form.get("seller_id", ""),
            name=form.get("name", ""),
            category=form.get("category", ""),
            price=price,
            stock_quantity=stock_quantity,
            attributes=attributes,
        )
    except ValidationError as exc:
        return render_template("seller_add.html", error=str(exc))

    return redirect(url_for("seller_products"))


@app.route("/seller/products")
def seller_products():
    return render_template("seller_products.html", products=catalog.all())


@app.route("/seller/products/<product_id>/edit", methods=["GET", "POST"])
def seller_edit_product(product_id):
    product = catalog.get(product_id)
    if product is None:
        return render_template("seller_edit.html", product=None, error="Product does not exist", product_id=product_id)

    if request.method == "POST":
        form = request.form
        try:
            inventory.update_product(
                product_id,
                name=form.get("name") or None,
                category=form.get("category") or None,
                price=float(form["price"]) if form.get("price") else None,
                stock_quantity=int(form["stock_quantity"]) if form.get("stock_quantity") not in (None, "") else None,
            )
        except ProductNotFoundError as exc:
            return render_template("seller_edit.html", product=None, error=str(exc), product_id=product_id)
        return redirect(url_for("seller_products"))

    return render_template("seller_edit.html", product=product, error=None, product_id=product_id)


# ---------------------------------------------------------------------------
# US-3 / US-4 / US-5 / US-6: Buyer search, filters, ranking, facets
# ---------------------------------------------------------------------------

@app.route("/search")
def search_page():
    query_text = request.args.get("q", "")
    filters = {}
    for key in request.args:
        if key.startswith("filter_") and request.args.get(key):
            filters[key[len("filter_"):]] = request.args[key]

    results = search_service.search(query_text=query_text, filters=filters)
    facets = search_service.get_facets(results)

    if query_text or filters:
        query_id = f"QRY-{uuid.uuid4().hex[:8]}"
        event_capture.capture_search(get_user_id(), get_session_id(), query_id)
    else:
        query_id = None

    # Build facet links that merge the clicked value into the currently
    # applied filters, so selecting a facet narrows on top of US-4 filters
    # already in effect (TC-6.2), rather than replacing them.
    facet_links = {}
    for facet_name, values in facets.items():
        facet_links[facet_name] = []
        for value in values:
            merged = {**filters, facet_name: value}
            query_args = {f"filter_{k}": v for k, v in merged.items()}
            facet_links[facet_name].append((value, url_for("search_page", q=query_text, **query_args)))

    return render_template(
        "search.html",
        query_text=query_text,
        filters=filters,
        results=results,
        facet_links=facet_links,
        query_id=query_id,
    )


@app.route("/product/<product_id>")
def product_detail(product_id):
    product = catalog.get(product_id)
    if product is None:
        return render_template("product_detail.html", product=None), 404

    referrer_query_id = request.args.get("query_id")
    if referrer_query_id:
        event_capture.capture_click(get_user_id(), get_session_id(), product_id)
    event_capture.capture_product_view(get_user_id(), get_session_id(), product_id)

    return render_template("product_detail.html", product=product)


@app.route("/product/<product_id>/add_to_cart", methods=["POST"])
def add_to_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    event_capture.capture_add_to_cart(get_user_id(), get_session_id(), product_id, quantity=quantity)
    return redirect(url_for("product_detail", product_id=product_id))


# ---------------------------------------------------------------------------
# US-7: Personalized recommendations
# ---------------------------------------------------------------------------

@app.route("/recommendations", methods=["GET", "POST"])
def recommendations_page():
    if request.method == "POST":
        session["user_id"] = request.form.get("user_id") or None
        return redirect(url_for("recommendations_page"))

    recommended_ids = recommendation_service.get_recommendations_for_display(
        get_user_id(), get_session_id()
    )
    recommended_products = [catalog.get(pid) for pid in recommended_ids if catalog.get(pid)]

    return render_template(
        "recommendations.html",
        recommended_products=recommended_products,
        user_id=get_user_id(),
    )


# ---------------------------------------------------------------------------
# US-8: Client-reported interaction events (scroll, time spent)
# ---------------------------------------------------------------------------

@app.route("/api/events/scroll", methods=["POST"])
def api_capture_scroll():
    data = request.get_json(silent=True) or {}
    event_capture.capture_scroll(
        get_user_id(), get_session_id(),
        product_id=data.get("product_id"),
        metadata={"scroll_depth_percent": data.get("scroll_depth_percent")},
    )
    return jsonify({"status": "logged"})


@app.route("/api/events/time_spent", methods=["POST"])
def api_capture_time_spent():
    data = request.get_json(silent=True) or {}
    event_capture.capture_time_spent(
        get_user_id(), get_session_id(),
        product_id=data.get("product_id"),
        duration_seconds=data.get("duration_seconds", 0),
    )
    return jsonify({"status": "logged"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
