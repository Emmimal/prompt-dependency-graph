"""
Section diffing + impact calculation.

Deliberately mechanical, per the locked v1 scope: a section is "changed"
iff its text differs between two versions. No embeddings, no semantic
judgment. The graph tells us who COULD be affected (structural) and who
declared a dependency on the specific thing that changed (candidate).
Whether behavior actually changed is a job for evaluation, not this code.
"""

from dataclasses import dataclass

from model import PromptComponent
from graph import DependencyGraph


def changed_sections(old: PromptComponent, new: PromptComponent) -> list[str]:
    if old.name != new.name:
        raise ValueError("comparing sections across two different components")
    changed = []
    for section, old_text in old.sections.items():
        new_text = new.sections.get(section)
        if new_text is None:
            changed.append(section)  # section removed -> treat as changed
            continue
        if old_text.strip() != new_text.strip():
            changed.append(section)
    return changed


@dataclass
class ImpactReport:
    component: str
    old_version: int
    new_version: int
    changed_sections: list[str]
    structural: set[str]
    candidate: set[str]

    def summary(self) -> str:
        reduction = 0.0
        if self.structural:
            reduction = 100 * (1 - len(self.candidate) / len(self.structural))
        lines = [
            f"Changed: {self.component}@{self.old_version} -> @{self.new_version}",
            f"Changed sections: {', '.join(self.changed_sections) or '(none)'}",
            f"Reachable (ceiling):   {len(self.structural)}",
            f"Candidate (this edit): {len(self.candidate)}",
            f"Reduction: {reduction:.0f}%",
        ]
        return "\n".join(lines)


def compute_impact(
    graph: DependencyGraph,
    old: PromptComponent,
    new: PromptComponent,
) -> ImpactReport:
    changed = changed_sections(old, new)

    structural = graph.structural_blast_radius(old.name)

    candidate: set[str] = set()
    for section in changed:
        candidate |= graph.section_dependents(old.name, section)
        # anything downstream of a directly-affected node is also a candidate
        frontier = candidate.copy()
        seen = set(candidate)
        while frontier:
            nxt = set()
            for name in frontier:
                nxt |= graph.node_to_direct_node_dependents.get(name, set())
            nxt -= seen
            candidate |= nxt
            seen |= nxt
            frontier = nxt

    return ImpactReport(
        component=old.name,
        old_version=old.version,
        new_version=new.version,
        changed_sections=changed,
        structural=structural,
        candidate=candidate,
    )
