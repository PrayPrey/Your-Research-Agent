"""A-4: Benchmark N-grams — extract char n-gram sets from benchmark test items."""
import pickle
from pathlib import Path
from typing import Optional

from config import BENCHMARKS, NGRAM_SIZE, CHECKPOINT_DIR


def _get_task_docs(task_name: str):
    """Load task test docs via lm_eval API (v0.4.x compatible)."""
    try:
        from lm_eval.tasks import TaskManager
        tm = TaskManager()
        task_dict = tm.load_task_or_group([task_name])
        if not task_dict:
            raise ValueError(f"Task {task_name} not found")
        task_obj = list(task_dict.values())[0]
        if hasattr(task_obj, 'test_docs'):
            docs = list(task_obj.test_docs())
        elif hasattr(task_obj, 'validation_docs'):
            docs = list(task_obj.validation_docs())
        else:
            docs = []
        return task_obj, docs
    except Exception as e:
        raise RuntimeError(f"Failed to load task {task_name}: {e}")


def _doc_to_text(task_obj, doc: dict) -> str:
    """Extract text from a benchmark doc."""
    try:
        return task_obj.doc_to_text(doc)
    except Exception:
        # Fallback: concatenate known text fields
        parts = []
        for key in ("question", "sentence", "ctx", "passage", "text", "premise"):
            if key in doc and isinstance(doc[key], str):
                parts.append(doc[key])
        return " ".join(parts) if parts else str(doc)


def extract_ngrams(
    benchmarks: list[str] = BENCHMARKS,
    n: int = NGRAM_SIZE,
    checkpoint_path: Optional[Path] = None,
) -> dict[str, frozenset]:
    """Return {benchmark_name: frozenset_of_char_ngrams} from full test sets."""
    if checkpoint_path is None:
        checkpoint_path = CHECKPOINT_DIR / f"ngram_sets_n{n}.pkl"

    if checkpoint_path.exists():
        print(f"✓ Loading ngram_sets (n={n}) from checkpoint")
        with open(checkpoint_path, "rb") as f:
            return pickle.load(f)

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    ngram_sets: dict[str, frozenset] = {}

    for bm in benchmarks:
        print(f"  Extracting {n}-grams from {bm}...")
        try:
            task_obj, docs = _get_task_docs(bm)
            ngrams: set[str] = set()
            for doc in docs:
                text = _doc_to_text(task_obj, doc)
                for i in range(len(text) - n + 1):
                    ngrams.add(text[i:i + n])
            ngram_sets[bm] = frozenset(ngrams)
            print(f"    {bm}: {len(docs)} test items → {len(ngrams):,} unique {n}-grams")
        except Exception as e:
            print(f"    WARNING: {bm} load failed ({e}), using empty set")
            ngram_sets[bm] = frozenset()

    with open(checkpoint_path, "wb") as f:
        pickle.dump(ngram_sets, f, protocol=5)
    print(f"✓ ngram_sets saved to {checkpoint_path}")
    return ngram_sets
