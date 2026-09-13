---
name: 'step-01-discussion'
description: 'Phase 2A: Free-Form Research Discussion (Self-Contained Loop INLINE)'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue'
thisStepFile: '{workflow_path}/steps/step-01-discussion.md'
nextStepFile: '{workflow_path}/steps/step-02-structuring.md'
workflowFile: '{workflow_path}/workflow.md'

# Helper References
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'
---

# Step 1: Free-Form Research Discussion (Self-Contained Loop)

**Progress: Step 1 of 3** | Next: Step 2 - Result Structuring

---

## STEP GOAL

Run a free-form, multi-perspective research discussion with 6 research personas. The discussion generates and validates a research hypothesis through natural scientific discourse.

**Architecture:** This step runs entirely **INLINE** in a single turn using a Self-Contained Loop:
1. Call `orchestrate_exchange.py` via Bash to get persona selection + convergence check
2. Parse JSON output
3. If converged → BREAK and write Final Assessments
4. Write persona exchange to `discussion_log.md`
5. Loop back to step 1

No Hook dependency. No response termination. Everything runs in one continuous turn.

---

## COMMON RULES

> **Read:** See `_common-rules.md` for Universal Rules, UNATTENDED Mode Enforcement, and MCP Error Retry Protocol.

### Step-Specific Rules
- This step runs **INLINE** — you execute the discussion directly in a single turn
- The **orchestrate_exchange.py** script provides persona selection and convergence detection
- Write all discussion exchanges to `discussion_log.md` in the research folder
- When orchestrator returns `converged: true`, write Final Assessments and proceed to Step 2
- Do NOT use Task Agent for this step
- **MAX_LOOP_ITERATIONS = 60** — safety valve to prevent infinite loops

---

## PREREQUISITES

Verify outputs from Step 0 exist:

```python
# Required files from Step 0
REQUIRED_FILES = [
    f"{research_folder}/stage1_context_{gap_id}.yaml", # Gap context
    f"{research_folder}/01_round_table/00_metadata.yaml", # Metadata
    f"{research_folder}/discussion_log.md", # Initialized by Step 0
]

for f in REQUIRED_FILES:
    IF NOT exists(f):
        STOP(f"Missing prerequisite: {f}. Re-run Step 0.")
```

---

## RESEARCH PERSONAS

> **Single Source of Truth:** Load persona information from `{workflow_path}/personas.yaml`
>
> The personas.yaml file contains authoritative definitions for all 6 research personas:
> - **Perspective Personas** (4): Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax
> - **Refinement Personas** (2): Dr. Ally, Prof. Rex
>
> Each persona includes: icon, name, title, role, identity, communication_style, principles, response_focus, key_questions.
>
> See `agents/research-discussion-orchestrator.md` for execution guidance (BMad-style activation sequence).

```python
# Load personas at discussion start
personas_yaml = yaml.load(Read(f"{workflow_path}/personas.yaml"))
perspective_personas = personas_yaml["perspective"] # 4 personas
refinement_personas = personas_yaml["refinement"] # 2 personas

# Quick reference table (dynamically built from YAML)
# | Icon | Name | Title |
# |------|------|-------|
# | 🔭 | Dr. Nova | Creative Novelty Explorer |
# | 🔬 | Prof. Vera | Rigorous Validation Architect |
# | 🎯 | Dr. Sage | Research Impact Evaluator |
# | ⚙️ | Prof. Pax | Feasibility & Reality Checker |
# | 🛡️ | Dr. Ally | Hypothesis Strengthening Champion |
# | 🔍 | Prof. Rex | Hypothesis Stress-Test Master |
```

---

## EXECUTION SEQUENCE

### 1. Load Discussion Context

