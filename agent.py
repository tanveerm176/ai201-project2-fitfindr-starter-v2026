"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

     The query is parsed with regular expressions. Tool inputs and outputs pass
     through session fields so each stage is visible and testable.

    Each tool call is traced, and model failures are returned as actionable
    session errors rather than uncaught exceptions.
    """
    session = new_session(query, wardrobe)
    price_match = re.search(
        r"\b(?:under|below|up\s+to|at\s+most|max(?:imum)?(?:\s+price)?)\s*\$?\s*(\d+(?:\.\d+)?)\b",
        session["query"],
        re.IGNORECASE,
    )
    size_match = re.search(
        r"\bsize\s+([a-z]+\d*(?:/[a-z]+\d*)?|\d+(?:\.\d+)?)\b",
        session["query"],
        re.IGNORECASE,
    )

    modifiers = [match.span() for match in (price_match, size_match) if match]
    description = session["query"]
    for start, end in sorted(modifiers, reverse=True):
        description = description[:start] + " " + description[end:]
    description = re.sub(r"\s+", " ", description).strip(" ,.;")

    session["parsed"] = {
        "description": description,
        "size": size_match.group(1) if size_match else None,
        "max_price": float(price_match.group(1)) if price_match else None,
    }

    trace.check_iterations(1)
    search_inputs = session["parsed"]
    session["search_results"] = call_tool("search_listings", {
        "description": search_inputs["description"],
        "size": search_inputs["size"],
        "max_price": search_inputs["max_price"],
    })
    trace.step(
        "search_listings (via MCP)",
        inputs=(
            f"description={search_inputs['description']!r}, "
            f"size={search_inputs['size']!r}, "
            f"max_price={search_inputs['max_price']!r}"
        ),
        returned=session["search_results"],
    )
    if not session["search_results"]:
        session["error"] = (
            "No listings matched those filters. Try a different description, "
            "size, or higher price limit."
        )
        return session

    session["selected_item"] = session["search_results"][0]

    trace.check_iterations(2)
    try:
        session["outfit_suggestion"] = suggest_outfit(
            session["selected_item"], session["wardrobe"]
        )
    except ModelUnavailable as exc:
        session["error"] = (
            "The model couldn't be reached to generate outfit advice. "
            "Check your internet connection and GEMINI_API_KEY, then try again. "
            f"Details: {exc}"
        )
        trace.step(
            "suggest_outfit",
            inputs=(
                f"new_item_id={session['selected_item'].get('id')!r}, "
                f"new_item_title={session['selected_item'].get('title')!r}, "
                f"wardrobe_items={len(session['wardrobe'].get('items') or [])}"
            ),
            returned=session["error"],
        )
        return session
    trace.step(
        "suggest_outfit",
        inputs=(
            f"new_item_id={session['selected_item'].get('id')!r}, "
            f"new_item_title={session['selected_item'].get('title')!r}, "
            f"wardrobe_items={len(session['wardrobe'].get('items') or [])}"
        ),
        returned=session["outfit_suggestion"],
    )

    trace.check_iterations(3)
    try:
        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"], session["selected_item"]
        )
    except ModelUnavailable as exc:
        session["error"] = (
            "The model couldn't be reached to create the fit-card caption. "
            "Check your internet connection and GEMINI_API_KEY, then try again. "
            f"Details: {exc}"
        )
        trace.step(
            "create_fit_card",
            inputs=(
                f"outfit={session['outfit_suggestion']!r}, "
                f"new_item={session['selected_item'].get('title')!r}"
            ),
            returned=session["error"],
        )
        return session
    trace.step(
        "create_fit_card",
        inputs=(
            f"outfit={session['outfit_suggestion']!r}, "
            f"new_item={session['selected_item'].get('title')!r}"
        ),
        returned=session["fit_card"],
    )
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
