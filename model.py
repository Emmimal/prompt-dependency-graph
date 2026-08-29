"""
Core data model for the prompt dependency graph toy system.

A PromptComponent is a reusable, versioned block of prompt text broken
into named sections (e.g. "refunds", "privacy"). Agents don't depend on
a whole component blindly -- they declare which specific sections they
actually consume, which is what makes candidate blast radius possible.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PromptComponent:
    name: str
    version: int
    sections: dict[str, str]  # section name -> section text

    @property
    def key(self) -> str:
        return f"{self.name}@{self.version}"


@dataclass
class SectionDependency:
    """One agent's dependency on specific sections of one component."""
    component: str          # component name, e.g. "base-policy"
    sections: list[str]     # which sections this agent actually uses
    kind: str = "imports"   # imports | inherits | references | formats-with


@dataclass
class AgentConfig:
    """A synthetic agent/prompt config that consumes one or more components."""
    name: str
    role: str
    dependencies: list[SectionDependency] = field(default_factory=list)

    def depends_on(self, component: str, sections: list[str], kind: str = "imports"):
        self.dependencies.append(SectionDependency(component, sections, kind))
        return self

    def component_names(self) -> set[str]:
        return {d.component for d in self.dependencies}
