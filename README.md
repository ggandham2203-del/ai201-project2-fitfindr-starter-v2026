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

**Moment 3 (unit 4)**

- *What I asked for:* How to build scenarios for criteria 3, 4, and 5, which all require "5 different
  queries" / "5 different items" rather than one query run 5 times like criteria 1 and 2.
- *What came back:* My first instinct (prompted by thinking out loud with Claude) was three separate
  batches of 5 scenarios each — 15 total — one batch per criterion. Claude pointed out that since all
  three criteria's "5 different X" requirement could be satisfied by the *same* 5 queries (as long as
  each query also specified a `max_price`), one batch of 5 could serve all three, and verified this by
  actually running `tools.py::search_listings` directly against my 5 candidate queries and
  `data/listings.json` to confirm each one had one clear, unambiguous top match before I committed to it.
- *What I changed:* `scenarios.py` ended up with 5 "diverse item" scenarios instead of 15, each reused
  for criteria 3, 4, and 5 in the README — roughly a third of the model calls for the same evidence.

**Moment 4 (unit 4)**

- *What I asked for:* To build the After run log for Milestone 5 once the data-normalization fix was in.
- *What came back:* Two of the five "crochet halter top" tries came back with a real `503 UNAVAILABLE`
  from the live model on the `create_fit_card` step — unrelated to the code change, but since I was using
  "Try 1 from each item" as my fixed sampling method, it showed up as a miss on criterion 4 in the After
  table (MET → MISSED). The easy move would have been to quietly re-run until it came back clean.
- *What I changed:* I kept the result as-is and wrote up why the miss happened (a transient service
  error, caught correctly by the `ModelUnavailable` handler) rather than re-rolling for a better-looking
  table — and added it to What's Still Broken as a genuine, newly-found gap: `generate.py`'s retry logic
  doesn't currently retry on `503`, only on rate-limit errors.

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
| 1. Matching query completes all 3 tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. State — `id` passed through unchanged | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card — 2–4 sentences, mentions price | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**How criteria 3, 4, and 5 map onto the scenarios.** Criteria 3, 4, and 5 all
say "5 different queries" / "5 different items," not "the same query 5
times" like criteria 1 and 2. `scenarios.py` has one batch of 5 scenarios
("diverse item 1–5"), each a different distinctive query with a different
`max_price`, that together supply the evidence for all three — rather than
writing three separate 5-query batches (15 scenarios, ~3x the model calls)
for criteria whose "5 different X" requirement is identical in shape. For
the table above, each criterion's 5 "tries" are Try 1 from each of the 5
diverse-item scenarios (`leather bomber`, `silk button-down`, `velvet
blazer`, `crochet halter top`, `suede chelsea boots`) — one try per item,
since what each criterion needs is 5 *different* items, not 5 repeats of
one.

**Real output, pasted as text, naming the file and function that produced
it** (`run_eval.py::run_once`, which calls `agent.py::run_agent`):

**Criterion 1** — `vintage graphic tee under $30`, Try 1 of 5 (all 5 tries
completed identically in structure; see full trace/output above in the
unedited run log):

```
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
Outfit:   Pair the Y2K baby tee with your baggy straight-leg jeans and chunky
white sneakers for an effortless early 2000s streetwear look. Layer the
vintage black denim jacket over top and accessorize with your black
crossbody bag to tie the monochrome details together.
Fit card: Living out my ultimate 2000s pop star fantasy in this butterfly
print baby tee. Snagged this absolute gem on Depop and it's giving major
nostalgia for just $18. Grab it before I change my mind and keep it for
myself!
```

**Criterion 2** — `designer ballgown size XXS under $5`, Try 1 of 5 (all 5
tries identical):

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

