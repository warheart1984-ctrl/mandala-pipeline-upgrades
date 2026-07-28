/**
 * Drift radar — compare constitutional expectations vs observed files.
 * Status: **partial**. Writes JSON report (stdout or --out).
 *
 * Usage:
 *   node mandala-agent/drift-radar/generate-report.mjs
 *   node mandala-agent/drift-radar/generate-report.mjs --out drift-radar.json
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { runLinter } from "../../scripts/mandala-lint/constitutional-linter.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");

function exists(rel) {
  return fs.existsSync(path.join(ROOT, rel));
}

function probe(rel, expect = "present") {
  const ok = exists(rel);
  return {
    path: rel,
    expect,
    status: ok ? "aligned" : "drift",
    detail: ok ? "found" : "missing",
  };
}

function genblazeByok() {
  const rows = [];
  const ui = "mrs/apps/genblaze-media/app/static/index.html";
  const byok = "mrs/apps/genblaze-media/app/byok.py";
  const charter = "docs/genblaze/security/byok-security-charter.md";
  const trail = "docs/governance/cecp/trails/genblaze-byok-session-2026-07/README.md";

  for (const p of [ui, byok, charter, trail]) {
    rows.push(probe(p));
  }

  if (exists(ui)) {
    const text = fs.readFileSync(path.join(ROOT, ui), "utf8");
    rows.push({
      path: ui,
      expect: "sessionStorage BYOK",
      status: text.includes("sessionStorage") ? "aligned" : "drift",
      detail: text.includes("localStorage") && /genblaze_api_key/.test(text)
        ? "localStorage near BYOK key — review"
        : text.includes("sessionStorage")
          ? "sessionStorage present"
          : "sessionStorage missing",
    });
  }
  if (exists(byok)) {
    const text = fs.readFileSync(path.join(ROOT, byok), "utf8");
    rows.push({
      path: byok,
      expect: "hosted flag + printSoT false",
      status:
        text.includes("is_hosted_render") && text.includes("printSoT")
          ? "aligned"
          : "drift",
      detail: "policy helpers present",
    });
  }
  return rows;
}

function hosts() {
  return [
    {
      host: "Browser",
      status: exists("js") || exists("mrs/packages/renderer-web") ? "partial" : "unknown",
      detail: "browser host surfaces exist; full adapter matrix not claimed",
    },
    {
      host: "Unity",
      status: exists("unity") ? "skeleton" : "unknown",
      detail: "unity/ present as skeleton if found",
    },
    {
      host: "Unreal",
      status: exists("unreal") ? "skeleton" : "unknown",
      detail: "unreal/ present as skeleton if found",
    },
  ];
}

function packCorpus() {
  const skills = "mandala-agent-pack/manifests/skills.json";
  const agents = "mandala-agent-pack/manifests/agents.yaml";
  const rows = [probe(skills), probe(agents)];
  if (exists(skills)) {
    try {
      const data = JSON.parse(fs.readFileSync(path.join(ROOT, skills), "utf8"));
      const list = data.mandalaAgents || [];
      const total = list.reduce((n, a) => n + (a.skills?.length || 0), 0);
      rows.push({
        path: skills,
        expect: "14 agents catalog",
        status: list.length === 14 ? "aligned" : "drift",
        detail: `${list.length} agents · ${total} skill IDs (catalog; not 312 executable SKILL.md files)`,
      });
    } catch (e) {
      rows.push({
        path: skills,
        expect: "parseable JSON",
        status: "drift",
        detail: String(e),
      });
    }
  }
  return rows;
}

const lint = runLinter(ROOT);

const report = {
  generatedAt: new Date().toISOString(),
  fidelity: "partial",
  note:
    "Drift radar is a documentation/probe aid. PASS/aligned ≠ runtime constitutional enforcement.",
  linter: {
    errorCount: lint.errorCount,
    warnCount: lint.warnCount,
    checks: lint.checks,
    issues: lint.issues,
  },
  genblazeByok: genblazeByok(),
  hosts: hosts(),
  corpus: packCorpus(),
  governance: [
    probe("engine/constitution/charter.js"),
    probe("engine/governance/policies/default.policies.json"),
    probe("engine/conformance/default.conformance-profile.json"),
    probe("docs/governance/cecp/MANDALA_SIX_AGENTS.md"),
  ],
};

const outIdx = process.argv.indexOf("--out");
const outPath =
  outIdx >= 0
    ? path.resolve(process.argv[outIdx + 1])
    : path.join(__dirname, "drift-radar.json");

fs.writeFileSync(outPath, JSON.stringify(report, null, 2) + "\n", "utf8");
console.log(JSON.stringify(report, null, 2));
console.error(`\nWrote ${outPath}`);
