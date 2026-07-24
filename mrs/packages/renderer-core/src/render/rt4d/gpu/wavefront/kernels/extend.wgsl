// extend.wgsl — Phase B/C declared stub
struct Ray { origin : vec3<f32>, dir : vec3<f32>, }
@group(0) @binding(0) var<storage, read_write> rays : array<Ray>;
@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id : vec3<u32>) { _ = id; }
