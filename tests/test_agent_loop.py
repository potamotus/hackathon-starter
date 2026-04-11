from __future__ import annotations

import copy

from certified_turtles.agents.loop import run_agent_chat
from certified_turtles.tools.registry import openai_tools_for_names


class FakeMWSClient:
    def __init__(self, responses: list[dict]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def chat_completions(self, model: str, messages: list, **kwargs):
        self.calls.append(
            {
                "model": model,
                "n_msg": len(messages),
                "messages": copy.deepcopy(messages),
                "has_tools": "tools" in kwargs,
            }
        )
        if not self._responses:
            raise RuntimeError("unexpected extra chat_completions call")
        return self._responses.pop(0)


def test_agent_finishes_after_tool_round(monkeypatch):
    monkeypatch.setattr("certified_turtles.agents.loop.run_primitive_tool", lambda name, args: "MOCK_RESULT")
    r1 = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "web_search", "arguments": '{"query": "x"}'},
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ]
    }
    r2 = {
        "choices": [
            {
                "message": {"role": "assistant", "content": "Финал", "tool_calls": None},
                "finish_reason": "stop",
            }
        ]
    }
    fake = FakeMWSClient([r1, r2])
    out = run_agent_chat(fake, "mws-gpt-alpha", [{"role": "user", "content": "hi"}], max_tool_rounds=5)
    assert out["truncated"] is False
    assert out["tool_rounds_used"] == 2
    assert fake.calls[0]["has_tools"] is True
    roles = [m["role"] for m in out["messages"]]
    assert roles == ["system", "user", "assistant", "tool", "assistant"]


def test_agent_truncates_when_rounds_exhausted(monkeypatch):
    monkeypatch.setattr("certified_turtles.agents.loop.run_primitive_tool", lambda n, a: "x")
    r_tool = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "c",
                            "type": "function",
                            "function": {"name": "web_search", "arguments": "{}"},
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ]
    }
    fake = FakeMWSClient([r_tool])
    out = run_agent_chat(fake, "m", [{"role": "user", "content": "hi"}], max_tool_rounds=1)
    assert out["truncated"] is True
    assert out["tool_rounds_used"] == 1


def test_execute_python_guidance_appended_to_existing_system(monkeypatch):
    monkeypatch.setattr("certified_turtles.agents.loop.run_primitive_tool", lambda n, a: "x")
    final = {"choices": [{"message": {"role": "assistant", "content": "ok"}}]}
    fake = FakeMWSClient([final])
    tools = openai_tools_for_names(("execute_python",))
    run_agent_chat(
        fake,
        "m",
        [{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "hi"}],
        tools=tools,
        max_tool_rounds=1,
    )
    sent = fake.calls[0]["messages"]
    assert sent[0]["role"] == "system"
    assert "You are helpful." in sent[0]["content"]
    assert "execute_python" in sent[0]["content"]


def test_tool_policy_without_execute_python(monkeypatch):
    monkeypatch.setattr("certified_turtles.agents.loop.run_primitive_tool", lambda n, a: "x")
    final = {"choices": [{"message": {"role": "assistant", "content": "ok"}}]}
    fake = FakeMWSClient([final])
    tools = openai_tools_for_names(("web_search",))
    run_agent_chat(fake, "m", [{"role": "user", "content": "hi"}], tools=tools, max_tool_rounds=1)
    sent = fake.calls[0]["messages"]
    assert len(sent) == 2
    assert sent[0]["role"] == "system"
    assert "tool_calls" in sent[0]["content"]
    assert "plt.savefig" not in sent[0]["content"]
