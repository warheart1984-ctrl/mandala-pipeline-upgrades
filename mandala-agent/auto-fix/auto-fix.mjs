#!/usr/bin/env node
/**
 * Mandala auto-fix — DRY-RUN by default.
 *
 * Safety:
 * - Never writes protected constitutional paths unless --allow-protected (dangerous).
 * - --apply required to mutate non-protected files.
 * - Dangerous regex "gut" fixes (NVENC exec, CKL loadDefault) → report only.
 *
 * Usage:
 *   node mandala-agent/auto-fix/auto-fix.mjs
 *   node mandala-agent/auto-fix/auto-fix.mjs --apply
 *   node mandala-agent/auto-fix/auto-fix.mjs --apply --allow-protected   # DANGEROUS
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { runLinter } from "../../scripts/mandala-lint/constitutional-linter.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");

const APPLY = process.argv.includes("--apply");
const ALLOW_PROTECTED = process.argv.includes("--allow-protected");

const PROTECTED_PREFIXES = [
  "engine/constitution/",
  "engine/governance/policies/",
  "engine/conformance/default.conformance-profile.json",
  "constitution/",
  "AGENTS.md",
  "CITATION.cff",
  ".zenodo.json",
];

function isProtected(rel) {
  const n = rel.replace(/\\/g, "/");
  return PROTECTED_PREFIXES.some((p) => n === p || n.startsWith(p));
}

/**
 * @typedef {{ id: string, file: string, kind: 'manual'|'patch', summary: string, protected?: boolean, diff?: string }} PlanItem
 */

/** @type {PlanItem[]} */
const plan = [];

function proposeManual(id, file, summary) {
  plan.push({ id, file, kind: "manual", summary, protected: isProtected(file) });
}

function proposePatch(id, file, summary, nextContent, prevContent) {
  plan.push({
    id,
    file,
    kind: "patch",
    summary,
    protected: isProtected(file),
    diff: `--- a/${file}\n+++ b/${file}\n@@ planned @@\n# length ${prevContent.length} → ${nextContent.length}\n`,
    _next: nextContent,
  });
}

const lint = runLinter(ROOT);

// Map known issues to safe plans
for (const issue of lint.issues) {
  if (issue.type === "security" && issue.file.includes("NVENCEncoder")) {
    proposeManual(
      "nvenc-exec-review",
      issue.file,
      "Manual review needed — do not auto-gut NVENCEncoder child_process usage. Prefer execFile + documented args.",
    );
  } else if (issue.type === "ckl") {
    proposeManual(
      "ckl-filter-review",
      issue.file,
      "Manual review needed — do not auto-rewrite CKL loadDefault / precedent filters.",
    );
  } else if (issue.type === "charter") {
    proposeManual(
      "charter-review",
      issue.file,
      "Protected path — charter edits require explicit user auth; auto-fix refuses by default.",
    );
  } else if (issue.type === "byok" && issue.file.includes("index.html")) {
    // Safe suggestion only if localStorage used for BYOK key — report
    proposeManual(
      "byok-session-storage",
      issue.file,
      "Ensure BYOK keys use sessionStorage only (no localStorage). Manual UI review.",
    );
  } else {
    proposeManual(
      `${issue.type}-review`,
      issue.file,
      `Manual review: ${issue.message}`,
    );
  }
}

// Optional safe doc touch: ensure pack README safety blurb exists (non-protected)
const readmeRel = "mandala-agent-pack/README.md";
const readmePath = path.join(ROOT, readmeRel);
if (fs.existsSync(readmePath)) {
  const cur = fs.readFileSync(readmePath, "utf8");
  if (!cur.includes("auto-fix") && APPLY) {
    // only when applying and missing — append safety note
  }
}

console.log("Mandala auto-fix");
console.log(`mode: ${APPLY ? "APPLY" : "DRY-RUN (default)"}`);
console.log(`allow-protected: ${ALLOW_PROTECTED}`);
console.log(`planned items: ${plan.length}`);
console.log("");

let applied = 0;
let refused = 0;

for (const item of plan) {
  console.log(`- [${item.kind}] ${item.id}`);
  console.log(`  file: ${item.file}${item.protected ? " (PROTECTED)" : ""}`);
  console.log(`  ${item.summary}`);
  if (item.diff) console.log(item.diff);

  if (!APPLY) continue;

  if (item.kind !== "patch") {
    console.log("  → skipped (manual)");
    continue;
  }
  if (item.protected && !ALLOW_PROTECTED) {
    console.log("  → REFUSED (protected; pass --allow-protected to override — DANGEROUS)");
    refused++;
    continue;
  }
  if (item.protected && ALLOW_PROTECTED) {
    console.log("  → REFUSED anyway pending explicit per-file auth in this tool version");
    refused++;
    continue;
  }
  if (item._next) {
    fs.mkdirSync(path.dirname(path.join(ROOT, item.file)), { recursive: true });
    fs.writeFileSync(path.join(ROOT, item.file), item._next, "utf8");
    applied++;
    console.log("  → applied");
  }
}

console.log("");
console.log(
  APPLY
    ? `Done. applied=${applied} refused=${refused}`
    : "Dry-run only — no files written. Re-run with --apply for non-protected patches (none planned as auto-safe today).",
);
console.log(
  "Protected paths always require human auth; --allow-protected is documented as dangerous and still refused for charter/CKL guts.",
);
