"""
Тесты РЕАЛЬНОЙ цепочки: пользователь сказал X → память сохранилась → в другом чате X видно в промпте.

Не моки абстракций, а проверка фактического поведения системы.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault("CT_CLAUDE_HOME", tempfile.mkdtemp(prefix="ct_cross_"))

from certified_turtles.memory_runtime.manager import ClaudeLikeMemoryRuntime
from certified_turtles.memory_runtime.storage import (
    memory_dir,
    read_body,
    read_frontmatter,
    rebuild_memory_index,
    scan_memory_headers,
    write_memory_file,
)
from certified_turtles.memory_runtime.prompting import build_memory_prompt


def _mock_client_selecting(*filenames: str) -> MagicMock:
    """Mock MWSGPTClient that returns given filenames as selected memories."""
    client = MagicMock()
    resp = {
        "choices": [{
            "message": {
                "content": json.dumps({"selected_memories": list(filenames)})
            }
        }]
    }
    client.chat_completions.return_value = resp
    return client


def _mock_client_noop() -> MagicMock:
    """Mock MWSGPTClient that returns empty selection."""
    return _mock_client_selecting()


# ────────────────────────────────────────────────────────────────
# 1. scope_id: все чаты видят одну и ту же папку памяти
# ────────────────────────────────────────────────────────────────

class TestCrossChatMemorySharing:
    """Memories written in chat A are visible in chat B's prompt."""

    def setup_method(self):
        self.scope = f"shared-scope-{os.urandom(4).hex()}"

    def test_memory_written_in_chat_a_visible_in_chat_b_prompt(self):
        """ГЛАВНЫЙ ТЕСТ: сохранили память в чате A → она появляется в промпте чата B."""
        # Чат A: extractor сохраняет "user loves pizza"
        write_memory_file(
            self.scope,
            name="User food preferences",
            description="User loves pizza",
            type_="user",
            body="The user said they love pizza. This is a stated preference.",
            filename="user-food-prefs.md",
        )

        # Чат B: новый session_id, тот же scope_id
        client = _mock_client_selecting("user-food-prefs.md")
        bundle = build_memory_prompt(
            client,
            model="test-model",
            messages=[{"role": "user", "content": "какую еду я люблю?"}],
            scope_id=self.scope,
            session_id=f"chat-b-{os.urandom(4).hex()}",
            user_query="какую еду я люблю?",
        )

        # Проверяем: содержимое памяти реально в промпте
        assert "pizza" in bundle.prompt.lower(), (
            f"Memory content not found in prompt! Prompt:\n{bundle.prompt[:500]}"
        )
        assert "user-food-prefs.md" in bundle.selected_memories

    def test_memory_index_visible_across_sessions(self):
        """MEMORY.md видна в промпте независимо от session_id."""
        write_memory_file(
            self.scope,
            name="Project setup",
            description="Project uses FastAPI + Python 3.12",
            type_="project",
            body="FastAPI backend with Python 3.12 and uv package manager.",
        )
        rebuild_memory_index(self.scope, force=True)

        # Другая сессия, client=None (plain mode)
        bundle = build_memory_prompt(
            None,
            model="m",
            messages=[{"role": "user", "content": "what stack?"}],
            scope_id=self.scope,
            session_id=f"other-{os.urandom(4).hex()}",
            user_query="what stack?",
        )

        assert "MEMORY.md" in bundle.prompt
        assert "Project setup" in bundle.prompt or "project-setup" in bundle.prompt.lower()

    def test_two_scopes_isolated(self):
        """Разные scope → разные папки памяти, нет утечки."""
        scope_a = f"scope-a-{os.urandom(4).hex()}"
        scope_b = f"scope-b-{os.urandom(4).hex()}"

        write_memory_file(scope_a, name="Secret A", description="only in A",
                          type_="user", body="this is scope A data")

        headers_a = scan_memory_headers(scope_a)
        headers_b = scan_memory_headers(scope_b)

        assert len(headers_a) == 1
        assert len(headers_b) == 0

    def test_multiple_memories_selected_in_prompt(self):
        """Несколько файлов памяти → все попадают в промпт."""
        write_memory_file(self.scope, name="Pref 1", description="Loves sushi",
                          type_="user", body="User loves sushi.", filename="pref-sushi.md")
        write_memory_file(self.scope, name="Pref 2", description="Hates mushrooms",
                          type_="user", body="User hates mushrooms.", filename="pref-mushrooms.md")

        client = _mock_client_selecting("pref-sushi.md", "pref-mushrooms.md")
        bundle = build_memory_prompt(
            client,
            model="m",
            messages=[{"role": "user", "content": "what food do I like?"}],
            scope_id=self.scope,
            session_id=f"multi-{os.urandom(4).hex()}",
            user_query="what food do I like?",
        )

        assert "sushi" in bundle.prompt.lower()
        assert "mushrooms" in bundle.prompt.lower()


