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
    session["parsed"] = _parse_query(query)

    # Each pass runs one step, writes its result into the session, and picks the
    # next step from what the session now holds.
    trace.step("parse query", inputs=query, returned=session["parsed"])

    next_step = "search"
    count = 0
    try:
        while next_step != "done":
            count += 1
            trace.check_iterations(count)

            if next_step == "search":
                parsed = session["parsed"]
                session["search_results"] = call_tool("search_listings", {
                    "description": parsed["description"],
                    "size": parsed["size"],
                    "max_price": parsed["max_price"],
                })
                trace.step(
                    "search_listings (via MCP)",
                    inputs=parsed,
                    returned=session["search_results"],
                )

                # THE BRANCH: nothing came back, so stop. suggest_outfit is
                # never called with nothing.
                if not session["search_results"]:
                    session["error"] = _no_results_message(parsed)
                    trace.step("branch", note="search returned [] — stopping, suggest_outfit not called")
                    return session

                session["selected_item"] = session["search_results"][0]
                trace.step("select item", returned=session["selected_item"],
                           note="first result goes into session['selected_item']")
                next_step = "suggest"

            elif next_step == "suggest":
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"], session["wardrobe"]
                )
                trace.step(
                    "suggest_outfit",
                    inputs=(
                        f"item id={session['selected_item']['id']} "
                        f"({session['selected_item']['title']}), "
                        f"wardrobe items={len(session['wardrobe'].get('items', []))}"
                    ),
                    returned=session["outfit_suggestion"],
                )
                next_step = "card"

            elif next_step == "card":
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"], session["selected_item"]
                )
                trace.step(
                    "create_fit_card",
                    inputs=(
                        f"item id={session['selected_item']['id']} "
                        f"({session['selected_item']['title']})"
                    ),
                    returned=session["fit_card"],
                )
                next_step = "done"
    except ModelUnavailable as exc:
        session["error"] = (
            f"The model couldn't be reached while running {next_step!r}, so no "
            f"{'outfit or fit card' if next_step == 'suggest' else 'fit card'} "
            f"was made. {exc} Fix the key, then run the same query again."
        )
        trace.step("model unavailable", note=f"stopped at {next_step!r}")

    return session


# ── helpers ───────────────────────────────────────────────────────────────────

# Words that describe the request rather than the item. Left in, they would
# score matches against listings that merely contain "a" or "looking".
_FILLER = {
    "a", "an", "the", "i", "im", "me", "my", "want", "need", "looking", "look",
    "for", "find", "show", "get", "some", "something", "in", "under", "below",
    "over", "max", "maximum", "less", "than", "up", "to", "size", "and", "or",
    "please", "with", "of",
    # money words ("under 50 dollars") and the fragments left when an
    # apostrophe splits a word ("I'd" -> "i", "d"; "don't" -> "don", "t")
    "dollar", "dollars", "bucks", "usd", "d", "s", "ll", "m", "ve", "re", "t",
}

# "size small" / "size large" -> the labels the listings actually use.
_SIZE_WORDS = {
    "small": "S", "medium": "M", "large": "L",
    "extra small": "XS", "extra large": "XL",
}


def _parse_query(query: str) -> dict:
    """
    Pull description, size and max_price out of a plain-language query.

    Uses regex and word filtering, no model call:
      - price: a "$30" / "$30.50" amount, or "under/below/max/up to 30"
      - size:  the word after "size" ("size M", "size XXS"); spelled-out sizes
               ("size small") map to S/M/L/XL, since listings use labels
               (the mapping only applies after the word "size", because
               "medium wash" is a denim colour, not a size)
      - description: what is left, minus the price and size phrases and filler
    """
    text = query

    max_price = None
    price_match = re.search(r"\$\s*(\d+(?:\.\d+)?)", text) or re.search(
        r"\b(?:under|below|max|maximum|up to|less than)\s+(\d+(?:\.\d+)?)", text, re.I
    )
    if price_match:
        max_price = float(price_match.group(1))
        text = text.replace(price_match.group(0), " ")

    size = None
    size_match = re.search(
        r"\bsize\s+(extra\s+(?:small|large)|[A-Za-z0-9]+)", text, re.I
    )
    if size_match:
        said = " ".join(size_match.group(1).lower().split())
        size = _SIZE_WORDS.get(said, said.upper())
        text = text.replace(size_match.group(0), " ")

    # "t-shirt" would otherwise split into "t" and "shirt"; listings say "tee".
    text = re.sub(r"\bt[-\s]?shirts?\b", "tee", text, flags=re.I)

    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    description = " ".join(w for w in words if w not in _FILLER)

    return {"description": description, "size": size, "max_price": max_price}


def _no_results_message(parsed: dict) -> str:
    """Say what was searched and what the user could change."""
    tried = [f"'{parsed['description']}'"]
    changes = ["use fewer or different keywords"]
    if parsed["size"] is not None:
        tried.append(f"size {parsed['size']}")
        changes.append("drop or change the size")
    if parsed["max_price"] is not None:
        tried.append(f"under ${parsed['max_price']:g}")
        changes.append("raise the price limit")
    return (
        f"Nothing matched {', '.join(tried)}. Try to "
        f"{', or '.join(changes)}."
    )


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
