#!/usr/bin/env node
/**
 * Sovereign X Router capability inspector CLI (skeleton).
 * STATUS: **declared** / **skeleton** — lists registry; no live GPU probe.
 *
 * Usage:
 *   node sovereign-x/cli/sx-capabilities.js list
 *   node sovereign-x/cli/sx-capabilities.js inspect gpu.gen.nvidia.nim_flux
 */

import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const requireJson = createRequire(import.meta.url);
const registryPath = join(
  __dirname,
  "..",
  "router",
  "registry",
  "gpuSkillsRegistry.json",
);
const registry = requireJson(registryPath);

function main() {
  const args = process.argv.slice(2);
  const command = args[0] || "list";

  if (command === "list") {
    console.log("Sovereign X Router capabilities:");
    console.log("- cpu.rt4d.print (authoritative)");
    for (const cap of Object.keys(registry.skills ?? {})) {
      console.log(`- ${cap} (assist, skill: ${registry.skills[cap]})`);
    }
    return;
  }

  if (command === "inspect") {
    const cap = args[1];
    if (!cap) {
      console.error("Usage: sx-capabilities inspect <capability>");
      process.exit(1);
    }
    if (cap === "cpu.rt4d.print") {
      console.log("Capability: cpu.rt4d.print");
      console.log("Skill path: (none — PathTracer4D / Digital Printer SoT)");
      console.log("Authority: authoritative");
      return;
    }
    const skill = registry.skills?.[cap];
    if (!skill) {
      console.error(`Capability not found: ${cap}`);
      process.exit(1);
    }
    const meta = registry.capabilityMeta?.[cap] ?? {};
    console.log(`Capability: ${cap}`);
    console.log(`Skill path: ${skill}`);
    console.log(`Authority: ${meta.authority ?? "assist"}`);
    console.log(`capabilityClass: ${meta.capabilityClass ?? "(n/a)"}`);
    return;
  }

  console.error(`Unknown command: ${command}`);
  process.exit(1);
}

main();