# ────────────────────────────────────────────────────────────────
# 2. plain mode больше не ломает выборку памяти
# ────────────────────────────────────────────────────────────────

class TestPlainModeMemorySelection:
    """After fix: even in plain mode, relevant memories are selected."""

    def setup_method(self):
        self.scope = f"plain-scope-{os.urandom(4).hex()}"

    def test_plain_mode_still_selects_memories(self):
        """Ранее: client=None → select_relevant_memories пропускался. Теперь: client передаётся всегда."""
        write_memory_file(self.scope, name="User pref", description="Loves pizza",
                          type_="user", body="User said they love pizza.", filename="pizza.md")

        client = _mock_client_selecting("pizza.md")
        bundle = build_memory_prompt(
            client,  # was None before fix
            model="m",
            messages=[{"role": "user", "content": "что я люблю?"}],
            scope_id=self.scope,
            session_id=f"plain-{os.urandom(4).hex()}",
            user_query="что я люблю?",
        )

        assert "pizza" in bundle.prompt.lower()
        assert len(bundle.selected_memories) > 0

    def test_null_client_still_shows_index(self):
        """Даже если client=None, MEMORY.md всё равно в промпте."""
        write_memory_file(self.scope, name="Some fact", description="Important fact",
                          type_="project", body="This is important.")
        rebuild_memory_index(self.scope, force=True)

        bundle = build_memory_prompt(
            None,
            model="m",
            messages=[{"role": "user", "content": "hi"}],
            scope_id=self.scope,
            session_id=f"null-{os.urandom(4).hex()}",
            user_query="hi",
        )

        assert "MEMORY.md" in bundle.prompt
        assert "Some fact" in bundle.prompt or "some-fact" in bundle.prompt


# ────────────────────────────────────────────────────────────────
# 3. scope_id fallback: Open WebUI без project_id
# ────────────────────────────────────────────────────────────────

class TestScopeIdFallback:
    """scope_id defaults to 'default-scope', not session_id."""

    def test_no_project_id_gives_shared_scope(self):
        from certified_turtles.api.openai_proxy import _request_ids

        # Чат 1
        body1 = {"conversation_id": "chat-111"}
        sid1, scope1 = _request_ids(body1)

        # Чат 2
        body2 = {"conversation_id": "chat-222"}
        sid2, scope2 = _request_ids(body2)

        # session_id разные, scope_id ОДИНАКОВЫЙ
        assert sid1 != sid2
        assert scope1 == scope2 == "default-scope"

    def test_explicit_project_id_used(self):
        from certified_turtles.api.openai_proxy import _request_ids

        body = {"conversation_id": "chat-1", "project_id": "my-project"}
        sid, scope = _request_ids(body)
        assert scope == "my-project"

    def test_workspace_id_in_metadata_used(self):
        from certified_turtles.api.openai_proxy import _request_ids

        body = {"conversation_id": "c1", "metadata": {"workspace_id": "ws-42"}}
        sid, scope = _request_ids(body)
        assert scope == "ws-42"