```python
# Load persona guide
persona_guide = Read(f"{workflow_path}/agents/research-discussion-orchestrator.md")

# Read current discussion state
discussion_log = Read(f"{research_folder}/discussion_log.md")

# Previous Failure / Routing Context is hard input when present.
# If discussion_log.md contains this section with SUPERSEDED, ROUTED_TO_PHASE_2A,
# PARTIAL, FAIL, or pivot records, every exchange must redesign away from the
# failed approach families and preserve validated partial findings.
prior_failure_context = extract_section(discussion_log, "### Previous Failure / Routing Context")

# Count current exchanges
exchange_count = count_exchanges(discussion_log) # Count "### Exchange" headers

# Resolve script paths
ORCHESTRATOR_SCRIPT = f"{workflow_path}/scripts/orchestrate_exchange.py"
ORCHESTRATOR_CONFIG = f"{workflow_path}/scripts/phase2a_config.yaml"
PERSONAS_YAML = f"{workflow_path}/personas.yaml"
PYTHON = "/home/anonymous/miniforge3/envs/YouRA/bin/python"
```

### 2. Begin Discussion (Exchange 1)

**For the FIRST exchange only**, start with Dr. Nova:

```markdown
### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

[Your response as Dr. Nova - introduce creative initial ideas for addressing the research gap. Reference specific papers from the briefing. Propose 2-3 unconventional angles to explore.]
```

Write this to `discussion_log.md`, then **continue directly to the loop** (do NOT stop).

### 3. Self-Contained Discussion Loop (Dual-Exchange Tikitaka)

After writing Exchange 1, enter the orchestration loop. Each iteration produces **2 exchanges**: one by the external LLM and one by Claude, creating a tikitaka dynamic between different AI perspectives.

