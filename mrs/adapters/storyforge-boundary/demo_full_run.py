#!/usr/bin/env python3
"""One-shot StoryForge→MRS full run (fixture RenderRequests → PNGs).

Starts from sample RenderRequests that represent StoryForge Runtime output
(Story→…→RenderRequest remains SF-owned / declared). MRS executes every
intake→pixels stage: proton HQ, scene-spec RT4D, optional Engine3D still.

Usage:
  python mrs/adapters/storyforge-boundary/demo_full_run.py
  python mrs/adapters/storyforge-boundary/demo_full_run.py --out-dir output/cecp-full-run

Writes under --out-dir:
  proton/beauty.png (+ depth.png, normal.png)
  scene/beauty.png (or copied scene-spec PNG)
  engine3d/beauty.png (best-effort)
  evidence.json, render-results.json
  OPTIONAL: genblaze-render-request.json when --genblaze-smoke

Prints absolute PNG paths. Exit 0 if proton HQ + at least one beauty PNG OK.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from paths import default_output_dir, repo_root  # noqa: E402
from route import route_render_request  # noqa: E402

FIXTURES = {
    "proton": _DIR / "fixtures" / "sample-render-request-cinematic-proton.json",
    "scene": _DIR / "fixtures" / "sample-render-request-cinematic-scene.json",
    "engine3d": _DIR / "fixtures" / "sample-render-request-cinematic-engine3d.json",
}


def _copy_role_pngs(result: dict[str, Any], dest_dir: Path, prefix: str) -> list[str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    abs_paths: list[str] = []
    role_map = {
        "beauty-png": "beauty.png",
        "depth-png": "depth.png",
        "normal-png": "normal.png",
    }
    for art in result.get("artifacts") or []:
        role = art.get("role")
        uri = art.get("uri")
        if role not in role_map or not uri:
            continue
        src = Path(uri)
        if not src.is_file():
            continue
        dest = dest_dir / role_map[role]
        shutil.copy2(src, dest)
        abs_paths.append(str(dest.resolve()))
    # Fallback: first beauty-like PNG under request out
    if not abs_paths:
        for art in result.get("artifacts") or []:
            if art.get("mediaType") == "image/png" and art.get("uri"):
                src = Path(art["uri"])
                if src.is_file():
                    dest = dest_dir / f"{prefix}-beauty.png"
                    shutil.copy2(src, dest)
                    abs_paths.append(str(dest.resolve()))
                    break
    return abs_paths


def _try_genblaze_smoke(out_dir: Path, request: dict[str, Any]) -> dict[str, Any]:
    """In-process Genblaze /api/render-request when deps available."""
    os.environ["RENDER_REQUEST_API_ENABLED"] = "1"
    genblaze_app = repo_root() / "mrs" / "apps" / "genblaze-media"
    if str(genblaze_app) not in sys.path:
        sys.path.insert(0, str(genblaze_app))
    try:
        from fastapi.testclient import TestClient  # noqa: WPS433
        from app.main import app  # noqa: WPS433
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "skipped": True,
            "reason": f"genblaze TestClient unavailable: {exc}",
        }

    client = TestClient(app)
    # Use draft scene smoke for speed inside HTTP path
    body = dict(request)
    body["requestId"] = "rr-genblaze-smoke"
    body["payload"] = dict(body["payload"])
    body["payload"]["render"] = dict(body["payload"]["render"])
    body["payload"]["render"]["quality"] = "draft"
    body["payload"]["render"]["width"] = 64
    body["payload"]["render"]["height"] = 48
    resp = client.post("/api/render-request", json=body)
    payload = {
        "ok": resp.status_code == 200,
        "statusCode": resp.status_code,
        "body": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text[:2000],
    }
    out_path = out_dir / "genblaze-render-request.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    payload["evidencePath"] = str(out_path.resolve())
    return payload


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="CECP StoryForge→4D full demo run")
    p.add_argument(
        "--out-dir",
        default=None,
        help="Output root (default: <repo>/output/cecp-full-run)",
    )
    p.add_argument(
        "--skip-engine3d",
        action="store_true",
        help="Skip Engine3D still (proton + scene only)",
    )
    p.add_argument(
        "--genblaze-smoke",
        action="store_true",
        help="Also POST /api/render-request via FastAPI TestClient",
    )
    p.add_argument(
        "--routes",
        default="proton,scene,engine3d",
        help="Comma list: proton,scene,engine3d",
    )
    args = p.parse_args(argv)

    out_root = Path(args.out_dir) if args.out_dir else (default_output_dir() / "cecp-full-run")
    out_root.mkdir(parents=True, exist_ok=True)

    wanted = {s.strip() for s in args.routes.split(",") if s.strip()}
    if args.skip_engine3d:
        wanted.discard("engine3d")

    results: dict[str, Any] = {}
    png_abs: list[str] = []
    errors: list[str] = []

    for name in ("proton", "scene", "engine3d"):
        if name not in wanted:
            continue
        fixture = FIXTURES[name]
        if not fixture.is_file():
            errors.append(f"missing fixture {fixture}")
            continue
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        sub = out_root / name
        sub.mkdir(parents=True, exist_ok=True)
        result = route_render_request(raw, execute=True, out_dir=sub)
        results[name] = result
        (sub / "render-result.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        if result.get("status") != "ok":
            errors.append(f"{name}: {result.get('status')} {result.get('error')}")
            continue
        png_abs.extend(_copy_role_pngs(result, sub, name))

    genblaze: dict[str, Any] | None = None
    if args.genblaze_smoke:
        scene_req = json.loads(FIXTURES["scene"].read_text(encoding="utf-8"))
        genblaze = _try_genblaze_smoke(out_root, scene_req)

    evidence = {
        "kind": "cecp-storyforge-4d-full-run",
        "status": "enforced" if not errors else "partial",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "outDir": str(out_root.resolve()),
        "routes": sorted(wanted),
        "pngs": png_abs,
        "errors": errors,
        "ownership": {
            "storyforgeUpstream": "declared",
            "mrsRenderRequestToPixels": "enforced",
        },
        "genblaze": genblaze,
        "resultsSummary": {
            k: {
                "status": v.get("status"),
                "routeUsed": v.get("routeUsed"),
                "mappedTo": (v.get("mapping") or {}).get("mappedTo"),
                "statusTag": (v.get("mapping") or {}).get("statusTag"),
                "artifactCount": len(v.get("artifacts") or []),
            }
            for k, v in results.items()
        },
    }
    evidence_path = out_root / "evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    (out_root / "render-results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )

    print("=== CECP StoryForge->4D full run ===")
    print(f"outDir: {out_root.resolve()}")
    print(f"evidence: {evidence_path.resolve()}")
    print("PNGs:")
    for path in png_abs:
        print(f"  {path}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  {e}")
    if genblaze is not None:
        print(f"genblazeSmoke: ok={genblaze.get('ok')} skipped={genblaze.get('skipped')}")

    # Require proton beauty for success; scene preferred
    proton_ok = any(p.replace("\\", "/").endswith("/proton/beauty.png") for p in png_abs)
    if not proton_ok:
        proton_ok = any("proton" in p.replace("\\", "/") and p.lower().endswith(".png") for p in png_abs)
    return 0 if proton_ok and not any("proton:" in e for e in errors) else 1


if __name__ == "__main__":
    raise SystemExit(main())