# ────────────────────────────────────────────────────────────────
# 4. Full runtime E2E: prepare → after → prepare в другом чате
# ────────────────────────────────────────────────────────────────

class TestRuntimeFullCycle:
    """Симуляция полного цикла через MemoryRuntime: два чата, общий scope."""

    def setup_method(self):
        self.scope = f"cycle-scope-{os.urandom(4).hex()}"
        self.runtime = ClaudeLikeMemoryRuntime()

    def test_memory_persists_across_sessions_via_runtime(self):
        """
        Чат A: prepare + after_response.
        Симулируем что extractor записал память.
        Чат B: prepare → промпт содержит память из A.
        """
        session_a = f"sess-a-{os.urandom(4).hex()}"
        session_b = f"sess-b-{os.urandom(4).hex()}"

        # Чат A: пользователь говорит
        client = _mock_client_noop()
        msgs_a = [{"role": "user", "content": "я люблю пиццу"}]
        prepared_a = self.runtime.prepare_messages(
            client, model="m", messages=msgs_a,
            session_id=session_a, scope_id=self.scope,
        )
        final_a = [*prepared_a, {"role": "assistant", "content": "Отлично, я запомню!"}]

        # Симуляция: after_response запускает extractor, который пишет память
        # (в реальности это async subagent, мы имитируем его результат)
        write_memory_file(
            self.scope,
            name="User food preference",
            description="User loves pizza",
            type_="user",
            body="User explicitly said: 'я люблю пиццу' (I love pizza).",
            filename="user-food.md",
            source="memory_extractor",
        )

        self.runtime.after_response(
            client, model="m", prepared_messages=prepared_a,
            final_messages=final_a, session_id=session_a, scope_id=self.scope,
        )

        # Чат B: другая сессия, тот же scope
        client_b = _mock_client_selecting("user-food.md")
        msgs_b = [{"role": "user", "content": "какую еду я люблю?"}]
        prepared_b = self.runtime.prepare_messages(
            client_b, model="m", messages=msgs_b,
            session_id=session_b, scope_id=self.scope,
        )

        # Проверяем: системный промпт содержит информацию о пицце
        system_prompt = prepared_b[0]["content"]
        assert "pizza" in system_prompt.lower() or "пицц" in system_prompt.lower(), (
            f"Memory about pizza not in system prompt!\n{system_prompt[:1000]}"
        )

    def test_surfaced_memories_tracked_per_session(self):
        """surfaced_memories в meta.json привязаны к session, не к scope."""
        session_1 = f"surf-1-{os.urandom(4).hex()}"
        session_2 = f"surf-2-{os.urandom(4).hex()}"

        write_memory_file(self.scope, name="Fact", description="A fact",
                          type_="project", body="Some fact.", filename="fact.md")

        # Session 1 видит fact.md
        client = _mock_client_selecting("fact.md")
        self.runtime.prepare_messages(
            client, model="m",
            messages=[{"role": "user", "content": "tell me"}],
            session_id=session_1, scope_id=self.scope,
        )

        # Session 2 тоже должна видеть fact.md (не отфильтрована как "already surfaced")
        client2 = _mock_client_selecting("fact.md")
        bundle = build_memory_prompt(
            client2, model="m",
            messages=[{"role": "user", "content": "tell me too"}],
            scope_id=self.scope, session_id=session_2, user_query="tell me too",
        )
        assert "fact.md" in bundle.selected_memories


# ────────────────────────────────────────────────────────────────
# 5. Extractor реально пишет → память реально видна
# ────────────────────────────────────────────────────────────────

