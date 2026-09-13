# Task Generation Code Examples

> **Reference File:** This file contains code examples for step-09-generate-tasks.md
>
> **Purpose:** Extracted to reduce step file size for optimal LLM performance

---

## Initialize Task Generation Context

```python
# Get hypothesis context from workflow state
hypothesis_id = workflow_state["hypothesis_id"] # e.g., "h-e1"
hypothesis_id_upper = hypothesis_id.upper() # e.g., "H-E1"
hypothesis_folder = workflow_state["hypothesis_folder"]
tier = workflow_state.get("tier", "LIGHT") # LIGHT (15 tasks) or FULL (30 tasks)

# Set budget based on tier
if tier == "FULL":
    total_budget = 30
else:
    total_budget = 15

print(f"✓ Task Generation Context:")
print(f" Hypothesis: {hypothesis_id_upper}")
print(f" Tier: {tier} (max {total_budget} tasks)")
print(f" Output: {hypothesis_folder}/03_tasks.yaml")
```

---

## Parse 03_prd.md - Data Tasks

```python
# Pattern to identify manual download datasets
manual_download_indicators = [
    "twitter-research/tgn",
    "yule-BUAA/DyGLib",
    "shenyangHuang/TGB",
    # Any GitHub repository source (not PyG built-in)
]

data_prep_tasks = []

# For each manual download dataset:
data_prep_tasks.append({
    "id": f"task-{len(data_prep_tasks)+1:03d}",
    "epic": "Data Preparation",
    "title": f"Download {dataset_name} dataset",
    "description": f"Download from: {source_repository}\nPlace in: ./data/{dataset_name.lower()}/",
    "feature_tag": "data-preparation",
    "priority": 100 - len(data_prep_tasks),
    "source_document": "03_prd.md",
    "complexity": None,
    "test_requirements": "Data download tasks do not require tests."
})
```

---

## Parse 03_prd.md - Environment Setup

```python
# Create single environment setup task
env_task = {
    "id": f"task-{len(data_prep_tasks)+1:03d}",
    "epic": "Environment Setup",
    "title": "Setup development environment",
    "description": f"""Install required packages:
{packages_list}

External repositories for reference:
{repo_list}
""",
    "feature_tag": "setup",
    "priority": 100 - len(data_prep_tasks) - 1,
    "source_document": "03_prd.md",
    "complexity": None,
    "test_requirements": "Environment setup does not require tests."
}
```

---

## Parse 03_architecture.md - Epic Tasks

```python
# Map architecture modules to feature tags
module_to_feature = {
    "data": "data-pipeline",
    "models": "model",
    "training": "training",
    "evaluation": "evaluation",
    "experiment": "experiment"
}

epic_tasks = []
for epic in parsed_epics:
    epic_anchor = f"#Epic-{epic['id']}"
    epic_tasks.append({
        "id": f"task-{current_id:03d}",
        "epic": epic["name"],
        "title": epic["title"],
        "description": epic["description"],
        "feature_tag": module_to_feature.get(epic["module"], "implementation"),
        "priority": 0,
        "source_document": "03_architecture.md",
        "complexity": epic.get("complexity"),
        "test_requirements": """
## Test Requirements (MANDATORY)
- Create `tests/test_{module}.py` for this task
- Minimum 3 test methods with REAL assertions
- NO placeholder tests (pass, ..., assert True)
- Tests must be runnable with `pytest`
- Tests must validate task requirements, not just file coverage
""",
        "reference_files": {
            "architecture": f"03_architecture.md{epic_anchor}",
            "logic": None,
            "config": None
        }
    })
```

---

## Link reference_files to Epic Tasks

```python
logic_sections = {} # e.g., {"E1": "03_logic.md#PMLP_API"}
config_sections = {} # e.g., {"E1": "03_config.md#model_config"}

for section in parsed_logic_sections:
    if section["epic_id"]:
        logic_sections[section["epic_id"]] = f"03_logic.md#{section['anchor']}"

for section in parsed_config_sections:
    if section["epic_id"]:
        config_sections[section["epic_id"]] = f"03_config.md#{section['anchor']}"

for task in epic_tasks:
    epic_id = task["epic"].split("-")[-1] if "-" in task["epic"] else task["epic"]
    if epic_id in logic_sections:
        task["reference_files"]["logic"] = logic_sections[epic_id]
    if epic_id in config_sections:
        task["reference_files"]["config"] = config_sections[epic_id]

print(f"✓ Linked reference_files for {len(epic_tasks)} Epic tasks")
```

---

## Apply Exclusion List (Budget Rebalancing)

