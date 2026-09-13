---
name: 'archive_helpers'
description: 'Functions for archiving research files when routing to Phase 0 or Phase 2A'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - archive_for_phase0_routing
  - archive_for_phase2a_routing

# Called By
called_by:
  - 'phase2a-dialogue/steps/step-00-initialize.md'
  - 'phase4-coding/steps/step-08-completion.md'
  - 'phase5-baseline-repo-comparison/steps/step-10b-finalize.md'
---

# Archive Helpers

> Functions for archiving research files when routing to Phase 0 or Phase 2A.
> Ensures clean state for new research attempts while preserving historical records.
> Called by: Phase 4 step-08-completion.md, Phase 5 step-10b-finalize.md

---

## Overview

When routing occurs (Phase 0 or Phase 2A), existing research files must be **explicitly archived** before starting fresh.
This is different from "natural file separation" - even though Phase 0 creates a new dated folder, the previous
attempt's files should be moved to an `_archive/` subfolder with clear failure context.

| Routing Target | Archive Scope | Preserved Files |
|----------------|---------------|-----------------|
| Phase 0 | **Entire research folder** | None (all archived) |
| Phase 2A | **Phase 2A+ results only** | 00_brainstorm_session.md, 01_targeted_research*.md |

---

## Constants

```python
# Files to archive for Phase 0 routing (entire folder)
PHASE0_ARCHIVE_PATTERNS = [
    "00_brainstorm_session.md",
    "01_targeted_research*.md",
    "01_round_table/",
    "02_hypothesis*.md",
    "02_extended*.md",
    "02b_verification_plan*.md",
    "02c_experiment_brief*.md",
    "03_*.md",
    "verification_state.yaml",
    "hypotheses/",
    "baseline_comparison/",
    "papers/",
    "phase2a_step_tasks.yaml",
    "stage1_context_*.yaml",
    "paper_config.yaml",
    "prior_failure_context.yaml"
]

# Files to archive for Phase 2A routing (keep Phase 0/1 results)
PHASE2A_ARCHIVE_PATTERNS = [
    "01_round_table/",
    "02_hypothesis*.md",
    "02_synthesis.yaml",
    "02_extended*.md",
    "02b_verification_plan*.md",
    "02c_experiment_brief*.md",
    "discussion_log.md",
    "03_refinement.yaml",
    "03_*.md",
    "verification_state.yaml",
    "h-*/",
    "hypotheses/",
    "baseline_comparison/",
    "phase2a_step_tasks.yaml",
    "stage1_context_*.yaml",
    "paper_config.yaml",
]

# Files to PRESERVE for Phase 2A routing
PHASE2A_PRESERVE_PATTERNS = [
    "00_brainstorm_session.md",
    "01_targeted_research*.md",
    "papers/" # Downloaded papers are reusable
]
```

---

## archive_for_phase0_routing(research_folder, timestamp, failure_reason)

Archive **entire** research folder when routing to Phase 0 (fundamental failure).

**Called by:** Phase 4 step-08-completion.md (MUST_WORK FAIL), Phase 5 step-10b-finalize.md (DETERMINES_SUCCESS PARTIAL)

```python
def archive_for_phase0_routing(research_folder, timestamp, failure_reason):
    """
    Archive entire research folder when routing to Phase 0.

    This is called when:
    - Phase 4 MUST_WORK gate FAIL → Phase 0 (fundamental flaw)
    - Phase 5 DETERMINES_SUCCESS gate PARTIAL → Phase 0 (approach failed)

    Creates: {research_folder}/_archive/

    Args:
        research_folder: Path to research folder (e.g., ".../youra_research/")
        timestamp: Timestamp string (e.g., "20260108_103542") - used in marker file only
        failure_reason: Descriptive reason for failure

    Returns:
        dict: Summary of actions taken
              {
                  "success": True,
                  "archive_folder": "_archive/",
                  "archived_count": 15,
                  "archived_files": ["00_brainstorm_session.md", ...],
                  "marker_file": "_ARCHIVED.md"
              }
    """
    import os
    import shutil
    from pathlib import Path
    from glob import glob

    research_path = Path(research_folder)
    archive_folder = research_path / "_archive"

    # Create archive folder
    archive_folder.mkdir(parents=True, exist_ok=True)

    archived_files = []
    archived_count = 0

    # Archive all files matching patterns
    for pattern in PHASE0_ARCHIVE_PATTERNS:
        # Handle both files and directories
        matches = list(research_path.glob(pattern))

        for item in matches:
            if item.exists():
                dest = archive_folder / item.name

                if item.is_dir():
                    # Move directory
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.move(str(item), str(dest))
                else:
                    # Move file
                    shutil.move(str(item), str(dest))

                archived_files.append(item.name)
                archived_count += 1

    # Create marker file with failure context
    marker_content = f"""# Archived Research Attempt

**Archive Date:** {timestamp}
**Archive Type:** PHASE_0_ROUTING (Complete Archive)
**Failure Reason:** {failure_reason}

---

## Contents

This folder contains a complete snapshot of a failed research attempt.
All files from the original research folder have been archived here.

### Archived Files:
{chr(10).join(f"- {f}" for f in archived_files)}

---

## Why Archived?

This research attempt was terminated and routed back to Phase 0 for a fresh start.
The failure context has been saved to Serena Memory for learning purposes.

**Memory Reference:** failure_*.md or phase5_failure_*.md

---

*Archived by archive_helpers.archive_for_phase0_routing()*
"""

    marker_path = archive_folder / "_ARCHIVED.md"
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(marker_content)

    return {
        "success": True,
        "archive_folder": str(archive_folder.relative_to(research_path)),
        "archived_count": archived_count,
        "archived_files": archived_files,
        "marker_file": "_ARCHIVED.md"
    }
```

