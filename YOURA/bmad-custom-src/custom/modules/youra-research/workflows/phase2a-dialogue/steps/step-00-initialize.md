---
name: 'step-00-initialize'
description: 'Initialize Phase 2A: Gap Selection and Paper Preparation'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue'
thisStepFile: '{workflow_path}/steps/step-00-initialize.md'
nextStepFile: '{workflow_path}/steps/step-01-discussion.md'
workflowFile: '{workflow_path}/workflow.md'

# Helper References
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Template References
templates:
  step_tasks: '{workflow_path}/templates/phase2a_step_tasks_template.yaml'
---

# Step 0: Initialize - Gap Selection & Paper Preparation

**Progress: Step 0 of 4** | Next: Step 1 - Round Table Discussion

---

## STEP GOAL

Initialize Phase 2A by selecting the highest priority research gap from Phase 1 output and preparing related papers for agent reading.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules
- 🛑 MUST read Phase 1 output to extract gaps
- 📖 MUST select gap based on priority criteria (HIGH > MEDIUM, PRIMARY > SECONDARY)
- 🔧 MUST run paper preparation if reference papers exist

---

## EXECUTION SEQUENCE

### 1. Load Configuration

```python
config = Read("{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml")
research_folder = config.research_output_path + "/youra_research/"
```

### 1.5 Failure Context Recovery (Serena Memory)

<critical>
Phase 2A may be invoked after Phase 4 PARTIAL + SUPERSEDE (ROUTE_TO_2A).
Check for ALL failure records to inform hypothesis redesign direction.
This section consumes **ALL** `.serena/memories/*.md` content injected by the Phase 2A launcher
as mandatory hard input to understand the complete failure history.
This follows the same pattern as Phase 0 Section 0.3.
</critical>

<helper-reference>
**Helper:** `{helpers_path}/phase2a_failure_context.md`
**Functions:**
- `parse_launcher_prompt_serena_memory_context()` → Read injected `.serena/memories/*.md` hard input
- `detect_recursive_entry(contexts)` → Determine version and feature name
</helper-reference>

```python
# Get Pipeline Project ID from Phase 0 output
phase0_file = f"{research_folder}/00_brainstorm_session.md"
IF NOT exists(phase0_file):
    STOP("Phase 0 output not found: 00_brainstorm_session.md. Run Phase 0 first.")

phase0_content = Read(phase0_file)
pipeline_project_title = extract_frontmatter(phase0_content, "pipeline_project_title")

pipeline_project = mcp__archon__find_projects(query=pipeline_project_title)
pipeline_project_id = pipeline_project["projects"][0]["id"]

# Load failure contexts from the mandatory launcher prompt block.
# The launcher injects every .serena/memories/*.md file under
# <serena_memory_context>...</serena_memory_context>.
from helpers.phase2a_failure_context import (
    parse_launcher_prompt_serena_memory_context,
    detect_recursive_entry,
)

previous_failure_contexts = parse_launcher_prompt_serena_memory_context()

# Determine recursive entry status
entry_info = detect_recursive_entry(previous_failure_contexts)
is_recursive = entry_info["is_recursive"]
version = entry_info["version"]
feature = entry_info["feature"]
```

<action>**Store Failure Context for Later Steps:**

If any memory files are found:
- Remember all content as `previous_failure_contexts`
- Include a concise `Previous Failure / Routing Context` section in `discussion_log.md`
- Note types of failures (Phase 4 FAIL, Phase 4 SUPERSEDE, Phase 5 PARTIAL, limitations, etc.)
- This information will be used in Step 1 (Round Table Discussion) to:
  - Guide hypothesis redesign away from approaches that failed before
  - Preserve what showed promise from partial results
  - Ensure new hypothesis addresses root causes from failure records
</action>

### 1.7 Archive Previous Artifacts

<critical>
When Phase 2A is entered recursively (ROUTED_TO_PHASE_2A from Phase 4), previous Phase 2A+
artifacts (02c, 03_*, h-*/, verification_state.yaml, etc.) must be archived BEFORE generating
new outputs. Phase 0 and Phase 1 results are preserved.

This step uses the existing `archive_for_phase2a_routing()` helper. Without this, old v1 files
remain and may be mistaken for current results by downstream verification checks.
</critical>

<helper-reference>
**Helper:** `{helpers_path}/archive_helpers.md`
**Function:** `archive_for_phase2a_routing(research_folder, timestamp, supersede_reason)`
</helper-reference>

