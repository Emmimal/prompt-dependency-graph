import json

from agents import build_agents, build_workflows
from components import COMPONENTS_V1, make_v2
from sharing_experiment import EXPERIMENT_V1, attach_sharing_tiers
from graph import DependencyGraph
from impact import compute_impact
from model import PromptComponent

agents = build_agents()
attach_sharing_tiers(agents)          # mutate BEFORE workflows are built
workflows = build_workflows(agents)   # so workflows inherit the tiers too
all_nodes = agents + workflows
graph = DependencyGraph(all_nodes)
num_agents = len(agents)
num_nodes = len(all_nodes)

print(f"System: {num_agents} agents + {len(workflows)} workflows = {num_nodes} nodes\n")


def make_experiment_v2(section: str, new_text: str) -> PromptComponent:
    new_sections = dict(EXPERIMENT_V1.sections)
    new_sections[section] = new_text
    return PromptComponent(name="experiment", version=2, sections=new_sections)


sharing_tests = [
    ("share-10", "Rollout flag: enable feature X for a small pilot group."),
    ("share-25", "Rollout flag: enable feature Y for a larger cohort."),
    ("share-50", "Rollout flag: enable feature Z for half the fleet, revised."),
    ("share-75", "Rollout flag: enable feature W for nearly the whole fleet."),
]

print(f"{'Section':<12}{'Direct':>8}{'% agents':>10}{'Structural':>12}{'Candidate':>11}{'Reduction':>11}")
rows = []
for section, new_text in sharing_tests:
    new_comp = make_experiment_v2(section, new_text)
    report = compute_impact(graph, EXPERIMENT_V1, new_comp)
    direct = len(graph.section_dependents("experiment", section))
    pct_agents = 100 * direct / num_agents
    reduction = 100 * (1 - len(report.candidate) / len(report.structural)) if report.structural else 0
    rows.append({
        "section": section,
        "direct": direct,
        "pct_of_agents": round(pct_agents, 1),
        "structural": len(report.structural),
        "candidate": len(report.candidate),
        "reduction": round(reduction, 1),
    })
    print(f"{section:<12}{direct:>8}{pct_agents:>9.1f}%{len(report.structural):>12}{len(report.candidate):>11}{reduction:>10.0f}%")

# tone (universal component) computed for real on this same graph, not hardcoded --
# attach_sharing_tiers doesn't touch tone, so this is a fair like-for-like comparison
tone_old = COMPONENTS_V1["tone"]
tone_new = make_v2("tone", "professional", "Respond formally and warmly. Avoid slang and emoji.")
tone_report = compute_impact(graph, tone_old, tone_new)
tone_direct = len(graph.direct_dependents("tone"))
tone_pct_agents = 100 * tone_direct / num_agents
tone_reduction = 100 * (1 - len(tone_report.candidate) / len(tone_report.structural)) if tone_report.structural else 0
rows.append({
    "section": "tone (universal)",
    "direct": tone_direct,
    "pct_of_agents": round(tone_pct_agents, 1),
    "structural": len(tone_report.structural),
    "candidate": len(tone_report.candidate),
    "reduction": round(tone_reduction, 1),
})
print(f"{'tone (100%)':<12}{tone_direct:>8}{tone_pct_agents:>9.1f}%{len(tone_report.structural):>12}{len(tone_report.candidate):>11}{tone_reduction:>10.0f}%")

with open("sharing_results.json", "w") as f:
    json.dump({"num_agents": num_agents, "num_nodes": num_nodes, "rows": rows}, f, indent=2)
