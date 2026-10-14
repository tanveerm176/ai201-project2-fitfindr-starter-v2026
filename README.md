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
> These commands let you inspect the listings and try the completed FitFindr workflow.
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

FitFindr takes a request for secondhand clothing, including an optional size and budget, and searches local resale listings. It ranks keyword matches and filters out items that do not meet the requested size or maximum price. For the best match, it uses the user's wardrobe to suggest outfits and creates a short fit-card caption. If nothing matches, it stops and tells the user whether to change the description, size, or price limit.

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

- **What it does:** Finds listings that match the requested description and any supplied size or maximum-price filters, ranked by relevance.
- **Inputs:** `description` (str), `size` (str | None), `max_price` (float | None).
- **Returns:** Up to the configured result limit: a list of listing dicts containing `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`, with the strongest keyword match first.
- **When it has nothing:** Returns an empty list when no listings match.

### `suggest_outfit`

- **What it does:** Suggests one or two outfits that use a selected listing and pieces from the user's wardrobe.
- **Inputs:** `new_item` (dict representing a listing), `wardrobe` (dict with `items` as a list of wardrobe-item dicts).
- **Returns:** A non-empty string with outfit suggestions; with wardrobe items, suggestions name owned pieces.
- **When it has nothing:** If `wardrobe['items']` is empty, returns general styling advice for the listing instead of an empty string.

### `create_fit_card`

- **What it does:** Writes a short social caption for the selected listing and its outfit suggestion.
- **Inputs:** `outfit` (str), `new_item` (dict representing a listing).
- **Returns:** A two-to-four sentence caption that mentions the item, price, and platform once each and describes its vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, returns a descriptive message instead of raising an error.

**Spec check:** Could someone else build these tools from this inventory without asking me anything? Yes. Size matching uses exact normalized size tokens, so `M` matches `S/M` and `L` does not match `XL`.

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

**Branch rule:** If `search_listings` returns an empty list, set `session['error']` to `No listings matched those filters. Try a different description, size, or higher price limit.` and stop. Otherwise, take the first result, store it in `session['selected_item']`, and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Use regular expressions to extract a size and a maximum price; treat the remaining words as the description.

**What moves through the session:** `query` -> `parsed` -> `search_results` -> `selected_item` -> `outfit_suggestion` -> `fit_card`; on the empty-results branch, set `error` and return before calling the later tools.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
     Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

     Outfit:   **Outfit 1: Y2K Streetwear**
* **New Item:** Y2K Butterfly Baby Tee
* **Bottoms:** Baggy straight-leg jeans (`w_001`)
* **Outerwear:** Black cropped zip hoodie (`w_005`)
* **Shoes:** Chunky white sneakers (`w_007`)
* **Bag:** Black crossbody bag (`w_010`)
* *Why it works:* The fitted crop of the baby tee balances the baggy silhouette of the dark-wash jeans, leaning into authentic early-2000s proportions.

**Outfit 2: Edgy Contrast**
* **New Item:** Y2K Butterfly Baby Tee
* **Bottoms:** Wide-leg khaki trousers (`w_002`)
* **Outerwear:** Vintage black denim jacket (`w_006`)
* **Shoes:** Black combat boots (`w_008`)
* **Accessories:** Brown leather belt (`w_009`)
* *Why it works:* The pink and purple butterfly graphic softens the utilitarian khaki trousers, while the black denim jacket and combat boots add a grounded, grunge edge.

     Fit card: Channel ultimate early-2000s energy with this Y2K Baby Tee — Butterfly Print, featuring a sweet pink and purple graphic and a fitted crop length. Pair it with baggy jeans or utilitarian trousers to nail that authentic nostalgic silhouette. Score this piece for just $18.0 currently live on depop.

