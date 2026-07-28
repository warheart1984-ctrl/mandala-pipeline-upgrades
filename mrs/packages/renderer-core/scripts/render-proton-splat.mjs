#!/usr/bin/env node
/**
 * render-proton-splat.mjs — CECP Ω∞ six-mod proton pipeline CLI.
 *
 * STATUS: **enforced** (Scene→ProtonField→Lighting→Projection→Raster→AOVs→PNG)
 *
 * Sibling path to path-trace / Engine3D triangle soft-raster.
 *
 * Usage:
 *   node scripts/render-proton-splat.mjs --help
 *   node scripts/render-proton-splat.mjs --demo [--width N] [--height N] [--output out.png]
 *   node scripts/render-proton-splat.mjs --scene-spec path.json [...]
 *   node scripts/render-proton-splat.mjs --star-demo [--out-dir dir] [--aov depth,normal]
 *   node scripts/render-proton-splat.mjs --lattice-demo [--out-dir dir]
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import process from "node:process";

import { mintCir } from "../../../adapters/proton-raster-bridge/mintCir.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PKG_ROOT = join(__dirname, "..");
const ENGINE3D_ROOT = join(PKG_ROOT, "..", "engine3d-core");
const PROTON_INDEX = pathToFileURL(
  join(__dirname, "../src/render/rt4d/proton/index.js"),
).href;

const USAGE = `render-proton-splat.mjs — CECP six-mod proton pipeline (STATUS: enforced)

Usage:
  node scripts/render-proton-splat.mjs --help
  node scripts/render-proton-splat.mjs --demo [--width N] [--height N] [--output <png>] [--provenance <json>]
  node scripts/render-proton-splat.mjs --scene-spec <path.json> [--width N] [--height N] [--output <png>]
  node scripts/render-proton-splat.mjs --star-demo [--width 256|512] [--height N] [--out-dir <dir>] [--aov depth,normal] [--seed N]
  node scripts/render-proton-splat.mjs --lattice-demo [--width N] [--height N] [--out-dir <dir>] [--aov depth,normal]

Mods: Scene→ProtonField → Lighting4D → 4DProjection → ProtonRaster → Depth/Normal → PNG
CIR is a thin IntentRecord overlay (intentId required). Soft splat ≠ triangle soft-raster.

Judge-wow dense star path (--star-demo): create4dStarWorld → worldDocumentToRt4dPrimitives
  → fromWorldDocumentRt4d → runProtonPipelineFromField → beauty/depth/normal under --out-dir.
`;

/**
 * @param {string[]} argv
 */
function parseArgs(argv) {
  /** @type {Record<string, string|boolean>} */
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") out.help = true;
    else if (a === "--demo") out.demo = true;
    else if (a === "--star-demo") out["star-demo"] = true;
    else if (a === "--lattice-demo") out["lattice-demo"] = true;
    else if (a.startsWith("--") && i + 1 < argv.length && !argv[i + 1].startsWith("--")) {
      out[a.slice(2)] = argv[++i];
    } else if (a.startsWith("--")) {
      out[a.slice(2)] = true;
    }
  }
  return out;
}

/**
 * Clamp judge-wow resolution; allow 8+ for unit demos, prefer 256–512 for wow.
 * @param {unknown} raw
 * @param {number} fallback
 */
function parseDim(raw, fallback) {
  const n = parseInt(String(raw ?? fallback), 10);
  if (!Number.isFinite(n) || n < 8) return fallback;
  return Math.min(1024, n);
}

/**
 * @param {string} aovRaw
 */
function parseAov(aovRaw) {
  const parts = String(aovRaw || "depth,normal")
    .split(",")
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);
  return {
    depth: parts.includes("depth"),
    normal: parts.includes("normal"),
    none: parts.includes("none") || parts.length === 0,
  };
}

