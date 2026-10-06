"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

Search uses the local listings data; the outfit and fit-card tools use the
model adapter in `generate.py`.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import json
import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    keywords = set(re.findall(r"[a-z0-9]+", description.casefold()))
    requested_sizes = set(re.findall(r"[a-z]+\d*|\d+(?:\.\d+)?", (size or "").casefold()))
    ranked = []

    for position, listing in enumerate(load_listings()):
        if max_price is not None and listing["price"] > max_price:
            continue

        if requested_sizes:
            listing_sizes = set(
                re.findall(r"[a-z]+\d*|\d+(?:\.\d+)?", listing["size"].casefold())
            )
            if not requested_sizes.issubset(listing_sizes):
                continue

        searchable = " ".join(
            [
                listing.get("title", ""),
                listing.get("description", ""),
                listing.get("category", ""),
                " ".join(listing.get("style_tags", [])),
            ]
        )
        listing_keywords = set(re.findall(r"[a-z0-9]+", searchable.casefold()))
        score = len(keywords & listing_keywords)
        if score:
            ranked.append((score, position, listing))

    ranked.sort(key=lambda result: (-result[0], result[1]))
    return [
        listing
        for _, _, listing in ranked[: config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    wardrobe_items = wardrobe.get("items") or []
    item_details = json.dumps(new_item, ensure_ascii=False, indent=2)

    if wardrobe_items:
        prompt = (
            f"The user is considering this secondhand item:\n{item_details}\n\n"
            "Their wardrobe contains these items:\n"
            f"{json.dumps(wardrobe_items, ensure_ascii=False, indent=2)}\n\n"
            "Suggest one or two practical outfits using the new item and pieces "
            "from their wardrobe. Name the owned pieces you use."
        )
    else:
        prompt = (
            f"The user is considering this secondhand item:\n{item_details}\n\n"
            "The user has no wardrobe items saved. Give one or two general "
            "styling ideas for this item using common clothing or accessories. "
            "Do not claim the user owns any particular pieces."
        )

    response = generate(
        prompt,
        system="Give specific, useful outfit advice. Keep the response concise.",
    )
    return response.strip() or "Try styling this piece with simple layers and accessories."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    title = new_item.get("title", "this find")
    if not outfit.strip():
        return f"Add an outfit suggestion before creating a fit card for {title}."

    price = new_item.get("price", "an unknown price")
    platform = new_item.get("platform", "the resale platform")
    prompt = (
        "Write a natural social-media fit-card caption in two to four sentences. "
        "Mention the listing title, its exact price, and its platform once each. "
        "Make it specific to the item's vibe, not a product listing. Do not "
        "invent details.\n\n"
        f"Listing:\n{json.dumps(new_item, ensure_ascii=False, indent=2)}\n\n"
        f"Outfit suggestion:\n{outfit.strip()}\n\n"
        f"Required listing title: {title}\n"
        f"Required price: ${price}\n"
        f"Required platform: {platform}"
    )
    response = generate(
        prompt,
        system="Write concise, varied captions grounded only in the supplied details.",
    )
    return response.strip() or f"{title} for ${price} from {platform}, styled your way."
