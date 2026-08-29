"""
Small library of shared, versioned prompt components.

These are the "base-policy", "tone", "format" etc. building blocks that
the ~50 synthetic agents compose. Kept deliberately small (a handful of
components, 2-4 sections each) so the whole system fits in one sitting.
"""

from model import PromptComponent

# version 1 of each component (the "before" state)
COMPONENTS_V1: dict[str, PromptComponent] = {
    "base-policy": PromptComponent(
        name="base-policy",
        version=1,
        sections={
            "refunds": "Customers may request refunds within 30 days of purchase.",
            "privacy": "Never expose customer PII in responses, logs, or summaries.",
            "escalation": "Escalate disputes over $500 to a human agent immediately.",
        },
    ),
    "tone": PromptComponent(
        name="tone",
        version=1,
        sections={
            "professional": "Respond formally. Avoid slang, emoji, and contractions.",
            "concise": "Keep responses under 3 sentences unless detail is requested.",
        },
    ),
    "format": PromptComponent(
        name="format",
        version=1,
        sections={
            "json": "Return output as a single JSON object with no extra prose.",
            "markdown": "Return output as Markdown with headers for each section.",
        },
    ),
    "domain": PromptComponent(
        name="domain",
        version=1,
        sections={
            "billing": "You have expertise in invoices, subscriptions, and refunds.",
            "product": "You have expertise in product features and troubleshooting.",
        },
    ),
    "safety": PromptComponent(
        name="safety",
        version=1,
        sections={
            "no-medical-advice": "Never provide medical diagnoses or treatment advice.",
            "no-legal-advice": "Never provide binding legal advice; suggest a professional.",
        },
    ),
}


def make_v2(component_name: str, section: str, new_text: str) -> PromptComponent:
    """Produce version 2 of a component with exactly one section changed.

    This is the mechanism the experiments use to make a single, isolated
    edit and then measure blast radius -- everything else about the
    component is left untouched.
    """
    original = COMPONENTS_V1[component_name]
    new_sections = dict(original.sections)
    if section not in new_sections:
        raise KeyError(f"{component_name} has no section '{section}'")
    new_sections[section] = new_text
    return PromptComponent(name=component_name, version=2, sections=new_sections)