```python
MAX_LOOP_ITERATIONS = 30 # Safety valve (each iteration = 2 exchanges, so max ~60 exchanges)

for iteration in range(MAX_LOOP_ITERATIONS):
    # ── A. Call orchestrator script via Bash ──
    result_json = Bash(f"""
        {PYTHON} "{ORCHESTRATOR_SCRIPT}" \
            --discussion-log "{research_folder}/discussion_log.md" \
            --config "{ORCHESTRATOR_CONFIG}" \
            --personas "{PERSONAS_YAML}" \
            --research-folder "{research_folder}"
    """)

    # ── B. Parse JSON output ──
    try:
        result = json.loads(result_json.strip())
    except json.JSONDecodeError:
        log("⚠️ Orchestrator JSON parse error, using round-robin fallback")
        all_personas = perspective_personas + refinement_personas
        idx1 = exchange_count % len(all_personas)
        idx2 = (exchange_count + 1) % len(all_personas)
        result = {
            "converged": False,
            "exchange_number": exchange_count + 1,
            "llm_exchange": None,
            "llm_persona": {"name": all_personas[idx1]["name"], "icon": all_personas[idx1]["icon"]},
            "claude_persona": {"name": all_personas[idx2]["name"], "icon": all_personas[idx2]["icon"]},
            "fallback": True,
        }

    # ── C. Check convergence ──
    if result.get("converged"):
        log(f"✅ Discussion CONVERGED at exchange {result.get('exchange_number', exchange_count)}")
        convergence_summary = result.get("summary", "Convergence criteria met.")
        BREAK # Exit loop → proceed to Final Assessments (Section 6)

    # ── D. Check for error ──
    if result.get("error"):
        log(f"⚠️ Orchestrator error: {result['error']}")
        CONTINUE # Skip this iteration

    # ── E. Exchange N: Write LLM's response ──
    exchange_number = result.get("exchange_number", exchange_count + 1)
    llm_exchange = result.get("llm_exchange")
    llm_persona = result.get("llm_persona", {})
    claude_persona_info = result.get("claude_persona", {})

    if llm_exchange:
        # LLM already wrote the full exchange — append to discussion_log.md
        # Wrap in Exchange header:
        append_to_discussion_log(f"""
### Exchange {exchange_number}

{llm_exchange}

---
""")
        log(f"📝 Exchange {exchange_number}: {llm_persona.get('icon','')} {llm_persona.get('name','')} (External LLM)")
    else:
        # Fallback: Claude writes this exchange too (as llm_persona)
        # Write response as llm_persona using personas.yaml definition
        append_to_discussion_log(f"""
### Exchange {exchange_number}

[Write as {llm_persona.get('icon','')} **{llm_persona.get('name','')}** using personas.yaml]

---
""")

    # ── F. Exchange N+1: Claude writes response (as claude_persona) ──
    claude_exchange_number = exchange_number + 1

    # Load claude_persona's full definition from personas.yaml
    # Read the recent 4 exchanges (including LLM's just-written one)
    # Write an authentic response that REACTS to what the LLM persona just said

    # ── F.1 Paper Reference: If orchestrator assigned a paper reference ──
    # Check result["claude_paper_reference"] — if present, it contains:
    # {"paper": "P1", "sections": ["Methodology", "Experiments & Results"]}
    #
    # To use it:
    # 1. Map paper ID (e.g. "P1") to summary file:
    # summary_files = sorted(glob(f"{research_folder}/paper_summaries/*_summary.md"))
    # P1 = summary_files[0], P2 = summary_files[1], etc.
    # 2. Read the summary file
    # 3. Find the assigned sections (### Methodology, ### Experiments & Results)
    # 4. Include that content in your response, citing specific findings
    #
    # Example:
    # claude_ref = result.get("claude_paper_reference")
    # if claude_ref:
    # paper_id = claude_ref["paper"] # e.g. "P1"
    # sections = claude_ref["sections"] # e.g. ["Methodology"]
    # idx = int(paper_id[1:]) - 1 # P1 -> index 0
    # summary_path = sorted(glob(f"{research_folder}/paper_summaries/*_summary.md"))[idx]
    # summary_content = Read(summary_path)
    # # Find and read the assigned ### sections from the summary
    # # Incorporate findings into your persona response

    # Claude writes under ### Exchange {claude_exchange_number}
    # Follow the Persona Response Format (Section 4)
    # Use claude_persona's identity, principles, communication_style, response_focus, key_questions
    # MUST reference and respond to the LLM's exchange above
    # If paper reference was assigned, cite specific evidence from the paper sections

    exchange_count = claude_exchange_number # Update for next iteration (2 exchanges added)
```

**Important Loop Rules:**
- Do NOT terminate your response between iterations — everything runs in one continuous turn
- Each iteration produces **2 exchanges**: External LLM (Exchange N) + Claude (Exchange N+1)
- The **External LLM** and **Claude** see each other's recent exchanges (last 4) creating genuine tikitaka
- On script failure: Claude writes both exchanges using round-robin personas
- If `MAX_LOOP_ITERATIONS` reached without convergence: force convergence and proceed

### 3.3. Tikitaka Dynamics

The dual-exchange architecture creates a genuine cross-model discussion:

| Exchange | Written By | Persona | Context (reads last 4) |
|----------|-----------|---------|----------------------|
| N | External LLM (GPT-5.2) | Selected by LLM 1 | Includes Claude's previous exchanges |
| N+1 | Claude | Selected by LLM 1 | Includes LLM's just-written Exchange N |
| N+2 | External LLM (GPT-5.2) | Selected by LLM 1 | Includes Claude's Exchange N+1 |
| N+3 | Claude | Selected by LLM 1 | Includes LLM's Exchange N+2 |

**Claude's response rules for Exchange N+1:**
1. **Read** the LLM's Exchange N carefully — identify claims, arguments, and gaps
2. **Load** claude_persona's full definition from `personas.yaml`
3. **React** authentically: agree, disagree, build upon, or challenge the LLM's points
4. **Build on prior points**: Reference the LLM persona by name when responding to their arguments
5. **Stay in character**: Use the assigned persona's communication style and principles

