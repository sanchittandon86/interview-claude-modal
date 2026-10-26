"""
High-volume synthetic data generator for the e-commerce search & recommendations
platform (sellers, products, buyers/sessions, search query logs, interaction
events, and sample recommendation output).

Field schemas match the smaller illustrative dataset produced earlier in the
project, scaled up to volumes suitable for performance/high-load testing
(US-1 through US-9, TC-8.7 and TC-9.3 in particular).
"""

import json
import random
from datetime import datetime, timedelta

random.seed(42)

OUT_DIR = "."

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

CATEGORIES = {
    "Apparel > Jackets": {"color": ["Blue", "Black", "Olive", "Red"], "size": ["S", "M", "L", "XL"], "material": ["Denim", "Leather", "Cotton"]},
    "Apparel > Shirts": {"color": ["White", "Black", "Grey", "Navy"], "size": ["S", "M", "L", "XL"], "material": ["Cotton", "Linen", "Polyester"]},
    "Footwear > Sneakers": {"color": ["White", "Black", "Red", "Grey"], "size": ["6", "7", "8", "9", "10"], "material": ["Mesh", "Leather", "Canvas"]},
    "Electronics > Audio": {"color": ["Black", "White", "Silver"], "connectivity": ["Bluetooth 5.2", "Wired", "Wi-Fi"]},
    "Electronics > Smart Home": {"color": ["White", "Black"], "connectivity": ["Wi-Fi/Zigbee", "Wi-Fi", "Bluetooth"]},
    "Home > Kitchen": {"color": ["Ivory", "White", "Black"], "material": ["Ceramic", "Stainless Steel", "Glass"]},
    "Home > Decor": {"scent": ["Lavender", "Vanilla", "Cedar", "Citrus"]},
    "Sports > Fitness": {"color": ["Black", "Blue", "Pink"], "size": ["S", "M", "L"]},
    "Beauty > Skincare": {"skin_type": ["Dry", "Oily", "Combination", "Sensitive"]},
    "Books > Fiction": {"format": ["Paperback", "Hardcover", "E-book"]},
}

BRANDS = ["Urban Threads", "TechNest", "HomeBliss", "FitCore", "PureGlow", "PageTurner", "StrideWear", "NestHome"]
DEVICE_TYPES = ["mobile", "desktop", "tablet"]
LOCATIONS = ["Austin, US", "Toronto, CA", "Manchester, UK", "Berlin, DE", "Sydney, AU", "Mumbai, IN", "Sao Paulo, BR", "Tokyo, JP"]
EVENT_TYPES = ["search", "click", "product_view", "scroll", "time_spent", "add_to_cart"]

START_TIME = datetime(2026, 10, 1, 0, 0, 0)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def random_timestamp(days_span=27):
    return START_TIME + timedelta(
        days=random.uniform(0, days_span),
        seconds=random.randint(0, 86399),
    )


# ---------------------------------------------------------------------------
# Sellers
# ---------------------------------------------------------------------------

NUM_SELLERS = 50
sellers = []
for i in range(1, NUM_SELLERS + 1):
    sellers.append({
        "seller_id": f"SEL-{1000 + i}",
        "name": f"{random.choice(BRANDS)} Store {i}",
        "email": f"seller{i}@example.com",
        "joined_date": (START_TIME - timedelta(days=random.randint(30, 900))).strftime("%Y-%m-%d"),
    })

# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

NUM_PRODUCTS = 2000
products = []
for i in range(1, NUM_PRODUCTS + 1):
    category = random.choice(list(CATEGORIES.keys()))
    attr_options = CATEGORIES[category]
    attributes = {k: random.choice(v) for k, v in attr_options.items()}
    created = random_timestamp()
    # ~2% of products updated after creation (supports US-2 update scenarios)
    updated = created + timedelta(days=random.randint(0, 5)) if random.random() < 0.3 else created
    # ~3% out-of-stock edge case
    stock = 0 if random.random() < 0.03 else random.randint(1, 500)

    products.append({
        "product_id": f"PRD-{20000 + i}",
        "seller_id": random.choice(sellers)["seller_id"],
        "name": f"{category.split(' > ')[-1]} Item #{i}",
        "category": category,
        "brand": random.choice(BRANDS),
        "price": round(random.uniform(9.99, 299.99), 2),
        "currency": "USD",
        "stock_quantity": stock,
        "attributes": attributes,
        "status": "active",
        "created_at": iso(created),
        "updated_at": iso(updated),
    })

product_ids = [p["product_id"] for p in products]

# ---------------------------------------------------------------------------
# Buyers / Sessions
# ---------------------------------------------------------------------------

NUM_USERS = 3000
users = []
for i in range(1, NUM_USERS + 1):
    is_guest = random.random() < 0.1
    users.append({
        "user_id": None if is_guest else f"USR-{30000 + i}",
        "session_id": f"SESS-{i:06d}",
        "device_type": random.choice(DEVICE_TYPES),
        "location": random.choice(LOCATIONS),
        "created_at": iso(random_timestamp()),
    })

# ---------------------------------------------------------------------------
# Search query logs
# ---------------------------------------------------------------------------

