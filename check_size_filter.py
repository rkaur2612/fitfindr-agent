"""
Criterion 5: the size-match rule avoids false substring matches.

    python check_size_filter.py

Runs search_listings with five size queries — "M", "L", "S", "XL", "W28" — and
checks that every returned listing really has that size as a whole token. The
five cases are the five "tries" for criterion 5 in the run log.

It calls tools.search_listings directly, not over MCP: the size rule is plain
filtering code, and MCP only changes how the call travels. The result cap is
lifted so a false positive can't hide past the first ten results.

The description is every word in the listings' titles and tags, so the keyword
score can't be what excludes a listing — only the size filter can.
"""

import re

import config
from tools import search_listings, _size_tokens
from utils.data_loader import load_listings

SIZES = ["M", "L", "S", "XL", "W28"]


def main() -> None:
    listings = load_listings()
    config.SEARCH_RESULT_LIMIT = 10_000

    words = set()
    for listing in listings:
        words |= set(re.findall(r"[a-z0-9]+", " ".join(
            [listing["title"], listing["description"], *listing["style_tags"]]).lower()))
    description = " ".join(sorted(words))

    passes = 0
    for size in SIZES:
        results = search_listings(description, size=size)
        wrong = [r for r in results if size.upper() not in _size_tokens(r["size"])]

        # Would a plain substring test have let something extra through? If not,
        # this case couldn't have caught the bug it exists to catch.
        substring_only = [
            l for l in listings
            if size.lower() in l["size"].lower() and size.upper() not in _size_tokens(l["size"])
        ]
        sizes_returned = sorted({r["size"] for r in results})
        ok = not wrong
        passes += ok
        print(f"size {size!r}: {'PASS' if ok else 'FAIL'} — "
              f"{len(results)} returned, sizes {sizes_returned}")
        if wrong:
            print(f"    false positives: {[(r['id'], r['size']) for r in wrong]}")
        print(f"    a substring test would also have matched: "
              f"{sorted({l['size'] for l in substring_only}) or 'nothing extra'}")

    print(f"\n{passes} of {len(SIZES)} cases passed")


if __name__ == "__main__":
    main()
