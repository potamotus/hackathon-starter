from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

# OpenAI: имя функции ^[a-zA-Z0-9_-]+$
ToolHandler = Callable[[dict[str, Any]], str]


@dataclass(frozen=True)
class ToolSpec:
    """Регистрируемый тул для LLM: схема для API + обработчик (без HTTP к MWS)."""

    name: str
    description: str
    parameters: Mapping[str, Any]
    handler: ToolHandler

    def to_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": dict(self.parameters),
            },
        }


_TOOLS: dict[str, ToolSpec] = {}


def register_tool(spec: ToolSpec) -> None:
    """Регистрирует тул; при дубликате имени последняя регистрация перекрывает предыдущую."""
    if not spec.name or not spec.name.replace("_", "").replace("-", "").isalnum():
        raise ValueError(f"Некорректное имя тула: {spec.name!r}")
    _TOOLS[spec.name] = spec


def get_tool_spec(name: str) -> ToolSpec | None:
    return _TOOLS.get(name)


def list_primitive_tool_names() -> list[str]:
    return sorted(_TOOLS.keys())


def openai_tools_for_names(names: tuple[str, ...]) -> list[dict[str, Any]]:
    """Список `tools` для chat/completions; пустой список — вызов без tools (под-агент без примитивов)."""
    items: list[dict[str, Any]] = []
    for n in names:
        spec = _TOOLS.get(n)
        if spec:
            items.append(spec.to_openai_tool())
    return items


def run_primitive_tool(name: str, arguments: dict[str, Any]) -> str:
    spec = _TOOLS.get(name)
    if spec is None:
        return json.dumps({"error": f"Неизвестный примитивный тул: {name}"}, ensure_ascii=False)
    try:
        return spec.handler(arguments)
    except Exception as e:  # noqa: BLE001
        return json.dumps({"error": "tool_failed", "tool": name, "detail": str(e)}, ensure_ascii=False)


def openai_definitions_all_primitives() -> list[dict[str, Any]]:
    return [spec.to_openai_tool() for _, spec in sorted(_TOOLS.items())]