QUERY_TERMS = ["jacket", "sneakers", "headphones", "smart hub", "dinnerware", "candle",
               "yoga mat", "serum", "novel", "shirt", "running shoes", "speaker", ""]

NUM_QUERIES = 8000
queries = []
for i in range(1, NUM_QUERIES + 1):
    user = random.choice(users)
    term = random.choice(QUERY_TERMS)
    matches = [] if term == "" or random.random() < 0.05 else random.sample(product_ids, k=min(random.randint(1, 10), len(product_ids)))
    queries.append({
        "query_id": f"QRY-{500000 + i}",
        "user_id": user["user_id"],
        "session_id": user["session_id"],
        "query_text": term,
        "filters_applied": {} if random.random() < 0.6 else {"category": random.choice(list(CATEGORIES.keys()))},
        "facets_selected": {} if random.random() < 0.7 else {"color": random.choice(["Black", "White", "Blue"])},
        "results_count": len(matches),
        "ranking_order": matches,
        "timestamp": iso(random_timestamp()),
    })

query_ids = [q["query_id"] for q in queries]

# ---------------------------------------------------------------------------
# Interaction events (includes realistic session bursts for load testing)
# ---------------------------------------------------------------------------

events = []
event_counter = 0

NUM_BURST_SESSIONS = 500   # sessions with rapid-fire event bursts (TC-8.7 / TC-9.3)
EVENTS_PER_BURST = 40      # events packed into a short window per burst session

for _ in range(NUM_BURST_SESSIONS):
    user = random.choice(users)
    product = random.choice(product_ids)
    query = random.choice(query_ids)
    burst_start = random_timestamp()
    t = burst_start
    for _ in range(EVENTS_PER_BURST):
        event_counter += 1
        etype = random.choice(EVENT_TYPES)
        metadata = {}
        if etype == "scroll":
            metadata = {"scroll_depth_percent": random.randint(1, 100)}
        elif etype == "time_spent":
            metadata = {"duration_seconds": random.randint(1, 180)}
        elif etype == "add_to_cart":
            metadata = {"quantity": random.randint(1, 3)}
        elif etype == "click":
            metadata = {"position_in_results": random.randint(1, 20)}

        events.append({
            "event_id": f"EVT-{700000 + event_counter}",
            "event_type": etype,
            "user_id": user["user_id"],
            "session_id": user["session_id"],
            "query_id": query if etype == "search" else None,
            "product_id": product if etype != "search" else None,
            "timestamp": iso(t),
            "metadata": metadata,
        })
        t += timedelta(milliseconds=random.randint(100, 900))

# Background (non-burst) steady-state events across remaining sessions
NUM_BACKGROUND_EVENTS = 40000
for _ in range(NUM_BACKGROUND_EVENTS):
    event_counter += 1
    user = random.choice(users)
    etype = random.choice(EVENT_TYPES)
    product = random.choice(product_ids)
    query = random.choice(query_ids)
    metadata = {}
    if etype == "scroll":
        metadata = {"scroll_depth_percent": random.randint(1, 100)}
    elif etype == "time_spent":
        metadata = {"duration_seconds": random.randint(1, 180)}
    elif etype == "add_to_cart":
        metadata = {"quantity": random.randint(1, 3)}
    elif etype == "click":
        metadata = {"position_in_results": random.randint(1, 20)}

    events.append({
        "event_id": f"EVT-{700000 + event_counter}",
        "event_type": etype,
        "user_id": user["user_id"],
        "session_id": user["session_id"],
        "query_id": query if etype == "search" else None,
        "product_id": product if etype != "search" else None,
        "timestamp": iso(random_timestamp()),
        "metadata": metadata,
    })

# ---------------------------------------------------------------------------
# Recommendation output samples (from black-box ML system)
# ---------------------------------------------------------------------------

recommendations = []
for i, user in enumerate(random.sample(users, k=3000), start=1):
    empty = random.random() < 0.05
    recommendations.append({
        "recommendation_id": f"REC-{900000 + i}",
        "user_id": user["user_id"],
        "session_id": user["session_id"],
        "recommended_products": [] if empty else random.sample(product_ids, k=random.randint(1, 8)),
        "generated_at": iso(random_timestamp()),
        "source": "recommendation_ml_system",
    })

# ---------------------------------------------------------------------------
# Write output files
# ---------------------------------------------------------------------------

def write_json(filename, data):
    with open(f"{OUT_DIR}/{filename}", "w") as f:
        json.dump(data, f, indent=2)


def write_jsonl(filename, data):
    with open(f"{OUT_DIR}/{filename}", "w") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")


write_json("sellers.json", sellers)
write_jsonl("products.jsonl", products)
write_jsonl("users_sessions.jsonl", users)
write_jsonl("search_queries.jsonl", queries)
write_jsonl("events.jsonl", events)
write_jsonl("recommendations.jsonl", recommendations)

print(f"sellers: {len(sellers)}")
print(f"products: {len(products)}")
print(f"users/sessions: {len(users)}")
print(f"search_queries: {len(queries)}")
print(f"events: {len(events)} (includes {NUM_BURST_SESSIONS} burst sessions x {EVENTS_PER_BURST} events)")
print(f"recommendations: {len(recommendations)}")
