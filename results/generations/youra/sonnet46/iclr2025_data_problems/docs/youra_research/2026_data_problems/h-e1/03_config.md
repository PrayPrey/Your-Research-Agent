# Configuration: H-E1 — Conditional Demographic Association Density Pipeline

**Hypothesis ID:** H-E1
**Hypothesis Type:** EXISTENCE (PoC)
**Generated:** 2026-03-14

Applied: Standard Python experiment config pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Config Files Found:** None - new config
**Pattern Used:** hardcoded dict (EXISTENCE PoC)

---

## Full Experiment Configuration

```python
CONFIG = {
    # Experiment core
    "seed": 42,
    "n_docs": 10_000_000,
    "window_size": 10,
    "n_bootstrap": 10_000,
    "gate_threshold_pct": 5.0,

    # External model / dataset IDs
    "fasttext_model_id": "mlfoundations/fasttext-oh-eli5",
    "dataset_id": "mlfoundations/dclm-baseline-1.0",

    # Corpus configurations C0–C6
    "configurations": {
        "C0": {"type": "unfiltered", "percentile": 0},
        "C1": {"type": "fasttext",   "percentile": 10},
        "C2": {"type": "fasttext",   "percentile": 30},
        "C3": {"type": "fasttext",   "percentile": 50},
        "C4": {"type": "fasttext",   "percentile": 70},
        "C5": {"type": "fasttext",   "percentile": 90},
        "C6": {"type": "doremi",     "percentile": None},
    },

    # Occupation lexicon — 60 WinoBias occupations
    "occupation_lexicon": [
        "nurse", "engineer", "lawyer", "teacher", "doctor",
        "housekeeper", "receptionist", "janitor", "carpenter", "electrician",
        "accountant", "supervisor", "secretary", "auditor", "writer",
        "designer", "broker", "pharmacist", "cashier", "analyst",
        "manager", "librarian", "counselor", "chef", "mechanic",
        "plumber", "developer", "programmer", "scientist", "researcher",
        "consultant", "administrator", "attendant", "guard", "baker",
        "clerk", "editor", "physician", "surgeon", "therapist",
        "assistant", "director", "coordinator", "technician", "inspector",
        "investigator", "detective", "officer", "dispatcher", "firefighter",
        "paramedic", "veterinarian", "dentist", "hygienist", "nutritionist",
        "coach", "instructor", "tutor", "painter", "driver",
    ],

    # Demographic lexicon — gendered pronouns + demographic NEs
    "demographic_lexicon": [
        # Gendered pronouns
        "he", "she", "his", "her", "him", "they", "their", "them",
        # Demographic NEs (race/nationality markers from WinoBias/BBQ)
        "man", "woman", "men", "women", "male", "female",
        "boy", "girl", "gentleman", "lady", "sir", "madam",
        "african", "asian", "hispanic", "latino", "latina",
        "white", "black", "caucasian", "american", "european",
    ],

    # Paths
    "data_dir": "h-e1/data",
    "figures_dir": "h-e1/figures",
    "results_path": "h-e1/results.json",
    "validation_path": "h-e1/04_validation.md",

    # Visualization settings (A-5)
    "viz": {
        "figure_size": (10, 6),
        "figure_size_heatmap": (12, 8),
        "dpi": 150,
        "color_scheme": "colorblind",        # seaborn palette safe for publication
        "bar_color": "#4C72B0",
        "highlight_color": "#DD8452",        # threshold / DoReMi accent
        "output_format": "png",
        "font_size_title": 14,
        "font_size_axis": 12,
        "font_size_tick": 10,
        "ci_capsize": 5,
        "threshold_linestyle": "--",
    },
}
```

---

## A-5: Visualization Module [Complexity: 10, Budget: 1]

Applied: Standard matplotlib/seaborn figure config pattern

The visualization config is embedded in `CONFIG["viz"]` above. Key values:

- `figure_size`: (10, 6) — standard widescreen layout for bar/trend charts
- `figure_size_heatmap`: (12, 8) — wider for occupation x demographic matrix
- `dpi`: 150 — publication-quality without excessive file size
- `color_scheme`: `"colorblind"` — seaborn palette for accessibility
- `output_format`: `"png"` — universally readable, no LaTeX dependency
- `highlight_color`: accent for MUST_WORK 5% threshold line and DoReMi bars

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Visualizer Implementation | Implement all 4 figure methods in `visualize.py` using `CONFIG["viz"]` settings: bar chart with CI error bars, monotonic trend plot, demographic heatmap (seaborn), relative change horizontal bar chart with 5% threshold line |
