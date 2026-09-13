---
phase: 2C
hypothesis_id: h-e1
generated_at: "2026-07-30"
status: complete
---

# Experiment Brief: h-e1 — Data Infrastructure Viability (Existence Gate)

## 1. Objective

Verify that fuzzy joining Open LLM Leaderboard v1 (fboulnois/llm-leaderboard-csv v1.3.0) with `lighteval/bbq_helm` at rapidfuzz WRatio threshold=75 yields N≥30 open-weight LLMs with complete scores on {TruthfulQA MC2, BBQ accuracy, MMLU} simultaneously.

**Gate type:** MUST_WORK. All downstream partial Spearman analysis (h-m1 through h-m3) is invalid if N<30.

---

## 2. Datasets

### 2.1 Primary Dataset A — Open LLM Leaderboard v1 CSV

| Field | Value |
|-------|-------|
| Name | fboulnois/llm-leaderboard-csv |
| Type | standard (frozen GitHub release) |
| Release | v1.3.0 (last version with HF Open LLM Leaderboard v1; current repo only generates LMArena) |
| Asset URL | `https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv` |
| Fallback URL | GitHub API: `https://api.github.com/repos/fboulnois/llm-leaderboard-csv/releases/tags/v1.3.0` |
| Key columns | `model_name`, `TruthfulQA_MC2`, `MMLU` (exact column names to be verified at runtime) |
| Expected size | 300+ open-weight model rows |
| Verified | Via `requests.head()` URL test before any computation |

**Open-weight filter:** Exclude rows where model name contains known proprietary model identifiers: `gpt`, `claude`, `gemini`, `palm`, `cohere`, `titan`, `j2-`, `command`. Apply case-insensitive substring match.

### 2.2 Primary Dataset B — lighteval/bbq_helm

| Field | Value |
|-------|-------|
| Name | lighteval/bbq_helm |
| Type | standard (HuggingFace dataset) |
| Load method | `datasets.load_dataset("lighteval/bbq_helm", split="train")` |
| Total rows | 11,864 (BBQ question-level model evaluation rows) |
| Key columns | `model` (model name), `acc` or `accuracy` (per-question accuracy; to be confirmed at runtime) |
| Aggregation | Group by `model`; compute mean accuracy → one row per model (BBQ accuracy score) |
| Expected models | ~79 HELM Lite models after aggregation |
| Verified | Via HuggingFace `datasets` API load |

### 2.3 Fallback Dataset B — HELM Lite v1.9.0

| Field | Value |
|-------|-------|
| Trigger | If `lighteval/bbq_helm` join yields N<30 after threshold=70 retry |
| Name | HELM Lite v1.9.0 BBQ subset |
| Source | `https://crfm.stanford.edu/helm/lite/v1.9.0/` leaderboard API or HuggingFace `ckkissane/helm-lite-v1.9.0` |
| Expected models | ~79 models with BBQ scores |

---

## 3. Experimental Design

### 3.1 Step-by-Step Protocol

**Step 0: URL Pre-flight Test**
```python
import requests

urls = {
    "llm_csv": "https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv",
    "bbq_helm": "https://huggingface.co/datasets/lighteval/bbq_helm",
}
for name, url in urls.items():
    r = requests.head(url, allow_redirects=True, timeout=15)
    assert r.status_code == 200, f"URL FAIL [{name}]: HTTP {r.status_code} — {url}"
    print(f"URL OK [{name}]: HTTP {r.status_code}")
```
Abort immediately if any URL returns non-200. Document the exact HTTP status code.

**Step 1: Load LLM Leaderboard v1 CSV**
```python
import pandas as pd
import io

resp = requests.get(urls["llm_csv"], timeout=60)
resp.raise_for_status()
llm_df = pd.read_csv(io.StringIO(resp.text))

# Inspect columns at runtime
print("LLM LB columns:", llm_df.columns.tolist())
print("LLM LB shape:", llm_df.shape)

# Identify TruthfulQA MC2 and MMLU columns by fuzzy name match
# Expected: 'TruthfulQA MC2', 'TruthfulQA_MC2', 'truthfulqa_mc2', etc.
# Expected: 'MMLU', 'Average', 'mmlu', etc.
```

