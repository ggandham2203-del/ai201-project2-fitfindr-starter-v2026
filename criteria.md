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

## 3. State — the item passed through, not reconstructed

Given 5 different queries that each return at least one match, the `id` in
`session["selected_item"]` is identical to the `id` of the listing object
actually passed into `suggest_outfit` — in 5 of 5 tries.

**Why this target:**

The hand-off from `search_listings` to `suggest_outfit` is a plain dictionary
reference with no transformation step in between — there's no legitimate
source of noise that would excuse a mismatch, so it should hold every time.

---

## 4. Fit card — structural reliability despite wording variation

Given 5 different items, each resulting fit card is a non-empty caption of
2–4 sentences that mentions the item's price at least once — in 5 of 5 tries.

**Why this target:**

`TEMPERATURE=0.9` means the exact wording is expected to differ run to run —
that's by design, not a defect. But the length and the price mention are
controlled by my prompt, not the model's creative discretion, so those two
structural facts shouldn't be allowed to slip even while the phrasing varies.

---

## 5. Search respects the price ceiling exactly

Given 5 queries that each specify a `max_price`, every listing returned in
`search_results` has a `price` less than or equal to that ceiling — in 5 of 5
tries.

**Why this target:**

This filter runs over static local data with no model call involved, so
there's no randomness to account for — any violation would be a
straightforward bug in the filter logic, not noise worth budgeting a miss
for.



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
