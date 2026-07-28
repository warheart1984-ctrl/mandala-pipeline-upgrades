import assert from "node:assert/strict";
import { describe, it, mock } from "node:test";

import {
  SharedImageFormat,
  SharedResourceType,
  FLAG,
  ProducerStatus,
  ConsumerStatus,
  makeImageHandleName,
  makeSemaphoreHandleName,
  makeFenceHandleName,
  makeConfigHandleName,
  SharedConfigBlock,
  SharedFrameDescriptor,
  HandleDescriptor,
  gpuErrorToString,
  SHARED_GPU_IMAGE_MAGIC,
  SHARED_GPU_IMAGE_VERSION,
} from "../../src/gpu/SharedGPUImage.js";

import { parseSharedFrame, SharedFramePreview, SHARED_FRAME_MAGIC, SHARED_FRAME_HEADER_BYTES } from "../../src/gpu/SharedFramePreview.js";

import { isWebGPUSupported } from "../../src/gpu/WebGPURenderer.js";

import { ShadowMapper, createShadowMapper } from "../../src/gpu/ShadowMapper.js";

/* Define WebGPU globals needed by module constructors */
globalThis.GPUTextureUsage = {
  TEXTURE_BINDING: 8,
  COPY_DST: 4,
  COPY_SRC: 2,
  RENDER_ATTACHMENT: 16,
};
globalThis.GPUBufferUsage = {
  UNIFORM: 1,
  COPY_DST: 4,
  COPY_SRC: 2,
  MAP_READ: 1,
  STORAGE: 128,
};
globalThis.GPUShaderStage = {
  VERTEX: 1,
  FRAGMENT: 2,
  COMPUTE: 4,
};
globalThis.GPUMapMode = { READ: 1, WRITE: 2 };
if (!globalThis.navigator) {
  Object.defineProperty(globalThis, "navigator", { value: {}, writable: true, configurable: true });
}
if (!globalThis.document) {
  Object.defineProperty(globalThis, "document", { value: { createElement: () => ({ getContext: () => {} }) }, writable: true, configurable: true });
}

import { PostProcessor, createPostProcessor } from "../../src/gpu/PostProcessor.js";

import { EnvironmentMapper } from "../../src/gpu/EnvironmentMapper.js";

import { GPUMeshRenderer, isMeshRendererSupported } from "../../src/gpu/GPUMeshRenderer.js";

import { ComputeMeshSampler, createComputeMeshSampler } from "../../src/gpu/ComputeMeshSampler.js";

import { GPURenderPipeline, PipelineState, createGPURenderPipeline } from "../../src/gpu/GPURenderPipeline.js";

import { GPUPreviewClient, PreviewState } from "../../src/gpu/GPUPreviewClient.js";

/* ── SharedGPUImage (pure functions) ─────────────────────────────── */

describe("SharedGPUImage — enums", () => {
  it("SharedImageFormat has expected values", () => {
    assert.equal(SharedImageFormat.UNDEFINED, 0);
    assert.equal(SharedImageFormat.R8G8B8A8_UNORM, 1);
    assert.equal(SharedImageFormat.R8G8B8A8_SRGB, 2);
    assert.equal(SharedImageFormat.R32G32B32A32_SFLOAT, 7);
  });

  it("SharedResourceType has expected values", () => {
    assert.equal(SharedResourceType.INVALID, 0);
    assert.equal(SharedResourceType.VULKAN_IMAGE, 1);
    assert.equal(SharedResourceType.DXGI_SHARED_RESOURCE, 3);
  });

  it("FLAG has expected bitmask values", () => {
    assert.equal(FLAG.RESIZE_PENDING, 1 << 0);
    assert.equal(FLAG.DEVICE_LOST, 1 << 2);
    assert.equal(FLAG.CONSUMER_READY, 1 << 4);
  });

  it("ProducerStatus has expected values", () => {
    assert.equal(ProducerStatus.IDLE, 0);
    assert.equal(ProducerStatus.FRAME_READY, 2);
    assert.equal(ProducerStatus.ERROR, 3);
  });

  it("ConsumerStatus has expected values", () => {
    assert.equal(ConsumerStatus.DISCONNECTED, 0);
    assert.equal(ConsumerStatus.CONNECTED, 1);
    assert.equal(ConsumerStatus.ERROR, 3);
  });
});