async function loadEngine3d(moduleRel) {
  const dist = join(ENGINE3D_ROOT, "dist", "src", ...moduleRel.split("/"));
  const srcTs = join(ENGINE3D_ROOT, "src", ...moduleRel.split("/")).replace(
    /\.js$/,
    ".ts",
  );
  if (existsSync(dist)) {
    return import(pathToFileURL(dist).href);
  }
  // Prefer dist; if missing, try built alternate path
  const alt = join(ENGINE3D_ROOT, "dist", ...moduleRel.split("/"));
  if (existsSync(alt)) {
    return import(pathToFileURL(alt).href);
  }
  throw new Error(
    `engine3d-core module missing: ${dist}. Run: npm run build in mrs/packages/engine3d-core` +
      (existsSync(srcTs) ? " (src present but dist not built)" : ""),
  );
}

/**
 * @param {Record<string, string|boolean>} args
 * @param {Awaited<ReturnType<typeof import>>} proton
 * @param {import("../../../adapters/proton-raster-bridge/mintCir.js").CirOverlay|object} cir
 * @param {number} width
 * @param {number} height
 */
async function runWorldDemo(args, proton, cir, width, height) {
  const {
    protonFieldFromWorldDocumentRt4d,
    enrichJudgeWowField,
    runProtonPipelineFromField,
    defaultCamera4D,
    encodeDepthPng,
    encodeNormalPng,
  } = proton;

  const seed = parseInt(String(args.seed ?? "42"), 10) >>> 0;
  let world;
  let mode;

  if (args["star-demo"]) {
    mode = "star-demo";
    const { create4dStarWorld } = await loadEngine3d("world/StarWorld.js");
    const { worldDocumentToRt4dPrimitives } = await loadEngine3d(
      "scene/WorldDocumentRt4d.js",
    );
    // Dense wow plate: 16 arms × 3 samples + core + halo (halo capped in enrich)
    const doc = create4dStarWorld({
      seed,
      armCount: 16,
      includeHalo: true,
      armLength: 2.4,
      coreRadius: 0.45,
      armRadius: 0.14,
    });
    const prims = worldDocumentToRt4dPrimitives(doc);
    world = { id: doc.id, primitives: prims };
  } else {
    mode = "lattice-demo";
    const { createWorldGenerator, generateWorldFromGenerator } =
      await loadEngine3d("world/WorldGenerator.js");
    const { worldDocumentToRt4dPrimitives } = await loadEngine3d(
      "scene/WorldDocumentRt4d.js",
    );
    const doc = generateWorldFromGenerator(
      createWorldGenerator("mandala", seed, { count: 24 }),
    );
    const prims = worldDocumentToRt4dPrimitives(doc);
    world = { id: doc.id ?? `mandala-${seed}`, primitives: prims };
  }

  const field0 = protonFieldFromWorldDocumentRt4d(world, {
    intentId: cir.id,
    worldId: world.id,
  });
  const field = enrichJudgeWowField(field0);
  const camera = defaultCamera4D({
    width,
    height,
    origin: [0, 0, -3.2, 0.15],
    params: { d4: 4, d3: 4, scale: 95, nearW: 0.05 },
  });
  // Mild / skipped lighting — enrich supplies chromatic colors; Reinhard wash hides them
  const result = runProtonPipelineFromField(field, {
    intentId: cir.id,
    worldId: world.id,
    width,
    height,
    cir,
    camera,
    skipLighting: true,
    mod1Status: "worlddocument-rt4d",
  });

  const outDir =
    typeof args["out-dir"] === "string"
      ? resolve(String(args["out-dir"]))
      : resolve(process.cwd(), `output/proton-${mode}`);
  mkdirSync(outDir, { recursive: true });

  const aov = parseAov(typeof args.aov === "string" ? args.aov : "depth,normal");
  const beautyPath = join(outDir, "beauty.png");
  writeFileSync(beautyPath, result.image.png);

  /** @type {Record<string, string|undefined>} */
  const aovPaths = { beautyPath };
  if (aov.depth) {
    aovPaths.depthPath = join(outDir, "depth.png");
    writeFileSync(aovPaths.depthPath, encodeDepthPng(result.depth));
  }
  if (aov.normal) {
    aovPaths.normalPath = join(outDir, "normal.png");
    writeFileSync(aovPaths.normalPath, encodeNormalPng(result.normals));
  }

  const evidence = {
    ...result.evidence,
    mode,
    seed,
    worldId: world.id,
    intentId: cir.id,
    beautyPath: aovPaths.beautyPath,
    depthPath: aovPaths.depthPath,
    normalPath: aovPaths.normalPath,
    status: "enforced",
  };
  const evidencePath = join(outDir, "evidence.json");
  writeFileSync(evidencePath, JSON.stringify(evidence, null, 2) + "\n");

  process.stdout.write(
    JSON.stringify(
      {
        ok: true,
        status: "enforced",
        mode,
        outDir,
        evidencePath,
        evidence,
        protonCount: result.field.protons.length,
        droppedCount: result.projected.dropped.length,
        ...aovPaths,
      },
      null,
      2,
    ) + "\n",
  );
}

