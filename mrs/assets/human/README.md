# Human face assets (Engine3D)

| File | Role | Status |
|------|------|--------|
| `HumanFaceNeutral.glb` | Neutral face mesh | **Fixture** in-repo (low tris) unless replaced |
| `HumanFaceRigged.glb` | Bones + blendshapes | **Fixture** in-repo unless replaced |

## Operator upgrade

Overwrite these same filenames with licensed production assets — no API changes.

Full workflow: [ENGINE3D_FACERIG_OPERATOR_GUIDE_v1.0](../../../docs/4d-engine/engine3d/ENGINE3D_FACERIG_OPERATOR_GUIDE_v1.0.md) · [topology checklist](../../../docs/4d-engine/engine3d/ENGINE3D_FACE_TOPOLOGY_CHECKLIST_v1.0.md) · [Blender export preset](../../../docs/4d-engine/engine3d/ENGINE3D_FACE_BLENDER_EXPORT_PRESET_v1.0.md)

Validate a rigged GLB:

```bash
cd mrs/packages/engine3d-core
npm run validate:face-glb -- ../../assets/human/HumanFaceRigged.glb
```

## Constitutional

See [ENGINE3D_FACE_STRUCTURE_SPEC_v1.0](../../../docs/4d-engine/engine3d/ENGINE3D_FACE_STRUCTURE_SPEC_v1.0.md).

- Engine3D owns face geometry.
- In-repo GLBs are **fixtures** for CI/demos — not a 20k–40k production sculpt.
- Operators may overwrite these filenames with licensed production assets without API changes.

## Regenerate fixtures

```bash
cd mrs/packages/engine3d-core
node scripts/build-face-fixture-glb.mjs
```

## Required bones / blendshapes

Bones: Head, Jaw, LeftEye, RightEye, LeftBrow, RightBrow, UpperLip, LowerLip  

Blendshapes: Smile, Frown, BlinkLeft, BlinkRight, Squint, WideEyes, MouthOpen, MouthNarrow
