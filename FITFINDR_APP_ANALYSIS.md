# FitFindr App Analysis

## 1. What this app is meant to do

FitFindr is a thrift-shopping assistant for a user who wants to search a catalog of secondhand clothing listings, pick a likely match, and get help styling it using their wardrobe.

The intended flow is:

1. A user types a shopping query such as "vintage graphic tee under $30".
2. The app parses the request into a description, optional size, and optional price ceiling.
3. It searches the listing dataset for matching items.
4. If anything matches, it chooses one item and asks the model for outfit suggestions based on the user's wardrobe.
5. It then writes a short fit-card caption for a social post that mentions the item, price, platform, and style vibe.

In other words, the app is designed to behave like an AI shopping copilot with a data-backed search step and a creative writing step.

---

## 2. What the current repo is actually doing

This repository is not a finished product yet. It is a starter scaffold for a course project. The codebase is laid out to support the eventual app, but the core business logic is intentionally left as TODOs and stubs.

The clearest indicators are:

- `tools.py` defines the three main functions, but all of them return empty values or placeholder strings.
- `agent.py::run_agent()` is still incomplete and immediately returns an error saying the planning loop is not built yet.
- The app still runs, but the core product flow does not work yet.

So the current state is best described as: a working CLI shell and data+AI infrastructure around an unfinished agent loop.

---

## 3. Core files and their roles

### `app.py`

This is the command-line entry point.

It defines the user-facing commands:

- `python app.py fields` — shows what a listing and wardrobe item look like.
- `python app.py listings` — prints listing data, optionally with full records.
- `python app.py examples` — shows example queries, including one intentionally impossible query.
- `python app.py ask '...'` — runs the agent on a search query.
- `python app.py ask` — loops repeatedly until the user quits.

The file also handles argument parsing with `argparse` and wraps execution in a `main()` function.

### `config.py`

This is the app's central settings file.

Important settings include:

- `TEMPERATURE` — controls model variation; higher values produce more varied output.
- `CACHE_ENABLED` — reuses previous model responses while building, to save quota during debugging.
- `MAX_ITERATIONS` — a loop safety limit to prevent runaway agent loops.
- `SEARCH_RESULT_LIMIT` — how many search results to keep.
- `MODEL` — the Gemini model name.
- `REQUESTS_PER_MINUTE` and `SESSION_REQUEST_BUDGET` — pacing and guardrails.

This file is designed to keep model and runtime settings in one visible place.

### `utils/data_loader.py`

This file loads the mock data used by the app:

- `load_listings()` reads `data/listings.json`
- `get_example_wardrobe()` and `get_empty_wardrobe()` read the example wardrobe and empty template from `data/wardrobe_schema.json`

The dataset is a realistic mock catalog of secondhand items with fields like:

- `id`
- `title`
- `description`
- `category`
- `style_tags`
- `size`
- `condition`
- `price`
- `colors`
- `brand`
- `platform`

The wardrobe schema defines items like tops, bottoms, outerwear, shoes, and accessories, and includes a sample user closet.

### `tools.py`

This file defines the three tools the app is supposed to use:

1. `search_listings(description, size, max_price)`
   - Should look through the listings and return the best matching items.
   - Current status: stubbed and returns `[]`.

2. `suggest_outfit(new_item, wardrobe)`
   - Should produce styling advice based on the chosen item and the user's wardrobe.
   - Current status: stubbed and returns an empty string.

3. `create_fit_card(outfit, new_item)`
   - Should write a social-style caption describing the find and the outfit.
   - Current status: stubbed and returns an empty string.

These tools are the heart of the app, but they are not yet implemented.

### `agent.py`

This file is meant to manage the planning loop.

Its job is to:

- start a new session,
- parse the user query,
- call `search_listings()`,
- branch on whether results were found,
- call `suggest_outfit()`,
- call `create_fit_card()`,
- return a session state object.

In the current code, the loop is explicitly left as a TODO and exits early with:

> "The planning loop isn't built yet — see the TODO in agent.py."

This means the app structure is present, but the orchestration logic is not yet connected.

### `generate.py`

This is the model integration layer.

It is the one place the app talks to the external AI service. It handles:

- API key loading from `.env`
- prompt/call caching
- per-minute request pacing
- session-level request budgets
- retry logic for rate limits
- friendly error messages when the model is unavailable or key is invalid
- token usage accounting

This is the service adapter that the real tool functions would eventually call.

### `trace.py`

This file provides a debugging trace facility.

It stores step-by-step output for the loop and can print a trace like:

- which tool was called,
- what inputs were passed,
- what was returned,
- whether the loop took the empty branch.

The idea is to make debugging much easier when the agent loop is eventually implemented.

---

## 4. How the app is supposed to behave when finished

The intended execution path is:

1. User types a query through `app.py ask`.
2. `agent.py::run_agent()` creates a session dictionary.
3. The query is parsed into fields like description, size, and maximum price.
4. `search_listings()` filters the dataset by those values.
5. If no results match, the agent stops early with a user-friendly error.
6. If matches exist, it picks the first result and sends it to `suggest_outfit()`.
7. `suggest_outfit()` turns the new item plus wardrobe into outfit advice.
8. `create_fit_card()` turns the outfit and item into a “fit card” caption.
9. The session object is returned and printed to the terminal.

That expected architecture is the core product concept.

---

## 5. Current state of the app's real behavior

Right now, the app is mostly a scaffold for that workflow.

The actual behavior in this snapshot is:

- The command-line app launches successfully.
- `fields` and `listings` commands work as informational commands.
- `examples` prints valid sample queries and one empty-search query.
- `ask` calls the agent, but the agent exits immediately because the loop is not implemented.
- Tool functions do not actually search, style, or caption anything yet.

This means the app currently functions as a home for the project specs and tool design, rather than as a usable assistant.

---

## 6. Why this app is structured this way

The project is deliberately organized to teach a clean agent-building pattern:

- data layer: load real mock data,
- tool layer: implement query/search and model-based generation,
- agent layer: orchestrate the control flow,
- model adapter: centralize AI requests and quota protection,
- CLI layer: expose the app to the user,
- trace/debugging utilities: make iteration and failure diagnosis easier.

This is a classic agent architecture in miniature: tool functions + planning loop + model access + user interface.

---

## 7. Bottom line

The application is a starter project for building an AI-powered thrift-shopping recommender. It contains the right architecture, the right dataset, and the right CLI entry points, but the actual logic is still intentionally unbuilt.

At the moment:

- the app can run,
- the data and settings exist,
- the model integration layer exists,
- but the agent loop and the three core tools are still stubs.

So the current state is a blueprint for the finished app, not a working version of the finished app.
