from __future__ import annotations

import copy
import json
import logging
from typing import Any

from certified_turtles.mws_gpt.client import MWSGPTClient
from certified_turtles.tools import DEFAULT_TOOLS, run_tool

logger = logging.getLogger(__name__)


def _first_choice(data: dict[str, Any]) -> dict[str, Any]:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("Ответ chat/completions без choices")
    ch0 = choices[0]
    if not isinstance(ch0, dict):
        raise ValueError("choices[0] не объект")
    return ch0


def _choice_message(choice: dict[str, Any]) -> dict[str, Any]:
    msg = choice.get("message")
    if not isinstance(msg, dict):
        raise ValueError("В ответе нет message")
    return msg


def run_agent_chat(
    client: MWSGPTClient,
    model: str,
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | dict[str, Any] | None = "auto",
    max_tool_rounds: int = 10,
    **chat_kwargs: Any,
) -> dict[str, Any]:
    """
    Цикл агента: вызовы chat/completions с `tools`, исполнение tool_calls, повтор до ответа без инструментов
    или исчерпания лимита раундов (число HTTP-запросов к chat/completions).
    """
    work = copy.deepcopy(messages)
    tool_list = DEFAULT_TOOLS if tools is None else tools
    last_raw: dict[str, Any] | None = None
    rounds = 0

    while rounds < max_tool_rounds:
        rounds += 1
        extra = dict(chat_kwargs)
        if tool_choice is not None:
            extra["tool_choice"] = tool_choice
        logger.debug("agent chat round %s messages=%s", rounds, len(work))
        last_raw = client.chat_completions(model, work, tools=tool_list, **extra)
        choice = _first_choice(last_raw)
        msg = _choice_message(choice)
        work.append(copy.deepcopy(msg))

        tcalls = msg.get("tool_calls") or []
        if not tcalls:
            return {
                "messages": work,
                "completion": last_raw,
                "tool_rounds_used": rounds,
                "truncated": False,
            }

        for tc in tcalls:
            if not isinstance(tc, dict):
                continue
            fn = tc.get("function")
            if not isinstance(fn, dict):
                continue
            name = str(fn.get("name") or "")
            raw_args = fn.get("arguments")
            if isinstance(raw_args, str):
                try:
                    args: Any = json.loads(raw_args or "{}")
                except json.JSONDecodeError:
                    args = {"_raw_arguments": (raw_args or "")[:2000]}
            elif isinstance(raw_args, dict):
                args = raw_args
            else:
                args = {}
            if not isinstance(args, dict):
                args = {}
            tid = str(tc.get("id") or "")
            content = run_tool(name, args)
            work.append({"role": "tool", "tool_call_id": tid, "content": content})

    return {
        "messages": work,
        "completion": last_raw,
        "tool_rounds_used": rounds,
        "truncated": True,
    }
