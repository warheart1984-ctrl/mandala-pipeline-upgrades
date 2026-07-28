#!/usr/bin/env node
/**
 * CLI entry for constitutional linter.
 * Exit 1 on severity=error issues. Warnings alone → exit 0.
 */
import { runLinter } from "./constitutional-linter.mjs";

const summary = runLinter();
const json = process.argv.includes("--json");

if (json) {
  console.log(JSON.stringify(summary, null, 2));
} else {
  console.log("Mandala constitutional linter (partial heuristics)");
  console.log(`root: ${summary.root}`);
  console.log(`checks: ${summary.checkCount} · errors: ${summary.errorCount} · warns: ${summary.warnCount}`);
  for (const c of summary.checks) {
    const mark =
      c.status === "pass" ? "PASS" : c.status === "skip" ? "SKIP" : c.status === "warn" ? "WARN" : "FAIL";
    console.log(`  [${mark}] ${c.id}${c.detail ? " — " + c.detail : ""}`);
  }
  if (summary.issues.length) {
    console.log("\nIssues:");
    for (const i of summary.issues) {
      console.log(`  - (${i.severity}/${i.fidelity}) [${i.type}] ${i.file}: ${i.message}`);
    }
  }
  console.log(
    "\nNote: substring probes are partial — not full constitutional enforcement (Drive-G-1).",
  );
}

process.exit(summary.errorCount > 0 ? 1 : 0);
