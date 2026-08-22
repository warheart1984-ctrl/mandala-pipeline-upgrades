"""Physical invariants — Python encoding of the document method.

Encoding spec (do not invent another):
  mrs/packages/renderer-core/src/render/rt4d/math/physical_invariants.md

Pattern: Invariant → boolean predicate on states.
Meta: invariant_predicate_result(id, ok, evidence) → {id, ok, evidence}

JS SoT for the three document predicates: physicalInvariants.js
This file ports those three, then instantiates the same method for other
invariants the finished Mandala/MRS project actually claims.

Physical validity (CONTRACT.md layer 3) remains declared. A passing
predicate is not a physics proof. Rosetta maps shared state only.
"""

from __future__ import annotations

import math
from typing import Any, Iterable, Mapping, Sequence

# Default absolute tolerance used by document predicate forms.
PHYSICAL_INVARIANT_TOL = 1e-9

# Document / proto / holography constants as claimed in-repo (not invented).
PROTO_MASS_BOUND = 1e-2  # mandala/proto/constitution.mjs numericalErrorBound
JOINT_FLIP_DEG = 60  # character/holography/boundary-appearance.mjs
K_LOCK = 0.8
K_LOCK_DRIFT = 0.08
RHO_SPARSE = 0.05  # mandala/engine/chamber/sparse-cull.mjs
MINKOWSKI_C = 1.0


# ---------------------------------------------------------------------------
# Document predicates (physical_invariants.md §1–3)
# ---------------------------------------------------------------------------


def _as_components(v: Any) -> tuple[float, ...]:
    if isinstance(v, Mapping):
        if "w" in v or "z" in v:
            return (
                float(v.get("x", 0)),
                float(v.get("y", 0)),
                float(v.get("z", 0)),
                float(v.get("w", 0)),
            )
        return (float(v.get("x", 0)), float(v.get("y", 0)))
    if isinstance(v, (list, tuple)):
        return tuple(float(x) for x in v)
    raise TypeError("squared_norm: expected array or {x,y[,z,w]}")


def squared_norm(v: Any) -> float:
    return sum(c * c for c in _as_components(v))


def length_preserved(v: Any, v_rot: Any, tol: float = PHYSICAL_INVARIANT_TOL) -> bool:
    """Geometry: ‖v‖² = ‖Rv‖² when RᵀR = I. Document: lengthPreserved."""
    return abs(squared_norm(v) - squared_norm(v_rot)) < tol


def energy_conserved(
    e_before: float, e_after: float, tol: float = PHYSICAL_INVARIANT_TOL
) -> bool:
    """Calculus: dE/dt = 0 ⇒ E(t1) = E(t2). Document: energyConserved."""
    return abs(float(e_before) - float(e_after)) < tol


def radial_distance_invariant(
    x: float, y: float, xp: float, yp: float, tol: float = PHYSICAL_INVARIANT_TOL
) -> bool:
    """Trig: x'² + y'² = x² + y². Document: radialDistanceInvariant."""
    return abs((x * x + y * y) - (xp * xp + yp * yp)) < tol


def rotate2d(x: float, y: float, theta: float) -> dict[str, float]:
    """Explicit 2D rotation from the document's trigonometric section."""
    c = math.cos(theta)
    s = math.sin(theta)
    return {"x": x * c - y * s, "y": x * s + y * c}


def pythagorean_identity_holds(
    theta: float, tol: float = PHYSICAL_INVARIANT_TOL
) -> bool:
    c = math.cos(theta)
    s = math.sin(theta)
    return abs(c * c + s * s - 1.0) < tol


def length_preserved_under_2d_rotation(
    x: float, y: float, theta: float, tol: float = PHYSICAL_INVARIANT_TOL
) -> bool:
    r = rotate2d(x, y, theta)
    return radial_distance_invariant(x, y, r["x"], r["y"], tol)


def length_preserved4(v: Any, v_rot: Any, tol: float = PHYSICAL_INVARIANT_TOL) -> bool:
    """Same geometric invariant on vec4. Does not add new physics."""
    return abs(squared_norm(v) - squared_norm(v_rot)) < tol


