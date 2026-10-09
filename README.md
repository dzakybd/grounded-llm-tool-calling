# Grounded LLM Tool Calling

Companion code for the blog post [Building a Grounded LLM Assistant: No Hallucinations About Me](https://dzakyfawwaz.web.id/en/blog/grounded-llm-assistant).

A minimal FastAPI server that shows how to use tool calling to ground an LLM assistant in structured, typed content — so it fetches facts instead of fabricating them.

## The Core Idea

Instead of stuffing a system prompt with information about you, give the model four narrow tools and let it decide which ones to call. The tools return compact, labeled text from your actual content modules. The model can only answer what the tools return.

```
User question
    ↓
Tool-calling loop (≤ 4 rounds, no streaming)
    ↓  calls get_about / get_experience / get_projects / get_publications
Final answer (streaming, tools disabled)
    ↓
Browser renders Markdown as it arrives
```

## Running It

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your OPENROUTER_API_KEY
uvicorn server:app --reload
```

Test with the included client:

```bash
python client_example.py "What stack did you use on your last project?"
```

## Key Files

| File | What it does |
|------|-------------|
| `server.py` | FastAPI app: rate limiting, tool loop, streaming |
| `tools.py` | The 4 tool handlers — replace with your real content |
| `rate_limiter.py` | Fixed-window in-memory rate limiter |
| `client_example.py` | Simple streaming client for local testing |

## Adapting for Your Own Portfolio

1. Edit `tools.py` — replace the placeholder strings with your actual bio, experience, projects, and publications.
2. Set `OPENROUTER_API_KEY` and optionally `MODEL` in `.env`.
3. Deploy behind a process manager (pm2, systemd) that keeps the single Node/Python process alive — the in-memory rate limiter resets on restart, which is fine for a personal site.

## Rate Limits

Two overlapping windows (both must pass):

- **Per IP**: 20 requests per 60 seconds
- **Per conversation**: 10 requests per 5 minutes (keyed by a `conversationId` the client generates)

Both are in-memory fixed windows. A single-process deployment is sufficient; a restart resets the counters.
