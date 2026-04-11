from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


MEMORY_ACTIONS = {"new", "update", "delete", "ignore"}
MEMORY_SCOPES = {"session", "personal", "project", "team"}
MEMORY_SENSITIVITY = {"low", "medium", "high", "restricted"}
MEMORY_CATEGORIES = {
    "project",
    "preference",
    "contact",
    "decision",
    "deadline",
    "skill",
    "role",
    "identity",
    "workflow",
}


MEMORY_JUDGE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "should_store",
        "action",
        "scope",
        "category",
        "confidence",
        "stability",
        "sensitivity",
        "reason",
        "normalized_fact",
        "memory_candidates",
    ],
    "properties": {
        "should_store": {"type": "boolean"},
        "action": {"type": "string", "enum": sorted(MEMORY_ACTIONS)},
        "scope": {"type": "string", "enum": sorted(MEMORY_SCOPES)},
        "category": {"type": "string", "enum": sorted(MEMORY_CATEGORIES)},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "stability": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "sensitivity": {"type": "string", "enum": sorted(MEMORY_SENSITIVITY)},
        "reason": {"type": "string", "minLength": 1, "maxLength": 200},
        "normalized_fact": {"type": "string", "maxLength": 500},
        "memory_candidates": {
            "type": "array",
            "maxItems": 3,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "content",
                    "action",
                    "category",
                    "scope",
                    "confidence",
                    "stability",
                ],
                "properties": {
                    "content": {"type": "string", "minLength": 1, "maxLength": 500},
                    "action": {"type": "string", "enum": ["new", "update", "delete"]},
                    "category": {"type": "string", "enum": sorted(MEMORY_CATEGORIES)},
                    "scope": {"type": "string", "enum": sorted(MEMORY_SCOPES)},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "stability": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "normalized_fact": {"type": "string", "maxLength": 500},
                    "existing_memory_hint": {"type": "string", "maxLength": 500},
                    "reason": {"type": "string", "maxLength": 200},
                },
            },
        },
    },
}


MEMORY_JUDGE_SYSTEM_PROMPT = """You are MemoryJudge, a write gate for long-term memory.

Your job is NOT to answer the user. Your only job is to decide whether new
conversation content is worth storing as long-term memory.

Return only valid JSON matching the provided schema.

Store only durable, useful facts that improve future personalization or task
continuity. Prefer precision over recall.

Good memory candidates:
- stable user preferences
- user role / identity / responsibilities
- long-lived project context
- confirmed deadlines and commitments
- recurring workflows or habits
- durable contacts and relationships
- decisions that were clearly made

Do NOT store:
- greetings, thanks, acknowledgements, filler
- one-off requests and transient task state
- speculative or uncertain statements
- assistant guesses or assumptions
- chain-of-thought or hidden reasoning
- secrets, credentials, financial IDs, passwords, tokens
- highly sensitive personal data unless the user explicitly asks to remember it

Interpret actions as:
- new: create a fresh memory
- update: replace or supersede an existing memory
- delete: remove/forget a previously stored memory
- ignore: do not write anything

Scope rules:
- session: useful only for the current or recent conversation
- personal: durable facts about one user
- project: durable facts tied to a specific ongoing project
- team: shared team-level knowledge or decisions

Sensitivity rules:
- low: safe personalization data
- medium: potentially private but usually acceptable
- high: sensitive personal or business data
- restricted: never store automatically

If the content is not clearly durable, set should_store=false and action=ignore.
If the content contradicts an existing memory, prefer update instead of new.
If the user explicitly asks to remember or forget something, honor that intent
unless it is restricted data.
"""


@dataclass
class MemoryCandidate:
    content: str
    action: str
    category: str
    scope: str
    confidence: float
    stability: float
    normalized_fact: str = ""
    existing_memory_hint: str = ""
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MemoryJudgeDecision:
    should_store: bool
    action: str
    scope: str
    category: str
    confidence: float
    stability: float
    sensitivity: str
    reason: str
    normalized_fact: str = ""
    memory_candidates: list[MemoryCandidate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["memory_candidates"] = [candidate.to_dict() for candidate in self.memory_candidates]
        return data

    @classmethod
    def ignore(cls, reason: str) -> "MemoryJudgeDecision":
        return cls(
            should_store=False,
            action="ignore",
            scope="session",
            category="project",
            confidence=0.0,
            stability=0.0,
            sensitivity="low",
            reason=reason,
            normalized_fact="",
            memory_candidates=[],
        )


def build_memory_judge_prompt(
    messages: list[dict[str, Any]],
    *,
    existing_memories: list[dict[str, Any]] | None = None,
    project_hint: str = "",
) -> str:
    existing_memories = existing_memories or []

    return (
        "Evaluate whether this conversation contains long-term memory worth storing.\n\n"
        f"Project hint: {project_hint or 'n/a'}\n\n"
        f"Conversation messages:\n{messages}\n\n"
        f"Existing relevant memories:\n{existing_memories}\n\n"
        "Return exactly one JSON object that matches the schema."
    )
