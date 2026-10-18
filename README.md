# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

A user describes a secondhand piece in plain language, such as "a vintage graphic tee under $30, size M". FitFindr pulls the description, size and price ceiling out of the query and searches the listings data. It then picks the best match and suggests one or two outfits that pair it with pieces from the user's wardrobe, or general styling advice if the wardrobe is empty. Finally it writes a short social-media-style caption for the find. If nothing matches, it stops early and says what to change instead of going on with nothing.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings data for items matching a description, and optionally filters by size and a maximum price.
- **Inputs:** `description` (str) — keywords describing what the user wants; `size` (str, optional) — a size to filter by, or `None` to skip size filtering; `max_price` (float, optional) — maximum price, inclusive, or `None` to skip price filtering.
- **Returns:** A list of full listing dicts (`id, title, description, category, style_tags, size, condition, price, colors, brand, platform`), sorted best match first by keyword overlap with `description`, capped at `config.SEARCH_RESULT_LIMIT`.
- **When it has nothing:** An empty list — not `None`, not an exception.
- **Size-match rule:** A listing's `size` field is split into whole tokens on spaces, slashes, and parentheses (e.g. `"S/M"` → `["S", "M"]`, `"XL (oversized)"` → `["XL", "oversized"]`). The query `size` is matched case-insensitively against these whole tokens — not as a substring. This means `"M"` matches `"S/M"`, but `"L"` does **not** match `"XL"`.

### `suggest_outfit`

- **What it does:** Given a thrifted item and the user's wardrobe, suggests one or two outfit combinations.
- **Inputs:** `new_item` (dict) — a listing dict (the item the user is considering, e.g. from `search_listings`, with fields like `title, price, platform, category, colors, style_tags`); `wardrobe` (dict) — a dict with key `"items"` holding a list of wardrobe item dicts, each with `id, name, category, colors, style_tags, notes`.
- **Returns:** A non-empty string suggesting one or two outfits, naming specific wardrobe items by name (e.g. "black cropped zip hoodie") when the wardrobe is non-empty.
- **When it has nothing:** If `wardrobe["items"]` is empty, returns general styling advice for the new item and acknowledges that no wardrobe was given — rather than raising an error or returning `""`.

### `create_fit_card`

- **What it does:** Writes a short caption someone would actually post about the find.
- **Inputs:** `outfit` (str) — the outfit suggestion string from `suggest_outfit()`; `new_item` (dict) — the listing dict for the item.
- **Returns:** A two-to-four sentence caption, mentioning the item, its price, and its platform once each, written in a casual, post-like voice that's specific about the vibe.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns a descriptive message rather than raising an exception.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, store a message in the session naming what the user could change (e.g. raise `max_price`, loosen `size`, or rephrase `description`) and stop — `suggest_outfit` and `create_fit_card` are never called. Otherwise, take the first result from the list, store it in the session as `selected_item`, and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex and word filtering — no model call (`agent.py::_parse_query`). A `$30` amount (or "under/below/max/up to 30") becomes `max_price`; the word after "size" becomes `size`, uppercased; the description is what remains after removing those phrases and filler words like "looking for a". The result is stored in `session["parsed"]`.

**What moves through the session:** In order: `query` → `parsed` → `search_results` → `selected_item` (the first result) → `outfit_suggestion` → `fit_card`. Each step writes its result to the session, and the next step reads its input back out of the session rather than from a local variable. On an empty search, `error` is set to a message naming the search and what to change, and `outfit_suggestion` and `fit_card` stay `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here is a Y2K-inspired outfit using your new butterfly baby tee and pieces from your wardrobe:

**The Outfit: Sweet & Edgy Y2K Streetwear**
*   **Top:** Y2K Baby Tee — Butterfly Print 
*   **Bottoms:** Baggy straight-leg jeans, dark wash
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag

**Why it works:** 
The fitted silhouette of the butterfly baby tee creates a great contrast against the relaxed, slouchy fit of the baggy dark wash jeans—a signature Y2K proportion play. Tossing on the vintage black denim jacket keeps the color palette grounded while leaning into that early-2000s grunge-meets-girly vibe. Finish the look with the chunky white sneakers to tie in the white from the tee, and sling the black crossbody bag over your shoulder for effortless everyday wear.

  Fit card: finally scored this little butterfly print Y2K baby tee on depop for just $18! honestly obsessed with the early 2000s grunge-meets-girly vibe. throwing it on with baggy jeans and chunky sneakers for the ultimate casual street fit. ✨🦋

0 model calls this session, 2 served from cache
```

