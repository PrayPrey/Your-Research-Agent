# Phase 0 Brainstorm - Validation Checklist

## Step Execution Tracking

### Step 0: Initialize
- [ ] Output file existence checked (auto-resume detection)
- [ ] Resume point determined (if existing file found)
- [ ] Serena Memory checked: ALL failure-related files read (phase5_failure_*, failure_*, pivot_*, limitation_*)
- [ ] Previous brainstorm searched (for ROUTE_TO_0 case)
- [ ] **Archive Verification (Section 0.3.5):**
  - [ ] If failure context exists: _archive/ folder checked
  - [ ] If archive missing: Late recovery executed
  - [ ] Archive marker file created (if late recovery)
  - [ ] If previous Pipeline not [FAILED]: Archon Pipeline terminate late recovery executed
- [ ] Auto-fill mode detection (UNATTENDED triggers checked)
- [ ] If UNATTENDED + ROUTE_TO_0: New brainstorm generated with lessons from failures
- [ ] If UNATTENDED: Auto-fill executed and workflow completed
- [ ] Output directory created
- [ ] Template copied to output file

### Step 1: Session Setup
- [ ] User greeted and initial interest captured
- [ ] Starting point assessed (Vague/General/Specific/Near-Ready)
- [ ] Context gathered (papers, problem, timeline)
- [ ] Failure context integrated (if previous failure exists)
- [ ] Archon Pipeline Project created (if not in Step 0)
- [ ] File write: `initial_interest`, `existing_context` saved

### Step 2: Exploration Approach
- [ ] Approach options presented (1-4)
- [ ] User selection captured
- [ ] Session plan configured based on selection
- [ ] File write: `approach_selection`, `session_plan` saved

### Step 3: Execute Techniques
- [ ] Selected techniques executed with facilitation
- [ ] Energy checkpoints performed
- [ ] Key insights documented throughout
- [ ] File write: `technique_sessions` saved

### Step 4: Synthesize Research Question
- [ ] Transition check completed
- [ ] Initial question articulated
- [ ] Question sharpened (specific, context, measurable)
- [ ] Failure context validation (if applicable)
- [ ] Detailed sub-questions generated (optional)
- [ ] File write: `main_research_question`, `refined_question`, `detailed_questions` saved

### Step 5: Reference Papers
- [ ] Reference papers requested
- [ ] Relevance notes collected (if papers provided)
- [ ] File write: `reference_papers` saved

### Step 6: Validation
- [ ] Current state displayed for review
- [ ] So What Test completed
- [ ] Feasibility Check completed
- [ ] Failure context final check (if applicable)
- [ ] File write: `so_what_validation`, `feasibility_validation` saved

### Step 7: Complete Session
- [ ] Phase 1 Input Package generated
- [ ] Session summary compiled
- [ ] Archon Pipeline Task updated (Phase 0 → done, Phase 1 → doing)
- [ ] File write: ALL remaining placeholders filled (including `pipeline_project_title`)

---

## Interactive Discovery Mode (NEW)

> **Note:** This section applies ONLY to Discovery Mode execution path.
> Standard Mode uses Step 1-3 above. UNATTENDED Mode uses Step 0 only.

### Step 0: Initialize (Same as Standard Mode)
- [ ] Interactive Mode Router executed (Section 0.7)
- [ ] User selected Discovery Mode [D]
- [ ] Route to step-01-interactive-discovery.md configured

### Step 1-D: Interactive Discovery
- [ ] High-energy opening with user control commands introduced
- [ ] 20-30 research angles generated collaboratively
- [ ] Anti-bias domain pivots performed (CRITICAL):
  - [ ] Domain pivot after angle #5
  - [ ] Domain pivot after angle #10
  - [ ] Domain pivot after angle #15
  - [ ] Domain pivot after angle #20
  - [ ] Domain pivot after angle #25 (if applicable)
- [ ] IDEA FORMAT used for all angles:
  - [ ] Domain Category specified for each angle
  - [ ] Mnemonic Title provided
  - [ ] Concept description (2-3 sentences)
  - [ ] Novelty explained
  - [ ] Why Interesting captured
