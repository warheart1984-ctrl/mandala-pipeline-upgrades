/**
 * Governance Kernel — CKL + contracts → Decision
 */

import { resolveAuthority } from "../constitution/contracts.js";
import { CHARTER } from "../constitution/charter.js";
import {
  ConstitutionalKnowledgeLayer,
  resolveDecision,
} from "./ConstitutionalKnowledgeLayer.js";

export class GovernanceKernel {
  /**
   * @param {object} options
   * @param {import('./ConstitutionalKnowledgeLayer.js').ConstitutionalKnowledgeLayer} options.ckl
   * @param {object} [options.cse]
   */
  constructor({ ckl, cse = null } = {}) {
    this.ckl = ckl ?? new ConstitutionalKnowledgeLayer([]);
    this.cse = cse;
    this.charterId = CHARTER.id;
  }

  /**
   * evaluateIntent(intent, evidence) → Decision
   */
  evaluateIntent(intent, evidence) {
    const worldId = intent?.world ?? intent?.constraints?.worldId ?? "*";
    const policies = this.ckl.GetPoliciesForWorld(worldId);
    const precedents = this.ckl.GetPrecedents(intent);
    const decision = resolveDecision(intent, evidence, policies, precedents);

    const enriched = {
      ...decision,
      charterId: this.charterId,
      intentId: intent?.id ?? null,
      worldId,
      policiesApplied: policies.policies.map((p) => p.id),
      precedentCount: precedents.length,
    };

    this.ckl.recordPrecedent({ intent, decision: enriched });
    return enriched;
  }

  resolveAuthority(actor, action) {
    return resolveAuthority(actor, action);
  }
}
