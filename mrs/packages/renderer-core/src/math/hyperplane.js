/**
 * Hyperplane in 4D — the core slicing primitive.
 * H = { x ∈ ℝ⁴ | n·x = d }
 *
 * A hyperplane is defined by a normal vector n ∈ ℝ⁴ and offset d.
 * It divides ℝ⁴ into two half-spaces: n·x ≤ d (inside) and n·x > d (outside).
 */

import { dot, normalize, scale, add } from "./vec4.js";

/**
 * Create a hyperplane from normal and offset.
 * @param {{x,y,z,w}} normal - 4D normal vector (will be normalized)
 * @param {number} d - offset from origin
 */
export function createHyperplane(normal, d = 0) {
  return { n: normalize(normal), d };
}

/**
 * Create a hyperplane from a point and normal.
 * @param {{x,y,z,w}} point - a point on the hyperplane
 * @param {{x,y,z,w}} normal - 4D normal vector
 */
export function hyperplaneFromPointAndNormal(point, normal) {
  const n = normalize(normal);
  return { n, d: dot(n, point) };
}

/**
 * Compute signed distance from a 4D point to the hyperplane.
 * Negative = inside (behind the plane), positive = outside (in front).
 * @param {Hyperplane} plane
 * @param {{x,y,z,w}} point
 * @returns {number} signed distance
 */
export function signedDistance(plane, point) {
  return dot(plane.n, point) - plane.d;
}

/**
 * Test if a point is inside the hyperplane (on the negative side).
 */
export function isInside(plane, point) {
  return signedDistance(plane, point) <= 0;
}

/**
 * Find the intersection point of a line segment (v0→v1) with the hyperplane.
 * Returns the parameter t where the intersection occurs, such that:
 *   intersection = v0 + t * (v1 - v0)
 * t ∈ [0,1] if intersection is within the segment.
 *
 * @param {Hyperplane} plane
 * @param {{x,y,z,w}} v0 - start of segment
 * @param {{x,y,z,w}} v1 - end of segment
 * @returns {number} parameter t
 */
export function edgeIntersectT(plane, v0, v1) {
  const d0 = signedDistance(plane, v0);
  const d1 = signedDistance(plane, v1);

  // Avoid division by zero
  if (Math.abs(d0 - d1) < 1e-10) {
    return 0.5; // parallel to plane, return midpoint
  }

  return d0 / (d0 - d1);
}

/**
 * Compute the intersection point of a segment with the hyperplane.
 * @param {Hyperplane} plane
 * @param {{x,y,z,w}} v0
 * @param {{x,y,z,w}} v1
 * @returns {{x,y,z,w}} intersection point
 */
export function edgeIntersect(plane, v0, v1) {
  const t = edgeIntersectT(plane, v0, v1);
  return {
    x: v0.x + t * (v1.x - v0.x),
    y: v0.y + t * (v1.y - v0.y),
    z: v0.z + t * (v1.z - v0.z),
    w: v0.w + t * (v1.w - v0.w),
  };
}

/**
 * Intersect segment [a,b] with hyperplane H = {x | n·x = d}.
 * Returns null if no crossing within the open segment (or parallel miss);
 * otherwise { point, t } with t ∈ [0,1] and point = a + t(b−a).
 *
 * Spec alias for edgeIntersect / edgeIntersectT with explicit miss handling.
 *
 * @param {Hyperplane} plane
 * @param {{x,y,z,w}} a
 * @param {{x,y,z,w}} b
 * @returns {{ point: {x,y,z,w}, t: number } | null}
 */
export function intersectSegment(plane, a, b) {
  const da = signedDistance(plane, a);
  const db = signedDistance(plane, b);
  if (Math.abs(da) < 1e-10) return { point: { ...a }, t: 0 };
  if (Math.abs(db) < 1e-10) return { point: { ...b }, t: 1 };
  if (da * db > 0) return null; // same side — no crossing
  if (Math.abs(da - db) < 1e-10) return null; // parallel
  const t = da / (da - db);
  if (t < -1e-10 || t > 1 + 1e-10) return null;
  const tc = Math.max(0, Math.min(1, t));
  return {
    t: tc,
    point: {
      x: a.x + tc * (b.x - a.x),
      y: a.y + tc * (b.y - a.y),
      z: a.z + tc * (b.z - a.z),
      w: a.w + tc * (b.w - a.w),
    },
  };
}

/**
 * Orthogonal projection of point onto hyperplane: x' = x − (n·x − d) n.
 * @param {Hyperplane} plane
 * @param {{x,y,z,w}} point
 * @returns {{x,y,z,w}}
 */
export function projectOntoHyperplane(plane, point) {
  const dist = signedDistance(plane, point);
  return {
    x: point.x - dist * plane.n.x,
    y: point.y - dist * plane.n.y,
    z: point.z - dist * plane.n.z,
    w: point.w - dist * plane.n.w,
  };
}

/**
 * Orthonormal basis (e1,e2,e3) spanning the hyperplane (perp to n).
 * Deterministic Gram–Schmidt from canonical axes.
 * @param {{x,y,z,w}} normal - preferably unit
 * @returns {[{x,y,z,w},{x,y,z,w},{x,y,z,w}]}
 */