No listings matched "designer ballgown" under $5 in size XXS. Try using
different keywords, or raising the price ceiling, or trying a different
size.
```

**Criterion 3** — state hand-off, confirmed with an explicit `id` check
(`agent.py::run_agent`, called directly):

```
$ python -c 'from agent import run_agent; from utils.data_loader import get_example_wardrobe; s = run_agent("leather bomber jacket under $80", get_example_wardrobe()); print("id:", s["selected_item"]["id"]); print("title:", s["selected_item"]["title"])'
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe_items
      out: **Outfit 1:** Pair the 90s Leather Bomber with the white ribbed tank top tucked into the baggy straight-leg je…
id: lst_022
title: 90s Leather Bomber — Black
```

`lst_022` is the real id for "90s Leather Bomber — Black" in
`data/listings.json`. Since `agent.py::run_agent` does
`session["selected_item"] = results[0]` and then immediately calls
`suggest_outfit(session["selected_item"], wardrobe)` — the same dict
object, no intermediate copy or rebuild — the `id` cannot diverge between
the two by construction. Across the 5 diverse-item scenarios, the title
threaded through `selected_item` → the outfit suggestion → the fit card was
correct and consistent every time (e.g. the velvet blazer run names "the
emerald velvet blazer" and "$52" throughout; the crochet top run names "the
cream crochet halter top" and "22.0" throughout) — independent, visible
confirmation that the right item, not a different one, reached every later
step in all 5 tries.

**Criterion 4** — one fit card per item, from each of the 5 diverse-item
scenarios, Try 1:

```
Absolute staple 90s leather bomber in the best worn-in black. Throw it on
over a white ribbed tank and baggy jeans for effortless grunge energy, or
dress it down with khakis and sneakers. Grab this vintage essential for $75
exclusively on Depop before I change my mind!

So obsessed with this vintage sage green silk button-down, but I have too
many similar tops in my rotation. It has the dreamiest minimalist
earth-tone vibe—style it thrown open over a white tank with wide-leg
trousers, or buttoned up with dark denim and boots. Snag it here on Depop
for just $28!

Obsessed with this rich emerald velvet blazer—it's the ultimate
holiday-party-meets-coffee-run statement piece. I'm listing it on Depop for
$52, but honestly, letting this one go hurts! Throw it over a beat-up white
tank and baggy jeans to nail that effortless high-low vibe.

Obsessed with this cream crochet halter top for 22.0 on depop, but my
closet is just drowning in summer boho pieces right now. It looks unreal
layered over a ribbed tank with dark wash denim, or toughened up with black
combat boots and a vintage jacket. Grab it before I change my mind and keep
it for festival season!

