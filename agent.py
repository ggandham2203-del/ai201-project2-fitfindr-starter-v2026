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


# ── query parsing ─────────────────────────────────────────────────────────────

_PRICE_RE = re.compile(r"(?:under|below|less than)\s*\$?\s*(\d+(?:\.\d+)?)", re.I)
_SIZE_RE = re.compile(r"\b(?:in\s+)?size\s+([A-Za-z0-9/]+)", re.I)


def parse_query(query: str) -> dict:
    """
    Pull a max_price and a size out of free text with two regexes. Whatever
    text is left after stripping both matched fragments becomes the
    description passed to search_listings.

    "vintage graphic tee under $30, size M" ->
        {"description": "vintage graphic tee ,", "size": "M", "max_price": 30.0}

    (The stray punctuation left behind doesn't matter — search_listings tokenizes
    on non-alphanumeric characters anyway.)
    """
    remaining = query
    max_price = None
    size = None

    price_match = _PRICE_RE.search(remaining)
    if price_match:
        max_price = float(price_match.group(1))
        remaining = remaining[: price_match.start()] + remaining[price_match.end():]

    size_match = _SIZE_RE.search(remaining)
    if size_match:
        size = size_match.group(1)
        remaining = remaining[: size_match.start()] + remaining[size_match.end():]

    description = re.sub(r"\s+", " ", remaining).strip(" ,")

    return {"description": description, "size": size, "max_price": max_price}


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

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    count = 0

    # 1. Parse the query into description / size / max_price.
    count += 1
    trace.check_iterations(count)
    parsed = parse_query(query)
    session["parsed"] = parsed
    trace.step("parse_query", inputs={"query": query}, returned=parsed)

    # 2. Search, via MCP. THIS IS THE BRANCH.
    count += 1
    trace.check_iterations(count)
    search_inputs = {
        "description": parsed["description"],
        "size": parsed["size"],
        "max_price": parsed["max_price"],
    }
    results = call_tool("search_listings", search_inputs)
    session["search_results"] = results

    if not results:
        suggestions = ["using different keywords"]
        if parsed["max_price"] is not None:
            suggestions.append("raising the price ceiling")
        if parsed["size"]:
            suggestions.append("trying a different size")

        price_note = f" under ${parsed['max_price']:.0f}" if parsed["max_price"] is not None else ""
        size_note = f" in size {parsed['size']}" if parsed["size"] else ""

        session["error"] = (
            f"No listings matched \"{parsed['description']}\"{price_note}{size_note}. "
            f"Try {', or '.join(suggestions)}."
        )
        trace.step(
            "search_listings (via MCP)",
            inputs=search_inputs,
            returned=results,
            note="branch: empty, stopping before suggest_outfit",
        )
        return session

    trace.step(
        "search_listings (via MCP)",
        inputs=search_inputs,
        returned=results,
        note="branch: results found, continuing to suggest_outfit",
    )

    # 3. Pick the best-scoring result and hand it to suggest_outfit.
    session["selected_item"] = results[0]

    count += 1
    trace.check_iterations(count)
    outfit_inputs = {
        "new_item": session["selected_item"].get("title"),
        "wardrobe_items": len(wardrobe.get("items") or []),
    }
    try:
        session["outfit_suggestion"] = suggest_outfit(session["selected_item"], wardrobe)
    except ModelUnavailable as exc:
        session["error"] = f"Couldn't reach the styling model to suggest an outfit: {exc}"
        trace.step(
            "suggest_outfit",
            inputs=outfit_inputs,
            returned=None,
            note="branch: model unavailable, stopping before create_fit_card",
        )
        return session

    trace.step("suggest_outfit", inputs=outfit_inputs, returned=session["outfit_suggestion"])

    # 4. Turn the outfit + item into a caption.
    count += 1
    trace.check_iterations(count)
    card_inputs = {
        "outfit": session["outfit_suggestion"],
        "new_item": session["selected_item"].get("title"),
    }
    try:
        session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])
    except ModelUnavailable as exc:
        session["error"] = f"Couldn't reach the captioning model to write a fit card: {exc}"
        trace.step(
            "create_fit_card",
            inputs=card_inputs,
            returned=None,
            note="branch: model unavailable, stopping",
        )
        return session

    trace.step("create_fit_card", inputs=card_inputs, returned=session["fit_card"])

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
