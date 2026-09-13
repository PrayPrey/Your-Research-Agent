---
name: "Phase 6.5.1: Overleaf LaTeX + PDF Generation"
description: "Convert final reviewed paper to Overleaf-compilable LaTeX project and compile to PDF"
version: "1.0"
web_bundle: false
---

# Phase 6.5.1: Overleaf LaTeX + PDF Generation

> **Pipeline Position:** Phase 6.5 (Adversarial Review) -> **[Phase 6.5.1: Overleaf + PDF]** -> Complete
> **Input:** `paper/06_paper_final.md` (from Phase 6.5)
> **Output:** `paper/overleaf/` (LaTeX project + compiled PDF)

**Goal:** Convert the final reviewed Markdown paper into an Overleaf-compilable LaTeX project following ICML 2025 format, then compile to PDF locally.

---

## Overview

```
06_paper_final.md ──┐
06_references.bib ──┤──→ [Phase 6.5.1] ──→ overleaf/
paper/figures/ ───┘ ├── main.tex
                                            ├── sections/*.tex (9 files)
                                            ├── figures/*
                                            ├── references.bib
                                            ├── output.pdf
                                            └── README.md
```

---

## Step 1: Initialize

### 1.1 Validate Inputs

```yaml
required:
  - paper/06_paper_final.md # Must exist
recommended:
  - paper/06_references.bib # For bibliography
  - paper/figures/ # For embedded figures
```

### 1.2 Create Folder Structure

```
paper/overleaf/
├── sections/
├── figures/
```

### 1.3 Check LaTeX Toolchain

```bash
which pdflatex # Required for compilation
which bibtex # Required for references
```

If not available, generate LaTeX project but skip compilation step.

### 1.4 ICML Style Files

**Auto-download official ICML 2025 style package:**

```bash
cd {overleaf_dir}

# Check if style files already exist
if [ ! -f "icml2025.sty" ]; then
    echo "📥 Downloading official ICML 2025 style files..."

    # Download style package
    wget -O icml2025.zip https://media.icml.cc/Conferences/ICML2025/Styles/icml2025.zip

    # Extract using Python (cross-platform)
    python3 -m zipfile -e icml2025.zip .

    # Copy required files from extracted folder
    cp icml2025/icml2025.sty .
    cp icml2025/icml2025.bst .
    cp icml2025/algorithm.sty .
    cp icml2025/algorithmic.sty .
    cp icml2025/fancyhdr.sty .

    # Clean up
    rm -rf icml2025/ icml2025.zip

    echo "✅ ICML 2025 style files installed"
else
    echo "✅ ICML 2025 style files already present"
fi

# Install missing LaTeX packages if needed
if ! kpsewhich forloop.sty > /dev/null 2>&1; then
    echo "📦 Installing forloop package..."
    tlmgr install forloop
fi
```

**Fallback:** If download fails, create stub files and note in README.md that user must manually download from:
- https://media.icml.cc/Conferences/ICML2025/Styles/icml2025.zip

---

## Step 2: Markdown to LaTeX Conversion

### 2.1 Parse Paper Sections

Split `06_paper_final.md` by `---` separators and section headers into:

| File | Source Section |
|------|---------------|
| `abstract.tex` | Abstract (before first `#` section) |
| `introduction.tex` | Section 1: Introduction |
| `related_work.tex` | Section 2: Related Work |
| `methodology.tex` | Section 3: Methodology |
| `experiments.tex` | Section 4: Experimental Setup |
| `results.tex` | Section 5: Results |
| `discussion.tex` | Section 6: Discussion |
| `conclusion.tex` | Section 7: Conclusion |
| `appendix.tex` | Appendix (if present) |

### 2.2 Conversion Rules

#### Structural Elements

| Markdown | LaTeX |
|----------|-------|
| `# Title` | `\section{Title}` |
| `## Subtitle` | `\subsection{Subtitle}` |
| `### Sub-sub` | `\subsubsection{Sub-sub}` |
| `**bold**` | `\textbf{bold}` |
| `*italic*` | `\textit{italic}` |
| `` `code` `` | `\texttt{code}` |
| `- item` | `\begin{itemize}\item item\end{itemize}` |
| `1. item` | `\begin{enumerate}\item item\end{enumerate}` |

#### Special Character Escaping

These characters MUST be escaped in normal text (NOT in math mode):

| Character | LaTeX | Notes |
|-----------|-------|-------|
| `%` | `\%` | Always escape |
| `&` | `\&` | Always escape |
| `#` | `\#` | Always escape |
| `_` | `\_` | Except in math mode and `\texttt{}` |
| `{` | `\{` | Only in normal text |
| `}` | `\}` | Only in normal text |
| `~` | `\textasciitilde{}` | Rare |
| `^` | `\^{}` | Only outside math mode |