Column name normalization (handle varied naming):
```python
col_map = {}
for col in llm_df.columns:
    lower = col.lower().replace(' ', '_').replace('-', '_')
    if 'truthful' in lower and 'mc2' in lower:
        col_map['TruthfulQA_MC2'] = col
    elif lower == 'mmlu' or lower == 'mmlu_avg':
        col_map['MMLU'] = col
    elif 'model' in lower and 'name' in lower or lower == 'model':
        col_map['model_name'] = col

assert 'TruthfulQA_MC2' in col_map, f"TruthfulQA MC2 column not found. Columns: {llm_df.columns.tolist()}"
assert 'MMLU' in col_map, f"MMLU column not found. Columns: {llm_df.columns.tolist()}"
assert 'model_name' in col_map, f"Model name column not found."

llm_clean = llm_df[[col_map['model_name'], col_map['TruthfulQA_MC2'], col_map['MMLU']]].copy()
llm_clean.columns = ['model_name', 'TruthfulQA_MC2', 'MMLU']
llm_clean = llm_clean.dropna(subset=['TruthfulQA_MC2', 'MMLU'])
print(f"LLM LB after dropping NaN: {len(llm_clean)} rows")
```

Open-weight filter:
```python
PROPRIETARY = ['gpt', 'claude', 'gemini', 'palm', 'cohere', 'titan', 'j2-', 'command', 'text-davinci', 'luminous']
mask_proprietary = llm_clean['model_name'].str.lower().apply(
    lambda n: any(p in n for p in PROPRIETARY)
)
llm_open = llm_clean[~mask_proprietary].copy()
print(f"Open-weight models: {len(llm_open)} (removed {mask_proprietary.sum()} proprietary)")
```

**Step 2: Load and Aggregate lighteval/bbq_helm**
```python
from datasets import load_dataset

bbq_raw = load_dataset("lighteval/bbq_helm", split="train")
bbq_df = bbq_raw.to_pandas()

# Inspect columns
print("BBQ columns:", bbq_df.columns.tolist())
print("BBQ shape:", bbq_df.shape)
print("BBQ sample models:", bbq_df['model'].unique()[:10] if 'model' in bbq_df.columns else "NO MODEL COL")

# Identify accuracy column
acc_col = None
for col in bbq_df.columns:
    if col.lower() in ['acc', 'accuracy', 'score', 'exact_match']:
        acc_col = col
        break
assert acc_col is not None, f"Accuracy column not found. Columns: {bbq_df.columns.tolist()}"

# Aggregate: mean accuracy per model
model_col = 'model' if 'model' in bbq_df.columns else bbq_df.columns[0]
bbq_agg = bbq_df.groupby(model_col)[acc_col].mean().reset_index()
bbq_agg.columns = ['model_name_bbq', 'BBQ_accuracy']
print(f"BBQ aggregated: {len(bbq_agg)} unique models")
print(f"BBQ accuracy range: [{bbq_agg['BBQ_accuracy'].min():.3f}, {bbq_agg['BBQ_accuracy'].max():.3f}]")
```

**Step 3: Fuzzy Join at WRatio threshold=75 (Primary)**
```python
from rapidfuzz import process, fuzz, utils

llm_names = llm_open['model_name'].tolist()
bbq_names = bbq_agg['model_name_bbq'].tolist()

def fuzzy_join_wratio(left_names, right_names, threshold=75):
    """Returns list of (left_name, right_name, score) for matches above threshold."""
    matches = []
    for lname in left_names:
        result = process.extractOne(
            lname,
            right_names,
            scorer=fuzz.WRatio,
            processor=utils.default_process,
            score_cutoff=threshold
        )
        if result:
            rname, score, _ = result
            matches.append({'model_name': lname, 'model_name_bbq': rname, 'match_score': score})
    return pd.DataFrame(matches)

match_df = fuzzy_join_wratio(llm_names, bbq_names, threshold=75)
match_rate = len(match_df) / len(bbq_agg)
print(f"Primary join (WRatio=75): {len(match_df)} matches, match_rate={match_rate:.3f}")
```

