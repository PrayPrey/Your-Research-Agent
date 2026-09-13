# Archon Task Synchronization Helpers - Index

> Unified Archon Project Management - Task synchronization across phases.
> Used by: Phase 0, 2A, 2B, 3, 4, 5, hypothesis-loop
>
> **Design Principle:** All hypothesis tasks are managed in a SINGLE Pipeline Project
> using the `feature` field to group tasks by hypothesis ID.

---

## ⚠️ IMPORTANT: This file is an INDEX only

**Do NOT read this entire file.** Instead, read only the specific helper file you need.

---

## Helper Files Overview

| File | Functions | Used By |
|------|-----------|---------|
| [`archon_pipeline_creation.md`](./archon_pipeline_creation.md) | `create_pipeline_phase_tasks` | Phase 0 |
| [`archon_hypothesis_tasks.md`](./archon_hypothesis_tasks.md) | `get_pipeline_project_id`, `create_hypothesis_tasks`, `update_hypothesis_task_status` | Phase 2B, Phase 4 |
| [`archon_cascade.md`](./archon_cascade.md) | `find_dependent_hypotheses`, `mark_hypothesis_superseded`, `update_verification_state_cascade` | Phase 4 step-06, step-06b |
| [`archon_phase_reset.md`](./archon_phase_reset.md) | `reset_phase_tasks` | Phase 0, Phase 4, Phase 5 |
| [`archon_hypothesis_phase.md`](./archon_hypothesis_phase.md) | `get_or_create_hypothesis_phase_tasks`, `update_hypothesis_phase_status`, `is_first_hypothesis` | hypothesis-loop |

---

## Quick Reference by Phase

### Phase 0 - Brainstorm
```python
from archon_pipeline_creation import create_pipeline_phase_tasks
from archon_phase_reset import reset_phase_tasks # For recursive entry
```

### Phase 2A-Dialogue - Hypothesis
```python
from phase2a_step_task_management import create_or_update_step_tasks
```

### Phase 2B - Planning
```python
from archon_hypothesis_tasks import create_hypothesis_tasks, get_pipeline_project_id
```

### Phase 3 - Implementation
```python
# Tasks generated inline in step-09-generate-tasks.md (03_tasks.yaml)
# No Archon helper needed - local file generation
```

### Phase 4 - Coding
```python
from archon_hypothesis_tasks import update_hypothesis_task_status
from archon_cascade import find_dependent_hypotheses, mark_hypothesis_superseded, update_verification_state_cascade
from archon_phase_reset import reset_phase_tasks
# Implementation tasks: read directly from 04_checkpoint.yaml
```

### Phase 5 - Baseline Comparison
```python
from archon_phase_reset import reset_phase_tasks
```

### Hypothesis Loop
```python
from archon_hypothesis_phase import is_first_hypothesis, get_or_create_hypothesis_phase_tasks, update_hypothesis_phase_status
```

---

## Architecture Overview

```
Pipeline Project (created in Phase 0)
├── Phase Tasks (11 tasks: Phase 0 ~ Phase 6.5)
│ └── feature: "Pipeline"
│
├── Step Tasks (Phase 2A: 5 tasks)
│ └── feature: "Phase2A-v1"
│
└── Hypothesis Tasks (created in Phase 2B)
    ├── [H-E1] Placeholder Task
    │ └── feature: "H-E1"
    ├── [H-M1] Placeholder Task
    │ └── feature: "H-M1"
    └── Implementation Tasks (created in Phase 3)
        └── feature: same as parent hypothesis
```