class TestExtractorWritesMemory:
    """
    Имитация: extractor subagent вызывает file_write для создания памяти.
    Проверяем что write_memory_file + build_memory_prompt работают вместе.
    """

    def setup_method(self):
        self.scope = f"extractor-{os.urandom(4).hex()}"

    def test_write_then_read_in_prompt(self):
        """write_memory_file → scan_memory_headers → select → build_prompt → содержимое видно."""
        write_memory_file(
            self.scope,
            name="Coding style",
            description="User prefers functional style",
            type_="feedback",
            body="When reviewing code, the user consistently prefers functional programming patterns over OOP.",
            filename="coding-style.md",
        )

        # Проверяем файл существует и парсится
        mem_root = memory_dir(self.scope)
        path = mem_root / "coding-style.md"
        assert path.is_file()
        fm = read_frontmatter(path)
        assert fm["name"] == "Coding style"
        assert fm["type"] == "feedback"
        body = read_body(path)
        assert "functional programming" in body

        # Проверяем: headers содержат файл
        headers = scan_memory_headers(self.scope)
        filenames = [h.filename for h in headers]
        assert "coding-style.md" in filenames

        # Проверяем: build_memory_prompt инъектирует содержимое
        client = _mock_client_selecting("coding-style.md")
        bundle = build_memory_prompt(
            client, model="m",
            messages=[{"role": "user", "content": "review my code"}],
            scope_id=self.scope, session_id=f"ex-{os.urandom(4).hex()}",
            user_query="review my code",
        )
        assert "functional programming" in bundle.prompt

    def test_overwrite_updates_content(self):
        """Обновление памяти → новое содержимое видно в промпте."""
        write_memory_file(
            self.scope, name="Fav color", description="Blue",
            type_="user", body="User likes blue.", filename="fav-color.md",
        )
        # Обновляем
        write_memory_file(
            self.scope, name="Fav color", description="Actually red",
            type_="user", body="User changed preference to red.", filename="fav-color.md",
        )

        client = _mock_client_selecting("fav-color.md")
        bundle = build_memory_prompt(
            client, model="m",
            messages=[{"role": "user", "content": "what color?"}],
            scope_id=self.scope, session_id=f"col-{os.urandom(4).hex()}",
            user_query="what color?",
        )
        assert "changed preference to red" in bundle.prompt
        assert "User likes blue" not in bundle.prompt  # old content gone

    def test_delete_removes_from_prompt(self):
        """Удалённая память не попадает в промпт."""
        from certified_turtles.memory_runtime.storage import delete_memory_file

        write_memory_file(
            self.scope, name="Temp", description="temp",
            type_="user", body="Temporary fact.", filename="temp-fact.md",
        )
        delete_memory_file(self.scope, "temp-fact.md")

        client = _mock_client_selecting("temp-fact.md")  # selector returns it, but file is gone
        bundle = build_memory_prompt(
            client, model="m",
            messages=[{"role": "user", "content": "anything?"}],
            scope_id=self.scope, session_id=f"del-{os.urandom(4).hex()}",
            user_query="anything?",
        )
        assert "Temporary fact" not in bundle.prompt


# ────────────────────────────────────────────────────────────────
# 6. Fallback selector без LLM
# ────────────────────────────────────────────────────────────────

class TestFallbackSelectorE2E:
    """Когда LLM-клиент недоступен, fallback_select по ключевым словам."""

    def setup_method(self):
        self.scope = f"fallback-{os.urandom(4).hex()}"

    def test_fallback_finds_relevant_memory(self):
        """Без LLM: fallback keyword match всё равно находит подходящую память."""
        from certified_turtles.memory_runtime.selector import fallback_select

        write_memory_file(self.scope, name="Pizza preference", description="User loves pizza margherita",
                          type_="user", body="Loves pizza.", filename="pizza.md")
        write_memory_file(self.scope, name="Work setup", description="Uses VS Code on macOS",
                          type_="project", body="VS Code.", filename="work.md")

        headers = scan_memory_headers(self.scope)
        selected = fallback_select(headers, "what pizza do I like?")
        assert "pizza.md" in selected