```python
IF is_recursive:
    from helpers.archive_helpers import archive_for_phase2a_routing

    # Build supersede reason from failure contexts
    supersede_reasons = []
    for ctx in previous_failure_contexts:
        content = ctx["content"]
        # Extract hypothesis ID and failure type if available
        import re
        h_match = re.search(r"\*\*Hypothesis:\*\*\s*(\S+)", content)
        if h_match:
            supersede_reasons.append(h_match.group(1))

    supersede_reason = (
        f"ROUTED_TO_PHASE_2A: Recursive entry v{version}. "
        f"Previous hypotheses: {', '.join(supersede_reasons) if supersede_reasons else 'unknown'}. "
        f"Failure contexts: {len(previous_failure_contexts)} memory files."
    )

    timestamp = current_timestamp()
    archive_result = archive_for_phase2a_routing(
        research_folder=research_folder,
        timestamp=timestamp,
        supersede_reason=supersede_reason,
    )

    Log(f"Archived {archive_result['archived_count']} items to {archive_result['archive_folder']}")
    Log(f"Preserved: {archive_result['preserved_files']}")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Previous Artifacts Archived
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version: v{version} (recursive entry)
Archived: {archive_result['archived_count']} items → {archive_result['archive_folder']}
Preserved: {', '.join(archive_result['preserved_files'])}
Reason: {supersede_reason}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
ELSE:
    Log("First execution — no artifacts to archive")
```

### 1.6 Create Step-Level Archon Tasks

> **Purpose:** Create 5 step-level tasks in Archon for fine-grained progress tracking.
> This enables Claude to track which step is currently executing, and reduces step-skipping incidents.
>
> **Note:** This is for Phase 2A-Dialogue ONLY. Phase 2A-Extended does NOT use step-level tasks.

<helper-reference>
**Helper:** `{helpers_path}/phase2a_step_task_management.md`
**Functions:**
- `create_step_tasks(pipeline_project_id, feature)` → Create 5 Archon tasks, returns task IDs
- `render_step_tasks_yaml(template, context)` → Render template with {{placeholder}} substitution
**Helper:** `{helpers_path}/phase2a_failure_context.md`
**Function:** `extract_failure_source_info(contexts)` → Extract source phase/hypothesis/failure type for template
</helper-reference>

```python
from helpers.phase2a_step_task_management import create_step_tasks, render_step_tasks_yaml
from helpers.phase2a_failure_context import extract_failure_source_info

# Create 5 step tasks in Archon
task_result = create_step_tasks(pipeline_project_id, feature)
step_task_ids = task_result["step_task_ids"]

# Extract failure source info for template (or defaults for non-recursive)
IF is_recursive:
    source_info = extract_failure_source_info(previous_failure_contexts)
ELSE:
    source_info = {
        "source_phase": "null", "source_hypothesis": "null",
        "failure_type": "null", "serena_memory": "null"
    }

# Render step tasks YAML from template
step_tasks_template = Read("{templates.step_tasks}")
render_context = {
    "version": str(version),
    "feature": feature,
    "is_recursive": str(is_recursive).lower(),
    "pipeline_project_id": pipeline_project_id,
    "gap_id": selected_gap["id"] if 'selected_gap' in dir() else "pending",
    "timestamp": current_timestamp(),
    "task_id_2a_0": step_task_ids.get("2A-0", ""),
    "task_id_2a_p": step_task_ids.get("2A-P", ""),
    "task_id_2a_1": step_task_ids.get("2A-1", ""),
    "task_id_2a_2": step_task_ids.get("2A-2", ""),
    "task_id_2a_3": step_task_ids.get("2A-3", ""),
    **source_info,
}
step_tasks_content = render_step_tasks_yaml(step_tasks_template, render_context)

# Save to research folder
step_tasks_file = f"{research_folder}/phase2a_step_tasks.yaml"
Write(step_tasks_file, step_tasks_content)
Log(f"Step tasks saved to: {step_tasks_file}")

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Step-Level Archon Tasks Created
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature: {feature}
Version: {version}
Recursive: {is_recursive}

Tasks:
• 2A-0: Gap Selection [doing] ← CURRENT
• 2A-P: Paper Preparation [todo]
• 2A-1: Round Table [todo]
• 2A-2: Synthesis [todo]
• 2A-3: Refinement [todo]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
```

### 2. Read Phase 1 Output

