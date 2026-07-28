/**
 * GpuAssistModule — multi-vendor GPU assist routing.
 * Namespace: sx.router.module.gpu.assist
 * STATUS: **partial** — routes via router.route stubs; no live GPU.
 *
 * User drop-in (ESM). Public API: handleLookDev / handleSceneSpecAssist / handleEmbeddings.
 */

export class GpuAssistModule {
  /**
   * @param {{ route: (capabilityId: string, request?: object) => Promise<object> }} router
   */
  constructor(router) {
    this.router = router;
  }

  async handleLookDev(request) {
    if (request.determinismRequired) {
      return this.router.route("cpu.rt4d.print", {
        ...request,
        capabilityClass: "print",
        backend: "cpu.rt4d.print",
      });
    }
    const vendor = request.vendorPreference || "neutral";
    if (vendor === "nvidia") {
      return this.router.route("gpu.gen.nvidia.nim_flux", {
        ...request,
        assistOnly: true,
      });
    }
    if (vendor === "amd") {
      return this.router.route("gpu.inference.amd.rocm", {
        ...request,
        assistOnly: true,
      });
    }
    return this.router.route("gpu.gen.nvidia.nim_flux", {
      ...request,
      assistOnly: true,
    });
  }

  async handleSceneSpecAssist(request) {
    if (request.determinismRequired) {
      return this.router.route("cpu.rt4d.print", {
        ...request,
        capabilityClass: "print",
        backend: "cpu.rt4d.print",
      });
    }
    const vendor = request.vendorPreference || "neutral";
    if (vendor === "nvidia") {
      return this.router.route("gpu.inference.nvidia.tao", {
        ...request,
        assistOnly: true,
      });
    }
    if (vendor === "amd") {
      return this.router.route("gpu.inference.amd.rocm", {
        ...request,
        assistOnly: true,
      });
    }
    return this.router.route("gpu.inference.nvidia.tao", {
      ...request,
      assistOnly: true,
    });
  }

  async handleEmbeddings(request) {
    const vendor = request.vendorPreference || "nvidia";
    if (request.determinismRequired) {
      return this.router.route("cpu.rt4d.print", {
        ...request,
        capabilityClass: "print",
        backend: "cpu.rt4d.print",
      });
    }
    if (vendor === "nvidia" || vendor === "neutral") {
      return this.router.route("gpu.inference.nvidia.tao", {
        ...request,
        mode: "embeddings",
        assistOnly: true,
      });
    }
    return this.router.route("gpu.inference.amd.rocm", {
      ...request,
      mode: "embeddings",
      assistOnly: true,
    });
  }
}

export default GpuAssistModule;
