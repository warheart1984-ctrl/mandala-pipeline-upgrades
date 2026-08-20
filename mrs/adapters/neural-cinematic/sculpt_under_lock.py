"""Resolve characterId → sculpt under identityLock (production ZBrush preferred).

Status honesty:
- production OBJ/FBX present → productionSculpt=true, status partial_with_gaps
  (mesh locked; full skin/rig verification may still be incomplete)
- else fixture anthro / blender preview → productionSculpt=false,
  status core-enforced-fixture-not-production-sculpt

Never claim ZBrush production when only the tetrahedron fixture exists.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MRS = ROOT.parents[1]
REPO = ROOT.parents[2]

CHARACTER_ID_DEFAULT = "warrior-anthro-fox-01"

# Production intake (drop ZBrush export here)
PRODUCTION_DIR_CANDIDATES = (
    MRS / "packages" / "sovereign-sculptor" / "production" / CHARACTER_ID_DEFAULT,
    Path("/media/jon/New Volume/Mandala Rendering Software/mrs/packages/sovereign-sculptor/production")
    / CHARACTER_ID_DEFAULT,
    ROOT / "production" / CHARACTER_ID_DEFAULT,
)

# Fixture fallbacks (NOT production)
SCULPTOR_ROOTS = (
    MRS / "packages" / "sovereign-sculptor",
    Path("/media/jon/New Volume/Mandala Rendering Software/mrs/packages/sovereign-sculptor"),
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_sculptor_root() -> Path | None:
    for root in SCULPTOR_ROOTS:
        if (root / "fixtures" / "anthro").is_dir() or (root / "production").is_dir():
            return root
    return None


def find_production_dir(character_id: str = CHARACTER_ID_DEFAULT) -> Path | None:
    candidates = [
        MRS / "packages" / "sovereign-sculptor" / "production" / character_id,
        Path("/media/jon/New Volume/Mandala Rendering Software/mrs/packages/sovereign-sculptor/production")
        / character_id,
        ROOT / "production" / character_id,
    ]
    for d in candidates:
        if d.is_dir():
            return d
    return None


def find_production_mesh(prod_dir: Path) -> Path | None:
    for name in (
        "sculpt.obj",
        "sculpt.fbx",
        "production.obj",
        "production.fbx",
        "warrior.obj",
        "warrior.fbx",
        "mesh.obj",
        "mesh.fbx",
    ):
        p = prod_dir / name
        if p.is_file() and p.stat().st_size > 1024:
            return p
    # any reasonably large obj/fbx
    for p in sorted(prod_dir.glob("*.obj")) + sorted(prod_dir.glob("*.fbx")):
        if p.is_file() and p.stat().st_size > 1024:
            return p
    return None


def ensure_production_intake(character_id: str = CHARACTER_ID_DEFAULT) -> Path:
    """Create production drop folder + README if missing. Prefer MRS sculptor package."""
    sculptor = find_sculptor_root()
    base = (
        (sculptor / "production" / character_id)
        if sculptor
        else (ROOT / "production" / character_id)
    )
    base.mkdir(parents=True, exist_ok=True)
    readme = base / "README.md"
    if not readme.is_file():
        readme.write_text(
            f"""# Production sculpt intake — `{character_id}`

**Status:** drop a **ZBrush** (or equivalent) export here to unlock production under identityLock.

## Required

| File | Purpose |
|------|---------|
| `sculpt.obj` **or** `sculpt.fbx` | Production body mesh from ZBrush (GoZ / Decimation Master export OK) |
| `identityLock.json` | Optional operator overrides; digests are rewritten on import |

## Optional

| File | Purpose |
|------|---------|
| `preview.png` | If present, used as NCE keyframe (else Blender bake attempted) |
| `displacement.exr` / `.tif` | Displacement maps (declared until wired) |
| `uv.png` | UV layout reference |

## Import

```bash
python3 mrs/adapters/neural-cinematic/import_zbrush_production.py --character-id {character_id}
```