- [ ] YES AND facilitation demonstrated:
  - [ ] AI built on user ideas (not just prompting)
  - [ ] Wild extensions offered
  - [ ] Provocative connections made
- [ ] User control commands supported:
  - [ ] "different angle" → immediate domain pivot
  - [ ] "go deeper" → deep dive on current angle
  - [ ] "next technique" → route to step-02
  - [ ] "I'm ready" → route to step-03
- [ ] Energy checkpoints conducted (every 8-10 exchanges)
- [ ] Discovery Journey Narrative documented:
  - [ ] Exploration path tracked (angles 1-5, 6-10, etc.)
  - [ ] Domain pivots recorded
  - [ ] User energy patterns noted
  - [ ] Breakthrough moments identified
- [ ] File write: All angles saved in IDEA FORMAT
- [ ] Total angles generated: [X] (minimum 20 expected)

### Step 2-D: Interactive Exploration (OPTIONAL)
- [ ] User chose Exploration phase (not skipped to synthesis)
- [ ] Welcome with context from step-01 angles
- [ ] Flow-based technique selection offered:
  - [ ] [R] Recommend based on angles
  - [ ] [C] Choose from menu
  - [ ] [S] Skip to synthesis
- [ ] If technique selected:
  - [ ] Technique loaded from research-methods.csv
  - [ ] TRUE interactive facilitation (not script execution)
  - [ ] YES AND approach throughout
  - [ ] AI contributions to exploration (not just prompts)
  - [ ] Energy checkpoints every 4-5 exchanges
  - [ ] "next technique" command supported anytime
  - [ ] User controls pacing (can skip or extend)
- [ ] Technique insights documented:
  - [ ] Key discoveries captured
  - [ ] Connections to angles identified
  - [ ] User's creative patterns noted
- [ ] File write: Exploration insights saved
- [ ] Route decision made (more exploration or synthesis)

### Step 3-D: Interactive Synthesis
- [ ] All [X] research angles reviewed
- [ ] Discovery Journey Narrative loaded from step-01
- [ ] Exploration insights loaded from step-02 (if applicable)
- [ ] 3-5 themes identified from angles
- [ ] Collaborative convergence executed (NOT imposing):
  - [ ] User's theme preference solicited
  - [ ] Draft question built on user preference
  - [ ] Multiple refinement rounds offered
  - [ ] User's synthesis preferences incorporated
  - [ ] YES AND approach maintained
- [ ] Iterative refinement conducted:
  - [ ] At least 2 refinement rounds completed
  - [ ] User satisfaction verified before finalizing
  - [ ] Question reflects user's passion
- [ ] Journey-to-question narrative created:
  - [ ] Starting point documented
  - [ ] Discovery path summarized
  - [ ] Exploration insights integrated (if applicable)
  - [ ] Synthesis process explained
  - [ ] Breakthrough moments celebrated
- [ ] Question power explained:
  - [ ] Novelty articulated
  - [ ] Feasibility assessed
  - [ ] Impact described
  - [ ] User passion captured
- [ ] File write: Synthesis results and journey narrative saved
- [ ] Route to step-04-synthesize.md (shared with Standard Mode)

### Discovery Mode Quality Metrics
- [ ] Total research angles: ≥20 (target: 20-30)
- [ ] Domain diversity: ≥5 different domains explored
- [ ] Anti-bias pivots: Documented in journey narrative
- [ ] User energy: High engagement maintained throughout
- [ ] Collaborative feel: TRUE partnership (not form-filling)
- [ ] Final question: Emerged from dialogue (not imposed)

---

## Research Question Quality

- [ ] Question is specific enough to investigate
- [ ] Question addresses a clear problem or gap
- [ ] Question is feasible to answer
- [ ] "So What" test passed (significance established)
- [ ] Failure context addressed (if routing from Phase 4/5)

---

## Output Completeness

### Required Outputs
- [ ] `initial_interest` - User's starting research interest
- [ ] `approach_selection` - Selected exploration approach
- [ ] `session_plan` - Planned technique sequence
- [ ] `main_research_question` - Initial question formulation
- [ ] `refined_question` - Sharpened research question

