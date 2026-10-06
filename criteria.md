# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"The agent handles errors"_ is an opinion.
_"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
The search is a plain keyword match, so an unusual phrasing can miss even when a related listing exists. Allowing one miss accounts for that limitation while still requiring the common query to work reliably.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This branch is deterministic: an empty search result should always stop the loop before any model-backed tools run. There is no wording variation from a model to justify an occasional failure.

---

## 3. Something about state

For a matching query, the ID in `session["selected_item"]` matches the `new_item` ID recorded in the `suggest_outfit` trace inputs — in 5 of 5 tries.

**Why this target:**
Passing the selected item through session state is deterministic and does not depend on the model, so it should be correct every time. Comparing IDs proves it is the same listing, even if two listings have similar titles.

---

## 4. Something about the fit card

Across 5 uncached tries for the same matching query, at least 4 fit cards mention the selected listing's title, exact price, and platform, and are 2–4 sentences long. The wording may differ between tries.

**Why this target:**
The model can vary its wording, so identical captions are not required; the item facts and a post-length caption are what make each result useful. Four of five allows an occasional formatting or omission error without treating unreliable cards as acceptable.

---

## 5. Your choice

For the query `vintage graphic tee under $30`, every result in `session["search_results"]` costs $30 or less — in 5 of 5 tries.

**Why this target:**
The price ceiling is a direct numeric filter against local listing data, not a model judgment, so it should be consistent every time. A 5-of-5 target is realistic and catches a search that silently ignores the user's budget.

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
