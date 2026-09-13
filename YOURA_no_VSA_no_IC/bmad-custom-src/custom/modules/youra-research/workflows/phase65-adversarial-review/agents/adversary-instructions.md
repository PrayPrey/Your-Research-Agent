# Adversary Agent - Execution Instructions

> **Config:** See `adversary-agent.yaml` for full configuration
> **Personas:** See `personas/*.yaml` for individual persona definitions

---

## On Spawn

You receive:
1. `paper_file` - Paper to review
2. `ground_truth_file` - `065_ground_truth.yaml` (actual values)
3. `round` - Current round (R1, R2, R3)
4. `output_file` - Where to write review
5. Optional: `sections_folder`, `narrative_blueprint`, `previous_review`

---

## Execution Flow

```yaml
1. Read ground_truth_file FIRST (know actual facts)
2. Read paper completely with critical eye
3. Apply ACTIVE personas for this round (see adversary-agent.yaml)
4. Write comprehensive review to output_file
5. Return summary to orchestrator
```

---

## Round-Persona Mapping

| Round | Active Personas |
|-------|-----------------|
| R1 | accuracy_checker, bored_reviewer, skeptical_expert |
| R2 | accuracy_checker, skeptical_expert |
| R3 | bored_reviewer |

---

## Output Structure

```markdown
# Adversarial Review - Round {N}

**Paper:** {title}
**Reviewed:** {ISO8601}

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | {N} | {N} | {status} |
| Engagement | {N} | {N} | {status} |
| Credibility | {N} | {N} | {status} |

**Recommendation:** {MAJOR_REVISION | MINOR_REVISION | CONDITIONAL_ACCEPT}

---

## Part 1: Accuracy Check
{accuracy_checker output - see persona file}

## Part 2: Engagement Check
{bored_reviewer output - see persona file}

## Part 3: Credibility Check
{skeptical_expert output - see persona file}

## Part 4: Human Review Notes
| Location | Note | Type |
|----------|------|------|

## Summary for Revision Agent
1. **FATAL-{ID}:** {brief} - MUST FIX
2. **MAJOR-{ID}:** {brief} - SHOULD FIX
```

---

## Return Schema

```yaml
agent: "adversary"
round: "{N}"
status: "COMPLETED"
output_file: "{path}"
summary:
  accuracy: { fatal: N, major: N }
  engagement: { fatal: N, major: N, would_continue_reading: bool }
  credibility: { fatal: N, major: N }
  totals: { fatal: N, major: N }
  human_review_notes_count: N
  recommendation: "{MAJOR_REVISION | MINOR_REVISION | CONDITIONAL_ACCEPT}"
```
