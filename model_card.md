# Applied AI System Model Card

## Models used

| Role | Model | Provider | Notes |
|------|-------|----------|-------|
| Text embedding | `text-embedding-004` | Google Gemini | Converts PDF chunks and queries into 768-dimensional vectors for similarity search |
| Relevance evaluation | `gemma-4-31b-it` | Google Gemini | Reads retrieved context and returns `relevant`, `irrelevant`, or `ambiguous` |
| Answer generation | `gemma-4-31b-it` | Google Gemini | Produces the final grounded answer from whichever context won the routing decision |
| Web search | Tavily Search API | Tavily | Returns top-3 result snippets with URLs when local documents are insufficient |

---

## Intended use

**Primary use case:** Answering questions about documents a user has uploaded locally (PDFs), with automatic fallback to live web search when those documents don't contain the answer.

**Intended users:** Students, researchers, or professionals who want to query their own documents in natural language without needing to read every page.

**Intended environment:** Local or personal deployment. The app runs on a single machine with two free-tier API keys.

---

## Out-of-scope uses

- **Not suitable for high-stakes decisions** — medical, legal, or financial advice should not rely on this system without expert review.
- **Not designed for real-time or safety-critical systems** — API latency (typically 2–5 seconds per query) makes it unsuitable for time-sensitive applications.
- **Not a substitute for primary source verification** — the system reports what its sources say; it does not independently fact-check those sources.
- **Not multilingual** — performance degrades for non-English documents and queries because the underlying models are optimized for English.

---

## System pipeline

```
User query
    │
    ▼
Retriever — embed query → FAISS nearest-neighbor search → top-3 chunks from PDFs
    │
    ▼
Evaluator — Gemini judges: relevant / irrelevant / ambiguous
    │
    ├── relevant   → Generator (local context only)
    ├── irrelevant → Web Search → Generator (web context only)
    └── ambiguous  → Web Search → Generator (local + web combined)
    │
    ▼
Final answer returned to user via Gradio chat UI
```

---

## Training data

This system does not train any models. It uses pre-trained models from Google Gemini via API. The document index is built at runtime from PDFs placed in the `data/` folder by the user — no data leaves the user's machine except as API requests to Google and Tavily.

---

## Performance and evaluation

**No formal benchmark evaluation was conducted.** System behavior was validated through:

- Manual testing across the three routing paths (relevant, irrelevant, ambiguous)
- A unit test suite (24 tests, 100% pass rate) covering all pipeline modules with mocked API calls
- Observed routing behavior: the `ambiguous` verdict fires more frequently than expected when relevant information is distributed across multiple document chunks rather than concentrated in one

**Known performance factors:**

| Factor | Effect |
|--------|--------|
| Chunk size (400 words) | Larger chunks capture more context per retrieval but dilute relevance scoring |
| Top-k retrieval (k=3) | Retrieving more chunks improves recall but increases evaluator confusion |
| Evaluator temperature (0) | Deterministic verdict reduces randomness but may be overly cautious |
| Generator temperature (0.3) | Slight creativity in phrasing while staying grounded in context |

---

## Limitations

**Document quality dependence:** The system can only be as accurate as the PDFs it indexes. Scanned PDFs with poor OCR, outdated documents, or documents written from a particular bias will produce answers that reflect those flaws.

**No contradiction resolution:** When routing is `ambiguous`, local and web context are concatenated without any mechanism to detect or resolve conflicts between the two sources.

**No source ranking:** Web results are returned in Tavily's default order. The system does not evaluate the credibility or recency of web sources before including them in the answer.

**Memory:** The FAISS index is rebuilt from scratch on every startup. No state is persisted between sessions.

**Chunk boundary artifacts:** Splitting documents into fixed-size word windows can cut sentences mid-thought. A retrieved chunk may start or end in the middle of an argument, reducing coherence.

---

## Ethical considerations and potential misuse

**Misinformation amplification:** If a user loads documents containing false or misleading claims, the system will answer based on that content and present it with the same confidence as accurate information. There is no built-in fact-checking layer.

**Sensitive content:** The system has no content moderation on inputs or outputs. Users can query sensitive topics, and the generator will respond based on whatever context it receives.

**Mitigation recommendations for deployment:**
- Add an output content filter before displaying answers to users
- Display source citations prominently so users can verify claims
- Add a disclaimer that answers should not be used as a substitute for professional advice
- Implement per-user rate limiting to prevent API abuse via the web search fallback

---

## Caveats and recommendations

- Always review answers against the cited source before acting on them
- For best results, use clean, text-based PDFs rather than scanned images
- If the system consistently routes to web search for questions you expect the document to answer, the document may have poor text extraction — try a different PDF export tool
- The system is designed for personal/educational use; a production deployment would require additional safety layers, persistent storage, and API cost management
