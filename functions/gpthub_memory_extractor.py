"""
title: GPTHub Memory Extractor
author: Certified Turtles
author_url: https://github.com/potamotus/mts-true-tech-2026-certified-turtles
version: 1.0.0
license: MIT
description: Automatically extracts facts from conversations in batches and stores them as long-term memories.
"""

import json
import math
import os
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional

import aiohttp
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

DB_PATH = "/app/backend/data/webui.db"

try:
    from memory.fact_rules import infer_fact_attributes
    from memory.judge import MemoryCandidate, MemoryJudgeDecision, build_memory_judge_prompt
    from memory.schema import ensure_layered_storage_schema
except Exception:
    def infer_fact_attributes(text: str) -> dict:
        return {
            "category": "project",
            "scope": "personal",
            "critical": False,
            "fact_kind": "project_context",
            "matched_rule": "",
            "score": 0.0,
        }

    MemoryCandidate = None
    MemoryJudgeDecision = None
    ensure_layered_storage_schema = None

    def build_memory_judge_prompt(messages, *, existing_memories=None, project_hint=""):
        existing_memories = existing_memories or []
        return (
            "Evaluate whether this conversation contains long-term memory worth storing.\n\n"
            f"Project hint: {project_hint or 'n/a'}\n\n"
            f"Conversation messages:\n{messages}\n\n"
            f"Existing relevant memories:\n{existing_memories}\n\n"
            "Return exactly one JSON object."
        )

# ── Models ──────────────────────────────────────────────────────

VALID_CATEGORIES = {"project", "preference", "contact", "decision", "deadline", "skill", "role"}
VALID_SCOPES = {"session", "personal", "project", "team"}


@dataclass
class MemoryEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    content: str = ""
    category: str = "project"
    confidence: float = 0.8
    source: str = "auto_extract"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_accessed: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    access_count: int = 0
    source_chat_id: str = ""
    scope: str = "personal"
    status: str = "active"
    superseded_by: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MemoryEntry":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})

    @classmethod
    def from_db_row(cls, row: dict) -> "MemoryEntry":
        """Create from OpenWebUI memory table row."""
        try:
            meta = json.loads(row.get("metadata", "{}"))
        except (json.JSONDecodeError, TypeError):
            meta = {}
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            content=row["content"],
            category=row.get("category", "project"),
            confidence=row.get("confidence", 0.8),
            source=row.get("source", "auto_extract"),
            created_at=row.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=row.get("updated_at", datetime.now(timezone.utc).isoformat()),
            last_accessed=row.get("last_accessed", datetime.now(timezone.utc).isoformat()),
            access_count=row.get("access_count", 0),
            source_chat_id=row.get("source_chat_id", ""),
            scope=row.get("scope", "personal"),
            status=row.get("status", "active"),
            superseded_by=row.get("superseded_by", ""),
            metadata=meta,
        )

    @property
    def days_since_created(self) -> float:
        try:
            dt = datetime.fromisoformat(self.created_at)
            return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        except (ValueError, TypeError):
            return 0

    @property
    def days_since_accessed(self) -> float:
        try:
            dt = datetime.fromisoformat(self.last_accessed)
            return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        except (ValueError, TypeError):
            return 0

    def recency_score(self) -> float:
        return math.exp(-self.days_since_created / 90)

    def importance_score(self) -> float:
        return math.log(1 + self.access_count) * math.exp(-self.days_since_accessed / 180)

    def touch(self):
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc).isoformat()


# ── Dedup ───────────────────────────────────────────────────────

class DedupChecker:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self._n = 3

    def _char_ngrams(self, text: str) -> set:
        t = text.lower().strip()
        if len(t) < self._n:
            return {t}
        return {t[i : i + self._n] for i in range(len(t) - self._n + 1)}

    def jaccard(self, a: str, b: str) -> float:
        na, nb = self._char_ngrams(a), self._char_ngrams(b)
        if not na and not nb:
            return 1.0
        if not na or not nb:
            return 0.0
        return len(na & nb) / len(na | nb)

    def find_duplicate(self, new_content: str, existing: List[MemoryEntry]) -> Optional[MemoryEntry]:
        for entry in existing:
            if self.jaccard(new_content, entry.content) >= self.threshold:
                return entry
        return None

    def find_by_normalized_fact(
        self,
        normalized_fact: str,
        scope: str,
        existing: List[MemoryEntry],
    ) -> Optional[MemoryEntry]:
        target = normalized_fact.strip().lower()
        if not target:
            return None
        active_match = None
        for entry in existing:
            candidate = str(entry.metadata.get("normalized_fact", "")).strip().lower()
            if candidate and candidate == target and entry.scope == scope:
                if entry.status == "active":
                    return entry
                if active_match is None:
                    active_match = entry
        return active_match