describe("SharedGPUImage — handle name helpers", () => {
  it("makeImageHandleName formats correctly", () => {
    assert.equal(makeImageHandleName("test-instance", 0), "Global\\test-instance_image_0");
    assert.equal(makeImageHandleName("test-instance", 1), "Global\\test-instance_image_1");
  });

  it("makeSemaphoreHandleName formats correctly", () => {
    assert.equal(makeSemaphoreHandleName("test-instance", 0), "Global\\test-instance_sem_0");
  });

  it("makeFenceHandleName formats correctly", () => {
    assert.equal(makeFenceHandleName("test-instance"), "Global\\test-instance_fence");
  });

  it("makeConfigHandleName formats correctly", () => {
    assert.equal(makeConfigHandleName("test-instance"), "Global\\test-instance_config");
  });
});

describe("SharedGPUImage — SharedConfigBlock", () => {
  it("write produces a buffer of correct size", () => {
    const buf = SharedConfigBlock.write(null, 1920, 1080, 1, 2, 0, 42, 0);
    assert.ok(Buffer.isBuffer(buf));
    assert.equal(buf.length, 256);
  });

  it("write/read round-trips correctly", () => {
    const buf = SharedConfigBlock.write(
      { consumerPID: 12345, consumerStatus: ConsumerStatus.CONNECTED },
      640, 480, SharedImageFormat.R8G8B8A8_UNORM, 2, 1, 99, FLAG.CONSUMER_READY,
    );
    const result = SharedConfigBlock.read(buf.buffer);
    assert.notEqual(result, null);
    assert.equal(result.magic, SHARED_GPU_IMAGE_MAGIC);
    assert.equal(result.version, SHARED_GPU_IMAGE_VERSION);
    assert.equal(result.width, 640);
    assert.equal(result.height, 480);
    assert.equal(result.format, SharedImageFormat.R8G8B8A8_UNORM);
    assert.equal(result.doubleBufferSlots, 2);
    assert.equal(result.activeSlot, 1);
    assert.equal(result.frameCount, 99);
    assert.equal(result.producerStatus, ProducerStatus.FRAME_READY);
    assert.equal(result.consumerStatus, ConsumerStatus.CONNECTED);
    assert.equal(result.flags, FLAG.CONSUMER_READY);
  });

  it("read returns null for invalid magic", () => {
    const buf = Buffer.alloc(256);
    const result = SharedConfigBlock.read(buf.buffer);
    assert.equal(result, null);
  });

  it("getByteSize returns 256", () => {
    assert.equal(SharedConfigBlock.getByteSize(), 256);
  });
});

describe("SharedGPUImage — small classes", () => {
  it("SharedFrameDescriptor stores fields", () => {
    const d = new SharedFrameDescriptor(5, 800, 600, 1, 0);
    assert.equal(d.frameIndex, 5);
    assert.equal(d.width, 800);
    assert.equal(d.height, 600);
    assert.equal(d.format, 1);
    assert.equal(d.activeSlot, 0);
  });

  it("HandleDescriptor stores fields", () => {
    const h = new HandleDescriptor(1, 0xABC, "Global\\test");
    assert.equal(h.type, 1);
    assert.equal(h.handleValue, 0xABC);
    assert.equal(h.namedHandle, "Global\\test");
  });
});

