from __future__ import annotations

# Побочный эффект: регистрация встроенных тулов до сборки каталога родителя.
from . import builtins as _builtins  # noqa: F401
from .parent_tools import get_parent_tools
from .registry import ToolSpec, register_tool, run_primitive_tool

# Совместимость: старый импорт `run_tool`
run_tool = run_primitive_tool

DEFAULT_TOOLS = get_parent_tools()

__all__ = [
    "DEFAULT_TOOLS",
    "ToolSpec",
    "get_parent_tools",
    "register_tool",
    "run_primitive_tool",
    "run_tool",
]
