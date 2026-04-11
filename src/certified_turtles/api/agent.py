from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from certified_turtles.agents.loop import run_agent_chat
from certified_turtles.mws_gpt.client import DEFAULT_BASE_URL, MWSGPTClient, MWSGPTError

router = APIRouter(tags=["agent"])


class AgentChatRequest(BaseModel):
    model: str = Field(..., description="Идентификатор модели из allowlist ключа (например mws-gpt-alpha).")
    messages: list[dict] = Field(..., description="История в формате OpenAI chat messages.")
    max_tool_rounds: int = Field(default=10, ge=1, le=40)
    temperature: float | None = None
    max_tokens: int | None = None

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("messages не должны быть пустыми")
        return v


@router.post("/agent/chat")
def agent_chat(body: AgentChatRequest) -> dict:
    try:
        client = MWSGPTClient(
            base_url=os.environ.get("MWS_API_BASE", DEFAULT_BASE_URL),
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    extra: dict = {}
    if body.temperature is not None:
        extra["temperature"] = body.temperature
    if body.max_tokens is not None:
        extra["max_tokens"] = body.max_tokens

    try:
        return run_agent_chat(
            client,
            body.model,
            body.messages,
            max_tool_rounds=body.max_tool_rounds,
            **extra,
        )
    except MWSGPTError as e:
        raise HTTPException(
            status_code=502,
            detail={"message": str(e), "status": e.status, "body": e.body},
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