And a query that matches nothing, which stops before `suggest_outfit`:

```
$ python agent.py     (second example)
  stopped: Nothing matched 'designer ballgown', size XXS, under $5. Try to use fewer or different keywords, or drop or change the size, or raise the price limit.
  fit_card is None — it should still be None here
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]

$ python -c "from tools import search_listings; print(search_listings('zzzxqy'))"
[]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here are two ways to style your new vintage Levi's 501 jeans using pieces already in your wardrobe:

### Outfit 1: Casual Streetwear Layering
* **Bottoms:** Vintage Levi's 501 Jeans — Medium Wash
* **Tops:** White ribbed tank top
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

**Why it works:** The white ribbed tank keeps the look fresh and simple against the medium wash of the 501s, while throwing the vintage black denim jacket on top gives you a cool, textured double-denim moment. Finish it off with the chunky white sneakers and the black crossbody bag for an effortless, streetwear-ready vibe.

---

### Outfit 2: Cozy & Edgy Contrast
* **Bottoms:** Vintage Levi's 501 Jeans — Medium Wash
* **Tops:** Oversized grey crewneck sweatshirt
* **Accessories:** Brown leather belt, Black crossbody bag
* **Shoes:** Black combat boots

**Why it works:** Tucking the oversized grey crewneck casually into the medium wash 501s creates a great relaxed silhouette. Cinching it with the brown leather belt adds a nice detail, and grounding the outfit with black combat boots gives the vintage denim a tougher, grounded edge.

$ python -c "from tools import suggest_outfit; from utils.data_loader import load_listings; print(suggest_outfit(load_listings()[0], {'items': []}))"
Since I don't know what's in your closet yet, here are two foolproof ways to style those vintage 501s:

1. **The Casual Streetwear Look:** Pair them with an oversized graphic tee (tucked in or half-tucked), a vintage leather jacket or bomber, and a pair of retro sneakers like Nike Dunks or Sambas.
2. **The Classic High-Low Look:** Dress them down-to-earth by adding a crisp, slightly oversized white button-down shirt (sleeves rolled up), a simple leather belt, and classic loafers or chunky boots.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Found these vintage Levi's 501s on Depop for just $38 and I am literally never taking them off. The medium wash is *so* perfectly broken in and gives off major effortless off-duty model energy. Just gonna live in these with my favorite white sneakers from now on.

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('  ', load_listings()[0]))"
No outfit suggestion was available, so no fit card could be written.
```

**`create_fit_card` run three times on the same item**

With the default config (`CACHE_ENABLED` on, `TEMPERATURE = 0.9`), all three runs were word-for-word identical:

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"   (x3)
Found these vintage Levi's 501s on Depop for just $38 and I am literally never taking them off. The medium wash is *so* perfectly broken in and gives off major effortless off-duty model energy. Just gonna live in these with my favorite white sneakers from now on.
Found these vintage Levi's 501s on Depop for just $38 and I am literally never taking them off. The medium wash is *so* perfectly broken in and gives off major effortless off-duty model energy. Just gonna live in these with my favorite white sneakers from now on.
Found these vintage Levi's 501s on Depop for just $38 and I am literally never taking them off. The medium wash is *so* perfectly broken in and gives off major effortless off-duty model energy. Just gonna live in these with my favorite white sneakers from now on.
```

Temperature was already 0.9, so the cause was the cache. With the cache turned off (`AI201_CACHE=0`), the same three runs came out different:

```
$ AI201_CACHE=0 python -c "...create_fit_card('jeans and white sneakers', load_listings()[0])..."   (x3)
Finally scored the holy grail of denim: these vintage Levi's 501s in the absolute best medium wash. Throwing them on with some fresh white sneakers for that effortlessly cool 90s off-duty model vibe. Grabbed them on depop for just $38 and I honestly might never take them off.
Nothing beats the fit of broken-in vintage denim, especially when you find the dream wash like these Levi's 501s. Pair them with fresh white sneakers for that effortlessly cool, off-duty model vibe. Snagged this pair on Depop for just $38—absolute steal.
Found the holy grail of denim today on depop—these vintage Levi's 501s in the absolute dreamiest medium wash. For just $38, they’ve got that perfectly worn-in 90s slouch that brand-new jeans could never fake. Just add a simple white tee and fresh sneakers and you’ve got the ultimate lazy-girl chic uniform.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Claude to review my finished `tools.py` before I tested it.
- *What came back:* It said `search_listings` counts every word of the description toward the score, so filler like "a", "under" or "looking" would match listings that merely contain those words and push weak results up. It also said it could not confirm the wardrobe item keys (`name`, `category`) that `suggest_outfit` reads until the tool was run.
- *What I changed:* I added filler-word removal to the query parser, `agent.py::_parse_query`, so the description handed to `search_listings` is just the item words (for example "vintage graphic tee"). I ran `suggest_outfit` against the example wardrobe and it named real wardrobe pieces, so the keys were correct.

