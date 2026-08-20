"""Neural Cinematic Engine (NCE) — Mandala Visual Body adapter.

Status tags are honest: SRP declared_stub; Simulation Chamber + stills path partial.
Capability: neural_cinematic_simulation_backend
"""

from __future__ import annotations

SCHEMA_VERSION = "neural-cinematic/0.1"
CAPABILITY_ID = "neural_cinematic_simulation_backend"
HASH_ALG = "sha256"

# storyforge-mandala-contract/1.1 identityLock keys we may echo (not invent)
IDENTITY_LOCK_KEYS = (
    "species",
    "rigSpecies",
    "faceRefId",
    "bodyBuild",
    "armorId",
    "weaponId",
    "weaponHeldIn",
    "meshHash",
    "rigHash",
    "prohibitedMutations",
)