class ConflictResolver:
    CONTRADICTORY_PAIRS = [
        ("не ", "да"), ("нет", "да"), ("не знаю", "знаю"),
        ("отменили", "решили"), ("перенесли", "назначили"),
    ]

    def find_conflicts(self, new_fact: MemoryEntry, existing: List[MemoryEntry]) -> List[MemoryEntry]:
        conflicts = []
        for entry in existing:
            if entry.status != "active" or entry.category != new_fact.category:
                continue
            checker = DedupChecker(threshold=0.5)
            if checker.jaccard(new_fact.content, entry.content) > 0.5:
                new_lower = new_fact.content.lower()
                old_lower = entry.content.lower()
                for neg, pos in self.CONTRADICTORY_PAIRS:
                    if (neg in new_lower and pos in old_lower) or (pos in new_lower and neg in old_lower):
                        conflicts.append(entry)
                        break
        return conflicts

    def resolve(self, new_fact: MemoryEntry, conflicts: List[MemoryEntry]):
        for old in conflicts:
            old.status = "superseded"
            old.superseded_by = new_fact.id
            old.updated_at = new_fact.updated_at


# ── DB helpers ──────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_gpthub_schema():
    """Ensure personal memory stays working and layered knowledge tables exist."""
    if ensure_layered_storage_schema is not None:
        ensure_layered_storage_schema(DB_PATH)
        return

    conn = get_db()
    c = conn.cursor()
    c.execute("PRAGMA table_info(memory)")
    cols = {row["name"] for row in c.fetchall()}
    needed = {
        "category": "TEXT DEFAULT 'project'",
        "confidence": "REAL DEFAULT 0.8",
        "source": "TEXT DEFAULT 'auto_extract'",
        "last_accessed": "TEXT",
        "access_count": "INTEGER DEFAULT 0",
        "source_chat_id": "TEXT DEFAULT ''",
        "scope": "TEXT DEFAULT 'personal'",
        "status": "TEXT DEFAULT 'active'",
        "superseded_by": "TEXT DEFAULT ''",
        "metadata": "TEXT DEFAULT '{}'",
    }
    for col, dtype in needed.items():
        if col not in cols:
            c.execute(f"ALTER TABLE memory ADD COLUMN {col} {dtype}")
    conn.commit()
    conn.close()


# ── Extraction ──────────────────────────────────────────────────

TRIVIAL_PATTERNS = [
    r"привет", r"здравствуй", r"спасибо", r"пока", r"до свидания",
    r"\bok\b", r"хорошо", r"ладно", r"понятно",
    r"\bда\b", r"\bнет\b", r"угу", r"ага", r"спс",
]

EXPLICIT_TRIGGER_PATTERNS = [
    r"запомни", r"запомнить", r"remember", r"сохрани в память",
    r"добавь в память", r"запиши", r"зафиксируй",
]

FORGET_TRIGGER_PATTERNS = [
    r"забудь", r"удали из памяти", r"forget", r"delete memory", r"remove from memory",
]

SENSITIVE_PATTERNS = [
    r"\bsk-[A-Za-z0-9_-]+\b",
    r"\bghp_[A-Za-z0-9]+\b",
    r"\bgho_[A-Za-z0-9]+\b",
    r"\btoken\b",
    r"\bpassword\b",
    r"\bпарол[ья]\b",
    r"\bapi[_ -]?key\b",
    r"\bключ\b",
]

