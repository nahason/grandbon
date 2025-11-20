from dataclasses import dataclass, field
from typing import List
import streamlit as st

# ---------------------------
# Data model
# ---------------------------

@dataclass
class StoryArtifact:
    feature_description: str
    persona: str
    capability: str
    value: str
    user_story: str
    acceptance_criteria: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)


# ---------------------------
# Core logic (same as CLI prototype, lightly refactored)
# ---------------------------

def infer_persona(text: str) -> str:
    t = text.lower()
    if "admin" in t or "administrator" in t:
        return "system administrator"
    if "employee" in t or "staff" in t or "teller" in t:
        return "bank employee"
    if "customer" in t or "client" in t or "member" in t:
        return "banking customer"
    if "api" in t or "integration" in t:
        return "integrating system"
    return "user"


def extract_capability_and_value(text: str):
    t = text.strip()
    lower = t.lower()
    capability = t
    value = "so I can achieve my goal efficiently."
    # look for "so that" or "so I can"
    for marker in [" so that ", " so i can ", " so we can "]:
        if marker in lower:
            before, after = lower.split(marker, 1)
            capability = t[:len(before)].strip(" ,.")
            value = "so that " + t[len(before) + len(marker):].strip(" ,.")
            return capability, value
    # look for "i need", "we need", "i want", "we want"
    for marker in ["i need ", "we need ", "i want ", "we want "]:
        idx = lower.find(marker)
        if idx != -1:
            capability = t[idx + len(marker):].strip(" .")
            break
    return capability, value


def build_user_story(persona: str, capability: str, value: str) -> str:
    return f"As a {persona}, I want {capability}, {value}"


def generate_acceptance_criteria(feature_desc: str, persona: str) -> List[str]:
    base = feature_desc.lower()
    scenarios = []
    if any(k in base for k in ["login", "sign in", "authenticate"]):
        scenarios.append(
            "Scenario: Successful login\n"
            "  Given a valid registered account\n"
            "  When the user enters correct credentials\n"
            "  Then the user is authenticated and redirected to the dashboard"
        )
        scenarios.append(
            "Scenario: Invalid credentials\n"
            "  Given an existing account\n"
            "  When the user submits an incorrect username or password\n"
            "  Then the system rejects the login and displays a generic error message"
        )
        scenarios.append(
            "Scenario: Account lockout after repeated failures\n"
            "  Given an existing account\n"
            "  And the user has failed to log in multiple times\n"
            "  When the failed login attempt threshold is reached\n"
            "  Then the system locks the account and logs the event"
        )
    elif any(k in base for k in ["report", "dashboard", "analytics", "metrics"]):
        scenarios.append(
            "Scenario: Data successfully displayed\n"
            "  Given the user has access to the reporting feature\n"
            "  When the user opens the report or dashboard\n"
            "  Then the system loads and displays the relevant data for the selected period"
        )
        scenarios.append(
            "Scenario: Filters applied\n"
            "  Given the user is viewing a report\n"
            "  When the user applies a filter (e.g., date range, product, region)\n"
            "  Then the system refreshes the report using the selected filters"
        )
        scenarios.append(
            "Scenario: No data available\n"
            "  Given the user runs a report for a period with no activity\n"
            "  When the query completes\n"
            "  Then the system displays a clear 'No data available' message"
        )
    else:
        scenarios.append(
            "Scenario: Basic happy path\n"
            "  Given the required preconditions are met\n"
            "  When the user performs the primary action for this feature\n"
            "  Then the system completes the action successfully and confirms to the user"
        )
        scenarios.append(
            "Scenario: Missing or invalid input\n"
            "  Given the user has not provided all required information\n"
            "  When the user attempts to complete the action\n"
            "  Then the system prevents completion and highlights the missing or invalid fields"
        )
        scenarios.append(
            "Scenario: System error\n"
            "  Given an unexpected system error occurs during processing\n"
            "  When the user attempts the action\n"
            "  Then the system logs the error and displays a friendly error message with next steps"
        )
    return scenarios


