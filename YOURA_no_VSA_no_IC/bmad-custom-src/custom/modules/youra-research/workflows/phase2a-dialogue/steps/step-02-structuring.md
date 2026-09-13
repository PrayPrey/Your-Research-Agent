---
name: 'step-02-structuring'
description: 'Phase 2A: Structure discussion results into Phase 2B-compatible outputs'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue'
thisStepFile: '{workflow_path}/steps/step-02-structuring.md'
nextStepFile: null
workflowFile: '{workflow_path}/workflow.md'

# Helper References
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'
---

# Step 2: Result Structuring (Phase 2B-Compatible Output Generation)

**Progress: Step 2 of 3 (FINAL)**

---

## STEP GOAL

Transform the free-form discussion log into structured output files that Phase 2B can consume. This step runs **inline** in the Main Session (not a Task Agent).

**Key Principle:** Structuring is a POST-discussion activity. We capture what emerged from the discussion — we do not gate, filter, or constrain it.

**Architecture:** Instead of parsing specific markdown headers with `extract_section`/`extract_subsection`, Claude reads the **entire** `discussion_log.md` and directly synthesizes the content into Phase 2B-compatible YAML. This eliminates fragile header-matching and allows Step 1's discussion to flow naturally without rigid template constraints.

---

## COMMON RULES

> **Read:** See `_common-rules.md` for Universal Rules, UNATTENDED Mode Enforcement, and MCP Error Retry Protocol.

### Step-Specific Rules
- This step runs INLINE (not a Task Agent)
- MUST produce files compatible with Phase 2B input expectations
- No Binding Verification Gate — quality was ensured by the discussion itself
- No mechanical convergence metrics — convergence was judged qualitatively

---

## PHASE 2B COMPATIBILITY CONTRACT

> **CRITICAL:** Phase 2B expects these EXACT files as input:
>
> | File | Purpose | Load Strategy |
> |------|---------|---------------|
> | `03_refinement.yaml` | Primary hypothesis definition | FULL_LOAD |
> | `02_synthesis.yaml` | Synthesis details | FULL_LOAD |
> | `01_round_table/final_opinions.yaml` | Per-agent assessments | FULL_LOAD |
>
> This step MUST produce all three files in the expected format.

---

## PREREQUISITES

```python
# Required from Step 1
discussion_log_path = f"{research_folder}/discussion_log.md"

IF NOT exists(discussion_log_path):
    STOP("Missing discussion_log.md from Step 1. Re-run Step 1.")

discussion_log = Read(discussion_log_path)
```

---

## EXECUTION SEQUENCE

### 1. Read & Analyze Full Discussion Log

> **Key Change:** No more header-based parsing with `extract_section` / `extract_subsection`.
> Claude reads the ENTIRE discussion log and directly understands the content to generate structured YAML.
> This eliminates fragile header-matching and lets the discussion flow naturally without template constraints.

```python
# Read the full discussion log — this is the SOLE input
discussion_log = Read(f"{research_folder}/discussion_log.md")

# Also load gap context for metadata
gap_context = yaml.load(Read(f"{research_folder}/stage1_context_{gap_id}.yaml"))
metadata_yaml = yaml.load(Read(f"{research_folder}/01_round_table/00_metadata.yaml"))

# Load persona definitions (for final_opinions.yaml persona mapping)
personas_yaml = yaml.load(Read(f"{workflow_path}/personas.yaml"))

# Count exchanges and identify convergence reason from the log
exchange_count = count_exchanges(discussion_log) # Count "### Exchange" headers
# convergence_reason: extract from the final orchestrator output or Final Assessments section
```

**What you now have:** The complete discussion transcript including all exchanges, Final Assessments
(persona verdicts + consensus hypothesis + remaining concerns), and the full research context.

**What you do next:** Read the discussion content carefully and generate each YAML file by
synthesizing the information from the discussion. Use the YAML schema templates below as your
output format — fill every field by extracting/inferring from what was discussed.

### 2. Generate 03_refinement.yaml (Primary Output)

