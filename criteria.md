# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. The selected item's state carries through unchanged

Given a query that matches at least one listing, the `id` of
`session["selected_item"]` equals the `id` of the `new_item` actually passed
into `suggest_outfit` — 5 of 5 tries.

**Why this target:** The state-passing logic is deterministic code, not a
model call — nothing about moving a value through the session should vary
between runs, so a perfect score is the right bar here, unlike criterion 1
which depends on an imperfect keyword search.

---

## 4. The fit card isn't secretly deterministic

Running `create_fit_card` 3 times on the same item produces 3 outputs that are
not word-for-word identical to each other — in 3 of 3 tries.

**Why this target:** The caption calls a model specifically so the wording
varies; word-for-word identical output across all 3 runs would mean caching or
a temperature of 0 is silently making the tool deterministic when it
shouldn't be — this is the simplest check that catches that failure.



---

## 5. The size-match rule avoids false substring matches

Testing `search_listings` with 5 different size queries (`"M"`, `"L"`, `"S"`,
`"XL"`, `"W28"`) against the full listings dataset, the whole-token match
never produces a false positive — specifically, querying size `"L"` never
returns a listing whose size is `"XL (oversized)"`, and querying `"S"` never
returns a listing sized `"W28"` — in 5 of 5 test cases.

**Why this target:** This is deterministic filtering code, not a model call,
so a perfect score is the right bar — same reasoning as criterion 3. The
target specifically guards against the exact substring trap the tool's own
docstring warns about (`"l" in "xl"` being `True`).



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
