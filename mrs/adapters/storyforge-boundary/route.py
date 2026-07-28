"""Route a validated RenderRequest to MRS paths (minimal / skeleton).

Status: scene-spec path **partial** (echo embedded SceneSpecification).
Other routes **skeleton** — do not run PromptComposer / IModelBackend.
"""

from __future__ import annotations

from typing import Any

from validate_request import (
    RenderRequestValidationError,
    validate_render_request,
)


def _provenance_from(req: dict[str, Any]) -> dict[str, Any]:
    prov: dict[str, Any] = {
        "intentId": req["intentId"],
        "worldId": req["worldId"],
    }
    if "timelineId" in req:
        prov["timelineId"] = req["timelineId"]
    if "timeSeconds" in req:
        prov["timeSeconds"] = req["timeSeconds"]
    if "parameters" in req:
        prov["parameters"] = req["parameters"]
    return prov


def _refuse(req: dict[str, Any] | None, code: str, message: str) -> dict[str, Any]:
    base_id = (req or {}).get("requestId", "unknown")
    prov = (
        _provenance_from(req)
        if req and "intentId" in req and "worldId" in req
        else {"intentId": "unknown", "worldId": "unknown"}
    )
    return {
        "schemaVersion": "1.0",
        "requestId": base_id,
        "status": "refused",
        "provenance": prov,
        "routeUsed": "none",
        "error": {"code": code, "message": message},
        "mapping": {"note": "refused before MRS deep execution"},
    }


def route_render_request(data: Any) -> dict[str, Any]:
    """Validate then route. Returns RenderResult-shaped dict."""
    try:
        req = validate_render_request(data)
    except RenderRequestValidationError as exc:
        return _refuse(
            data if isinstance(data, dict) else None,
            "validation_failed",
            str(exc),
        )

    route = req["payload"]["route"]
    result: dict[str, Any] = {
        "schemaVersion": "1.0",
        "requestId": req["requestId"],
        "status": "ok",
        "provenance": _provenance_from(req),
        "routeUsed": route,
        "artifacts": [],
        "mapping": {
            "adapter": "mrs/adapters/storyforge-boundary",
            "sfOwnedStages": "declared-not-implemented-in-mrs",
        },
    }

    if route == "scene-spec":
        spec = req["payload"].get("sceneSpecification")
        if not isinstance(spec, dict):
            return _refuse(
                req,
                "missing_scene_specification",
                "route scene-spec requires payload.sceneSpecification object",
            )
        result["sceneSpecification"] = spec
        result["mapping"]["mappedTo"] = "SceneSpecification (embedded intake; compose-out-of-scope)"
        result["mapping"]["statusTag"] = "partial"
        return result

    if route == "engine3d-world":
        world = req["payload"].get("engine3dWorldDocument")
        if not isinstance(world, dict):
            return _refuse(
                req,
                "missing_engine3d_world",
                "route engine3d-world requires payload.engine3dWorldDocument",
            )
        result["engine3dWorldDocument"] = world
        result["mapping"]["mappedTo"] = "Engine3DWorldDocument (echo; expand not run)"
        result["mapping"]["statusTag"] = "skeleton"
        return result

    if route == "proton-raster":
        result["status"] = "ok"
        result["mapping"]["mappedTo"] = (
            "declared map toward mrs/adapters/proton-raster-bridge/ (not executed)"
        )
        result["mapping"]["statusTag"] = "skeleton"
        return result

    if route == "rt4d":
        result["mapping"]["mappedTo"] = "declared RT4D execution path (not executed)"
        result["mapping"]["statusTag"] = "skeleton"
        return result

    return _refuse(req, "unknown_route", f"unhandled route: {route}")