Token set ratio fallback (if match_rate < 0.55):
```python
if match_rate < 0.55:
    print("WARNING: match_rate < 0.55 — trying token_set_ratio fallback")
    def fuzzy_join_token_set(left_names, right_names, threshold=70):
        matches = []
        for lname in left_names:
            result = process.extractOne(
                lname,
                right_names,
                scorer=fuzz.token_set_ratio,
                processor=utils.default_process,
                score_cutoff=threshold
            )
            if result:
                rname, score, _ = result
                matches.append({'model_name': lname, 'model_name_bbq': rname, 'match_score': score})
        return pd.DataFrame(matches)
    
    match_df = fuzzy_join_token_set(llm_names, bbq_names, threshold=70)
    match_rate = len(match_df) / len(bbq_agg)
    print(f"Fallback join (token_set_ratio=70): {len(match_df)} matches, match_rate={match_rate:.3f}")
```

**Step 4: Build Joint Dataset**
```python
# Merge: LLM open-weight + BBQ via fuzzy match key
joint = llm_open.merge(match_df[['model_name', 'model_name_bbq', 'match_score']], on='model_name', how='inner')
joint = joint.merge(bbq_agg, on='model_name_bbq', how='inner')

# Complete rows: non-null in all three columns
joint_complete = joint.dropna(subset=['TruthfulQA_MC2', 'BBQ_accuracy', 'MMLU']).copy()
N = len(joint_complete)

print(f"\n=== H-E1 RESULT ===")
print(f"N complete rows: {N}")
print(f"Match rate: {match_rate:.3f}")
print(f"TruthfulQA MC2 range: [{joint_complete['TruthfulQA_MC2'].min():.2f}, {joint_complete['TruthfulQA_MC2'].max():.2f}]")
print(f"BBQ accuracy range: [{joint_complete['BBQ_accuracy'].min():.3f}, {joint_complete['BBQ_accuracy'].max():.3f}]")
print(f"MMLU range: [{joint_complete['MMLU'].min():.2f}, {joint_complete['MMLU'].max():.2f}]")
print(f"\nSample model names (first 10):")
print(joint_complete['model_name'].head(10).tolist())
```

**Step 5: Model Family Label Extraction (for downstream h-m2 BCa bootstrap)**
```python
import re

def extract_family(model_name):
    """Extract model family prefix for clustering in BCa bootstrap."""
    name_lower = model_name.lower()
    # Order matters: more specific patterns first
    families = [
        ('llama-2', r'llama.?2'), ('llama-3', r'llama.?3'), ('llama', r'llama'),
        ('mistral', r'mistral'), ('falcon', r'falcon'), ('mpt', r'^mpt'),
        ('pythia', r'pythia'), ('bloom', r'bloom'), ('gpt-j', r'gpt.?j'),
        ('gpt-neox', r'gpt.?neox'), ('opt', r'^opt-'), ('stablelm', r'stablelm'),
        ('vicuna', r'vicuna'), ('alpaca', r'alpaca'), ('wizardlm', r'wizard'),
        ('openhermes', r'openhermes'), ('nous', r'nous.?hermes'),
        ('deepseek', r'deepseek'), ('qwen', r'qwen'), ('yi', r'\byi-'),
    ]
    for family_name, pattern in families:
        if re.search(pattern, name_lower):
            return family_name
    # Fallback: first token before '-' or '/'
    base = re.split(r'[-/]', model_name)[0].lower()
    return base if base else 'unknown'

joint_complete['model_family'] = joint_complete['model_name'].apply(extract_family)
family_counts = joint_complete['model_family'].value_counts()
print("\nModel family distribution:")
print(family_counts.head(15))
llama_pct = family_counts.get('llama', 0) / N * 100
print(f"\nLlama family proportion: {llama_pct:.1f}% (risk R3 threshold: >30%)")
```

