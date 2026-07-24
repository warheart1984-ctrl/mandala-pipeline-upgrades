// shade.wgsl — Phase B/C declared stub
struct Ray { origin : vec3<f32>, dir : vec3<f32>, }
@group(0) @binding(0) var<storage, read> rays : array<Ray>;
@group(0) @binding(1) var<storage, read_write> accum : array<vec4<f32>>;
@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id : vec3<u32>) {
  let index = id.y * 1024u + id.x;
  let d = rays[index].dir;
  accum[index] = vec4<f32>(0.5 * (d.x + 1.0), 0.5 * (d.y + 1.0), 0.5 * (d.z + 1.0), 1.0);
}
