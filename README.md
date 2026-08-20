# OwenAI Website Builder

An autonomous AI agent that builds complete, production-quality websites from a single natural-language prompt — powered by an LLM with function-calling, a real file-system sandbox, and a self-correcting build loop.

## What it does

Give it a description like:

> "Build me a premium website for an AI engineer who builds autonomous agents and teaches AI courses. Include Home, Services, Courses, Portfolio, Contact. Dark futuristic design with purple/cyan accents."

...and the agent plans the structure, writes the HTML/Tailwind/JS, reads its own output back, and edits it until the result is coherent — without a human writing a single line of code.

## How it works

The system runs a **tool-calling agent loop**: the LLM is given three tools and repeatedly decides which one to call next, based on what it sees.

```
User prompt
   │
   ▼
┌─────────────────────────────────────────┐
│              Agent Loop                 │
│                                          │
│   ┌────────────┐                        │
│   │ create_file│──▶ writes new file     │
│   └────────────┘                        │
│   ┌────────────┐                        │
│   │ read_file  │──▶ inspects current    │
│   └────────────┘    file content        │
│   ┌────────────┐                        │
│   │ edit_file  │──▶ makes a targeted,   │
│   └────────────┘    surgical fix        │
│                                          │
│   Loop continues until the model stops  │
│   calling tools and confirms the build  │
└─────────────────────────────────────────┘
   │
   ▼
Finished site in /generated_sites/<project>/
```

Every build and every reply is logged to a local SQLite database, so the chat interface keeps a running history across sessions.

## Architecture

```
.
├── web.py                     # Flask entrypoint, route registration
├── ai_workflow/
│   └── intelligence.py        # Core agent loop: prompt → LLM → tool calls → response
├── route/
│   ├── prompt.py               # System prompt (the agent's design "constitution")
│   ├── reference.py            # Loads a reference HTML file for style grounding
│   ├── safe_path.py            # Sandboxes file writes to prevent path traversal
│   └── trim.py                 # Trims conversation history to control token usage
├── tools/
│   ├── create.py               # create_file — writes a new file
│   ├── read.py                 # read_file — reads back current file content
│   ├── edit.py                 # edit_file — targeted find/replace editing
│   └── tool.py                 # OpenAI-format tool schema definitions
├── database/
│   └── database.py             # SQLite chat memory (memoir table)
└── generated_sites/            # Output — one folder per built project
```

## Tech stack

- **Backend:** Flask (async routes)
- **LLM:** Google Gemini 2.5 Flash, via the OpenAI-compatible endpoint (`AsyncOpenAI` client pointed at `generativelanguage.googleapis.com`)
- **Agent tools:** `create_file`, `read_file`, `edit_file` — function-calling with structured JSON arguments
- **Sandboxing:** path-traversal protection so the agent can only write inside its own project folder
- **Frontend output:** HTML + Tailwind CSS (CDN) + vanilla JS — no build step required for generated sites
- **Memory:** SQLite, so the chat interface persists across restarts
- **Visual QA (in progress):** Playwright, for automated screenshot-based rendering checks

## Setup

```bash
git clone <repo>
cd owenai-website-builder
pip install flask openai python-dotenv
```

Create a `hide.env` file:
```
GEMINI_API=your_gemini_api_key_here
```

Run it:
```bash
python web.py
```
Visit `http://127.0.0.1:5009`.

## The engineering journey (a.k.a. what this project actually taught me)

This project's real value wasn't the first working build — it was debugging a real agentic system end to end:

- **Token-budget management** — hit real `413` (request too large) and `429` (rate limit) errors from provider TPM/RPD caps, and learned the difference between the two: one requires shrinking a single request, the other requires spacing requests over time.
- **Context bloat** — discovered that tool-call arguments embedded in assistant messages (not just tool results) silently accumulate in conversation history and blow up token usage if not trimmed.
- **Provider migration** — moved from Groq (fast, but a low 8K TPM free-tier cap) to Gemini (much higher throughput, different quota shape — daily request caps instead of pure per-minute token caps).
- **Function-calling failure modes** — encountered Gemini's `MALFORMED_FUNCTION_CALL` error when asking the model to generate very large content inside a single tool argument, and learned to break builds into smaller, incremental tool calls instead.
- **Modular refactor** — split a single working file into a clean multi-module architecture (`route/`, `tools/`, `ai_workflow/`), and fixed the resulting cascade of missing-import bugs one at a time — a good lesson in how Python scoping actually works across files.

## Known limitations / roadmap

- [ ] Playwright visual-QA step is defined but not yet fully wired into the tool loop
- [ ] No image generation/sourcing yet — generated sites currently lack real photography
- [ ] Currently single-model; a lightweight "critic pass" (second review call) is a planned next step for design-quality improvements
- [ ] Free-tier API quotas (daily request caps) currently limit how many builds/edits can run per day

## License

Personal/portfolio project — not yet licensed for reuse.