**Moment 2**

- *What I asked for:* I asked Claude to run `create_fit_card` three times on the same item, as Milestone 4 requires.
- *What came back:* All three captions were word-for-word identical. `TEMPERATURE` was already 0.9, so Claude pointed to `CACHE_ENABLED`, which defaults to on. It then re-ran with `AI201_CACHE=0`, and the three captions came out different.
- *What I changed:* I left the cache on in `config.py`, because it makes debugging free, and recorded both sets of runs under Sample Run. Criterion 4 is the check that catches this: it only means something with the cache off, which is how `run_eval.py` runs.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item in session matches item passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card not identical across runs | 3 of 3 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Size match has no false substring hits | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Produced by `run_eval.py --label before` (cache off, temperature 0.9, 40 model
calls, no crashes). Full log: `results/run_2026-10-18_1311_before.md`. Criterion 5
comes from `check_size_filter.py`, where the five tries are the five sizes `M`,
`L`, `S`, `XL`, `W28`, not five identical runs.

What counted as a PASS for each row:

1. The run ended with no error, `search_results` non-empty, and a non-empty fit card. All five also mentioned the price and the platform.
2. The run stopped with `session["error"]` naming the search and what to change, `suggest_outfit` never appears in the trace, and `fit_card` is empty.
3. The `id` of `session["selected_item"]` is the same `id` printed on the `suggest_outfit` trace line (`lst_007` in all five).
4. Try N is a PASS if its fit card is not word-for-word identical to any other card for the same item. All five cards for `lst_002` are different.
5. Every listing returned for that size has the size as a whole token (`check_size_filter.py`).

**Real output from one try per criterion**, pasted as text.

*Criterion 1 — `agent.py::run_agent` via `run_eval.py`, try 1, `vintage graphic tee under $30`:*

```
[1] parse query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    first result goes into session['selected_item']
[4] suggest_outfit
      in:  item id=lst_002 (Y2K Baby Tee — Butterfly Print), wardrobe items=10
      out: Here are two outfit ideas using your new butterfly Y2K baby tee and pieces straight from your wardrobe:  **Out…
[5] create_fit_card
      in:  item id=lst_002 (Y2K Baby Tee — Butterfly Print)
      out: Found this adorable butterfly baby tee on depop for just $18 and I’m literally obsessed. It gives major early …
```

*Criterion 2 — `agent.py::run_agent`, try 1, `designer ballgown size XXS under $5`:*

```
- stopped early: yes — Nothing matched 'designer ballgown', size XXS, under $5. Try to use fewer or different keywords, or drop or change the size, or raise the price limit.
- selected_item: (none)
- search_results: 0
[1] parse query
[2] search_listings (via MCP)
      out: [] (empty)
[3] branch
      →    search returned [] — stopping, suggest_outfit not called
```

*Criterion 3 — `agent.py::run_agent`, try 1, `denim jacket under $50`:*

```
[3] select item
      out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
[4] suggest_outfit
      in:  item id=lst_007 (Denim Jacket — Light Wash, Cropped), wardrobe items=10
[5] create_fit_card
      in:  item id=lst_007 (Denim Jacket — Light Wash, Cropped)
```