def generate_assumptions(feature_desc: str) -> List[str]:
    t = feature_desc.lower()
    assumptions = [
        "Business rules for this feature are documented and approved.",
        "User roles and permissions are clearly defined."
    ]
    if "mobile" in t or "app" in t:
        assumptions.append("The mobile application framework and design system are already in place.")
    if "api" in t or "integration" in t:
        assumptions.append("All integrated systems expose stable, documented APIs.")
    if "login" in t or "authentication" in t or "mfa" in t:
        assumptions.append("An enterprise identity provider is available for authentication.")
    return assumptions


def generate_dependencies(feature_desc: str) -> List[str]:
    t = feature_desc.lower()
    deps = []
    if any(k in t for k in ["login", "authentication", "mfa"]):
        deps.append("Identity and access management service.")
        deps.append("MFA or OTP provider (if multi-factor is required).")
    if "payment" in t or "card" in t or "ach" in t:
        deps.append("Payment processing gateway or core banking integration.")
    if "report" in t or "dashboard" in t or "analytics" in t:
        deps.append("Reporting or analytics data store.")
    if "api" in t or "integration" in t:
        deps.append("Upstream and downstream APIs for integrated systems.")
    if not deps:
        deps.append("Core application platform and shared services.")
    return deps


def generate_success_metrics(feature_desc: str) -> List[str]:
    t = feature_desc.lower()
    metrics = []
    if any(k in t for k in ["login", "sign in", "authenticate"]):
        metrics.extend([
            "Login success rate (target >= 99%).",
            "Average authentication response time (target < 500 ms).",
            "Reduction in login-related support tickets after launch."
        ])
    elif any(k in t for k in ["report", "dashboard", "analytics"]):
        metrics.extend([
            "Average report load time (target < 3 seconds).",
            "Percentage of report runs completed without error.",
            "Increase in active reporting users or sessions."
        ])
    else:
        metrics.extend([
            "Task completion rate for the new feature.",
            "Average time to complete the primary workflow using this feature.",
            "Reduction in manual workarounds or related support tickets."
        ])
    return metrics


def build_artifact(feature_desc: str) -> StoryArtifact:
    persona = infer_persona(feature_desc)
    capability, value = extract_capability_and_value(feature_desc)
    user_story = build_user_story(persona, capability, value)
    ac = generate_acceptance_criteria(feature_desc, persona)
    assumptions = generate_assumptions(feature_desc)
    deps = generate_dependencies(feature_desc)
    metrics = generate_success_metrics(feature_desc)
    return StoryArtifact(
        feature_description=feature_desc,
        persona=persona,
        capability=capability,
        value=value,
        user_story=user_story,
        acceptance_criteria=ac,
        assumptions=assumptions,
        dependencies=deps,
        success_metrics=metrics,
    )


# ---------------------------
# Renderers
# ---------------------------

def render_markdown(artifact: StoryArtifact) -> str:
    lines = [
        f"# User Story",
        "",
        artifact.user_story,
        "",
        "## Acceptance Criteria (Gherkin)",
    ]
    for s in artifact.acceptance_criteria:
        lines.append("```gherkin")
        lines.append(s)
        lines.append("```")
        lines.append("")
    lines.append("## Assumptions")
    for a in artifact.assumptions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Dependencies")
    for d in artifact.dependencies:
        lines.append(f"- {d}")
    lines.append("")
    lines.append("## Success Metrics")
    for m in artifact.success_metrics:
        lines.append(f"- {m}")
    return "\n".join(lines)


def render_jira(artifact: StoryArtifact) -> str:
    lines = [
        f"Summary: {artifact.capability}",
        "",
        "Description:",
        artifact.user_story,
        "",
        "Acceptance Criteria:",
    ]
    for idx, s in enumerate(artifact.acceptance_criteria, start=1):
        first_line = s.splitlines()[0].replace("Scenario:", "").strip()
        lines.append(f"{idx}. {first_line}")
    lines.append("")
    lines.append("Assumptions:")
    for a in artifact.assumptions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("Dependencies:")
    for d in artifact.dependencies:
        lines.append(f"- {d}")
    lines.append("")
    lines.append("Success Metrics:")
    for m in artifact.success_metrics:
        lines.append(f"- {m}")
    return "\n".join(lines)