### 3.5. Dynamic Paper Reference

The orchestrator now assigns specific paper sections for each persona to reference.

**How it works:**

1. **LLM 1** (persona selector) sees each paper's Key Contributions + Potential Relevance + section list
2. **LLM 1** assigns `paper_references` in its JSON output:
   ```json
   {"paper": "P1", "sections": ["Methodology", "Experiments & Results"]}
   ```
3. **LLM 2** receives the assigned sections' content injected into its prompt (automatic)
4. **Claude** receives `claude_paper_reference` in the orchestrator JSON output

**When Claude writes Exchange N+1 with an assigned paper reference:**

1. Read `{research_folder}/paper_summaries/*_summary.md` (map P1→first file, P2→second, etc.)
2. Find the assigned `### Section` headers in the summary
3. Incorporate the section content into your persona response
4. Cite findings using `[Author et al., Year]` format

**Fallback (no reference assigned):**
If no `claude_paper_reference` in the JSON, use the original approach:
- Read `{research_folder}/paper_summaries/{stem}_summary.md` when relevant
- Find the relevant section summary (e.g., "### Methodology")
- Use it directly for discussion points

---

### 4. Persona Response Format

Each persona response must follow this format:

```markdown
### Exchange {N}

{icon} **{name}** ({role}):

[Response content - 3-6 paragraphs]

**Key Points:**
- [Point 1]
- [Point 2]
- [Point 3]

---
```

**Response Guidelines:**
- Reference specific papers by `[Author et al., Year]` or title
- Build on previous speakers' points
- Challenge weak arguments constructively
- Propose concrete mechanisms, predictions, or experiments
- Stay in character for each persona

### 5. Convergence Detection

The orchestrator script checks these criteria via external LLM (once exchange count >= `min_exchanges` from `phase2a_config.yaml`).

> **Authoritative Source:** Exchange count thresholds are defined in `scripts/phase2a_config.yaml` under `discussion.min_exchanges` and `discussion.max_exchanges`.

- [ ] **SPECIFIC**: Clear core claim stated?
- [ ] **MECHANISM**: How it works explained?
- [ ] **PREDICTIONS**: 2-3 testable predictions with criteria?
- [ ] **NOVELTY**: What's new articulated?
- [ ] **FEASIBILITY**: Implementation realistic?
- [ ] **OBJECTIONS**: Major criticisms addressed?

When ALL criteria are met, the orchestrator returns:

```json
{"converged": true, "exchange_number": 7, "summary": "CONVERGE\nKey achievements:\n- ..."}
```

### 6. Write Final Assessments

When convergence is signaled (loop exits), append the Final Assessments section to `discussion_log.md`.

> **Note:** This is a LIGHTWEIGHT summary only. Step 2 will read the FULL discussion log
> and extract all structured hypothesis details (variables, mechanism, predictions, etc.)
> directly from the discussion content. Do NOT try to fill in detailed templates here.

```markdown
## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** [STRONG / MODERATE / WEAK]
- **Assessment:** [2-3 sentences on hypothesis novelty]

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** [STRONG / MODERATE / WEAK]
- **Assessment:** [2-3 sentences on testability]

🎯 **Dr. Sage** (Significance):
- **Verdict:** [STRONG / MODERATE / WEAK]
- **Assessment:** [2-3 sentences on research impact]

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** [STRONG / MODERATE / WEAK]
- **Assessment:** [2-3 sentences on implementation realism]

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

[Free-form summary of the hypothesis that emerged from the discussion, 5-10 sentences.
Include: core claim, proposed mechanism, key predictions, and experimental approach.
Write naturally — Step 2 will structure this into YAML.]

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- [Concern 1]
- [Concern 2]
- **Mitigation Strategy:** [How to address in experiments]
```

### 7. Proceed to Step 2

After writing Final Assessments:

