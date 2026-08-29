"""
Renders a curated, readable subgraph of the real 55-node system for the
base-policy/refunds change -- not all 55 nodes (unreadable), but a
representative slice: base-policy, its section, a sample of consumers
per role, and the workflows, colored by their real status from the
actual impact report (not hand-picked for effect).
"""

import networkx as nx
import matplotlib.pyplot as plt

from agents import build_agents, build_workflows
from components import COMPONENTS_V1, make_v2
from graph import DependencyGraph
from impact import compute_impact

agents = build_agents()
workflows = build_workflows(agents)
all_nodes = agents + workflows
g = DependencyGraph(all_nodes)

old = COMPONENTS_V1["base-policy"]
new = make_v2("base-policy", "refunds", "Customers may request refunds within 14 days of purchase.")
report = compute_impact(g, old, new)

# Build a readable subgraph: base-policy + 2 sample consumers per role that
# touch base-policy at all, plus every workflow (only 5, always readable).
sample_agents = []
seen_roles = set()
for a in agents:
    if "base-policy" not in a.component_names():
        continue
    if a.role not in seen_roles or sum(1 for s in sample_agents if s.role == a.role) < 2:
        sample_agents.append(a)
    seen_roles.add(a.role)
    if len(sample_agents) >= 10:
        break

G = nx.DiGraph()
G.add_node("base-policy", kind="component")
for a in sample_agents:
    G.add_node(a.name, kind="agent")
    G.add_edge("base-policy", a.name)
for w in workflows:
    G.add_node(w.name, kind="workflow")
    for a in sample_agents:
        if w.name in g.node_to_direct_node_dependents.get(a.name, set()):
            G.add_edge(a.name, w.name)

pos = nx.spring_layout(G, seed=3, k=1.1)

fig, ax = plt.subplots(figsize=(10, 7))

for node in G.nodes:
    kind = G.nodes[node]["kind"]
    if node == "base-policy":
        color, size = "#c53030", 1400
    elif node in report.candidate:
        color, size = "#dd6b20", 900
    elif node in report.structural:
        color, size = "#a0aec0", 700
    else:
        color, size = "#e2e8f0", 500
    nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=color,
                            node_size=size, ax=ax, edgecolors="#2d3748", linewidths=1.2)

nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#a0aec0", arrows=True,
                        arrowsize=12, width=1.2, connectionstyle="arc3,rad=0.05")
nx.draw_networkx_labels(G, pos, ax=ax, font_size=7.5)

legend_handles = [
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#c53030", markersize=12, label="changed component"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#dd6b20", markersize=12, label="candidate (declared this section)"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#a0aec0", markersize=12, label="reachable, not a candidate"),
]
ax.legend(handles=legend_handles, loc="upper left", fontsize=9, frameon=False)
ax.set_title(f"base-policy / refunds changed  —  {len(report.structural)} reachable, {len(report.candidate)} candidates\n(representative subgraph; sample of {len(sample_agents)} of {len(report.structural)} reachable agents shown)",
             fontsize=11.5, fontweight="bold")
ax.axis("off")

plt.tight_layout()
plt.savefig("visual3_real_change.png",
            dpi=180, bbox_inches="tight")
print("saved visual3")
print(f"reachable={len(report.structural)} candidate={len(report.candidate)} sample_shown={len(sample_agents)}")
