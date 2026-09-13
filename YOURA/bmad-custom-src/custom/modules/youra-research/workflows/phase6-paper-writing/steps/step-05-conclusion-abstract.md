---
name: 'step-05-conclusion-abstract'
description: 'Generate Conclusion and Abstract - needs full narrative arc'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase6-paper-writing'

# File References
thisStepFile: '{workflow_path}/steps/step-05-conclusion-abstract.md'
nextStepFile: '{workflow_path}/steps/step-06-references.md'
workflowFile: '{workflow_path}/workflow.md'
narrativeBlueprint: '{paper_folder}/06_narrative_blueprint.yaml'
---

# Step 05: Story Group C - Closure Sections

> **Step Position:** ... -> Step 4 (Story Group B) -> **[Step 5: Closure]** -> Step 6: References
> **Purpose:** Generate Conclusion and Abstract that close the narrative loop
> **Context Isolation:** NO - Requires full paper context
> **Execution Mode:** Task Agent with full paper awareness
> **Outputs:** `07_conclusion.md`, `00_abstract.md`

---

## Why Conclusion and Abstract Are Generated LAST

**The Problem with Early Abstract/Conclusion:**
```
Old approach:
  Abstract → first (before knowing full story)
  Conclusion → generic summary

Result:
  ❌ Abstract doesn't capture actual results
  ❌ Conclusion doesn't connect back to hook
  ❌ No narrative closure
  ❌ Reader feels story is incomplete
```

**The Closure-Last Approach:**
```
New approach:
  [All other sections] → Conclusion → Abstract (LAST)

Result:
  ✅ Abstract accurately summarizes full paper
  ✅ Conclusion closes the narrative loop
  ✅ Callback to Introduction hook
  ✅ Reader feels satisfied story arc
```

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:

- 🎯 Read ALL previous sections before generating
- 🔄 Conclusion must callback to Introduction hook
- 💬 Abstract compresses the COMPLETE story
- 📋 No new information in Conclusion (synthesis only)
- 🚫 FORBIDDEN to generate Abstract without seeing full paper

---

## Prerequisites

Before executing this step:

1. Steps 01-04 completed successfully
2. Story Group A sections exist (01-03)
3. Story Group B sections exist (04-06)
4. `06_narrative_blueprint.yaml` exists

---

## Task Agent Spawn Instructions

```yaml
task_agent:
  type: "general-purpose"
  context_isolation: false # CRITICAL: Needs full paper context

  inputs_to_load:
    # Narrative design
    - "{paper_folder}/06_narrative_blueprint.yaml"

    # Phase 4.5: For future work directions and verified insight
    - "{research_folder}/045_validated_hypothesis.md"

    # ALL previous sections (for context)
    - "{sections_folder}/01_introduction.md"
    - "{sections_folder}/02_related_work.md"
    - "{sections_folder}/03_methodology.md"
    - "{sections_folder}/04_experiments.md"
    - "{sections_folder}/05_results.md"
    - "{sections_folder}/06_discussion.md"

  outputs_to_write:
    - "{sections_folder}/07_conclusion.md"
    - "{sections_folder}/00_abstract.md"
```

---

## Execution Sequence

### 1. Load Full Paper Context

**CRITICAL:** Must read ALL previous sections before generating.

```yaml
action: "Load complete paper context"
files_to_read:
  - "{paper_folder}/06_narrative_blueprint.yaml"
  - "{sections_folder}/01_introduction.md"
  - "{sections_folder}/02_related_work.md"
  - "{sections_folder}/03_methodology.md"
  - "{sections_folder}/04_experiments.md"
  - "{sections_folder}/05_results.md"
  - "{sections_folder}/06_discussion.md"
```

Extract key elements:
```yaml
from_blueprint:
  - hook.opening_statement (for callback)
  - key_insight.aha_moment
  - takeaway.main_contribution
  - section_goals.conclusion
  - section_goals.abstract

from_introduction:
  - opening_hook
  - problem_statement
  - contributions_list

from_results:
  - main_results_numbers
  - key_findings

from_discussion:
  - limitations_acknowledged
  - broader_impact
```

---

### 2. Generate Conclusion (07_conclusion.md)

Conclusion closes the narrative loop. It does NOT introduce new information.

