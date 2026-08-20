#!/usr/bin/env python3
"""Import a ZBrush (or OBJ/FBX) production sculpt under identityLock.

Hashes mesh + optional low-memory Blender preview bake (Workbench, 384²).
Does not claim productionSculpt=true unless sculpt.obj|fbx is present and hashed.

Do not assume large system RAM (upgrade stick may be DOA). RX 580 VRAM
is unrelated — this path is CPU/RAM + optional Blender.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sculpt_under_lock import (  # noqa: E402
    CHARACTER_ID_DEFAULT,
    ensure_production_intake,
    find_production_mesh,
    resolve_sculpt_under_lock,
)


def import_mesh(src: Path, character_id: str, *, bake: bool = True) -> dict:
    src = Path(src).resolve()
    if not src.is_file():
        raise SystemExit(f"mesh not found: {src}")
    if src.suffix.lower() not in {".obj", ".fbx"}:
        raise SystemExit("expected .obj or .fbx (ZBrush Decimation Master / GoZ export)")

    prod = ensure_production_intake(character_id)
    dest_name = "sculpt.obj" if src.suffix.lower() == ".obj" else "sculpt.fbx"
    dest = prod / dest_name
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    # remove opposite format to avoid ambiguity
    other = prod / ("sculpt.fbx" if dest_name.endswith(".obj") else "sculpt.obj")
    if other.is_file() and other != dest:
        other.unlink()

    # Force re-resolve (bake preview if OBJ)
    result = resolve_sculpt_under_lock(character_id, ensure_intake=True)
    if bake and result.get("productionSculpt") and not result.get("keyframePath"):
        # resolve already attempts bake for OBJ
        result = resolve_sculpt_under_lock(character_id, ensure_intake=True)
    result["importedFrom"] = str(src)
    result["productionDir"] = str(prod)
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Import ZBrush production sculpt under identityLock")
    p.add_argument("--character-id", default=CHARACTER_ID_DEFAULT)
    p.add_argument(
        "--mesh",
        default="",
        help="Path to sculpt.obj / sculpt.fbx from ZBrush. Omit to only ensure intake folder.",
    )
    p.add_argument("--no-bake", action="store_true", help="Skip Blender preview bake")
    args = p.parse_args(argv)

    if not args.mesh:
        prod = ensure_production_intake(args.character_id)
        resolved = resolve_sculpt_under_lock(args.character_id)
        print(
            json.dumps(
                {
                    "action": "ensure_intake_only",
                    "productionDir": str(prod),
                    "meshPresent": find_production_mesh(prod) is not None,
                    "resolved": resolved,
                },
                indent=2,
            )
        )
        return 0

    out = import_mesh(Path(args.mesh), args.character_id, bake=not args.no_bake)
    print(json.dumps(out, indent=2))
    if not out.get("productionSculpt"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
