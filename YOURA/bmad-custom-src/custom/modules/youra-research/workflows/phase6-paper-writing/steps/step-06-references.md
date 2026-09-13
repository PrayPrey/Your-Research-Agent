---
name: 'step-06-references'
description: 'Compile all citations, verify with Semantic Scholar MCP, generate BibTeX'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase6-paper-writing'

# File References
thisStepFile: '{workflow_path}/steps/step-06-references.md'
nextStepFile: '{workflow_path}/steps/step-07-finalize.md'
workflowFile: '{workflow_path}/workflow.md'
---

# Step 06: Compile and Verify References

> **Step Position:** Step 5 (Closure) -> **[Step 6: References]** -> Step 7: Finalize
> **Purpose:** Compile all citations, verify with Semantic Scholar MCP, generate BibTeX
> **MCP Required:** Semantic Scholar

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:

- 🎯 Focus only on compiling citations, verifying with MCP, generating BibTeX
- 🚫 FORBIDDEN to include unverified citations without marking as [UNVERIFIED]
- 💬 Approach: Systematic verification with Semantic Scholar MCP
- 📋 Ensure all citation keys follow format: {FirstAuthorLastName}{Year}{FirstWord}

## EXECUTION PROTOCOLS:

- 🎯 Extract all citations from all section files (00-07)
- 💾 Verify each citation using Semantic Scholar MCP
- 📖 Generate BibTeX entries with proper formatting
- 🚫 FORBIDDEN to skip verification step for any citation

## CONTEXT BOUNDARIES:

- Available context: All section files (00_abstract.md through 07_conclusion.md)
- Focus: Citation compilation, verification, BibTeX generation
- Limits: Reference formatting only, no content changes
- Dependencies: Completed Story Group C (Step 5)

---

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. References Requirements (ICML 2025)

| Requirement | Specification |
|-------------|---------------|
| Format | BibTeX |
| Page Limit | Unlimited (not counted in 8 pages) |
| Style | ICML citation style |
| Verification | Recommended for accuracy |

---

## 2. References Workflow

```
┌─────────────────────────────────────┐
│ 1. Extract all citations from sections │
│ ↓                            │
│ 2. Verify each with Scholar MCP │
│ ↓                            │
│ 3. Generate BibTeX entries │
│ ↓                            │
│ 4. Create 06_references.bib │
└─────────────────────────────────────┘
```

---

## 3. Extract Citations from Sections

### 3.1 Read Section Files

Read all section files and extract all citations:

- `{sections_folder}/01_introduction.md`
- `{sections_folder}/02_related_work.md`
- `{sections_folder}/03_methodology.md`
- `{sections_folder}/04_experiments.md`
- `{sections_folder}/05_results.md`
- `{sections_folder}/06_discussion.md`

Citation formats to extract:
- Format: `[Author et al., Year]` or `[Author & Author, Year]`
- Placeholder format: `[CITE:topic_or_title]`

### 3.2 Create Citation List

```yaml
citations_to_verify:
  - inline: "[Smith et al., 2023]"
    search_query: "Smith 2023"
    context: "related_work"

  - inline: "[CITE:attention_is_all_you_need]"
    search_query: "Attention Is All You Need"
    context: "introduction"
```

---

## 4. Verify Citations with Semantic Scholar

### 4.1 For Each Citation

Use Semantic Scholar MCP to verify:

```
mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_title_search(
  query="{paper_title}",
  fields=["paperId", "title", "authors", "year", "venue", "citationCount", "externalIds"]
)
```

### 4.2 Verification Outcomes

| Outcome | Description | Action |
|---------|-------------|--------|
| **VERIFIED** | Exact or close match found | Use Scholar metadata |
| **PARTIAL** | Found but details differ | Use Scholar data with note |
| **UNVERIFIED** | Not found in Scholar | Keep original, mark unverified |

### 4.3 Get Full Paper Details

For verified papers:

```
mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_details(
  paper_id="{paperId}",
  fields=["paperId", "title", "authors", "year", "venue", "journal", "volume", "pages", "doi", "url"]
)
```

---

## 5. Generate BibTeX Entries

### 5.1 Citation Key Format

```
{FirstAuthorLastName}{Year}{FirstSignificantWord}
```

Examples:
- `Vaswani2017Attention`
- `Devlin2019BERT`
- `Brown2020Language`

### 5.2 BibTeX Templates

**Conference Paper:**
```bibtex
@inproceedings{Key,
  author = {Author1, First and Author2, First and Author3, First},
  title = {Paper Title},
  booktitle = {Proceedings of Conference Name},
  year = {2023},
  pages = {1--10},
  doi = {10.xxxx/xxxxx}
}
```

**Journal Article:**
```bibtex
@article{Key,
  author = {Author1, First and Author2, First},
  title = {Paper Title},
  journal = {Journal Name},
  year = {2023},
  volume = {XX},
  number = {X},
  pages = {1--10},
  doi = {10.xxxx/xxxxx}
}
```

**arXiv Preprint:**
```bibtex
@article{Key,
  author = {Author1, First and Author2, First},
  title = {Paper Title},
  journal = {arXiv preprint arXiv:XXXX.XXXXX},
  year = {2023}
}
```

---

## 6. Create References File

### 6.1 Write BibTeX File

Create `{output_folder}/06_references.bib`:

```bibtex
% References for: {Paper Title}
% Generated by Anonymous Research Pipeline
% Verification Rate: {X}%

@inproceedings{Vaswani2017Attention,
  author = {Vaswani, Ashish and Shazeer, Noam and ...},
  title = {Attention Is All You Need},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2017}
}

% ... more entries sorted alphabetically by key
```

### 6.2 Sort Entries

Sort all entries alphabetically by citation key.

---

## 7. Handle Unverified Citations

For each unverified citation:

1. **Try alternative search**: Different author order, year
2. **Check arXiv**: May be preprint only
3. **Mark in paper**: Add footnote if needed
4. **Log for review**: Flag for manual verification

---

## 8. Verification Summary

Create summary in checkpoint:

```yaml
citation_verification:
  total: {count}
  verified: {count}
  partial: {count}
  unverified: {count}
  verification_rate: {percentage}%

  unverified_list:
    - inline: "[Smith et al., 2023]"
      reason: "Not found in Semantic Scholar"
```

---

## 9. Update Checkpoint

Update `06_paper_checkpoint.yaml`:

```yaml
current_step: 7
citations_count: {total}
citations_verified: {verified}
citations_partial: {partial}
citations_unverified: {unverified}
verification_rate: {percentage}

updated_at: "{ISO8601}"
```

---

## 10. Proceed to Next Step

**NEXT:** Load, read the full file, and then execute `{nextStepFile}`

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All citations extracted from section files
- Each citation verified with Semantic Scholar MCP
- BibTeX entries generated with proper formatting
- Citation keys follow standard format
- 06_references.bib file created with sorted entries
- Verification summary logged in checkpoint
- Unverified citations marked appropriately

### ❌ SYSTEM FAILURE:

- Including citations without MCP verification attempt
- Missing BibTeX file creation
- Incorrect citation key format
- Not logging verification status for each citation
- Skipping alternative search for unverified citations
- Not updating checkpoint with citation statistics

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
