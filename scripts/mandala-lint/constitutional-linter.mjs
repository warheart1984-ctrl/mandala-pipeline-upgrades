/**
 * Constitutional Linter — path-honest heuristic checks for MRS.
 *
 * Status: **partial** — substring / existence probes, not full semantic enforcement.
 * Fragile string matches are labeled `partial` in issue.severity.
 * Missing optional files → status `skip` (does not fail the run).
 *
 * Usage: node scripts/mandala-lint/run.mjs
 * Exit: non-zero when any issue has severity `error`.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const DEFAULT_ROOT = path.resolve(__dirname, "../..");

const PROTECTED_HINTS = [
  "engine/constitution/",
  "engine/governance/policies/",
  "AGENTS.md",
  "constitution/CHARTER.md",
];

/**
 * @typedef {{ type: string, file: string, message: string, severity?: 'error'|'warn'|'skip', fidelity?: 'partial'|'declared'|'enforced' }} LintIssue
 */

export class ConstitutionalLinter {
  /**
   * @param {string} root
   */
  constructor(root = DEFAULT_ROOT) {
    this.root = root;
    /** @type {LintIssue[]} */
    this.issues = [];
    /** @type {{ id: string, status: string, detail?: string }[]} */
    this.checks = [];
  }

  /**
   * @param {string} rel
   */
  abs(rel) {
    return path.join(this.root, rel);
  }

  /**
   * @param {string} rel
   */
  readIfExists(rel) {
    const p = this.abs(rel);
    if (!fs.existsSync(p)) return null;
    return fs.readFileSync(p, "utf8");
  }

  /**
   * @param {LintIssue} issue
   */
  addIssue(issue) {
    this.issues.push({
      severity: "error",
      fidelity: "partial",
      ...issue,
    });
  }

  recordCheck(id, status, detail) {
    this.checks.push({ id, status, detail });
  }

  run() {
    this.checkCharterVersion();
    this.checkOrganStatuses();
    this.checkCKLFilters();
    this.checkCSEAndDeterminismContracts();
    this.checkGPUAssistOnly();
    this.checkZeroSecretPersistence();
    this.checkEvidenceChainPurity();
    this.checkRendererCoreESM();
    this.checkWebGPUUsage();
    this.checkSecurityHardening();
    return this.issues;
  }

  checkCharterVersion() {
    const rel = "engine/constitution/charter.js";
    const charter = this.readIfExists(rel);
    if (!charter) {
      this.addIssue({
        type: "charter",
        file: rel,
        message: "charter.js missing",
        severity: "error",
      });
      this.recordCheck("charter.version", "fail", "missing");
      return;
    }
    // Real charter uses version: "1.0.0"
    const ok = /version:\s*"1\.0\.0"/.test(charter);
    if (!ok) {
      this.addIssue({
        type: "charter",
        file: rel,
        message: "Charter version string drift (expected version: \"1.0.0\").",
        fidelity: "partial",
      });
      this.recordCheck("charter.version", "fail");
    } else {
      this.recordCheck("charter.version", "pass");
    }
  }

  checkOrganStatuses() {
    const rel = "engine/constitution/charter.js";
    const charter = this.readIfExists(rel);
    if (!charter) return;
    // Real shape: governanceKernel: { id: "...", status: "enforced" }
    const gk =
      /governanceKernel:\s*\{[^}]*status:\s*"enforced"/.test(charter) ||
      charter.includes('governanceKernel: { id: "organ.gk", status: "enforced" }');
    const ckl =
      /ckl:\s*\{[^}]*status:\s*"enforced"/.test(charter) ||
      charter.includes('ckl: { id: "organ.ckl", status: "enforced" }');
    if (!gk) {
      this.addIssue({
        type: "charter",
        file: rel,
        message: "governanceKernel status not observed as enforced (partial probe).",
        fidelity: "partial",
      });
      this.recordCheck("charter.governanceKernel", "fail");
    } else {
      this.recordCheck("charter.governanceKernel", "pass");
    }
    if (!ckl) {
      this.addIssue({
        type: "charter",
        file: rel,
        message: "ckl status not observed as enforced (partial probe).",
        fidelity: "partial",
      });
      this.recordCheck("charter.ckl", "fail");
    } else {
      this.recordCheck("charter.ckl", "pass");
    }
  }

