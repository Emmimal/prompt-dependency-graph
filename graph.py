"""
The dependency graph itself: direct dependents, transitive (structural)
dependents, and section-aware candidate dependents.

Kept deliberately simple -- this is graph traversal, not the centerpiece
of the article. The interesting part is what we DO with it (impact.py).
"""

from collections import defaultdict

from model import AgentConfig


class DependencyGraph:
    def __init__(self, nodes: list[AgentConfig]):
        self.nodes = {n.name: n for n in nodes}

        # component name -> set of node names that declare ANY dependency on it
        self.component_to_dependents: dict[str, set[str]] = defaultdict(set)
        # (component, section) -> set of node names that declare that section
        self.section_to_dependents: dict[tuple[str, str], set[str]] = defaultdict(set)
        # node name -> node names that depend on it (for transitive traversal
        # through the workflow layer, which depends on agents, not components)
        self.node_to_direct_node_dependents: dict[str, set[str]] = defaultdict(set)

        self._index(nodes)

    def _index(self, nodes: list[AgentConfig]):
        agent_names = {n.name for n in nodes}
        for node in nodes:
            for dep in node.dependencies:
                self.component_to_dependents[dep.component].add(node.name)
                for section in dep.sections:
                    self.section_to_dependents[(dep.component, section)].add(node.name)
                # if this "component" name is actually another node (agent),
                # record a node->node edge for transitive traversal
                if dep.component in agent_names:
                    self.node_to_direct_node_dependents[dep.component].add(node.name)

    def direct_dependents(self, component: str) -> set[str]:
        """Nodes that declare a direct dependency on this component, at all."""
        return set(self.component_to_dependents.get(component, set()))

    def structural_blast_radius(self, component: str) -> set[str]:
        """Every node reachable by following dependency edges transitively --
        the conservative 'could be affected' answer. Since our synthetic
        system is two layers (components -> agents -> workflows), this
        equals direct dependents plus anything downstream of them.
        """
        affected = set()
        frontier = self.direct_dependents(component)
        while frontier:
            affected |= frontier
            next_frontier = set()
            for name in frontier:
                next_frontier |= self.node_to_direct_node_dependents.get(name, set())
            frontier = next_frontier - affected
        return affected

    def section_dependents(self, component: str, section: str) -> set[str]:
        """Nodes that declared a dependency on this SPECIFIC section."""
        return set(self.section_to_dependents.get((component, section), set()))
