from __future__ import annotations
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from datasketch import MinHashLSH

if TYPE_CHECKING:
    from config import Config
    from ngram_extractor import NgramExtractor

logger = logging.getLogger(__name__)


class MatrixBuilder:
    def __init__(self, config: "Config", extractor: "NgramExtractor"):
        self.config = config
        self.extractor = extractor

    def query_cell(
        self,
        subtask_name: str,
        texts: list[str],
        corpus_name: str,
        lsh: MinHashLSH,
    ) -> dict:
        """Compute contamination for one (subtask, corpus) cell."""
        n_contaminated = 0
        for text in texts:
            minhash = self.extractor.text_to_minhash(text)
            if lsh.query(minhash):
                n_contaminated += 1
        n_items = len(texts)
        rate = n_contaminated / n_items if n_items > 0 else 0.0
        logger.info(
            f"Querying {corpus_name} for sub-task {subtask_name}: "
            f"{n_contaminated}/{n_items} contaminated ({rate:.3f})"
        )
        return {
            "subtask": subtask_name,
            "corpus": corpus_name,
            "n_items": n_items,
            "n_contaminated": n_contaminated,
            "rate": rate,
        }

    def build_matrix(
        self,
        benchmarks: dict[str, list[str]],
        indices: dict[str, MinHashLSH],
    ) -> pd.DataFrame:
        """Iterate 59 subtasks × 3 corpora, return DataFrame with 177 rows."""
        rows = []
        total_cells = len(benchmarks) * len(indices)
        for subtask_name, texts in benchmarks.items():
            for corpus_name, lsh in indices.items():
                rows.append(self.query_cell(subtask_name, texts, corpus_name, lsh))
                if len(rows) % 10 == 0:
                    logger.info(f"Matrix: {len(rows)}/{total_cells} cells completed")
        df = pd.DataFrame(rows)
        assert len(df) == 177, f"Expected 177 rows, got {len(df)}"
        out = Path(self.config.results_dir) / "contamination_matrix.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        logger.info(f"Saved contamination matrix to {out}")
        return df

    def to_wide(self, matrix_df: pd.DataFrame) -> pd.DataFrame:
        """Pivot long [177, 5] to wide [59, 3]; index=subtask, columns=corpus."""
        wide = matrix_df.pivot(index="subtask", columns="corpus", values="rate")
        # Ensure standard column order
        for col in ["pile", "c4", "redpajama"]:
            if col not in wide.columns:
                wide[col] = float("nan")
        return wide[["pile", "c4", "redpajama"]]