# Document names (physical_invariants.md / physicalInvariants.js).
lengthPreserved = length_preserved
energyConserved = energy_conserved
radialDistanceInvariant = radial_distance_invariant
pythagoreanIdentityHolds = pythagorean_identity_holds
lengthPreservedUnder2dRotation = length_preserved_under_2d_rotation
lengthPreserved4 = length_preserved4


def invariant_predicate_result(
    inv_id: str, ok: bool, evidence: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Meta-pattern: every invariant collapses to a boolean on states."""
    return {"id": inv_id, "ok": bool(ok), "evidence": dict(evidence or {})}


invariantPredicateResult = invariant_predicate_result


PHYSICAL_INVARIANTS: tuple[dict[str, str], ...] = (
    {
        "id": "PI-GEO-LENGTH",
        "branch": "geometry",
        "statement": "Orthogonal transforms preserve squared length: ‖v‖² = ‖Rv‖² when RᵀR = I",
        "predicate": "lengthPreserved",
        "status": "tested",
        "contract": "projection",
    },
    {
        "id": "PI-CALC-ENERGY",
        "branch": "calculus",
        "statement": "dE/dt = 0 ⇒ E(t) constant ⇒ E(t1) = E(t2)",
        "predicate": "energyConserved",
        "status": "tested",
        "contract": "projection",
    },
    {
        "id": "PI-TRIG-RADIAL",
        "branch": "trigonometry",
        "statement": "2D rotation with cos²θ+sin²θ=1 preserves x²+y²",
        "predicate": "radialDistanceInvariant",
        "status": "tested",
        "contract": "projection",
    },
)


# ---------------------------------------------------------------------------
# Same method, other invariants the finished project actually claims
# ---------------------------------------------------------------------------


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


def so4_isometry(r: Sequence[Sequence[float]], tol: float = 1e-6) -> bool:
    """Math form of CONTRACT.md / validateSO4: det(R)=1 and RᵀR = I₄.

    Status: mathematical **enforced** on JS/CPU. Physical validity **declared**.
    """
    n = 4
    if len(r) != n or any(len(row) != n for row in r):
        return False
    det = _mat4_det(r)
    if abs(det - 1.0) > tol:
        return False
    rt_r = [[_dot(_col(r, i), _col(r, j)) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            expected = 1.0 if i == j else 0.0
            if abs(rt_r[i][j] - expected) > tol:
                return False
    return True


def _col(m: Sequence[Sequence[float]], j: int) -> list[float]:
    return [float(m[i][j]) for i in range(len(m))]


def _mat4_det(m: Sequence[Sequence[float]]) -> float:
    # Same expansion as so4.js mat4det (row-major 4×4).
    a = [[float(m[i][j]) for j in range(4)] for i in range(4)]
    def minor3(r0, r1, r2, c0, c1, c2):
        return (
            a[r0][c0] * (a[r1][c1] * a[r2][c2] - a[r1][c2] * a[r2][c1])
            - a[r0][c1] * (a[r1][c0] * a[r2][c2] - a[r1][c2] * a[r2][c0])
            + a[r0][c2] * (a[r1][c0] * a[r2][c1] - a[r1][c1] * a[r2][c0])
        )
    return (
        a[0][0] * minor3(1, 2, 3, 1, 2, 3)
        - a[0][1] * minor3(1, 2, 3, 0, 2, 3)
        + a[0][2] * minor3(1, 2, 3, 0, 1, 3)
        - a[0][3] * minor3(1, 2, 3, 0, 1, 2)
    )


def hyperplane_incidence(
    n: Sequence[float], d: float, x: Sequence[float], tol: float = PHYSICAL_INVARIANT_TOL
) -> bool:
    """H = {x | n·x = d}. Math **enforced** (slice). Physical slice-as-physics **declared**."""
    return abs(_dot(n, x) - float(d)) <= tol


def hyperplane_basis_orthonormal(
    n: Sequence[float], basis: Sequence[Sequence[float]], tol: float = 1e-9
) -> bool:
    """Slice basis orthonormal and ⊥ n (CONTRACT.md invariants row)."""
    if len(basis) != 3:
        return False
    nn = math.sqrt(sum(float(c) * float(c) for c in n))
    if nn < 1e-15:
        return False
    nh = [float(c) / nn for c in n]
    for e in basis:
        if abs(_dot(nh, e)) > tol:
            return False
        if abs(math.sqrt(sum(float(c) * float(c) for c in e)) - 1.0) > tol:
            return False
    for i in range(3):
        for j in range(i + 1, 3):
            if abs(_dot(basis[i], basis[j])) > tol:
                return False
    return True


def scalar_mass_conserved(
    phi_before: Iterable[float],
    phi_after: Iterable[float],
    bound: float = PROTO_MASS_BOUND,
) -> bool:
    """proto.scalar-mass-conservation: |Σφ' − Σφ| ≤ numerical_error_bound.

    Proto AAIS gate **enforced**. RHFD Claim B / physical vacuum **not claimed**.
    """
    return abs(sum(float(x) for x in phi_after) - sum(float(x) for x in phi_before)) <= bound


def no_superluminal_defect(chebyshev_step: float, max_step: float = 1.0) -> bool:
    """mandala.engine.no-superluminal-defect: Chebyshev cells/dt ≤ maxStep. **partial**."""
    return float(chebyshev_step) <= float(max_step)


def unit_timelike_normal(
    n_up: Sequence[float],
    g4: Sequence[float] | None = None,
    tol: float = 1e-12,
) -> bool:
    """g_μν n^μ n^ν = −1 (projector.assertNormalUnit). Holography **partial**; not GR."""
    g = list(g4) if g4 is not None else [-1.0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    n = [float(x) for x in n_up]
    s = 0.0
    for mu in range(4):
        for nu in range(4):
            s += g[mu * 4 + nu] * n[mu] * n[nu]
    return abs(s + 1.0) <= tol


def induced_hij_is_delta(h: Sequence[float], tol: float = 1e-12) -> bool:
    """Flat Minkowski → h_ij = δ_ij (inducedMetricHij). Computational dual **partial**."""
    if len(h) < 9:
        return False
    eye = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
    return all(abs(float(h[i]) - eye[i]) <= tol for i in range(9))


def null_constraint_ok(
    dx: float, dy: float, dz: float, dt: float, c: float = MINKOWSKI_C
) -> bool:
    """metric.nullConstraintOk: |Δx| ≤ c|Δt|. Declared stub, not a geodesic solver."""
    spatial = math.hypot(float(dx), float(dy), float(dz))
    return spatial <= abs(float(c) * float(dt)) + 1e-9


def rho_in_unit_interval(rho: Iterable[float], lo: float = 0.0, hi: float = 1.0) -> bool:
    """EGT ρ used as a correlation proxy in [0,1] (holo-loop clamps). **partial**."""
    vals = [float(x) for x in rho]
    return bool(vals) and all(lo <= v <= hi for v in vals)


def w_ij_in_unit_interval(weights: Iterable[float], lo: float = 0.0, hi: float = 1.0) -> bool:
    """EGT edges w_ij ∈ [0,1] as claimed by HOLOGRAPHIC_BULK_BOUNDARY.md. **partial**."""
    vals = [float(x) for x in weights]
    return bool(vals) and all(lo <= v <= hi for v in vals)


def k_lock_stable(
    k: float,
    k_prev: float | None = None,
    k_lock: float = K_LOCK,
    drift: float = K_LOCK_DRIFT,
) -> bool:
    """Bone lock: |K| ≥ kLock and | |K| − |K_prev| | < 0.08. Character **partial**."""
    k_abs = abs(float(k))
    prev = k_abs if k_prev is None else abs(float(k_prev))
    return k_abs >= float(k_lock) and abs(k_abs - prev) < float(drift)


def dhat_joint_flip(align_cos: float, joint_deg: float = JOINT_FLIP_DEG) -> bool:
    """Joint detector: |Ê_i · Ê_j| < cos(60°). Heuristic **partial**, not a conservation law."""
    return abs(float(align_cos)) < math.cos(math.radians(float(joint_deg)))


def bulk_egt_coupling(bulk_stepped: bool, egt_updated: bool) -> bool:
    """CIEMS inv-bulk-egt-coupling: no bulk step without updateEGT. Soft **partial**."""
    return (not bool(bulk_stepped)) or bool(egt_updated)


def ads_cft_claim_b_not_claimed() -> bool:
    """AdS/CFT / RT / von Neumann: project says not claimed. Predicate must not pass."""
    return False


# Project instantiations: same encoding (id, branch, statement, predicate, status).
PROJECT_INVARIANTS: tuple[dict[str, str], ...] = (
    {
        "id": "math4d.so4-isometry",
        "branch": "geometry",
        "statement": "det(R_4)=1 and R_4ᵀ R_4 = I_4 (SO(4) isometry / oriented volume)",
        "predicate": "so4_isometry",
        "status": "enforced",  # JS/CPU math. Physical validity declared (CONTRACT.md layer 3).
        "contract": "projection",
        "physical": "declared",
    },
    {
        "id": "math4d.hyperplane-incidence",
        "branch": "geometry",
        "statement": "H = {x ∈ ℝ⁴ | n·x = d}; slice basis orthonormal and ⊥ n",
        "predicate": "hyperplane_incidence",
        "status": "enforced",
        "contract": "projection",
        "physical": "declared",
    },
    {
        "id": "proto.scalar-mass-conservation",
        "branch": "calculus",
        "statement": "|Σφ' − Σφ| ≤ numerical_error_bound (default 1e-2)",
        "predicate": "scalar_mass_conserved",
        "status": "enforced",  # AAIS gate. Not Claim B / physical vacuum.
        "contract": "proto",
        "physical": "declared",
    },
    {
        "id": "mandala.engine.no-superluminal-defect",
        "branch": "calculus",
        "statement": "Defect Chebyshev step ≤ maxDefectStep (default 1 cell/dt)",
        "predicate": "no_superluminal_defect",
        "status": "partial",
        "contract": "proto",
        "physical": "declared",
    },
    {
        "id": "holo.unit-timelike-normal",
        "branch": "geometry",
        "statement": "g_μν n^μ n^ν = −1",
        "predicate": "unit_timelike_normal",
        "status": "partial",
        "contract": "holography",
        "physical": "declared",
    },
    {
        "id": "holo.induced-hij",
        "branch": "geometry",
        "statement": "h_ij = g_ij − g_0i g_0j / g_00; flat Minkowski → δ_ij",
        "predicate": "induced_hij_is_delta",
        "status": "partial",
        "contract": "holography",
        "physical": "declared",
    },
    {
        "id": "holo.null-constraint",
        "branch": "calculus",
        "statement": "|Δx| ≤ c|Δt| (lattice units; not a continuum null geodesic)",
        "predicate": "null_constraint_ok",
        "status": "declared",
        "contract": "holography",
        "physical": "declared",
    },
    {
        "id": "holo.rho-bounds",
        "branch": "geometry",
        "statement": "ρ ∈ [0,1] as EGT correlation proxy (not von Neumann)",
        "predicate": "rho_in_unit_interval",
        "status": "partial",
        "contract": "holography",
        "physical": "declared",
    },
    {
        "id": "holo.w-ij-bounds",
        "branch": "geometry",
        "statement": "w_ij ∈ [0,1] on EGT edges",
        "predicate": "w_ij_in_unit_interval",
        "status": "partial",
        "contract": "holography",
        "physical": "declared",
    },
    {
        "id": "character.k-lock",
        "branch": "geometry",
        "statement": "Bone lock: |K| ≥ 0.8 and |Δ|K|| < 0.08",
        "predicate": "k_lock_stable",
        "status": "partial",
        "contract": "character",
        "physical": "declared",
    },
    {
        "id": "character.dhat-60",
        "branch": "geometry",
        "statement": "Joint if |d̂^i · d̂^j| < cos(60°)",
        "predicate": "dhat_joint_flip",
        "status": "partial",
        "contract": "character",
        "physical": "declared",
    },
    {
        "id": "inv-bulk-egt-coupling",
        "branch": "calculus",
        "statement": "No bulk step without corresponding updateEGT (CIEMS soft)",
        "predicate": "bulk_egt_coupling",
        "status": "partial",
        "contract": "holography",
        "physical": "declared",
    },
    {
        "id": "holo.ads-cft-claim-b",
        "branch": "geometry",
        "statement": "AdS/CFT / RT / von Neumann / HRT — not claimed",
        "predicate": "ads_cft_claim_b_not_claimed",
        "status": "declared",
        "contract": "holography",
        "physical": "not-claimed",
    },
    {
        "id": "EI-RADIOMETRIC",
        "branch": "calculus",
        "statement": "Lambertian4D BRDF = 3ρ/(4π), pdf = 3cosθ/(4π) (normalization tests)",
        "predicate": "energyConserved",
        "status": "tested",
        "contract": "projection",
        "physical": "declared",
    },
)


ALL_INVARIANTS: tuple[dict[str, str], ...] = PHYSICAL_INVARIANTS + PROJECT_INVARIANTS

PREDICATES = {
    "lengthPreserved": length_preserved,
    "energyConserved": energy_conserved,
    "radialDistanceInvariant": radial_distance_invariant,
    "so4_isometry": so4_isometry,
    "hyperplane_incidence": hyperplane_incidence,
    "hyperplane_basis_orthonormal": hyperplane_basis_orthonormal,
    "scalar_mass_conserved": scalar_mass_conserved,
    "no_superluminal_defect": no_superluminal_defect,
    "unit_timelike_normal": unit_timelike_normal,
    "induced_hij_is_delta": induced_hij_is_delta,
    "null_constraint_ok": null_constraint_ok,
    "rho_in_unit_interval": rho_in_unit_interval,
    "w_ij_in_unit_interval": w_ij_in_unit_interval,
    "k_lock_stable": k_lock_stable,
    "dhat_joint_flip": dhat_joint_flip,
    "bulk_egt_coupling": bulk_egt_coupling,
    "ads_cft_claim_b_not_claimed": ads_cft_claim_b_not_claimed,
}


def check(inv_id: str, state: Mapping[str, Any]) -> dict[str, Any]:
    """Run the document method: look up predicate, return {id, ok, evidence}.

    `state` is the predicate's keyword arguments. Missing state → ok False,
    not a fabricated physical pass.
    """
    inv = next((i for i in ALL_INVARIANTS if i["id"] == inv_id), None)
    if inv is None:
        return invariant_predicate_result(inv_id, False, {"error": "unknown id"})
    fn = PREDICATES.get(inv["predicate"])
    if fn is None:
        return invariant_predicate_result(inv_id, False, {"error": "no predicate"})
    try:
        ok = bool(fn(**state))
    except TypeError as exc:
        return invariant_predicate_result(
            inv_id, False, {"error": str(exc), "status": inv["status"]}
        )
    return invariant_predicate_result(
        inv_id,
        ok,
        {
            "status": inv["status"],
            "physical": inv.get("physical", "declared"),
            "contract": inv.get("contract", ""),
        },
    )


def catalog() -> list[dict[str, str]]:
    return [dict(row) for row in ALL_INVARIANTS]


if __name__ == "__main__":
    r = rotate2d(3, 4, math.pi / 6)
    assert length_preserved({"x": 3, "y": 4}, r)
    assert energy_conserved(1.0, 1.0)
    assert radial_distance_invariant(3, 4, r["x"], r["y"])
    assert scalar_mass_conserved([1.0, 2.0], [1.5, 1.5])
    assert unit_timelike_normal((1.0, 0.0, 0.0, 0.0))
    assert induced_hij_is_delta((1, 0, 0, 0, 1, 0, 0, 0, 1))
    assert bulk_egt_coupling(True, True)
    assert not ads_cft_claim_b_not_claimed()
    print("physical_invariants.py smoke: ok (%d catalog entries)" % len(ALL_INVARIANTS))
