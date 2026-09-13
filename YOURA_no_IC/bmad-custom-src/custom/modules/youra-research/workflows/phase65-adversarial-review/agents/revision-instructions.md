# Revision Agent - Execution Instructions

> **Config:** See `revision-agent.yaml` for full configuration

---

## On Spawn

You receive:
1. `paper_file` - Paper to revise
2. `review_file` - Adversary's review
3. `round` - Current round (R1, R2, R3)
4. `output_file` - Where to write revised paper
5. `changelog_file` - Where to append changes

---

## Execution Flow

```yaml
1. Read paper completely
2. Read adversary review completely
3. Triage each issue (ACCEPT / PARTIAL / REJECT)
4. Fix issues in priority order (FATAL first, then MAJOR)
5. Coherence check - no new contradictions
6. Write revised paper to output_file
7. Append changes to changelog_file
8. Return summary to orchestrator
```

---

## Triage Decision Guide

| Decision | When | Action |
|----------|------|--------|
| **ACCEPT** | Adversary is correct | Fix as suggested |
| **PARTIAL** | Valid concern, different fix | Fix our way, document why |
| **REJECT** | Adversary misunderstood | Add clarification anyway |

---

## Changelog Format

```markdown
# Revision Log - Round {N}

**Date**: {ISO8601}
**Input Paper**: {input_file}
**Review File**: {review_file}
**Output Paper**: {output_file}

---

## FATAL Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|

## MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|

## Sections Modified

- Section X.Y: {change description}

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
```

---

## Return Schema

```yaml
agent: "revision"
round: "{N}"
status: "COMPLETED"
output_file: "{path}"
changelog_file: "{path}"
summary:
  issues_received: { fatal: N, major: N }
  issues_addressed: { accepted: N, partially_accepted: N, rejected: N }
  sections_modified: ["Section X.Y", ...]
  word_count_delta: +/-N
  remaining_concerns: ["..."]
```
