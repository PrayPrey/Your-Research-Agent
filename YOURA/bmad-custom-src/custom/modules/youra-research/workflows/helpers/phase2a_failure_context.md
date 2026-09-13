---
name: 'phase2a_failure_context'
description: 'Functions for reading Serena Memory files and detecting recursive Phase 2A entry from failure history'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - parse_launcher_prompt_serena_memory_context
  - load_failure_contexts
  - detect_recursive_entry
  - extract_failure_source_info

# Called By
called_by:
  - 'phase2a-dialogue/steps/step-00-initialize.md'
---

# Phase 2A Failure Context Helper Functions

> Functions for reading Serena Memory files and detecting recursive Phase 2A entry.
> Phase 2A may be invoked after Phase 4 PARTIAL + SUPERSEDE (ROUTE_TO_2A).
> These functions read ALL memory files to understand the complete failure history
> and inform hypothesis redesign direction.
>
> **Pattern Reference:** Same memory reading pattern as Phase 0 Section 0.3.
> **Memory File Reference:** See `serena_memory_patterns.md` for file naming conventions and content formats.

---

## Constants

### FAILURE_DETECTION_PATTERNS

```python
# Priority-ordered patterns for detecting failure source from memory file content.
# Order matters: SUPERSEDED > PHASE5_PARTIAL > PHASE4_FAIL (most recent routing cause first)
FAILURE_DETECTION_PATTERNS = [
    {
        "type": "SUPERSEDED",
        "markers": ["Status:** SUPERSEDED", "Superseded Hypothesis Record"],
        "source_phase": "Phase 4",
        "failure_type": "SUPERSEDED",
    },
    {
        "type": "PHASE5_PARTIAL",
        "markers": ["Phase 5 Failure Record", 'phase="Phase 5"'],
        "source_phase": "Phase 5",
        "failure_type": "PARTIAL",
    },
    {
        "type": "PHASE4_FAIL",
        "markers": ["Failure Record"],
        "additional_marker": "Final Status:** PARTIAL/FAIL",
        "source_phase": "Phase 4",
        "failure_type": "FAIL",
    },
]

# Regex pattern for extracting hypothesis ID from memory file content
HYPOTHESIS_ID_PATTERN = r"\*\*Hypothesis:\*\*\s*(\S+)"
```

---

## Functions

### 1. parse_launcher_prompt_serena_memory_context

```python
def parse_launcher_prompt_serena_memory_context() -> list:
    """
    Parse the mandatory <serena_memory_context> block injected by run_phase2a.py.

    The Phase 2A launcher reads every .md file under .serena/memories and embeds
    the contents directly in the initial prompt. This function treats that prompt
    block as the primary hard input for recursive/rerouted Phase 2A execution.

    Returns:
        list[dict] - Each dict has {"file": str, "content": str}

    Usage:
        previous_failure_contexts = parse_launcher_prompt_serena_memory_context()
    """
    prompt_block = READ_CURRENT_PROMPT_SECTION(
        start_tag="<serena_memory_context>",
        end_tag="</serena_memory_context>",
    )

    contexts = []
    IF prompt_block:
        FOR section IN split_on_markdown_file_headings(prompt_block):
            # Sections are injected as:
            # ### .serena/memories/<memory>.md
            # <content>
            file_name = extract_heading_after_prefix(section, "### ")
            content = extract_body_after_heading(section)
            IF file_name AND content:
                contexts.append({"file": file_name, "content": content})

    return contexts
```

---

### 2. load_failure_contexts

```python
def load_failure_contexts() -> dict:
    """
    Read all Serena Memory .md files for failure context recovery.

    Calls mcp__serena__list_memories() and reads each .md file's content.
    Memory files are self-documenting with complete metadata.

    Args:
        (none - uses mcp__serena__list_memories() directly)

    Returns:
        Dictionary containing:
            - contexts: list[dict] - Each dict has {"file": str, "content": str}
            - count: int - Number of memory files loaded

    Usage:
        failure_result = load_failure_contexts()
        previous_failure_contexts = failure_result["contexts"]
        Log(f"Loaded {failure_result['count']} Serena Memory files for context")
    """
    memory_list = mcp__serena__list_memories()
    contexts = []

    IF memory_list AND len(memory_list) > 0:
        FOR memory_file IN memory_list:
            IF memory_file.endswith(".md"):
                content = mcp__serena__read_memory(memory_file_name=memory_file)
                contexts.append({
                    "file": memory_file,
                    "content": content
                })
        Log(f"Loaded {len(contexts)} Serena Memory files for context")
    ELSE:
        Log("No Serena Memory files found - first execution")

    return {
        "contexts": contexts,
        "count": len(contexts)
    }
```

### 3. detect_recursive_entry

