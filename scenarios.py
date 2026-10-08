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

    # Criteria 3, 4, and 5 all say "5 different queries" / "5 different
    # items" — not "the same query 5 times" like criteria 1 and 2. So these
    # five scenarios each use a different, distinctive query that (checked
    # against data/listings.json by hand) scores clearly highest for one
    # specific listing, with no other listing close behind. Each also
    # specifies a different max_price, so the same five runs double as
    # evidence for criterion 5 (price ceiling respected).
    #
    # Rather than writing three separate batches of five queries each (15
    # scenarios, ~3x the model calls for no real benefit), these five are
    # reused for all three criteria: the "criterion" field is set to 3, but
    # the README manually builds the criterion-4 and criterion-5 rows from
    # this same output too — see the Run Log for how each row is read.
    {
        "name": "diverse item 1 — leather bomber",
        "query": "leather bomber jacket under $80",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "diverse item 2 — silk button-down",
        "query": "silk button-down sage green under $35",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "diverse item 3 — velvet blazer",
        "query": "velvet blazer emerald green under $60",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "diverse item 4 — crochet halter top",
        "query": "crochet halter top under $25",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "diverse item 5 — suede chelsea boots",
        "query": "suede chelsea boots tan under $50",
        "wardrobe": "example",
        "criterion": 3,
    },
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