#### Tables

**Markdown:**
```markdown
| Model | Accuracy | F1 |
|-------|----------|-----|
| Baseline | 85.2 | 83.1 |
| **Ours** | **92.4** | **91.2** |
```

**LaTeX:**
```latex
\begin{table}[h]
\centering
\caption{Caption here}
\label{tab:label}
\begin{tabular}{lcc}
\toprule
Model & Accuracy & F1 \\
\midrule
Baseline & 85.2 & 83.1 \\
\textbf{Ours} & \textbf{92.4} & \textbf{91.2} \\
\bottomrule
\end{tabular}
\end{table}
```

#### Figures

**Markdown:**
```markdown
![Figure 2: Performance comparison](figures/fig_results_1.png)
```

**LaTeX:**
```latex
\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figures/fig_results_1.png}
\caption{Performance comparison.}
\label{fig:performance}
\end{figure}
```

#### Citations

**Markdown:** `[Vaswani et al., 2017]`
**LaTeX:** `\cite{Vaswani2017}` or `\citep{Vaswani2017}`

Match citation keys to entries in `references.bib`.

#### Math

Math expressions `$...$` and `$$...$$` pass through unchanged. Ensure:
- Inline math: `$x^2$` stays as `$x^2$`
- Display math: `$$E = mc^2$$` becomes `\begin{equation}E = mc^2\end{equation}`

### 2.3 Abstract Special Handling

The abstract does NOT use `\section{}`. It is placed inside:
```latex
\begin{abstract}
{content}
\end{abstract}
```

This is handled by `main.tex` which uses `\input{sections/abstract}`.

### 2.7 Figure Integration (AUTO - Intelligent Insertion)

> **Purpose:** Insert figures from `figure_registry.yaml` at appropriate locations in LaTeX sections by analyzing paper content and figure metadata.

**CRITICAL:** This is NOT hardcoded logic. LLM analyzes actual content and makes intelligent decisions.

#### 2.7.1 Load Metadata (Understand Context)

```pseudo
# Step 1: Load figure registry
figures = LOAD_YAML("../figure_registry.yaml")['figures']
print(f"Found {len(figures)} figures to integrate")

# Step 2: Load verification state to understand hypotheses
verification_state = LOAD_YAML("../verification_state.yaml")
hypotheses = verification_state['hypotheses'] # e.g., {h-e1: {...}, h-m1: {...}, h-m2: {...}}

# Step 3: Read the original paper to understand structure
paper_content = READ("../06_paper_final.md")
```

**What you now know:**
- Which figures exist (filenames, hypotheses they belong to)
- Which hypotheses exist in this research (h-e1, h-m1, h-m2, etc.)
- What the paper actually says about each hypothesis

#### 2.7.2 Group Figures by Hypothesis

```pseudo
# Group figures by which hypothesis they validate
figures_by_hypothesis = {}
FOR EACH figure IN figures:
    hyp_id = figure['hypothesis'] # e.g., 'h-e1'
    IF hyp_id NOT IN figures_by_hypothesis:
        figures_by_hypothesis[hyp_id] = []
    figures_by_hypothesis[hyp_id].append(figure)

# Example result (varies by research):
# Research A (3 hypotheses):
# {
# 'h-existence-1': [fig_1, fig_2],
# 'h-mechanism-1': [fig_3],
# 'h-condition-1': [fig_4, fig_5]
# }
#
# Research B (2 hypotheses):
# {
# 'h-optimizer-baseline': [fig_1, fig_2, fig_3],
# 'h-scaling-behavior': [fig_4]
# }
```

#### 2.7.3 Analyze Results Section Structure

```pseudo
# Read the generated results.tex to understand its structure
results_tex = READ("sections/results.tex")

# Understand: What subsections exist? What does each discuss?
# Example detection (adapt to actual paper structure):
# - "\subsection{Baseline Comparison (H-OPT-1)}" → this discusses h-opt-1
# - "\subsection{Scaling Behavior}" → might discuss h-scale-1
# - Table appears → good insertion point is AFTER the table

# Parse subsections (extract hypothesis ID from heading or content)
subsections = PARSE_SUBSECTIONS(results_tex)
# Example result (varies by research):
# [
# {title: 'Baseline Performance', start: 10, end: 50, hypothesis: 'h-base-1'},
# {title: 'Ablation Study', start: 51, end: 80, hypothesis: 'h-abl-1'},
# {title: 'Sensitivity Analysis', start: 81, end: 120, hypothesis: 'h-sens-1'}
# ]
```

#### 2.7.4 Intelligent Insertion (Pseudo Code - NOT Hardcoded!)