```python
def detect_recursive_entry(failure_contexts: list) -> dict:
    """
    Determine if this is a recursive Phase 2A entry and compute version/feature.

    Examines memory file content for pivot records to determine how many
    hypothesis pivots have occurred, then computes the version number.

    Args:
        failure_contexts: list of dicts from load_failure_contexts()["contexts"]
            Each dict: {"file": str, "content": str}

    Returns:
        Dictionary containing:
            - is_recursive: bool - True if any failure contexts exist
            - version: int - 1 for first run, 2+ for recursive entries
            - feature: str - e.g., "Phase2A-v1", "Phase2A-v2"
            - pivot_count: int - Number of pivot records found

    Usage:
        entry_info = detect_recursive_entry(previous_failure_contexts)
        is_recursive = entry_info["is_recursive"]
        version = entry_info["version"]
        feature = entry_info["feature"]
    """
    is_recursive = len(failure_contexts) > 0
    version = 1
    pivot_count = 0

    IF is_recursive:
        # Count pivots from content (look for "Hypothesis Pivot Record" or "Pivot Reason" fields)
        pivot_count = sum(
            1 for ctx in failure_contexts
            if "Hypothesis Pivot Record" in ctx["content"] or "Pivot Reason" in ctx["content"]
        )
        version = pivot_count + 2 # v1 = original, v2+ = after pivots
        feature = f"Phase2A-v{version}"
        Log(f"Recursive entry detected: {feature} (from {len(failure_contexts)} memory files)")
    ELSE:
        feature = "Phase2A-v1"

    return {
        "is_recursive": is_recursive,
        "version": version,
        "feature": feature,
        "pivot_count": pivot_count,
    }
```

### 4. extract_failure_source_info

```python
def extract_failure_source_info(failure_contexts: list) -> dict:
    """
    Extract source phase, hypothesis, and failure type from memory file content.

    Uses priority-ordered FAILURE_DETECTION_PATTERNS to identify the most relevant
    failure source. Priority: SUPERSEDED > Phase 5 Failure > Phase 4 Failure.

    Used for template rendering in phase2a_step_tasks.yaml.

    Args:
        failure_contexts: list of dicts from load_failure_contexts()["contexts"]
            Each dict: {"file": str, "content": str}

    Returns:
        Dictionary containing:
            - source_phase: str - "Phase 4" | "Phase 5" | "Unknown"
            - source_hypothesis: str - e.g., "h-e1" | "Unknown"
            - failure_type: str - "SUPERSEDED" | "PARTIAL" | "FAIL" | "Unknown"
            - serena_memory: str - comma-separated list of memory file names

    Usage:
        source_info = extract_failure_source_info(previous_failure_contexts)
        # → {"source_phase": "Phase 4", "source_hypothesis": "h-e1",
        # "failure_type": "SUPERSEDED", "serena_memory": "superseded_h-e1.md"}

        # For non-recursive (no failure contexts):
        source_info = {"source_phase": "null", "source_hypothesis": "null",
                       "failure_type": "null", "serena_memory": "null"}
    """
    import re

    source_phase = "Unknown"
    source_hypothesis = "Unknown"
    failure_type = "Unknown"
    memory_files_list = ", ".join([ctx["file"] for ctx in failure_contexts])

    # Priority-ordered search through failure detection patterns
    FOR pattern IN FAILURE_DETECTION_PATTERNS:
        FOR ctx IN failure_contexts:
            content = ctx["content"]
            markers = pattern["markers"]

            # Check if ALL markers match (or ANY marker matches for multi-marker patterns)
            marker_found = any(marker in content for marker in markers)

            # Additional marker check (for PHASE4_FAIL which needs both)
            IF "additional_marker" in pattern:
                marker_found = marker_found AND (pattern["additional_marker"] in content)

            IF marker_found:
                source_phase = pattern["source_phase"]
                failure_type = pattern["failure_type"]

                # Extract hypothesis ID from content
                match = re.search(HYPOTHESIS_ID_PATTERN, content)
                IF match:
                    source_hypothesis = match.group(1)

                # Found highest-priority match, stop searching
                return {
                    "source_phase": source_phase,
                    "source_hypothesis": source_hypothesis,
                    "failure_type": failure_type,
                    "serena_memory": memory_files_list,
                }

    # No pattern matched (unusual - may indicate new memory file type)
    return {
        "source_phase": source_phase,
        "source_hypothesis": source_hypothesis,
        "failure_type": failure_type,
        "serena_memory": memory_files_list,
    }
```

---

## Cross-References

| Related Helper | Relationship |
|---------------|--------------|
| `serena_memory_patterns.md` | Defines memory file naming conventions and content formats used by this helper |
| `phase2a_step_task_management.md` | Consumes `extract_failure_source_info()` output for template rendering |
| `archon_pipeline_creation.md` | Defines pipeline-level tasks; this helper operates at step-level |