```python
excluded_ids = []
if excluded_subtasks and len(excluded_subtasks) > 0:
    excluded_ids = [s["id"] for s in excluded_subtasks]
    logic_subtasks = [s for s in logic_subtasks if s["id"] not in excluded_ids]
    config_subtasks = [s for s in config_subtasks if s["id"] not in excluded_ids]
    print(f"⚠️ Budget Rebalancing Applied: {len(excluded_ids)} subtasks excluded")
    for excl in excluded_subtasks:
        print(f" - {excl['id']}: {excl['reason']}")
```

---

## Consolidate and Prioritize Tasks

```python
all_tasks = []
current_id = 1

# Priority order: data prep (100-95) → env setup (94) → epic (93-50) → subtasks (49-2) → failsafe (1)

for i, task in enumerate(data_prep_tasks):
    task["id"] = f"task-{current_id:03d}"
    task["priority"] = 100 - i
    all_tasks.append(task)
    current_id += 1

env_task["id"] = f"task-{current_id:03d}"
env_task["priority"] = 100 - len(data_prep_tasks)
all_tasks.append(env_task)
current_id += 1

base_priority = 100 - len(data_prep_tasks) - 1
for i, epic in enumerate(epic_tasks):
    epic["id"] = f"task-{current_id:03d}"
    epic["priority"] = base_priority - i
    all_tasks.append(epic)
    current_id += 1

subtask_priority = base_priority - len(epic_tasks)
for i, subtask in enumerate(logic_subtasks):
    subtask["id"] = f"task-{current_id:03d}"
    subtask["priority"] = subtask_priority - i
    all_tasks.append(subtask)
    current_id += 1

# Failsafe task (always last)
failsafe_task = {
    "id": f"task-{current_id:03d}",
    "epic": "Pipeline Management",
    "title": "Pipeline Continuation Checkpoint",
    "description": "/full-pipeline-unattended - FAILSAFE CONTINUATION TASK",
    "feature_tag": "pipeline-continue",
    "priority": 1,
    "source_document": "system",
    "complexity": None,
    "test_requirements": "Failsafe task does not require tests."
}
all_tasks.append(failsafe_task)
```

---

## Generate 03_tasks.yaml

```python
import yaml
from datetime import datetime

tasks_file_content = {
    "version": "1.1",
    "metadata": {
        "hypothesis_id": hypothesis_id.lower(),
        "hypothesis_id_upper": hypothesis_id_upper,
        "tier": tier,
        "total_budget": total_budget,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_documents": ["03_prd.md", "03_architecture.md", "03_logic.md", "03_config.md"],
        "budget_rebalancing": {
            "applied": len(excluded_ids) > 0,
            "excluded_count": len(excluded_ids),
            "excluded_ids": excluded_ids
        }
    },
    "tasks": all_tasks,
    "budget_summary": {
        "data_preparation": len(data_prep_tasks),
        "environment_setup": 1,
        "epic_tasks": len(epic_tasks),
        "subtasks": len(logic_subtasks) + len(config_subtasks),
        "failsafe": 1,
        "total": len(all_tasks)
    }
}

if len(all_tasks) > total_budget:
    print(f"⚠️ WARNING: Task count ({len(all_tasks)}) exceeds budget ({total_budget})")

tasks_output_path = f"{hypothesis_folder}/03_tasks.yaml"
with open(tasks_output_path, 'w') as f:
    yaml.dump(tasks_file_content, f, default_flow_style=False, sort_keys=False)
```

---

## Verify Task File

```python
with open(tasks_output_path, 'r') as f:
    verification = yaml.safe_load(f)

tasks = verification.get("tasks", [])
print(f"✓ Verification passed:")
print(f" - Tasks in file: {len(tasks)}")
print(f" - Data preparation: {verification['budget_summary']['data_preparation']}")
print(f" - Epic tasks: {verification['budget_summary']['epic_tasks']}")
print(f" - Subtasks: {verification['budget_summary']['subtasks']}")
```

---

## Update verification_state.yaml

```yaml
sub_hypotheses:
  {{hypothesis_id}}:
    implementation_planning:
      status: "COMPLETED"
      tier: {{tier}}
      budget: {{total_budget}}
      tasks_file: "03_tasks.yaml"
      task_count: {{len(all_tasks)}}
      task_breakdown:
        data_preparation: {{data_prep_count}}
        environment_setup: 1
        epic_tasks: {{epic_count}}
        subtasks: {{subtask_count}}
        failsafe: 1
      files:
        - "03_prd.md"
        - "03_architecture.md"
        - "03_logic.md"
        - "03_config.md"
        - "03_tasks.yaml"
```