  checkCKLFilters() {
    const rel = "engine/governance/ConstitutionalKnowledgeLayer.js";
    const ckl = this.readIfExists(rel);
    if (!ckl) {
      this.addIssue({
        type: "ckl",
        file: rel,
        message: "CKL module missing",
      });
      this.recordCheck("ckl.filters", "fail", "missing");
      return;
    }
    const ok =
      ckl.includes('p.decision === false || p.decision === "deny"') ||
      ckl.includes("p.decision === false || p.decision === 'deny'");
    if (!ok) {
      this.addIssue({
        type: "ckl",
        file: rel,
        message: "CKL recentDenials filter pattern drift (partial substring).",
        fidelity: "partial",
      });
      this.recordCheck("ckl.filters", "fail");
    } else {
      this.recordCheck("ckl.filters", "pass");
    }
    if (!ckl.includes("loadDefault")) {
      this.addIssue({
        type: "ckl",
        file: rel,
        message: "CKL loadDefault() not found (partial).",
        severity: "warn",
        fidelity: "partial",
      });
    }
  }

  checkCSEAndDeterminismContracts() {
    const cseRel = "js/constitution/cse.js";
    const cse = this.readIfExists(cseRel);
    if (!cse) {
      this.addIssue({
        type: "cse",
        file: cseRel,
        message: "CSE module missing",
      });
      this.recordCheck("cse.exists", "fail");
    } else {
      this.recordCheck("cse.exists", "pass");
      // User skeleton checked determinismRequired inside cse.js — that string is
      // not present in current CSE. Determinism gates live in SX GPU contracts.
      if (!cse.includes("determinismRequired")) {
        this.recordCheck(
          "cse.determinismRequired_string",
          "skip",
          "Not in cse.js; see sovereign-x GPU contracts (honest path).",
        );
      }
    }

    const contractCandidates = [
      "sovereign-x/router/contracts/gpuPrintSafeguard.js",
      "sovereign-x/router/contracts/gpuDispatchContract.js",
      "mrs/packages/sovereign-x-router/src/GpuDispatchContract.js",
    ];
    let found = false;
    for (const rel of contractCandidates) {
      const body = this.readIfExists(rel);
      if (body && body.includes("determinismRequired")) {
        found = true;
        this.recordCheck("determinism.contracts", "pass", rel);
        break;
      }
    }
    if (!found) {
      this.addIssue({
        type: "determinism",
        file: contractCandidates[0],
        message: "No determinismRequired contract found in known SX paths.",
        fidelity: "partial",
      });
      this.recordCheck("determinism.contracts", "fail");
    }
  }

  checkGPUAssistOnly() {
    // Do NOT substring-scan GPU files for "print"/"deterministic" (false positives).
    const safeguard = "sovereign-x/router/contracts/gpuPrintSafeguard.js";
    const body = this.readIfExists(safeguard);
    if (!body) {
      this.addIssue({
        type: "gpu",
        file: safeguard,
        message: "gpuPrintSafeguard.js missing — assist-only print gate not found.",
      });
      this.recordCheck("gpu.printSafeguard", "fail");
      return;
    }
    const hasAssert =
      body.includes("assertGpuPrintSafeguard") || body.includes("checkGpuPrintSafeguard");
    if (!hasAssert) {
      this.addIssue({
        type: "gpu",
        file: safeguard,
        message: "gpuPrintSafeguard exports not detected (partial).",
        fidelity: "partial",
      });
      this.recordCheck("gpu.printSafeguard", "fail");
    } else {
      this.recordCheck("gpu.printSafeguard", "pass");
    }
  }

