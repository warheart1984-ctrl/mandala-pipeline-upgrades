// Lens Effects — Bokeh Depth of Field & Optical Vignette
// Full-screen quad pass applied after TAA to avoid sharpening grain into bokeh.
// Uses 60-degree increment hexagonal bokeh disk sampling with brightness-weighted blending.

struct FrameParams {
  sampleIndex: f32,
  maxDepth: f32,
  width: f32,
  height: f32,
  seed: f32,
  _p0: f32,
  _p1: f32,
  _p2: f32,
  uvCoord: vec2<f32>,
};

@group(0) @binding(0) var<uniform> frame: FrameParams;
@group(0) @binding(1) var<storage, read> color_tex: array<vec4<f32>>; // TAA output
@group(0) @binding(2) var<storage, read> depth_tex: array<f32>; // Depth buffer
@group(0) @binding(3) var<storage, read_write> output_tex: array<vec4<f32>>; // Accumulation buffer

const PI: f32 = 3.14159265;
const EPS: f32 = 1e-6;

fn pcgHash(input: u32) -> u32 {
  var state = input * 747796405u + 2891336453u;
  let word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
  return (word >> 22u) ^ word;
}

fn randFloat(seed: ptr<function, u32>) -> f32 {
  *seed = pcgHash(*seed);
  return f32(*seed) / 4294967295.0;
}

// Hexagonal bokeh disk sample kernel (6 samples at 60-degree intervals)
const hex_bokeh_samples: array<vec2<f32>, 6> = array<vec2<f32>, 6>(
  vec2<f32>(1.0, 0.0),
  vec2<f32>(0.5, 0.86602540378),
  vec2<f32>(-0.5, 0.86602540378),
  vec2<f32>(-1.0, 0.0),
  vec2<f32>(-0.5, -0.86602540378),
  vec2<f32>(0.5, -0.86602540378)
);

// Optical vignette function — Gaussian falloff
fn vignette(radius: f32, strength: f32) -> f32 {
  return exp(-strength * radius * radius);
}

// Main image processing function
@compute @workgroup_size(64)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let idx = u32(gid.x);
  let total = u32(frame.width * frame.height);
  if (idx >= total) { return; }
  
  let color = color_tex[idx];
  let depth = depth_tex[idx];
  let u = frame.uvCoord.x;
  let v = frame.uvCoord.y;
  
  // Calculate circle of confusion based on depth and camera parameters
  let coc = depth * frame.lensRadius / max(frame.focalDistance, 0.1) * 0.5;
  let coc_size = max(coc, 0.001);
  
  // Bokeh accumulation — hexagonal disk sampling
  let bokeh_color = vec4<f32>(0.0);
  let sample_weight_sum = 0.0;
  
  for (var i = 0u; i < 6u; i = i + 1u) {
    let sample = hex_bokeh_samples[i];
    let sample_pos = vec2<f32>(u + sample.x * coc_size, v + sample.y * coc_size);
    
    // Sample with jitter for anti-aliasing
    let seed_val = frame.seed * 4294967295.0 + f32(idx) * 1000.0 + f32(i);
    let jitter = vec2<f32>(
      randFloat(&seed_val) * 0.125,
      randFloat(&seed_val * 4294967295.0 + 12345u) * 0.125
    );
    
    let sample_pos_jittered = sample_pos + jitter;
    
    // Clamp to image bounds
    let clamped_x = clamp(sample_pos_jittered.x, 0.0, frame.width - 1.0);
    let clamped_y = clamp(sample_pos_jittered.y, 0.0, frame.height - 1.0);
    
    let sample_idx = u32(clamped_y * frame.width + clamped_x);
    let sample_color = color_tex[sample_idx];
    
    // Brightness-weighted blending
    let brightness = dot(sample_color.rgb, vec3<f32>(0.2126, 0.7152, 0.0722));
    let weight = brightness * 0.5;
    sample_weight_sum += weight;
    bokeh_color += sample_color * weight;
  }
  
  // Normalize bokeh
  if (sample_weight_sum > 0.0) {
    bokeh_color /= sample_weight_sum;
  }
  
  // Optical vignette
  let center_dist = length(frame.uvCoord - vec2<f32>(0.5));
  let vignette_factor = vignette(center_dist, 3.0);
  
  // Combine original color with bokeh effect
  let final_color = mix(color, bokeh_color, 0.7) * vignette_factor;
  
  // Output to accumulation buffer
  output_tex[idx] = final_color;
}