### Optional Outputs (if provided)
- [ ] `detailed_questions` - Sub-questions for deeper investigation
- [ ] `reference_papers` - Starting papers for Phase 1
- [ ] `technique_sessions` - Technique execution records
- [ ] `lessons_from_previous_attempts` - ROUTE_TO_0 context (what failed, why, new direction)

### Validation Results
- [ ] `so_what_validation` - Significance response
- [ ] `feasibility_validation` - Feasibility assessment

### Session Insights
- [ ] `key_insights` - Key discoveries from session
- [ ] `techniques_used` - List of techniques applied
- [ ] `areas_for_exploration` - Promising directions for future
- [ ] `session_duration` - Actual session time recorded
- [ ] `next_steps` - Clear guidance for proceeding

---

## Phase 1 Input Package

- [ ] `phase1_research_question` - Ready for Phase 1 investigation
- [ ] `phase1_detailed_question` - Supporting sub-questions (or marked as not provided)
- [ ] `phase1_reference_papers` - Reference papers (or marked as not provided)

---

## Archon Pipeline Integration

- [ ] Pipeline Project created: `Anonymous Pipeline: {initial_interest_summary}`
- [ ] `pipeline_project_title` recorded in output file
- [ ] 11 Phase Tasks created (Phase 0-6.5)
- [ ] Phase 0 Task status: `doing` → `done`
- [ ] Phase 1 Task status: `todo` → `doing`

---

## Failure Context Recovery (If Routing from Phase 4/5)

- [ ] Serena Memory: ALL failure-related files read (not just latest)
- [ ] Previous brainstorm found in research_folder (including _archive/)
- [ ] Failure source identified (Phase 4 FAIL / Phase 4 PARTIAL / Phase 5 PARTIAL)
- [ ] Complete failure history analyzed (multiple files = multiple lessons)
- [ ] `what_not_to_do` extracted from all failure records
- [ ] Previous brainstorm direction reviewed
- [ ] "Lessons from Previous Attempts" section generated
- [ ] New direction validated against ALL previous failures
- [ ] Final check confirms avoidance of previous pitfalls

---

## Auto-Fill Mode (UNATTENDED)

**Triggers:**
- [ ] `batch_mode: true` parameter
- [ ] `mode="unattended"` in invocation
- [ ] `#batch-mode` marker in input
- [ ] `research_idea_content` parameter present

**If Triggered:**
- [ ] Research components extracted from input
- [ ] Minimal output file generated
- [ ] Archon Pipeline created and updated
- [ ] Workflow completed (Steps 1-6 skipped)

---

## Validation Summary

**Total Checks:** 120+

**Execution Modes:**
- **Standard Mode:** Step 0-7 completion + Research Question Quality + Output Completeness
- **Discovery Mode:** Step 0 + Step 1-D/2-D/3-D + Discovery Quality Metrics + Step 4-7 (shared)
- **UNATTENDED Mode:** Auto-Fill execution + Archon Pipeline Integration

**Minimum Pass Criteria:**

**For Standard Mode:**
- All Step 0-7 execution checks completed
- Research question passes "So What" test
- Phase 1 Input Package complete
- Archon Pipeline updated (Phase 0 done, Phase 1 doing)

**For Discovery Mode:**
- Step 0 + Interactive Mode Router completed
- Step 1-D: 20-30 research angles with anti-bias pivots
- Step 2-D: Optional exploration (if selected)
- Step 3-D: Collaborative synthesis with journey narrative
- Discovery Mode Quality Metrics met
- Step 4-7: Shared synthesis/validation completed
- Research question passes "So What" test
- Phase 1 Input Package complete
- Archon Pipeline updated (Phase 0 done, Phase 1 doing)

**For UNATTENDED Mode:**
- Auto-Fill execution (Section 0.4.1 or 0.4.2)
- Phase 1 Input Package generated
- Archon Pipeline Integration completed

---

**Validation Completed:** {{date}}
**Validator:** Phase 0 Brainstorm Workflow (YouRA)