export function hyperplaneBasis(normal) {
  const n = normalize(normal);
  const candidates = [
    { x: 1, y: 0, z: 0, w: 0 },
    { x: 0, y: 1, z: 0, w: 0 },
    { x: 0, y: 0, z: 1, w: 0 },
    { x: 0, y: 0, z: 0, w: 1 },
  ];
  let bestIdx = 0;
  let bestDot = Infinity;
  for (let i = 0; i < candidates.length; i++) {
    const d = Math.abs(dot(n, candidates[i]));
    if (d < bestDot) {
      bestDot = d;
      bestIdx = i;
    }
  }
  const u1raw = {
    x: candidates[bestIdx].x - n.x * dot(n, candidates[bestIdx]),
    y: candidates[bestIdx].y - n.y * dot(n, candidates[bestIdx]),
    z: candidates[bestIdx].z - n.z * dot(n, candidates[bestIdx]),
    w: candidates[bestIdx].w - n.w * dot(n, candidates[bestIdx]),
  };
  const basis = [normalize(u1raw)];
  for (let i = 0; i < candidates.length; i++) {
    if (i === bestIdx) continue;
    let v = { ...candidates[i] };
    v = {
      x: v.x - n.x * dot(n, v),
      y: v.y - n.y * dot(n, v),
      z: v.z - n.z * dot(n, v),
      w: v.w - n.w * dot(n, v),
    };
    for (const b of basis) {
      const db = dot(b, v);
      v = { x: v.x - b.x * db, y: v.y - b.y * db, z: v.z - b.z * db, w: v.w - b.w * db };
    }
    if (Math.sqrt(dot(v, v)) > 1e-6) {
      basis.push(normalize(v));
      if (basis.length === 3) break;
    }
  }
  return basis;
}

/**
 * Classify vertices of a triangle against the hyperplane.
 * Returns array of signed distances.
 */
export function classifyTriangle(plane, v0, v1, v2) {
  return [signedDistance(plane, v0), signedDistance(plane, v1), signedDistance(plane, v2)];
}

/**
 * Create a rotation in SO(4) that rotates the hyperplane normal.
 * This allows "looking around" in 4D by rotating the slicing plane.
 *
 * @param {{x,y,z,w}} currentNormal - current hyperplane normal
 * @param {{x,y,z,w}} targetDirection - desired new normal direction
 * @returns {Function} rotation function: vec4 → vec4
 */
export function rotationAligningNormal(currentNormal, targetDirection) {
  const from = normalize(currentNormal);
  const to = normalize(targetDirection);

  // If already aligned, return identity
  if (
    Math.abs(from.x - to.x) < 1e-6 &&
    Math.abs(from.y - to.y) < 1e-6 &&
    Math.abs(from.z - to.z) < 1e-6 &&
    Math.abs(from.w - to.w) < 1e-6
  ) {
    return (p) => ({ ...p });
  }

  // If opposite, rotate 180° in any plane containing the normal
  if (
    Math.abs(from.x + to.x) < 1e-6 &&
    Math.abs(from.y + to.y) < 1e-6 &&
    Math.abs(from.z + to.z) < 1e-6 &&
    Math.abs(from.w + to.w) < 1e-6
  ) {
    // 180° rotation around a perpendicular axis
    // Find a perpendicular vector
    const perp = findPerpendicular(from);
    return (p) => rotate180(p, perp);
  }

  // General case: Householder reflection or Givens rotation
  // Use a rotation that takes `from` to `to`
  return createRotationFromTo(from, to);
}

function findPerpendicular(v) {
  // Find a vector perpendicular to v in 4D
  if (Math.abs(v.x) < 0.9) {
    return normalize({ x: 1, y: 0, z: 0, w: 0 });
  }
  return normalize({ x: 0, y: 1, z: 0, w: 0 });
}

function rotate180(p, axis) {
  // 180° rotation around an axis: reflect through the axis
  const d = dot(axis, p);
  return {
    x: 2 * d * axis.x - p.x,
    y: 2 * d * axis.y - p.y,
    z: 2 * d * axis.z - p.z,
    w: 2 * d * axis.w - p.w,
  };
}

function createRotationFromTo(from, to) {
  // Rotation that takes vector `from` to vector `to`
  // Uses the formula: R = I + [v][v]^T / (1 + f·t) where v = t - f
  // Actually, simpler: use Householder-like reflection
  // R = 2 * (to ⊗ from) / (from·from) - I ... no, that's not right either

  // Correct approach: use the fact that R = I + sin(θ)[u]× + (1-cos(θ))[u]×²
  // in 4D, rotation is in a plane. We need to find the rotation plane and angle.

  // Simpler: use two reflections
  // R = H_to * H_from where H_v = I - 2*v*v^T/(v^T*v)
  // This rotates from to to by reflecting first through from, then through to

  const hFrom = (p) => {
    const d = dot(from, p);
    return {
      x: p.x - 2 * d * from.x,
      y: p.y - 2 * d * from.y,
      z: p.z - 2 * d * from.z,
      w: p.w - 2 * d * from.w,
    };
  };

  const hTo = (p) => {
    const d = dot(to, p);
    return {
      x: p.x - 2 * d * to.x,
      y: p.y - 2 * d * to.y,
      z: p.z - 2 * d * to.z,
      w: p.w - 2 * d * to.w,
    };
  };

  return (p) => hTo(hFrom(p));
}

/**
 * Animate the hyperplane offset over time.
 * @param {Hyperplane} base - base hyperplane
 * @param {number} speed - offset change per second
 * @param {number} t - time in seconds
 * @returns {Hyperplane}
 */
export function animateHyperplane(base, speed, t) {
  return {
    n: base.n,
    d: base.d + speed * t,
  };
}
