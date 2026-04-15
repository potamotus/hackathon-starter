"""
Классификатор задач для автоматического роутинга.

Двухуровневый: быстрые эвристики (взвешенный скоринг) → LLM только при низкой уверенности.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from certified_turtles.agent_debug_log import agent_logger
from certified_turtles.mws_gpt.model_config import CLASSIFIER_MODEL, TaskType

if TYPE_CHECKING:
    from certified_turtles.mws_gpt.client import MWSGPTClient

_cls_log = agent_logger("classifier")

# ── Взвешенные сигналы ──
# (паттерн, вес). Вес 3 = сильный сигнал, 1 = слабый.
# Паттерны проверяются через `in` для строк и `re.search` для regex.

_CODE_SIGNALS: list[tuple[str | re.Pattern, int]] = [
    # Безусловные маркеры (код в тексте)
    (re.compile(r"```"), 5),
    (re.compile(r"\bdef\s+\w+\s*\("), 5),
    (re.compile(r"\bimport\s+\w+"), 4),
    (re.compile(r"\bclass\s+\w+"), 4),
    (re.compile(r"const\s+\w+\s*="), 4),
    (re.compile(r"function\s+\w+\s*\("), 4),
    # Языки программирования
    ("python", 3), ("javascript", 3), ("typescript", 3),
    ("java ", 3), ("c++", 3), ("golang", 3), ("rust ", 3),
    ("sql", 3), ("html", 2), ("css", 2), ("react", 3),
    ("django", 3), ("fastapi", 3), ("flask", 3), ("nodejs", 3),
    # Действия с кодом
    ("код ", 2), ("code", 2), ("функци", 2), ("function", 2),
    ("алгоритм", 2), ("algorithm", 2), ("баг", 2), ("bug", 2),
    ("debug", 2), ("отладк", 2), ("рефактор", 2), ("refactor", 2),
    ("api", 2), ("endpoint", 2), ("query", 2), ("запрос к ", 1),
    ("реализуй", 2), ("implement", 2), ("парсинг", 2), ("regex", 3),
    ("массив", 1), ("array", 1), ("цикл ", 1), ("loop", 1),
    ("сортировк", 2), ("рекурси", 2), ("бинарн", 2),
]

_MATH_SIGNALS: list[tuple[str | re.Pattern, int]] = [
    # Формулы и выражения
    (re.compile(r"\d+\s*[+\-*/^]\s*\d+"), 3),
    (re.compile(r"[=≠≤≥<>]\s*\d"), 2),
    (re.compile(r"\b\d+%"), 1),
    (re.compile(r"√|∫|∑|∏|Δ|π"), 4),
    (re.compile(r"\b(sin|cos|tan|log|ln|exp)\b"), 3),
    # Ключевые слова
    ("вычисли", 3), ("calculate", 3), ("посчитай", 3), ("compute", 3),
    ("реши ", 2), ("solve", 2), ("уравнени", 3), ("equation", 3),
    ("формул", 2), ("formula", 2), ("интеграл", 3), ("производн", 3),
    ("математик", 2), ("math ", 2), ("алгебр", 3), ("геометр", 3),
    ("вероятност", 2), ("probability", 2), ("статистик", 2),
    ("матриц", 2), ("matrix", 2), ("вектор", 2),
    ("дробь", 2), ("процент", 1), ("корень", 2),
]

_KNOWLEDGE_SIGNALS: list[tuple[str | re.Pattern, int]] = [
    # Вопросительные конструкции (^ = начало — сильнее; без ^ = слабее)
    (re.compile(r"^(что такое|что значит|кто тако[йе])\b"), 4),
    (re.compile(r"^(what is|who is|what does)\b"), 4),
    (re.compile(r"^почему\b"), 3), (re.compile(r"^why\b"), 3),
    (re.compile(r"^(в чём разница|чем отличается|what.s the difference)\b"), 3),
    # Могут быть в середине предложения
    (re.compile(r"\bкак работает\b"), 3), (re.compile(r"\bhow does\b"), 3),
    (re.compile(r"\bчто такое\b"), 3), (re.compile(r"\bwhat is\b"), 3),
    # Слова-маркеры
    ("объясни", 2), ("explain", 2), ("расскажи", 2), ("tell me", 2),
    ("опиши", 1), ("describe", 1),
    ("истори", 2), ("history", 2), ("факт", 1),
    ("определени", 2), ("definition", 2),
    ("принцип", 1), ("теори", 2), ("концепци", 2),
]

_INSTRUCTION_SIGNALS: list[tuple[str | re.Pattern, int]] = [
    ("пошагово", 3), ("step by step", 3), ("по шагам", 3),
    ("инструкци", 2), ("instruction", 2), ("туториал", 2), ("tutorial", 2),
    ("строго", 2), ("strictly", 2), ("exactly", 2),
    ("по порядку", 2), ("in order", 2),
    ("как сделать", 2), ("how to", 2),
    ("гайд", 2), ("guide", 2), ("рецепт", 2),
    (re.compile(r"^\d+[\.\)]\s"), 2),  # нумерованный список
]

_IMAGE_GEN_SIGNALS: list[tuple[str | re.Pattern, int]] = [
    # Прямые запросы на генерацию
    (re.compile(r"\b(нарисуй|нарисовать|нарисуйте)\b"), 5),
    (re.compile(r"\b(сгенерируй|сгенерировать|сгенерируйте)\s.*(картинк|изображени|фото|иллюстрац|арт)"), 5),
    (re.compile(r"\b(сгенерируй|сгенерировать|сгенерируйте)\s"), 3),  # "сгенерируй котенка" без слова "картинку"
    (re.compile(r"\b(создай|создать|создайте)\s.*(картинк|изображени|фото|иллюстрац|арт|лого|постер|баннер)"), 5),
    (re.compile(r"\b(generate|create|make|draw)\s.*(image|picture|photo|illustration|art|logo|poster|banner)"), 5),
    (re.compile(r"\b(покажи|покажите)\s.*(как выглядит|как будет выглядеть)"), 4),
    # Описания для генерации
    ("нарисуй", 5), ("draw ", 3),
    ("картинк", 3), ("изображени", 3), ("фотк", 3), ("фото ", 2),
    ("иллюстрац", 2), ("illustration", 2),
    ("фотореалист", 3), ("photorealistic", 3),
    ("в стиле", 2), ("in the style of", 2),
    ("лого", 2), ("logo", 2), ("постер", 2), ("poster", 2),
    ("баннер", 2), ("banner", 2), ("обложк", 2), ("cover art", 2),
    ("аватар", 2), ("avatar", 2), ("иконк", 2), ("icon", 2),
    ("пиксельарт", 3), ("pixel art", 3),
    ("3d рендер", 3), ("3d render", 3),
]

_CHAT_SIGNALS: list[tuple[str | re.Pattern, int]] = [
    (re.compile(r"^(привет|здравствуй|добрый|хай|хей|hello|hi |hey)\b"), 3),
    (re.compile(r"^(как дела|как ты|как жизнь|how are you)\b"), 4),
    (re.compile(r"^(спасибо|thanks|thank you)\b"), 3),
    (re.compile(r"^(пока|до свидания|bye|goodbye)\b"), 4),
    ("ахах", 2), ("хах", 2), ("lol", 2), ("ок ", 2),
]

_ALL_SIGNALS: list[tuple[TaskType, list[tuple[str | re.Pattern, int]]]] = [
    (TaskType.CODE, _CODE_SIGNALS),
    (TaskType.MATH, _MATH_SIGNALS),
    (TaskType.KNOWLEDGE, _KNOWLEDGE_SIGNALS),
    (TaskType.INSTRUCTION, _INSTRUCTION_SIGNALS),
    (TaskType.IMAGE_GEN, _IMAGE_GEN_SIGNALS),
    (TaskType.CHAT, _CHAT_SIGNALS),
]

# Порог уверенности: если лучший скор < этого и сообщение длинное → LLM
_CONFIDENCE_THRESHOLD = 3
_LLM_LENGTH_THRESHOLD = 80


# ── LLM fallback prompt ──

CLASSIFIER_PROMPT = """Ты классификатор задач. Определи тип задачи пользователя.

