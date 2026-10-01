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

A user describes what they're looking for in plain language — e.g. "vintage graphic tee under $30,
size M" — and FitFindr searches the listings data, picks the best match, and figures out what it would
go with. It returns the matching item (title, price, platform), one or two outfit ideas built from the
user's own wardrobe (or general styling advice if they haven't saved one), and a short caption they
could actually post about the find. If nothing in the data matches what they asked for, it says so
instead of guessing, and tells them what to change — a wider price range, a different size, or
different keywords.



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

- **What it does:** Searches `data/listings.json` for items whose title, description, and style tags overlap with the query's keywords, optionally narrowed by size and a price ceiling.
- **Inputs:** `description` (str) — free-text keywords, e.g. `"vintage graphic tee"`. `size` (str | None) — a size token to match against a listing's `size` field, case-insensitively; `None` skips size filtering. `max_price` (float | None) — highest acceptable price, inclusive; `None` skips the price filter.
- **Returns:** `list[dict]` — matching listing dicts (`id, title, description, category, style_tags, size, condition, price, colors, brand, platform`), sorted best keyword match first, capped at `config.SEARCH_RESULT_LIMIT`.
- **When it has nothing:** returns `[]` — an empty list, never `None`, never an exception. This is what the loop branches on.

**Size matching note:** listing sizes are inconsistent strings (`"W30 L30"`, `"S/M"`, `"XL (oversized)"`, plain numbers for shoes). A plain substring check is wrong — `"s" in "us 9"` and `"l" in "xl"` are both `True`. The rule: split both the listing's size and the query's size into tokens on non-alphanumeric characters (spaces, `/`, parentheses), lowercase them, and match if the query's token set intersects the listing's token set. `"S/M"` → `{"s","m"}`; a query size of `"M"` → `{"m"}` → match. `"XL (oversized)"` → `{"xl","oversized"}`; a query size of `"L"` → `{"l"}` → no match.

### `suggest_outfit`

- **What it does:** Calls the model to propose one or two outfit combinations pairing the newly found item with pieces from the user's wardrobe.
- **Inputs:** `new_item` (dict) — a listing dict, as returned by `search_listings`. `wardrobe` (dict) — a wardrobe dict with an `'items'` key holding a list of wardrobe item dicts; the list may be empty.
- **Returns:** `str` — a non-empty string of outfit suggestions in natural language.
- **When it has nothing:** if `wardrobe['items']` is empty, returns general styling advice for the item (still a non-empty string) instead of failing or returning `""`.

### `create_fit_card`

- **What it does:** Writes a short, postable caption (2–4 sentences) for the item, built from the outfit suggestion.
- **Inputs:** `outfit` (str) — the string returned by `suggest_outfit`. `new_item` (dict) — the listing dict for the item.
- **Returns:** `str` — a 2–4 sentence caption that mentions the item, its price, and its platform once each, and is specific about the vibe.
- **When it has nothing:** if `outfit` is empty or whitespace-only, returns a fixed fallback string (e.g. `"Couldn't write a caption — no outfit suggestion to build one from."`) rather than raising or returning `""`.

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

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what the user could change (loosen the price ceiling, drop the size filter, or try different keywords) and return the session — do not call `suggest_outfit` or `create_fit_card`. Otherwise, take the first (best-scoring) result as `session["selected_item"]` and continue on to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex. One pattern pulls a price ceiling out of phrases like `"under $30"` or `"below $45"` into `max_price`. A second pulls a size out of phrases like `"size M"` or `"size 8"` into `size`. Whatever text remains after stripping both matched fragments becomes `description`.

