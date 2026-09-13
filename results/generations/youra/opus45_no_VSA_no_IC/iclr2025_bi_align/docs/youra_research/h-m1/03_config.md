# H-M1 Configuration

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (hardcoded dict)
**Pattern Used**: Pydantic `BaseSettings` (h-m1 is standalone; h-e1's dict format not reused directly — only its `output_dir="outputs/"` convention referenced for path defaults)

**Verified fields from h-e1 config.py**: `output_dir: "outputs/"`, `seed: 42`, `batch_size: 8` — confirms h-e1 outputs live under `docs/youra_research/h-e1/code/outputs/`.

---

## A-1: Config Module [Complexity: 1, Budget: 1]

**Applied**: Standard Pydantic Settings pattern (env + CLI override)

### Configuration (Pydantic Model)

```python
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

class HM1Config(BaseSettings):
    model_config = {"env_prefix": "HM1_"}

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    batch_size: int = 64
    h_e1_output_dir: Path = Path("docs/youra_research/h-e1/code/outputs")
    output_dir: Path = Path("docs/youra_research/h-m1/code/outputs")
    bootstrap_samples: int = 1000
    random_seed: int = 42

    # Derived input files (h-e1 outputs)
    @property
    def rm_scores_path(self) -> Path:
        return self.h_e1_output_dir / "rm_scores.parquet"

    @property
    def mode_dist_path(self) -> Path:
        return self.h_e1_output_dir / "mode_distribution.json"

    # Derived output files
    @property
    def embeddings_path(self) -> Path:
        return self.output_dir / "embeddings.npz"

    @property
    def similarity_scores_path(self) -> Path:
        return self.output_dir / "similarity_scores.parquet"

    @property
    def stats_path(self) -> Path:
        return self.output_dir / "statistical_results.json"

    # Fixed by hypothesis (not configurable via CLI)
    min_samples_per_mode: int = 500
    mode_1_label: int = 1
    mode_3_label: int = 3
```

### YAML Schema (optional override file)

```yaml
# config.yaml
embedding_model: sentence-transformers/all-MiniLM-L6-v2
batch_size: 64
h_e1_output_dir: docs/youra_research/h-e1/code/outputs
output_dir: docs/youra_research/h-m1/code/outputs
bootstrap_samples: 1000
random_seed: 42
```

Load via: `HM1Config(**yaml.safe_load(open("config.yaml")))`

### CLI Args

```python
import argparse

def parse_args() -> HM1Config:
    p = argparse.ArgumentParser(description="H-M1 semantic similarity analysis")
    p.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2")
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--h-e1-output-dir", type=Path, default=Path("docs/youra_research/h-e1/code/outputs"))
    p.add_argument("--output-dir", type=Path, default=Path("docs/youra_research/h-m1/code/outputs"))
    p.add_argument("--bootstrap-samples", type=int, default=1000)
    p.add_argument("--random-seed", type=int, default=42)
    args = p.parse_args()
    return HM1Config(
        embedding_model=args.embedding_model,
        batch_size=args.batch_size,
        h_e1_output_dir=args.h_e1_output_dir,
        output_dir=args.output_dir,
        bootstrap_samples=args.bootstrap_samples,
        random_seed=args.random_seed,
    )
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Config module | `HM1Config` (Pydantic) + YAML loader + CLI parser in `code/config.py` |