Until `sculpt.obj`/`sculpt.fbx` exists, Mandala falls back to the **fixture** anthro sculpt
(`core-enforced-fixture-not-production-sculpt`) and must **not** claim `productionSculpt=true`.
""",
            encoding="utf-8",
        )
    lock_path = base / "identityLock.json"
    if not lock_path.is_file():
        lock_path.write_text(
            json.dumps(
                {
                    "characterId": character_id,
                    "species": "anthro-fox",
                    "rigSpecies": "anthro",
                    "faceRefId": "heroic-fox-face-v1",
                    "bodyBuild": "heroic-athletic",
                    "armorId": "courtyard-plate-v1",
                    "weaponId": "courtyard-sword-v1",
                    "weaponHeldIn": "right",
                    "meshHash": "sha256:PENDING-drop-zbrush-sculpt-obj",
                    "rigHash": "sha256:PENDING-production-rig",
                    "prohibitedMutations": [
                        "extra-tails",
                        "human-only-face",
                        "left-hand-sword-swap",
                        "armor-dissolution",
                        "weather-rewrite",
                        "fixture-tetrahedron-as-production",
                    ],
                    "productionSculpt": False,
                    "statusTag": "declared",
                    "gaps": ["zbrush_sculpt_obj_or_fbx_missing"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return base


def _fixture_paths() -> dict[str, Path | None]:
    root = find_sculptor_root()
    if not root:
        return {"root": None, "constitutional": None, "preview": None, "glb": None}
    anthro = root / "fixtures" / "anthro"
    blender = root / "fixtures" / "blender-anthro-v1"
    return {
        "root": root,
        "constitutional": anthro / "anthro-character-fixture.constitutional.json",
        "preview": blender / "anthro-blender-preview.png"
        if (blender / "anthro-blender-preview.png").is_file()
        else None,
        "glb": blender / "anthro-blender-character.glb"
        if (blender / "anthro-blender-character.glb").is_file()
        else (anthro / "anthro-character-fixture.glb"),
        "sculpt_json": anthro / "anthro-character-fixture.sculpt.json",
    }


def _find_blender() -> str | None:
    for p in (
        Path("/media/jon/New Volume/Mandala Rendering Software/runtime/bin/blender"),
        REPO / "runtime" / "bin" / "blender",
        shutil.which("blender") and Path(shutil.which("blender") or ""),
    ):
        if p and Path(p).is_file() and os.access(p, os.X_OK):
            return str(p)
    # flatpak
    if shutil.which("flatpak"):
        return "flatpak"
    return None


def bake_preview_png_from_obj(obj_path: Path, dest_png: Path) -> dict[str, Any]:
    """Best-effort low-memory Blender bake of production OBJ → PNG keyframe.

    Tuned for modest system RAM (extra stick DOA — do not assume 32GB).
    RX 580 VRAM is unrelated; this path is CPU/RAM + optional Blender.
    """
    blender = _find_blender()
    dest_png.parent.mkdir(parents=True, exist_ok=True)
    if not blender:
        return {"ok": False, "status": "declared", "gaps": ["blender_missing"], "why": "no blender"}

    script = dest_png.with_suffix(".bake.py")
    script.write_text(
        f"""
import bpy
import math
bpy.ops.wm.read_factory_settings(use_empty=True)
# Low-memory import: no image search, split by object only
bpy.ops.import_scene.obj(
    filepath={str(obj_path)!r},
    use_image_search=False,
    split_mode="OFF",
)
# Drop heavy modifiers / unused data if present
for obj in list(bpy.data.objects):
    if obj.type == "MESH":
        obj.data.use_auto_smooth = False
bpy.ops.object.select_all(action="DESELECT")
# camera
cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam)
bpy.context.scene.camera = cam
cam.location = (2.4, -2.4, 1.6)
cam.rotation_euler = (math.radians(65), 0, math.radians(45))
# light (simple point — cheaper than area)
light_data = bpy.data.lights.new(name="Key", type="POINT")
light_data.energy = 800
light = bpy.data.objects.new(name="Key", object_data=light_data)
bpy.context.scene.collection.objects.link(light)
light.location = (2, -1, 3)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "SINGLE"
scene.render.resolution_x = 384
scene.render.resolution_y = 384
scene.render.resolution_percentage = 100
scene.render.filepath = {str(dest_png)!r}
# Cap tile / memory pressure where available
if hasattr(scene.render, "tile_x"):
    scene.render.tile_x = 128
    scene.render.tile_y = 128
