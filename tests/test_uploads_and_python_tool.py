from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import certified_turtles.tools.builtins  # noqa: F401 - регистрация тулов
from certified_turtles.main import app
from certified_turtles.tools.registry import run_primitive_tool


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("UPLOADS_DIR", str(tmp_path / "up"))
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    return TestClient(app)


def test_upload_then_read_workspace_file(client):
    r = client.post("/api/v1/uploads", files={"file": ("data.csv", b"a,b\n1,2\n", "text/csv")})
    assert r.status_code == 200, r.text
    fid = r.json()["file_id"]
    raw = run_primitive_tool("read_workspace_file", {"file_id": fid})
    data = json.loads(raw)
    assert "1,2" in data["content"]


def test_execute_python_simple_stdout(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    raw = run_primitive_tool("execute_python", {"code": "print(2 + 2)"})
    data = json.loads(raw)
    assert data.get("returncode") == 0
    assert "4" in (data.get("stdout") or "")


def test_execute_python_rejects_bad_import(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    raw = run_primitive_tool("execute_python", {"code": "import os\nprint(os.name)"})
    data = json.loads(raw)
    assert data.get("error") == "validation_failed"


def test_execute_python_allows_sys(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    raw = run_primitive_tool("execute_python", {"code": "import sys\nprint(sys.version_info[0])"})
    data = json.loads(raw)
    assert data.get("returncode") == 0


def test_execute_python_rejects_attribute_open(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    raw = run_primitive_tool(
        "execute_python",
        {"code": "from pathlib import Path\nPath('/tmp/x').open('r')"},
    )
    data = json.loads(raw)
    assert data.get("error") == "validation_failed"


def test_upload_xlsx_then_workspace_file_path(client):
    r = client.post("/api/v1/uploads", files={"file": ("book.xlsx", b"not-a-real-xlsx", "application/octet-stream")})
    assert r.status_code == 200, r.text
    fid = r.json()["file_id"]
    raw = run_primitive_tool("workspace_file_path", {"file_id": fid})
    data = json.loads(raw)
    assert "absolute_path" in data
    assert data["file_id"] == fid
    assert data["suffix"] == ".xlsx"


def test_workspace_file_path_unknown_file(client):
    raw = run_primitive_tool("workspace_file_path", {"file_id": "nope.csv"})
    data = json.loads(raw)
    assert "error" in data


def test_workspace_file_path_rejects_placeholder(client):
    raw = run_primitive_tool("workspace_file_path", {"file_id": "[CT: RAG-источник ...]"})
    data = json.loads(raw)
    assert data.get("error") == "file_id_placeholder"


def test_workspace_file_path_rejects_file_id_placeholder_text(client):
    raw = run_primitive_tool("workspace_file_path", {"file_id": "file_id_из_ответа"})
    data = json.loads(raw)
    assert data.get("error") == "file_id_placeholder"


def test_execute_python_with_file_id(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    up = client.post("/api/v1/uploads", files={"file": ("data.csv", b"a,b\n1,2\n", "text/csv")})
    assert up.status_code == 200, up.text
    fid = up.json()["file_id"]
    code = (
        "import pandas as pd\n"
        "df = pd.read_csv(CT_DATA_FILE_ABSPATH, encoding='utf-8', on_bad_lines='skip')\n"
        "print(df.shape[0])\n"
    )
    raw = run_primitive_tool("execute_python", {"code": code, "file_id": fid})
    data = json.loads(raw)
    assert data.get("returncode") == 0
    assert "1" in (data.get("stdout") or "")


def test_execute_python_unescapes_literal_newlines(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    raw = run_primitive_tool("execute_python", {"code": "print(1)\\nprint(2)"})
    data = json.loads(raw)
    assert data.get("returncode") == 0
    assert "1" in (data.get("stdout") or "")
    assert "2" in (data.get("stdout") or "")


def test_execute_python_rewrites_literal_uploaded_file_id(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    up = client.post("/api/v1/uploads", files={"file": ("data.csv", b"a,b\n1,2\n", "text/csv")})
    assert up.status_code == 200, up.text
    fid = up.json()["file_id"]
    code = (
        "import pandas as pd\\n"
        f"df = pd.read_csv('{fid}', encoding='utf-8', on_bad_lines='skip')\\n"
        "print(df.iloc[0, 0])\\n"
    )
    raw = run_primitive_tool("execute_python", {"code": code})
    data = json.loads(raw)
    assert data.get("returncode") == 0
    assert "1" in (data.get("stdout") or "")


def test_execute_python_handles_multiple_file_ids_and_workspace_file_path(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GENERATED_FILES_DIR", str(tmp_path / "gen"))
    up1 = client.post("/api/v1/uploads", files={"file": ("left.csv", b"value\n10\n", "text/csv")})
    up2 = client.post("/api/v1/uploads", files={"file": ("right.csv", b"value\n20\n", "text/csv")})
    assert up1.status_code == 200, up1.text
    assert up2.status_code == 200, up2.text
    fid1 = up1.json()["file_id"]
    fid2 = up2.json()["file_id"]
    code = (
        "import pandas as pd\n"
        f"file_id = '{fid1}'\n"
        f"file_id_2 = '{fid2}'\n"
        "left_path = workspace_file_path(file_id)['absolute_path']\n"
        "right = pd.read_csv(CT_DATA_FILE_ABSPATH + file_id_2)\n"
        "left = pd.read_csv(left_path)\n"
        "print(int(left['value'].sum() + right['value'].sum()))\n"
    )
    raw = run_primitive_tool("execute_python", {"code": code, "file_id": fid1, "file_id_2": fid2})
    data = json.loads(raw)
    assert data.get("returncode") == 0, data
    assert "30" in (data.get("stdout") or "")
