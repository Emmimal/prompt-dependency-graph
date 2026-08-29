"""
A component built specifically to control sharing level, so we can test
whether candidate-reduction forms a curve against how widely a component
is shared -- rather than relying on the incidental sharing levels of the
organically-designed base-policy/tone/format/safety components.
"""

from model import PromptComponent, AgentConfig

EXPERIMENT_V1 = PromptComponent(
    name="experiment",
    version=1,
    sections={
        "share-10": "Rollout flag: enable feature X for pilot cohort.",
        "share-25": "Rollout flag: enable feature Y for expanded cohort.",
        "share-50": "Rollout flag: enable feature Z for half the fleet.",
        "share-75": "Rollout flag: enable feature W for most of the fleet.",
    },
)


def pick_evenly(items: list, k: int) -> list:
    """Pick k items spread evenly across the list (by index), so the
    sample isn't clustered inside a single role."""
    n = len(items)
    if k >= n:
        return list(items)
    step = n / k
    indices = sorted({int(i * step) for i in range(k)})
    return [items[i] for i in indices]


def attach_sharing_tiers(agents: list[AgentConfig]) -> None:
    """Mutates agents in place, adding nested share-10/25/50/75 deps.
    Nested so share-75 is a superset of share-50, etc. -- this isolates
    "how many consumers" as the one variable under test.
    """
    n = len(agents)
    tiers = {
        "share-10": pick_evenly(agents, round(n * 0.10)),
        "share-25": pick_evenly(agents, round(n * 0.25)),
        "share-50": pick_evenly(agents, round(n * 0.50)),
        "share-75": pick_evenly(agents, round(n * 0.75)),
    }
    for section, chosen in tiers.items():
        for agent in chosen:
            agent.depends_on("experiment", [section], kind="references")