**Step 6: Gate Evaluation and Reporting**
```python
# Primary success criterion
gate_pass = N >= 30
match_rate_pass = match_rate >= 0.55

print(f"\n{'='*50}")
print(f"H-E1 GATE EVALUATION")
print(f"{'='*50}")
print(f"Primary: N={N} >= 30 → {'PASS' if gate_pass else 'FAIL'}")
print(f"Secondary: match_rate={match_rate:.3f} >= 0.55 → {'PASS' if match_rate_pass else 'WARN'}")
print(f"\nOverall gate: {'PASS — proceed to h-m1' if gate_pass else 'FAIL — activate fallback chain'}")

if not gate_pass:
    print("\nFAILURE ACTION:")
    print("1. Try HELM Lite v1.9.0 as BBQ source")
    print("2. Lower WRatio threshold to 70")
    print("3. If N still < 30 → STOP; report data availability finding")
```

**Step 7: Save Joint Dataset**
```python
import os

os.makedirs("results/h-e1", exist_ok=True)
joint_complete.to_csv("results/h-e1/joint_dataset.csv", index=False)
print(f"\nSaved joint dataset: results/h-e1/joint_dataset.csv ({N} rows)")

# Summary report
summary = {
    "N_complete": N,
    "match_rate": round(match_rate, 4),
    "gate_pass": gate_pass,
    "threshold_used": 75 if match_rate >= 0.55 else 70,
    "TruthfulQA_MC2_mean": round(joint_complete['TruthfulQA_MC2'].mean(), 4),
    "BBQ_accuracy_mean": round(joint_complete['BBQ_accuracy'].mean(), 4),
    "MMLU_mean": round(joint_complete['MMLU'].mean(), 4),
    "llama_family_pct": round(llama_pct, 1),
    "n_families": joint_complete['model_family'].nunique(),
}
import json
with open("results/h-e1/summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("Saved summary: results/h-e1/summary.json")
```

---

## 4. Success Criteria

| Criterion | Threshold | Type | Action if Failed |
|-----------|-----------|------|-----------------|
| N complete rows | ≥ 30 | MUST_WORK (gate) | Activate fallback chain (HELM Lite + threshold=70); STOP if still <30 |
| match_rate | ≥ 0.55 | Secondary (warning) | Log warning; try token_set_ratio fallback |
| URL pre-flight | HTTP 200 for both sources | Infrastructure gate | Try GitHub API fallback for llm.csv; try HELM Lite for BBQ |

---

## 5. Environment & Dependencies

```txt
pandas>=1.5.0
rapidfuzz>=3.0.0
datasets>=2.0.0  # HuggingFace datasets
requests>=2.28.0
numpy>=1.23.0
scipy>=1.10.0    # for downstream h-m2 BCa bootstrap
pingouin>=0.5.3  # for downstream h-m2 partial_corr
```

**No GPU required.** CPU-only, single machine. Expected runtime: <5 minutes (URL fetch + dataset load + fuzzy join over ~300 × ~79 model name pairs).

**Compute:** Any CPU with 4GB RAM. No training. Pure data loading, string matching, and aggregation.

---

## 6. Expected Outputs

```
results/h-e1/
├── joint_dataset.csv      # N rows × columns: model_name, TruthfulQA_MC2, MMLU, BBQ_accuracy, model_family, match_score, model_name_bbq
└── summary.json           # N_complete, match_rate, gate_pass, column statistics
```

### Expected Result Range (based on prior h-e1 run with match_rate=0.857)

- N: 40–70 complete rows (LLM LB v1 has 300+ models; bbq_helm has ~79; intersection after quality filter)
- match_rate: 0.55–0.90 (prior runs achieved 0.857 at WRatio=75)
- TruthfulQA MC2 range: ~25–75 (percent correct on MC2 task)
- BBQ accuracy range: ~0.40–0.90 (proportion correct across BBQ question types)
- MMLU range: ~30–75 (5-shot MMLU accuracy, percent)

