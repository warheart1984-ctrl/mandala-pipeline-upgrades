"""AAIS — Factory Workers (contract / worker ID stubs only).

Full AAIS runtime is **not** hosted in Mandala. AIKI has an optional
`aais` inference provider stub (`aiki/pipeline/inference/adapters/aais_stub.py`);
Infinity/AAIS owns worker orchestration.

This module records worker IDs + enforcement notes for the NCE evidence chain.
Status: **declared** (stubs). Do not invent a Mandala AAIS runtime here.
"""

from __future__ import annotations

from typing import Any

# Worker IDs — Factory Workers organ (expression pipeline, not narrative law)
WORKER_IDS = (
    "aais.scene_breakdown",
    "aais.depth_estimate",
    "aais.geometry_camera_light_solve",
    "aais.sim_preset",
    "aais.painter_pass",
    "aais.sound_alignment",
    "aais.continuity_check",
)

ENFORCEMENT_NOTES = (
    "AAIS workers are Factory Workers: they execute expression tasks under "
    "Story Forge narrative constraints. Mandala records worker ids in NCS "
    "modelIds/evidence; Mandala does not host the AAIS scheduler.",
    "Depth / geometry / physics solves remain declared until an external AAIS "
    "or Mandala reconstruction backend is wired.",
    "Painter pass on RX 580 is Mandala ai_painter (SD-Turbo) — tagged "
    "partial_with_gaps — not a full AAIS painter farm.",
    "Reuse AIKI IPI aais provider only as an optional inference backend; "
    "do not make NCE depend on AIKI at import time.",
)


def worker_stub_manifest() -> dict[str, Any]:
    return {
        "organ": "AAIS",
        "role": "Factory Workers",
        "status": "declared",
        "runtimeHostedInMandala": False,
        "aikiProviderId": "aais",
        "aikiProviderPath": "aiki/pipeline/inference/adapters/aais_stub.py",
        "workerIds": list(WORKER_IDS),
        "enforcementNotes": list(ENFORCEMENT_NOTES),
    }


def planned_worker_ids_for_request(*, requires_simulation: bool, paint: bool) -> list[str]:
    """Which worker IDs a request would invoke if AAIS were live."""
    ids = ["aais.scene_breakdown", "aais.continuity_check"]
    if requires_simulation:
        ids.append("aais.sim_preset")
    if paint:
        ids.append("aais.painter_pass")
    # depth/geometry remain declared stubs — listed but not executed
    ids.extend(["aais.depth_estimate", "aais.geometry_camera_light_solve"])
    return ids
