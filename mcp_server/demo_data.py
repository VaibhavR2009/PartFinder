"""
PartFinder — Demo / Fixture Data
=================================
These pre-canned responses are returned when DEMO_MODE=true.
They mirror the real SerpApi response shape so agents see the
same data structure in both modes — no agent code changes needed.

This approach lets the author record a demo video without burning
live quota or depending on API uptime on recording day.
"""

# ---------------------------------------------------------------------------
# Home Depot search fixture — "2x4 lumber 8 foot" query
# ---------------------------------------------------------------------------
HD_SEARCH_FIXTURES: dict[str, list[dict]] = {
    "default": [
        {
            "product_id": "206006818",
            "title": "2 in. x 4 in. x 8 ft. Prime Whitewood Stud",
            "price": 4.27,
            "rating": 4.5,
            "reviews": 2341,
            "thumbnail": "https://images.thdstatic.com/productImages/default1.jpg",
            "link": "https://www.homedepot.com/p/206006818",
        },
        {
            "product_id": "100052893",
            "title": "2 in. x 4 in. x 8 ft. #2 Grade Fir Lumber",
            "price": 5.98,
            "rating": 4.3,
            "reviews": 987,
            "thumbnail": "https://images.thdstatic.com/productImages/default2.jpg",
            "link": "https://www.homedepot.com/p/100052893",
        },
    ],
    "wood screw": [
        {
            "product_id": "202031458",
            "title": "#8 x 3 in. Phillips Bugle-Head Coarse Thread Sharp Point Polymer Coated Exterior Screw (1 lb. Pack)",
            "price": 9.98,
            "rating": 4.7,
            "reviews": 5123,
            "thumbnail": "https://images.thdstatic.com/productImages/screw1.jpg",
            "link": "https://www.homedepot.com/p/202031458",
        },
        {
            "product_id": "202031460",
            "title": "#9 x 2-1/2 in. Star Drive Exterior Coated Wood Screws (5 lb. Pack)",
            "price": 21.97,
            "rating": 4.6,
            "reviews": 2891,
            "thumbnail": "https://images.thdstatic.com/productImages/screw2.jpg",
            "link": "https://www.homedepot.com/p/202031460",
        },
    ],
    "plywood": [
        {
            "product_id": "1000138501",
            "title": "3/4 in. x 4 ft. x 8 ft. Sanded Plywood",
            "price": 56.47,
            "rating": 4.4,
            "reviews": 1874,
            "thumbnail": "https://images.thdstatic.com/productImages/ply1.jpg",
            "link": "https://www.homedepot.com/p/1000138501",
        },
        {
            "product_id": "1000138502",
            "title": "1/2 in. x 4 ft. x 8 ft. BC Plywood",
            "price": 42.98,
            "rating": 4.2,
            "reviews": 934,
            "thumbnail": "https://images.thdstatic.com/productImages/ply2.jpg",
            "link": "https://www.homedepot.com/p/1000138502",
        },
    ],
    "cedar": [
        {
            "product_id": "1000771690",
            "title": "2 in. x 6 in. x 8 ft. Select Cedar Decking Board",
            "price": 17.98,
            "rating": 4.5,
            "reviews": 567,
            "thumbnail": "https://images.thdstatic.com/productImages/cedar1.jpg",
            "link": "https://www.homedepot.com/p/1000771690",
        },
        {
            "product_id": "1000771691",
            "title": "1 in. x 6 in. x 8 ft. Western Red Cedar Board",
            "price": 12.48,
            "rating": 4.3,
            "reviews": 445,
            "thumbnail": "https://images.thdstatic.com/productImages/cedar2.jpg",
            "link": "https://www.homedepot.com/p/1000771691",
        },
    ],
    "landscape fabric": [
        {
            "product_id": "300020095",
            "title": "Vigoro 3 ft. x 50 ft. Heavy Duty Landscape Fabric",
            "price": 14.98,
            "rating": 4.1,
            "reviews": 892,
            "thumbnail": "https://images.thdstatic.com/productImages/fabric1.jpg",
            "link": "https://www.homedepot.com/p/300020095",
        },
        {
            "product_id": "300020096",
            "title": "Vigoro 4 ft. x 100 ft. Weed Barrier Landscape Fabric",
            "price": 21.98,
            "rating": 4.0,
            "reviews": 723,
            "thumbnail": "https://images.thdstatic.com/productImages/fabric2.jpg",
            "link": "https://www.homedepot.com/p/300020096",
        },
    ],
    "corner bracket": [
        {
            "product_id": "202034204",
            "title": "Simpson Strong-Tie 3 in. x 3 in. Galvanized Angle Bracket (4-Pack)",
            "price": 7.47,
            "rating": 4.6,
            "reviews": 1234,
            "thumbnail": "https://images.thdstatic.com/productImages/bracket1.jpg",
            "link": "https://www.homedepot.com/p/202034204",
        },
        {
            "product_id": "202034205",
            "title": "Everbilt 4 in. Zinc-Plated Corner Brace (4-Pack)",
            "price": 5.98,
            "rating": 4.4,
            "reviews": 876,
            "thumbnail": "https://images.thdstatic.com/productImages/bracket2.jpg",
            "link": "https://www.homedepot.com/p/202034205",
        },
    ],
}