> This is the PRIMARY file Phase 2B reads. Analyze the discussion log and generate
> a complete `03_refinement.yaml` following the schema below.
>
> **How to fill each field:**
> - Read the discussion exchanges for claims, mechanisms, predictions, and experimental proposals
> - Read the Final Assessments section for persona verdicts and consensus hypothesis
> - Synthesize naturally — the discussion may not have explicit headers for each field,
> so use your understanding of the discussion content to populate the schema

Write `03_refinement.yaml` to `{research_folder}/03_refinement.yaml` following this EXACT schema.
Replace all `{placeholder}` values with content derived from the discussion:

```yaml
# 03_refinement.yaml - Phase 2A Output
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# This file is the PRIMARY input for Phase 2B step-01-init-parsing.
# Section numbers (0, 0.5, 1.1-1.6, 2, 4, 5) match Phase 2B parsing expectations.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

metadata:
  generated_at: "{timestamp}"
  workflow: "phase2a-dialogue "
  architecture: "Self-Contained Tikitaka Loop"
  schema_version: "10.0.0" # Free-parse schema (Phase 2B-compatible)
  gap_id: "{gap_id}"
  gap_title: "{gap_title}"
  execution_mode: "UNATTENDED"
  discussion_exchanges: {exchange_count}
  convergence_reason: "{convergence_reason}"

# ═══════════════════════════════════════════════════════════════
# SECTION 0: Established Facts & Claim Scope
# ═══════════════════════════════════════════════════════════════
# Phase 2B Step 1,3 use this to SKIP re-verification of established claims.
# → Extract from discussion: what claims did personas agree are already proven?
# vs. what needs new verification?

established_facts:
  claims:
    - claim: "..." # A claim discussed as already established
      status: "BUILD_ON" # or "PROVE_NEW"
      evidence: "..." # Citation or reasoning from discussion
    # ... additional claims
  scope_reduction_percentage: 0 # (Total - PROVE_NEW) / Total * 100
  phase2b_4_instructions: |
    Instructions for later phases on how to handle established vs. new claims.

# ═══════════════════════════════════════════════════════════════
# SECTION 0.5: Cross-Domain Transfer Summary (OPTIONAL)
# ═══════════════════════════════════════════════════════════════
# Only include if the discussion involved cross-domain mechanism transfer.
# Phase 2B checks: if this section exists AND transfer_validation_criteria non-empty,
# set requires_transfer_validation = true.

# cross_domain_transfer:
# source_field: "..."
# core_principle: "..."
# dl_translation: "..."
# preserved: "..."
# approximated: "..."
# lost: "..."
# fidelity_score: "High|Medium|Low"
# validation_criteria:
# - "..."

# ═══════════════════════════════════════════════════════════════
# SECTION 1.1: Core Statement
# ═══════════════════════════════════════════════════════════════
# → Extract from: Dr. Ally's consensus hypothesis + discussion convergence points
# Format as Under-If-Then-Because structure

core_statement:
  hypothesis_id: "H-{MethodName}-v1"
  confidence_level: 0.75 # Based on persona verdict strengths
  core_hypothesis_statement: |
    Under [scope], if [IV intervention], then [DV outcome], because [mechanism].
  alternative_hypothesis_h0: |
    There is no significant difference in [DV] between [IV conditions].

# ═══════════════════════════════════════════════════════════════
# SECTION 1.2: Variables Table
# ═══════════════════════════════════════════════════════════════
# → Extract from: discussion of what to manipulate, measure, and control

variables:
  independent:
    - name: "..."
      type: "categorical|continuous"
      operationalization: "how measured/manipulated"
      levels: [] # for categorical; omit for continuous
  dependent:
    - name: "..."
      type: "continuous"
      operationalization: "metric, range, unit"
      primary: true
    # additional DVs with primary: false
  controlled:
    - name: "..."
      operationalization: "how controlled"

# ═══════════════════════════════════════════════════════════════
# SECTION 1.3: Causal Mechanism (DYNAMIC)
# ═══════════════════════════════════════════════════════════════
# Phase 2B reads causal_chain_count to determine H-M sub-hypothesis count.
# → Extract from: discussion of HOW the hypothesis works (mechanism steps)

causal_mechanism:
  causal_chain_count: 3 # Number of steps (typically 2-5)
  steps:
    - step: 1
      description: "..."
      evidence: "..." # Citation/reasoning from discussion
      falsifier: "..." # What would disprove this step
    # ... one entry per mechanism step
  key_tension: "..." # Key unresolved tension from discussion
  evidence_summary: |
    Summary of evidence supporting the causal chain.

# ═══════════════════════════════════════════════════════════════
# SECTION 1.4: Key Assumptions (A1-A5)
# ═══════════════════════════════════════════════════════════════
# Phase 2B Step 5 maps each assumption to a risk.
# → Extract from: Prof. Rex's concerns + implicit assumptions in discussion

key_assumptions:
  - id: "A1"
    assumption: "..."
    supporting_evidence: "..."
    consequence_if_violated: "..."
  # ... up to A5

# ═══════════════════════════════════════════════════════════════
# SECTION 1.5: Scope & Boundaries
# ═══════════════════════════════════════════════════════════════
# Phase 2B Step 3 uses scope to detect H-C (condition) sub-hypotheses.
# → Extract from: discussion of where hypothesis applies/doesn't

scope:
  applies_to: |
    Domains, settings, conditions where hypothesis holds.
  does_not_apply_to: |
    Explicit exclusions discussed.
  known_limitations: |
    Constraints acknowledged in discussion.

# ═══════════════════════════════════════════════════════════════
# SECTION 1.6: Testable Predictions
# ═══════════════════════════════════════════════════════════════
# P1 (primary=true) → becomes basis for H-E1 in Phase 2B.
# → Extract from: Dr. Ally's predictions + discussion consensus on testable claims

predictions:
  - id: "P1"
    primary: true
    statement: "..."
    test_method: "..."
    success_criterion: "..."
    falsification: "..."
  - id: "P2"
    primary: false
    statement: "..."
    test_method: "..."
    success_criterion: "..."
    falsification: "..."
  # ... typically P1-P3

# ═══════════════════════════════════════════════════════════════
# SECTION 2: Experimental Setup Selection
# ═══════════════════════════════════════════════════════════════
# → Extract from: discussion of datasets, models, baselines

experimental_setup:
  dataset:
    name: "..."
    type: "standard|custom|synthetic"
    source: "..."
    path: "..."
    hypothesis_fit: "Why this dataset fits the hypothesis"
  model:
    name: "..."
    type: "..."
    source: "..."
    hypothesis_fit: "Why this model fits"
  baselines:
    - name: "..."
      method: "..."

# ═══════════════════════════════════════════════════════════════
# SECTION 3: Novelty & Innovation
# ═══════════════════════════════════════════════════════════════
# → Extract from: Dr. Nova's assessment + discussion differentiation points

novelty:
  preserved_novelty: "..."
  key_innovation: "..."
  differentiation:
    - prior_work: "..."
      difference: "..."

# ═══════════════════════════════════════════════════════════════
# SECTION 4: Key Related Work
# ═══════════════════════════════════════════════════════════════
# → Extract from: papers cited in discussion, baseline comparisons

related_work:
  baselines:
    - method: "..."
      performance: "..."
      dataset: "..."
      why_insufficient: "..."
  best_baseline_performance: "..."

# ═══════════════════════════════════════════════════════════════
# SECTION 5: Phase 2B Readiness
# ═══════════════════════════════════════════════════════════════
# → Synthesize from discussion: what must exist, what mechanism to test, what to compare

phase2b_readiness:
  status: "READY"
  sh1_existence: "What must exist/hold true for hypothesis to work"
  sh2_mechanism: "Core mechanism to test"
  sh3_comparison: "What to compare against (deferred to Phase 5)"
  open_questions:
    - "..."

# ═══════════════════════════════════════════════════════════════
# DECISION & DISCUSSION CONTEXT
# ═══════════════════════════════════════════════════════════════

decision:
  overall_status: "VALIDATED"
  discussion_convergence: "..."
  clarity_verified: true
  remaining_objections: []

discussion_context:
  total_exchanges: {exchange_count}
  agent_participation:
    dr_nova: 0 # Count from discussion log
    prof_vera: 0
    dr_sage: 0
    prof_pax: 0
    dr_ally: 0
    prof_rex: 0
  paper_citations: 0
  convergence_type: "qualitative"
```

