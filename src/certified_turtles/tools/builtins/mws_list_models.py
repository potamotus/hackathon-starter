from __future__ import annotations

import json
import os
from typing import Any

from certified_turtles.mws_gpt.client import DEFAULT_BASE_URL, MWSGPTClient, MWSGPTError
from certified_turtles.tools.registry import ToolSpec, register_tool


def _handle_mws_list_models(_arguments: dict[str, Any]) -> str:
    """GET /v1/models тем же ключом, что и chat/completions (серверный MWS_API_KEY)."""
    try:
        client = MWSGPTClient(base_url=os.environ.get("MWS_API_BASE", DEFAULT_BASE_URL))
        data = client.list_models()
    except ValueError as e:
        return json.dumps({"error": "mws_key_missing", "detail": str(e)}, ensure_ascii=False)
    except MWSGPTError as e:
        return json.dumps(
            {
                "error": "mws_request_failed",
                "status": e.status,
                "detail": str(e),
                "body_preview": (e.body or "")[:2000],
            },
            ensure_ascii=False,
        )
    if not isinstance(data, dict):
        return json.dumps({"raw": data}, ensure_ascii=False)
    items = data.get("data")
    if isinstance(items, list):
        slim: list[dict[str, Any]] = []
        for m in items[:500]:
            if isinstance(m, dict):
                slim.append({"id": m.get("id"), "owned_by": m.get("owned_by")})
        return json.dumps(
            {"object": data.get("object"), "data": slim, "count": len(slim)},
            ensure_ascii=False,
        )
    return json.dumps(data, ensure_ascii=False)


register_tool(
    ToolSpec(
        name="mws_list_models",
        description=(
            "Возвращает список моделей MWS GPT, доступных для текущего серверного API-ключа "
            "(GET /v1/models). Вызывай, когда пользователь просит проверить/перечислить модели, "
            "сравнить id или убедиться, что модель существует. Не пытайся делать это через "
            "`execute_python` с requests/urllib — там сеть запрещена."
        ),
        parameters={"type": "object", "properties": {}},
        handler=_handle_mws_list_models,
    )
)
