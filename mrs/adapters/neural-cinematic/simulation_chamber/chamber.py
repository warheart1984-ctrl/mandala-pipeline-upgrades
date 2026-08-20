"""Simulation Chamber — Mandala Motion Organ (skip-Cosmos local path).

Inputs: Story Forge scene truth refs, optional reconstruction stub, camera path,
weather intent, emotional vectors (via request mood/intensity).
Outputs: flipbook frames + camera metadata; depth/normal buffers declared stubs.

Cosmos Transfer = optional rented-NVIDIA polish later — never required here.
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path
from typing import Any

from nce import CAPABILITY_ID, SCHEMA_VERSION
from nce.canonical import file_sha256

LIMITATION = (
    "Simulation Chamber is the Mandala Motion Organ and replaces Cosmos Transfer "
    "for local demo motion. Backend here is a camera-path flipbook of a governed "
    "still — not soft-body physics, not monocular depth, not temporal AI video."
)


def camera_pose(path_id: str, t: float) -> dict[str, float]:
    """Deterministic camera metadata for t in [0, 1]."""
    t = max(0.0, min(1.0, float(t)))
    if path_id == "push-in":
        return {
            "azimuth_deg": 0.0,
            "elevation_deg": 8.0,
            "distance": 4.0 - 1.5 * t,
            "fov_deg": 42.0 - 6.0 * t,
        }
    if path_id == "close-up":
        return {
            "azimuth_deg": 12.0 * math.sin(t * math.pi),
            "elevation_deg": 5.0,
            "distance": 2.2 - 0.4 * t,
            "fov_deg": 35.0,
        }
    return {
        "azimuth_deg": 360.0 * t,
        "elevation_deg": 12.0,
        "distance": 3.5,
        "fov_deg": 40.0,
    }


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def solid_png(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    r, g, b = rgb
    raw = b"".join(b"\x00" + bytes([r, g, b]) * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )


def _tint_png_bytes(src: bytes, frame_index: int, frame_count: int) -> bytes:
    if len(src) < 400:
        t = frame_index / max(1, frame_count - 1)
        r = int(40 + 80 * t) % 256
        g = int(60 + 40 * (1 - t)) % 256
        b = int(100 + 50 * math.sin(t * math.pi)) % 256
        return solid_png(64, 64, (r, g, b))
    return src


def declared_buffer_stubs(frame_index: int) -> dict[str, Any]:
    """Depth/normal motion buffers — declared stubs (not computed)."""
    return {
        "depthBuffer": {
            "status": "declared",
            "uri": None,
            "note": f"depth buffer not computed (frame {frame_index})",
        },
        "normalBuffer": {
            "status": "declared",
            "uri": None,
            "note": f"normal buffer not computed (frame {frame_index})",
        },
        "motionBuffer": {
            "status": "declared",
            "uri": None,
            "note": f"optical flow / motion vectors not computed (frame {frame_index})",
        },
    }


def run_chamber(
    *,
    out_dir: Path,
    base_still: Path,
    production_id: str,
    scene_id: str,
    shot_spec: dict[str, Any],
    character_id: str | None = None,
    identity_lock: dict[str, Any] | None = None,
    weather_intent: list[str] | None = None,
    emotional_vector: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Emit SCW + frame still refs. Status: partial (flipbook Motion Organ)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path_id = shot_spec["cameraPathId"]
    frame_count = int(shot_spec.get("frameCount") or 8)
    frame_count = max(1, min(64, frame_count))
    weather = list(weather_intent or shot_spec.get("weatherTags") or [])

    src_bytes = Path(base_still).read_bytes()
    frames: list[dict[str, Any]] = []
    for i in range(frame_count):
        t = 0.0 if frame_count == 1 else i / (frame_count - 1)
        cam = camera_pose(path_id, t)
        name = f"sim_{path_id.replace('-', '_')}_{i:03d}.png"
        dest = out_dir / name
        dest.write_bytes(_tint_png_bytes(src_bytes, i, frame_count))
        frames.append(
            {
                "role": "sim_frame",
                "uri": str(dest),
                "sha256": file_sha256(dest),
                "camera": cam,
                "buffers": declared_buffer_stubs(i),
                "notes": f"Simulation Chamber flipbook frame {i}/{frame_count - 1}",
            }
        )

    scw: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "SimulatedCinematicWorld",
        "status": "partial",
        "capabilityId": CAPABILITY_ID,
        "sceneId": scene_id,
        "productionId": production_id,
        "characterId": character_id,
        "identityLock": identity_lock,
        "shotSpec": {
            "cameraPathId": path_id,
            "mood": shot_spec.get("mood") or "",
            "weatherTags": weather,
            "frameCount": frame_count,
        },
        "emotionalVector": emotional_vector,
        "baseKeyframeRef": str(base_still),
        "cosmosRequired": False,
        "rendererBackend": "camera_orbit_flipbook",
        "organ": "Mandala Simulation Chamber",
        "role": "Motion Organ",
        "limitation": LIMITATION,
    }
    return scw, frames
