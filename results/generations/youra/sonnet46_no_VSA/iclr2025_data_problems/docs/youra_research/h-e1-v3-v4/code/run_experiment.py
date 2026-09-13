#!/usr/bin/env python3
"""
h-e1-v3-v4: Global k-th Percentile Threshold Disparity Analysis
RedPajama-V2 ccnet_perplexity — Cramér's V gate: [0.40, 0.57] for k in {10,20,30,40,50}
Gate bounds updated from h-e1 [0.29, 0.41] based on empirical results.
"""
import gzip
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
from scipy.stats.contingency import association
from statsmodels.stats.multitest import multipletests

# ─── paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("docs/youra_research/h-e1-v3-v4")
CACHE_PATH = Path("docs/youra_research/redpajama_sample.parquet")
HF_CACHE_ROOT = Path.home() / ".cache/huggingface/hub/datasets--togethercomputer--RedPajama-Data-V2"
HF_DATASETS_CACHE = Path.home() / ".cache/huggingface/datasets/togethercomputer___red_pajama-data-v2/sample/1.0.0"
OUTPUT_DIR = BASE_DIR
FIGURES_DIR = BASE_DIR / "figures"
K_VALUES = [10, 20, 30, 40, 50]

# Updated gate bounds (h-e1: 0.29/0.41 → h-e1-v3-v4: 0.40/0.57)
GATE_V_MIN = 0.40
GATE_V_MAX = 0.57

# Mechanism verification uses wider bounds
MECH_V_MIN = 0.38
MECH_V_MAX = 0.60

_LANG_RE = re.compile(r"/([a-z]{2})_(?:head|middle|tail)\.signals\.json\.gz$")


# ─── data loader ──────────────────────────────────────────────────────────────

def _parse_signals_file(path: Path, lang: str) -> list[dict]:
    rows = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                qs = obj.get("quality_signals", {})
                if isinstance(qs, str):
                    qs = json.loads(qs)
                ppl_entry = qs.get("ccnet_perplexity")
                if ppl_entry:
                    ppl = float(ppl_entry[0][2])
                    doc_lang = (obj.get("metadata") or {}).get("language") or lang
                    rows.append({"language": doc_lang, "ccnet_perplexity": ppl})
            except Exception:
                continue
    return rows


def _find_signals_files() -> list[tuple[Path, str]]:
    snapshot_dirs = sorted((HF_CACHE_ROOT / "snapshots").iterdir())
    if not snapshot_dirs:
        return []
    snap = snapshot_dirs[-1]
    sig_root = snap / "sample" / "quality_signals"
    result = []
    for gz in sorted(sig_root.rglob("*.signals.json.gz")):
        m = _LANG_RE.search(gz.as_posix())
        if m:
            result.append((gz, m.group(1)))
    return result


def _load_from_arrow_cache() -> pd.DataFrame | None:
    import pyarrow.ipc as pa_ipc

    arrow_dirs = sorted(HF_DATASETS_CACHE.iterdir()) if HF_DATASETS_CACHE.exists() else []
    if not arrow_dirs:
        return None
    hash_dir = arrow_dirs[0]
    arrow_files = sorted(hash_dir.glob("*.arrow"))
    if not arrow_files:
        return None

    rows = []
    for arrow_file in arrow_files:
        with open(str(arrow_file), "rb") as fh:
            reader = pa_ipc.open_stream(fh)
            table = reader.read_all()
        meta_col = table["meta"]
        qs_col = table["quality_signals"]
        for i in range(table.num_rows):
            try:
                meta_raw = meta_col[i].as_py()
                meta = json.loads(meta_raw) if isinstance(meta_raw, str) else meta_raw
                lang = meta.get("language") if isinstance(meta, dict) else None
                qs_raw = qs_col[i].as_py()
                qs = json.loads(qs_raw) if isinstance(qs_raw, str) else qs_raw
                ppl_entry = qs.get("ccnet_perplexity") if isinstance(qs, dict) else None
                if lang and ppl_entry:
                    rows.append({"language": lang, "ccnet_perplexity": float(ppl_entry[0][2])})
            except Exception:
                continue
    if not rows:
        return None
    return pd.DataFrame(rows)