---

## 7. Failure Response Chain

```
IF URL pre-flight fails:
  → For llm.csv: try GitHub API endpoint for v1.3.0 release assets
  → For bbq_helm: try HELM Lite v1.9.0 BBQ scores
  → Document HTTP status codes; STOP if both alternatives fail

IF N < 30 after primary join (WRatio=75):
  → Step 1: Lower threshold to 70 and retry WRatio join
  → Step 2: Switch BBQ source to HELM Lite v1.9.0
  → Step 3: Lower threshold to 65 with HELM Lite
  → If all steps yield N < 30: STOP; report "data infrastructure insufficient";
    publish data availability finding; route to Phase 0 for alternative data sources

IF match_rate < 0.55 but N ≥ 30:
  → Log warning with matched/unmatched model name samples
  → Check for systematic naming pattern differences (e.g., "org/model" vs "model")
  → Apply model name normalization: strip org prefix (everything before "/")
  → Continue if N ≥ 30 after normalization
```

---

## 8. Research Methodology Notes

### Why rapidfuzz WRatio + token_set_ratio fallback

`WRatio` is a weighted composite scorer that selects the best of partial ratio, token sort ratio, and token set ratio based on string lengths. It handles the common case where `lighteval/bbq_helm` uses HuggingFace model names in `org/model` format while LLM LB v1 may use only the base model name. `utils.default_process` normalizes case and non-alphanumeric characters before matching, which is critical for matching e.g. `"Llama-2-7B-chat"` to `"meta-llama/Llama-2-7b-chat-hf"`.

The `token_set_ratio` fallback handles cases where word order or subset matching is more appropriate (e.g., model names with version suffixes).

### Why prior match_rate=0.857 is a BUILD_ON reference

The verification plan (02b_verification_plan.md §0 BUILD_ON) notes that fuzzy join at WRatio threshold=75-80 was validated in a prior h-e1 run with match_rate=0.857. This experiment re-executes the join to get the current N count with the exact {TruthfulQA MC2, BBQ accuracy, MMLU} triple — the prior run may have used different columns or datasets.

### pingouin.partial_corr Spearman caveat (for downstream h-m2)

`pg.partial_corr(method='spearman')` uses inverse covariance matrix (rank-based covariance), which differs from the regression-residuals approach. This is correct for continuous scores but will warn if any variable is binary or has excessive ties. All three columns (TruthfulQA MC2, BBQ accuracy, MMLU) are continuous float scores, so no tie issue is expected. Log `joint_complete.nunique()` as a sanity check.

### BCa bootstrap clustering (for downstream h-m2)

Model family labels extracted in Step 5 will be used in h-m2 to implement cluster-aware BCa bootstrap (sampling whole families rather than individual models). The Llama family proportion >30% is the risk R3 threshold — if exceeded, the family-weighted Fisher z robustness check becomes the primary result rather than the unclustered Fisher z.

---

## 9. Archon / Past Cases

**[NOT_FOUND - ARCHON]** — Archon KB searches for "fuzzy join dataset matching rapidfuzz", "Spearman correlation leaderboard benchmark analysis", and "HuggingFace dataset download LLM evaluation" returned only diffusion/image generation content (similarity scores 0.36–0.58, irrelevant domain). No applicable past cases in Archon KB.

**[INFERRED]** Implementation patterns synthesized from:
- RapidFuzz official documentation and GitHub discussions (process.extractOne + WRatio + default_process)
- pingouin documentation (partial_corr spearman method, inverse covariance matrix approach)
- scipy.stats.bootstrap BCa documentation (n_resamples, paired=True for correlation CIs)
- fboulnois/llm-leaderboard-csv repository (v1.3.0 = last HF Open LLM LB v1 release)
- lighteval/bbq_helm HuggingFace dataset card (11,864 rows, needs aggregation by model)