**What moves through the session:** `query` → `parsed` (`description`, `size`, `max_price`) → `search_results` → `selected_item` → (`selected_item` + `wardrobe`) → `outfit_suggestion` → (`outfit_suggestion` + `selected_item`) → `fit_card`. `error` is only set on the early-stop path, in which case `outfit_suggestion` and `fit_card` stay `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear Edge**
Pair the Y2K butterfly baby tee with your baggy straight-leg dark wash jeans and chunky white sneakers
for a classic noughties silhouette. Layer your black cropped zip hoodie overtop unzipped to tie the
streetwear aesthetic together.

**Outfit 2: Casual Contrast**
Combine the fitted baby tee with your wide-leg khaki trousers and brown leather belt for an effortless
mix of earth tones and playful Y2K style. Finish the look with your black combat boots to add a touch
of grunge contrast to the sweet butterfly graphic.

  Fit card: the cutest lil butterfly baby tee to channel your inner 2000s pop star. honestly looks so
good with baggy denim or paired with grunge combat boots for that exact contrast. snag this thrifted
find on depop right now for just $18.0!

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'price': 18.0, 'size': 'S/M', ...},
 {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'price': 24.0, 'size': 'L', ...},
 {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'price': 15.0, 'size': 'S/M', ...},
 {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'price': 19.0, 'size': 'L', ...},
 {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'price': 27.0, 'size': 'W29', ...},
 {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'price': 26.0, 'size': 'L', ...}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
**Outfit 1: Casual Streetwear**
Pair the vintage Levi's 501 jeans with the white ribbed tank top and chunky white sneakers, then layer
on the vintage black denim jacket for a classic, effortless look. Complete the outfit with your black
crossbody bag for easy everyday wear.

**Outfit 2: Cozy & Relaxed**
Tuck the oversized grey crewneck sweatshirt into the medium wash Levi's 501s and secure the waist with
your brown leather belt. Finish off the look by pairing them with black combat boots for a
grunge-inspired contrast.

$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
These vintage Levi's 501s pair effortlessly with casual basics like a crisp white t-shirt, a classic
crewneck sweatshirt, or an oversized flannel. Complement their medium wash and streetwear vibe with
neutral earth tones, black, or heather gray, and finish the look with retro sneakers or leather boots.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Obsessed with the wash on these vintage Levi's 501 jeans — the exact slouchy, broken-in fit we're all
hunting for right now. Throw them on with some beat-up white sneakers and an oversized tee for that
effortless 90s off-duty look. Grab this pair on Depop for just $38 before I change my mind and keep them.

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('', load_listings()[0]))"
Couldn't write a caption — no outfit suggestion to build one from.
```

Note: running `create_fit_card` twice on the identical item + outfit string returned the identical
caption both times — that's `CACHE_ENABLED` reusing the first answer while building (documented
behavior), not a sign `TEMPERATURE` isn't working. Real variation across 5 tries gets checked in unit 4
with the cache off via `run_eval.py`.

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Help specifying and building `search_listings`' size filter.
- *What came back:* Claude pointed out that a plain substring check would misfire on this data —
  `"L"` would match inside `"XL"`, and `"S"` would match inside a shoe size like `"US 9"` if the digits
  ever lined up — something I hadn't caught from skimming the listings.
- *What I changed:* I had it implement size matching by tokenizing both the query size and the
  listing's size on non-alphanumeric characters and comparing token sets, instead of a substring check —
  confirmed by testing that a `size="M"` query excludes a `"XL (oversized)"` listing.

**Moment 2**

- *What I asked for:* To test `create_fit_card` by running it twice on the same item and outfit.
- *What came back:* Both runs returned a word-for-word identical caption, which looked like
  `TEMPERATURE` wasn't doing anything. Claude traced it to `CACHE_ENABLED` instead — `generate()`
  reuses the cached response for an identical prompt while building, which is documented behavior in
  `generate.py`, not a broken temperature setting.
- *What I changed:* I didn't change the code — I added a note in the Sample Run section explaining the
  identical output so it doesn't get misread later, and left the real variability check for unit 4's
  `run_eval.py`, which turns the cache off.

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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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

```

**Empty search**

```

```

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