#### 2.1 Callback to Introduction Hook

From `section_goals.conclusion.callback_to_hook`:

```markdown
## Conclusion

[Opening that connects back to Introduction hook]

Example structures:
- "We began by observing that [hook problem]. Our work shows that..."
- "The challenge of [hook problem] motivated us to develop..."
- "Returning to our initial question of [hook], we have demonstrated..."
```

**CRITICAL:** The reader should feel the story coming full circle.

#### 2.2 Summary of Contributions

Synthesize (not just repeat) the contributions:

```markdown
### Summary

In this work, we addressed [problem] by [key insight].

Our main contributions are:
1. [Contribution 1 - with concrete result]
2. [Contribution 2 - with concrete result]
3. [Contribution 3 - if applicable]
```

**Each contribution should reference actual results.**

#### 2.3 Future Work Vision

From `045_validated_hypothesis.md` **Section 7: Future Work**:

**NOT just "more experiments on more datasets" — every direction must trace to experiment evidence.**

Source future work from Phase 4.5 Section 7, which provides three grounded categories:

```markdown
### Future Directions

This work opens several promising directions:

**From Untested Alternative Explanations:**
[From 045_validated_hypothesis.md Section 7.1 — competing explanations that need testing]

**From Unverified Assumptions:**
[From 045_validated_hypothesis.md Section 7.2 — assumptions that need explicit verification]

**From Scope Extensions:**
[From 045_validated_hypothesis.md Section 7.3 — extending results to new settings]
```

**Critical:** Every future direction must reference what experiment result motivated it.

#### 2.4 Memorable Ending

From `section_goals.conclusion.memorable_ending`:

```markdown
[Final sentence that leaves lasting impression]

Examples:
- "Our findings suggest that [broader insight]..."
- "We hope this work encourages [future direction]..."
- "As [field] continues to evolve, [key message]..."
```

---

### 3. Generate Abstract (00_abstract.md)

Abstract is the compressed version of the ENTIRE paper. Generated LAST.

#### 3.1 Abstract Structure

From `section_goals.abstract`:

```markdown
## Abstract

[Sentence 1-2: Problem and its importance]
[Sentence 3: Our approach - key insight]
[Sentence 4-5: Main results - with numbers]
[Sentence 6: Significance/contribution]
```

**Target: ~150 words (4-6 sentences)**

#### 3.2 Abstract Writing Principle

**The Abstract is a STORY, not a data summary.**

Write as a researcher explaining your work to a colleague over coffee — lead with the problem, share the insight, mention the headline result, and convey why it matters. Numbers should appear only when they genuinely strengthen the narrative (e.g., one striking result that captures the main finding). If you find yourself listing metrics, thresholds, or statistical details, you have left storytelling mode and entered reporting mode. Step back and ask: "What is the ONE thing a reader should take away?"

#### 3.3 Abstract Generation Template

```markdown
[Problem statement with concrete impact].
[Why existing approaches are insufficient - one sentence].
In this paper, we propose [method name], which [key insight in one sentence].
[Brief description of how it works - optional, one sentence max].
Our experiments on [datasets] show that [main result - use a number only if it sharpens the point].
[One sentence on significance or broader impact].
```

#### 3.4 Abstract Quality Checklist

**MUST include:**
- [ ] Concrete problem statement
- [ ] Key insight (not just "we propose X")
- [ ] Main result (quantitative or qualitative — whichever tells the story better)
- [ ] Significance statement

**MUST avoid:**
- [ ] Citations in abstract
- [ ] Undefined acronyms
- [ ] "X is important" opening
- [ ] Enumerating metrics, thresholds, or statistical details — the Abstract is not a Results table

#### 3.5 Abstract Examples

**❌ BAD (too vague):**
```
Deep learning has achieved remarkable success in many domains.
However, challenges remain in certain areas. In this paper, we
propose a novel method to address these challenges. Our method
achieves good results on several benchmarks.
```

**❌ BAD (data dump disguised as abstract):**
```
We find 3 stable edges (|ρ| > 0.35, stability > 0.90) after
removing a capability confound explaining 88.2% of variance.
These survive isotropic (95th = 2.0) and heteroskedastic
(95th = 1.0) null models. Tucker's φ > 0.99 confirms
measurement invariance. Jaccard = 0.0 reveals taxonomy sensitivity.
```