  checkZeroSecretPersistence() {
    const uiRel = "mrs/apps/genblaze-media/app/static/index.html";
    const byokRel = "mrs/apps/genblaze-media/app/byok.py";
    const ui = this.readIfExists(uiRel);
    const byok = this.readIfExists(byokRel);

    if (!ui) {
      this.addIssue({
        type: "byok",
        file: uiRel,
        message: "Genblaze static UI missing",
      });
      this.recordCheck("byok.ui", "fail");
    } else {
      if (/\blocalStorage\b/.test(ui) && /BYOK|api.?key|genblaze_api_key/i.test(ui)) {
        // Only flag if localStorage appears near BYOK — still partial
        this.addIssue({
          type: "byok",
          file: uiRel,
          message: "localStorage referenced near BYOK UI (must be sessionStorage-only).",
          fidelity: "partial",
        });
        this.recordCheck("byok.no_localStorage", "fail");
      } else if (/\blocalStorage\b/.test(ui)) {
        this.recordCheck(
          "byok.no_localStorage",
          "warn",
          "localStorage present in page; verify not used for BYOK keys",
        );
      } else {
        this.recordCheck("byok.no_localStorage", "pass");
      }
      if (!ui.includes("sessionStorage")) {
        this.addIssue({
          type: "byok",
          file: uiRel,
          message: "sessionStorage not found in Genblaze UI (BYOK expected).",
          fidelity: "partial",
        });
        this.recordCheck("byok.sessionStorage", "fail");
      } else {
        this.recordCheck("byok.sessionStorage", "pass");
      }
    }

    if (!byok) {
      this.addIssue({ type: "byok", file: byokRel, message: "byok.py missing" });
      this.recordCheck("byok.module", "fail");
    } else {
      const ok =
        byok.includes("byok_permitted") &&
        byok.includes("printSoT") &&
        byok.includes("GENBLAZE_ALLOW_BYOK");
      if (!ok) {
        this.addIssue({
          type: "byok",
          file: byokRel,
          message: "byok.py missing expected policy markers (partial).",
          fidelity: "partial",
        });
        this.recordCheck("byok.module", "fail");
      } else {
        this.recordCheck("byok.module", "pass");
      }
    }
  }

  checkEvidenceChainPurity() {
    // Fictional engine/printer/DigitalPrinter.js — probe real printer packages.
    const candidates = [
      "mrs/adapters/storyforge-boundary/printer/evidence.py",
      "mrs/adapters/storyforge-boundary/printer/pipeline.py",
      "mrs/adapters/storyforge-boundary/printer/sovereignty.py",
      "sovereign-x/lineage/sceneSpecLineageTracker.js",
    ];
    let any = false;
    for (const rel of candidates) {
      const body = this.readIfExists(rel);
      if (!body) {
        this.recordCheck(`printer.${path.basename(rel)}`, "skip", "missing");
        continue;
      }
      any = true;
      // Partial secret leak heuristic — avoid matching comments carelessly:
      // look for assignment-like api_key / nvidia_api_key persistence patterns.
      if (
        /\bnvidia_api_key\s*=/.test(body) ||
        /\bapiKey\s*[:=]/.test(body) ||
        /sessionStorage\.getItem/.test(body)
      ) {
        this.addIssue({
          type: "printer",
          file: rel,
          message: "Possible secret/key material pattern in printer/evidence path (manual review).",
          severity: "warn",
          fidelity: "partial",
        });
        this.recordCheck(`printer.${path.basename(rel)}.secrets`, "warn");
      } else {
        this.recordCheck(`printer.${path.basename(rel)}.secrets`, "pass");
      }
    }
    if (!any) {
      this.recordCheck("printer.paths", "skip", "No known printer packages found");
    }
  }

