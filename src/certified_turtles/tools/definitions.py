from __future__ import annotations

from typing import Any

# OpenAI-совместимый список `tools` для chat/completions.
DEFAULT_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Поиск актуальной информации в интернете (заголовки, ссылки, краткие сниппеты). "
                "Используй для фактов после 2024 года, курсов валют, новостей, документации библиотек."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос на языке запроса пользователя или на английском.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Сколько результатов вернуть (1–10).",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
]