describe("SharedGPUImage — gpuErrorToString", () => {
  it("returns known error names", () => {
    assert.equal(gpuErrorToString(0), "SUCCESS");
    assert.equal(gpuErrorToString(1), "HANDLE_NOT_FOUND");
    assert.equal(gpuErrorToString(4), "TIMEOUT");
    assert.equal(gpuErrorToString(9), "INTERNAL_ERROR");
  });

  it("returns UNKNOWN for unmapped codes", () => {
    assert.equal(gpuErrorToString(255), "UNKNOWN(255)");
  });
});

/* ── SharedFramePreview (pure function + class) ──────────────────── */

describe("SharedFramePreview — parseSharedFrame", () => {
  function makeFrameBuffer(width, height, frameIndex, activeSlot) {
    const stride = width * 4;
    const slotBytes = stride * height;
    const totalBytes = 32 + slotBytes * 2;
    const buf = new ArrayBuffer(totalBytes);
    const view = new DataView(buf);
    view.setUint32(0, SHARED_FRAME_MAGIC, true);
    view.setUint32(4, 1, true);
    view.setUint32(8, width, true);
    view.setUint32(12, height, true);
    view.setUint32(16, stride, true);
    view.setUint32(20, frameIndex, true);
    view.setUint32(24, activeSlot, true);
    view.setUint32(28, slotBytes, true);
    return buf;
  }

  it("parses a valid shared frame", () => {
    const buf = makeFrameBuffer(4, 4, 42, 0);
    const result = parseSharedFrame(buf);
    assert.equal(result.width, 4);
    assert.equal(result.height, 4);
    assert.equal(result.stride, 16);
    assert.equal(result.frameIndex, 42);
    assert.equal(result.activeSlot, 0);
    assert.ok(result.pixels instanceof Uint8ClampedArray);
    assert.equal(result.pixels.byteLength, 4 * 4 * 4);
  });

  it("throws on buffer too small for header", () => {
    const buf = new ArrayBuffer(16);
    assert.throws(() => parseSharedFrame(buf), /shared frame header is incomplete/);
  });

  it("throws on invalid magic", () => {
    const buf = new ArrayBuffer(64);
    new DataView(buf).setUint32(0, 0xDEAD, true);
    assert.throws(() => parseSharedFrame(buf), /unsupported shared frame/);
  });

  it("throws on invalid dimensions", () => {
    const buf = new ArrayBuffer(128);
    const view = new DataView(buf);
    view.setUint32(0, SHARED_FRAME_MAGIC, true);
    view.setUint32(4, 1, true);
    view.setUint32(8, 0, true);
    assert.throws(() => parseSharedFrame(buf), /invalid shared frame dimensions/);
  });
});

describe("SharedFramePreview — class", () => {
  it("constructor stores canvas and readFrame", () => {
    const mockCanvas = { getContext: () => ({ putImageData: () => {} }) };
    const readFrame = () => new ArrayBuffer(64);
    const preview = new SharedFramePreview(mockCanvas, readFrame);
    assert.equal(preview.canvas, mockCanvas);
    assert.equal(preview.readFrame, readFrame);
    assert.equal(preview.lastFrame, -1);
    assert.equal(preview.running, false);
  });

  it("start sets running = true", () => {
    const mockCanvas = { getContext: () => ({ putImageData: () => {} }) };
    const preview = new SharedFramePreview(mockCanvas, () => new ArrayBuffer(64));
    preview.start(1000);
    assert.equal(preview.running, true);
    preview.stop();
    assert.equal(preview.running, false);
  });

  it("start is idempotent when already running", () => {
    const mockCanvas = { getContext: () => ({ putImageData: () => {} }) };
    const preview = new SharedFramePreview(mockCanvas, () => new ArrayBuffer(64));
    preview.start(1000);
    preview.start(500);
    assert.equal(preview.running, true);
    preview.stop();
  });
});

/* ── WebGPURenderer (isWebGPUSupported) ──────────────────────────── */

