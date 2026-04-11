from __future__ import annotations

from certified_turtles.tools.parent_tools import AGENT_TOOL_PREFIX, get_parent_tools, parse_agent_tool_name
from certified_turtles.tools.registry import list_primitive_tool_names


def test_primitives_registered():
    assert "web_search" in list_primitive_tool_names()


def test_parent_tools_include_primitives_and_agents():
    tools = get_parent_tools()
    names = [t["function"]["name"] for t in tools if t.get("type") == "function"]
    assert "web_search" in names
    assert f"{AGENT_TOOL_PREFIX}research" in names
    assert f"{AGENT_TOOL_PREFIX}writer" in names


def test_parse_agent_tool_name():
    assert parse_agent_tool_name(f"{AGENT_TOOL_PREFIX}research") == "research"
    assert parse_agent_tool_name("web_search") is None
    assert parse_agent_tool_name(f"{AGENT_TOOL_PREFIX}unknown") is None
