# Paper Preparation Guide

> Detailed documentation for Step 0 paper preparation process

---
bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue/scripts/prepare_papers.py
## Script Information
bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue/scripts
**Script Location:** `bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue/scripts/prepare_papers.py`

**Requirements:**
- Python 3.8+
- `markitdown` (Microsoft MarkItDown)
- `requests`
- `pyyaml`

**Usage (MUST use YouRA conda environment!):**
```bash
# MANDATORY: Proper conda activation sequence
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniforge3")
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate YouRA

# Run script
python bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue/scripts/prepare_papers.py \
    --config {research_folder}/paper_config.yaml \
    --output {research_folder}/papers/
```

⚠️ **WARNING:** Running without YouRA conda environment will fail (markitdown not installed globally)!

---

## Execution Steps

### Step 5.1: Create Paper Config from Phase 1 Data

**CRITICAL:** Use `arxiv_id` as PRIMARY identifier (not Semantic Scholar ID)

```python
paper_config = {
    "papers": []
}

FOR paper IN selected_gap.related_papers:
    # PRIORITY: Use arxiv_id for direct arXiv download
    # Fallback: Use Semantic Scholar ID with openAccessPdf

    IF paper.arxiv_id:
        paper_config["papers"].append({
            "id": paper.arxiv_id, # e.g., "2301.00001"
            "source": "arxiv", # PRIMARY source
            "title": paper.title,
            "semantic_scholar_id": paper.paper_id # backup reference
        })
    ELSE:
        paper_config["papers"].append({
            "id": paper.paper_id,
            "source": "semantic_scholar", # fallback source
            "title": paper.title
        })
        Log(f"WARNING: No arXiv ID for {paper.title} - using Semantic Scholar (may fail)")

# Write config file
config_path = f"{research_folder}/paper_config.yaml"
Write(config_path, yaml.dump(paper_config))
```

### Step 5.2: Run Paper Preparation Script

```python
script_path = "bmad-custom-src/custom/modules/youra-research/workflows/phase2a-dialogue/scripts/prepare_papers.py"

# MUST use YouRA virtual environment (conda) with proper activation!
# CRITICAL: source conda.sh BEFORE conda activate
Bash(f"""
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniforge3")
source "${{CONDA_BASE}}/etc/profile.d/conda.sh"
conda activate YouRA && python {script_path} --config {config_path} --output {research_folder}/papers/
""")
```

⚠️ **Common Mistake:** `conda activate YouRA` alone will FAIL without `source conda.sh` first!

### Step 5.3: Script Processing

Script will:
1. Download PDFs from arXiv (PRIMARY) or Semantic Scholar (fallback)
2. Convert to Markdown using MarkItDown
3. Extract content BEFORE References section
4. Save as `{paper_id}.md` in papers/ folder
5. Write `preparation_summary.json`

### Step 5.4: MANDATORY VALIDATION (MarkItDown Output Verification)

```python
papers_dir = Path(f"{research_folder}/papers/")
MIN_MD_SIZE_BYTES = 1000 # Minimum 1KB for valid conversion

validation_results = []
FOR paper IN paper_config["papers"]:
    paper_id = paper["id"]
    source = paper["source"]

    # Determine expected file names
    IF source == "arxiv":
        safe_id = re.sub(r'[^\w\-_]', '_', paper_id)
        pdf_name = f"arxiv_{safe_id}.pdf"
        md_name = f"arxiv_{safe_id}.md"
    ELSE:
        safe_id = re.sub(r'[^\w\-_]', '_', paper_id)[:50]
        pdf_name = f"{safe_id}.pdf"
        md_name = f"{safe_id}.md"

    pdf_path = papers_dir / pdf_name
    md_path = papers_dir / md_name

    # Validation checks
    validation = {
        "paper_id": paper_id,
        "pdf_exists": pdf_path.exists(),
        "md_exists": md_path.exists(),
        "md_size_bytes": md_path.stat().st_size if md_path.exists() else 0,
        "md_valid": False
    }

    # MD file must exist AND have minimum size
    IF validation["md_exists"] AND validation["md_size_bytes"] >= MIN_MD_SIZE_BYTES:
        validation["md_valid"] = True
        validation["status"] = "SUCCESS"
    ELIF validation["md_exists"]:
        validation["status"] = "CONVERSION_FAILED_EMPTY"
        Log(f"WARNING: MD file too small ({validation['md_size_bytes']} bytes): {paper_id}")
    ELIF validation["pdf_exists"]:
        validation["status"] = "CONVERSION_FAILED"
        Log(f"WARNING: PDF exists but MD not created: {paper_id}")
    ELSE:
        validation["status"] = "DOWNLOAD_FAILED"
        Log(f"WARNING: PDF download failed: {paper_id}")

    validation_results.append(validation)

# Summary
valid_papers = [v for v in validation_results if v["status"] == "SUCCESS"]
Log(f"Paper Validation: {len(valid_papers)}/{len(validation_results)} papers ready")

IF len(valid_papers) == 0:
    STOP("CRITICAL: No papers successfully prepared. Check paper_config and arXiv IDs.")
```

---

## Script Output Structure

```
{research_folder}/papers/
├── arxiv_{arxiv_id_1}.pdf # Original PDF (arXiv source)
├── arxiv_{arxiv_id_1}.md # Converted MD (before References)
├── arxiv_{arxiv_id_2}.pdf
├── arxiv_{arxiv_id_2}.md
└── preparation_summary.json # Processing summary
```

---

## Validation Criteria

| Check | Requirement | Failure Action |
|-------|-------------|----------------|
| PDF exists | File must exist | Mark as DOWNLOAD_FAILED |
| MD exists | File must exist | Mark as CONVERSION_FAILED |
| MD size | >= 1000 bytes | Mark as CONVERSION_FAILED_EMPTY |

---

## Troubleshooting

### IF Script Fails:
- Check `preparation_summary.json` for error details
- **Missing arXiv ID**: Phase 1 must include `arxiv_id` in paper references
- Some papers may not have Open Access PDFs from Semantic Scholar
- Continue with successfully converted papers (at least 1 required)

### Phase 1 Integration Note:
Phase 1 MUST save `arxiv_id` for each paper:
```yaml
# Phase 1 output format (01_targeted_research.md)
related_papers:
  - paper_id: "abc123def" # Semantic Scholar ID
    arxiv_id: "2301.00001" # REQUIRED for Phase 2A download
    title: "Paper Title"
```
