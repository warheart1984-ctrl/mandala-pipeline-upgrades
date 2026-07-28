/**
 * LookDevEngine — GPU-powered look-dev (assist-only steps).
 * Namespace: sx.router.module.gpu.assist.lookDevEngine
 * STATUS: **declared** / **skeleton** — no live GPU; final print is outside.
 */

export class LookDevEngine {
  /**
   * @param {{ route: (capabilityId: string, request?: object) => Promise<object> }} router
   */
  constructor(router) {
    this.router = router;
  }

  /**
   * Steps 1–3 assistOnly. Step 4 (human curation) and Step 5 (cpu.rt4d.print)
   * happen outside this module.
   */
  async run(request) {
    const concept = await this.router.route("gpu.gen.nvidia.nim_flux", {
      ...request,
      assistOnly: true,
    });
    const enhanced = await this.router.route("gpu.compute.nvidia.cuda", {
      ...concept,
      assistOnly: true,
    });
    const hints = await this.router.route("gpu.inference.nvidia.tao", {
      ...enhanced,
      assistOnly: true,
    });
    return {
      assistOnly: true,
      nonAuthoritative: true,
      status: "declared",
      concept,
      enhanced,
      hints,
      nextStep: "human_curation_then_cpu.rt4d.print",
    };
  }
}

export default LookDevEngine;
