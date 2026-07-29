"""IDAC.RenderRuntime v0.1 component facades."""

from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.dispatch import DispatchError, ENGINE_BY_LANE, build_dispatch_target
from app.idac.core.contracts import EvidenceContract, ExecutionPlan, IntentContract, PlanViolationError
from app.idac.domains.rendering.adapters import RenderEvidenceAdapter, RenderValidationAdapter
from app.models import DirectRequest, DispatchTarget, NormalizedPlan
from app.render_accel import build_replay_record_skeleton


class ViolationEmitter:
    @staticmethod
    def emit(error: PlanViolationError) -> dict[str, Any]:
        return error.to_violation()


class TileScheduler:
    """ATCM tile grid — staged evidence; Genblaze remains full-frame."""

    status = "partial"

    @staticmethod
    def describe(domain_plan: dict[str, Any]) -> dict[str, Any]:
        summary = domain_plan.get("atcm_summary") or {}
        rp = domain_plan.get("render_plan") or {}
        tee = rp.get("tile_execution_evidence") or {}
        return {
            "status": "partial",
            "tile_count": summary.get("tile_count") or tee.get("tile_count"),
            "execution_mode": rp.get("execution_mode", "full_frame_dispatch"),
            "note": "Staged tile evidence attached; per-tile Genblaze shade blocked-on-downstream-API",
        }


class ShadingEngine:
    status = "declared"

    @staticmethod
    def describe(domain_plan: dict[str, Any]) -> dict[str, Any]:
        rp = domain_plan.get("render_plan") or {}
        return {
            "status": "declared",
            "execution_mode": rp.get("execution_mode", "full_frame_dispatch"),
        }


class PostFXEngine:
    status = "declared"

    @staticmethod
    def describe(domain_plan: dict[str, Any]) -> dict[str, Any]:
        rp = domain_plan.get("render_plan") or {}
        ms = rp.get("math_strategies") or {}
        upscale = ms.get("upscale_strategy") or {}
        return {
            "status": "declared",
            "upscale_strategy": upscale.get("strategy"),
            "director_today": upscale.get("director_today"),
        }


class EvidenceEmitter:
    @staticmethod
    def build(
        *,
        intent: IntentContract,
        plan: ExecutionPlan,
        execution_trace: dict[str, Any],
        artifacts: dict[str, Any],
        environment: dict[str, Any],
        outcome: str,
    ) -> EvidenceContract:
        return EvidenceContract(
            intent_ref=intent.id,
            plan_ref=plan.plan_id,
            execution_trace=execution_trace,
            artifacts=artifacts,
            environment=environment,
            outcome=outcome,  # type: ignore[arg-type]
        )


