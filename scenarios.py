"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    # Criterion 1, other phrasings. Added in unit 4 Milestone 5 after the
    # diagnosis found that every try of criterion 1 used one well-formed query,
    # so its "some phrasings will miss" reason was never tested. Each of these
    # is something the data CAN match, so a failure here is the parser's.
    {
        # Apostrophe in "I'd". Expected to pass both before and after: a control.
        "name": "phrasing: apostrophe and filler",
        "query": "I'd love a cute top for a night out, size M, under $25",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # "size small" and "dollars" instead of "S" and "$50".
        "name": "phrasing: size word and 'dollars'",
        "query": "a denim jacket in size small under 50 dollars",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # "t-shirt" split into "t" and "shirt". Completes either way; a control
        # for the fact that criterion 1 does not judge whether the item is right.
        "name": "phrasing: t-shirt",
        "query": "Under $20 t-shirt",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # "size large" spelled out.
        "name": "phrasing: size large",
        "query": "grab me a black hoodie, size large, under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # Criterion 3 — state. A different matching query from criterion 1, so
        # it isn't just the same run twice. Judged by comparing
        # session["selected_item"]["id"] with the `item id=` in the trace's
        # suggest_outfit step.
        "name": "selected item carries through",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 — the fit card. The SAME query five times, so the same
        # item each time (the first search result is deterministic). Judged by
        # comparing the five fit cards word for word.
        "name": "fit card, same item repeated",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    # Criterion 5 (the size-match rule) tests search_listings directly with five
    # different size queries, so it can't be five identical tries of one query.
    # It lives in check_size_filter.py, and its five cases are the five tries.
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
