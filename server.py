import json
import os
from collections.abc import Generator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

from rate_limiter import RateLimiter
from tools import get_about, get_experience, get_projects, get_publications

load_dotenv()

app = FastAPI()

# ── Rate limiters ──────────────────────────────────────────────────────────────
ip_limiter = RateLimiter(max_requests=20, window_seconds=60)
conv_limiter = RateLimiter(max_requests=10, window_seconds=300)

# ── OpenAI-compatible client (OpenRouter) ──────────────────────────────────────
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
MODEL = os.getenv("MODEL", "anthropic/claude-3-5-haiku")

# ── Tool registry ──────────────────────────────────────────────────────────────
TOOL_HANDLERS: dict[str, object] = {
    "get_about": get_about,
    "get_experience": get_experience,
    "get_projects": get_projects,
    "get_publications": get_publications,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_about",
            "description": (
                "Returns the person's bio, current role, positioning, "
                "domain expertise, and contact preferences."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_experience",
            "description": (
                "Returns the full work history and education, with dates, "
                "locations, highlights, and skills used."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_projects",
            "description": (
                "Returns project case studies with problem statement, "
                "approach, tech stack, and measurable impact."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_publications",
            "description": (
                "Returns peer-reviewed papers, conference presentations, "
                "and research impact metrics (citations, h-index)."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

SYSTEM_PROMPT = """\
You are a portfolio assistant. Your job is to answer questions about the person \
whose portfolio this is.

Rules:
1. Before answering any factual question, call the relevant tool(s).
2. Never fabricate facts, dates, employers, titles, or numbers beyond what the \
tools return.
3. If the tools don't contain the answer, say so plainly instead of guessing.
4. Only answer questions about this person. Politely decline anything unrelated.
5. Match the visitor's language (English or Indonesian).
6. Keep answers concise and friendly.
"""


def run_tool(name: str) -> str:
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return f"Unknown tool: {name}"
    return handler()  # type: ignore[operator]


# ── Request / response models ──────────────────────────────────────────────────
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    conversationId: str = "default"


# ── Chat endpoint ──────────────────────────────────────────────────────────────
@app.post("/api/chat")
async def chat(request: Request, body: ChatRequest) -> StreamingResponse:
    ip = request.client.host if request.client else "unknown"

    # Rate limiting
    ip_ok, ip_retry = ip_limiter.is_allowed(ip)
    if not ip_ok:
        raise HTTPException(
            status_code=429,
            detail={"error": "Too many requests. Try again shortly.", "retryAfter": ip_retry},
        )
    conv_ok, conv_retry = conv_limiter.is_allowed(body.conversationId)
    if not conv_ok:
        raise HTTPException(
            status_code=429,
            detail={"error": "Conversation limit reached. Please wait.", "retryAfter": conv_retry},
        )

    # Input validation
    if not body.messages:
        raise HTTPException(status_code=400, detail={"error": "messages is empty"})
    if len(body.messages) > 40:
        raise HTTPException(status_code=400, detail={"error": "Too many messages in history"})
    last_message = body.messages[-1].content
    if len(last_message) > 1000:
        raise HTTPException(status_code=400, detail={"error": "Message too long (max 1000 chars)"})

    # Build conversation
    conv: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    conv += [{"role": m.role, "content": m.content} for m in body.messages]

    try:
        # Tool-calling loop (no streaming, max 4 rounds)
        for _ in range(4):
            resp = client.chat.completions.create(
                model=MODEL,
                messages=conv,
                tools=TOOLS,
                tool_choice="auto",
            )
            msg = resp.choices[0].message
            if not msg.tool_calls:
                break
            # Append assistant turn with tool calls
            conv.append(msg.model_dump(exclude_unset=True))
            # Run each tool and append its result
            for tc in msg.tool_calls:
                result = run_tool(tc.function.name)
                conv.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        # Stream the final answer (tools disabled)
        def generate() -> Generator[str, None, None]:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=conv,
                stream=True,
                max_tokens=800,
            )
            has_content = False
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    has_content = True
                    yield json.dumps({"delta": delta}) + "\n"
            if not has_content:
                yield json.dumps({"delta": "I don't have information about that."}) + "\n"
            yield json.dumps({"done": True}) + "\n"

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    except HTTPException:
        raise
    except Exception:
        return JSONResponse(status_code=500, content={"error": "internal error"})
