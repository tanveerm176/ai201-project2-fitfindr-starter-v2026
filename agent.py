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

# from mcp_client import call_tool

# # was: results = search_listings(parsed["description"], parsed["size"], parsed["max_price"])
# results = call_tool("search_listings", {
#     "description": parsed["description"],
#     "size": parsed["size"],
#     "max_price": parsed["max_price"],
# })

# session["parsed"] = parsed
# trace.step("parse_query", inputs=query, returned=str(parsed))

# session["search_results"] = results
# trace.step("search_listings (via MCP)", inputs=str(parsed), returned=results, note=f"{len(results)} match(es)")

# if not results:
#     session["error"] = _nothing_found_message(parsed)
#     trace.step("branch", note="search returned []: stopping before suggest_outfit")
#     return session

# session["selected_item"] = results[0]
# trace.step("select_item", returned=session["selected_item"])

# # after suggest_outfit(...)
# trace.step("suggest_outfit", inputs=session["selected_item"],
#            returned=session["outfit_suggestion"])

# # after create_fit_card(...)
# trace.step("create_fit_card", inputs=session["selected_item"],
#            returned=session["fit_card"])

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

    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
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
    session["search_results"] = call_tool("search_listings", {
        "description": session["parsed"]["description"],
        "size": session["parsed"]["size"],
        "max_price": session["parsed"]["max_price"],
    })
    if not session["search_results"]:
        session["error"] = (
            "No listings matched those filters. Try a different description, "
            "size, or higher price limit."
        )
        return session

    session["selected_item"] = session["search_results"][0]

    trace.check_iterations(2)
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )

    trace.check_iterations(3)
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
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
