from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def duckduckgo_text_search(query: str, *, max_results: int = 5) -> list[dict[str, Any]]:
    """Текстовый поиск через DuckDuckGo (без API-ключа). Возвращает список {title, href, body}."""
    from duckduckgo_search import DDGS

    capped = max(1, min(int(max_results), 10))
    results: list[dict[str, Any]] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=capped):
                results.append(
                    {
                        "title": item.get("title") or "",
                        "href": item.get("href") or "",
                        "body": (item.get("body") or "")[:2000],
                    }
                )
    except Exception:
        logger.exception("web_search failed for query=%r", query)
        raise
    return results


def format_search_results_for_llm(items: list[dict[str, Any]]) -> str:
    if not items:
        return "Поиск не дал результатов. Сформулируй запрос иначе или скажи пользователю, что данных нет."
    lines: list[str] = []
    for i, it in enumerate(items, 1):
        title = it.get("title") or "(без заголовка)"
        href = it.get("href") or ""
        body = (it.get("body") or "").strip().replace("\n", " ")
        if len(body) > 400:
            body = body[:400] + "…"
        lines.append(f"{i}. {title}\n   URL: {href}\n   {body}")
    return "\n\n".join(lines)
