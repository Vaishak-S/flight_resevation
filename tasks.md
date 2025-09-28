Nice — clear goal. I won’t ask questions unless strictly needed; instead I’ll give a concrete, day-by-day **1-week plan** (7 days × 2 hours/day) of focused sub-tasks to get a minimal but working Streamlit + FastAPI + MCP-tooling flight booking demo. Each subtask has a short deliverable so you can check progress every session.

# Plan assumptions (so the subtasks make sense)

* Minimal viable product (MVP) that supports: **book**, **cancel**, **reschedule** flight flows via a chat UI backed by an LLM-driven MCP server that calls FastAPI endpoints.
* Local dev stack: Python 3.10+, virtualenv/venv, FastAPI, Uvicorn, Streamlit, SQLAlchemy (SQLite for MVP), simple MCP server implemented as a small Python service (can be later replaced by a proper agent framework).
* No external LLM provider locked in — implement an LLM adapter interface (so you can plug OpenAI/Anthropic/other later).
* Keep the flows deterministic/simplified (no real payments, only reservations recorded in DB).

If any of the above assumptions should change (DB choice, auth, provider), tell me and I’ll adapt the plan — otherwise proceed.

---

# Week plan (2 hours per day)

## Day 1 — Project scaffolding & spec (2 × 60 min)

1. Create repo & branches, local Python venv.

   * Deliverable: repo root with README stub, `.gitignore`, `requirements.txt`.
   * Time: 15 min
2. Define tech stack & app layout; write brief API contract and sample payloads for `book`, `cancel`, `reschedule`.

   * Deliverable: `docs/API_SPEC.md` with endpoint paths + request/response JSON examples.
   * Time: 35 min
3. Create skeleton folders & files.

   * Structure:

     ```
     flight-chat/
     ├─ backend/
     │  ├─ app/
     │  │  ├─ main.py            # FastAPI entry
     │  │  ├─ api/
     │  │  │  ├─ bookings.py    # endpoints
     │  │  ├─ models.py         # SQLAlchemy models
     │  │  ├─ schemas.py        # Pydantic schemas
     │  │  ├─ db.py             # DB setup
     │  └─ requirements.txt
     ├─ mcp_server/
     │  ├─ mcp.py               # LLM intent parsing + tool routing
     │  └─ tools.py             # functions that call backend endpoints
     ├─ frontend/
     │  ├─ streamlit_app.py
     ├─ scripts/
     │  ├─ seed_db.py
     └─ README.md
     ```
   * Deliverable: empty files created.
   * Time: 10 min

## Day 2 — Backend DB + models + basic endpoints (2 × 60 min)

1. Implement DB and SQLAlchemy models (SQLite for now).

   * Deliverable: `backend/app/db.py` and `models.py` with `Booking` model (id, passenger_name, from, to, date, time, status, created_at, updated_at, booking_reference).
   * Time: 45 min
2. Create Pydantic schemas and stub endpoints for book/cancel/reschedule (no logic yet).

   * Deliverable: `schemas.py` and `api/bookings.py` with POST `/book`, POST `/cancel`, POST `/reschedule` that return simple JSON.
   * Time: 75 min

## Day 3 — Implement FastAPI business logic + persistence (2 × 60 min)

1. Implement booking business logic:

   * Create bookings with generated `booking_reference` (e.g., `BK-<timestamp>`), status = `CONFIRMED`.
   * Deliverable: working `/book` endpoint that persists to DB and returns booking reference.
   * Time: 60 min
2. Implement cancel and reschedule:

   * `/cancel` takes `booking_reference` -> sets `status=CANCELLED` and returns confirmation.
   * `/reschedule` takes `booking_reference` + new date/time -> updates booking and returns new details.
   * Add simple validation (404 if not found, status checks).
   * Deliverable: functioning cancel/reschedule endpoints + unit test calls via `curl` or `httpie`.
   * Time: 60 min

## Day 4 — MCP server: LLM interface + tools adapters (2 × 60 min)

1. Implement LLM adapter interface and a **simple rule/regex intent parser** for MVP:

   * `mcp_server/llm_adapter.py` with `generate_response(prompt)` (returns deterministic responses for dev or calls a real LLM if available).
   * Deliverable: adapter with a configurable `USE_MOCK_LLM = True` flag.
   * Time: 40 min
2. Implement `tools.py` with three tools that call backend endpoints:

   * `book_tool(payload) -> calls backend /book`
   * `cancel_tool(booking_reference) -> calls /cancel`
   * `reschedule_tool(payload) -> calls /reschedule`
   * Use `requests` to call FastAPI local endpoints.
   * Deliverable: tool functions + a local test script `mcp_server/test_tools.py`.
   * Time: 80 min

## Day 5 — Wire MCP to LLM & implement flow orchestration (2 × 60 min)

1. Implement `mcp.py` core:

   * Accept user message, call LLM adapter to identify intent and extract slots (passenger name, from, to, date/time, booking_reference).
   * Map intent to corresponding tool and call that tool with the structured data.
   * Return combined assistant message and tool output.
   * Deliverable: `mcp_server/mcp.py` with `handle_message(user_text)` returning JSON `{assistant_text, tool_output}`.
   * Time: 80 min
2. Create a few test prompts and iterate on prompt templates / slot-extraction heuristics.

   * Deliverable: `examples/` with sample conversations and expected outputs.
   * Time: 40 min

## Day 6 — Streamlit chat UI + integrate with MCP (2 × 60 min)

1. Build Streamlit UI:

   * Chat message stream, input box, send button, show booking summary cards, show booking reference and action buttons (Cancel / Reschedule prefilled form).
   * Deliverable: `frontend/streamlit_app.py` that sends user message to MCP server and displays response and tool output.
   * Time: 80 min
2. Add little UX niceties:

   * Render statuses (CONFIRMED, CANCELLED), ephemeral loading spinner while waiting.
   * Save chat history in `st.session_state`.
   * Deliverable: working UI locally (`streamlit run frontend/streamlit_app.py`).
   * Time: 40 min

## Day 7 — Testing, logging, docs, deployment prep (2 × 60 min)

1. End-to-end test flows and fix bugs:

   * Test booking -> cancel -> reschedule flows via UI and direct API.
   * Add logging to backend and MCP for easier troubleshooting.
   * Deliverable: `tests/` folder with basic integration scripts + updated bug fixes.
   * Time: 60 min
2. Final polish & deliverables:

   * Create `Dockerfile` and `docker-compose.yml` for local dev (FastAPI + MCP service + Streamlit), or at least provide run instructions.
   * Finalize `README.md` with run steps, API spec pointer, and how to switch to a real LLM.
   * Deliverable: working README and docker files (or run scripts).
   * Time: 60 min


----------------------------------------------------------------------------------------------------------------

# Minimal folder/file checklist to create right now

* `backend/app/main.py` (FastAPI app)
* `backend/app/api/bookings.py`
* `backend/app/models.py`, `schemas.py`, `db.py`
* `mcp_server/mcp.py`, `mcp_server/tools.py`, `mcp_server/llm_adapter.py`
* `frontend/streamlit_app.py`
* `scripts/seed_db.py`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `README.md`, `docs/API_SPEC.md`