EXTRACTION_SYSTEM_PROMPT = """You are a memory extraction assistant. Analyze the conversation and extract NEW facts about the user that should be remembered long-term.

Rules:
- Extract ONLY new information not already known
- Categories: project, preference, contact, decision, deadline, skill, role
- Return a JSON array (can be empty if no new facts)
- Each fact: {"category": "...", "fact": "...", "confidence": 0.0-1.0}
- Confidence: 0.9+ for explicit statements, 0.7+ for implied, below 0.7 skip
- If no new facts, return []

Return ONLY valid JSON, no markdown, no explanations."""


def normalize_memory_fact(category: str, content: str, scope: str = "personal") -> str:
    text = re.sub(r"\s+", " ", (content or "").strip().lower())
    text = re.sub(r"^\[[a-z_]+\]\s*", "", text)

    if category == "deadline":
        subject = "general"
        if "gpthub" in text:
            subject = "gpthub"
        elif "проект" in text:
            subject = "project"
        elif "демо" in text:
            subject = "demo"
        return f"{scope}:deadline:{subject}"

    if category in {"role", "identity", "skill"}:
        return f"{scope}:{category}={text}"

    if category in {"project", "decision", "workflow", "preference", "contact"}:
        compact = re.sub(r"[^a-zа-я0-9_:= -]+", "", text)
        return f"{scope}:{category}={compact[:180]}"

    return f"{scope}:{category}={text[:180]}"