describe("WebGPURenderer — isWebGPUSupported", () => {
  it("returns false when navigator.gpu is absent", () => {
    assert.equal(isWebGPUSupported({}), false);
    assert.equal(isWebGPUSupported({ navigator: {} }), false);
  });

  it("returns false when gpu.requestAdapter is absent", () => {
    assert.equal(isWebGPUSupported({ navigator: { gpu: {} } }), false);
  });

  it("returns true when navigator.gpu.requestAdapter exists", () => {
    assert.equal(isWebGPUSupported({ navigator: { gpu: { requestAdapter: () => {} } } }), true);
  });

  it("uses globalThis by default", () => {
    const prev = globalThis.navigator?.gpu;
    assert.equal(typeof isWebGPUSupported(), "boolean");
  });
});

/* ── ShadowMapper (vector math + constructor) ────────────────────── */

describe("ShadowMapper — constructor defaults", () => {
  it("sets reasonable defaults", () => {
    const device = {};
    const sm = new ShadowMapper(device, {});
    assert.equal(sm.device, device);
    assert.equal(sm.size, 2048);
    assert.equal(sm.shadowMap, null);
    assert.equal(sm.shadowSampler, null);
    assert.equal(sm.lightPosition.x, 5);
    assert.equal(sm.lightPosition.y, 5);
    assert.equal(sm.lightTarget.w, 0);
  });

  it("accepts custom options", () => {
    const sm = new ShadowMapper({}, { size: 1024, lightPosition: { x: 1, y: 2, z: 3, w: 4 } });
    assert.equal(sm.size, 1024);
    assert.equal(sm.lightPosition.x, 1);
    assert.equal(sm.lightPosition.w, 4);
  });
});

describe("ShadowMapper — createShadowMapper factory", () => {
  it("creates instance and calls init", async () => {
    const calls = [];
    const mockDevice = {
      createTexture: () => ({ createView: () => ({}) }),
      createSampler: () => ({}),
      createBuffer: () => ({}),
      createShaderModule: () => ({}),
      createBindGroupLayout: () => ({}),
      createPipelineLayout: () => ({}),
      createRenderPipeline: () => ({}),
      createBindGroup: () => ({}),
    };
    const mapper = await createShadowMapper(mockDevice, { size: 512 });
    assert.ok(mapper instanceof ShadowMapper);
    assert.equal(mapper.size, 512);
  });
});

/* ── PostProcessor (constructor + updateUniforms) ────────────────── */

describe("PostProcessor — constructor defaults", () => {
  it("sets defaults", () => {
    const pp = new PostProcessor({});
    assert.equal(pp.width, 1920);
    assert.equal(pp.height, 1080);
    assert.equal(pp.bloomEnabled, true);
    assert.equal(pp.toneMappingEnabled, true);
    assert.equal(pp.chromaticAberrationEnabled, true);
    assert.equal(pp.vignetteEnabled, false);
    assert.equal(pp.bloomThreshold, 1.0);
    assert.equal(pp.bloomStrength, 0.5);
    assert.equal(pp.exposure, 1.0);
    assert.equal(pp.contrast, 1.0);
    assert.equal(pp.saturation, 1.0);
    assert.equal(pp.chromaticAberrationStrength, 0.005);
  });

  it("accepts custom options", () => {
    const pp = new PostProcessor({}, { width: 800, height: 600, bloomEnabled: false, vignetteEnabled: true });
    assert.equal(pp.width, 800);
    assert.equal(pp.height, 600);
    assert.equal(pp.bloomEnabled, false);
    assert.equal(pp.vignetteEnabled, true);
  });
});

describe("PostProcessor — updateUniforms", () => {
  it("calls device.queue.writeBuffer with expected size", () => {
    let writtenBuffer = null;
    let writtenOffset = null;
    let writtenData = null;
    const device = {
      queue: {
        writeBuffer: (buf, off, data) => {
          writtenBuffer = buf;
          writtenOffset = off;
          writtenData = data;
        },
      },
    };
    const pp = new PostProcessor(device);
    pp.width = 640;
    pp.height = 480;
    pp.uniformBuffer = { fake: true };
    pp.updateUniforms();
    assert.equal(writtenBuffer, pp.uniformBuffer);
    assert.equal(writtenOffset, 0);
    assert.ok(writtenData instanceof Float32Array);
    assert.equal(writtenData.length, 64);
    assert.equal(writtenData[0], pp.bloomThreshold);
    assert.equal(writtenData[8], pp.width);
    assert.equal(writtenData[9], pp.height);
  });
});