Типы задач:
- code: написание кода, отладка, программирование
- math: математика, вычисления, уравнения, статистика
- knowledge: вопросы о фактах, объяснения, "что такое", история, наука
- instruction: пошаговые инструкции, строгое следование формату
- image: генерация изображения, нарисовать картинку, создать лого/постер/баннер
- chat: обычный разговор, приветствия, личные вопросы

Ответь ТОЛЬКО одним словом: code, math, knowledge, instruction, image или chat.

Задача пользователя:
{user_message}

Тип задачи:"""

_TASK_TYPE_MAP = {
    "code": TaskType.CODE,
    "math": TaskType.MATH,
    "knowledge": TaskType.KNOWLEDGE,
    "instruction": TaskType.INSTRUCTION,
    "image": TaskType.IMAGE_GEN,
    "chat": TaskType.CHAT,
}


# ── Scoring engine ──

@dataclass
class _ScoreResult:
    task_type: TaskType
    score: int
    runner_up_score: int  # для оценки уверенности


def _score_text(text: str) -> _ScoreResult:
    """Взвешенный скоринг по всем категориям, возвращает лучшую."""
    text_lower = text.lower()
    scores: dict[TaskType, int] = {}

    for task_type, signals in _ALL_SIGNALS:
        total = 0
        for pattern, weight in signals:
            if isinstance(pattern, re.Pattern):
                if pattern.search(text_lower):
                    total += weight
            else:
                if pattern in text_lower:
                    total += weight
        scores[task_type] = total

    # Приветствия — это шум, не задача. CHAT побеждает только если
    # ни одна другая категория не набрала >= 2 очков.
    chat_score = scores.get(TaskType.CHAT, 0)
    best_task_score = max(
        (s for t, s in scores.items() if t != TaskType.CHAT), default=0
    )
    if chat_score > 0 and best_task_score >= 2:
        scores[TaskType.CHAT] = 0

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_type, best_score = ranked[0]
    runner_up_score = ranked[1][1] if len(ranked) > 1 else 0

    return _ScoreResult(
        task_type=best_type if best_score > 0 else TaskType.CHAT,
        score=best_score,
        runner_up_score=runner_up_score,
    )


# ── Classifier ──

class TaskClassifier:
    """Двухуровневый классификатор: эвристики → LLM при низкой уверенности."""

    def __init__(self, client: "MWSGPTClient"):
        self._client = client
        self._cache: dict[str, tuple[TaskType, float]] = {}
        self._cache_ttl = 300

    def _get_cache_key(self, text: str) -> str:
        return text[:200].strip().lower()

    def _extract_user_message(self, messages: list[dict[str, Any]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content[:1000]
                if isinstance(content, list):
                    texts = []
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            texts.append(part.get("text", ""))
                    return " ".join(texts)[:1000]
        return ""

    def classify(self, messages: list[dict[str, Any]]) -> TaskType:
        user_message = self._extract_user_message(messages)
        if not user_message:
            return TaskType.CHAT

        cache_key = self._get_cache_key(user_message)
        if cache_key in self._cache:
            task_type, cached_at = self._cache[cache_key]
            if time.time() - cached_at < self._cache_ttl:
                return task_type

        result = _score_text(user_message)
        task_type = result.task_type

        confident = (
            result.score >= _CONFIDENCE_THRESHOLD
            and result.score - result.runner_up_score >= 2
        )

        _cls_log.debug(
            "Heuristic: %s (score=%d, runner_up=%d, confident=%s) — %r",
            task_type.value, result.score, result.runner_up_score,
            confident, user_message[:80],
        )

        # LLM только при низкой уверенности + достаточно длинное сообщение
        if not confident and len(user_message) > _LLM_LENGTH_THRESHOLD:
            try:
                llm_type = self._classify_with_llm(user_message)
                _cls_log.debug("LLM override: %s → %s", task_type.value, llm_type.value)
                task_type = llm_type
            except Exception:
                pass

        self._cache[cache_key] = (task_type, time.time())
        return task_type

    def _classify_with_llm(self, user_message: str) -> TaskType:
        prompt = CLASSIFIER_PROMPT.format(user_message=user_message)
        response = self._client.chat_completions(
            model=CLASSIFIER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.0,
        )
        if not response or "choices" not in response:
            return TaskType.UNKNOWN
        content = response["choices"][0].get("message", {}).get("content", "").strip().lower()
        for key, tt in _TASK_TYPE_MAP.items():
            if key in content:
                return tt
        return TaskType.UNKNOWN


# ── Public API ──

_classifier: TaskClassifier | None = None


def get_classifier(client: "MWSGPTClient") -> TaskClassifier:
    global _classifier
    if _classifier is None:
        _classifier = TaskClassifier(client)
    return _classifier


def classify_task(client: "MWSGPTClient", messages: list[dict[str, Any]]) -> TaskType:
    classifier = get_classifier(client)
    return classifier.classify(messages)
