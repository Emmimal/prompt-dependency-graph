"""
~50 synthetic agent configurations, plus a small "workflow" layer that
depends on multiple agents (not directly on components). The workflow
layer is what creates real transitive dependencies and diamond shapes:

    base-policy --> support-agent-*  --\
                                          >-- refund-workflow
    base-policy --> escalation-agent-*  /

A change to base-policy doesn't just affect agents directly -- it can
ripple into workflows two hops away, which is the interesting case for
structural vs. candidate blast radius.
"""

import random

from model import AgentConfig

random.seed(7)  # deterministic synthetic system

ROLES = ["support", "sales", "analyst", "operations", "marketing"]
TEAMS = ["core", "enterprise", "smb", "emea", "apac", "trial", "vip", "partner", "internal", "beta"]


def build_agents() -> list[AgentConfig]:
    agents: list[AgentConfig] = []

    for role in ROLES:
        for team in TEAMS:
            name = f"{role}-{team}"
            agent = AgentConfig(name=name, role=role)

            # every agent inherits tone + a domain section -- shared baseline
            agent.depends_on("tone", ["professional"], kind="inherits")

            if role == "support":
                agent.depends_on("base-policy", ["refunds", "privacy"], kind="imports")
                agent.depends_on("domain", ["billing"], kind="references")
                agent.depends_on("format", ["json"], kind="formats-with")
                if team in ("enterprise", "vip"):
                    agent.depends_on("base-policy", ["escalation"], kind="imports")
                    agent.depends_on("safety", ["no-legal-advice"], kind="inherits")

            elif role == "sales":
                agent.depends_on("base-policy", ["privacy"], kind="imports")
                agent.depends_on("domain", ["product"], kind="references")
                agent.depends_on("format", ["markdown"], kind="formats-with")
                if team in ("enterprise", "partner"):
                    agent.depends_on("base-policy", ["escalation"], kind="imports")

            elif role == "analyst":
                agent.depends_on("base-policy", ["escalation"], kind="references")
                agent.depends_on("domain", ["billing"], kind="references")
                agent.depends_on("format", ["json"], kind="formats-with")
                agent.depends_on("tone", ["concise"], kind="inherits")

            elif role == "operations":
                agent.depends_on("base-policy", ["refunds", "escalation"], kind="imports")
                agent.depends_on("safety", ["no-legal-advice", "no-medical-advice"], kind="inherits")
                agent.depends_on("format", ["json"], kind="formats-with")

            elif role == "marketing":
                agent.depends_on("domain", ["product"], kind="references")
                agent.depends_on("format", ["markdown"], kind="formats-with")
                agent.depends_on("tone", ["concise"], kind="inherits")
                # deliberately NOT dependent on base-policy at all --
                # an intentionally irrelevant branch of the graph

            agents.append(agent)

    return agents


def build_workflows(agents: list[AgentConfig]) -> list[AgentConfig]:
    """Workflow-level nodes that depend on AGENTS (not components directly),
    creating the transitive hop that matters for structural blast radius.
    """
    by_name = {a.name: a for a in agents}

    def wf(name: str, agent_names: list[str]) -> AgentConfig:
        w = AgentConfig(name=name, role="workflow")
        for an in agent_names:
            assert an in by_name, f"unknown agent {an!r} referenced by workflow {name!r}"
            # workflow depends on the AGENT itself (a node), not on the
            # agent's components directly. This is the genuine second hop:
            # a component change reaches the workflow only by first reaching
            # one of its constituent agents, then propagating along this edge.
            w.depends_on(an, ["output"], kind="inherits")
        return w

    workflows = [
        wf("refund-workflow", ["support-core", "support-enterprise", "operations-core"]),
        wf("escalation-workflow", ["support-vip", "analyst-core", "operations-enterprise"]),
        wf("renewal-workflow", ["sales-enterprise", "sales-partner", "analyst-enterprise"]),
        wf("onboarding-workflow", ["sales-smb", "marketing-core", "support-trial"]),
        wf("compliance-workflow", ["operations-vip", "operations-enterprise", "analyst-vip"]),
    ]
    return workflows


if __name__ == "__main__":
    agents = build_agents()
    workflows = build_workflows(agents)
    all_nodes = agents + workflows
    print(f"{len(agents)} agents + {len(workflows)} workflows = {len(all_nodes)} total nodes")
    for a in agents[:5]:
        print(a.name, "->", [(d.component, d.sections) for d in a.dependencies])
