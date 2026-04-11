from __future__ import annotations

from fastapi import FastAPI

from certified_turtles.api.agent import router as agent_router

app = FastAPI(
    title="Certified Turtles / GPTHub API",
    version="0.2.0",
    description="MWS GPT, агент с tool calling (в т.ч. web_search), точка для GPTHub.",
)

app.include_router(agent_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