**✅ GOOD (story with selective numbers):**
```
Neural networks trained on real-world data often rely on spurious
correlations, leading to significant accuracy drops on minority
groups. Existing mitigation methods require explicit group
annotations, limiting their applicability. We introduce [Method],
which automatically identifies and down-weights spurious patterns
by tracking sample learning dynamics during training. Our key
insight is that samples relying on spurious features are learned
faster than those requiring core features. Experiments on CelebA,
Waterbirds, and CivilComments show [Method] improves worst-group
accuracy by 12.3% over ERM while requiring no group labels,
providing a practical path toward more robust models without
additional annotation costs.
```

---

### 4. Verify Narrative Closure

After generating both sections:

#### 4.1 Narrative Loop Check

```yaml
verify:
  - "Conclusion callbacks to Introduction hook"
  - "Reader can see complete story arc"
  - "No loose ends or unanswered questions"
```

#### 4.2 Consistency Check

```yaml
verify:
  - "Abstract numbers match Results section exactly"
  - "Conclusion contributions match Introduction contributions"
  - "No contradictions with earlier sections"
```

#### 4.3 Completeness Check

```yaml
verify:
  - "Abstract captures: problem, insight, results, significance"
  - "Conclusion captures: summary, future work, memorable ending"
  - "Both sections reference actual results"
```

---

### 5. Write Section Files

**Note:** Abstract is numbered 00 to appear first in final paper.

```yaml
outputs:
  - file: "{sections_folder}/07_conclusion.md"
    content: "[Generated Conclusion]"

  - file: "{sections_folder}/00_abstract.md"
    content: "[Generated Abstract]"
```

---

### 6. Update Checkpoint

Update `06_paper_checkpoint.yaml`:

```yaml
current_step: 6
story_groups:
  group_a:
    status: "complete"
  group_b:
    status: "complete"
  group_c:
    status: "complete"
    sections:
      - conclusion: "complete"
      - abstract: "complete"
    completed_at: "{ISO8601}"

sections_completed:
  - "00_abstract"
  - "01_introduction"
  - "02_related_work"
  - "03_methodology"
  - "04_experiments"
  - "05_results"
  - "06_discussion"
  - "07_conclusion"

updated_at: "{ISO8601}"
```

---

### 7. Return to Orchestrator

```yaml
agent: "story-group-c"
status: "COMPLETED"
outputs:
  - "07_conclusion.md"
  - "00_abstract.md"

summary:
  conclusion:
    word_count: {N}
    callbacks_to_hook: true/false
    future_directions_count: {N}
    memorable_ending: true/false

  abstract:
    word_count: {N}
    sentence_count: {N}
    quantitative_results_included: true/false
    no_citations: true/false
    no_undefined_acronyms: true/false

narrative_closure:
  full_story_arc: true/false
  numbers_consistent: true/false
  no_loose_ends: true/false
```

---

### 8. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

---

## Output Summary

| Output | Path | Description |
|--------|------|-------------|
| Conclusion | `{sections_folder}/07_conclusion.md` | Narrative closure with future work |
| Abstract | `{sections_folder}/00_abstract.md` | Compressed full story (~150 words) |
| Updated Checkpoint | `{paper_folder}/06_paper_checkpoint.yaml` | All sections complete |

---

## 🚨 SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- ALL previous sections read before generating
- Conclusion callbacks to Introduction hook
- Abstract reads like a story a colleague would want to hear, not a metrics report
- No citations in abstract
- No undefined acronyms in abstract
- Future work is visionary (not just "more experiments")
- Any numbers in abstract match Results section exactly
- Narrative loop is closed (reader feels completion)

### ❌ SYSTEM FAILURE:

- Generating Abstract without reading full paper
- No callback to Introduction hook
- Abstract that reads like a results table (listing metrics, thresholds, p-values)
- Abstract so vague it says nothing concrete ("achieves good results")
- Citations in abstract
- Generic future work ("more experiments on more datasets")
- Numbers don't match Results section
- Story feels incomplete

**Master Rule:** These sections CLOSE the narrative. The Abstract compresses the full story. The Conclusion brings the reader back to where they started - but transformed by the journey.
