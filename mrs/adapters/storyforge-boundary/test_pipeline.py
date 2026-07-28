"""Pipeline execute tests — mocked subprocess + optional live smoke skip.

Status: **enforced** for mocked path; live Node smoke is optional.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

_DIR = Path(__file__).resolve().parent
import sys

if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from execute import (  # noqa: E402
    ExecuteError,
    execute_proton_raster,
    execute_scene_spec,
    sha256_bytes,
)
from route import route_render_request  # noqa: E402

FIXTURE_EXEC = _DIR / "fixtures" / "sample-render-request-executable.json"
FIXTURE = _DIR / "fixtures" / "sample-render-request.json"


def test_non_execute_proton_remains_skeleton():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["payload"]["route"] = "proton-raster"
    result = route_render_request(data, execute=False)
    assert result["status"] == "ok"
    assert result["mapping"]["statusTag"] == "skeleton"
    assert result["mapping"]["execute"] is False


def test_execute_scene_spec_mocked(tmp_path, monkeypatch):
    data = json.loads(FIXTURE_EXEC.read_text(encoding="utf-8"))
    png = tmp_path / "out.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
    prov = tmp_path / "out.provenance.json"

    def fake_run(argv, **kwargs):
        # Last --output / --provenance from argv
        out = None
        provenance = None
        for i, a in enumerate(argv):
            if a == "--output" and i + 1 < len(argv):
                out = Path(argv[i + 1])
            if a == "--provenance" and i + 1 < len(argv):
                provenance = Path(argv[i + 1])
        assert out is not None
        out.write_bytes(png.read_bytes())
        if provenance:
            provenance.write_text(
                json.dumps({"sha256": sha256_bytes(png.read_bytes())}),
                encoding="utf-8",
            )
        return subprocess.CompletedProcess(argv, 0, stdout="{}", stderr="")

    monkeypatch.setenv("SCENE_SPEC_SCRIPT_PATH", str(tmp_path / "render-scene.mjs"))
    (tmp_path / "render-scene.mjs").write_text("// stub\n", encoding="utf-8")
    monkeypatch.setenv("RT4D_NODE_PATH", str(tmp_path / "node.exe"))
    (tmp_path / "node.exe").write_text("stub", encoding="utf-8")

    deep = execute_scene_spec(data, out_dir=tmp_path, run_fn=fake_run)
    assert deep["statusTag"] == "partial"
    assert deep["artifacts"][0]["role"] == "beauty-png"
    assert len(deep["hashes"]["pngSha256"]) == 64

    result = route_render_request(data, execute=True, out_dir=tmp_path)
    # Re-run with same fake via monkeypatch of execute._run
    import execute as ex

    monkeypatch.setattr(ex, "_run", fake_run)
    result = route_render_request(data, execute=True, out_dir=tmp_path)
    assert result["status"] == "ok"
    assert result["artifacts"]
    assert result["mapping"]["hashes"]["pngSha256"]


def test_execute_proton_mocked(tmp_path, monkeypatch):
    data = json.loads(FIXTURE_EXEC.read_text(encoding="utf-8"))
    data["payload"]["route"] = "proton-raster"

    def fake_run(argv, **kwargs):
        out = None
        for i, a in enumerate(argv):
            if a == "--output" and i + 1 < len(argv):
                out = Path(argv[i + 1])
        assert out is not None
        out.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x11" * 16)
        return subprocess.CompletedProcess(argv, 0, stdout="{}", stderr="")

    monkeypatch.setenv(
        "PROTON_PIPELINE_SCRIPT", str(tmp_path / "run_proton_pipeline.mjs")
    )
    (tmp_path / "run_proton_pipeline.mjs").write_text("// stub\n", encoding="utf-8")
    monkeypatch.setenv("RT4D_NODE_PATH", str(tmp_path / "node.exe"))
    (tmp_path / "node.exe").write_text("stub", encoding="utf-8")

    deep = execute_proton_raster(data, out_dir=tmp_path, run_fn=fake_run)
    assert deep["artifacts"][0]["sha256"]
    assert deep["mappedTo"].endswith("run_proton_pipeline.mjs")


def test_execute_missing_script_errors(tmp_path, monkeypatch):
    data = json.loads(FIXTURE_EXEC.read_text(encoding="utf-8"))
    monkeypatch.delenv("SCENE_SPEC_SCRIPT_PATH", raising=False)
    monkeypatch.setenv("SCENE_SPEC_SCRIPT_PATH", str(tmp_path / "missing.mjs"))
    monkeypatch.setenv("RT4D_NODE_PATH", str(tmp_path / "node.exe"))
    (tmp_path / "node.exe").write_text("stub", encoding="utf-8")
    with pytest.raises(ExecuteError, match="not found"):
        execute_scene_spec(data, out_dir=tmp_path)


def test_route_execute_maps_errors(tmp_path, monkeypatch):
    data = json.loads(FIXTURE_EXEC.read_text(encoding="utf-8"))
    monkeypatch.setenv("SCENE_SPEC_SCRIPT_PATH", str(tmp_path / "missing.mjs"))
    monkeypatch.setenv("RT4D_NODE_PATH", str(tmp_path / "node.exe"))
    (tmp_path / "node.exe").write_text("stub", encoding="utf-8")
    result = route_render_request(data, execute=True, out_dir=tmp_path)
    assert result["status"] == "error"
    assert result["error"]["code"] == "execute_failed"


def test_new_modules_have_no_storyforge_imports():
    for name in (
        "execute.py",
        "paths.py",
        "run_pipeline.py",
        "smoke_pipeline.py",
        "route.py",
        "validate_request.py",
    ):
        text = (_DIR / name).read_text(encoding="utf-8")
        assert "import story_forge" not in text
        assert "from story_forge" not in text
        assert "import storyforge" not in text
        assert "from storyforge" not in text
