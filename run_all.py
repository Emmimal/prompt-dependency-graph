"""
Single entry point: reproduces every number and image used in the
article, in the same order they were generated.

Usage:
    pip install matplotlib networkx
    python3 run_all.py
"""

import subprocess
import sys

STEPS = [
    ("run_experiments.py", "5 original changes: base-policy x2, tone, format, safety"),
    ("run_sharing_experiments.py", "10/25/50/75/100% sharing-level curve"),
    ("flat_vs_deep.py", "isolated flat vs. deep dependency shape comparison"),
    ("make_visual1.py", "visual1_direct_vs_traversal.png"),
    ("make_visual2.py", "visual2_sharing_curve.png"),
    ("make_visual3.py", "visual3_real_change.png"),
    ("benchmark.py", "runtime table: build graph / single call / 1,000 calls"),
]

for script, description in STEPS:
    print("=" * 70)
    print(f"Running {script}  ({description})")
    print("=" * 70)
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"\n{script} failed (exit code {result.returncode}) -- stopping.")
        sys.exit(result.returncode)
    print()

print("=" * 70)
print("Done. All numbers printed above (including the runtime table);")
print("PNGs written to this directory:")
print("  visual1_direct_vs_traversal.png")
print("  visual2_sharing_curve.png")
print("  visual3_real_change.png")
print("=" * 70)