```pseudo
FOR EACH subsection IN subsections:
    hypothesis_id = subsection['hypothesis'] # e.g., 'h-e1'

    # Get figures for this hypothesis
    relevant_figures = figures_by_hypothesis.get(hypothesis_id, [])

    IF len(relevant_figures) == 0:
        CONTINUE # No figures for this hypothesis

    # Find insertion point in this subsection
    # ANALYZE CONTENT to find best location:
    # - After interpretation paragraph?
    # - After a table?
    # - Before next subsection?

    subsection_content = GET_CONTENT(results_tex, subsection['start_line'], subsection['end_line'])

    # LLM DECISION POINT: Where should figures go?
    # Look for patterns like:
    # - "\\textbf{Interpretation:}" → insert BEFORE this
    # - "\\end{table}" → insert AFTER this
    # - End of subsection content → insert before next subsection

    insertion_point = FIND_BEST_INSERTION_POINT(subsection_content)

    # Generate LaTeX for each figure
    FOR EACH figure IN relevant_figures:
        figure_latex = GENERATE_FIGURE_LATEX(figure, hypothesis_id, paper_content)
        INSERT(results_tex, insertion_point, figure_latex)
```

#### 2.7.5 Generate Figure LaTeX (Context-Aware)

```pseudo
FUNCTION GENERATE_FIGURE_LATEX(figure, hypothesis_id, paper_content):
    filename = figure['original_name']
    width = figure.get('width', '0.9\\textwidth')
    fig_id = figure['id']

    # INTELLIGENT CAPTION GENERATION
    # Analyze: What does the paper SAY about this hypothesis?
    # Analyze: What does the filename suggest?

    hypothesis_section = EXTRACT_SECTION_ABOUT(paper_content, hypothesis_id)

    # LLM REASONING (examples - NOT exhaustive patterns):
    # Example A:
    # Filename: 'optimizer_comparison.png'
    # Hypothesis content: "Our method achieves 2.3x speedup..."
    # → Caption: "Training speedup comparison. Proposed optimizer achieves
    # 2.3x faster convergence than baseline methods."
    #
    # Example B:
    # Filename: 'loss_landscape.png'
    # Hypothesis content: "smoother optimization surface"
    # → Caption: "Loss landscape visualization showing smoother optimization
    # surface with proposed regularization."
    #
    # Example C:
    # Filename: 'scaling_curve.png'
    # Hypothesis content: "log-linear scaling up to 1B parameters"
    # → Caption: "Scaling behavior analysis. Method maintains log-linear
    # efficiency up to 1B parameters."

    # Generate caption by UNDERSTANDING context, not pattern matching
    caption = GENERATE_CAPTION_FROM_CONTEXT(
        filename=filename,
        hypothesis_content=hypothesis_section,
        hypothesis_id=hypothesis_id
    )

    # Handle side-by-side figures (e.g., pca_hacw + pca_ablated)
    IF SHOULD_BE_SIDE_BY_SIDE(figure, relevant_figures):
        RETURN GENERATE_SIDE_BY_SIDE_FIGURE(figure, related_figure, caption)
    ELSE:
        RETURN f"""
\\begin{{figure}}[t]
\\centering
\\includegraphics[width={width}]{{figures/{filename}}}
\\caption{{{caption}}}
\\label{{fig:{fig_id}}}
\\end{{figure}}
"""
```

#### 2.7.6 Example Caption Generation Logic (Pseudo)

```pseudo
FUNCTION GENERATE_CAPTION_FROM_CONTEXT(filename, hypothesis_content, hypothesis_id):
    # Read what the paper says about this hypothesis
    # Extract key claims and metrics

    # Example A - Optimizer research:
    # - Paper mentions "converges in 50% fewer steps"
    # - Paper mentions "AdamW baseline"
    # - Filename: 'convergence_comparison.png'
    # → Caption: "Convergence comparison. Proposed optimizer reaches target loss
    # in 50% fewer steps than AdamW baseline."

    # Example B - Architecture research:
    # - Paper mentions "reduces FLOPs by 3x"
    # - Paper mentions "maintains 95% accuracy"
    # - Filename: 'efficiency_accuracy_tradeoff.png'
    # → Caption: "Efficiency-accuracy trade-off. Proposed architecture reduces
    # FLOPs by 3x while maintaining 95% of baseline accuracy."

    # Example C - Dataset research:
    # - Paper mentions "performance saturates at 10K samples"
    # - Filename: 'data_scaling.png'
    # → Caption: "Data scaling behavior. Performance saturates at approximately
    # 10K training samples across all model sizes."

    # DON'T use rigid patterns - UNDERSTAND the content!
    RETURN CAPTION_BASED_ON_UNDERSTANDING
```

#### 2.7.7 Special Cases

**Side-by-side figures (when comparison makes sense):**

