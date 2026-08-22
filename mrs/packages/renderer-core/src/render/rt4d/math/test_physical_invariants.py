"""Smoke for the document encoding: Invariant → boolean predicate on states."""

from __future__ import annotations

import math
import unittest

from physical_invariants import (
    ALL_INVARIANTS,
    PHYSICAL_INVARIANTS,
    PHYSICAL_INVARIANT_TOL,
    ads_cft_claim_b_not_claimed,
    bulk_egt_coupling,
    check,
    dhat_joint_flip,
    energy_conserved,
    hyperplane_basis_orthonormal,
    hyperplane_incidence,
    induced_hij_is_delta,
    invariant_predicate_result,
    k_lock_stable,
    length_preserved,
    length_preserved_under_2d_rotation,
    null_constraint_ok,
    pythagorean_identity_holds,
    radial_distance_invariant,
    rho_in_unit_interval,
    rotate2d,
    scalar_mass_conserved,
    so4_isometry,
    unit_timelike_normal,
    w_ij_in_unit_interval,
)


class DocumentPredicates(unittest.TestCase):
    def test_catalog_has_three_document_invariants(self):
        self.assertEqual(len(PHYSICAL_INVARIANTS), 3)
        for inv in PHYSICAL_INVARIANTS:
            self.assertEqual(inv["status"], "tested")
            self.assertTrue(inv["id"] and inv["predicate"] and inv["statement"])

    def test_length_preserved_rotation(self):
        for theta in (0, math.pi / 6, math.pi / 4, math.pi / 2, 1.234, -2.5):
            r = rotate2d(3, 4, theta)
            self.assertTrue(length_preserved({"x": 3, "y": 4}, r))
            self.assertTrue(radial_distance_invariant(3, 4, r["x"], r["y"]))
            self.assertTrue(length_preserved_under_2d_rotation(3, 4, theta))

    def test_length_preserved_rejects_stretch(self):
        self.assertFalse(length_preserved({"x": 1, "y": 0}, {"x": 2, "y": 0}))

    def test_pythagorean(self):
        for i in range(20):
            theta = (i / 20) * 4 * math.pi - 2 * math.pi
            self.assertTrue(pythagorean_identity_holds(theta))

    def test_energy(self):
        self.assertTrue(energy_conserved(42.5, 42.5))
        self.assertFalse(energy_conserved(1, 1.001, 1e-9))

    def test_meta_pattern(self):
        ok = invariant_predicate_result("PI-CALC-ENERGY", energy_conserved(3, 3), {"E_before": 3})
        self.assertEqual(ok["id"], "PI-CALC-ENERGY")
        self.assertTrue(ok["ok"])
        self.assertEqual(ok["evidence"]["E_before"], 3)


class ProjectPredicates(unittest.TestCase):
    def test_so4_identity(self):
        i4 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        self.assertTrue(so4_isometry(i4))
        bad = [[2, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        self.assertFalse(so4_isometry(bad))

    def test_hyperplane(self):
        n = (0, 0, 0, 1)
        self.assertTrue(hyperplane_incidence(n, 0, (1, 2, 3, 0)))
        self.assertFalse(hyperplane_incidence(n, 0, (1, 2, 3, 1)))
        basis = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0))
        self.assertTrue(hyperplane_basis_orthonormal(n, basis))

    def test_mass_and_holo(self):
        self.assertTrue(scalar_mass_conserved([1.0, 2.0], [1.5, 1.5]))
        self.assertFalse(scalar_mass_conserved([0.0], [1.0], bound=1e-2))
        self.assertTrue(unit_timelike_normal((1.0, 0.0, 0.0, 0.0)))
        self.assertTrue(induced_hij_is_delta((1, 0, 0, 0, 1, 0, 0, 0, 1)))
        self.assertTrue(null_constraint_ok(0.5, 0, 0, 1.0))
        self.assertFalse(null_constraint_ok(2.0, 0, 0, 1.0))
        self.assertTrue(rho_in_unit_interval([0.0, 0.5, 1.0]))
        self.assertTrue(w_ij_in_unit_interval([0.1, 1.0]))
        self.assertTrue(k_lock_stable(0.85, 0.84))
        self.assertTrue(dhat_joint_flip(0.0))
        self.assertFalse(dhat_joint_flip(1.0))
        self.assertTrue(bulk_egt_coupling(True, True))
        self.assertFalse(bulk_egt_coupling(True, False))
        self.assertFalse(ads_cft_claim_b_not_claimed())

    def test_check_missing_state_is_not_a_physical_pass(self):
        result = check("proto.scalar-mass-conservation", {})
        self.assertFalse(result["ok"])

    def test_ads_cft_check_never_passes(self):
        result = check("holo.ads-cft-claim-b", {})
        self.assertFalse(result["ok"])
        self.assertEqual(result["evidence"].get("physical"), "not-claimed")

    def test_catalog_physical_honesty(self):
        self.assertGreaterEqual(len(ALL_INVARIANTS), 3)
        for inv in ALL_INVARIANTS:
            if inv["id"].startswith("PI-"):
                continue
            self.assertIn(inv.get("physical", "declared"), ("declared", "not-claimed"))


if __name__ == "__main__":
    unittest.main()