```python
# YOU (Claude) generate the complete 03_refinement.yaml by reading discussion_log.md
# and filling every field in the schema above. No extract_section/build_refinement_yaml calls.
#
# Process:
# 1. Read the full discussion log (already loaded above)
# 2. Identify the core hypothesis from convergence points and Dr. Ally's consensus
# 3. Extract mechanism steps from discussion of how the hypothesis works
# 4. Identify variables from experimental proposals in the discussion
# 5. Extract predictions from testable claims discussed
# 6. Map Prof. Rex's concerns to key assumptions
# 7. Compile experimental setup from dataset/model/baseline discussion
# 8. Generate the YAML directly

Write(f"{research_folder}/03_refinement.yaml", refinement_yaml_content)
Log("Generated 03_refinement.yaml")
```

### 3. Generate 02_synthesis.yaml (Synthesis Output)

> Phase 2B also reads this file for synthesis details.
> Generate by synthesizing discussion content — same free-parse approach.

Write `02_synthesis.yaml` to `{research_folder}/02_synthesis.yaml` following this schema:

```yaml
# 02_synthesis.yaml - Phase 2A Synthesis
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Supplementary file loaded by Phase 2B (FULL_LOAD).
# Contains synthesis details, measurement plan, and validation strategy.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

metadata:
  generated_at: "{timestamp}"
  workflow: "phase2a-dialogue "
  architecture: "Self-Contained Tikitaka Loop"
  schema_version: "10.0.0"
  gap_id: "{gap_id}"

# → Core hypothesis summary (should be consistent with 03_refinement.yaml)
hypothesis_draft:
  title: "..."
  hypothesis_id: "..."
  core_claim: |
    ...
  mechanism: |
    ...
  predictions:
    - P1: "..."
    - P2: "..."
    - P3: "..."

# → Variable summary (mirrors 03_refinement.yaml Section 1.2 for cross-validation)
variables_summary:
  independent: "..."
  dependent_primary: "..."
  controlled: "..."

# → Null hypothesis (mirrors 03_refinement.yaml Section 1.1)
null_hypothesis:
  h0_statement: |
    ...
  statistical_test: "..."
  significance_level: 0.05

novelty_assessment:
  status: "VERIFIED"
  key_innovation: "..."
  differentiation_summary: |
    ...

clarity:
  overall_level: "HIGH"
  clarity_verified: true
  improvements_needed: []

experimental_scope:
  models: []
  datasets: []
  baselines: []

# → Measurement plan derived from experimental discussion
measurement_plan:
  data_collection:
    - source: "..."
  procedure:
    - step: "..."
  success_criteria:
    - "..."

# → Validation strategy
validation:
  internal_validity:
    - "..."
  external_validity:
    - "..."

# → Key insights from the discussion itself
discussion_synthesis:
  key_insights:
    - "..."
  breakthrough_moments:
    - "..."
  resolved_tensions:
    - "..."
```

