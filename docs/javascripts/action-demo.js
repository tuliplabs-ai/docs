/* Copyright 2026 The Tulip Authors · SPDX-License-Identifier: Apache-2.0 */
(function () {
  const scenarios = {
    staging: {
      status: "✓ Allowed", tone: "allow",
      summary: "The staging rollout passes policy and the simulated deploy function runs.",
      evidence: "CI passed · image checkout-api:1.8.2 · staging", decision: "allow",
      audit: "deploy checkout-api · allow · policy checks passed", line: "blast"
    },
    production: {
      status: "… Held for approval", tone: "hold",
      summary: "The production label triggers a human hold. No deploy function runs.",
      evidence: "CI passed · image checkout-api:1.8.2 · production", decision: "require_human",
      audit: "deploy checkout-api · require_human · production policy", line: "human"
    },
    prohibited: {
      status: "× Denied", tone: "deny",
      summary: "The prohibited label triggers a hard denial. Approval cannot override it.",
      evidence: "CI passed · action tagged prohibited", decision: "deny",
      audit: "deploy checkout-api · deny · label denied by policy", line: "deny"
    },
    unsupported: {
      status: "↺ Abstained", tone: "abstain",
      summary: "The unsupported causal claim scores below the GSAR threshold, so no deploy is proposed.",
      evidence: "Claim: database saturation · evidence refs: none", decision: "replan",
      audit: "grounding decision · replan · unsupported claim", line: "ground"
    }
  };

  function mount(root) {
    const buttons = root.querySelectorAll("[data-demo-scenario]");
    if (!buttons.length) return;
    const fields = {
      status: root.querySelector("[data-demo-status]"), summary: root.querySelector("[data-demo-summary]"),
      evidence: root.querySelector("[data-demo-evidence]"), decision: root.querySelector("[data-demo-decision]"),
      audit: root.querySelector("[data-demo-audit]")
    };
    function select(name) {
      const scenario = scenarios[name];
      if (!scenario) return;
      buttons.forEach((button) => button.setAttribute("aria-selected", String(button.dataset.demoScenario === name)));
      Object.entries(fields).forEach(([key, node]) => { if (node) node.textContent = scenario[key]; });
      fields.status.className = "action-demo__status action-demo__status--" + scenario.tone;
      root.querySelectorAll("[data-code-line]").forEach((line) => {
        line.classList.toggle("is-active", line.dataset.codeLine === scenario.line);
      });
    }
    buttons.forEach((button) => button.addEventListener("click", () => select(button.dataset.demoScenario)));
    select("staging");
  }

  function init() { document.querySelectorAll("[data-action-demo]").forEach(mount); }
  if (typeof document$ !== "undefined") document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
