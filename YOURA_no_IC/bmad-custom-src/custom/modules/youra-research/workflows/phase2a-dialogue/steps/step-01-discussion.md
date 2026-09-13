---
name: 'step-01-discussion'
description: 'Phase 2A: Free-Form Research Discussion (Claude Self-Play Loop INLINE — Independent-Controller Ablation)'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue'
thisStepFile: '{workflow_path}/steps/step-01-discussion.md'
nextStepFile: '{workflow_path}/steps/step-02-structuring.md'
workflowFile: '{workflow_path}/workflow.md'

# Helper References
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'
---

# Step 1: Free-Form Research Discussion (Claude Self-Play Loop)

**Progress: Step 1 of 3** | Next: Step 2 - Result Structuring

---

## ABLATION NOTE (Independent Controller Removed)

> This step originally ran a "Tikitaka" loop in which an **external LLM**
> (GPT-5.2 via `orchestrate_exchange.py`) selected personas, wrote alternating
> exchanges, and judged convergence. In this ablation build the external LLM is
> **removed**: Claude plays ALL personas itself and judges convergence itself
> against the same 6 criteria. Do NOT call `orchestrate_exchange.py`.
> The discussion protocol (persona set, exchange format, min/max exchange
> thresholds, convergence criteria, Final Assessments) is unchanged.

---

## STEP GOAL

Run a free-form, multi-perspective research discussion with 6 research personas. The discussion generates and validates a research hypothesis through natural scientific discourse.

**Architecture:** This step runs entirely **INLINE** in a single turn using a Self-Play Loop:
1. Claude selects the next 2 personas (coverage-based rotation)
2. Claude writes Exchange N as persona A, then Exchange N+1 as persona B (reacting to N)
3. Once `min_exchanges` reached, Claude self-checks the 6 convergence criteria and records the verdict
4. If ALL criteria met → BREAK and write Final Assessments
5. Loop back to step 1

No Hook dependency. No external LLM. No response termination. Everything runs in one continuous turn.

---

## COMMON RULES

> **Read:** See `_common-rules.md` for Universal Rules, UNATTENDED Mode Enforcement, and MCP Error Retry Protocol.

### Step-Specific Rules
- This step runs **INLINE** — you execute the discussion directly in a single turn
- Do NOT call `orchestrate_exchange.py` or any external LLM — Claude writes every exchange and judges convergence itself
- Write all discussion exchanges to `discussion_log.md` in the research folder
- Record every convergence self-check in `{research_folder}/01_round_table/convergence_checks.md` (audit trail for the ablation study)
- When ALL 6 convergence criteria are met (self-judged), write Final Assessments and proceed to Step 2
- Do NOT use Task Agent for this step
- **MAX_LOOP_ITERATIONS = 30** — safety valve to prevent infinite loops (each iteration = 2 exchanges)

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

# Load exchange thresholds — AUTHORITATIVE source (unchanged from baseline)
config = yaml.load(Read(f"{workflow_path}/scripts/phase2a_config.yaml"))
MIN_EXCHANGES = config["discussion"]["min_exchanges"]   # e.g. 15
MAX_EXCHANGES = config["discussion"]["max_exchanges"]   # e.g. 20

# Paper summaries (created by Step 0)
paper_summaries = sorted(glob(f"{research_folder}/paper_summaries/*_summary.md"))
# P1 = paper_summaries[0], P2 = paper_summaries[1], etc.
```

### 2. Begin Discussion (Exchange 1)

**For the FIRST exchange only**, start with Dr. Nova:

```markdown
### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

[Your response as Dr. Nova - introduce creative initial ideas for addressing the research gap. Reference specific papers from the briefing. Propose 2-3 unconventional angles to explore.]
```

Write this to `discussion_log.md`, then **continue directly to the loop** (do NOT stop).

### 3. Self-Play Discussion Loop (Dual-Exchange)

After writing Exchange 1, enter the self-play loop. Each iteration produces **2 exchanges**, both written by Claude as two DIFFERENT personas reacting to each other and to the recent discussion.

```python
MAX_LOOP_ITERATIONS = 30 # Safety valve (each iteration = 2 exchanges, so max ~60 exchanges)

