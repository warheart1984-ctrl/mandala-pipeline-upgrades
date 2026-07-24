// accumulate.wgsl — Phase B/C declared stub
@group(0) @binding(0) var<storage, read> accum : array<vec4<f32>>;
@group(0) @binding(1) var outputTex : texture_storage_2d<rgba8unorm, write>;
@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id : vec3<u32>) {
  let index = id.y * 1024u + id.x;
  textureStore(outputTex, vec2<i32>(i32(id.x), i32(id.y)), vec4<f32>(accum[index].xyz, 1.0));
}
