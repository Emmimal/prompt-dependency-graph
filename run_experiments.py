from agents import build_agents, build_workflows
from components import COMPONENTS_V1, make_v2
from graph import DependencyGraph
from impact import compute_impact

agents = build_agents()
workflows = build_workflows(agents)
all_nodes = agents + workflows
graph = DependencyGraph(all_nodes)

print(f"System: {len(agents)} agents + {len(workflows)} workflows = {len(all_nodes)} nodes\n")

# The five changes from the locked protocol:
# change policy, change tone, change format, change a highly-shared
# component, change a leaf component.
experiments = [
    ("base-policy", "refunds", "Customers may request refunds within 14 days of purchase."),
    ("tone", "professional", "Respond formally and warmly. Avoid slang and emoji."),
    ("format", "json", "Return output as a single minified JSON object, no prose, no markdown."),
    ("base-policy", "privacy", "Never expose customer PII in responses, logs, summaries, or analytics events."),
    ("safety", "no-medical-advice", "Never provide medical diagnoses, dosages, or treatment plans."),
]

results = []
for component, section, new_text in experiments:
    old = COMPONENTS_V1[component]
    new = make_v2(component, section, new_text)
    report = compute_impact(graph, old, new)
    results.append(report)
    print(report.summary())
    print()

print("=" * 60)
print(f"{'Change':<28}{'Structural':>11}{'Candidate':>11}{'Reduction':>11}")
for r in results:
    label = f"{r.component}/{r.changed_sections[0]}"
    reduction = 100 * (1 - len(r.candidate) / len(r.structural)) if r.structural else 0
    print(f"{label:<28}{len(r.structural):>11}{len(r.candidate):>11}{reduction:>10.0f}%")
