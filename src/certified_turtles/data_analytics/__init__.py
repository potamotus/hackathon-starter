"""Аналитика таблиц без отдельного окружения: загрузка CSV/XLSX → `workspace_file_path` + `execute_python`, под-агент `agent_data_analyst`."""

from __future__ import annotations

from certified_turtles.agents.registry import DATA_ANALYST_AGENT_ID

__all__ = ("DATA_ANALYST_AGENT_ID",)