```python
phase1_file = research_folder + "01_targeted_research.md"
phase1_content = Read(phase1_file)

IF phase1_file NOT exists:
    STOP("Phase 1 output not found. Run /phase1-targeted first.")
```

### 3. Parse Research Gaps and Select

<helper-reference>
**Helper:** `{helpers_path}/gap_parsing.md`
**Functions:**
- `parse_research_gaps(phase1_content)` → List of gaps with papers, repos, queries
- `select_highest_priority_primary(gaps)` → Selected gap
</helper-reference>

```python
from helpers.gap_parsing import parse_research_gaps, select_highest_priority_primary

gaps = parse_research_gaps(phase1_content)
selected_gap = select_highest_priority_primary(gaps)

Log(f"Selected Gap: {selected_gap['title']}")
Log(f"Priority: {selected_gap['priority']} | Relevance: {selected_gap['relevance']}")
```

### 4. Prepare Papers via Script

> **Purpose:** Download reference papers from arXiv/Semantic Scholar and convert to Markdown using MarkItDown.
> **Detailed Guide:** `{workflow_path}/docs/paper-preparation-guide.md`

#### 4.1 Create Paper Config from Selected Gap

```python
IF NOT selected_gap["related_papers"]:
    Log("No reference papers to prepare, skipping paper preparation")
    GOTO Step 5

paper_config = {"papers": []}

FOR paper IN selected_gap["related_papers"]:
    # PRIORITY: Use arxiv_id for direct arXiv download
    IF paper.get("arxiv_id"):
        paper_config["papers"].append({
            "id": paper["arxiv_id"],
            "source": "arxiv",
            "title": paper.get("title", "Unknown"),
            "semantic_scholar_id": paper.get("paper_id")
        })
    ELSE:
        paper_config["papers"].append({
            "id": paper.get("paper_id"),
            "source": "semantic_scholar",
            "title": paper.get("title", "Unknown")
        })
        Log(f"WARNING: No arXiv ID for {paper.get('title')} - using Semantic Scholar (may fail)")

config_path = f"{research_folder}/paper_config.yaml"
Write(config_path, yaml.dump(paper_config))
Log(f"Paper config created: {len(paper_config['papers'])} papers")
```

#### 4.2 Run Paper Preparation Script (YouRA Conda Environment)

> ⚠️ **CRITICAL:** Must run in YouRA conda environment where `markitdown` is installed!

```python
script_path = "{workflow_path}/scripts/prepare_papers.py"
papers_output_dir = f"{research_folder}/papers"

# MUST use YouRA conda environment with proper activation sequence
# Note: `conda activate` alone will FAIL without `source conda.sh` first!
Bash(f"""
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniforge3")
source "${{CONDA_BASE}}/etc/profile.d/conda.sh"
conda activate YouRA && python {script_path} --config {config_path} --output {papers_output_dir}
""")
```

#### 4.3 Validate Paper Preparation Results

```python
summary_path = Path(f"{papers_output_dir}/preparation_summary.json")

IF summary_path.exists():
    summary = json.load(Read(summary_path))
    success_count = summary.get("success", 0)
    total_count = summary.get("total", 0)

    Log(f"Paper Preparation: {success_count}/{total_count} papers converted successfully")

    IF success_count == 0:
        Log("WARNING: No papers successfully prepared. Continuing without paper context.")
ELSE:
    Log("WARNING: preparation_summary.json not found. Paper preparation may have failed.")
```

### 4.4 Generate Paper Summaries

> **Purpose:** Generate LLM-powered section summaries for each paper.
> Summaries are used by the orchestrator (`orchestrate_exchange.py`) to provide content-aware
> paper reference instructions during discussion, instead of blind filename-only suggestions.
> The summarizer uses `.claude/hooks/auto_responder_config.yaml` `openrouter.model`
> and `openrouter.api_key_env` (normally `OPENROUTER_API_KEY`).

```python
IF success_count > 0:
    summaries_dir = f"{research_folder}/paper_summaries"

    Bash(f"""
    CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniforge3")
    source "${{CONDA_BASE}}/etc/profile.d/conda.sh"
    conda activate YouRA && python {script_path} \
        --summarize \
        --papers-dir {papers_output_dir} \
        --summaries-dir {summaries_dir}
    """)

    # Validate summaries
    summary_files = glob(f"{summaries_dir}/*_summary.md")
    Log(f"Paper Summaries: {len(summary_files)} generated")

    IF len(summary_files) == 0:
        Log("WARNING: No paper summaries generated. Orchestrator will use filename-only reference.")
ELSE:
    Log("No papers to summarize (skipping)")
```

