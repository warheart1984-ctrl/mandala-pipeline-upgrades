import fs from "node:fs";
import path from "node:path";

export class ConstitutionalLinter {
  constructor(root) {
    this.root = root;
    this.issues = [];
  }

  run() {
    this.checkCharterVersion();
    this.checkOrganStatuses();
    this.checkCKLFilters();
    this.checkCSEDeterminism();
    this.checkGPUAssistOnly();
    this.checkZeroSecretPersistence();
    this.checkEvidenceChainPurity();
    this.checkRendererCoreESM();
    this.checkWebGPUUsage();
    this.checkSecurityHardening();
    return this.issues;
  }

  addIssue(type, file, message) {
    this.issues.push({ type, file, message });
  }

  checkCharterVersion() {
    const charter = fs.readFileSync(
      path.join(this.root, "engine/constitution/charter.js"),
      "utf8"
    );
    if (!charter.includes(`version: "1.0.0"`)) {
      this.addIssue("charter", "charter.js", "Charter version drift detected.");
    }
  }

  checkOrganStatuses() {
    const charter = fs.readFileSync(
      path.join(this.root, "engine/constitution/charter.js"),
      "utf8"
    );
    if (!charter.includes(`governanceKernel: "enforced"`)) {
      this.addIssue("charter", "charter.js", "governanceKernel must be enforced.");
    }
    if (!charter.includes(`ckl: "enforced"`)) {
      this.addIssue("charter", "charter.js", "CKL must be enforced.");
    }
  }

  checkCKLFilters() {
    const ckl = fs.readFileSync(
      path.join(this.root, "engine/governance/ConstitutionalKnowledgeLayer.js"),
      "utf8"
    );
    if (!ckl.includes(`p.decision === false || p.decision === "deny"`)) {
      this.addIssue("ckl", "CKL", "CKL precedent filter drift detected.");
    }
  }

  checkCSEDeterminism() {
    const cse = fs.readFileSync(
      path.join(this.root, "js/constitution/cse.js"),
      "utf8"
    );
    if (!cse.includes("determinismRequired")) {
      this.addIssue("cse", "CSE", "CSE missing determinismRequired enforcement.");
    }
  }

  checkGPUAssistOnly() {
    const gpuFiles = [
      "GPUMeshRenderer.js",
      "GPURenderPipeline.js",
      "EnvironmentMapper.js",
      "ShadowMapper.js",
      "PostProcessor.js"
    ];
    gpuFiles.forEach(file => {
      const content = fs.readFileSync(
        path.join(this.root, "mrs/packages/renderer-core/src/gpu", file),
        "utf8"
      );
      if (content.includes("print") || content.includes("deterministic")) {
        this.addIssue("gpu", file, "GPU file contains forbidden print/deterministic logic.");
      }
    });
  }

  checkZeroSecretPersistence() {
    const genblaze = fs.readFileSync(
      path.join(this.root, "genblaze/src/lib/nimClient.js"),
      "utf8"
    );
    if (genblaze.includes("localStorage")) {
      this.addIssue("byok", "nimClient.js", "BYOK must never use localStorage.");
    }
  }

  checkEvidenceChainPurity() {
    const printer = fs.readFileSync(
      path.join(this.root, "engine/printer/DigitalPrinter.js"),
      "utf8"
    );
    if (printer.includes("apiKey")) {
      this.addIssue("printer", "DigitalPrinter.js", "Evidence chain contaminated with secrets.");
    }
  }

  checkRendererCoreESM() {
    const files = [
      "TimelineSerializer.js",
      "GPUVideoEncoder.js",
      "NVENCEncoder.js"
    ];
    files.forEach(file => {
      const content = fs.readFileSync(
        path.join(this.root, "mrs/packages/renderer-core/src", file),
        "utf8"
      );
      if (content.includes("require(")) {
        this.addIssue("esm", file, "ESM/require drift detected.");
      }
    });
  }

  checkWebGPUUsage() {
    const envMapper = fs.readFileSync(
      path.join(this.root, "mrs/packages/renderer-core/src/gpu/EnvironmentMapper.js"),
      "utf8"
    );
    if (!envMapper.includes("GPUTextureUsage.COPY_DST")) {
      this.addIssue("webgpu", "EnvironmentMapper.js", "C1 WebGPU fix missing.");
    }

    const meshRenderer = fs.readFileSync(
      path.join(this.root, "mrs/packages/renderer-core/src/gpu/GPUMeshRenderer.js"),
      "utf8"
    );
    if (!meshRenderer.includes(`storeOp: "store"`)) {
      this.addIssue("webgpu", "GPUMeshRenderer.js", "C2 WebGPU fix missing.");
    }
  }

  checkSecurityHardening() {
    const nvenc = fs.readFileSync(
      path.join(this.root, "mrs/packages/renderer-core/src/encode/NVENCEncoder.js"),
      "utf8"
    );
    if (nvenc.includes("exec(")) {
      this.addIssue("security", "NVENCEncoder.js", "Shell injection risk detected.");
    }
  }
}