# ---------------------------------------------------------------------------
# Home Depot product detail fixture
# ---------------------------------------------------------------------------
HD_PRODUCT_FIXTURES: dict[str, dict] = {
    "206006818": {
        "product_id": "206006818",
        "title": "2 in. x 4 in. x 8 ft. Prime Whitewood Stud",
        "price": 4.27,
        "brand": "Unbranded",
        "model": "SWE42-0800",
        "description": "Framing stud suitable for interior/exterior framing. Kiln-dried for stability.",
        "dimensions": {"length_in": 96, "width_in": 3.5, "thickness_in": 1.5},
        "material": "Whitewood / SPF",
        "rating": 4.5,
        "in_stock_locally": True,
        "availability": "In stock at selected store",
        "fulfillment": "Store pickup available today",
        "link": "https://www.homedepot.com/p/206006818",
    },
    "202031458": {
        "product_id": "202031458",
        "title": "#8 x 3 in. Phillips Bugle-Head Coarse Thread Sharp Point Polymer Coated Exterior Screw (1 lb. Pack)",
        "price": 9.98,
        "brand": "Grip-Rite",
        "model": "GR3CS1",
        "description": "Polymer coated for corrosion resistance. Suitable for exterior wood applications.",
        "specifications": {"length_in": 3.0, "diameter": "#8", "coating": "Polymer/Green", "drive": "Phillips", "thread": "Coarse"},
        "quantity": "approx. 130 per lb",
        "rating": 4.7,
        "in_stock_locally": True,
        "availability": "In stock at selected store",
        "fulfillment": "Store pickup available today",
        "link": "https://www.homedepot.com/p/202031458",
    },
    "1000138501": {
        "product_id": "1000138501",
        "title": "3/4 in. x 4 ft. x 8 ft. Sanded Plywood",
        "price": 56.47,
        "brand": "Unbranded",
        "description": "Sanded plywood for shelving, furniture, cabinets.",
        "dimensions": {"thickness_in": 0.75, "width_ft": 4, "length_ft": 8},
        "material": "Softwood plywood",
        "grade": "BC",
        "rating": 4.4,
        "in_stock_locally": True,
        "availability": "In stock at selected store",
        "fulfillment": "Store pickup available today or delivery in 2 days",
        "link": "https://www.homedepot.com/p/1000138501",
    },
    "1000771690": {
        "product_id": "1000771690",
        "title": "2 in. x 6 in. x 8 ft. Select Cedar Decking Board",
        "price": 17.98,
        "brand": "Unbranded",
        "description": "Western Red Cedar, naturally rot and insect resistant. Ideal for outdoor raised beds, decking.",
        "dimensions": {"thickness_in": 1.5, "width_in": 5.5, "length_ft": 8},
        "material": "Western Red Cedar",
        "rating": 4.5,
        "in_stock_locally": True,
        "availability": "In stock at selected store",
        "fulfillment": "Store pickup available today",
        "link": "https://www.homedepot.com/p/1000771690",
    },
    "300020095": {
        "product_id": "300020095",
        "title": "Vigoro 3 ft. x 50 ft. Heavy Duty Landscape Fabric",
        "price": 14.98,
        "brand": "Vigoro",
        "description": "Heavy duty woven polypropylene. Blocks weeds while allowing water and nutrients through.",
        "dimensions": {"width_ft": 3, "length_ft": 50},
        "material": "Woven polypropylene",
        "rating": 4.1,
        "in_stock_locally": True,
        "availability": "In stock at selected store",
        "fulfillment": "Store pickup available today",
        "link": "https://www.homedepot.com/p/300020095",
    },
    "202034204": {
        "product_id": "202034204",
        "title": "Simpson Strong-Tie 3 in. x 3 in. Galvanized Angle Bracket (4-Pack)",
        "price": 7.47,
        "brand": "Simpson Strong-Tie",
        "description": "Galvanized steel corner brace for structural connections. 3x3 inch L-shape.",
        "specifications": {"size": "3x3 in", "material": "Galvanized steel", "pack": 4},
        "rating": 4.6,
        "in_stock_locally": True,
        "availability": "In stock at selected store",
        "fulfillment": "Store pickup available today",
        "link": "https://www.homedepot.com/p/202034204",
    },
}