These tan suede Chelsea boots add the exact right amount of texture to a
minimalist earth-tone fit or a vintage streetwear look. They're super
versatile and instantly elevate any denim-and-tee combo. Grab them on
Poshmark now for just $44.0 before I change my mind and keep them!
```

Each is non-empty, 3 sentences (within the 2–4 range), and mentions the
item's price exactly once ($75, $28, $52, 22.0, $44.0).

**Criterion 5** — verified directly against `tools.py::search_listings`
(not inferred from the trace, which only prints the first 3 titles):

```
$ python -c "from tools import search_listings; [print(q, mp, [x['price'] for x in search_listings(q, max_price=mp)]) for q, mp in [('leather bomber jacket', 80), ('silk button-down sage green', 35), ('velvet blazer emerald green', 60), ('crochet halter top', 25), ('suede chelsea boots tan', 50)]]"
leather bomber jacket 80 [75.0, 45.0, 42.0, 55.0, 12.0, 33.0, 38.0]
silk button-down sage green 35 [28.0, 30.0, 12.0, 16.0, 18.0, 33.0]
velvet blazer emerald green 60 [52.0, 38.0, 18.0, 28.0]
crochet halter top 25 [22.0, 15.0, 20.0]
suede chelsea boots tan 50 [44.0, 14.0, 38.0]
```

Every price in every list is at or under its ceiling.

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
| 1 | Matching query completes all 3 tools | 4 of 5 | MET (5/5) | Counted PASS/FAIL per try (stopped early = FAIL, else PASS): 5 passes ≥ 4 target. |
| 2 | Impossible query stops before tool 2 | 5 of 5 | MET (5/5) | Checked `session["error"]` was set and `suggest_outfit` never ran (trace stops at step 2) on all 5 tries: 5/5. |
| 3 | State — `id` passed through unchanged | 5 of 5 | MET (5/5) | Checked, for each of 5 different items, that `session["selected_item"]["id"]` is the literal object passed into `suggest_outfit` (code has no copy step between the two lines) and that the item's identifying details (title, price) stayed consistent from search result through to the fit card: 5/5. |
| 4 | Fit card — 2–4 sentences, mentions price | 5 of 5 | MET (5/5) | Counted sentences (terminal `.`/`!`/`?`) and checked for the price figure in each of 5 different items' fit cards: all 5 were 3 sentences and named the price once: 5/5. |
| 5 | Search respects the price ceiling | 5 of 5 | MET (5/5) | Ran `search_listings` directly for 5 different `max_price` values and checked every returned price against its ceiling with a one-line comparison, not by eye: 5/5. |

**Diagnoses**

I didn't miss anything — all five criteria held at or above their targets. Rather than call that a clean bill of health, here's an honest read of what that result actually shows and doesn't show.

**Criteria 2, 3, and 5 are solid, and I'd stand behind a 5/5 MET on all three.** They're not model-dependent (criterion 2 branches on local data, criterion 3 is a guaranteed-by-construction reference hand-off, criterion 5 is a deterministic filter), so there's no real chance of flakiness across tries — the 5-tries structure confirms consistency rather than surfacing rare failures, which is exactly what their "5 of 5, no randomness" reasoning in `criteria.md` predicted.

**Criterion 1 is the one I'd flag.** Its target was deliberately 4 of 5, not 5 of 5, "because my search is a plain keyword match and some phrasings will miss" — but my test scenario reused the single best-matching query from unit 3 (`vintage graphic tee under $30`), run 5 times. A plain keyword-overlap search returns the *same* result for the *same* query every time — there's no run-to-run randomness in `search_listings` at all, since it doesn't call the model. So this test could never have produced anything but 5/5; it never exercised the actual risk the target was written to budget for (an imperfectly-phrased query scoring zero overlap and coming back empty). If I were tightening one criterion, it's this one — not the target itself, but the test: 5 *different*, more realistically-imperfect phrasings (synonyms or wording a real user might type that isn't literally in the listing text — "jumper" instead of "sweater," "purse" instead of "bag") would be the honest way to find out whether 4 of 5 is really where this system sits, instead of confirming something that was never in doubt.

**Criterion 4 is the closest to a real stress test among the three "diverse item" criteria**, since it depends on `TEMPERATURE=0.9` model output staying structurally consistent across genuinely different prompts (different item details each time) — and it held. I'd call this a meaningful pass, not an artifact of an easy scenario.

**One real latent bug exists that none of these five criteria would ever catch**, because it's not about behavior under valid input — `search_listings` indexes `listing["price"]` and `listing["size"]` directly, so a listing missing either field crashes the whole agent with a raw `KeyError` instead of any handled message. I confirmed this by constructing a listing with no `price` field and calling `search_listings` on it directly: it raised `KeyError: 'price'` rather than skipping the bad record or defaulting it. This never fires against the current `data/listings.json` (every listing is well-formed), so none of my criteria were positioned to find it — but it's exactly the inconsistency last unit's feedback named ("`search_listings` indexes directly... while `suggest_outfit` uses `.get()` with fallbacks for the same kind of record... Mixed assumptions are how a `None` size or missing field turns into a crash"). That's the mechanism behind this unit's improvement (below).

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Failure modes triggered on purpose**

1. **Empty search** — `python app.py ask 'designer ballgown size XXS under $5' --trace`. The loop stops at step 2 and returns: *"No listings matched "designer ballgown" under $5 in size XXS. Try using different keywords, or raising the price ceiling, or trying a different size."* Names three concrete levers, never calls `suggest_outfit`.

2. **Empty wardrobe** — `python app.py ask 'denim jacket under $50' --empty-wardrobe --trace`. All 4 steps complete; `suggest_outfit` returns general styling advice ("This versatile light-wash denim jacket pairs effortlessly with high-waisted wide-leg trousers, slip dresses, or casual sweatpants…") instead of crashing or returning an empty string. This path was already handled in unit 3 — unit 4 confirmed it still holds.

3. **Model unavailable** — one character of `GEMINI_API_KEY` in `.env` changed, then `python app.py ask 'silk slip dress in midi length under $40' --trace` (a query not previously run, so it couldn't be served from cache). The loop completes step 2 (search still works — it's local data, no model needed), reaches step 3, and stops: *"Couldn't reach the styling model to suggest an outfit: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com."* No stack trace, no hang, `create_fit_card` never runs. The key was restored immediately after.

The empty-search branch and the empty-wardrobe handling already existed from unit 3 and needed no changes — this unit's job there was triggering them on purpose and confirming the messages still hold up. The model-unavailable handler is new this unit: `generate.py` already raised `ModelUnavailable` with a readable message, but nothing in `agent.py` caught it, so a bad key would have surfaced as an uncaught exception. I added a `try`/`except ModelUnavailable` around both model-calling steps (`suggest_outfit` and `create_fit_card`) in `agent.py::run_agent`, each setting `session["error"]` and returning early rather than crashing or continuing with no outfit/fit card.

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: results found, continuing to suggest_outfit
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe_items
      out: **Outfit 1: Y2K Streetwear Edge** Pair the Y2K butterfly baby tee with your baggy straight-leg dark wash jeans…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: the cutest lil butterfly baby tee to channel your inner 2000s pop star. honestly looks so good with baggy deni…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear Edge**
Pair the Y2K butterfly baby tee with your baggy straight-leg dark wash jeans and chunky white sneakers for a classic
noughties silhouette. Layer your black cropped zip hoodie over top unzipped to tie the streetwear aesthetic together.

**Outfit 2: Casual Contrast**
Combine the fitted baby tee with your wide-leg khaki trousers and brown leather belt for an effortless mix of earth
tones and playful Y2K style. Finish the look with your black combat boots to add a touch of grunge contrast to the
sweet butterfly graphic.

  Fit card: the cutest lil butterfly baby tee to channel your inner 2000s pop star. honestly looks so good with baggy
denim or paired with grunge combat boots for that exact contrast. snag this thrifted find on depop right now for
just $18.0!

0 model calls this session, 2 served from cache
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

  No listings matched "designer ballgown" under $5 in size XXS. Try using different keywords, or raising the price
ceiling, or trying a different size.

0 model calls this session
```

