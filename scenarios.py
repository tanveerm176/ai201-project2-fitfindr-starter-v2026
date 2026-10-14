"""
The runs your test needs. <- UNIT 4, MILESTONE 3

`run_eval.py` runs each scenario five times with caching disabled.
"""

SCENARIOS = [
    {
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "impossible query stops early",
        "query": "unobtainium ceremonial jumpsuit size ZZQX under $0.01",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        "name": "selected item ID reaches outfit tool",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "fit card includes item facts",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "results respect price ceiling",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "empty wardrobe advice",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about malformed scenarios before a long run."""
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