0 model calls this session, 2 served from cache

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(x['title'], x['price'], x['size'], x['platform']) for x in search_listings('graphic tee', max_price=30)])"
[('Y2K Baby Tee — Butterfly Print', 18.0, 'S/M', 'depop'), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L', 'depop'), ('Mesh Long-Sleeve Top — Black', 15.0, 'S/M', 'depop'), ('Vintage Band Tee — Faded Grey', 19.0, 'L', 'depop'), ('Low-Rise Cargo Pants — Khaki', 27.0, 'W29', 'poshmark'), ('Vintage Graphic Hoodie — Faded Black', 26.0, 'L', 'depop')]

```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
**Outfit 1: Effortless Streetwear**
*   **Top:** White ribbed tank top (w_003)
*   **Outerwear:** Vintage black denim jacket (w_006)
*   **Shoes:** Chunky white sneakers (w_007)
*   **Accessories:** Brown leather belt (w_009) + Black crossbody bag (w_010)
*   *Why it works:* The cropped black jacket balances the straight-leg fit of the vintage 501s, while the white tank and sneakers keep the look fresh and casual.

**Outfit 2: Cozy Casual**
*   **Top:** Oversized grey crewneck sweatshirt (w_004)
*   **Shoes:** Black combat boots (w_008)
*   **Accessories:** Brown leather belt (w_009)
*   *Why it works:* Pairing the fitted, classic 501s with an oversized crewneck creates a balanced high-low silhouette. Tuck the front of the sweatshirt in to show off the belt.

```

```
$ python -c "import config; config.CACHE_ENABLED=False; from tools import create_fit_card; from utils.data_loader import load_listings; item=load_listings()[0]; [print(f'Try {i+1}: {create_fit_card(\"jeans and white sneakers\", item)}') for i in range(3)]"
Try 1: Pair these classic Vintage Levi's 501 Jeans — Medium Wash with clean white sneakers for an effortless streetwear look. Featuring a great medium wash with natural knee fading, they bring instant vintage character to your rotation. Grab this pair now on depop for just $38.0.
Try 2: Throw on those white sneakers and the Vintage Levi's 501 Jeans — Medium Wash for an effortless, classic look. These broken-in blues bring the ultimate streetwear energy with just the right amount of knee fading. Grab them now on depop for $38.0.
Try 3: Pair these effortless Vintage Levi's 501 Jeans — Medium Wash with clean white sneakers for an easy, everyday look. They feature a great medium wash with natural light fading at the knees. Grab this classic denim staple for $38.0 on depop before it's gone!

```

### Failure-path checks

```
$ python app.py ask 'unobtainium ceremonial jumpsuit size ZZQX under $0.01'
No listings matched those filters. Try a different description, size, or higher price limit.
0 model calls this session
```

The empty-wardrobe check used the CLI with `--empty-wardrobe` and a local
deterministic model stub, so it did not send a request to the model provider:

```
$ python app.py ask 'vintage graphic tee under $30' --empty-wardrobe
(running with an empty wardrobe)
Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop
Outfit: Try layering this graphic tee under a denim jacket and pairing it with neutral trousers. Finish with comfortable sneakers and a simple accessory.
Fit card: Pair the tee with relaxed jeans and sneakers for an easy casual look.
0 model calls this session
```

For model-unavailable handling, I used a disposable invalid `GEMINI_API_KEY`
environment override and disabled cache, leaving `.env` unchanged:

```
$ python app.py ask 'vintage band tee under $25'
The model couldn't be reached to generate outfit advice. Check your internet connection and GEMINI_API_KEY, then try again. Details: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
1 model calls this session
```

Before adding the `ModelUnavailable` handler, this path printed a
`ModelUnavailable` message and exited with status 1. After the handler it
returns an actionable session error and exits normally.

---

## How I Used AI

**Moment 1**

- _What I asked for:_ I asked GitHub Copilot to implement the three tools from their existing signatures, especially the search filters and the empty-wardrobe behavior.
- _What came back:_ It proposed keyword-overlap ranking, exact size-token matching, a price ceiling, and separate prompts for wardrobes with and without saved items.
- _What I changed:_ I checked the size edge cases against the listing data, kept matching case-insensitive, and verified that `M` matches `S/M` while `L` does not match `XL`. I also tested the empty-wardrobe prompt path.

**Moment 2**

- _What I asked for:_ I asked GitHub Copilot to wire `run_agent()` through the session fields and stop before outfit generation when search returns no results.
- _What came back:_ It added regex parsing for size and price and passed the selected listing through session state to the next tool.
- _What I changed:_ The first run exposed a missing `re` import. I added it, reran the happy path, and checked that the selected listing ID matched the ID received by `suggest_outfit`; I also verified the no-match message and that `fit_card` stays `None`.

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
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item ID reaches `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card includes title, price, platform, 2-4 sentences | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search results respect the $30 ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try per criterion**, from
[`results/run_2026-10-13_2250_before.md`](./results/run_2026-10-13_2250_before.md).
Evaluator output was produced by `run_eval.py::run_once` calling
`agent.py::run_agent`; the price-filter output was produced by
`mcp_client.call_tool` -> `mcp_server.py::search_listings` ->
`tools.search_listings`.

**Criterion 1 — `agent.py::run_agent`**

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10
Fit card:
Channel your inner early 2000s icon with this sweet-meets-grunge Y2K Baby Tee — Butterfly Print, featuring a fitted crop length and pink, purple, and white graphic. Pair the pink-and-purple butterfly graphic with baggy jeans or utilitarian trousers for the ultimate nostalgic silhouette. Snag this excellent-condition vintage top for just $18.0 on depop before it's gone!
```

**Criterion 2 — `agent.py::run_agent` empty-search branch**

```
- stopped early: yes — No listings matched those filters. Try a different description, size, or higher price limit.
- selected_item: (none)
- search_results: 0
[1] search_listings (via MCP)
      in:  description='unobtainium ceremonial jumpsuit', size='ZZQX', max_price=0.01
      out: [] (empty)
```

**Criterion 3 — `agent.py::run_agent` trace inputs**

```
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[2] suggest_outfit
      in:  new_item_id='lst_002', new_item_title='Y2K Baby Tee — Butterfly Print', wardrobe_items=10
```

The selected item's ID and the `suggest_outfit` input ID were `lst_002` in
each of the five recorded tries.

**Criterion 4 — `tools.create_fit_card`, try 1**

```
Lean into effortless 2000s style with the Y2K Baby Tee — Butterfly Print, featuring a sweet graphic and fitted crop length. Layer the pink and purple tones under a zip hoodie or pair it with baggy denim for that ultimate nostalgic silhouette. Grab this cute vintage find for just $18.0 today on depop!
```

The five actual cards are in the linked run report under “fit card includes
item facts”; each contains the exact title, `$18.0`, `depop`, and 2-4
sentences.

**Criterion 5 — five calls to `tools.search_listings` via MCP**

```
Try 1: count=10, prices=[18.0, 24.0, 19.0, 26.0, 15.0, 22.0, 27.0, 20.0, 30.0, 12.0], within_limit=True
Try 2: count=10, prices=[18.0, 24.0, 19.0, 26.0, 15.0, 22.0, 27.0, 20.0, 30.0, 12.0], within_limit=True
Try 3: count=10, prices=[18.0, 24.0, 19.0, 26.0, 15.0, 22.0, 27.0, 20.0, 30.0, 12.0], within_limit=True
Try 4: count=10, prices=[18.0, 24.0, 19.0, 26.0, 15.0, 22.0, 27.0, 20.0, 30.0, 12.0], within_limit=True
Try 5: count=10, prices=[18.0, 24.0, 19.0, 26.0, 15.0, 22.0, 27.0, 20.0, 30.0, 12.0], within_limit=True
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

| #   | Criterion | Target | Verdict | How I decided |
| --- | --------- | ------ | ------- | ------------- |
| 1   | Matching query completes all three tools | 4 of 5 | MET (5/5) | All five matching runs reached `create_fit_card` and returned a non-empty fit card. |
| 2   | Impossible query stops before tool 2 | 5 of 5 | MET (5/5) | All five returned zero listings, set the actionable empty-search message, and traced only `search_listings`; no outfit tool ran. |
| 3   | Selected item ID reaches `suggest_outfit` | 5 of 5 | MET (5/5) | All five traces showed `new_item_id='lst_002'`, matching the selected listing ID. |
| 4   | Fit card includes title, exact price, platform, and 2-4 sentences | 4 of 5 | MET (5/5) | Each of the five uncached cards included `Y2K Baby Tee — Butterfly Print`, `$18.0`, `depop`, and 2-3 sentences. |
| 5   | Search results respect the $30 ceiling | 5 of 5 | MET (5/5) | All five searches returned the same 10 listings; every price was at or below $30 (maximum $30.0). |

**Diagnoses**

There were no misses to diagnose. None of the tool, loop-branch, session, or
model-output steps failed these five measured criteria in this run. The run
supports the deterministic 5-of-5 targets (#2, #3, and #5) for the tested
inputs. Criteria 1 and 4 allowed one miss but both achieved 5/5; based on this
evidence, criterion 4 is the one I would tighten to 5 of 5 on a future run.
I have not changed its original target after seeing these results.

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
[1] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] suggest_outfit
      in:  new_item='Y2K Baby Tee — Butterfly Print', wardrobe_items=10
      out: **Outfit 1: Y2K Streetwear** * **New Item:** Y2K Butterfly Baby Tee * **Bottoms:** Baggy straight-leg jeans (`…
[3] create_fit_card
      in:  outfit='**Outfit 1: Y2K Streetwear**\n* **New Item:** Y2K Butterfly Baby Tee\n* **Bottoms:** Baggy straight-le…
      out: Channel ultimate early-2000s energy with this Y2K Baby Tee — Butterfly Print, featuring a sweet pink and purpl…
```

**Empty search**

```
$ python app.py ask 'unobtainium ceremonial jumpsuit size ZZQX under $0.01' --trace
[1] search_listings (via MCP)
      in:  description='unobtainium ceremonial jumpsuit', size='ZZQX', max_price=0.01
      out: [] (empty)
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

In `tools.py::create_fit_card`, I strengthened the prompt to require the
listing title, dollar price, and platform exactly once each, copied verbatim
with their spelling and capitalization preserved, in two to four complete
sentences.

**Which failure it was meant to fix:**

This targets potential misses in criterion 4, where the model's fit-card
output could omit or alter a required listing fact or produce the wrong
sentence count. The before-run had no misses, so it is a reliability
improvement to the prompt contract rather than a fix for an observed failed
try.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item ID reaches `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card includes title, exact price, platform, 2-4 sentences | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search results respect the $30 ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Five tries per scenario, with caching off. The full evaluator output,
including all five real fit cards and each trace, is in
[`results/run_2026-10-13_2306_after.md`](./results/run_2026-10-13_2306_after.md).

**Did it help, and how do I know:**

All five fit-card tries still met criterion 4 after the prompt change, and
criteria 1, 2, 3, and 5 remained 5/5. It did not improve the measured score:
criterion 4 was already 5/5 in the before-run. The prompt now states the exact
format more clearly, but these runs cannot demonstrate a reliability increase
from a perfect baseline. The improvement therefore caused no measured
regression, but its benefit remains unproven.

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
