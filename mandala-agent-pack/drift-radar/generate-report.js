import fs from "node:fs";
import path from "node:path";

function read(file) {
  return fs.readFileSync(path.join(process.cwd(), file), "utf8");
}

const radar = {
  charter: {},
  ckl: {},
  cse: {},
  policies: {},
  gpu: {},
  genblaze: {},
  hosts: {}
};

// Charter drift
const charter = read("engine/constitution/charter.js");
radar.charter.version = charter.includes(`version: "1.0.0"`) ? "aligned" : "drift";
radar.charter.organs = {
  governanceKernel: charter.includes(`governanceKernel: "enforced"`) ? "enforced" : "drift",
  ckl: charter.includes(`ckl: "enforced"`) ? "enforced" : "drift"
};

// CKL drift
const ckl = read("engine/governance/ConstitutionalKnowledgeLayer.js");
radar.ckl.precedentFilter = ckl.includes(`p.decision === false || p.decision === "deny"`) ? "aligned" : "drift";
radar.ckl.loadDefault = ckl.includes("import.meta.url") ? "aligned" : "drift";

// CSE drift
const cse = read("js/constitution/cse.js");
radar.cse.determinismRequired = cse.includes("determinismRequired") ? "aligned" : "missing";

// GPU drift
const envMapper = read("mrs/packages/renderer-core/src/gpu/EnvironmentMapper.js");
const meshRenderer = read("mrs/packages/renderer-core/src/gpu/GPUMeshRenderer.js");
radar.gpu.webgpu = {
  environmentMapper: envMapper.includes("GPUTextureUsage.COPY_DST") ? "aligned" : "drift",
  meshRenderer: meshRenderer.includes(`storeOp: "store"`) ? "aligned" : "drift"
};

// Genblaze drift (BYOK)
const nimClient = read("genblaze/src/lib/nimClient.js");
radar.genblaze.byok = {
  sessionOnly: !nimClient.includes("localStorage"),
  noLogging: !nimClient.includes("console.log"),
  noPrinter: !nimClient.includes("DigitalPrinter")
};

// Hosts drift (stubs)
radar.hosts.browser = "unknown";
radar.hosts.unity = "unknown";
radar.hosts.unreal = "unknown";

console.log(JSON.stringify(radar, null, 2));