def render_azure_devops(artifact: StoryArtifact) -> str:
    lines = [
        f"Title: {artifact.capability}",
        "",
        "Description:",
        artifact.user_story,
        "",
        "Acceptance Criteria (Gherkin):",
    ]
    for s in artifact.acceptance_criteria:
        lines.append("")
        lines.append(s)
    lines.append("")
    lines.append("Assumptions:")
    for a in artifact.assumptions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("Dependencies:")
    for d in artifact.dependencies:
        lines.append(f"- {d}")
    lines.append("")
    lines.append("Success Metrics:")
    for m in artifact.success_metrics:
        lines.append(f"- {m}")
    return "\n".join(lines)


def render_copado(artifact: StoryArtifact) -> str:
    lines = [
        f"User Story Name: {artifact.capability}",
        "",
        "User Story:",
        artifact.user_story,
        "",
        "Acceptance Criteria:",
    ]
    for s in artifact.acceptance_criteria:
        lines.append("")
        lines.append(s)
    lines.append("")
    lines.append("Assumptions:")
    for a in artifact.assumptions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("Dependencies:")
    for d in artifact.dependencies:
        lines.append(f"- {d}")
    lines.append("")
    lines.append("Success Metrics:")
    for m in artifact.success_metrics:
        lines.append(f"- {m}")
    return "\n".join(lines)


# ---------------------------
# Streamlit UI
# ---------------------------

def main():
    st.set_page_config(page_title="Universal User Story Generator", layout="wide")

    st.title("Universal User Story Generator")
    st.caption("Describe your feature in plain English → get User Story, Gherkin AC, assumptions, dependencies, and metrics.")

    col_input, col_options = st.columns([2, 1])

    with col_input:
        feature_desc = st.text_area(
            "Describe the feature or change you need:",
            placeholder="Example: I need a login screen for banking customers with MFA so that they can securely access their accounts.",
            height=180,
        )

    with col_options:
        st.subheader("Output Options")
        formats = st.multiselect(
            "Target formats",
            options=["Markdown", "Jira", "Azure DevOps", "Copado"],
            default=["Markdown", "Jira", "Azure DevOps", "Copado"],
        )
        generate_button = st.button("Generate Story")

    if generate_button:
        if not feature_desc.strip():
            st.warning("Please enter a feature description first.")
            return

        artifact = build_artifact(feature_desc)

        st.markdown("---")
        st.subheader("Generated User Story (core)")
        st.markdown(f"**Persona:** {artifact.persona}")
        st.markdown(f"**User Story:** {artifact.user_story}")

        st.subheader("Acceptance Criteria (Gherkin)")
        for s in artifact.acceptance_criteria:
            st.code(s, language="gherkin")

        st.subheader("Assumptions")
        for a in artifact.assumptions:
            st.markdown(f"- {a}")

        st.subheader("Dependencies")
        for d in artifact.dependencies:
            st.markdown(f"- {d}")

        st.subheader("Success Metrics")
        for m in artifact.success_metrics:
            st.markdown(f"- {m}")

        st.markdown("---")
        st.subheader("Platform-Specific Views")

        if "Markdown" in formats:
            with st.expander("Markdown"):
                md = render_markdown(artifact)
                st.code(md, language="markdown")

        if "Jira" in formats:
            with st.expander("Jira"):
                jira = render_jira(artifact)
                st.code(jira, language="text")

        if "Azure DevOps" in formats:
            with st.expander("Azure DevOps"):
                ado = render_azure_devops(artifact)
                st.code(ado, language="text")

        if "Copado" in formats:
            with st.expander("Copado"):
                copado = render_copado(artifact)
                st.code(copado, language="text")


if __name__ == "__main__":
    main()