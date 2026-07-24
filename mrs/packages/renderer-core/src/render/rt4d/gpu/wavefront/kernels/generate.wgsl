// generate.wgsl — Phase B/C declared stub (Drive-G-1)
struct Ray { origin : vec3<f32>, dir : vec3<f32>, }
@group(0) @binding(0) var<storage, read_write> rays : array<Ray>;
struct CameraUniform {
  origin : vec3<f32>, _pad0 : f32,
  forward : vec3<f32>, _pad1 : f32,
  right : vec3<f32>, _pad2 : f32,
  up : vec3<f32>, _pad3 : f32,
  width : u32, height : u32,
}
@group(0) @binding(1) var<uniform> camera : CameraUniform;
@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id : vec3<u32>) {
  if (id.x >= camera.width || id.y >= camera.height) { return; }
  let nx = (f32(id.x) + 0.5) / f32(camera.width);
  let ny = (f32(id.y) + 0.5) / f32(camera.height);
  let dir = normalize(camera.forward + (nx * 2.0 - 1.0) * camera.right + (1.0 - ny * 2.0) * camera.up);
  let index = id.y * camera.width + id.x;
  rays[index].origin = camera.origin;
  rays[index].dir = dir;
}