```python
# Generate 02_synthesis.yaml by synthesizing discussion content
# Must be consistent with 03_refinement.yaml (same hypothesis, same predictions)
Write(f"{research_folder}/02_synthesis.yaml", synthesis_yaml_content)
Log("Generated 02_synthesis.yaml")
```

### 4. Generate 01_round_table/final_opinions.yaml (Agent Assessments)

> Phase 2B reads this for per-agent perspective assessments.
> Extract from the `## Final Assessments` section of discussion_log.md.
>
> **Single Source of Truth:** Persona metadata (icon, name) loaded from `personas.yaml`.

Write to `{research_folder}/01_round_table/final_opinions.yaml`:

```yaml
# final_opinions.yaml - Agent Final Assessments
metadata:
  generated_at: "{timestamp}"
  workflow: "phase2a-dialogue "
  architecture: "Self-Contained Tikitaka Loop"
  source: "discussion_log.md Final Assessments"

final_opinions:
  # → Extract each persona's verdict + assessment from Final Assessments
  perspective_novelty:
    agent: "Dr. Nova"
    icon: "🔭"
    assessment: |
      [Verdict + assessment from Final Assessments]
    key_points:
      - "..."

  perspective_falsifiability:
    agent: "Prof. Vera"
    icon: "🔬"
    assessment: |
      ...
    key_points:
      - "..."

  perspective_significance:
    agent: "Dr. Sage"
    icon: "🎯"
    assessment: |
      ...
    key_points:
      - "..."

  perspective_plausibility:
    agent: "Prof. Pax"
    icon: "⚙️"
    assessment: |
      ...
    key_points:
      - "..."

  # → Extract from Consensus Hypothesis section
  refiner_advocate:
    agent: "Dr. Ally"
    icon: "🛡️"
    assessment: |
      ...
    key_points:
      - "..."

  # → Extract from Remaining Concerns section
  refiner_critic:
    agent: "Prof. Rex"
    icon: "🔍"
    assessment: |
      ...
    key_points:
      - "..."

consensus:
  status: "CONVERGED"
  convergence_reason: "..."
  remaining_objections: []
```