  checkRendererCoreESM() {
    const files = [
      "mrs/packages/renderer-core/src/timeline/TimelineSerializer.js",
      "mrs/packages/renderer-core/src/encode/GPUVideoEncoder.js",
      "mrs/packages/renderer-core/src/encode/NVENCEncoder.js",
    ];
    for (const rel of files) {
      const body = this.readIfExists(rel);
      if (!body) {
        this.recordCheck(`esm.${path.basename(rel)}`, "skip", "missing");
        continue;
      }
      // Dynamic import() is OK; CommonJS require( is drift.
      if (/\brequire\s*\(/.test(body)) {
        this.addIssue({
          type: "esm",
          file: rel,
          message: "CommonJS require() detected in ESM renderer-core module (partial).",
          fidelity: "partial",
        });
        this.recordCheck(`esm.${path.basename(rel)}`, "fail");
      } else {
        this.recordCheck(`esm.${path.basename(rel)}`, "pass");
      }
    }
  }

  checkWebGPUUsage() {
    const envRel = "mrs/packages/renderer-core/src/gpu/EnvironmentMapper.js";
    const meshRel = "mrs/packages/renderer-core/src/gpu/GPUMeshRenderer.js";
    const env = this.readIfExists(envRel);
    const mesh = this.readIfExists(meshRel);

    if (!env) {
      this.recordCheck("webgpu.C1", "skip", "EnvironmentMapper.js missing");
    } else if (!env.includes("GPUTextureUsage.COPY_DST")) {
      this.addIssue({
        type: "webgpu",
        file: envRel,
        message: "C1: GPUTextureUsage.COPY_DST not observed in EnvironmentMapper (partial).",
        fidelity: "partial",
      });
      this.recordCheck("webgpu.C1", "fail");
    } else {
      this.recordCheck("webgpu.C1", "pass");
    }

    if (!mesh) {
      this.recordCheck("webgpu.C2", "skip", "GPUMeshRenderer.js missing");
    } else if (!mesh.includes('storeOp: "store"') && !mesh.includes("storeOp: 'store'")) {
      this.addIssue({
        type: "webgpu",
        file: meshRel,
        message: "C2: storeOp: \"store\" not observed in GPUMeshRenderer (partial).",
        fidelity: "partial",
      });
      this.recordCheck("webgpu.C2", "fail");
    } else {
      this.recordCheck("webgpu.C2", "pass");
    }
  }

  checkSecurityHardening() {
    const rel = "mrs/packages/renderer-core/src/encode/NVENCEncoder.js";
    const nvenc = this.readIfExists(rel);
    if (!nvenc) {
      this.recordCheck("security.nvenc", "skip", "missing");
      return;
    }
    // Prefer execFile*; flag only if bare `.exec(` / ` exec(` appears without execFile.
    const hasExecFile = /\bexecFile(?:Sync)?\b/.test(nvenc);
    const hasBareExec = /(?:^|[^\w])exec\s*\(/.test(nvenc);
    if (hasBareExec && !hasExecFile) {
      this.addIssue({
        type: "security",
        file: rel,
        message: "Bare child_process.exec( pattern (partial) — prefer execFile.",
        fidelity: "partial",
      });
      this.recordCheck("security.nvenc.exec", "fail");
    } else {
      this.recordCheck(
        "security.nvenc.exec",
        "pass",
        hasExecFile ? "uses execFile/dynamic import pattern" : "no exec( pattern",
      );
    }
  }

  summary() {
    const errors = this.issues.filter((i) => i.severity === "error");
    const warns = this.issues.filter((i) => i.severity === "warn");
    return {
      root: this.root,
      fidelity: "partial",
      protectedPathHints: PROTECTED_HINTS,
      checkCount: this.checks.length,
      issueCount: this.issues.length,
      errorCount: errors.length,
      warnCount: warns.length,
      checks: this.checks,
      issues: this.issues,
    };
  }
}

export function runLinter(root = DEFAULT_ROOT) {
  const linter = new ConstitutionalLinter(root);
  linter.run();
  return linter.summary();
}