class MemoryExtractor:
    def __init__(self, valves: dict):
        self.valves = valves
        self._message_buffer: dict = {}
        self._last_extracted: dict = {}
        self._dedup = DedupChecker(threshold=0.85)
        self._conflict_resolver = ConflictResolver()
        ensure_gpthub_schema()

    def should_extract(self, user_id: str) -> bool:
        buffer = self._message_buffer.get(user_id, [])
        last = self._last_extracted.get(user_id, 0)
        now = time.time()
        return (
            len(buffer) >= self.valves.get("batch_size", 5)
            or (now - last) > self.valves.get("batch_timeout_sec", 300)
        )

    def is_explicit_trigger(self, text: str) -> bool:
        if not text:
            return False
        lower = text.lower()
        return any(re.search(p, lower) for p in EXPLICIT_TRIGGER_PATTERNS + FORGET_TRIGGER_PATTERNS)

    def is_forget_trigger(self, text: str) -> bool:
        if not text:
            return False
        lower = text.lower()
        return any(re.search(p, lower) for p in FORGET_TRIGGER_PATTERNS)

    def is_trivial(self, text: str) -> bool:
        if not text:
            return True
        return any(re.search(p, text.lower()) for p in TRIVIAL_PATTERNS)

    def contains_sensitive_data(self, text: str) -> bool:
        if not text:
            return False
        lower = text.lower()
        return any(re.search(pattern, lower) for pattern in SENSITIVE_PATTERNS)

    def buffer_message(self, user_id: str, chat_id: str, messages: list, response: dict):
        if user_id not in self._message_buffer:
            self._message_buffer[user_id] = []
        self._message_buffer[user_id].append({
            "chat_id": chat_id,
            "messages": messages[-3:],
            "response": response,
            "timestamp": time.time(),
        })

    def clear_buffer(self, user_id: str):
        self._message_buffer.pop(user_id, None)
        self._last_extracted[user_id] = time.time()

    async def extract_and_store(
        self, user_id: str, chat_id: str, messages: list, response: dict,
        user_token: str, base_url: str, force: bool = False,
    ) -> List[MemoryEntry]:
        try:
            last_user_text = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_text = str(msg.get("content", ""))
                    break

            if force:
                context_messages = messages[-10:]
            else:
                buffer = self._message_buffer.get(user_id, [])
                context_messages = []
                for item in buffer:
                    context_messages.extend(item["messages"])
                context_messages = context_messages[-10:]

            if not context_messages:
                return []

            judge = await self._judge_memory_worth(user_id, context_messages, force=force)
            if force:
                facts = self._facts_from_explicit_trigger(
                    user_id=user_id,
                    text=last_user_text,
                    judge=judge,
                )
                if not facts and not self._passes_write_policy(judge, force=force):
                    return []
            else:
                if not self._passes_write_policy(judge, force=force):
                    return []
                facts = self._facts_from_judge(judge)

            if not facts:
                if force and self.is_forget_trigger(last_user_text):
                    facts = self._facts_from_forget_trigger(user_id, last_user_text)
                else:
                    facts = await self._call_extraction_model(context_messages)

            stored = []
            for fact in facts:
                action = fact.get("action", judge.get("action", "new"))
                confidence = fact.get("confidence", 0)
                threshold = self.valves.get("confidence_threshold", 0.7)
                if confidence < threshold:
                    continue

                entry = MemoryEntry(
                    user_id=user_id,
                    content=f"[{fact['category']}] {fact['fact']}",
                    category=fact.get("category", "project"),
                    confidence=confidence,
                    source="explicit" if force else "auto_extract",
                    source_chat_id=chat_id,
                    scope=fact.get("scope", judge.get("scope", "personal")),
                    metadata={
                        "normalized_fact": (
                            fact.get("normalized_fact")
                            or judge.get("normalized_fact")
                            or normalize_memory_fact(
                                fact.get("category", "project"),
                                fact.get("fact", ""),
                                fact.get("scope", judge.get("scope", "personal")),
                            )
                        ),
                        "judge_reason": fact.get("reason", judge.get("reason", "")),
                        "judge_action": action,
                        "judge_sensitivity": judge.get("sensitivity", "low"),
                        "fact_kind": fact.get("fact_kind", ""),
                        "critical": bool(fact.get("critical", False)),
                        "matched_rule": fact.get("matched_rule", ""),
                    },
                )
                stored_entry = await self._store_with_dedup(entry, action=action)
                if stored_entry:
                    stored.append(stored_entry)

            if not force:
                self.clear_buffer(user_id)
            return stored
        except Exception:
            return []

    async def _call_extraction_model(self, messages: list) -> list:
        endpoint = self.valves.get("mws_gpt_endpoint", "https://api.gpt.mws.ru/v1")
        model = self.valves.get("extraction_model", "mws-gpt-alpha")
        api_key = self.valves.get("api_key", "")
        if not api_key:
            return []

        conversation = json.dumps(messages, ensure_ascii=False, indent=2)
        prompt = f"Conversation:\n{conversation}\n\nExtract facts as JSON array."

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{endpoint}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500,
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                content = re.sub(r"^```(?:json)?\s*", "", content.strip())
                content = re.sub(r"\s*```$", "", content.strip())
                try:
                    result = json.loads(content)
                    return result if isinstance(result, list) else []
                except json.JSONDecodeError:
                    return []

    async def _judge_memory_worth(self, user_id: str, messages: list, force: bool = False):
        last_user_text = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_text = str(msg.get("content", ""))
                break

        if self.is_trivial(last_user_text) and not force:
            return self._ignore_decision("trivial_message")

        if self.contains_sensitive_data(last_user_text):
            return self._ignore_decision("restricted_sensitive_data")

        endpoint = self.valves.get("mws_gpt_endpoint", "https://api.gpt.mws.ru/v1")
        model = self.valves.get("judge_model", self.valves.get("extraction_model", "mws-gpt-alpha"))
        api_key = self.valves.get("api_key", "")
        if not api_key:
            return self._ignore_decision("missing_api_key")

        existing_memories = self._get_existing_memories(user_id, limit=5)
        prompt = build_memory_judge_prompt(
            messages,
            existing_memories=existing_memories,
            project_hint=self._guess_project_hint(existing_memories),
        )

        system_prompt = (
            "You are MemoryJudge, a write gate for long-term memory. "
            "Return only valid JSON. Store only durable, useful, safe facts. "
            "Do not store secrets, credentials, or highly sensitive data. "
            "Actions: new, update, delete, ignore. "
            "Scopes: session, personal, project, team."
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{endpoint}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.0,
                    "max_tokens": 700,
                    "response_format": {"type": "json_object"},
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    return self._ignore_decision("judge_http_error")
                data = await resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                content = re.sub(r"^```(?:json)?\s*", "", content.strip())
                content = re.sub(r"\s*```$", "", content.strip())
                try:
                    parsed = json.loads(content)
                    return parsed if isinstance(parsed, dict) else self._ignore_decision("judge_non_object")
                except json.JSONDecodeError:
                    return self._ignore_decision("judge_bad_json")

    def _ignore_decision(self, reason: str) -> dict:
        if MemoryJudgeDecision is not None:
            return MemoryJudgeDecision.ignore(reason).to_dict()
        return {
            "should_store": False,
            "action": "ignore",
            "scope": "session",
            "category": "project",
            "confidence": 0.0,
            "stability": 0.0,
            "sensitivity": "low",
            "reason": reason,
            "normalized_fact": "",
            "memory_candidates": [],
        }

    def _passes_write_policy(self, judge: dict, force: bool = False) -> bool:
        if not judge or not judge.get("should_store"):
            return False
        if judge.get("action") == "ignore":
            return False
        if judge.get("sensitivity") == "restricted":
            return False

        confidence_threshold = self.valves.get("judge_confidence_threshold", 0.80)
        stability_threshold = self.valves.get("judge_stability_threshold", 0.75)
        if force:
            confidence_threshold = min(confidence_threshold, 0.70)
            stability_threshold = min(stability_threshold, 0.60)

        if float(judge.get("confidence", 0.0)) < confidence_threshold:
            return False
        if float(judge.get("stability", 0.0)) < stability_threshold:
            return False
        return True

    def _facts_from_judge(self, judge: dict) -> list:
        candidates = judge.get("memory_candidates", [])
        facts = []
        for candidate in candidates[:3]:
            action = candidate.get("action", "new")
            if action not in {"new", "update", "delete"}:
                continue
            facts.append(
                {
                    "category": candidate.get("category", judge.get("category", "project")),
                    "fact": candidate.get("content", "").strip(),
                    "confidence": candidate.get("confidence", judge.get("confidence", 0.0)),
                    "scope": candidate.get("scope", judge.get("scope", "personal")),
                    "action": action,
                    "normalized_fact": candidate.get("normalized_fact", judge.get("normalized_fact", "")),
                    "reason": candidate.get("reason", judge.get("reason", "")),
                }
            )
        return [fact for fact in facts if fact.get("fact")]

    def _facts_from_explicit_trigger(self, user_id: str, text: str, judge: dict) -> list:
        if self.is_forget_trigger(text):
            return self._facts_from_forget_trigger(user_id, text)

        cleaned = re.sub(r"^(запомни|запомнить|remember|сохрани в память|добавь в память|запиши|зафиксируй)\s*[:,-]?\s*", "", text.strip(), flags=re.IGNORECASE)
        inferred = infer_fact_attributes(cleaned)
        category = judge.get("category") or inferred["category"]
        scope = judge.get("scope") or inferred["scope"]
        normalized_fact = normalize_memory_fact(category, cleaned, scope)
        existing = self._get_existing_memories(user_id, limit=10)
        action = "new"
        for memory in existing:
            normalized_existing = self._extract_normalized_fact_from_memory(memory)
            if (
                memory.get("category") == category
                and memory.get("scope", "personal") == scope
                and normalized_existing == normalized_fact
            ):
                action = "update"
                break
        return [{
            "category": category,
            "fact": cleaned,
            "confidence": max(float(judge.get("confidence", 0.0) or 0.0), 0.95),
            "scope": scope,
            "action": action if judge.get("action") in {None, "", "ignore"} else judge.get("action", action),
            "normalized_fact": normalized_fact,
            "reason": "explicit_trigger_fallback",
            "fact_kind": inferred["fact_kind"],
            "critical": inferred["critical"],
            "matched_rule": inferred["matched_rule"],
        }]

    def _facts_from_forget_trigger(self, user_id: str, text: str) -> list:
        memories = self._get_existing_memories(user_id, limit=10)
        query = re.sub(r"^(забудь|удали из памяти|forget|delete memory|remove from memory)\s*[:,-]?\s*", "", text.strip(), flags=re.IGNORECASE).lower()
        best = None
        best_score = 0.0
        for memory in memories:
            content = str(memory.get("content", ""))
            score = self._text_similarity_for_forget(content, query)
            if score > best_score:
                best = memory
                best_score = score
        if not best:
            return []
        inferred = infer_fact_attributes(query)
        category = best.get("category", inferred["category"])
        scope = best.get("scope", "personal")
        return [{
            "category": category,
            "fact": best.get("content", ""),
            "confidence": 0.99,
            "scope": scope,
            "action": "delete",
            "normalized_fact": self._extract_normalized_fact_from_memory(best),
            "reason": "forget_trigger_fallback",
            "fact_kind": inferred["fact_kind"],
            "critical": inferred["critical"],
            "matched_rule": inferred["matched_rule"],
        }]

    def _infer_category(self, text: str) -> str:
        return infer_fact_attributes(text)["category"]

    def _infer_scope(self, text: str) -> str:
        return infer_fact_attributes(text)["scope"]

    def _text_similarity_for_forget(self, content: str, query: str) -> float:
        content_words = set(re.sub(r"[^a-zа-я0-9 ]+", " ", content.lower()).split())
        query_words = set(re.sub(r"[^a-zа-я0-9 ]+", " ", query.lower()).split())
        if not content_words or not query_words:
            return 0.0
        return len(content_words & query_words) / max(len(query_words), 1)

    def _extract_normalized_fact_from_memory(self, memory: dict) -> str:
        metadata = memory.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                metadata = {}
        if isinstance(metadata, dict):
            direct = metadata.get("normalized_fact")
            if direct:
                return str(direct)
            nested = metadata.get("metadata", {})
            if isinstance(nested, str):
                try:
                    nested = json.loads(nested)
                except json.JSONDecodeError:
                    nested = {}
            if isinstance(nested, dict):
                return str(nested.get("normalized_fact", ""))
        return ""

    def _get_existing_memories(self, user_id: str, limit: int = 5) -> list:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "SELECT id, content, category, scope, status, updated_at, metadata FROM memory WHERE user_id = ? AND status = 'active' ORDER BY updated_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    def _guess_project_hint(self, existing_memories: list) -> str:
        for memory in existing_memories:
            if memory.get("category") == "project":
                return memory.get("content", "")
        return ""

    def _store_with_dedup(self, entry: MemoryEntry, action: str = "new") -> Optional[MemoryEntry]:
        """Store in OpenWebUI memory table with dedup."""
        conn = get_db()
        c = conn.cursor()

        # Get existing memories for this user
        c.execute("SELECT * FROM memory WHERE user_id = ?", (entry.user_id,))
        rows = c.fetchall()
        existing = [MemoryEntry.from_db_row(dict(r)) for r in rows]
        active_same_scope = [
            item for item in existing
            if item.status == "active" and item.scope == entry.scope and item.category == entry.category
        ]

        # Check dedup
        normalized_fact = str(entry.metadata.get("normalized_fact", ""))
        exact_match = self._dedup.find_by_normalized_fact(normalized_fact, entry.scope, active_same_scope or existing)
        dup = exact_match or self._dedup.find_duplicate(entry.content, active_same_scope or existing)
        if dup:
            if action == "delete":
                c.execute(
                    "UPDATE memory SET status = ?, updated_at = ? WHERE id = ?",
                    ("deleted", entry.updated_at, dup.id)
                )
                conn.commit()
                conn.close()
                dup.status = "deleted"
                return dup
            dup.touch()
            c.execute(
                "UPDATE memory SET access_count = ?, last_accessed = ? WHERE id = ?",
                (dup.access_count, dup.last_accessed, dup.id)
            )
            if action == "update":
                c.execute(
                    "UPDATE memory SET status = ?, superseded_by = ?, updated_at = ? WHERE id = ?",
                    ("superseded", entry.id, entry.updated_at, dup.id)
                )
                conn.commit()
                conn.close()
                dup.status = "superseded"
                dup.superseded_by = entry.id
                return self._insert_entry(entry)
            conn.commit()
            conn.close()
            return dup

        if action == "delete":
            conn.close()
            return None

        # Check conflicts
        conflicts = self._conflict_resolver.find_conflicts(entry, existing)
        if conflicts:
            self._conflict_resolver.resolve(entry, conflicts)
            for conflict in conflicts:
                c.execute(
                    "UPDATE memory SET status = ?, superseded_by = ?, updated_at = ? WHERE id = ?",
                    (conflict.status, conflict.superseded_by, conflict.updated_at, conflict.id)
                )

        inserted = self._insert_entry(entry, conn=conn)
        return inserted

    def _insert_entry(self, entry: MemoryEntry, conn: sqlite3.Connection | None = None) -> Optional[MemoryEntry]:
        owns_conn = conn is None
        if conn is None:
            conn = get_db()
        c = conn.cursor()
        now_ts = int(time.time())
        c.execute(
            "INSERT INTO memory (id, user_id, content, created_at, updated_at, category, confidence, source, last_accessed, access_count, source_chat_id, scope, status, superseded_by, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                entry.id, entry.user_id, entry.content,
                now_ts, now_ts,
                entry.category, entry.confidence, entry.source,
                entry.last_accessed, entry.access_count,
                entry.source_chat_id, entry.scope, entry.status, entry.superseded_by,
                json.dumps(entry.to_dict()),
            )
        )
        conn.commit()
        if owns_conn:
            conn.close()
        return entry


