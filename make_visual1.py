import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis("off")

nodes = ["comp-b", "agent-1", "workflow-1", "agent-2", "workflow-2"]
xs = [0.8, 2.8, 4.8, 6.8, 8.8]
y = 2.6

colors = ["#2b6cb0", "#e2e8f0", "#e2e8f0", "#e2e8f0", "#e2e8f0"]

for x, label, color in zip(xs, nodes, colors):
    box = FancyBboxPatch((x - 0.75, y - 0.4), 1.5, 0.8,
                          boxstyle="round,pad=0.05,rounding_size=0.08",
                          linewidth=1.4, edgecolor="#2d3748", facecolor=color)
    ax.add_patch(box)
    text_color = "white" if color == "#2b6cb0" else "#2d3748"
    ax.text(x, y, label, ha="center", va="center", fontsize=9.5,
             fontweight="bold" if color == "#2b6cb0" else "normal", color=text_color)

for i in range(len(xs) - 1):
    arrow = FancyArrowPatch((xs[i] + 0.75, y), (xs[i + 1] - 0.75, y),
                              arrowstyle="-|>", mutation_scale=14,
                              linewidth=1.4, color="#4a5568")
    ax.add_patch(arrow)

# direct-lookup bracket: only comp-b -> agent-1
ax.annotate("", xy=(xs[1], y + 0.9), xytext=(xs[0], y + 0.9),
            arrowprops=dict(arrowstyle="-", color="#c53030", lw=1.6))
ax.text((xs[0] + xs[1]) / 2, y + 1.15, "direct lookup\nfinds: 1",
         ha="center", fontsize=9.5, color="#c53030", fontweight="bold")

# graph traversal bracket: everything
ax.annotate("", xy=(xs[4], y - 1.1), xytext=(xs[0], y - 1.1),
            arrowprops=dict(arrowstyle="-", color="#2f855a", lw=1.6))
ax.text((xs[0] + xs[4]) / 2, y - 1.45, "graph traversal\nfinds: 4",
         ha="center", fontsize=9.5, color="#2f855a", fontweight="bold")

ax.set_title("A one-hop dependency lookup misses 3 of 4 real consumers",
              fontsize=12, fontweight="bold", pad=18)

plt.tight_layout()
plt.savefig("visual1_direct_vs_traversal.png",
            dpi=180, bbox_inches="tight")
print("saved visual1")