bpy.ops.render.render(write_still=True)
""",
        encoding="utf-8",
    )
    if blender == "flatpak":
        cmd = [
            "flatpak",
            "run",
            "org.blender.Blender",
            "--background",
            "--python",
            str(script),
        ]
    else:
        cmd = [blender, "--background", "--python", str(script)]
    run = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if dest_png.is_file() and dest_png.stat().st_size > 1000:
        return {
            "ok": True,
            "status": "partial_with_gaps",
            "path": str(dest_png),
            "gaps": [
                "workbench_384_preview_not_lookdev",
                "low_memory_bake_settings",
                "no_pbr_materials_from_zbrush",
            ],
        }
    return {
        "ok": False,
        "status": "declared",
        "gaps": ["blender_bake_failed"],
        "why": (run.stderr or run.stdout or "")[-600:],
    }


def resolve_sculpt_under_lock(
    character_id: str = CHARACTER_ID_DEFAULT,
    *,
    ensure_intake: bool = True,
) -> dict[str, Any]:
    """Prefer ZBrush production mesh; else fixture. Always returns identityLock + keyframe hint."""
    if ensure_intake:
        prod_dir = ensure_production_intake(character_id)
    else:
        prod_dir = find_production_dir(character_id) or ensure_production_intake(character_id)

    mesh = find_production_mesh(prod_dir)
    if mesh:
        mesh_hash = "sha256:" + _sha256_file(mesh)
        preview = prod_dir / "preview.png"
        bake = {"ok": preview.is_file(), "path": str(preview) if preview.is_file() else None}
        if not preview.is_file() and mesh.suffix.lower() == ".obj":
            bake = bake_preview_png_from_obj(mesh, preview)
        # rig hash: production rig not yet separate — stamp pending or hash sidecar
        rig_path = prod_dir / "rig.json"
        if not rig_path.is_file():
            # use character-rig/1.0 fixture rig digest if available
            fx = _fixture_paths()
            rig_hash = "sha256:PENDING-production-rig-bind"
            if fx.get("constitutional") and Path(fx["constitutional"]).is_file():
                dig = json.loads(Path(fx["constitutional"]).read_text(encoding="utf-8")).get(
                    "digests", {}
                )
                # Keep fixture rigDigest only as declared interim bind target
                if dig.get("rigDigest"):
                    rig_hash = "sha256:" + dig["rigDigest"]
        else:
            rig_hash = "sha256:" + _sha256_file(rig_path)

        lock = {
            "species": "anthro-fox",
            "rigSpecies": "anthro",
            "faceRefId": "heroic-fox-face-v1",
            "bodyBuild": "heroic-athletic",
            "armorId": "courtyard-plate-v1",
            "weaponId": "courtyard-sword-v1",
            "weaponHeldIn": "right",
            "meshHash": mesh_hash,
            "rigHash": rig_hash,
            "prohibitedMutations": [
                "extra-tails",
                "human-only-face",
                "left-hand-sword-swap",
                "armor-dissolution",
                "weather-rewrite",
                "swap-to-tetrahedron-fixture",
            ],
        }
        # persist lock
        (prod_dir / "identityLock.json").write_text(
            json.dumps(
                {
                    **lock,
                    "characterId": character_id,
                    "productionSculpt": True,
                    "statusTag": "partial_with_gaps",
                    "meshPath": str(mesh),
                    "gaps": [
                        "skin_layers_may_be_incomplete",
                        "production_rig_bind_may_use_interim_rigDigest",
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        keyframe = None
        if bake.get("ok") and bake.get("path"):
            keyframe = bake["path"]
        return {
            "characterId": character_id,
            "productionSculpt": True,
            "statusTag": "partial_with_gaps",
            "fixtureStatus": None,
            "meshPath": str(mesh),
            "keyframePath": keyframe,
            "identityLock": lock,
            "productionDir": str(prod_dir),
            "bake": bake,
            "gaps": [
                "zbrush_mesh_present_skin_rig_verification_partial",
            ]
            + list((bake.get("gaps") if isinstance(bake, dict) else None) or []),
        }

    # --- Fixture fallback (NOT production) ---
    fx = _fixture_paths()
    digests: dict[str, Any] = {}
    if fx.get("constitutional") and Path(fx["constitutional"]).is_file():
        digests = json.loads(Path(fx["constitutional"]).read_text(encoding="utf-8")).get(
            "digests", {}
        )
    mesh_digest = digests.get("meshDigest") or "fixture-mesh-anthro-fox-warrior-v1"
    rig_digest = digests.get("rigDigest") or "fixture-rig-anthro-character-rig-1.0"
    lock = {
        "species": "anthro-fox",
        "rigSpecies": "anthro",
        "faceRefId": "heroic-fox-face-v1",
        "bodyBuild": "heroic-athletic",
        "armorId": "courtyard-plate-v1",
        "weaponId": "courtyard-sword-v1",
        "weaponHeldIn": "right",
        "meshHash": f"sha256:{mesh_digest}",
        "rigHash": f"sha256:{rig_digest}",
        "prohibitedMutations": [
            "extra-tails",
            "human-only-face",
            "left-hand-sword-swap",
            "armor-dissolution",
            "weather-rewrite",
        ],
    }
    keyframe = str(fx["preview"]) if fx.get("preview") else None
    return {
        "characterId": character_id,
        "productionSculpt": False,
        "statusTag": "core-enforced-fixture-not-production-sculpt",
        "fixtureStatus": "core-enforced-fixture-not-production-sculpt",
        "meshPath": str(fx["glb"]) if fx.get("glb") else None,
        "keyframePath": keyframe,
        "identityLock": lock,
        "productionDir": str(prod_dir),
        "gaps": [
            "zbrush_sculpt_obj_missing_drop_into_production_dir",
            "using_anthro_fixture_or_blender_demo_not_zbrush",
        ],
        "claim": "NOT productionSculpt — drop sculpt.obj from ZBrush into productionDir",
    }


if __name__ == "__main__":
    print(json.dumps(resolve_sculpt_under_lock(), indent=2))
