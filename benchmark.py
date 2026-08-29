"""
Actual timing measurements for the runtime claims made in the article.
Nothing here was hand-estimated -- every number printed is timed on this
machine, right now, using time.perf_counter().

Usage:
    python3 benchmark.py
"""

import time

from agents import build_agents, build_workflows
from components import COMPONENTS_V1, make_v2
from graph import DependencyGraph
from impact import compute_impact


def time_it(fn, repeats: int) -> float:
    """Returns total elapsed seconds for `repeats` calls to fn()."""
    start = time.perf_counter()
    for _ in range(repeats):
        fn()
    return time.perf_counter() - start


agents = build_agents()
workflows = build_workflows(agents)
all_nodes = agents + workflows

# --- Build graph ---
BUILD_REPEATS = 200
build_elapsed = time_it(lambda: DependencyGraph(all_nodes), BUILD_REPEATS)
build_ms = 1000 * build_elapsed / BUILD_REPEATS

# --- Single compute_impact() call ---
graph = DependencyGraph(all_nodes)
old = COMPONENTS_V1["base-policy"]
new = make_v2("base-policy", "refunds", "Customers may request refunds within 14 days of purchase.")

SINGLE_REPEATS = 2000
single_elapsed = time_it(lambda: compute_impact(graph, old, new), SINGLE_REPEATS)
single_ms = 1000 * single_elapsed / SINGLE_REPEATS

# --- 1,000 calls, timed as one block (matches the article's framing) ---
block_elapsed = time_it(lambda: compute_impact(graph, old, new), 1000)
block_ms = 1000 * block_elapsed

print(f"System: {len(agents)} agents + {len(workflows)} workflows = {len(all_nodes)} nodes\n")
print(f"{'Operation':<38}{'Latency':>12}   Notes")
print(f"{'Build graph (' + str(len(all_nodes)) + ' nodes, 5 components)':<38}"
      f"{build_ms:>9.3f} ms   avg of {BUILD_REPEATS} builds")
print(f"{'compute_impact() single call':<38}"
      f"{single_ms:>9.4f} ms   avg of {SINGLE_REPEATS} calls")
print(f"{'compute_impact() x 1,000 calls':<38}"
      f"{block_ms:>9.2f} ms   single timed block, no caching")
