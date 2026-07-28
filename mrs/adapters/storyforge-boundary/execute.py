"""Deep execution for validated RenderRequest routes.

Invokes existing MRS Node CLIs (render-scene, proton pipeline, engine3d still,
worlddocument-rt4d). Does **not** implement StoryForge PromptComposer.

Status: **partial** — scene-spec and proton paths exercised by tests/smoke;
engine3d / rt4d best-effort with honest refuse when scripts missing.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from paths import (
    default_output_dir,
    engine3d_still_script,
    find_node,
    proton_pipeline_script,
    render_scene_script,
    worlddocument_rt4d_script,
)


class ExecuteError(RuntimeError):
    """Deep route failed (missing script, subprocess error, bad output)."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def _run(
    argv: list[str],
    *,
    timeout: float | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    to = timeout
    if to is None:
        to = float(os.environ.get("MRS_RENDER_TIMEOUT_SECONDS", "120"))
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=to,
        cwd=str(cwd) if cwd else None,
        check=False,
    )


def _ensure_node() -> str:
    node = find_node()
    if not node:
        raise ExecuteError("node binary not found (set RT4D_NODE_PATH)")
    return node


def execute_scene_spec(
    req: dict[str, Any],
    *,
    out_dir: Path | None = None,
    run_fn: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """SceneSpecification → render-scene.mjs → PNG + provenance hashes."""
    spec = req["payload"].get("sceneSpecification")
    if not isinstance(spec, dict):
        raise ExecuteError("scene-spec route requires payload.sceneSpecification")

    # Normalize minimal fixtures into SceneSpecification shape
    spec_out = dict(spec)
    if "kind" not in spec_out:
        spec_out["kind"] = "SceneSpecification"
    if "schemaVersion" not in spec_out:
        spec_out["schemaVersion"] = "1.0"
    if "id" not in spec_out:
        spec_out["id"] = req.get("requestId", "render-request-scene")

    render = req["payload"]["render"]
    width = int(render["width"])
    height = int(render["height"])
    samples = int(render.get("samples") or 2)
    max_depth = int(render.get("maxDepth") or 3)
    seed = render.get("seed")
    if seed is None:
        seed = 42

    script = render_scene_script()
    if script is None:
        raise ExecuteError("render-scene.mjs not found (set SCENE_SPEC_SCRIPT_PATH)")

    out_root = out_dir or default_output_dir()
    out_root.mkdir(parents=True, exist_ok=True)
    req_id = req["requestId"]
    png_path = out_root / f"{req_id}-scene-spec.png"
    prov_path = out_root / f"{req_id}-scene-spec.provenance.json"
    spec_path = out_root / f"{req_id}-scene-spec.json"

    # Clamp for smoke-friendly defaults when quality=draft
    if render.get("quality", "draft") == "draft":
        width = min(width, 128)
        height = min(height, 96)
        samples = min(samples, 2)
        max_depth = min(max_depth, 3)

    # Merge output into spec so CLI uses request dims
    output = dict(spec_out.get("output") or {})
    output.update(
        {
            "width": width,
            "height": height,
            "samples": samples,
            "maxDepth": max_depth,
            "seed": int(seed),
        }
    )
    spec_out["output"] = output
    spec_path.write_text(json.dumps(spec_out), encoding="utf-8")

    node = _ensure_node()
    argv = [
        node,
        str(script),
        "--",
        "--spec",
        str(spec_path),
        "--width",
        str(width),
        "--height",
        str(height),
        "--samples",
        str(samples),
        "--output",
        str(png_path),
        "--provenance",
        str(prov_path),
    ]
    runner = run_fn or _run
    proc = runner(argv, cwd=script.parent)
    if proc.returncode != 0:
        raise ExecuteError(
            f"render-scene failed ({proc.returncode}): {proc.stderr[-2000:]}"
        )
    if not png_path.is_file():
        raise ExecuteError(f"render-scene did not write PNG: {png_path}")

    png_bytes = png_path.read_bytes()
    png_hash = sha256_bytes(png_bytes)
    prov: dict[str, Any] = {}
    if prov_path.is_file():
        try:
            prov = json.loads(prov_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prov = {}
    if prov.get("sha256") and prov["sha256"] != png_hash:
        # Prefer file hash as artifact truth
        pass

    return {
        "sceneSpecification": spec_out,
        "artifacts": [
            {
                "role": "beauty-png",
                "uri": str(png_path.as_posix()),
                "sha256": png_hash,
                "mediaType": "image/png",
            }
        ],
        "hashes": {
            "requestSha256": sha256_json(req),
            "sceneSpecSha256": sha256_json(spec_out),
            "pngSha256": png_hash,
            "promptSpecHash": (req.get("provenance") or {}).get("promptSpecHash"),
            "renderIntentHash": (req.get("provenance") or {}).get("renderIntentHash"),
        },
        "cliProvenance": prov,
        "mappedTo": "render-scene.mjs (SceneSpecification → RT4D still)",
        "statusTag": "partial",
    }


def execute_proton_raster(
    req: dict[str, Any],
    *,
    out_dir: Path | None = None,
    run_fn: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """Proton soft-splat via run_proton_pipeline.mjs (scene-spec or demo)."""
    script = proton_pipeline_script()
    if script is None:
        raise ExecuteError(
            "run_proton_pipeline.mjs not found (set PROTON_PIPELINE_SCRIPT)"
        )

    render = req["payload"]["render"]
    width = min(int(render["width"]), 128)
    height = min(int(render["height"]), 96)
    out_root = out_dir or default_output_dir()
    out_root.mkdir(parents=True, exist_ok=True)
    req_id = req["requestId"]
    png_path = out_root / f"{req_id}-proton.png"

    node = _ensure_node()
    argv = [
        node,
        str(script),
        "--width",
        str(width),
        "--height",
        str(height),
        "--output",
        str(png_path),
    ]
    spec = req["payload"].get("sceneSpecification")
    spec_path: Path | None = None
    if isinstance(spec, dict):
        spec_out = dict(spec)
        if "kind" not in spec_out:
            spec_out["kind"] = "SceneSpecification"
        if "schemaVersion" not in spec_out:
            spec_out["schemaVersion"] = "1.0"
        if "id" not in spec_out:
            spec_out["id"] = req_id
        spec_path = out_root / f"{req_id}-proton-spec.json"
        spec_path.write_text(json.dumps(spec_out), encoding="utf-8")
        argv.extend(["--scene-spec", str(spec_path)])
    else:
        argv.append("--demo")

    runner = run_fn or _run
    proc = runner(argv, cwd=script.parent)
    if proc.returncode != 0:
        raise ExecuteError(
            f"proton pipeline failed ({proc.returncode}): {proc.stderr[-2000:]}"
        )
    if not png_path.is_file():
        raise ExecuteError(f"proton pipeline did not write PNG: {png_path}")

    png_hash = sha256_bytes(png_path.read_bytes())
    evidence_path = Path(str(png_path).replace(".png", ".evidence.json"))
    evidence: dict[str, Any] = {}
    if evidence_path.is_file():
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            evidence = {}

    return {
        "artifacts": [
            {
                "role": "beauty-png",
                "uri": str(png_path.as_posix()),
                "sha256": png_hash,
                "mediaType": "image/png",
            }
        ],
        "hashes": {
            "requestSha256": sha256_json(req),
            "pngSha256": png_hash,
            "promptSpecHash": (req.get("provenance") or {}).get("promptSpecHash"),
            "renderIntentHash": (req.get("provenance") or {}).get("renderIntentHash"),
        },
        "evidence": evidence,
        "mappedTo": "proton-raster-bridge/run_proton_pipeline.mjs",
        "statusTag": "partial",
    }


def execute_engine3d_world(
    req: dict[str, Any],
    *,
    out_dir: Path | None = None,
    run_fn: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """Echo/expand Engine3D world; still render when script present."""
    world = req["payload"].get("engine3dWorldDocument")
    if not isinstance(world, dict):
        raise ExecuteError("engine3d-world requires payload.engine3dWorldDocument")

    out_root = out_dir or default_output_dir()
    out_root.mkdir(parents=True, exist_ok=True)
    req_id = req["requestId"]
    world_path = out_root / f"{req_id}-engine3d-world.json"
    world_path.write_text(json.dumps(world), encoding="utf-8")

    script = engine3d_still_script()
    artifacts: list[dict[str, Any]] = [
        {
            "role": "engine3d-world-json",
            "uri": str(world_path.as_posix()),
            "sha256": sha256_json(world),
            "mediaType": "application/json",
        }
    ]
    status_tag = "partial"
    mapped = "engine3dWorldDocument written; still not run"

    if script is not None:
        node = _ensure_node()
        still_dir = out_root / f"{req_id}-engine3d-still"
        still_dir.mkdir(parents=True, exist_ok=True)
        render = req["payload"]["render"]
        argv = [
            node,
            str(script),
            "--engine3d-still",
            "--out-dir",
            str(still_dir),
            "--width",
            str(min(int(render["width"]), 128)),
            "--height",
            str(min(int(render["height"]), 96)),
            "--aov",
            "depth,normal",
        ]
        # Some still CLIs accept --world; if not, demo still still proves binary
        env_world = os.environ.get("ENGINE3D_STILL_WORLD_PATH")
        if env_world:
            argv.extend(["--world", env_world])
        runner = run_fn or _run
        proc = runner(argv, cwd=script.parent)
        if proc.returncode == 0:
            pngs = sorted(still_dir.rglob("*.png"))
            if pngs:
                png_hash = sha256_bytes(pngs[0].read_bytes())
                artifacts.append(
                    {
                        "role": "beauty-png",
                        "uri": str(pngs[0].as_posix()),
                        "sha256": png_hash,
                        "mediaType": "image/png",
                    }
                )
                mapped = "render-engine3d-still.mjs"
                status_tag = "partial"
            else:
                mapped = "engine3d still ran but no PNG; world JSON retained"
                status_tag = "skeleton"
        else:
            mapped = (
                "engine3d still failed; world JSON retained "
                f"(exit {proc.returncode})"
            )
            status_tag = "skeleton"
    else:
        status_tag = "skeleton"
        mapped = "ENGINE3D_STILL_SCRIPT_PATH missing; world JSON only"

    hashes = {
        "requestSha256": sha256_json(req),
        "worldSha256": sha256_json(world),
        "promptSpecHash": (req.get("provenance") or {}).get("promptSpecHash"),
        "renderIntentHash": (req.get("provenance") or {}).get("renderIntentHash"),
    }
    beauty = next((a for a in artifacts if a["role"] == "beauty-png"), None)
    if beauty:
        hashes["pngSha256"] = beauty["sha256"]

    return {
        "engine3dWorldDocument": world,
        "artifacts": artifacts,
        "hashes": hashes,
        "mappedTo": mapped,
        "statusTag": status_tag,
    }


def execute_rt4d(
    req: dict[str, Any],
    *,
    out_dir: Path | None = None,
    run_fn: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """RT4D via worldDocument or SceneSpecification fallback."""
    world = req["payload"].get("worldDocumentRt4d")
    if isinstance(world, dict):
        script = worlddocument_rt4d_script()
        if script is None:
            raise ExecuteError(
                "render-worlddocument-rt4d.mjs not found "
                "(set RT4D_WORLD_SCRIPT_PATH)"
            )
        out_root = out_dir or default_output_dir()
        out_root.mkdir(parents=True, exist_ok=True)
        req_id = req["requestId"]
        world_path = out_root / f"{req_id}-rt4d-world.json"
        png_path = out_root / f"{req_id}-rt4d.png"
        world_path.write_text(json.dumps(world), encoding="utf-8")
        node = _ensure_node()
        render = req["payload"]["render"]
        argv = [
            node,
            str(script),
            "--world",
            str(world_path),
            "--width",
            str(min(int(render["width"]), 128)),
            "--height",
            str(min(int(render["height"]), 96)),
            "--output",
            str(png_path),
        ]
        runner = run_fn or _run
        proc = runner(argv, cwd=script.parent)
        if proc.returncode != 0 or not png_path.is_file():
            raise ExecuteError(
                f"rt4d world render failed ({proc.returncode}): "
                f"{proc.stderr[-2000:]}"
            )
        png_hash = sha256_bytes(png_path.read_bytes())
        return {
            "artifacts": [
                {
                    "role": "beauty-png",
                    "uri": str(png_path.as_posix()),
                    "sha256": png_hash,
                    "mediaType": "image/png",
                }
            ],
            "hashes": {
                "requestSha256": sha256_json(req),
                "worldSha256": sha256_json(world),
                "pngSha256": png_hash,
            },
            "mappedTo": "render-worlddocument-rt4d.mjs",
            "statusTag": "partial",
        }

    # Fallback: scene-spec path is the enforced RT4D still surface
    if isinstance(req["payload"].get("sceneSpecification"), dict):
        result = execute_scene_spec(req, out_dir=out_dir, run_fn=run_fn)
        result["mappedTo"] = (
            "rt4d route → render-scene.mjs (SceneSpecification fallback)"
        )
        return result

    raise ExecuteError(
        "rt4d route requires payload.worldDocumentRt4d or sceneSpecification"
    )


def execute_route(
    req: dict[str, Any],
    *,
    out_dir: Path | None = None,
    run_fn: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    route = req["payload"]["route"]
    if route == "scene-spec":
        return execute_scene_spec(req, out_dir=out_dir, run_fn=run_fn)
    if route == "proton-raster":
        return execute_proton_raster(req, out_dir=out_dir, run_fn=run_fn)
    if route == "engine3d-world":
        return execute_engine3d_world(req, out_dir=out_dir, run_fn=run_fn)
    if route == "rt4d":
        return execute_rt4d(req, out_dir=out_dir, run_fn=run_fn)
    raise ExecuteError(f"unhandled route for execute: {route}")
