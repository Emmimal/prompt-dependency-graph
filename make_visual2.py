import json
import subprocess
import sys

import matplotlib.pyplot as plt

# Always regenerate from a live run rather than trusting a stale copy of the
# numbers -- this is what let the old hardcoded values silently drift out of
# sync with the actual code after a graph-model fix.
subprocess.run([sys.executable, "run_sharing_experiments.py"], check=True)
with open("sharing_results.json") as f:
    data = json.load(f)

rows = data["rows"]
shares = [r["pct_of_agents"] for r in rows]
reduction = [r["reduction"] for r in rows]
labels = [r["section"].replace(" (universal)", "\n(universal)") for r in rows]

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(shares, reduction, marker="o", markersize=9, linewidth=2.5, color="#2b6cb0", zorder=3)
for x, y, label in zip(shares, reduction, labels):
    ax.annotate(f"{y}%", (x, y), textcoords="offset points", xytext=(0, 12),
                ha="center", fontsize=10, fontweight="bold", color="#2d3748")
    ax.annotate(label, (x, y), textcoords="offset points", xytext=(0, -22),
                ha="center", fontsize=8.5, color="#718096")

ax.axhline(0, color="#cbd5e0", linewidth=1, zorder=1)
ax.set_xlabel("component sharing level (% of agents that depend on it)", fontsize=10.5)
ax.set_ylabel("candidate blast radius reduction vs. reachable ceiling", fontsize=10.5)
ax.set_title("Dependency-aware evaluation helps most for selectively shared components",
             fontsize=12.5, fontweight="bold", pad=14)
ax.set_ylim(-8, 100)
ax.set_xlim(0, 110)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)

plt.tight_layout()
plt.savefig("visual2_sharing_curve.png",
            dpi=180, bbox_inches="tight")
print("saved visual2")