class RenderExecutor:
    """RenderExecution — plan-faithful dispatch to Genblaze lanes."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.tile_scheduler = TileScheduler()
        self.shading_engine = ShadingEngine()
        self.postfx_engine = PostFXEngine()
        self.evidence_emitter = EvidenceEmitter()
        self.violation_emitter = ViolationEmitter()

    def execute(
        self,
        plan: ExecutionPlan,
        *,
        intent: IntentContract,
        http_client: httpx.Client | None = None,
    ) -> EvidenceContract:
        if plan.domain in {"ai", "compile"} and plan.enforcement == "declared":
            return self.evidence_emitter.build(
                intent=intent,
                plan=plan,
                execution_trace={"status": "declared_stub", "domain": plan.domain},
                artifacts={"note": "stub domain"},
                environment={"genblaze_base_url": self._settings.genblaze_base_url},
                outcome="declared_stub",
            )

        domain_plan = plan.domain_plan or {}
        if plan.domain == "render" and domain_plan.get("atcm_activated"):
            if not RenderValidationAdapter.check_tile_complexity_evidence(domain_plan):
                raise PlanViolationError(
                    code="render.no_complexity_evidence",
                    message="Rendering invariant: no tile plan without complexity evidence",
                    plan_ref=plan.plan_id,
                    intent_ref=intent.id,
                )

        dispatch_doc = plan.resource_plan.get("dispatch") or {}
        normalized = NormalizedPlan.model_validate(domain_plan.get("normalized_plan") or {})
        target = DispatchTarget.model_validate(dispatch_doc)
        request = _request_from_plan(intent, plan)

        replay_target = build_dispatch_target(normalized, request, self._settings)
        if replay_target.endpoint != target.endpoint or replay_target.payload != target.payload:
            raise PlanViolationError(
                code="idac.plan_drift",
                message="Dispatch drift vs frozen ExecutionPlan",
                plan_ref=plan.plan_id,
                intent_ref=intent.id,
            )

        runtime_meta = {
            "tile_scheduler": self.tile_scheduler.describe(domain_plan),
            "shading_engine": self.shading_engine.describe(domain_plan),
            "postfx_engine": self.postfx_engine.describe(domain_plan),
        }

        try:
            from app.main import dispatch_render as director_dispatch_render

            try:
                result = director_dispatch_render(self._settings, target, client=http_client)
            except TypeError:
                result = director_dispatch_render(self._settings, target)
        except DispatchError as exc:
            return self.evidence_emitter.build(
                intent=intent,
                plan=plan,
                execution_trace={
                    "endpoint": target.endpoint,
                    "lane": normalized.lane,
                    "error": str(exc),
                    "runtime": runtime_meta,
                },
                artifacts={},
                environment={"genblaze_base_url": self._settings.genblaze_base_url},
                outcome="dispatch_error",
            )

        artifacts = RenderEvidenceAdapter.wrap_render_accel(dispatch_result=result, replay_record=None)
        render_plan = domain_plan.get("render_plan")
        preview = domain_plan.get("complexity_evidence_preview") or {}
        if isinstance(render_plan, dict):
            replay = build_replay_record_skeleton(
                render_plan_id=str(render_plan.get("id")),
                complexity_evidence_id=str(preview.get("id") or "unknown"),
                lane=normalized.lane,
                engine=ENGINE_BY_LANE[normalized.lane],
                dispatch_endpoint=target.endpoint,
                result=result,
            )
            artifacts = RenderEvidenceAdapter.wrap_render_accel(
                dispatch_result=result,
                replay_record=replay,
            )
            artifacts["render_accel"] = {
                "render_plan_id": render_plan.get("id"),
                "complexity_evidence_id": preview.get("id"),
            }

        run_id = None
        for key in ("structure", "render", "image"):
            block = result.get(key)
            if isinstance(block, dict) and block.get("run_id"):
                run_id = block.get("run_id")
                break

        return self.evidence_emitter.build(
            intent=intent,
            plan=plan,
            execution_trace={
                "endpoint": target.endpoint,
                "lane": normalized.lane,
                "engine": ENGINE_BY_LANE[normalized.lane],
                "run_id": run_id,
                "runtime": runtime_meta,
            },
            artifacts=artifacts,
            environment={
                "genblaze_base_url": self._settings.genblaze_base_url,
                "policy_ref": intent.policy_ref,
            },
            outcome="ok",
        )


def _request_from_plan(intent: IntentContract, plan: ExecutionPlan) -> DirectRequest:
    raw = (plan.domain_plan or {}).get("effective_request")
    if isinstance(raw, dict):
        return DirectRequest.model_validate(raw)
    return _request_from_intent(intent)


def _request_from_intent(intent: IntentContract) -> DirectRequest:
    c = intent.constraints
    return DirectRequest(
        prompt=str(c["prompt"]) if c.get("prompt") else None,
        quality=c.get("quality"),
        speed_profile=c.get("speed_profile"),
        atcm=bool(c.get("atcm")),
        scene_spec=c.get("scene_spec") if isinstance(c.get("scene_spec"), dict) else None,
        source_run_id=c.get("source_run_id"),
    )
