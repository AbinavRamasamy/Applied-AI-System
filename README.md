# Applied AI System — Ask Craig (CRAG Pipeline)

A Corrective RAG (CRAG) chatbot that answers questions from local PDFs and falls back to live web search when local documents are insufficient. It matters because standard RAG systems generate confident answers even when their retrieved context is irrelevant — Ask Craig adds an AI judge that detects this and reroutes to the web, so answers are always grounded in something real.

## Original Project

> **Project name:** Music Recommender Simulation

# Current Project

## System diagram
![System diagram](assets/diagrams/system_diagram.png)

The diagram has four main components. The **Retriever** splits PDFs into overlapping text chunks, embeds them with Gemini, and stores them in a FAISS vector index for fast similarity search. The **Evaluator** asks Gemini to read the retrieved chunks and return a single verdict — `relevant`, `irrelevant`, or `ambiguous` — which controls where the answer comes from. The **Web Search** module calls Tavily when local documents aren't sufficient. The **Generator** receives whichever context won the routing decision and produces the final answer. All of this is orchestrated by `main.py`, which also ensures the PDF index is built exactly once per session.

## Screenshot
![Project Showcase](assets/project_screenshot.png)

## How it works

1. User asks a question via the Gradio chat UI.
2. The system retrieves the most relevant chunks from indexed local PDFs.
3. A Gemini model judges whether the retrieved context is `relevant`, `irrelevant`, or `ambiguous`.
4. Depending on the verdict:
   - **Relevant** → answer from local documents only.
   - **Irrelevant** → answer from Tavily web search.
   - **Ambiguous** → answer from both sources combined.

## Setup

### 1. Clone the repo and enter the directory

```bash
git clone <repo-url>
cd Applied-AI-System
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

| Key | Where to get it |
|-----|-----------------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `TAVILY_API_KEY` | [Tavily](https://app.tavily.com/) |

### 4. Add your PDFs

Place any PDF files you want to query in the `data/` folder:

```
data/
  your-document.pdf
  another-file.pdf
```

If the folder is empty the system will skip local retrieval and fall back to web search for every query.

### 5. Run the app

```bash
python app.py
```

Open the URL printed in the terminal (default: `http://127.0.0.1:7860`).

To run without the UI (terminal only):

```bash
python -m src.main
```

## Project structure

```
app.py              # Gradio web interface entry point
src/
  clients.py        # API client setup (Gemini, Tavily)
  retriever.py      # PDF loading, chunking, embedding, FAISS index
  evaluator.py      # Relevance scoring via Gemini
  generator.py      # Final answer generation via Gemini
  web_tools.py      # Tavily web search fallback
  main.py           # CRAG pipeline orchestration
data/               # Place your PDF files here
requirements.txt
.env.example        # Copy to .env and add your keys
```

## Design decisions

**Why add an evaluator instead of always using web search?**
Always trusting local documents causes hallucinations when a question falls outside them; always using the web ignores files the user explicitly uploaded. The evaluator routes intelligently at the cost of one extra API call per query.

**Why FAISS instead of a managed vector database?**
FAISS runs in-process with no setup. The trade-off is that the index is rebuilt from scratch each startup; a persistent store like Chroma would be worth it at a larger scale.

**Why Gemini for both embedding and generation?**
One provider means one API key and a smaller dependency surface. The trade-off is vendor lock-in — swapping models requires edits in multiple files.

**Why Gradio for the UI?**
Gradio's `ChatInterface` delivers a working chat UI in ~10 lines with no frontend code. The trade-off is limited styling and layout control.

**Why split into five files?**
Each module has one job and can be tested in isolation. A failing test points immediately to the broken pipeline stage.

## Running the tests

```bash
# from the project root, with your venv active
pytest tests/ -v
```

No API keys or PDF files are needed — every external call is mocked. The suite covers:

| File | What is tested |
|------|---------------|
| `tests/test_retriever.py` | Text chunking, empty-index guard, PDF indexing, corrupt-PDF skip |
| `tests/test_evaluator.py` | All three verdicts, unexpected model output, API failure fallback |
| `tests/test_generator.py` | Normal answer, source label in prompt, API failure message |
| `tests/test_web_tools.py` | Result formatting, empty results, API failure |
| `tests/test_main.py` | Empty query, relevant/irrelevant/ambiguous routing, empty-web fallback, unhandled exception |

**What worked well:** Mocking at the module level (`@patch("src.evaluator.google_client")`) made tests fast and fully deterministic — no real API calls, no flakiness, no keys required. Testing pure functions like `_chunk_text` required no mocking at all. The `conftest.py` approach of patching SDK constructors before any `src.*` import cleanly solved the problem of `clients.py` validating keys at import time.

**What was tricky:** Getting the `conftest.py` import order right took iteration — `os.environ` must be set and the SDK constructors must be patched *before* any test file imports a `src.*` module, otherwise the real clients try to initialize. Also, `sys.path` had to be explicitly set because pytest doesn't automatically treat the project root as importable.

**What isn't tested:** The Gradio UI layer is not covered — verifying the chat interface renders correctly requires a browser. End-to-end integration tests with live API calls are also absent; the mock-based unit tests verify logic but not that the APIs return usable responses in practice.

## Reflection

**Limitations and biases**
The system is only as accurate as the PDFs it indexes — outdated or biased documents produce equally skewed answers with no warning to the user.
Tavily's ranking silently favors certain sources, and the `ambiguous` path blends local and web context with no way to detect contradictions between them.
Both models also perform best in English, so multilingual queries may return noticeably weaker results.

**Potential for misuse**
Loading documents with false claims lets the system present misinformation as a confident, sourced answer.
There is also no content moderation on inputs or outputs, so users can query sensitive topics without restriction.
A deployed version should add output filtering and a disclaimer that answers need independent verification.

**What surprised me during reliability testing**
The `ambiguous` verdict activated far more often than expected — relevant information spread across multiple chunks was frequently misclassified, triggering unnecessary web searches.
This added latency and occasionally pulled in web results that contradicted the uploaded document.
It made clear that chunk size and top-k retrieval are more critical tuning parameters than they initially seemed.

**Collaboration with AI during this project**
AI helped throughout with code structure, error handling, and building the test cases.
One helpful suggestion: patch mocks at the module where a client is *used* (`@patch("src.evaluator.google_client")`), not where it's defined — otherwise the mock doesn't intercept the actual call.
One flawed suggestion: the initial python test files were missing required modules, causing every test to fail with `ModuleNotFoundError` — a reminder to always run generated code before trusting it.

## Logging

The app logs to stdout at `INFO` level. Each pipeline stage (indexing, retrieval, relevance verdict, generation) emits a log line so you can trace what happened for any given query.
