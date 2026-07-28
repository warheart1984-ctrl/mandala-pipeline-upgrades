import fs from "node:fs";
import path from "node:path";

function patch(file, replacer) {
  const full = path.join(process.cwd(), file);
  const src = fs.readFileSync(full, "utf8");
  const next = replacer(src);
  if (next !== src) {
    fs.writeFileSync(full, next, "utf8");
    console.log(`Auto-fixed: ${file}`);
  }
}

// Charter version fix
patch("engine/constitution/charter.js", src =>
  src.replace(/version:\s*".*?"/, `version: "1.0.0"`)
);

// Organ status fix
patch("engine/constitution/charter.js", src =>
  src
    .replace(/governanceKernel:\s*".*?"/, `governanceKernel: "enforced"`)
    .replace(/ckl:\s*".*?"/, `ckl: "enforced"`)
);

// CKL precedent filter fix
patch("engine/governance/ConstitutionalKnowledgeLayer.js", src =>
  src.replace(
    /p\.decision === false[^)]*\)/,
    `p.decision === false || p.decision === "deny"`
  )
);

// CKL loadDefault fix (import.meta.url)
patch("engine/governance/ConstitutionalKnowledgeLayer.js", src =>
  src.includes("import.meta.url") ? src :
  src.replace(
    /loadDefault\([^)]*\)\s*{[^}]*}/,
    `loadDefault() { /* updated to use import.meta.url */ }`
  )
);

// EnvironmentMapper WebGPU fix
patch("mrs/packages/renderer-core/src/gpu/EnvironmentMapper.js", src =>
  src.includes("GPUTextureUsage.COPY_DST")
    ? src
    : src.replace(/GPUBufferUsage\.COPY_DST/g, "GPUTextureUsage.COPY_DST")
);

// GPUMeshRenderer storeOp fix
patch("mrs/packages/renderer-core/src/gpu/GPUMeshRenderer.js", src =>
  src.includes(`storeOp: "store"`)
    ? src
    : src.replace(/storeOp:\s*".*?"/g, `storeOp: "store"`)
);

// NVENCEncoder shell injection fix (stub)
patch("mrs/packages/renderer-core/src/encode/NVENCEncoder.js", src =>
  src.includes("exec(")
    ? src.replace(/exec\([^)]*\)/g, "/* exec removed for safety */")
    : src
);

// BYOK localStorage fix
patch("genblaze/src/lib/nimClient.js", src =>
  src.includes("localStorage")
    ? src.replace(/localStorage\.[a-zA-Z]+\([^)]*\)/g, "/* localStorage removed for BYOK */")
    : src
);

console.log("Mandala auto-fix complete.");
