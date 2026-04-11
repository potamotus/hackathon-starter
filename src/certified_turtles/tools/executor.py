from __future__ import annotations

"""Обратная совместимость: исполнение тулов перенесено в `tools.registry`."""

from certified_turtles.tools.registry import run_primitive_tool as run_tool

__all__ = ["run_tool"]