/* ── EnvironmentMapper (constructor) ─────────────────────────────── */

describe("EnvironmentMapper — constructor defaults", () => {
  it("sets defaults", () => {
    const em = new EnvironmentMapper({});
    assert.equal(em.size, 512);
    assert.equal(em.format, "rgba16float");
    assert.equal(em.reflectionStrength, 0.5);
    assert.equal(em.metallic, 0.5);
    assert.equal(em.environmentTexture, null);
    assert.equal(em.irradianceTexture, null);
    assert.equal(em.prefilterTexture, null);
    assert.equal(em.brdfTexture, null);
  });

  it("accepts custom options", () => {
    const em = new EnvironmentMapper({}, { size: 256, reflectionStrength: 0.8, metallic: 0.9 });
    assert.equal(em.size, 256);
    assert.equal(em.reflectionStrength, 0.8);
    assert.equal(em.metallic, 0.9);
  });
});

/* ── GPUMeshRenderer (constructor + isMeshRendererSupported) ─────── */

describe("GPUMeshRenderer — isMeshRendererSupported", () => {
  it("delegates to isWebGPUSupported via a boolean return", () => {
    assert.equal(typeof isMeshRendererSupported(), "boolean");
    assert.equal(typeof isMeshRendererSupported({}), "boolean");
  });
});

describe("GPUMeshRenderer — constructor defaults", () => {
  it("sets defaults", () => {
    const mr = new GPUMeshRenderer({});
    assert.equal(mr.width, 1920);
    assert.equal(mr.height, 1080);
    assert.equal(mr.sampleCount, 4);
    assert.equal(mr.format, "bgra8unorm");
    assert.equal(mr.renderMode, "solid");
    assert.equal(mr.pipeline, undefined);
    assert.equal(mr.texture, null);
    assert.equal(mr.vertexBuffer, null);
    assert.equal(mr.indexBuffer, null);
  });

  it("accepts custom options", () => {
    const mr = new GPUMeshRenderer({}, { width: 800, height: 600, sampleCount: 1, format: "rgba8unorm", renderMode: "wireframe" });
    assert.equal(mr.width, 800);
    assert.equal(mr.height, 600);
    assert.equal(mr.sampleCount, 1);
    assert.equal(mr.format, "rgba8unorm");
    assert.equal(mr.renderMode, "wireframe");
  });
});

/* ── ComputeMeshSampler (constructor + fallbackParamCode) ────────── */

describe("ComputeMeshSampler — constructor defaults", () => {
  it("sets defaults", () => {
    const cms = new ComputeMeshSampler({});
    assert.equal(cms.maxVertices, 256 * 256);
    assert.equal(cms.workgroupSize, 64);
    assert.equal(cms.pipeline, null);
    assert.equal(cms.bindGroup, null);
    assert.equal(cms.surfaceType, null);
  });

  it("accepts custom options", () => {
    const cms = new ComputeMeshSampler({}, { maxVertices: 128, workgroupSize: 32 });
    assert.equal(cms.maxVertices, 128);
    assert.equal(cms.workgroupSize, 32);
  });
});