```python
# Generate final_opinions.yaml from Final Assessments in discussion_log.md
Write(f"{research_folder}/01_round_table/final_opinions.yaml", final_opinions_yaml_content)
Log("Generated 01_round_table/final_opinions.yaml")
```

### 5. Generate 03_refinement.md (Human-Readable Summary)

> Generate a human-readable markdown summary of the hypothesis.
> Content should be consistent with `03_refinement.yaml`.

```python
# Generate human-readable summary from discussion content
# Include: metadata, research dialogue context, final hypothesis,
# predictions, novelty, experimental design, limitations, decision

# Load persona names from personas.yaml for participant list
participant_names = [p["name"] for p in personas_yaml["perspective"] + personas_yaml["refinement"]]
participants_str = ", ".join(participant_names)

refinement_md = f"""# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: {timestamp}
- **Workflow**: phase2a-dialogue 
- **Architecture**: Self-Contained Tikitaka Loop 
- **Gap ID**: {gap_id}
- **Gap Title**: {gap_title}
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: {exchange_count}

---

## Research Dialogue Context

**Participants**: {participants_str}

**Total Exchanges**: {exchange_count}

**Convergence Reason**: {convergence_reason}

### Key Insights
[Synthesize from discussion]

### Breakthrough Moments
[Key turning points in the discussion]

---

## Final Hypothesis

### Title
[Hypothesis title]

### Core Claim
[Under-If-Then-Because statement]

### Mechanism
[Causal mechanism summary]

---

## Predictions
[P1-P3 with success criteria]

---

## Novelty
[What's new and how it differs from prior work]

---

## Experimental Design
[Dataset, model, baselines]

---

## Limitations
[Known limitations and scope boundaries]

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | {convergence_reason} |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

"""

Write(f"{research_folder}/03_refinement.md", refinement_md)
Log("Generated 03_refinement.md")
```

### 6. Validate All Outputs

```python
# ━━━ Output Validation ━━━
REQUIRED_OUTPUTS = [
    f"{research_folder}/03_refinement.yaml",
    f"{research_folder}/03_refinement.md",
    f"{research_folder}/02_synthesis.yaml",
    f"{research_folder}/01_round_table/final_opinions.yaml",
    f"{research_folder}/discussion_log.md",
]

missing = []
for output_file in REQUIRED_OUTPUTS:
    IF NOT exists(output_file):
        missing.append(output_file)

IF missing:
    Log(f"ERROR: Missing output files: {missing}")
    STOP("Output validation failed. Some required files were not generated.")

# Quick content validation (Phase 2B-Compatible checks)
refinement = yaml.load(Read(f"{research_folder}/03_refinement.yaml"))

# Section 0: Established Facts
IF NOT refinement.get("established_facts", {}).get("claims"):
    Log("WARNING: 03_refinement.yaml missing established_facts.claims")

# Section 1.1: Core Statement
IF NOT refinement.get("core_statement", {}).get("hypothesis_id"):
    Log("WARNING: 03_refinement.yaml missing core_statement.hypothesis_id")
IF NOT refinement.get("core_statement", {}).get("core_hypothesis_statement"):
    Log("WARNING: 03_refinement.yaml missing core_statement.core_hypothesis_statement")
IF NOT refinement.get("core_statement", {}).get("alternative_hypothesis_h0"):
    Log("WARNING: 03_refinement.yaml missing core_statement.alternative_hypothesis_h0")

# Section 1.2: Variables
IF NOT refinement.get("variables"):
    Log("WARNING: 03_refinement.yaml missing variables")

# Section 1.3: Causal Mechanism
IF NOT refinement.get("causal_mechanism", {}).get("steps"):
    Log("WARNING: 03_refinement.yaml missing causal_mechanism.steps")

# Section 1.4: Key Assumptions
IF NOT refinement.get("key_assumptions"):
    Log("WARNING: 03_refinement.yaml missing key_assumptions")

# Section 1.5: Scope
IF NOT refinement.get("scope"):
    Log("WARNING: 03_refinement.yaml missing scope")

# Section 1.6: Predictions
IF NOT refinement.get("predictions"):
    Log("WARNING: 03_refinement.yaml missing predictions")

# Section 2: Experimental Setup
IF NOT refinement.get("experimental_setup"):
    Log("WARNING: 03_refinement.yaml missing experimental_setup")

# Section 5: Phase 2B Readiness
IF NOT refinement.get("phase2b_readiness"):
    Log("WARNING: 03_refinement.yaml missing phase2b_readiness")

# Decision
IF NOT refinement.get("decision", {}).get("clarity_verified"):
    Log("WARNING: clarity_verified not set in 03_refinement.yaml")

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Phase 2A Output Files Generated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 03_refinement.yaml ← Phase 2B primary input
📄 03_refinement.md ← Human-readable summary
📄 02_synthesis.yaml ← Synthesis details
📄 final_opinions.yaml ← Per-agent assessments
📄 discussion_log.md ← Full discussion transcript
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
```

