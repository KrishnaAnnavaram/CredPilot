"""
Policy corpus model: schema, version resolution and Markdown rendering.

The corpus is the retrieval target for the agentic-RAG tool (REQ-076). It is built
from structured definitions rather than hand-written files so that every rule keeps
a stable identifier, every document carries machine-readable metadata, and the
policies.csv / policy_rules.csv metadata tables cannot drift from the prose.

SOURCE CLASSIFICATION
---------------------
Every rule declares where its authority comes from. The five categories are fixed:

REGULATORY            A federal consumer-protection or banking obligation described
                      in the completed research report and attributable to a named
                      regulation (Reg B / Reg Z / Reg X / FCRA / HMDA / CIP).
AGENCY_INVESTOR       A published agency or investor guideline recorded in the
                      research report (Fannie Mae, Freddie Mac, FHA, VA, USDA, FHFA).
PUBLIC_LENDER_GUIDANCE  Something a named lender publishes about itself. Used only
                      to describe the *shape* of public lender disclosure; no real
                      lender's internal credit policy is reproduced anywhere.
COMMON_INDUSTRY_PRACTICE  An operational practice the research report describes as
                      common to mortgage origination without being a statutory rule.
SYNTHETIC_INTERNAL_POLICY  Invented by this project so the hackathon has
                      deterministic, testable thresholds. These are the rules that
                      carry numbers. They are NOT any real institution's policy.

Any numeric threshold that drives a pass/fail outcome in this dataset is
SYNTHETIC_INTERNAL_POLICY unless the research report establishes the exact value as
a genuine public rule for that product and context. Where the research report does
establish a public framework (for example the agency DTI definition), the rule
states the framework and cites the report, and a separate synthetic rule carries the
number this project actually enforces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Sequence

SOURCE_CATEGORIES = (
    "REGULATORY",
    "AGENCY_INVESTOR",
    "PUBLIC_LENDER_GUIDANCE",
    "COMMON_INDUSTRY_PRACTICE",
    "SYNTHETIC_INTERNAL_POLICY",
)

SEVERITIES = ("HARD_FAIL", "CONDITIONAL", "REFER", "ADVISORY")

OUTCOME_TYPES = ("PASS_FAIL", "PASS_REFER_FAIL", "CALCULATION", "PROCESS")

#: The fictional lender whose internal policy this corpus represents. Named so no
#: reader can mistake a synthetic threshold for a real institution's rule.
SYNTHETIC_LENDER = "Northwind Residential Lending (fictional)"


@dataclass(frozen=True)
class Rule:
    """One addressable rule inside a policy document."""

    rule_id: str
    title: str
    source_category: str
    severity: str
    outcome_type: str
    statement: str
    applies_when: str = "All applications within this document's scope."
    parameters: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[str, ...] = ()
    exception: str | None = None
    condition_template: str | None = None
    requires_human_review: bool = False
    research_reference: str | None = None
    cross_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.source_category not in SOURCE_CATEGORIES:
            raise ValueError(f"{self.rule_id}: bad source_category {self.source_category}")
        if self.severity not in SEVERITIES:
            raise ValueError(f"{self.rule_id}: bad severity {self.severity}")
        if self.outcome_type not in OUTCOME_TYPES:
            raise ValueError(f"{self.rule_id}: bad outcome_type {self.outcome_type}")
        if self.source_category not in (
            "SYNTHETIC_INTERNAL_POLICY",
            "AGENCY_INVESTOR",
            "REGULATORY",
        ):
            # A number that drives behaviour must name the authority it came from.
            # Descriptive string parameters (a vocabulary, a formula) are unrestricted.
            numeric = [
                k
                for k, v in self.parameters.items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)
            ]
            if numeric:
                raise ValueError(
                    f"{self.rule_id}: {self.source_category} cannot carry the numeric "
                    f"threshold(s) {numeric}; label it SYNTHETIC_INTERNAL_POLICY or cite "
                    "an agency/regulatory source for the exact value"
                )


@dataclass(frozen=True)
class Policy:
    """One version of one policy document."""

    policy_id: str
    title: str
    version: str
    effective_date: date
    family: str
    purpose: str
    scope_note: str
    rules: tuple[Rule, ...]
    product_scope: tuple[str, ...]
    occupancy_scope: tuple[str, ...] = ("primary_residence", "second_home", "investment")
    purpose_scope: tuple[str, ...] = ("purchase", "rate_term_refinance", "cash_out_refinance")
    jurisdiction: str = "US"
    source_category: str = "SYNTHETIC_INTERNAL_POLICY"
    priority: int = 50
    expiration_date: date | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    requires_human_review: bool = False
    definitions: tuple[tuple[str, str], ...] = ()
    documentation: tuple[str, ...] = ()
    exceptions_note: str | None = None
    related_policies: tuple[str, ...] = ()
    version_note: str | None = None
    owner: str = "Credit Policy Office"

    @property
    def slug(self) -> str:
        return f"{self.policy_id}_{self.family}_v{self.version}"

    @property
    def filename(self) -> str:
        return f"{self.slug}.md"


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _yaml_list(values: Sequence[str], indent: str = "  ") -> str:
    if not values:
        return " []"
    return "\n" + "\n".join(f"{indent}- {v}" for v in values)


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, date):
        return value.isoformat()
    text = str(value)
    if any(ch in text for ch in ":#{}[],&*?|-<>=!%@`") and not text.startswith('"'):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def render_policy(policy: Policy) -> str:
    """Render one policy version as a Markdown document with YAML front matter.

    The front matter is what the retriever filters on; the body is what it reads.
    Thresholds deliberately do not appear in the filename or the title, so a
    retriever cannot answer a threshold question without reading the document.
    """
    lines: list[str] = ["---"]
    lines.append(f"policy_id: {policy.policy_id}")
    lines.append(f"title: {_yaml_scalar(policy.title)}")
    lines.append(f"version: {policy.version}")
    lines.append(f"family: {policy.family}")
    lines.append(f"effective_date: {policy.effective_date.isoformat()}")
    lines.append(
        "expiration_date: "
        + (policy.expiration_date.isoformat() if policy.expiration_date else "null")
    )
    lines.append("product_scope:" + _yaml_list(policy.product_scope))
    lines.append("occupancy_scope:" + _yaml_list(policy.occupancy_scope))
    lines.append("purpose_scope:" + _yaml_list(policy.purpose_scope))
    lines.append(f"jurisdiction: {policy.jurisdiction}")
    lines.append(f"source_category: {policy.source_category}")
    lines.append(f"priority: {policy.priority}")
    lines.append(f"supersedes: {_yaml_scalar(policy.supersedes)}")
    lines.append(f"superseded_by: {_yaml_scalar(policy.superseded_by)}")
    lines.append(
        f"requires_human_review: {'true' if policy.requires_human_review else 'false'}"
    )
    lines.append(f"issuer: {_yaml_scalar(SYNTHETIC_LENDER)}")
    lines.append(f"owner: {_yaml_scalar(policy.owner)}")
    lines.append("rule_ids:" + _yaml_list([r.rule_id for r in policy.rules]))
    lines.append("synthetic: true")
    lines.append("---")
    lines.append("")

    lines.append(f"# {policy.title}")
    lines.append("")
    lines.append(
        f"**{policy.policy_id} · version {policy.version} · effective "
        f"{policy.effective_date.isoformat()}**"
    )
    lines.append("")
    lines.append(
        "> This is a **synthetic lending policy** written for the CredPilot hackathon "
        f"and attributed to {SYNTHETIC_LENDER}. It is not the policy of any real "
        "lender, and no proprietary automated-underwriting logic is reproduced in it. "
        "Each rule below declares its own `source_category`; only rules marked "
        "`SYNTHETIC_INTERNAL_POLICY` invent a number."
    )
    lines.append("")

    lines.append("## 1. Purpose")
    lines.append("")
    lines.append(policy.purpose)
    lines.append("")

    lines.append("## 2. Scope")
    lines.append("")
    lines.append(policy.scope_note)
    lines.append("")
    lines.append(f"- **Products:** {', '.join(policy.product_scope)}")
    lines.append(f"- **Occupancy:** {', '.join(policy.occupancy_scope)}")
    lines.append(f"- **Loan purpose:** {', '.join(policy.purpose_scope)}")
    lines.append(f"- **Jurisdiction:** {policy.jurisdiction}")
    lines.append("")

    if policy.definitions:
        lines.append("## 3. Definitions")
        lines.append("")
        for term, meaning in policy.definitions:
            lines.append(f"**{term}.** {meaning}")
            lines.append("")

    lines.append("## 4. Rules")
    lines.append("")
    for rule in policy.rules:
        lines.extend(_render_rule(rule))

    if policy.documentation:
        lines.append("## 5. Documentation requirements")
        lines.append("")
        for item in policy.documentation:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## 6. Exceptions and escalation")
    lines.append("")
    lines.append(
        policy.exceptions_note
        or "Any departure from this document requires a documented exception approved "
        "under POL-UWR-001. An exception is never granted by an automated component."
    )
    lines.append("")

    if policy.related_policies:
        lines.append("## 7. Related policies")
        lines.append("")
        for ref in policy.related_policies:
            lines.append(f"- {ref}")
        lines.append("")

    lines.append("## 8. Version history")
    lines.append("")
    lines.append("| Version | Effective | Note |")
    lines.append("| --- | --- | --- |")
    if policy.supersedes:
        lines.append(
            f"| (prior) | before {policy.effective_date.isoformat()} | "
            f"Superseded by this version. Prior version identifier: {policy.supersedes}. |"
        )
    lines.append(
        f"| {policy.version} | {policy.effective_date.isoformat()} | "
        + (policy.version_note or "Current version within its effective window.")
        + " |"
    )
    if policy.superseded_by:
        lines.append(
            f"| (later) | from {(policy.expiration_date or policy.effective_date).isoformat()} | "
            f"This version is superseded by {policy.superseded_by}. |"
        )
    lines.append("")
    lines.append(
        "An application is evaluated against the version whose effective window "
        "contains the application's underwriting as-of date. Retrieving the newest "
        "version of a policy is not the same as retrieving the applicable one."
    )
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _render_rule(rule: Rule) -> list[str]:
    out: list[str] = [f"### {rule.rule_id} — {rule.title}", ""]
    out.append(
        f"- **Source category:** `{rule.source_category}`"
        f" · **Severity:** `{rule.severity}`"
        f" · **Outcome:** `{rule.outcome_type}`"
    )
    if rule.requires_human_review:
        out.append("- **Human review:** required when this rule is triggered.")
    out.append("")
    out.append(f"**Applies when.** {rule.applies_when}")
    out.append("")
    out.append(rule.statement)
    out.append("")
    if rule.parameters:
        out.append("| Parameter | Value |")
        out.append("| --- | --- |")
        for key, value in rule.parameters.items():
            out.append(f"| `{key}` | {_param_display(value)} |")
        out.append("")
    if rule.evidence:
        out.append("**Acceptable evidence.** " + "; ".join(rule.evidence) + ".")
        out.append("")
    if rule.condition_template:
        out.append(
            "**Condition raised when unsatisfied.** " + rule.condition_template
        )
        out.append("")
    if rule.exception:
        out.append(f"**Exception.** {rule.exception}")
        out.append("")
    if rule.cross_refs:
        out.append("**See also:** " + ", ".join(rule.cross_refs) + ".")
        out.append("")
    if rule.research_reference:
        out.append(
            "**Basis.** " + rule.research_reference
        )
        out.append("")
    return out


def _param_display(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        if 0 < value < 1:
            return f"{value * 100:.2f}".rstrip("0").rstrip(".") + "%"
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, dict):
        return "; ".join(f"{k}: {_param_display(v)}" for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return ", ".join(_param_display(v) for v in value)
    return str(value)


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def build_registry(policies: Sequence[Policy]) -> dict[str, list[Policy]]:
    """Group policy versions by policy_id, ordered by effective date."""
    registry: dict[str, list[Policy]] = {}
    for policy in policies:
        registry.setdefault(policy.policy_id, []).append(policy)
    for versions in registry.values():
        versions.sort(key=lambda p: p.effective_date)
    return registry


def effective_policy(
    registry: dict[str, list[Policy]], policy_id: str, as_of: date
) -> Policy:
    """The version of `policy_id` in force on `as_of`.

    This is the temporal-retrieval contract the copilot must reproduce: selection is
    by effective window, never by 'latest'.
    """
    versions = registry.get(policy_id)
    if not versions:
        raise KeyError(f"unknown policy_id {policy_id}")
    chosen: Policy | None = None
    for policy in versions:
        if policy.effective_date <= as_of and (
            policy.expiration_date is None or as_of < policy.expiration_date
        ):
            chosen = policy
    if chosen is None:
        # Before the first effective date: the earliest version governs, and the
        # caller is told so rather than being handed the newest silently.
        chosen = versions[0]
    return chosen


def effective_rule(
    registry: dict[str, list[Policy]], rule_id: str, as_of: date
) -> tuple[Policy, Rule]:
    """Find the rule by id in whichever policy version is in force on `as_of`."""
    for policy_id, versions in registry.items():
        if any(any(r.rule_id == rule_id for r in v.rules) for v in versions):
            policy = effective_policy(registry, policy_id, as_of)
            for rule in policy.rules:
                if rule.rule_id == rule_id:
                    return policy, rule
    raise KeyError(f"unknown rule_id {rule_id} as of {as_of}")


def param(
    registry: dict[str, list[Policy]], rule_id: str, key: str, as_of: date
) -> Any:
    """Read one parameter off the rule version in force on `as_of`."""
    _policy, rule = effective_rule(registry, rule_id, as_of)
    if key not in rule.parameters:
        raise KeyError(f"{rule_id} has no parameter {key} as of {as_of}")
    return rule.parameters[key]
