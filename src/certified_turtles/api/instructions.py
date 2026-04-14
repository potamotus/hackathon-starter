from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from certified_turtles.memory_runtime.events import get_event_bus
from certified_turtles.memory_runtime.storage import (
    delete_instruction_file,
    instructions_dir,
    read_body,
    read_frontmatter,
    scan_instruction_headers,
    write_instruction_file,
)

log = logging.getLogger(__name__)
router = APIRouter(tags=["instructions"])

DEFAULT_SCOPE = "default-scope"

GENERATING_PLACEHOLDER = "\u2728 \u2026"


def _generate_name_sync(body: str, model: str) -> str:
    """Call LLM to generate a categorical name for an instruction."""
    from certified_turtles.mws_gpt.client import MWSGPTClient
    try:
        client = MWSGPTClient()
        resp = client.chat_completions(
            model,
            [
                {"role": "system", "content": (
                    "Generate a short categorical title (3-7 words) for a behavioral instruction/rule. "
                    "The title should describe the RULE, not the specific content. "
                    "Examples: 'Краткость ответов', 'Formal tone in emails', 'Не использовать эмодзи'. "
                    "Reply with ONLY the title, nothing else. Use the same language as the input."
                )},
                {"role": "user", "content": f"Content: {body[:500]}"},
            ],
        )
        name = resp["choices"][0]["message"]["content"].strip().strip("\"'")
        return name[:200] if name else "Untitled"
    except Exception as e:
        log.warning("Instruction name generation failed: %s", e)
        return "Untitled"


async def _generate_name_and_update(scope_id: str, filename: str, body: str, description: str, source: str):
    """Background task: generate name via LLM, then update the file."""
    from certified_turtles.memory_runtime.manager import get_last_model
    model = get_last_model(scope_id)
    name = await asyncio.get_event_loop().run_in_executor(None, _generate_name_sync, body, model)
    try:
        write_instruction_file(
            scope_id,
            name=name,
            description=description,
            body=body,
            filename=filename,
            source=source,
        )
    except Exception as e:
        log.warning("Failed to update instruction name: %s", e)


@router.get("/instructions")
async def list_instructions(scope_id: str = Query(DEFAULT_SCOPE)) -> dict[str, Any]:
    headers = scan_instruction_headers(scope_id)
    root = instructions_dir(scope_id)
    items = []
    for h in headers:
        body = read_body(root / h.filename)
        items.append({
            "filename": h.filename,
            "name": h.name,
            "description": body or h.description,
            "source": h.source,
            "mtime": h.mtime,
            "body": body,
        })
    return {"scope_id": scope_id, "instructions": items}


class InstructionWriteRequest(BaseModel):
    description: str = Field(..., max_length=500)
    body: str = Field(..., max_length=4096)
    source: str = Field(default="user", pattern=r"^(auto|user)$")


@router.put("/instructions/{filename:path}")
async def put_instruction(
    filename: str,
    req: InstructionWriteRequest,
    scope_id: str = Query(DEFAULT_SCOPE),
) -> dict[str, Any]:
    try:
        path = write_instruction_file(
            scope_id,
            name=GENERATING_PLACEHOLDER,
            description=req.description,
            body=req.body,
            filename=filename,
            source=req.source,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    asyncio.create_task(_generate_name_and_update(scope_id, filename, req.body, req.description, req.source))
    return {"ok": True, "filename": filename, "path": str(path)}


@router.delete("/instructions/{filename:path}")
async def remove_instruction(filename: str, scope_id: str = Query(DEFAULT_SCOPE)) -> dict[str, Any]:
    deleted = delete_instruction_file(scope_id, filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="Instruction not found")
    return {"ok": True, "filename": filename}


@router.get("/instruction-events")
async def instruction_events_sse(scope_id: str = Query(DEFAULT_SCOPE)):
    bus = get_event_bus()
    q = bus.subscribe()

    async def stream():
        yield "data: {\"type\":\"connected\"}\n\n"
        try:
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30)
                    if scope_id and event.scope_id != scope_id:
                        continue
                    if event.memory_type != "instruction":
                        continue
                    yield event.to_sse()
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            bus.unsubscribe(q)

    return StreamingResponse(stream(), media_type="text/event-stream")