Note how much shorter the empty-search trace is — it stops at step 2, before `suggest_outfit` or `create_fit_card` ever run. That's the branch actually branching, not just a different printout.

**On the MCP move:** `search_listings` is the tool I moved. In `mcp_server.py` I registered it under `@mcp.tool()` with the same name, inputs, and types as my Tool Inventory entry, plus a description written for a reader who can't see `tools.py` (what it filters on, and that it returns `[]`, never `null`, when nothing matches). In `agent.py`, the direct import `from tools import search_listings` became `from mcp_client import call_tool`, and the call site became `call_tool("search_listings", {"description": ..., "size": ..., "max_price": ...})`. I verified the swap with `python mcp_client.py` first (it listed the tool with the right description and three typed inputs, `size`/`max_price` correctly optional) before touching `agent.py`.

Nothing behaved differently after the rewire — `python app.py ask 'vintage graphic tee under $30'` returned the exact same item, outfit, and fit card as the unit-3 run (both served from cache, so this also confirms the cache key doesn't depend on how the tool was called). The only visible change is in the trace, where the step is now labeled `search_listings (via MCP)` and the inputs/outputs pass through one extra serialization round-trip (Python dict → MCP content block → JSON → Python dict again) that `mcp_client._unwrap()` handles. No behavior difference, same return shape — which is the result the assignment says to expect when the move goes cleanly.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

Two files, one change: `utils/data_loader.py::load_listings()` now normalizes every raw listing through a new `_normalize_listing()`, filling in a safe default (`""`, `[]`, `0.0`, `"unknown"`, etc. — see `_LISTING_DEFAULTS`) for any field missing from the JSON record. With that guarantee in place, `tools.py` was made consistent: `search_listings`'s `listing.get("style_tags", [])` became `listing["style_tags"]`, and `suggest_outfit`/`create_fit_card`'s `new_item.get('title')`-style fallbacks became direct indexing (`new_item['title']`, etc.), since `new_item` is always a listing dict that has already passed through the normalized loader. Wardrobe-item access (`w.get(...)` in `suggest_outfit`) was deliberately left alone — wardrobe items come from a different, separate data source that isn't validated by this change, so keeping `.get()` there is the correct call, not leftover inconsistency.

**Which failure it was meant to fix:**

Last unit's feedback: *"`search_listings` indexes directly (`listing["price"]`, `listing["size"]`) while `suggest_outfit` uses `.get()` with fallbacks for the same kind of record... Mixed assumptions are how a `None` size or missing field turns into a crash in the one code path you didn't test."* I confirmed this was a real, reproducible gap, not just a style nitpick — before this fix, constructing a listing with no `price` field and calling `search_listings` on it directly raised `KeyError: 'price'` and crashed the whole agent, rather than skipping or defaulting the bad record:

```
$ python3 -c "
import utils.data_loader as dl
_orig = dl.load_listings
def _broken():
    listings = _orig()
    bad = dict(listings[0]); del bad['price']
    return [bad] + listings[1:]
dl.load_listings = _broken
from tools import search_listings
try:
    r = search_listings('vintage', max_price=100)
    print('No crash:', len(r), 'results')
except Exception as e:
    print(f'CRASHED: {type(e).__name__}: {e}')
"
CRASHED: KeyError: 'price'
```

After the fix, the identical reproduction no longer crashes — the malformed listing gets `price: 0.0` from the normalizer and is simply treated as a $0 item instead of blowing up the loop:

```
No crash: 10 results. Top: Vintage Levi's 501 Jeans — Medium Wash 0.0
```

This never fires against the real `data/listings.json` (every listing there is complete), so it's not something any of my five criteria could have caught — it's a robustness fix for data the system hasn't been handed yet, not a fix for an observed miss.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all 3 tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. State — `id` passed through unchanged | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card — 2–4 sentences, mentions price | 5 of 5 | **FAIL** | PASS | PASS | PASS | PASS | MISSED (4/5) |
| 5. Search respects the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

(Same sampling method as the Before table: Try 1 from each of the 5 diverse-item scenarios, one try per item, since criteria 3–5 need 5 *different* items.)

**What happened on criterion 4's Try 1 (item 4, crochet halter top):** the service returned a real `503 UNAVAILABLE` ("This model is currently experiencing high demand") on the `create_fit_card` call — twice, on item 4's Try 1 and Try 3. `agent.py::run_agent`'s `ModelUnavailable` handler (added this unit) caught it correctly both times: `selected_item` and `outfit_suggestion` are intact, `session["error"]` is set to a readable message, and the run stops before producing a malformed or missing fit card — no crash, no stack trace:

```
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe_items
      out: Layer the cream crochet halter top directly over your white ribbed tank top, and pair them with your baggy str…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      →    branch: model unavailable, stopping

stopped early: yes — Couldn't reach the captioning model to write a fit card: Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

Note what *didn't* break: criterion 3 (state) is still 5/5 even on this exact try — `selected_item` was correctly threaded into `suggest_outfit`, which produced a valid outfit; only the second, later model call failed. The state hand-off and the model-availability failure are independent, and the trace makes that visible rather than just reporting "it failed."

**Did it help, and how do I know:**

For its actual target — yes, directly confirmed above: the reproduced crash is gone, and the five real-data queries (`search_listings` run again post-fix) return byte-identical results to before the fix, so nothing regressed for well-formed data. That's the only claim this improvement was meant to support, and it holds.

For the five criteria, the honest picture is one MET→MET→MET→**MISSED**→MET. I want to be precise about why, because it would be easy to either hide this or over-claim it: the criterion-4 miss was **not caused by this unit's code change**. The fix touches only local dict construction in `utils/data_loader.py` and attribute access in `tools.py` — it never calls the network. The actual cause was the live Gemini service returning a transient `503` twice during this run, which is exactly the kind of "model unavailable" condition the `ModelUnavailable` handler (a *different*, Milestone-2 change) exists to catch — and it did, cleanly. I'm reporting the 4/5 as-is instead of re-running the eval until criterion 4 comes back clean, because quietly re-rolling for a better-looking result is the opposite of what this unit is testing for. If anything, this is a second, real finding to add to the diagnosis: criterion 4's "5 of 5" target budgets for wording variation under `TEMPERATURE=0.9`, but not for the live model service itself being briefly unavailable mid-run — a second, independent reason (beyond criterion 1's) that a "5 of 5" or "4 of 5" target on a model-calling step is making an assumption about infrastructure reliability that this run shows doesn't always hold.



---

## What's Still Broken

**Criterion 4's target doesn't budget for the live model being briefly unavailable.** The After run showed this directly: `generate.py`'s retry logic only retries on rate-limit errors (`429`, or "resource"+"exhaust", or "rate"+"limit" in the message) — a `503 UNAVAILABLE` doesn't match any of those, so it's treated as a hard failure and raises `ModelUnavailable` immediately, with no retry, even though the service's own error message says "Spikes in demand are usually temporary." I'd broaden that check to also retry (with a short backoff) on `503`/`UNAVAILABLE` before giving up, so a run rides out a few-second blip instead of stopping early. I didn't make this change because it's a different fix from the one my diagnosis was built around (the data-normalization gap), and this unit's rule is one improvement — but it's now a concretely diagnosed, next-in-line fix, not a vague "might be nice."

**Criterion 1's target was never actually stress-tested.** My diagnosis already covers why: the before/after scenario reused the one query guaranteed to match, which can't exercise "some phrasings will miss." I stopped there rather than also building a second battery of 5 deliberately-imperfect phrasings, because that's a second test design change on top of the one code change this unit allows, and I'd rather report "I didn't test this well" honestly than rush a second experiment I can't give a fair before/after to. Next time: 5 queries using realistic synonyms absent from the listing text (e.g. "jumper" for sweater, "purse" for bag), see where it actually breaks, then decide whether 4/5 holds or whether the matching logic needs to improve.

**The ranking-quality gap from unit 3's feedback is still open.** The feedback noted that `search_listings`'s score is a raw count of overlapping tokens with no visibility into *why* a result is top, and suggested printing scores while testing to check the top result is top for a good reason. I didn't address this — and more than that, my five "diverse item" test queries were deliberately hand-picked (and checked against the real scoring function before use) to have one obvious, unambiguous best match each, specifically so criteria 3–5 wouldn't have to deal with a close call. That made for a clean test, but it also means none of this unit's testing says anything about ranking quality under a more realistic, ambiguous query — that risk is still exactly where the previous grader left it.

**Stretch features:** not attempted this unit — no second tool moved to MCP, no retry-with-looser-constraints on empty search, no second improvement. The one-improvement rule and the time this unit's model-call volume takes (real API calls, paced to the rate limit, run twice for before/after) were the stopping point, not a decision that these wouldn't be worth doing.



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