# ── OpenWebUI Filter ────────────────────────────────────────────

class Filter:
    def __init__(self):
        self.type = "filter"
        self.id = "gpthub_memory_extractor"
        self.name = "GPTHub Memory Extractor"
        self.valves = {
            "confidence_threshold": 0.7,
            "batch_size": 5,
            "batch_timeout_sec": 300,
            "mws_gpt_endpoint": os.environ.get("MWS_API_BASE", "https://api.gpt.mws.ru").rstrip("/") + "/v1",
            "extraction_model": os.environ.get("MEMORY_EXTRACTION_MODEL", "mws-gpt-alpha"),
            "judge_model": os.environ.get("MEMORY_JUDGE_MODEL", os.environ.get("MEMORY_EXTRACTION_MODEL", "mws-gpt-alpha")),
            "judge_confidence_threshold": float(os.environ.get("MEMORY_JUDGE_CONFIDENCE_THRESHOLD", "0.80")),
            "judge_stability_threshold": float(os.environ.get("MEMORY_JUDGE_STABILITY_THRESHOLD", "0.75")),
            "api_key": os.environ.get("MWS_GPT_API_KEY", os.environ.get("MWS_API_KEY", "")),
        }
        self._extractor = None

    def _get_extractor(self):
        if self._extractor is None:
            self._extractor = MemoryExtractor(self.valves)
        return self._extractor

    def _get_last_user_message(self, body: dict) -> str:
        if not body:
            return ""
        messages = body.get("messages", [])
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, list):
                    parts = [p.get("text", "") for p in content if isinstance(p, dict)]
                    return " ".join(parts)
                return content
        return ""

    def _get_base_url(self) -> str:
        return os.environ.get("WEBUI_URL", "http://localhost:3000")

    async def outlet(self, body: dict = None, __user__: dict = None, __event_emitter__=None, **kwargs):
        logger.info(f"OUTLET CALLED: body_keys={list(body.keys()) if body else None}, user={__user__}, kwargs_keys={list(kwargs.keys())}")
        try:
            user = __user__ or kwargs.get("user", {})
            response = kwargs.get("response", {})
            extractor = self._get_extractor()
            user_id = user.get("id", "")
            chat_id = body.get("chat_id", "") if body else ""
            messages = body.get("messages", []) if body else []
            last_user_msg = self._get_last_user_message(body) if body else ""

            logger.info(f"OUTLET: user_id={user_id}, chat_id={chat_id}, msgs={len(messages)}, last={last_user_msg[:50] if last_user_msg else '(empty)'}")

            extractor.buffer_message(user_id, chat_id, messages, response)

            if extractor.is_explicit_trigger(last_user_msg):
                logger.info("OUTLET: explicit trigger detected")
                await extractor.extract_and_store(
                    user_id=user_id, chat_id=chat_id, messages=messages,
                    response=response, user_token=user.get("token", ""),
                    base_url=self._get_base_url(), force=True,
                )
                return response or {}

            if extractor.should_extract(user_id):
                logger.info("OUTLET: batch extraction triggered")
                await extractor.extract_and_store(
                    user_id=user_id, chat_id=chat_id, messages=messages,
                    response=response, user_token=user.get("token", ""),
                    base_url=self._get_base_url(), force=False,
                )
            else:
                logger.info(f"OUTLET: not extracting yet (buffer={len(extractor._message_buffer.get(user_id, []))}, timeout not reached)")
        except Exception as e:
            logger.error(f"OUTLET ERROR: {e}", exc_info=True)
            pass

        return response or {}
