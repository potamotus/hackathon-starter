from __future__ import annotations

import json
from typing import Any

from .web_search import duckduckgo_text_search, format_search_results_for_llm


def run_tool(name: str, arguments: dict[str, Any]) -> str:
    """Выполняет инструмент по имени; возвращает строку для поля `content` сообщения role=tool."""
    if name == "web_search":
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            return json.dumps({"error": "Нужен непустой строковый параметр query."}, ensure_ascii=False)
        raw_max = arguments.get("max_results", 5)
        try:
            max_results = int(raw_max)
        except (TypeError, ValueError):
            max_results = 5
        try:
            items = duckduckgo_text_search(query.strip(), max_results=max_results)
        except Exception as e:  # noqa: BLE001 — отдаём модели текст ошибки
            return json.dumps(
                {"error": "search_failed", "detail": str(e)},
                ensure_ascii=False,
            )
        return format_search_results_for_llm(items)

    return json.dumps({"error": f"Неизвестный инструмент: {name}"}, ensure_ascii=False)