describe("ComputeMeshSampler — fallbackParamCode", () => {
  const cms = new ComputeMeshSampler({});

  it("generates code for clifford-torus", () => {
    const code = cms.fallbackParamCode({ id: "clifford-torus" });
    assert.ok(code.includes("R = 1.5"));
    assert.ok(code.includes("r = 0.8"));
    assert.ok(code.includes("result.x"));
    assert.ok(code.includes("result.w"));
  });

  it("generates code for hopf-surface", () => {
    const code = cms.fallbackParamCode({ id: "hopf-surface" });
    assert.ok(code.includes("theta = u * 6.28318"));
    assert.ok(code.includes("result.x"));
    assert.ok(code.includes("result.w"));
  });

  it("generates code for torus-3d", () => {
    const code = cms.fallbackParamCode({ id: "torus-3d" });
    assert.ok(code.includes("R = 1.5"));
    assert.ok(code.includes("r = 0.6"));
    assert.ok(code.includes("result.w = 0.3"));
  });

  it("generates code for trefoil-4d", () => {
    const code = cms.fallbackParamCode({ id: "trefoil-4d" });
    assert.ok(code.includes("cos(3.0 * t)"));
    assert.ok(code.includes("result.w"));
  });

  it("generates default code for unknown surface", () => {
    const code = cms.fallbackParamCode({ id: "unknown-surface" });
    assert.ok(code.includes("u * 2.0 - 1.0"));
    assert.ok(code.includes("v * 2.0 - 1.0"));
  });
});

describe("ComputeMeshSampler — generateParamCode", () => {
  const cms = new ComputeMeshSampler({});

  it("wraps fallback into evaluate function", () => {
    const code = cms.generateParamCode({ id: "clifford-torus", gpuParamCode: null });
    assert.ok(code.includes("fn evaluate"));
    assert.ok(code.includes("R = 1.5"));
  });
});

describe("ComputeMeshSampler — buildComputeShader", () => {
  const cms = new ComputeMeshSampler({});

  it("returns a WGSL-like shader string", () => {
    const code = cms.buildComputeShader({ id: "clifford-torus" });
    assert.ok(code.includes("@compute"));
    assert.ok(code.includes("@workgroup_size"));
    assert.ok(code.includes("fn main"));
    assert.ok(code.includes("evaluate(u, v)"));
  });

  it("uses surface.gpuSampleCode when available", () => {
    const code = cms.buildComputeShader({ id: "test", gpuSampleCode: "custom wgsl" });
    assert.equal(code, "custom wgsl");
  });
});

/* ── GPURenderPipeline (constructor + state management) ──────────── */

describe("GPURenderPipeline — PipelineState enum", () => {
  it("has expected states", () => {
    assert.equal(PipelineState.UNINITIALIZED, "uninitialized");
    assert.equal(PipelineState.READY, "ready");
    assert.equal(PipelineState.RENDERING, "rendering");
    assert.equal(PipelineState.ERROR, "error");
  });
});

describe("GPURenderPipeline — constructor defaults", () => {
  const gp = new GPURenderPipeline({}, {});

  it("sets defaults", () => {
    assert.deepEqual(gp.device, {});
    assert.equal(gp.meshRenderer, null);
    assert.equal(gp.postProcessor, null);
    assert.equal(gp.canvas, null);
    assert.equal(gp.width, 1920);
    assert.equal(gp.height, 1080);
    assert.equal(gp.sampleCount, 4);
    assert.equal(gp.state, PipelineState.UNINITIALIZED);
    assert.equal(gp.lastResult, null);
    assert.equal(gp.timelinePlayer, null);
  });
});

describe("GPURenderPipeline — getStats", () => {
  it("returns initial stats before init", () => {
    const gp = new GPURenderPipeline({});
    const stats = gp.getStats();
    assert.equal(stats.state, PipelineState.UNINITIALIZED);
    assert.equal(stats.width, 1920);
    assert.equal(stats.vertexCount, 0);
    assert.equal(stats.triangleCount, 0);
    assert.equal(stats.gpuRasterized, true);
  });
});

