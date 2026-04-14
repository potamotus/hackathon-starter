#!/usr/bin/env python3
"""
Воркер для subprocess: читает JSON из stdin { "query": "...", "report_type": "..." }.
Пишет JSON в stdout { "ok": true, "report": "..." } или { "ok": false, "error": "..." }.

Запускайте интерпретатором из venv после scripts/bootstrap_gpt_researcher_venv.sh.
Upstream: https://github.com/assafelovic/gpt-researcher (PyPI: gpt-researcher).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

_RESULT_PREFIX = "__CT_GPTR_JSON__:"


def _normalize_openai_base_url(raw: str | None) -> str | None:
    base = (raw or "").strip().rstrip("/")
    if not base:
        return None
    # GPT Researcher / langchain-openai ожидают OpenAI-совместимый base c /v1.
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    return base


def _apply_env(llm_model: str | None) -> None:
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("MWS_API_KEY") or os.environ.get("MWS_GPT_API_KEY")
    if key and not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = key
    base = _normalize_openai_base_url(os.environ.get("OPENAI_BASE_URL") or os.environ.get("MWS_API_BASE"))
    if base:
        os.environ["OPENAI_BASE_URL"] = base
    # На OpenAI-совместимом MWS явно фиксируем модель, иначе GPT Researcher
    # использует дефолты (gpt-*), которые у провайдера могут отсутствовать.
    model = (llm_model or "").strip()
    if model:
        os.environ.setdefault("FAST_LLM", f"openai:{model}")
        os.environ.setdefault("SMART_LLM", f"openai:{model}")
        os.environ.setdefault("STRATEGIC_LLM", f"openai:{model}")
    if not os.environ.get("TAVILY_API_KEY") and not os.environ.get("RETRIEVER"):
        os.environ.setdefault("RETRIEVER", "duckduckgo")


async def _run() -> dict[str, object]:
    raw = sys.stdin.read()
    req = json.loads(raw) if raw.strip() else {}
    query = str(req.get("query") or "").strip()
    report_type = str(req.get("report_type") or "research_report").strip()
    llm_model = str(req.get("llm_model") or "").strip()
    if not query:
        return {"ok": False, "error": "empty_query"}
    _apply_env(llm_model or None)
    from gpt_researcher import GPTResearcher  # noqa: WPS433 — только внутри изолированного venv

    researcher = GPTResearcher(query=query, report_type=report_type)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return {"ok": True, "report": report if isinstance(report, str) else str(report)}


def main() -> None:
    try:
        out = asyncio.run(_run())
    except Exception as e:
        out = {"ok": False, "error": str(e)}
    # Всегда печатаем итог в отдельной строке с префиксом, чтобы раннер мог
    # надёжно вытащить JSON даже если сторонние библиотеки пишут шум в stdout.
    sys.stdout.write(_RESULT_PREFIX + json.dumps(out, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
