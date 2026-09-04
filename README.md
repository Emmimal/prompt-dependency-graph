# prompt-dependency-graph

A pure-Python dependency graph for composable LLM prompts — section-level change tracking that separates the full dependency reach of an edit from the smaller set that actually needs targeted re-evaluation.

![Python Version](https://img.shields.io/badge/python-3.12-blue) ![License](https://img.shields.io/badge/license-MIT-green)

Composable prompts create hidden dependencies. Change one shared block — a base policy, a tone guide, an output schema — and you don't know which of your downstream agents actually need re-testing. This library gives you two numbers for any change: the full **reachable** ceiling (everyone downstream of the component, transitively) and the narrower **candidate** set (only the nodes that declared a dependency on the specific section that changed).

Read the full write-up on Towards Data Science → [Changing One Prompt Can Affect 50 Others — I Built a Prompt Dependency Graph](https://towardsdatascience.com/changing-one-prompt-can-affect-50-others-i-built-a-prompt-dependency-graph-to-find-what-needs-retesting/)

## What It Does

```
PromptComponent (versioned, named sections)
        │
        ▼
DependencyGraph ──┬── structural_blast_radius()  → Reachable (the ceiling)
                  └── section_dependents()       → Candidate (this edit)
                              │
                              ▼
                    Targeted evaluation set
```

| Component | Job |
|---|---|
| `PromptComponent` | Versioned prompt block broken into named sections, not an opaque blob of text |
| `AgentConfig` | A prompt config declaring which sections it depends on, and how (`imports` / `inherits` / `references` / `formats-with`) |
| `DependencyGraph` | Indexes component-level and section-level dependents; does the breadth-first transitive walk |
| `changed_sections()` | Mechanical text diff between two component versions — no embeddings, no semantic judgment |
| `compute_impact()` | Runs the graph traversal twice: once from the whole component (Reachable), once from only the changed section (Candidate) |

## Installation

```bash
git clone https://github.com/Emmimal/prompt-dependency-graph.git
cd prompt-dependency-graph
```

No dependencies for the core mechanism — pure standard library. `matplotlib` and `networkx` are only needed to regenerate the figures:

```bash
pip install matplotlib networkx
```

## Quick Start

```python
from model import PromptComponent, AgentConfig
from graph import DependencyGraph
from components import make_v2
from impact import compute_impact

base_policy_v1 = PromptComponent(
    name="base-policy",
    version=1,
    sections={"refunds": "Customers may request refunds within 30 days of purchase."},
)

support_agent = AgentConfig(name="support-core", role="support")
support_agent.depends_on("base-policy", ["refunds"], kind="imports")

sales_agent = AgentConfig(name="sales-core", role="sales")
sales_agent.depends_on("base-policy", ["privacy"], kind="imports")  # different section

graph = DependencyGraph([support_agent, sales_agent])

base_policy_v2 = make_v2("base-policy", "refunds",
    "Customers may request refunds within 14 days of purchase.")

report = compute_impact(graph, base_policy_v1, base_policy_v2)
print(report.summary())
# Reachable (ceiling):   2   <- both agents depend on base-policy somehow
# Candidate (this edit): 1   <- only support-core declared the "refunds" section
```

## Running the Experiments

Everything in the article reproduces from one entry point:

```bash
python run_all.py
```

| Script | What It Shows |
|---|---|
| `run_experiments.py` | Five real changes: `base-policy` (×2), `tone`, `format`, `safety` |
| `run_sharing_experiments.py` | Candidate narrowing across 10/25/50/75/100% component sharing levels |
| `flat_vs_deep.py` | Isolated flat-vs-transitive dependency shape comparison |
| `make_visual1.py` / `make_visual2.py` / `make_visual3.py` | Regenerates the three figures from live data, never hardcoded |
| `benchmark.py` | Real `time.perf_counter()` timings for graph build and `compute_impact()` |

## Project Structure

```
prompt-dependency-graph/
├── model.py                       # PromptComponent, SectionDependency, AgentConfig
├── components.py                  # 5 shared components + make_v2() versioning helper
├── agents.py                      # 50-agent, 5-workflow synthetic system generator
├── graph.py                       # DependencyGraph: direct/transitive/section-level indexes
├── impact.py                      # changed_sections() + compute_impact() + ImpactReport
├── sharing_experiment.py          # Controlled-sharing-level component for the curve test
├── flat_vs_deep.py                # Isolated flat vs. transitive shape comparison
├── run_experiments.py             # The five main change scenarios
├── run_sharing_experiments.py     # 10/25/50/75/100% sharing curve
├── benchmark.py                   # Real timing measurements
├── make_visual1.py                # Direct-vs-transitive lookup figure
├── make_visual2.py                # Sharing-level curve figure
├── make_visual3.py                # Candidate-vs-reachable subgraph figure
└── run_all.py                     # Single entry point, runs everything above in order
```

## Performance (CPU only, 55-node system)

| Operation | Latency | Notes |
|---|---|---|
| Build graph (55 nodes, 5 components) | 0.229 ms | avg of 200 builds |
| `compute_impact()` single call | 0.0375 ms | avg of 2,000 calls |
| `compute_impact()` × 1,000 calls | 31.91 ms | single timed block, no caching |

The mechanism itself is not the bottleneck in any realistic deployment — whatever evaluation suite you run against the candidate set will dominate total cost by a wide margin.

## When to Use This

Worth it when you have:
- Prompts composed out of shared building blocks (a base policy, a tone guide, an output schema) reused across multiple agents
- Enough agents that "which ones does this change actually touch" is a real question, not something you can hold in your head
- A prompt evaluation suite that gets slower every time you add another agent, and you want a principled way to scope what to re-run

Skip it when you have:
- Prompts with no shared structure — every agent has a fully independent system prompt, so there's no dependency graph to build
- A need to know whether behavior actually changed, not just what's structurally downstream — this tool tells you where to look, not what you'll find when you look

## Known Limitations

- Section diffing is purely mechanical (`old_text.strip() != new_text.strip()`) — a one-character fix and a full section rewrite are both just "changed." No semantic judgment, by design.
- Section renames aren't inferred. Renaming `refund_policy` to `refunds` is reported as one section removed and one added, not tracked as the same section under a new name.
- Dependency `kind` (`imports` / `inherits` / `references` / `formats-with`) is modeled but not yet load-bearing — the impact calculator treats all four identically.
- No circular dependency handling — the synthetic system was built without cycles.
- Validated on a 55-node synthetic system, not a production-scale prompt library. Whether a real system shows the same narrowing pattern depends entirely on its own dependency structure.

## Related Articles

## Related Reading

- **[Context Windows Don’t Know What’s Still True — I Built a System That Does](https://towardsdatascience.com/author/emmimalp.alexander/)**
- **[Changing One Prompt Can Affect 50 Others — I Built a Prompt Dependency Graph to Find What Needs Retesting](https://towardsdatascience.com/changing-one-prompt-can-affect-50-others-i-built-a-prompt-dependency-graph-to-find-what-needs-retesting/)**

## License

MIT