*Criterion 4 — `tools.py::create_fit_card`, the five fit cards for `lst_002` (tries 1–5):*

```
1 Found the ultimate Y2K butterfly baby tee on depop for just $18 and I am never taking it off. Gives major early 2000s pop princess energy, especially paired with low-rise denim. Grab it before I change my mind! 🦋✨
2 Found the ultimate butterfly baby tee on depop for just $18 and I am obsessed. The Y2K nostalgia is so real with this one—it gives major early 2000s mall rat energy. Can't wait to style it with baggy denim and combat boots all fall. 🦋✨
3 Found this absolute dream of a Y2K butterfly print baby tee on Depop for just $18 and I’m never taking it off. Pairing it with baggy dark wash denim and a black jacket gives me the exact sweet-yet-edgy vibe I've been looking for. So obsessed with how this turned out! 🦋✨
4 scored this butterfly print baby tee on depop for just $18 and I’m literally obsessed. throwing it on with some baggy dark denim and chunky sneakers for the ultimate Y2K streetwear look. so ready to live out my early 2000s pop star dreams in this.
5 scored this literal dream y2k butterfly baby tee on depop for just $18 and i am obsessed 🦋 pairing it with baggy jeans and chunky sneakers for max 2000s energy. so ready to live out my inner pop star era in this!
```

*Criterion 5 — `check_size_filter.py` (calls `tools.py::search_listings`):*

```
size 'M': PASS — 14 returned, sizes ['M', 'M/L', 'S/M']
    a substring test would also have matched: nothing extra
size 'L': PASS — 8 returned, sizes ['L', 'L/XL', 'M/L']
    a substring test would also have matched: ['One Size (adjustable)', 'W30 L30', 'XL', 'XL (fits oversized)', 'XL (oversized)']
size 'S': PASS — 6 returned, sizes ['S', 'S/M']
    a substring test would also have matched: ['One Size', 'One Size (adjustable)', 'One Size / Oversized', 'US 7', 'US 8', 'US 8.5', 'US 9', 'XL (fits oversized)', 'XL (oversized)']
size 'XL': PASS — 4 returned, sizes ['L/XL', 'XL', 'XL (fits oversized)', 'XL (oversized)']
    a substring test would also have matched: nothing extra
size 'W28': PASS — 2 returned, sizes ['W28']
    a substring test would also have matched: nothing extra

5 of 5 cases passed
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    first result goes into session['selected_item']
[4] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Here is a Y2K-inspired outfit using your new butterfly baby tee and pieces from your wardrobe:  **The Outfit: …
[5] create_fit_card
      in:  dict with keys: item
      out: finally scored this little butterfly print Y2K baby tee on depop for just $18! honestly obsessed with the earl…
```

**Empty search**

```
$ python app.py ask 'purple tuxedo with sequins size XXS under $3' --trace
[1] parse query
      in:  purple tuxedo with sequins size XXS under $3
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      →    search returned [] — stopping, suggest_outfit not called

  Nothing matched 'purple tuxedo sequins', size XXS, under $3. Try to use fewer or different keywords, or drop or change the size, or raise the price limit.
```

**The three failures, triggered on purpose**

```
Empty search     python app.py ask 'purple tuxedo with sequins size XXS under $3'
                 -> Nothing matched 'purple tuxedo sequins', size XXS, under $3. Try to use fewer or different keywords, or drop or change the size, or raise the price limit.

Empty wardrobe   python app.py ask 'vintage graphic tee under $30' --empty-wardrobe
                 -> Outfit: Since I don't know what's in your closet yet, here are two foolproof ways to style that Y2K butterfly tee: ... (general advice, then a fit card)

Model unavailable  GEMINI_API_KEY set to a bad value for one process, new query:
                 python app.py ask 'baggy cargo pants size W29 under $40'
                 Before the handler: "ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com." (exit code 1, no outfit)
                 After the handler (agent.py::run_agent):
                 -> The model couldn't be reached while running 'suggest', so no outfit or fit card was made. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Fix the key, then run the same query again.
```

I triggered the bad key with an environment variable for a single process, so `.env` was never edited. The handler catches `ModelUnavailable` around the whole loop and stores the message in `session["error"]`, leaving `outfit_suggestion` and `fit_card` as `None`.

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
