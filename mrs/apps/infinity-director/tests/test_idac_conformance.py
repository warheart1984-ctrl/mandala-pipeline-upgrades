"""IDAC conformance suite — L0 + partial L1 (see docs/IDAC_CONFORMANCE_SUITE.md)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.config import Settings
from app.idac import (
    IntentContract,
    IntentGoal,
    PlanViolationError,
    handle_intent,
    request_plan,
    validate_intent_evidence,
)
from app.idac.core.constitution import CONSTITUTIONAL_INVARIANTS
from app.idac.core.learning import record_learning_candidate
from app.idac.core.router import validate_intent, validate_plan
from app.idac.domains.rendering.adapters import RenderOptimizerAdapter, RenderValidationAdapter
from app.idac.domains.rendering.runtime import PostFXEngine, RenderExecutor, ShadingEngine, TileScheduler
from app.idac.runtime import execute_plan

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def _check_required(obj: dict, schema: dict) -> None:
    for key in schema.get("required", []):
        assert key in obj, f"missing required field {key!r}"
    for prop, spec in schema.get("properties", {}).items():
        if prop not in obj:
            continue
        if "const" in spec:
            assert obj[prop] == spec["const"], prop
        if "enum" in spec:
            assert obj[prop] in spec["enum"], prop


def _sample_intent(**overrides) -> IntentContract:
    base = dict(
        mission_ref="cecp/idac-stack-2026-07",
        policy_ref="RenderAccelContract/0.1.0",
        domain="render",
        goal=IntentGoal(
            statement="Produce governed preview still",
            justification="Reference runtime under mission_ref and policy_ref",
        ),
        constraints={"prompt": "empty sky wall flat structure", "speed_profile": "fast"},
    )
    base.update(overrides)
    return IntentContract(**base)


@pytest.fixture
def settings() -> Settings:
    return Settings(planner_mode="heuristic")


class TestIntentL0:
    def test_intent_contract_schema_shape(self):
        doc = _sample_intent().to_document()
        _check_required(doc, _load_schema("idac-intent.schema.json"))

    def test_constitutional_invariant_count(self):
        assert len(CONSTITUTIONAL_INVARIANTS) == 6

    def test_router_rejects_empty_mission(self):
        intent = _sample_intent(mission_ref="")
        with pytest.raises(PlanViolationError) as exc:
            validate_intent(intent)
        assert exc.value.code == "idac.intent_incomplete"


class TestOptimizerL0:
    def test_optimizer_must_not_execute(self, settings):
        plan = request_plan(_sample_intent(), settings=settings)
        assert plan.optimizer["must_not_execute"] is True
        _check_required(plan.to_document(), _load_schema("idac-execution-plan.schema.json"))

    def test_atcm_domain_plan_includes_render_plan(self, settings):
        intent = _sample_intent(constraints={"prompt": "flat wall", "atcm": True})
        plan = request_plan(intent, settings=settings)
        assert plan.domain_plan.get("atcm_activated") is True
        rp = plan.domain_plan.get("render_plan") or {}
        assert rp.get("kind") == "RenderPlan"
        assert RenderValidationAdapter.check_tile_complexity_evidence(plan.domain_plan)

    def test_ai_domain_stub(self, settings):
        intent = _sample_intent(domain="ai")
        plan = request_plan(intent, settings=settings)
        assert plan.enforcement == "declared"
        assert plan.domain_plan.get("status") == "declared"


class TestRouterL1:
    def test_handle_intent_mocked_dispatch(self, settings):
        intent = _sample_intent()
        plan = request_plan(intent, settings=settings)

        def _fake_dispatch(_settings, target, client=None):
            return {"structure": {"run_id": "idac-run-1", "preview_url": "/p/idac-run-1"}}

        with patch("app.main.dispatch_render", side_effect=_fake_dispatch):
            bundle = handle_intent(intent, settings=settings)

        assert bundle["validation"]["verdict"] == "pass"
        ev = bundle["evidence"]
        _check_required(ev, _load_schema("idac-evidence.schema.json"))
        assert ev["execution_trace"]["run_id"] == "idac-run-1"


class TestExecutionL0:
    def test_plan_drift_raises(self, settings):
        intent = _sample_intent()
        plan = request_plan(intent, settings=settings)
        plan.resource_plan["dispatch"] = {**plan.resource_plan["dispatch"], "endpoint": "/api/mutated"}

        with pytest.raises(PlanViolationError) as exc:
            execute_plan(plan, intent=intent, settings=settings)
        assert exc.value.code == "idac.plan_drift"


class TestEvidenceL0:
    def test_atcm_replay_record_on_success(self, settings):
        intent = _sample_intent(constraints={"prompt": "flat wall", "atcm": True})
        plan = request_plan(intent, settings=settings)

        with patch(
            "app.main.dispatch_render",
            return_value={"structure": {"run_id": "atcm-ev-1"}},
        ):
            evidence = execute_plan(plan, intent=intent, settings=settings)

        assert evidence.artifacts.get("replay_record") is not None
        assert evidence.intent_ref == intent.id
        assert evidence.plan_ref == plan.plan_id


class TestValidationL0:
    def test_validation_skeleton_bit_identical_skipped(self, settings):
        intent = _sample_intent()
        plan = request_plan(intent, settings=settings)
        with patch(
            "app.main.dispatch_render",
            return_value={"structure": {"run_id": "v-1"}},
        ):
            evidence = execute_plan(plan, intent=intent, settings=settings)
        report = validate_intent_evidence(intent, evidence)
        skipped = [c for c in report["checks"] if c.get("id") == "bit_identical_replay"][0]
        assert skipped.get("skipped") is True


class TestPlanViolationL0:
    def test_rejects_empty_goal_statement(self):
        intent = _sample_intent()
        intent = intent.model_copy(
            update={"goal": IntentGoal.model_construct(statement="", justification="has justification")},
        )
        with pytest.raises(PlanViolationError) as exc:
            validate_intent(intent)
        assert exc.value.code == "idac.intent_goal_invalid"

    def test_rejects_plan_intent_mismatch(self, settings):
        intent = _sample_intent()
        plan = request_plan(intent, settings=settings)
        plan.intent_ref = "intent-wrong"
        with pytest.raises(PlanViolationError) as exc:
            validate_plan(plan, intent)
        assert exc.value.code == "idac.plan_intent_mismatch"

    def test_rejects_optimizer_execute_breach(self, settings):
        intent = _sample_intent()
        plan = request_plan(intent, settings=settings)
        plan.optimizer = {**plan.optimizer, "must_not_execute": False}
        with pytest.raises(PlanViolationError) as exc:
            validate_plan(plan, intent)
        assert exc.value.code == "idac.optimizer_must_not_execute"


class TestLearningL0:
    def test_learning_records_candidate_on_pass(self, settings, tmp_path, monkeypatch):
        monkeypatch.setenv("IDAC_LEARNING_STORE_PATH", str(tmp_path / "candidates.jsonl"))
        intent = _sample_intent()
        plan = request_plan(intent, settings=settings)
        with patch(
            "app.main.dispatch_render",
            return_value={"structure": {"run_id": "learn-1"}},
        ):
            evidence = execute_plan(plan, intent=intent, settings=settings)
        validation = validate_intent_evidence(intent, evidence)
        out = record_learning_candidate(intent=intent, evidence=evidence, validation=validation)
        assert validation["verdict"] == "pass"
        assert out["recorded"] is True
        assert out["status"] == "partial"
        assert (tmp_path / "candidates.jsonl").is_file()

    def test_no_learning_without_validated_evidence(self, settings):
        intent = _sample_intent()
        out = record_learning_candidate(
            intent=intent,
            evidence=type("E", (), {"id": "ev-1", "plan_ref": "p-1"})(),
            validation={"verdict": "fail"},
        )
        assert out["recorded"] is False


class TestRenderRuntime:
    def test_tile_scheduler_declared_note(self):
        desc = TileScheduler.describe({"atcm_summary": {"tile_count": 16}})
        assert desc["status"] == "partial"
        assert "full-frame" in desc["note"] or "per-tile" in desc["note"]


class TestShadingEngineVerified:
    """ShadingEngine verification — mode validation, waiver, evidence shape."""

    def make_engine(self) -> ShadingEngine:
        return ShadingEngine(Settings(planner_mode="heuristic"))

    def test_accepts_full_frame_dispatch(self):
        engine = self.make_engine()
        desc = engine.describe({"render_plan": {"execution_mode": "full_frame_dispatch"}})
        assert desc["execution_mode"] == "full_frame_dispatch"
        assert desc["status"] == "partial"
        assert desc["per_tile_available"] is False

    def test_accepts_full_frame_with_tile_evidence(self):
        engine = self.make_engine()
        desc = engine.describe({"render_plan": {"execution_mode": "full_frame_with_tile_evidence"}})
        assert desc["execution_mode"] == "full_frame_with_tile_evidence"
        assert "W-TILE-FAITHFUL" in desc["waivers_applied"]
        assert desc["per_tile_available"] is False

    def test_rejects_per_tile_mode(self):
        engine = self.make_engine()
        with pytest.raises(PlanViolationError) as exc:
            engine.describe({"render_plan": {"execution_mode": "per_tile"}})
        assert "W-TILE-FAITHFUL" in str(exc.value)
        assert exc.value.code == "shading.per_tile_blocked"

    def test_defaults_to_full_frame_when_mode_unknown(self):
        engine = self.make_engine()
        desc = engine.describe({"render_plan": {"execution_mode": "quantum_raster"}})
        assert desc["execution_mode"] == "full_frame_dispatch"

    def test_describe_includes_capability_and_waiver_metadata(self):
        engine = self.make_engine()
        desc = engine.describe({"render_plan": {}})
        assert "status" in desc
        assert "execution_mode" in desc
        assert "per_tile_available" in desc
        assert "per_tile_note" in desc
        assert "waivers_applied" in desc
        assert isinstance(desc["waivers_applied"], list)

    def test_handles_empty_domain_plan(self):
        engine = self.make_engine()
        desc = engine.describe({})
        assert desc["execution_mode"] == "full_frame_dispatch"
        assert desc["tile_count"] == 0

    def test_tile_count_from_tile_evidence(self):
        engine = self.make_engine()
        desc = engine.describe({
            "render_plan": {
                "execution_mode": "full_frame_with_tile_evidence",
                "tile_execution_evidence": {"tile_count": 9, "status": "partial"},
            },
        })
        assert desc["tile_count"] == 9
        assert desc["tile_evidence_status"] == "partial"

    def test_validate_mode_rejects_per_tile(self):
        engine = self.make_engine()
        with pytest.raises(PlanViolationError) as exc:
            engine.validate_mode("per_tile")
        assert exc.value.code == "shading.per_tile_blocked"

    def test_validate_mode_accepts_valid(self):
        engine = self.make_engine()
        assert engine.validate_mode("full_frame_dispatch") == "full_frame_dispatch"
        assert engine.validate_mode("full_frame_with_tile_evidence") == "full_frame_with_tile_evidence"

    def test_validate_mode_defaults_unknown(self):
        engine = self.make_engine()
        assert engine.validate_mode("hyper_raster") == "full_frame_dispatch"


class TestDomainAdapterRendering:
    def test_render_executor_components(self, settings):
        ex = RenderExecutor(settings)
        assert ex.tile_scheduler.status == "partial"
        assert ex.shading_engine.status == "partial"
        assert ex.shading_engine._settings is not None
        assert ex.postfx_engine.status == "partial"


class TestPostFXEngineVerified:
    """PostFXEngine verification — strategy validation, metadata, waiver."""

    def make_engine(self) -> PostFXEngine:
        return PostFXEngine(Settings(planner_mode="heuristic"))

    def test_upscale_strategy_valid(self):
        engine = self.make_engine()
        desc = engine.describe({
            "render_plan": {
                "math_strategies": {
                    "upscale_strategy": {"strategy": "low_res_edge_aware_upscale"},
                },
            },
        })
        assert desc["upscale_strategy"] == "low_res_edge_aware_upscale"
        assert desc["status"] == "partial"

    def test_upscale_strategy_defaults_on_unknown(self):
        engine = self.make_engine()
        desc = engine.describe({
            "render_plan": {
                "math_strategies": {
                    "upscale_strategy": {"strategy": "ai_super_res"},
                },
            },
        })
        assert desc["upscale_strategy"] == "none_full_res"

    def test_brdf_strategy_valid(self):
        engine = self.make_engine()
        desc = engine.describe({
            "render_plan": {
                "math_strategies": {
                    "brdf_strategy": {"strategy": "piecewise_cheap_tiles"},
                },
            },
        })
        assert desc["brdf_strategy"] == "piecewise_cheap_tiles"

    def test_brdf_strategy_defaults_on_unknown(self):
        engine = self.make_engine()
        desc = engine.describe({
            "render_plan": {
                "math_strategies": {
                    "brdf_strategy": {"strategy": "path_trace_full"},
                },
            },
        })
        assert desc["brdf_strategy"] == "full_brdf_tiles"

    def test_visibility_strategy_valid(self):
        engine = self.make_engine()
        desc = engine.describe({
            "render_plan": {
                "math_strategies": {
                    "visibility_strategy": {"strategy": "director_tile_grid_only"},
                },
            },
        })
        assert desc["visibility_strategy"] == "director_tile_grid_only"

    def test_visibility_strategy_defaults_on_unknown(self):
        engine = self.make_engine()
        desc = engine.describe({
            "render_plan": {
                "math_strategies": {
                    "visibility_strategy": {"strategy": "hierarchical_z_buffer"},
                },
            },
        })
        assert desc["visibility_strategy"] == "director_tile_grid_only"

    def test_adaptive_samples_from_math_strategies(self):
        engine = self.make_engine()
        desc = engine.describe({
            "render_plan": {
                "math_strategies": {
                    "adaptive_samples": {
                        "strategy": "C_i_inverse",
                        "suggested_global_spp": 8,
                    },
                },
            },
        })
        assert desc["adaptive_samples_strategy"] == "C_i_inverse"
        assert desc["adaptive_samples_suggested_spp"] == 8

    def test_director_today_shape(self):
        engine = self.make_engine()
        desc = engine.describe({"render_plan": {"math_strategies": {}}})
        dt = desc["director_today"]
        assert "upscale" in dt
        assert "brdf" in dt
        assert "visibility" in dt

    def test_per_tile_waiver(self):
        engine = self.make_engine()
        desc = engine.describe({"render_plan": {}})
        assert desc["per_tile_postfx_available"] is False
        assert "W-TILE-FAITHFUL" in desc["waivers_applied"]

    def test_empty_domain_plan_defaults(self):
        engine = self.make_engine()
        desc = engine.describe({})
        assert desc["upscale_strategy"] == "none_full_res"
        assert desc["brdf_strategy"] == "full_brdf_tiles"

    def test_validate_upscale_static_method(self):
        assert PostFXEngine.validate_upscale("low_res_edge_aware_upscale") == "low_res_edge_aware_upscale"
        assert PostFXEngine.validate_upscale("none_full_res") == "none_full_res"
        assert PostFXEngine.validate_upscale("unknown") == "none_full_res"
        assert PostFXEngine.validate_upscale(None) == "none_full_res"

    def test_validate_brdf_static_method(self):
        assert PostFXEngine.validate_brdf("piecewise_cheap_tiles") == "piecewise_cheap_tiles"
        assert PostFXEngine.validate_brdf("full_brdf_tiles") == "full_brdf_tiles"
        assert PostFXEngine.validate_brdf("unknown") == "full_brdf_tiles"
        assert PostFXEngine.validate_brdf(None) == "full_brdf_tiles"

    def test_validate_visibility_static_method(self):
        assert PostFXEngine.validate_visibility("director_tile_grid_only") == "director_tile_grid_only"
        assert PostFXEngine.validate_visibility("unknown") == "director_tile_grid_only"
        assert PostFXEngine.validate_visibility(None) == "director_tile_grid_only"


class TestRouterHttpIntegrationL1:
    def test_direct_api_uses_idac_router(self, monkeypatch):
        from fastapi.testclient import TestClient

        from app.main import app
        from app.models import MemoryboardHints

        settings = Settings(
            genblaze_base_url="https://genblaze.example.test",
            planner_mode="heuristic",
        )
        monkeypatch.setattr("app.main.get_settings", lambda: settings)
        monkeypatch.setattr("app.main.read_memoryboard", lambda *_a, **_k: MemoryboardHints())

        def _dispatch(_settings, target, client=None):
            return {"structure": {"run_id": "direct-idac-1", "preview_url": "/p/direct-idac-1"}}

        monkeypatch.setattr("app.main.dispatch_render", _dispatch)
        client = TestClient(app)
        response = client.post(
            "/api/direct",
            json={"prompt": "empty sky wall flat structure", "speed_profile": "atcm"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["context_used"]["idac"] is True
        assert body["idac"] is not None
        assert body["idac"]["validation"]["verdict"] == "pass"
        assert body["idac"]["evidence"]["execution_trace"]["run_id"] == "direct-idac-1"
        assert body["render_plan"] is not None
        assert body["atcm"]["work_model"]["label"] == "estimate_not_measured"


@pytest.mark.skip(reason="L2: multi-domain orchestration not implemented")
class TestMultiDomainL2:
    def test_compile_and_ai_in_one_session(self):
        pass