# ---------------------------------------------------------------------------
# Amazon search fixture
# ---------------------------------------------------------------------------
AMAZON_SEARCH_FIXTURES: dict[str, list[dict]] = {
    "default": [
        {
            "asin": "B089FT1DRR",
            "title": "Prime-Line Products Wood Screws, Flat Head, Philips, #8 x 3-Inch, Steel Construction",
            "price": 11.99,
            "rating": 4.5,
            "reviews": 678,
            "link": "https://www.amazon.com/dp/B089FT1DRR",
            "prime": True,
        },
        {
            "asin": "B07MFJTHWG",
            "title": "NATIONAL NAIL 0050218 Grip Rite Exterior Screw, 5 lb, #9 x 2-1/2 in",
            "price": 24.99,
            "rating": 4.6,
            "reviews": 1231,
            "link": "https://www.amazon.com/dp/B07MFJTHWG",
            "prime": True,
        },
    ],
}

# ---------------------------------------------------------------------------
# Amazon product detail fixture
# ---------------------------------------------------------------------------
AMAZON_PRODUCT_FIXTURES: dict[str, dict] = {
    "B089FT1DRR": {
        "asin": "B089FT1DRR",
        "title": "Prime-Line Products Wood Screws, Flat Head, Philips, #8 x 3-Inch, Steel Construction",
        "price": 11.99,
        "brand": "Prime-Line",
        "description": "Flat head Phillips drive, #8 x 3-inch exterior wood screws. Corrosion resistant coating.",
        "rating": 4.5,
        "reviews": 678,
        "prime": True,
        "fulfillment": "Ships in 1-2 days (Prime)",
        "link": "https://www.amazon.com/dp/B089FT1DRR",
    },
}


def get_hd_search_fixture(query: str, n: int) -> list[dict]:
    """Return best-matching HD search fixture, capped to n results."""
    query_lower = query.lower()
    for key in HD_SEARCH_FIXTURES:
        if key != "default" and key in query_lower:
            return HD_SEARCH_FIXTURES[key][:n]
    return HD_SEARCH_FIXTURES["default"][:n]


def get_hd_product_fixture(product_id: str) -> dict | None:
    return HD_PRODUCT_FIXTURES.get(product_id)


def get_amazon_search_fixture(query: str, n: int) -> list[dict]:
    """Return Amazon search fixture, capped to n results."""
    return AMAZON_SEARCH_FIXTURES["default"][:n]


def get_amazon_product_fixture(asin: str) -> dict | None:
    return AMAZON_PRODUCT_FIXTURES.get(asin)