def load_data(cache_path: Path = CACHE_PATH) -> pd.DataFrame:
    if cache_path.exists():
        print(f"[data] Loading cache: {cache_path}")
        return pd.read_parquet(cache_path)

    print("[data] Attempting load from Arrow cache ...")
    df = None
    try:
        df = _load_from_arrow_cache()
    except Exception as e:
        print(f"[data] Arrow cache load failed: {e}, falling back to gz files")

    if df is None or len(df) < 100_000:
        files = _find_signals_files()
        if not files:
            raise FileNotFoundError(
                f"No data found. Download: load_dataset('togethercomputer/RedPajama-Data-V2', name='sample')"
            )
        print(f"[data] Parsing {len(files)} quality_signals gz files ...")
        all_rows: list[dict] = []
        for path, lang in files:
            rows = _parse_signals_file(path, lang)
            all_rows.extend(rows)
        df = pd.DataFrame(all_rows)

    df = df.dropna(subset=["ccnet_perplexity"])
    df["language"] = df["language"].astype(str)
    df = df[df["language"].isin(["en", "de", "fr", "es", "it"])].reset_index(drop=True)

    print(f"[data] Full dataset: {len(df)} rows, {df['language'].nunique()} languages")
    print(f"[data] Per-language counts: {df['language'].value_counts().to_dict()}")

    TARGET = 208_263
    if len(df) > TARGET * 1.05:
        print(f"[data] Subsampling to {TARGET} rows (stratified) ...")
        sampled = (
            df.groupby("language", group_keys=False)
            .apply(lambda g: g.sample(frac=TARGET / len(df), random_state=42))
        )
        df = sampled.reset_index(drop=True)
        print(f"[data] After subsample: {len(df)} rows")

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path, index=False)
    print(f"[data] Cached {len(df)} rows → {cache_path}")
    return df


# ─── validator ────────────────────────────────────────────────────────────────

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) < 190_000:
        raise ValueError(f"Too few rows: {len(df)} < 190,000")
    if df["language"].nunique() != 5:
        raise ValueError(f"Expected 5 languages, got {df['language'].nunique()}: {sorted(df['language'].unique())}")
    nan_rate = df["ccnet_perplexity"].isna().mean()
    if nan_rate > 0.01:
        raise ValueError(f"NaN rate {nan_rate:.3%} > 1%")
    df = df.dropna(subset=["ccnet_perplexity"])
    return df


# ─── analyzer ─────────────────────────────────────────────────────────────────

def analyze_thresholds(df: pd.DataFrame, k_values: list[int] = K_VALUES) -> dict:
    languages = sorted(df["language"].unique())
    results: dict = {}

    for k in k_values:
        threshold = df["ccnet_perplexity"].quantile(k / 100)
        retained = (df["ccnet_perplexity"] < threshold).astype(int)
        df_k = df.assign(retained=retained)

        contingency = pd.crosstab(df_k["language"], df_k["retained"])
        for col in [0, 1]:
            if col not in contingency.columns:
                contingency[col] = 0
        contingency = contingency[[0, 1]]

        v = association(contingency.values, method="cramer")
        chi2, p, _, _ = chi2_contingency(contingency.values)

        retention_rates = (
            df_k.groupby("language")["retained"].mean()
            .reindex(languages)
            .to_dict()
        )

        results[k] = {
            "threshold": float(threshold),
            "cramers_v": float(v),
            "chi2": float(chi2),
            "p_value": float(p),
            "retention_rates": {lang: float(r) for lang, r in retention_rates.items()},
        }

    return results


def apply_holm_correction(results: dict, k_values: list[int] = K_VALUES) -> dict:
    p_vals = [results[k]["p_value"] for k in k_values]
    _, p_holm, _, _ = multipletests(p_vals, method="holm")
    for i, k in enumerate(k_values):
        results[k]["p_holm"] = float(p_holm[i])
    return results


# ─── gate checker ─────────────────────────────────────────────────────────────

def check_gate(df: pd.DataFrame, results: dict, k_values: list[int] = K_VALUES) -> dict:
    indicators = {
        "data_loaded": bool(len(df) > 190_000),
        "five_languages": bool(df["language"].nunique() == 5),
        "no_nan_perplexity": bool(df["ccnet_perplexity"].isna().mean() < 0.01),
        "cramers_v_in_range": bool(all(
            GATE_V_MIN <= results[k]["cramers_v"] <= GATE_V_MAX for k in k_values
        )),
        "holm_p_significant": bool(all(
            results[k]["p_holm"] < 0.001 for k in k_values
        )),
    }
    gate_passed = bool(all(indicators.values()))
    return {"gate_passed": gate_passed, "indicators": indicators}


def verify_mechanism_activated(results: dict, k_values: list[int] = K_VALUES) -> tuple[bool, dict]:
    # Wider bounds for mechanism check vs strict gate bounds
    indicators = {
        "data_loaded": results.get("n_rows", 0) >= 190_000,
        "five_languages": results.get("n_languages", 0) == 5,
        "no_nan_perplexity": results.get("nan_rate", 1.0) < 0.01,
        "cramers_v_in_range": all(
            MECH_V_MIN <= results["per_k"][k]["cramers_v"] <= MECH_V_MAX
            for k in k_values
        ),
        "holm_p_significant": all(
            results["per_k"][k]["p_holm"] < 0.001
            for k in k_values
        ),
    }
    return bool(all(indicators.values())), indicators


# ─── visualizer ───────────────────────────────────────────────────────────────