for iteration in range(MAX_LOOP_ITERATIONS):
    # ── A. Select the next 2 personas (Claude decides, coverage-based) ──
    # Selection rules:
    #   1. COVERAGE FIRST: any persona that has not yet spoken takes priority
    #      (all 6 personas MUST participate before convergence is allowed).
    #   2. Then pick the persona whose role best challenges or extends the
    #      LAST exchange (e.g. a feasibility claim → Prof. Pax or Prof. Rex;
    #      a novelty claim → Prof. Vera for falsifiability).
    #   3. Never pick the same persona for both slots; avoid a persona
    #      speaking twice in a row across iterations.
    persona_a, persona_b = select_next_personas(discussion_log, personas_yaml)

    # ── B. Assign paper references (Claude decides, rotation-based) ──
    # Rotate through P1..Pn across iterations so every paper is used at least
    # once. For each persona, pick 1-2 relevant sections from the summary
    # (e.g. "### Methodology", "### Experiments & Results") and cite specific
    # findings using [Author et al., Year] format.
    paper_ref_a = assign_paper_reference(iteration, persona_a, paper_summaries)
    paper_ref_b = assign_paper_reference(iteration, persona_b, paper_summaries)

    # ── C. Exchange N: Claude writes as persona_a ──
    # Read the recent 4 exchanges. React authentically: agree, disagree,
    # build upon, or challenge. Use persona_a's identity, principles,
    # communication_style, response_focus, key_questions from personas.yaml.
    # Follow the Persona Response Format (Section 4).
    exchange_number = exchange_count + 1
    append_to_discussion_log(exchange_number, persona_a, response_a)

    # ── D. Exchange N+1: Claude writes as persona_b, REACTING to Exchange N ──
    # persona_b MUST reference persona_a by name and respond to their
    # specific claims, then add its own perspective.
    append_to_discussion_log(exchange_number + 1, persona_b, response_b)

    exchange_count = exchange_number + 1

    # ── E. Convergence self-check (only once min_exchanges reached) ──
    if exchange_count >= MIN_EXCHANGES:
        # Claude evaluates the WHOLE discussion so far against ALL 6 criteria.
        # Be strict: a criterion passes only if concrete evidence exists in
        # the log (quote the exchange numbers as evidence).
        verdicts = self_check_convergence(discussion_log)  # dict of 6 criteria → PASS/FAIL + evidence

        # Record the verdict (audit trail — REQUIRED)
        append_to_file(f"{research_folder}/01_round_table/convergence_checks.md", f"""
## Convergence Check @ Exchange {exchange_count}
- SPECIFIC:    {verdicts.SPECIFIC}    — {evidence}
- MECHANISM:   {verdicts.MECHANISM}   — {evidence}
- PREDICTIONS: {verdicts.PREDICTIONS} — {evidence}
- NOVELTY:     {verdicts.NOVELTY}     — {evidence}
- FEASIBILITY: {verdicts.FEASIBILITY} — {evidence}
- OBJECTIONS:  {verdicts.OBJECTIONS}  — {evidence}
- All personas spoke: {all_spoke}
- Verdict: {"CONVERGED" if all pass else "CONTINUE"}
""")

        if ALL criteria PASS and all 6 personas have spoken:
            BREAK # Exit loop → proceed to Final Assessments (Section 6)

    # ── F. Force-convergence guard ──
    if exchange_count >= MAX_EXCHANGES:
        # Force convergence: run one final Dr. Ally synthesis exchange that
        # explicitly resolves any still-failing criteria, record
        # "FORCED CONVERGENCE" in convergence_checks.md, then BREAK.
        BREAK
