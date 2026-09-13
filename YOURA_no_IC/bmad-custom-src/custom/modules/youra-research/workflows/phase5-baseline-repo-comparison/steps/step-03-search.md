---
name: 'step-03-search'
description: 'Search for baseline candidate repositories on GitHub'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# File References
thisStepFile: '{workflow_path}/steps/step-03-search.md'
prevStepFile: '{workflow_path}/steps/step-02-define.md'
nextStepFile: '{workflow_path}/steps/step-04-evaluate.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointFile: '{baseline_folder}/05_baseline_checkpoint.yaml'

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 3: Search for Baseline Repositories

## STEP GOAL:

Use Exa MCP to search for suitable baseline candidate repositories based on the search queries defined in Step 2.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus ONLY on searching and collecting repository candidates
- 🚫 FORBIDDEN to evaluate or score repositories (that's Step 4)
- 💬 Execute all search queries from comparison_plan.md
- 🔍 Validate and deduplicate results

## EXECUTION PROTOCOLS:

- 🎯 Load search queries from comparison_plan.md
- 💾 Save repo_candidates.md with all candidates
- 📖 Use Exa MCP for GitHub-specific searches
- 🚫 FORBIDDEN to proceed with less than 3 candidates

## CONTEXT BOUNDARIES:

- Available context: comparison_plan.md, checkpoint
- Focus: Repository search and collection only
- Limits: Do not evaluate or score repositories
- Dependencies: Step 2 must be completed with search queries

---

---

## 3.1 Load Search Queries

Load search queries from comparison_plan.md generated in Step 2.

---

## 3.2 Execute Exa Search

For each search query, use Exa MCP to search:

### Search Parameters

| Parameter | Value |
|-----------|-------|
| Tool | `mcp__exa__web_search_exa` |
| Query suffix | "site:github.com" |
| Results per query | 5 |
| Type | "auto" |

### Deduplicate Results

After collecting all results, deduplicate by URL.

---

## 3.3 Validate GitHub URLs

For each candidate:

1. **Parse URL** - Extract owner and repo name
2. **Clean URL** - Remove .git suffix and trailing slashes
3. **Filter invalid URLs** - Exclude /issues, /pulls, /wiki, /releases pages

---

## 3.4 Fetch Repository Metadata

Use gh CLI to get repository information:

### Command

```bash
gh repo view {owner}/{repo} --json name,description,stargazersCount,pushedAt,primaryLanguage,isArchived
```

### Load Config from Checkpoint

```python
# Load config from checkpoint (Single Source of Truth: workflow.yaml)
checkpoint = read_yaml(checkpoint_file)
wf_config = checkpoint.get("workflow_config", {})
min_stars = wf_config["comparison"]["min_stars"]
recent_activity_months = wf_config["comparison"]["recent_activity_months"]
```

### Filter Criteria

| Criteria | Threshold | Action |
|----------|-----------|--------|
| Archived | true | Skip |
| Stars | < {min_stars} | Skip |
| Last updated | > {recent_activity_months} months ago | Skip |
| Language | Not Python | Warning |

---

## 3.5 Quick Content Check

Check each repository for key files:

| File | Indicates |
|------|-----------|
| train.py | Training script exists |
| model.py | Model definition exists |
| requirements.txt | Dependencies defined |
| README.md | Documentation exists |
| config* | Configuration exists |

Calculate file score: (files found) / (total files checked)

---

## 3.6 Generate repo_candidates.md

Create `{baseline_folder}/repo_candidates.md`:

```markdown
# Baseline Repository Candidates

## Search Summary
- **Queries Executed:** {count}
- **Raw Results:** {count}
- **Validated Repositories:** {count}
- **Search Date:** {timestamp}

---

## Candidate List

### 1. {repo_name}

| Field | Value |
|-------|-------|
| **URL** | {url} |
| **Owner** | {owner} |
| **Stars** | {stars} |
| **Language** | {language} |
| **Last Updated** | {date} |
| **Description** | {description} |

**Key Files Found:**
- train.py: {yes/no}
- model.py: {yes/no}
- requirements.txt: {yes/no}
- config: {yes/no}

**Source Query:** {query}

---

{repeat for each candidate}

## Next Step
Step 4: Evaluate and score each candidate
```

---

## 3.7 Update Checkpoint

```yaml
current_step: 4
search:
  candidates_found: {count}
updated_at: "{timestamp}"
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Exa search fails | Retry with simpler query |
| gh CLI not authenticated | STOP with auth instructions |
| No candidates found | Expand search queries, retry |
| All repos filtered out | Lower minimum stars threshold |

---

## Step Completion Criteria

- [ ] Search executed successfully
- [ ] At least 3 candidates found
- [ ] repo_candidates.md saved
- [ ] Checkpoint updated

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN repo_candidates.md is saved with at least 3 candidates and checkpoint is updated, will you then immediately load, read entire file, then execute `{workflow_path}/steps/step-04-evaluate.md` to begin candidate evaluation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- All search queries from comparison_plan.md executed
- Exa MCP used with site:github.com suffix
- Results deduplicated by URL
- GitHub URLs validated and filtered
- Repository metadata fetched via gh CLI
- At least 3 valid candidates collected
- repo_candidates.md saved with full details
- Checkpoint updated with candidates_found count

### ❌ SYSTEM FAILURE:
- Proceeding without loading comparison_plan.md
- Not executing actual Exa searches
- Accepting less than 3 candidates without expanding search
- Not validating GitHub URLs
- Not saving repo_candidates.md
- Not updating checkpoint

---

**Next Step:** Load and execute `step-04-evaluate.md`