```pseudo
# Detect if two figures should be shown together
# Look for patterns like: method_A.png + method_B.png, or before.png + after.png

# Example A - Method comparison:
IF exists('proposed_method.png') AND exists('baseline_method.png'):
    RETURN f"""
\\begin{{figure}}[t]
\\centering
\\includegraphics[width=0.45\\linewidth]{{figures/proposed_method.png}}
\\hfill
\\includegraphics[width=0.45\\linewidth]{{figures/baseline_method.png}}
\\caption{{Comparison of [what]. Left: Proposed method shows [result].
          Right: Baseline method shows [different result].}}
\\label{{fig:method-comparison}}
\\end{{figure}}
"""

# Example B - Before/after comparison:
IF exists('before_optimization.png') AND exists('after_optimization.png'):
    # Generate side-by-side with before/after structure
```

#### 2.7.8 Verification

```pseudo
# After insertion, verify:
CHECK all_figures_from_registry_are_inserted()
CHECK all_captions_are_descriptive() # Not just "Results from h-e1"
CHECK figures_are_in_correct_sections()
CHECK no_duplicate_labels()

PRINT "✅ Inserted {count} figures across {num_hypotheses} hypotheses"
```

---

## Step 3: Assemble Project

### 3.1 Generate main.tex

Use the template at `phase6-paper-writing/templates/overleaf/main.tex`.

Replace placeholder tokens:

| Token | Source |
|-------|--------|
| `{PAPER_TITLE}` | Title from `06_paper_final.md` YAML frontmatter |
| `{PAPER_TITLE_SHORT}` | Abbreviated title (first 50 chars or manual) |

Keep author information as placeholders for human editing.

### 3.2 Copy References

```bash
cp paper/06_references.bib paper/overleaf/references.bib
```

### 3.3 Copy Figures

```bash
cp paper/figures/* paper/overleaf/figures/
```

### 3.4 Generate README.md

Create `overleaf/README.md` with:
- Quick start instructions for Overleaf upload
- Local compilation commands
- Checklist before submission
- Generated timestamp and pipeline version

---

## Step 4: Compile and Verify

### 4.1 Compilation Sequence

```bash
cd paper/overleaf/
pdflatex -interaction=nonstopmode main.tex # First pass
bibtex main # Process references
pdflatex -interaction=nonstopmode main.tex # Resolve references
pdflatex -interaction=nonstopmode main.tex # Final pass
cp main.pdf output.pdf # Final output
```

### 4.2 Error Handling

On compilation failure:
1. Read `main.log` for error messages
2. Common fixes:
   - Missing package: add `\usepackage{}`
   - Unescaped special character: escape it
   - Missing figure: create placeholder
   - Missing citation: add to .bib or remove `\cite{}`
3. Retry compilation (max 3 attempts)
4. If still failing: report errors in `.phase_state.json` but keep the LaTeX project

### 4.3 Verification

- [ ] `output.pdf` exists and is > 0 bytes
- [ ] All section .tex files exist (9 files)
- [ ] `main.tex` has no placeholder tokens remaining
- [ ] `references.bib` exists
- [ ] All `\cite{}` keys exist in .bib (warning if not)
- [ ] All `\includegraphics{}` files exist (warning if not)

### 4.4 Update Pipeline State

Update `verification_state.yaml`:
```yaml
overleaf_generation:
  status: "COMPLETED"
  completed_at: "{ISO8601}"
  output_folder: "paper/overleaf/"
  pdf_file: "paper/overleaf/output.pdf"
  compilation_status: "SUCCESS" | "PARTIAL" | "FAILED"
```

Create `.phase_state.json` via `create_phase_state.py`:
```json
{
  "status": "SUCCESS",
  "phase": "phase651-overleaf",
  "next_action": {
    "type": "stop",
    "reason": "Pipeline completed"
  }
}
```

---

## Completion Message

```
Phase 6.5.1: Overleaf + PDF Generation COMPLETE

Outputs:
  LaTeX Project: paper/overleaf/
  Compiled PDF: paper/overleaf/output.pdf

Quick Start (Overleaf):
  1. Upload paper/overleaf/ folder to new Overleaf project
  2. Download icml2025.sty and icml2025.bst from ICML website
  3. Set main.tex as main document, use pdfLaTeX compiler
  4. Compile (BibTeX, then pdfLaTeX twice)

Human Action Required:
  1. Replace author information placeholders
  2. Add acknowledgements
  3. Review 065_human_review_notes.md for minor fixes
  4. Final quality check in Overleaf
```

---

## SUCCESS/FAILURE Metrics

### SUCCESS:
- `overleaf/` folder created with correct structure
- All sections converted from Markdown to LaTeX
- `main.tex` generated from template with tokens replaced
- Figures and references copied
- PDF compilation attempted (success or documented failure)
- Pipeline state updated

### FAILURE:
- `06_paper_final.md` not found
- No .tex section files generated
- `main.tex` not created
- Pipeline state not updated
