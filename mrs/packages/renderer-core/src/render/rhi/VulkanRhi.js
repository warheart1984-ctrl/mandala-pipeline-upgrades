/**
 * Vulkan RHI — Phase C **declared** stub (Drive-G-1).
 * Not a production backend. Methods throw until RT4D v4 / native host work lands.
 *
 * @implements {import("./RhiContract.js").Rhi}
 */
export class VulkanRhi {
  constructor(_options = {}) {
    this._backend = /** @type {const} */ ("vulkan");
  }

  getBackend() {
    return this._backend;
  }

  async getDevices() {
    throw new Error(
      'VulkanRhi.getDevices: roadmap / Phase C+; not implemented (use createRhi("webgpu") stub)'
    );
  }

  async selectDevice(_deviceId = 0) {
    throw new Error(
      "VulkanRhi.selectDevice: roadmap / Phase C+; not implemented"
    );
  }

  async createBuffer(_size, _usage) {
    throw new Error(
      "VulkanRhi.createBuffer: roadmap / Phase C+; not implemented"
    );
  }

  async createTexture(_width, _height, _format) {
    throw new Error(
      "VulkanRhi.createTexture: roadmap / Phase C+; not implemented"
    );
  }

  async uploadBuffer(_handle, _data) {
    throw new Error(
      "VulkanRhi.uploadBuffer: roadmap / Phase C+; not implemented"
    );
  }

  async readBuffer(_handle, _target) {
    throw new Error(
      "VulkanRhi.readBuffer: roadmap / Phase C+; not implemented"
    );
  }

  async dispatchKernel(_kernelName, _x, _y, _z, _bindings) {
    throw new Error(
      "VulkanRhi.dispatchKernel: roadmap / Phase C+; not implemented"
    );
  }
}