<helper-reference>
**Helper:** `{helpers_path}/phase2a_step_task_management.md`
**Function:** `transition_step_tasks(step_tasks_file, transitions_spec, step_name, message)`
</helper-reference>

```python
# Update Archon task status via helper
from helpers.phase2a_step_task_management import transition_step_tasks

transition_step_tasks(
    step_tasks_file=step_tasks_file,
    transitions_spec=[
        {"task_key": "2A-P", "new_status": "done"},
        {"task_key": "2A-1", "new_status": "done"},
        {"task_key": "2A-2", "new_status": "doing"},
    ],
    step_name="step-01-discussion",
    message="Discussion converged, starting result structuring"
)

print(f"""
✅ Step 1 Complete (Discussion)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 2A-0: Gap Selection [done] ✓
• 2A-P: Paper Preparation [done] ✓
• 2A-1: Free Discussion [done] ✓ ({exchange_count} exchanges)
• 2A-2: Result Structuring [doing] ← CURRENT
• 2A-3: Advocate-Critic Refine. [todo]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Proceeding to Step 2 (Result Structuring)
""")

# Proceed to Step 2
Read("{nextStepFile}")
```

---

## DUAL-EXCHANGE TIKITAKA FLOW

```
┌──────────────────────────────────────────────────────────────┐
│ MAIN SESSION (INLINE) │
│ │
│ [Step 1 Start] │
│ │                                                       │
│ ▼                                                       │
│ Write Exchange 1 (Dr. Nova — by Claude) │
│ │                                                       │
│ ▼                                                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │              TIKITAKA LOOP (per iteration) │ │
│ │                                                          │ │
│ │  A. Bash: orchestrate_exchange.py │ │
│ │       │ │ │
│ │       ├── LLM 1: Select 2 personas + convergence check │ │
│ │       │ (reads last 4 exchanges) │ │
│ │       │ │ │
│ │       ├── converged: true ───► BREAK │ │
│ │       │ │ │
│ │       ├── LLM 2: Write full Exchange N │ │
│ │       │ (as llm_persona, reads last 4 exchanges) │ │
│ │       │ │ │
│ │       ▼ │ │
│ │  B. Parse JSON → append LLM's Exchange N │ │
│ │       │ │ │
│ │       ▼ │ │
│ │  C. Claude writes Exchange N+1 │ │
│ │     (as claude_persona, REACTS to LLM's Exchange N) │ │
│ │     (reads last 4 exchanges including LLM's) │ │
│ │       │ │ │
│ │       └──────── LOOP ──────────────────────────────────┐ │ │
│ │                                                        │ │ │
│ └────────────────────────────────────────────────────────┘ │ │
│ │
│ ┌──── CONVERGED ────────────────────────────────────────┘
│ ▼                                                       │
│ Write Final Assessments │
│ │                                                       │
│ ▼                                                       │
│ Update Archon Tasks → Proceed to Step 2 │
│ │
└──────────────────────────────────────────────────────────────┘
```

---

## SUCCESS/FAILURE METRICS

### SUCCESS
- Discussion ran INLINE in a single turn with Dual-Exchange Tikitaka Loop
- Both External LLM and Claude contributed exchanges (tikitaka dynamic)
- Exchange count reached `min_exchanges` from `scripts/phase2a_config.yaml` before convergence
- `discussion_log.md` contains complete transcript with both LLM and Claude exchanges
- All 6 personas participated at least once
- Final Assessments section written with persona verdicts and consensus hypothesis
- Archon task transitions executed (2A-1 → done, 2A-2 → doing)

### FAILURE
- Orchestrator script failed (check stderr output)
- Converged before `min_exchanges` reached
- Missing Final Assessments section
- Any persona never spoke
- `discussion_log.md` not updated
- Only one model contributed (no tikitaka — all LLM or all Claude)
- Archon tasks not updated
- Loop reached MAX_LOOP_ITERATIONS without convergence