### 7. Complete Phase 2A and Transition

<helper-reference>
**Helper:** `{helpers_path}/phase2a_step_task_management.md`
**Function:** `transition_step_tasks(step_tasks_file, transitions_spec, step_name, message)`
</helper-reference>

```python
from helpers.phase2a_step_task_management import transition_step_tasks

# Mark both remaining tasks as done
# Note: In Tikitaka architecture, 2A-3 (Advocate-Critic Refinement) is integrated
# into the discussion loop (Dr. Ally + Prof. Rex participate as personas),
# so 2A-3 completes together with structuring.
transition_step_tasks(
    step_tasks_file=step_tasks_file,
    transitions_spec=[
        {"task_key": "2A-2", "new_status": "done"},
        {"task_key": "2A-3", "new_status": "done"},
    ],
    step_name="step-02-structuring",
    message="Phase 2A complete — all output files generated"
)

# Mark pipeline-level Phase 2A task as done
# (This is the parent Phase 2A task, not the step-level tasks)
pipeline_phase2a_task = find_archon_task(
    project_id=pipeline_project_id,
    query="Phase 2A"
)
IF pipeline_phase2a_task:
    mcp__archon__manage_task(
        action="update",
        task_id=pipeline_phase2a_task["id"],
        status="done"
    )

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Phase 2A COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Architecture: Self-Contained Tikitaka Loop (Free-Parse)
Discussion: {exchange_count} exchanges
Hypothesis: {hypothesis_title}
Status: VALIDATED

Step Tasks:
• 2A-0: Gap Selection [done] ✓
• 2A-P: Paper Preparation [done] ✓
• 2A-1: Free Discussion [done] ✓
• 2A-2: Result Structuring [done] ✓
• 2A-3: Advocate-Critic Refine. [done] ✓

Output Files:
• 03_refinement.yaml → Phase 2B (primary)
• 02_synthesis.yaml → Phase 2B (synthesis)
• final_opinions.yaml → Phase 2B (assessments)
• 03_refinement.md → Human reference
• discussion_log.md → Full transcript

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

Log("Phase 2A Complete")
```

---

## SUCCESS/FAILURE METRICS

### SUCCESS
- All 5 output files generated and validated
- `03_refinement.yaml` has core_claim, predictions, decision.clarity_verified
- `02_synthesis.yaml` has hypothesis_draft and clarity.overall_level
- `final_opinions.yaml` has all 6 agent assessments
- `03_refinement.md` is human-readable summary
- All Archon step tasks marked as done
- Pipeline Phase 2A task marked as done

### FAILURE
- Any required output file missing
- `03_refinement.yaml` missing core fields (core_claim, predictions, decision)
- `02_synthesis.yaml` missing clarity verification
- Agent assessments incomplete (< 6 agents)
- Archon tasks not transitioned
- Phase 2B would fail to parse outputs
