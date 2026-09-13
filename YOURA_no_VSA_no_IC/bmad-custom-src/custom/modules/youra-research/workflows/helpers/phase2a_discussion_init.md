---
name: 'phase2a_discussion_init'
description: 'Functions for initializing discussion_log.md required by the Phase 2A Self-Contained Loop orchestrator'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - create_discussion_log

# Called By
called_by:
  - 'phase2a-dialogue/steps/step-00-initialize.md'
---

# Phase 2A Discussion Initialization Helper Functions

> Functions for creating `discussion_log.md` required by the Phase 2A
> Self-Contained Loop orchestrator (`orchestrate_exchange.py`).
>
> The orchestrator reads `discussion_log.md` to analyze discussion state,
> count exchanges, and detect convergence.

<critical>
ORCHESTRATOR COMPATIBILITY — DO NOT MODIFY THESE MARKERS:

The `discussion_log.md` MUST contain the exact string `## Discussion Briefing`
as a level-2 markdown header. This string is used by:

- `orchestrate_exchange.py` → exchange counting and context extraction
- `step-01-discussion.md` → Self-Contained Tikitaka Loop appends exchanges after this section

The completion marker `## Final Assessments` signals discussion end.
- `orchestrate_exchange.py` checks: `completion_marker in content`

Do NOT include the completion marker in the initial `discussion_log.md`.
</critical>

---

## Constants

```python
# Discussion markers — MUST match orchestrate_exchange.py and phase2a_config.yaml
DISCUSSION_BRIEFING_HEADER = "## Discussion Briefing"
COMPLETION_MARKER = "## Final Assessments"

# File names — MUST match phase2a_config.yaml detection section
DISCUSSION_LOG_NAME = "discussion_log.md"

# Version stamp for generated files
ARCHITECTURE_VERSION = "Self-Contained Tikitaka Loop"
```

---

## Functions

### 1. create_discussion_log

```python
def create_discussion_log(
    research_folder: str,
    selected_gap: dict,
    papers_dir: str = None,
    previous_failure_contexts: list = None
) -> dict:
    """
    Initialize discussion_log.md with briefing context for the Self-Contained Loop.

    Creates discussion_log.md with:
    - Metadata section (gap ID, title, timestamps, architecture version)
    - Discussion Briefing section with research gap description
    - Previous Failure / Routing Context section when Serena memories are present
    - Available papers list (scanned from papers_dir)
    - Research repos list (from selected_gap)

    Args:
        research_folder: Path to the research output folder
            e.g., "docs/youra_research/20260226_topic_name"
        selected_gap: Dictionary containing gap information. Required keys:
            - id: str - Gap identifier (e.g., "GAP-001")
            - title: str - Gap title
            - description: str - Gap description (used in briefing)
            Optional keys:
            - github_repos: list[str] - Related repository URLs
        papers_dir: Path to prepared papers directory (optional).
            If provided and exists, lists all *.md files in the briefing.
        previous_failure_contexts: List of prior failure/routing memory contexts.
            Each item should contain {"file": str, "content": str}. If provided,
            this context is written into discussion_log.md before Step 1 starts.

    Returns:
        Dictionary containing:
            - success: bool - True if file created
            - discussion_log_path: str - Path to created discussion_log.md
            - papers_count: int - Number of paper files listed in briefing

    Usage:
        init_result = create_discussion_log(
            research_folder=research_folder,
            selected_gap=selected_gap,
            papers_dir=f"{research_folder}/papers",
            previous_failure_contexts=previous_failure_contexts
        )
        Log(f"Discussion log initialized: {init_result['discussion_log_path']}")
    """
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. Build paper list for briefing
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    papers_list = ""
    papers_count = 0
    IF papers_dir:
        papers_path = Path(papers_dir)
        IF papers_path.exists():
            for paper_file in sorted(papers_path.glob("*.md")):
                papers_list += f"- `{paper_file.name}`\n"
                papers_count += 1

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. Build research repos list
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    github_repos = selected_gap.get('github_repos', [])
    repos_list = chr(10).join([f"- {repo}" for repo in github_repos]) if github_repos else "(None)"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. Build prior failure/routing context block
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    failure_context_block = "(No prior failure/routing context supplied.)"
    IF previous_failure_contexts:
        context_sections = []
        FOR ctx IN previous_failure_contexts:
            memory_file = ctx.get("file", "unknown-memory")
            memory_content = ctx.get("content", "").strip()
            IF memory_content:
                context_sections.append(f"#### {memory_file}\n\n{memory_content}")

        IF context_sections:
            failure_context_block = "\n\n".join(context_sections)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4. Initialize discussion_log.md with briefing context
    # CRITICAL: Must include "## Discussion Briefing" header for orchestrator
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    discussion_log_path = f"{research_folder}/{DISCUSSION_LOG_NAME}"

    discussion_log_content = f"""# Phase 2A: Research Discussion Log

## Metadata
- **Gap ID**: {selected_gap['id']}
- **Gap Title**: {selected_gap['title']}
- **Start Time**: {current_timestamp()}
- **Architecture**: {ARCHITECTURE_VERSION}
- **Execution Mode**: UNATTENDED

{DISCUSSION_BRIEFING_HEADER}

### Research Gap
{selected_gap['description']}

### Phase 1 Key Findings
(Refer to `01_targeted_research.md` for detailed findings)

### Previous Failure / Routing Context
This section is mandatory hard input for the Phase 2A discussion. If it contains
SUPERSEDED, ROUTED_TO_PHASE_2A, PARTIAL, FAIL, or pivot records, the discussion
must redesign away from the failed approach families and preserve validated
partial findings.

{failure_context_block}

### Available Papers
{papers_list if papers_list else "(No papers prepared)"}

### Research Repos
{repos_list}

---

"""

    Write(discussion_log_path, discussion_log_content)
    Log(f"Initialized {DISCUSSION_LOG_NAME} with briefing context")

    return {
        "success": True,
        "discussion_log_path": discussion_log_path,
        "papers_count": papers_count,
    }
```

---

## Integration Reference

```
┌─────────────────────────────────────────────────────────────────┐
│ create_discussion_log() │
│ (Called by step-00-initialize.md Section 5.5) │
│ │
│ Creates: │
│ └── discussion_log.md │
│ ├── ## Metadata │
│ ├── ## Discussion Briefing ← ORCHESTRATOR MARKER │
│ │     ├── ### Research Gap │
│ │     ├── ### Phase 1 Key Findings │
│ │     ├── ### Available Papers │
│ │     └── ### Research Repos │
│ └── (exchanges appended by step-01-discussion.md loop) │
│ │
│ Orchestrator Detection Flow: │
│ orchestrate_exchange.py: │
│ ├── discussion_log.md exists? → YES │
│ ├── Count "### Exchange" headers → N exchanges │
│ └── "## Final Assessments" found? → NO (not yet) │
│ ∴ Discussion in progress → select personas + check converge │
└─────────────────────────────────────────────────────────────────┘
```

## Cross-References

| Related File | Relationship |
|-------------|--------------|
| `phase2a-dialogue/scripts/orchestrate_exchange.py` | Reads discussion_log.md for state analysis and convergence detection |
| `phase2a-dialogue/scripts/phase2a_config.yaml` | Defines `detection.discussion_log`, `detection.completion_marker` |
| `phase2a-dialogue/steps/step-01-discussion.md` | Appends Exchange content to `discussion_log.md` in Tikitaka loop |
