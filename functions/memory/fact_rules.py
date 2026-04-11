from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FactRule:
    name: str
    category: str
    scope: str
    keywords: tuple[str, ...] = ()
    patterns: tuple[str, ...] = ()
    critical: bool = False
    fact_kind: str = ""
    score: float = 1.0


FACT_RULES: tuple[FactRule, ...] = (
    FactRule(
        name="deadline",
        category="deadline",
        scope="project",
        keywords=("дедлайн", "срок", "deadline", "сдать", "сдача", "до"),
        patterns=(
            r"\b\d{4}-\d{2}-\d{2}\b",
            r"\b\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b",
        ),
        critical=True,
        fact_kind="deadline",
        score=2.2,
    ),
    FactRule(
        name="deliverable",
        category="project",
        scope="project",
        keywords=("deliverable", "артефакт", "результат", "сдать", "отдать", "submit", "сдаём"),
        patterns=(
            r"\b(должны|нужно|надо)\s+(сдать|отдать|подготовить)\b",
            r"\bwhat to submit\b",
        ),
        critical=True,
        fact_kind="deliverable",
        score=2.0,
    ),
    FactRule(
        name="compliance_rule",
        category="decision",
        scope="project",
        keywords=("compliance", "policy", "rule", "правило", "обязаны", "нельзя", "нужно", "требование"),
        patterns=(
            r"\b(нельзя|запрещено|обязательно|обязаны|требуется)\b",
            r"\bmust\b",
            r"\brequired\b",
        ),
        critical=True,
        fact_kind="compliance_rule",
        score=1.8,
    ),
    FactRule(
        name="required_field",
        category="project",
        scope="project",
        keywords=("обязательное поле", "обязательные поля", "required field", "required fields", "mandatory field"),
        patterns=(
            r"\bобязательн\w*\s+пол",
            r"\brequired fields?\b",
            r"\bmandatory fields?\b",
        ),
        critical=True,
        fact_kind="required_field",
        score=1.8,
    ),
    FactRule(
        name="preference",
        category="preference",
        scope="personal",
        keywords=("предпочита", "люблю", "нравит", "удобнее", "лучше", "короче"),
        patterns=(
            r"\b(i prefer|prefer)\b",
            r"\bмне удобнее\b",
            r"\bмне лучше\b",
        ),
        fact_kind="preference",
        score=1.4,
    ),
    FactRule(
        name="role",
        category="role",
        scope="personal",
        keywords=("роль", "работаю", "engineer", "developer", "designer", "manager"),
        patterns=(
            r"\bя\s+(работаю|developer|engineer|designer|manager)\b",
            r"\bi am (a|an)?\s*(developer|engineer|designer|manager)\b",
        ),
        fact_kind="role",
        score=1.4,
    ),
    FactRule(
        name="decision",
        category="decision",
        scope="project",
        keywords=("решили", "решение", "выбрали", "договорились", "approved", "accepted"),
        patterns=(r"\b(решили|выбрали|договорились)\b",),
        fact_kind="decision",
        score=1.3,
    ),
    FactRule(
        name="team",
        category="project",
        scope="team",
        keywords=("команда", "team", "мы", "наш", "наша"),
        patterns=(r"\bwe\b",),
        fact_kind="team_context",
        score=1.1,
    ),
    FactRule(
        name="project",
        category="project",
        scope="project",
        keywords=("проект", "repo", "репо", "gpthub", "feature", "задача"),
        fact_kind="project_context",
        score=1.0,
    ),
)


def infer_fact_attributes(text: str) -> dict:
    lower = (text or "").strip().lower()
    if not lower:
        return {
            "category": "project",
            "scope": "personal",
            "critical": False,
            "fact_kind": "project_context",
            "matched_rule": "",
            "score": 0.0,
        }

    scored: list[tuple[float, FactRule]] = []
    for rule in FACT_RULES:
        score = 0.0
        for keyword in rule.keywords:
            if keyword and keyword in lower:
                score += rule.score
        for pattern in rule.patterns:
            if re.search(pattern, lower, flags=re.IGNORECASE):
                score += rule.score + 0.5
        if score > 0:
            scored.append((score, rule))

    if not scored:
        return {
            "category": "project",
            "scope": "personal",
            "critical": False,
            "fact_kind": "project_context",
            "matched_rule": "",
            "score": 0.0,
        }

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_rule = scored[0]
    return {
        "category": best_rule.category,
        "scope": best_rule.scope,
        "critical": best_rule.critical,
        "fact_kind": best_rule.fact_kind or best_rule.name,
        "matched_rule": best_rule.name,
        "score": round(best_score, 3),
    }