---

## archive_for_phase2a_routing(research_folder, timestamp, supersede_reason)

Archive Phase 2A+ results when routing to `/phase2a-dialogue` (keep Phase 0/1 outputs).

**Called by:** Phase 4 step-08-completion.md (PARTIAL → SUPERSEDED)

```python
def archive_for_phase2a_routing(research_folder, timestamp, supersede_reason):
    """
    Archive Phase 2A+ results when routing to /phase2a-dialogue workflow.

    This is called when:
    - Phase 4 MUST_WORK gate PARTIAL + LLM self-assessment = SUPERSEDED

    Phase 0/1 outputs are PRESERVED because:
    - Research question and targeted research are still valid
    - Only the hypothesis generation needs to be redone (via /phase2a-dialogue)

    Creates: {research_folder}/_archive/

    Args:
        research_folder: Path to research folder (e.g., ".../youra_research/")
        timestamp: Timestamp string (e.g., "20260108_103542") - used in marker file only
        supersede_reason: Descriptive reason for supersede

    Returns:
        dict: Summary of actions taken
              {
                  "success": True,
                  "archive_folder": "_archive/",
                  "archived_count": 10,
                  "archived_files": ["01_round_table/", ...],
                  "preserved_files": ["00_brainstorm_session.md", ...],
                  "marker_file": "_ARCHIVED.md"
              }
    """
    import os
    import shutil
    from pathlib import Path
    from glob import glob

    research_path = Path(research_folder)
    archive_folder = research_path / "_archive"

    # Create archive folder
    archive_folder.mkdir(parents=True, exist_ok=True)

    archived_files = []
    preserved_files = []
    archived_count = 0

    # Archive Phase 2A+ files (NOT Phase 0/1)
    for pattern in PHASE2A_ARCHIVE_PATTERNS:
        matches = list(research_path.glob(pattern))

        for item in matches:
            if item.exists():
                dest = archive_folder / item.name

                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.move(str(item), str(dest))
                else:
                    shutil.move(str(item), str(dest))

                archived_files.append(item.name)
                archived_count += 1

    # Record preserved files (for documentation)
    for pattern in PHASE2A_PRESERVE_PATTERNS:
        matches = list(research_path.glob(pattern))
        for item in matches:
            if item.exists():
                preserved_files.append(item.name)

    # Create marker file with supersede context
    marker_content = f"""# Archived Research Attempt (Superseded)

**Archive Date:** {timestamp}
**Archive Type:** PHASE_2A_ROUTING (Partial Archive - Phase 0/1 Preserved)
**Supersede Reason:** {supersede_reason}

---

## Contents

This folder contains Phase 2A+ results from a superseded hypothesis.
Phase 0 (brainstorm) and Phase 1 (targeted research) outputs are preserved in the parent folder.

### Archived Files (Phase 2A+):
{chr(10).join(f"- {f}" for f in archived_files)}

### Preserved Files (Phase 0/1):
{chr(10).join(f"- {f}" for f in preserved_files)}

---

## Why Archived?

The hypothesis generated in Phase 2A was found to be incompatible with dependent hypotheses.
A new hypothesis will be generated in Phase 2A using the same Phase 0/1 foundation.

**Memory Reference:** superseded_*.md or pivot_*.md

---

*Archived by archive_helpers.archive_for_phase2a_routing()*
"""

    marker_path = archive_folder / "_ARCHIVED.md"
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(marker_content)

    return {
        "success": True,
        "archive_folder": str(archive_folder.relative_to(research_path)),
        "archived_count": archived_count,
        "archived_files": archived_files,
        "preserved_files": preserved_files,
        "marker_file": "_ARCHIVED.md"
    }
```

---

## Archive Folder Structure

After archiving, the structure will look like:

```
youra_research/
├── _archive/
│ ├── _ARCHIVED.md # Marker with failure/supersede context
│ ├── 00_brainstorm_session.md # (Phase 0 routing only)
│ ├── 01_targeted_research.md # (Phase 0 routing only)
│ ├── 01_round_table/ # Phase 2A-dialogue output
│ ├── 02_synthesis.yaml # Phase 2A-dialogue output
│ ├── discussion_log.md # Phase 2A discussion transcript
│ ├── 03_refinement.yaml # Phase 2A-dialogue output
│ ├── 02_hypothesis_generation.md # Phase 2A-dialogue output
│ ├── verification_state.yaml # Pipeline state
│ ├── hypotheses/ # h-m1/, h-m2/, etc.
│ └── ...
│
├── 00_brainstorm_session.md # Preserved (Phase 2A routing only)
├── 01_targeted_research.md # Preserved (Phase 2A routing only)
└── papers/ # Preserved (Phase 2A routing only)
```

---