/**
 * @param {Record<string, string|boolean>} args
 */
async function run(args) {
  const proton = await import(PROTON_INDEX);
  const {
    runProtonPipeline,
    demoSceneSpec,
    writeTriptychAovs,
    encodeDepthPng,
    encodeNormalPng,
  } = proton;

  const width = parseDim(args.width, 256);
  const height = parseDim(args.height, 256);

  const cir = mintCir({
    seed: args.seed ?? "proton-cecp-1",
    goal: "proton-raster-cecp-six",
    actor: "mrs.proton-raster",
  });

  if (args["star-demo"] || args["lattice-demo"]) {
    await runWorldDemo(args, proton, cir, width, height);
    return;
  }

  const outDir =
    typeof args["out-dir"] === "string" ? resolve(String(args["out-dir"])) : null;
  const output =
    typeof args.output === "string"
      ? resolve(String(args.output))
      : outDir
        ? join(outDir, "beauty.png")
        : resolve(process.cwd(), "output/proton-splat-demo.png");
  const provenancePath =
    typeof args.provenance === "string"
      ? resolve(String(args.provenance))
      : outDir
        ? join(outDir, "evidence.json")
        : output.replace(/\.png$/i, "") + ".evidence.json";

  let sceneSpec;
  if (args.demo || (!args["scene-spec"] && !args.scene)) {
    sceneSpec = demoSceneSpec();
  } else {
    const scenePath = resolve(String(args["scene-spec"] ?? args.scene));
    sceneSpec = JSON.parse(readFileSync(scenePath, "utf8"));
  }

  const result = runProtonPipeline(sceneSpec, {
    intentId: cir.id,
    width,
    height,
    cir,
  });

  mkdirSync(dirname(output), { recursive: true });
  writeFileSync(output, result.image.png);

  const aov = parseAov(typeof args.aov === "string" ? args.aov : "");
  /** @type {Record<string, string>} */
  const extra = {};
  if (outDir || aov.depth || aov.normal) {
    const dir = outDir ?? dirname(output);
    mkdirSync(dir, { recursive: true });
    if (aov.depth) {
      const p = join(dir, "depth.png");
      writeFileSync(p, encodeDepthPng(result.depth));
      extra.depthPath = p;
    }
    if (aov.normal) {
      const p = join(dir, "normal.png");
      writeFileSync(p, encodeNormalPng(result.normals));
      extra.normalPath = p;
    }
    if (outDir) {
      await writeTriptychAovs({
        outDir: dir,
        beautyPng: result.image.png,
        depth: result.depth,
        normals: result.normals,
      });
      extra.depthPath = join(dir, "depth.png");
      extra.normalPath = join(dir, "normal.png");
    }
  }

  const evidence = {
    ...result.evidence,
    intentId: cir.id,
    beautyPath: output,
    ...extra,
  };
  writeFileSync(provenancePath, JSON.stringify(evidence, null, 2) + "\n");

  process.stdout.write(
    JSON.stringify(
      {
        ok: true,
        status: "enforced",
        pngPath: output,
        evidencePath: provenancePath,
        evidence,
        protonCount: result.field.protons.length,
        droppedCount: result.projected.dropped.length,
        ...extra,
      },
      null,
      2,
    ) + "\n",
  );
}

async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (args.help || argv.length === 0) {
    process.stdout.write(USAGE);
    process.exit(argv.length === 0 ? 1 : 0);
  }
  await run(args);
}

main().catch((err) => {
  process.stderr.write(String(err?.stack || err) + "\n");
  process.exit(1);
});
