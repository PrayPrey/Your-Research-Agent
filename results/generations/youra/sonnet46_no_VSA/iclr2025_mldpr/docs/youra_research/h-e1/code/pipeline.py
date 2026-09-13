import numpy as np
import pandas as pd
from rapidfuzz import fuzz
from rapidfuzz import process as rfuzz_process

from config import CFG


EVAL_FLAT_CACHE = "eval_flat.parquet"


class DataLoader:
    def load(self) -> pd.DataFrame:
        """Load pre-flattened eval data from local parquet cache; fall back to live HF API."""
        import os
        if os.path.exists(EVAL_FLAT_CACHE):
            df = pd.read_parquet(EVAL_FLAT_CACHE)
            print(f"Loaded {len(df)} rows from cache ({df['task_path'].nunique()} tasks)")
            self.validate_columns(df)
            return df
        # Fallback: use preprocess_eval.py to generate cache
        import subprocess, sys
        script = os.path.join(os.path.dirname(__file__), "preprocess_eval.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"preprocess_eval.py failed:\n{result.stderr}")
        df = pd.read_parquet(EVAL_FLAT_CACHE)
        self.validate_columns(df)
        print(f"Loaded {len(df)} rows via preprocess ({df['task_path'].nunique()} tasks)")
        return df

    def validate_columns(self, df: pd.DataFrame) -> None:
        required = ["task_path", "paper_url"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in eval dataset: {missing}")


class PanelBuilder:
    def load_or_build(self, panel_path: str) -> pd.DataFrame:
        try:
            panel = pd.read_csv(panel_path)
            print(f"Loaded h-e2 panel from {panel_path}: {len(panel)} rows")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"h-e2 panel not found at {panel_path}. "
                "Generate it from Phase 2B or provide h_e2_panel.csv."
            )
        self.validate(panel)
        return panel

    def validate(self, panel: pd.DataFrame) -> None:
        required = [
            "task_path", "duration", "event", "task_age",
            "log_publication_volume", "benchmark_introduction_year",
        ]
        missing = [c for c in required if c not in panel.columns]
        if missing:
            raise ValueError(f"Missing columns in h-e2 panel: {missing}")


class FuzzyJoiner:
    def join(
        self,
        eval_df: pd.DataFrame,
        panel: pd.DataFrame,
        threshold: int = None,
    ) -> pd.DataFrame:
        if threshold is None:
            threshold = CFG.fuzzy_threshold
        h_e2_slugs = panel["task_path"].unique().tolist()

        def match_one(slug: str):
            result = rfuzz_process.extractOne(
                slug, h_e2_slugs, scorer=fuzz.token_sort_ratio
            )
            if result is None or result[1] < threshold:
                return None
            return result[0]

        eval_df = eval_df.copy()
        eval_df["matched_task"] = eval_df["task_path"].map(match_one)
        n_matched = eval_df["matched_task"].notna().sum()
        print(f"Fuzzy join: {n_matched}/{len(eval_df)} rows matched (threshold={threshold})")
        return eval_df

    def coverage_count(self, joined: pd.DataFrame) -> int:
        matched = joined[joined["matched_task"].notna()]
        covered = (
            matched[matched["paper_url"].notna()]
            .groupby("matched_task")["paper_url"]
            .count()
        )
        return len(covered)


class DiversityAggregator:
    def filter_temporal(
        self,
        joined: pd.DataFrame,
        panel: pd.DataFrame,
    ) -> pd.DataFrame:
        if "pub_year" not in joined.columns:
            print("pub_year not found in eval data — using all rows (no temporal filter)")
            return joined
        intro_map = panel.set_index("task_path")["benchmark_introduction_year"].to_dict()
        joined = joined.copy()
        joined["intro_year_mapped"] = joined["matched_task"].map(intro_map)
        mask = (
            joined["pub_year"].isna()
            | joined["intro_year_mapped"].isna()
            | (joined["pub_year"] <= joined["intro_year_mapped"])
        )
        filtered = joined[mask]
        print(f"Temporal filter: {len(filtered)}/{len(joined)} rows retained")
        return filtered

    def aggregate(self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        stats = (
            filtered_df[filtered_df["matched_task"].notna()]
            .groupby("matched_task")
            .agg(
                unique_count=("paper_url", "nunique"),
                total_rows=("paper_url", "count"),
            )
            .reset_index()
        )
        stats["diversity_ratio"] = stats["unique_count"] / stats["total_rows"].clip(lower=1)
        stats["log_unique_count"] = np.log1p(stats["unique_count"])
        stats = stats.rename(columns={
            "matched_task": "task_path",
            "log_unique_count": "log_unique_paper_count_at_intro",
            "diversity_ratio": "paper_diversity_ratio_at_intro",
        })
        print(f"Aggregated diversity stats for {len(stats)} benchmarks")
        return stats

    def z_standardize(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        stats_df = stats_df.copy()
        for col, z_col in [
            ("log_unique_paper_count_at_intro", "log_unique_paper_count_at_intro_z"),
            ("paper_diversity_ratio_at_intro", "paper_diversity_ratio_at_intro_z"),
        ]:
            mean_ = stats_df[col].mean()
            std_ = stats_df[col].std()
            if std_ == 0:
                raise ValueError(f"Zero std for {col} — cannot z-standardize")
            stats_df[z_col] = (stats_df[col] - mean_) / std_
        return stats_df