```

**Important Loop Rules:**
- Do NOT terminate your response between iterations — everything runs in one continuous turn
- Each iteration produces **2 exchanges** by two DIFFERENT personas
- Genuinely inhabit each persona: they must disagree, challenge, and stress-test each other — do NOT let the discussion become an echo chamber where every persona agrees
- Converging before `MIN_EXCHANGES` is a FAILURE — keep the discussion going even if it feels converged early; use Prof. Rex / Prof. Pax to surface objections
- If `MAX_EXCHANGES` reached without convergence: force convergence (Section F) and proceed

### 3.3. Self-Play Dynamics

Without an external counterpart, adversarial pressure must come from persona discipline:

| Persona | Adversarial duty in self-play |
|---------|------------------------------|
| 🔬 Prof. Vera | Attack unfalsifiable or vague claims; demand testable form |
| ⚙️ Prof. Pax | Attack infeasible compute/data/implementation assumptions |
| 🔍 Prof. Rex | Actively try to BREAK the current hypothesis each time he speaks |
| 🔭 Dr. Nova | Push past incremental ideas; propose alternatives |
| 🎯 Dr. Sage | Challenge significance — "who cares if this is true?" |
| 🛡️ Dr. Ally | Synthesize ONLY what survived the attacks |

**Response rules for every exchange:**
1. **Read** the previous exchanges carefully — identify claims, arguments, and gaps
2. **Load** the persona's full definition from `personas.yaml`
3. **React** authentically: agree, disagree, build upon, or challenge specific prior points
4. **Reference** other personas by name when responding to their arguments
5. **Stay in character**: use the assigned persona's communication style and principles

### 3.5. Paper Reference (Self-Assigned)

Step 0 created `{research_folder}/paper_summaries/*_summary.md` (P1 = first file alphabetically, P2 = second, etc.).

**When writing an exchange with an assigned paper reference:**

1. Read the summary file for the assigned paper
2. Find the assigned `### Section` headers (e.g. `### Methodology`, `### Experiments & Results`)
3. Incorporate the section content into your persona response
4. Cite findings using `[Author et al., Year]` format

**Rotation rule:** across the whole discussion, every prepared paper must be referenced at least once, and grounding claims in paper evidence is preferred over unsupported speculation.

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

### 5. Convergence Detection (Self-Judged)

Claude checks these criteria ITSELF (once exchange count >= `min_exchanges` from `phase2a_config.yaml`). Every check must be recorded in `01_round_table/convergence_checks.md` with per-criterion evidence (exchange numbers).

> **Authoritative Source:** Exchange count thresholds are defined in `scripts/phase2a_config.yaml` under `discussion.min_exchanges` and `discussion.max_exchanges`.

- [ ] **SPECIFIC**: Clear core claim stated?
- [ ] **MECHANISM**: How it works explained?
- [ ] **PREDICTIONS**: 2-3 testable predictions with criteria?
- [ ] **NOVELTY**: What's new articulated?
- [ ] **FEASIBILITY**: Implementation realistic?
- [ ] **OBJECTIONS**: Major criticisms addressed?

Convergence additionally requires that **all 6 personas have spoken at least once**.

**Anti-leniency rule:** a criterion passes only if you can point to a concrete exchange where it is satisfied. When in doubt, mark FAIL and continue the discussion — premature convergence produces weak hypotheses that fail Phase 4.

### 6. Write Final Assessments

When convergence is reached (loop exits), append the Final Assessments section to `discussion_log.md`.

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
    message="Discussion converged (self-judged), starting result structuring"
)

print(f"""
✅ Step 1 Complete (Discussion — Self-Play)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 2A-0: Gap Selection [done] ✓
• 2A-P: Paper Preparation [done] ✓
• 2A-1: Free Discussion [done] ✓ ({exchange_count} exchanges, self-play)
• 2A-2: Result Structuring [doing] ← CURRENT
• 2A-3: Advocate-Critic Refine. [todo]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Proceeding to Step 2 (Result Structuring)
""")

# Proceed to Step 2
Read("{nextStepFile}")
```

---

## SELF-PLAY FLOW

```
┌──────────────────────────────────────────────────────────────┐
│ MAIN SESSION (INLINE — no external LLM)                      │
│                                                              │
│ [Step 1 Start]                                               │
│        │                                                     │
│        ▼                                                     │
│ Write Exchange 1 (Dr. Nova — by Claude)                      │
│        │                                                     │
│        ▼                                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │              SELF-PLAY LOOP (per iteration)             │ │
│ │                                                         │ │
│ │  A. Claude selects 2 personas (coverage-based)          │ │
│ │  B. Claude assigns paper references (rotation)          │ │
│ │  C. Claude writes Exchange N   (as persona A)           │ │
│ │  D. Claude writes Exchange N+1 (as persona B, reacts)   │ │
│ │  E. exchange_count >= min_exchanges?                    │ │
│ │       → self-check 6 criteria                           │ │
│ │       → record in convergence_checks.md                 │ │
│ │       → ALL PASS + all personas spoke ──► BREAK         │ │
│ │  F. exchange_count >= max_exchanges ──► FORCE + BREAK   │ │
│ │       │                                                 │ │
│ │       └──────── LOOP ──────────────────────────────────┘ │
│ └─────────────────────────────────────────────────────────┘ │
│        │                                                     │
│        ▼                                                     │
│ Write Final Assessments                                      │
│        │                                                     │
│        ▼                                                     │
│ Update Archon Tasks → Proceed to Step 2                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## SUCCESS/FAILURE METRICS

### SUCCESS
- Discussion ran INLINE in a single turn with the Self-Play Loop (no external LLM, no `orchestrate_exchange.py` call)
- Exchange count reached `min_exchanges` from `scripts/phase2a_config.yaml` before convergence
- `discussion_log.md` contains the complete transcript
- All 6 personas participated at least once, with genuine disagreement/challenge across exchanges
- Every convergence self-check recorded in `01_round_table/convergence_checks.md` with per-criterion evidence
- Final Assessments section written with persona verdicts and consensus hypothesis
- Archon task transitions executed (2A-1 → done, 2A-2 → doing)

### FAILURE
- Calling `orchestrate_exchange.py` or any external LLM (ablation violation)
- Converged before `min_exchanges` reached
- Missing Final Assessments section
- Any persona never spoke
- `discussion_log.md` not updated
- No convergence checks recorded in `convergence_checks.md`
- Echo-chamber discussion (no persona ever disagreed or challenged)
- Archon tasks not updated
- Loop reached MAX_LOOP_ITERATIONS without convergence or forced convergence
