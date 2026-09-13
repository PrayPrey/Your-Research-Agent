# Fix Phase 1 Output Workflow

**Purpose:** Automatically generate compact version (01_targeted_research.md) from full report (01_targeted_research_full.md)

**Trigger:** Called by post_step_validation when compact version is missing or invalid

**Mode:** UNATTENDED - No user interaction required

---

## EXECUTION CONTEXT

This workflow is invoked automatically when:
1. `01_targeted_research_full.md` exists
2. `01_targeted_research.md` is missing OR incorrectly formatted

**Input:** `{research_folder}/01_targeted_research_full.md`
**Output:** `{research_folder}/01_targeted_research.md`

---

## STEP 1: Read Full Report

```
Read: {research_folder}/01_targeted_research_full.md
```

Store the full content in memory for processing.

---

## STEP 2: Extract and Compress Sections

Transform full report to compact format following these rules:

### Section Transformations

| Full Report Section | Compact Version | Transformation |
|---------------------|-----------------|----------------|
| Executive Summary | Keep as-is | No change |
| 0. Reference Paper Analysis | Keep as-is | No change |
| 1. Research Questions | Keep as-is | No change |
| 2. Search Queries Generated | **Compress** | Keep only top 3 per category, add "(Sample)" |
| 3. Past Cases (Archon) | **Compress** | Summarize to key points, add "- Compact" |
| 4. Academic Literature (Scholar) | **Compress** | Summarize to key points, add "- Compact" |
| 5. Implementation Resources (Exa) | **Compress** | Summarize to key points, add "- Compact" |
| 6. Chain-of-Relations | **Compress** | Keep Cross-Reference Matrix, summarize others |
| 7. Verification Status | **REMOVE** | Not needed for Phase 2A |
| 8. Research Gaps | **Keep FULL** | Critical for Phase 2A - do not compress |
| 9. Conclusion | **Compress** | Keep Key Findings and Next Steps only |

### Compression Guidelines

**For Sections 2-6:**
- Keep only the most relevant 3-5 items per subsection
- Remove detailed descriptions, keep bullet points
- Preserve URLs, paper IDs, and GitHub links
- Add "Compact" suffix to section headers

**For Section 8 (Research Gaps):**
- **DO NOT COMPRESS** - This is the primary input for Phase 2A
- Keep all Gap details including:
  - Current State
  - Missing Piece
  - Potential Impact
  - All supporting evidence tables (SCHOLAR, ARCHON, EXA)
  - Gap Priority Matrix
  - User Input to Gap Traceability

---

## STEP 3: Generate Compact Report

Create `01_targeted_research.md` with the following structure:

```markdown
# Targeted Research Report: {research_topic}

**Generated:** {date}
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** {phase_output}
**Analyst:** Deep Learning Research Analyst
**Researcher:** {user_name}

---

## Executive Summary

{executive_summary}

---

## 0. Reference Paper Analysis

{reference_paper_analysis}

---

## 1. Research Questions

### Primary Research Question
{primary_research_question}

### Detailed Research Questions
{detailed_questions}

---

## 2. Search Queries Generated (Sample)

### Query Generation Source Summary
{query_summary}

### Priority 1: Reference Paper Concept Queries (Top 3)
{reference_queries_sample}

### Priority 2: Brainstorm Insights Queries (Top 3)
{brainstorm_queries_sample}

### Priority 3: Direct Question Decomposition Queries (Top 3)
{direct_queries_sample}

---

## 3. Past Cases & Best Practices (via Archon) - Compact

### Direct Implementations (Compact)
{archon_implementations_compact}

### Similar Architectural Patterns (Compact)
{archon_patterns_compact}

### Code Examples Found (Compact)
{archon_code_examples_compact}

---

## 4. Academic Literature Review (via Semantic Scholar) - Compact

### Directly Relevant Papers (Compact)
{scholar_relevant_papers_compact}

### Foundational Papers (Compact)
{scholar_foundational_papers_compact}

### Citation Network Analysis (Compact)
{scholar_citation_network_compact}

---

## 5. Implementation Resources (via Exa) - Compact

### Directly Relevant Implementations (Compact)
{exa_implementations_compact}

### Component Implementations (Compact)
{exa_components_compact}

### Tutorial Resources (Compact)
{exa_tutorials_compact}

### Code Analysis (Compact)
{exa_code_analysis_compact}

---

## 6. Chain-of-Relations Analysis - Compact

### Research Evolution Path (Compact)
{research_evolution_path_compact}

### Cross-Reference Matrix
{cross_reference_matrix}

---

## 8. Research Gaps

{full_section_8_from_original}

---

## 9. Conclusion - Compact

### Key Findings
{key_findings}

### Next Steps
{next_steps}

---

*Phase: 1 - Targeted Research Gathering (Phase 2A Input)*
*Total processing time: {processing_time}*
```

---

## STEP 4: Validate Output

Perform the following checks:

1. **File Size Check:** Compact < Full (should be 30-50% smaller)
2. **Section 8 Check:** "## 8. Research Gaps" must exist
3. **Gap Content Check:** At least one "#### Gap" subsection must exist

If any check fails:
- Log error
- Return failure status

---

## STEP 5: Complete

```
Log: Compact version generated successfully
Log: Full report size: {full_size} bytes
Log: Compact report size: {compact_size} bytes
Log: Compression ratio: {ratio}%
```

Return success status to caller.

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Full report not found | FAIL - Cannot proceed |
| Full report empty | FAIL - Cannot proceed |
| Section 8 extraction failed | FAIL - Critical section missing |
| Write failed | FAIL - Permission or disk issue |

On any FAIL:
- Log detailed error message
- Return failure status to post_step_validation
- post_step_validation will trigger notify_user fallback

---

## NOTES

- This workflow runs in UNATTENDED mode - no user prompts
- Section 8 (Research Gaps) is the most critical section for Phase 2A
- The compact version should be significantly smaller but preserve all gap information
- If compression is not possible, copy full report as compact (better than nothing)

---

*Part of Anonymous Research Pipeline*
*Auto-recovery for dual output system*