describe("GPURenderPipeline — state management methods", () => {
  it("resize passes through to meshRenderer if available", () => {
    let mrResizeCalled = false;
    const gp = new GPURenderPipeline({});
    gp.meshRenderer = { resize: (w, h) => { mrResizeCalled = true; assert.equal(w, 100); assert.equal(h, 200); } };
    gp.resize(100, 200);
    assert.equal(mrResizeCalled, true);
  });

  it("setRenderMode passes through to meshRenderer", () => {
    let mrSetMode = null;
    const gp = new GPURenderPipeline({});
    gp.meshRenderer = { setRenderMode: (m) => { mrSetMode = m; } };
    gp.setRenderMode("wireframe");
    assert.equal(mrSetMode, "wireframe");
  });

  it("attachPostProcessor stores reference", () => {
    const gp = new GPURenderPipeline({});
    const pp = { fake: true };
    gp.attachPostProcessor(pp);
    assert.equal(gp.postProcessor, pp);
  });

  it("attachTimeline sets up player", () => {
    const gp = new GPURenderPipeline({});
    const fakeTimeline = { tracks: [], duration: 5 };
    gp.attachTimeline(fakeTimeline);
    assert.notEqual(gp.timelinePlayer, null);
    assert.deepEqual(gp._timelineState, {});
  });

  it("attachTimeline(null) clears player", () => {
    const gp = new GPURenderPipeline({});
    gp.timelinePlayer = { fake: true };
    gp.attachTimeline(null);
    assert.equal(gp.timelinePlayer, null);
  });

  it("release resets state", () => {
    const gp = new GPURenderPipeline({});
    let mrReleased = false;
    gp.meshRenderer = { release: () => { mrReleased = true; } };
    gp.postProcessor = { fake: true };
    gp.mesh = { fake: true };
    gp.release();
    assert.equal(mrReleased, true);
    assert.equal(gp.postProcessor, null);
    assert.equal(gp.mesh, null);
    assert.equal(gp.state, PipelineState.UNINITIALIZED);
  });
});

/* ── GPUPreviewClient (constructor + PreviewState) ───────────────── */

describe("GPUPreviewClient — PreviewState enum", () => {
  it("has expected values", () => {
    assert.equal(PreviewState.DISCONNECTED, "disconnected");
    assert.equal(PreviewState.CONNECTING, "connecting");
    assert.equal(PreviewState.CONNECTED, "connected");
    assert.equal(PreviewState.PRESENTING, "presenting");
    assert.equal(PreviewState.DEVICE_LOST, "device-lost");
    assert.equal(PreviewState.ERROR, "error");
    assert.equal(PreviewState.RESTARTING, "restarting");
  });
});

describe("GPUPreviewClient — constructor defaults", () => {
  it("sets defaults", () => {
    const client = new GPUPreviewClient({ previewExePath: "test.exe" });
    assert.equal(client.instanceName, "4d-renderer");
    assert.equal(client.width, 1920);
    assert.equal(client.height, 1080);
    assert.equal(client.format, SharedImageFormat.R8G8B8A8_UNORM);
    assert.equal(client.doubleBufferSlots, 2);
    assert.equal(client.enableVsync, true);
    assert.equal(client.autoRestart, true);
    assert.equal(client.maxRestarts, 5);
    assert.equal(client.timeoutMs, 5000);
    assert.equal(client.state, PreviewState.DISCONNECTED);
    assert.equal(client.process, null);
    assert.equal(client.restartCount, 0);
    assert.equal(client.frameCount, 0);
  });

  it("accepts custom options", () => {
    const client = new GPUPreviewClient({ instanceName: "custom", width: 800, height: 600, autoRestart: false, previewExePath: "test.exe" });
    assert.equal(client.instanceName, "custom");
    assert.equal(client.width, 800);
    assert.equal(client.autoRestart, false);
  });
});

describe("GPUPreviewClient — findPreviewExe does not throw", () => {
  it("returns a string path", () => {
    mock.method(GPUPreviewClient.prototype, "findPreviewExe", () => "mocked-preview.exe");
    try {
      const client = new GPUPreviewClient({ previewExePath: undefined });
      const exe = client.findPreviewExe();
      assert.equal(exe, "mocked-preview.exe");
    } finally {
      mock.restoreAll();
    }
  });
});