### 5. Initialize Round Table Folder

```python
round_table_folder = f"{research_folder}/01_round_table"
os.makedirs(round_table_folder, exist_ok=True)

metadata_template = Read("{workflow_path}/templates/round_table/00_metadata_template.yaml")
metadata_yaml = metadata_template.replace("{{gap_id}}", selected_gap["id"])
metadata_yaml = metadata_yaml.replace("{{gap_title}}", selected_gap["title"])
metadata_yaml = metadata_yaml.replace("{{timestamp}}", current_timestamp())

Write(f"{round_table_folder}/00_metadata.yaml", metadata_yaml)
```

### 5.5 Initialize Discussion Log

> **Purpose:** Create `discussion_log.md` with briefing context for the Self-Contained Loop
> discussion in Step 1. The orchestrator script (`orchestrate_exchange.py`) reads this file
> to analyze discussion state and detect convergence.
>
> **Note:** `discussion_log.md` is required by `step-01-discussion.md` for the Tikitaka discussion loop.

<helper-reference>
**Helper:** `{helpers_path}/phase2a_discussion_init.md`
**Function:** `create_discussion_log(research_folder, selected_gap, papers_dir, previous_failure_contexts)` → Creates discussion_log.md
</helper-reference>

```python
from helpers.phase2a_discussion_init import create_discussion_log

init_result = create_discussion_log(
    research_folder=research_folder,
    selected_gap=selected_gap,
    papers_dir=f"{research_folder}/papers",
    previous_failure_contexts=previous_failure_contexts
)
Log(f"Discussion log initialized: {init_result['discussion_log_path']} ({init_result['papers_count']} papers listed)")
```

### 6. Prepare Stage 1 Context

```python
stage1_context = {
    "gap_id": selected_gap["id"],
    "gap_title": selected_gap["title"],
    "gap_description": selected_gap["description"],
    "papers_folder": f"{research_folder}/papers/",
    "github_repos": selected_gap["github_repos"],
    "archon_queries": selected_gap["archon_queries"],
    "exa_search_terms": selected_gap["exa_search_terms"],
    "round_table_folder": round_table_folder,
}

Write(f"{research_folder}/stage1_context_{selected_gap['id']}.yaml", yaml.dump(stage1_context))
```

### 6.5 Update Step Task with Gap ID

<helper-reference>
**Helper:** `{helpers_path}/phase2a_step_task_management.md`
**Function:** `update_step_tasks_gap_id(step_tasks_file, gap_id)`
</helper-reference>

```python
from helpers.phase2a_step_task_management import update_step_tasks_gap_id

update_step_tasks_gap_id(step_tasks_file, selected_gap["id"])
```

### 7. Complete Step 0 and Transition Tasks

<helper-reference>
**Helper:** `{helpers_path}/phase2a_step_task_management.md`
**Function:** `transition_step_tasks(step_tasks_file, transitions_spec, step_name, message)`
</helper-reference>

```python
from helpers.phase2a_step_task_management import transition_step_tasks

transition_step_tasks(
    step_tasks_file=step_tasks_file,
    transitions_spec=[
        {"task_key": "2A-0", "new_status": "done"},
        {"task_key": "2A-P", "new_status": "doing"},
    ],
    step_name="step-00-initialize",
    message="Gap selection complete, starting paper preparation"
)

print("""
✅ Step 0 Complete
━━━━━━━━━━━━━━━━━
• 2A-0: Gap Selection [done] ✓
• 2A-P: Paper Preparation [doing] ← CURRENT
• 2A-1: Tikitaka Discussion [todo] (Self-Contained Loop)
• 2A-2: Result Structuring [todo]
━━━━━━━━━━━━━━━━━
Discussion Files:
• discussion_log.md [initialized] ✓
━━━━━━━━━━━━━━━━━
→ Proceeding to Step 1 (Self-Contained Tikitaka Loop)
""")

Log("Phase 2A Initialization Complete")
# Proceed to Step 1 (Self-Contained Tikitaka Loop)
Read("{nextStepFile}")
```

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Phase 1 output read successfully
- Research gap selected with clear justification
- Round Table folder initialized with `00_metadata.yaml`
- Papers prepared (if references exist)
- Stage 1 context ready

### ❌ FAILURE
- Phase 1 output not found
- No research gaps in Phase 1 output
- Round Table folder not initialized
- Skipping to Stage 1 without proper initialization