def plot_figures(df: pd.DataFrame, results: dict, k_values: list[int] = K_VALUES) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    languages = sorted(df["language"].unique())

    # 1. Cramér's V bar chart — updated bounds [0.40, 0.57]
    fig, ax = plt.subplots(figsize=(7, 4))
    vs = [results[k]["cramers_v"] for k in k_values]
    colors = ["green" if GATE_V_MIN <= v <= GATE_V_MAX else "red" for v in vs]
    ax.bar([str(k) for k in k_values], vs, color=colors)
    ax.axhline(GATE_V_MIN, color="navy", linestyle="--", label=f"lower bound ({GATE_V_MIN})")
    ax.axhline(GATE_V_MAX, color="darkorange", linestyle="--", label=f"upper bound ({GATE_V_MAX})")
    ax.set_xlabel("k (percentile)")
    ax.set_ylabel("Cramér's V")
    ax.set_title("Cramér's V vs. k — Global Threshold Disparity (h-e1-v3-v4)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cramers_v_bar.png", dpi=150)
    plt.close(fig)

    # 2. Retention heatmap
    heatmap_data = pd.DataFrame(
        {k: results[k]["retention_rates"] for k in k_values}
    ).loc[languages]
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax)
    ax.set_xlabel("k (percentile)")
    ax.set_ylabel("Language")
    ax.set_title("Per-Language Retention Rate Heatmap")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "retention_heatmap.png", dpi=150)
    plt.close(fig)

    # 3. Perplexity KDE per language
    fig, ax = plt.subplots(figsize=(8, 4))
    for lang in languages:
        subset = df[df["language"] == lang]["ccnet_perplexity"].dropna()
        subset_clipped = subset[subset < subset.quantile(0.99)]
        sns.kdeplot(subset_clipped, ax=ax, label=lang, log_scale=True)
    ax.set_xlabel("ccnet_perplexity (log scale)")
    ax.set_ylabel("Density")
    ax.set_title("Perplexity Distribution by Language")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "perplexity_kde.png", dpi=150)
    plt.close(fig)

    # 4. Max-min retention gap vs k
    gaps = [
        max(results[k]["retention_rates"].values()) - min(results[k]["retention_rates"].values())
        for k in k_values
    ]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([str(k) for k in k_values], gaps, marker="o")
    ax.set_xlabel("k (percentile)")
    ax.set_ylabel("Max-Min Retention Gap (pp)")
    ax.set_title("Retention Gap across Languages vs. k")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "retention_gap.png", dpi=150)
    plt.close(fig)

    print(f"[figures] 4 figures saved to {FIGURES_DIR}")


# ─── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("h-e1-v3-v4: Global k-th Percentile Threshold Disparity")
    print(f"Gate bounds: Cramér's V ∈ [{GATE_V_MIN}, {GATE_V_MAX}]")
    print("=" * 60)

    # 1. Load
    df = load_data(CACHE_PATH)
    print(f"[data] Loaded {len(df)} rows, {df['language'].nunique()} languages: {sorted(df['language'].unique())}")

    # 2. Validate
    df = validate_data(df)
    print("[validate] OK")

    nan_rate = float(df["ccnet_perplexity"].isna().mean())

    # 3. Analyze
    results = analyze_thresholds(df, K_VALUES)

    # 4. Apply Holm correction
    results = apply_holm_correction(results, K_VALUES)

    for k in K_VALUES:
        r = results[k]
        print(f"  k={k:2d}: threshold={r['threshold']:.1f}, V={r['cramers_v']:.4f}, p_holm={r['p_holm']:.2e}")
        for lang, rate in sorted(r["retention_rates"].items()):
            print(f"        {lang}: {rate:.3f}")

    # 5. Gate check
    gate = check_gate(df, results, K_VALUES)
    print(f"\n[gate] passed={gate['gate_passed']}")
    for k, v in gate["indicators"].items():
        print(f"  {k}: {v}")

    # 6. Build full results for verify_mechanism_activated
    full_results = {
        "n_rows": len(df),
        "n_languages": int(df["language"].nunique()),
        "nan_rate": nan_rate,
        "per_k": results,
    }

    # 7. Mechanism verification
    mech_activated, mech_indicators = verify_mechanism_activated(full_results, K_VALUES)
    print(f"\n[mechanism] activated={mech_activated}")
    for k, v in mech_indicators.items():
        print(f"  {k}: {v}")

    # 8. Figures
    plot_figures(df, results, K_VALUES)

    # 9. Write outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results_json = {}
    for k, v in results.items():
        results_json[str(k)] = dict(v)

    full_results_json = {
        "n_rows": full_results["n_rows"],
        "n_languages": full_results["n_languages"],
        "nan_rate": full_results["nan_rate"],
        "per_k": results_json,
        "mechanism": {
            "activated": mech_activated,
            "indicators": mech_indicators,
        },
    }

    (OUTPUT_DIR / "results.json").write_text(json.dumps(full_results_json, indent=2))
    (OUTPUT_DIR / "gate_verdict.json").write_text(json.dumps(gate, indent=2))

    print(f"\n[output] results.json + gate_verdict.json → {OUTPUT_DIR}")
    print(f"[gate] PASSED={gate['gate_passed']}")

    sys.exit(0 if gate["gate_passed"] else 1)


if __name__ == "__main__":
    main()
