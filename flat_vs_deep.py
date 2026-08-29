"""
Same number of downstream consumers (4), two different shapes:

Component A (flat):            Component B (deep/transitive):
    A -> Agent1                    B -> Agent1 -> Workflow1 -> Agent2
    A -> Agent2                                       -> Workflow2 -> Agent3
    A -> Agent3                                                          -> Agent4
    A -> Agent4

Question: does structural_blast_radius() actually differ, or does the
flat count alone already capture everything a flat consumer list would?
"""

from model import PromptComponent, AgentConfig
from graph import DependencyGraph
from impact import compute_impact
from components import make_v2 as _unused  # noqa: reuse pattern only


def build_flat_case():
    comp_v1 = PromptComponent(name="comp-a", version=1, sections={"only": "original text"})
    comp_v2 = PromptComponent(name="comp-a", version=2, sections={"only": "changed text"})

    nodes = []
    for i in range(1, 5):
        a = AgentConfig(name=f"flat-agent-{i}", role="flat")
        a.depends_on("comp-a", ["only"])
        nodes.append(a)

    graph = DependencyGraph(nodes)
    return comp_v1, comp_v2, graph


def build_deep_case():
    comp_v1 = PromptComponent(name="comp-b", version=1, sections={"only": "original text"})
    comp_v2 = PromptComponent(name="comp-b", version=2, sections={"only": "changed text"})

    agent1 = AgentConfig(name="deep-agent-1", role="deep")
    agent1.depends_on("comp-b", ["only"])

    workflow1 = AgentConfig(name="deep-workflow-1", role="workflow")
    workflow1.depends_on("deep-agent-1", ["only"], kind="inherits")

    agent2 = AgentConfig(name="deep-agent-2", role="deep")
    agent2.depends_on("deep-workflow-1", ["only"], kind="inherits")

    workflow2 = AgentConfig(name="deep-workflow-2", role="workflow")
    workflow2.depends_on("deep-agent-2", ["only"], kind="inherits")

    nodes = [agent1, workflow1, agent2, workflow2]
    graph = DependencyGraph(nodes)
    return comp_v1, comp_v2, graph


if __name__ == "__main__":
    flat_v1, flat_v2, flat_graph = build_flat_case()
    flat_report = compute_impact(flat_graph, flat_v1, flat_v2)
    print("FLAT shape (4 direct consumers):")
    print(flat_report.summary())
    print(f"  direct_dependents(comp-a) = {flat_graph.direct_dependents('comp-a')}")
    print()

    deep_v1, deep_v2, deep_graph = build_deep_case()
    deep_report = compute_impact(deep_graph, deep_v1, deep_v2)
    print("DEEP/transitive shape (1 direct consumer, 4 total downstream nodes):")
    print(deep_report.summary())
    print(f"  direct_dependents(comp-b) = {deep_graph.direct_dependents('comp-b')}")
