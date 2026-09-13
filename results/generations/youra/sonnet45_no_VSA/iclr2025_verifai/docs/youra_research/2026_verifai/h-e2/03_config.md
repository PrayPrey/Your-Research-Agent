# Configuration Design: H-E2

**Date:** 2026-07-11  
**Hypothesis:** Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories  
**Type:** EXISTENCE (PoC) - Minimal configuration for "does it work?" validation  
**Format:** YAML configuration file + Python dataclass wrapper  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: Green-field project - designing new config schema  
**Config Files Found**: None - new config design  
**Pattern Used**: YAML config + Python dataclass wrapper  

**Rationale**: This is a taxonomy analysis experiment with no existing codebase. Configuration pattern selected based on research experiment best practices (reproducibility via YAML files, type-safe loading via dataclasses).

---

## Configuration Schema

### Applied Pattern
YAML configuration with dataclass wrapper (standard for research experiments with external tool dependencies and data paths).

### Core Configuration (YAML)

```yaml
# config.yaml - H-E2 Cross-Verifier Taxonomy Configuration
# EXISTENCE PoC: Minimal config to test "does it work?"

experiment:
  name: "h-e2-taxonomy-poc"
  hypothesis: "Cross-verifier semantic primitives exist"
  seed: 42
  output_dir: "./results"

verifiers:
  frama_c:
    version: "28.1"
    install_path: "/usr/local/bin/frama-c"
    wp_plugin: true
    timeout_seconds: 300
    # Minimal command-line flags for PoC
    flags: ["-wp", "-wp-prover", "alt-ergo"]
  
  dafny:
    version: "4.9.0"
    install_path: "/usr/local/bin/dafny"
    timeout_seconds: 300
    flags: ["/compile:0", "/timeLimit:10"]
  
  why3:
    version: "1.7.2"
    install_path: "/usr/local/bin/why3"
    timeout_seconds: 300
    # SMT solvers
    provers:
      - name: "Alt-Ergo"
        version: "2.5.2"
      - name: "Z3"
        version: "4.12.1"
    flags: ["--timeout", "10"]

datasets:
  # Minimal benchmark selection for PoC
  frama_c_examples:
    source: "git"
    url: "https://git.frama-c.com/pub/frama-c.git"
    branch: "28.1"
    path: "tests/wp"
    # PoC: Use only first 10 examples
    sample_size: 10
  
  juliet_subset:
    source: "manual"
    # Juliet Test Suite CWE categories relevant to verification
    path: "./data/juliet_subset"
    cwe_categories: ["CWE-190", "CWE-476", "CWE-457"]
    sample_size: 10
  
  why3_gallery:
    source: "git"
    url: "https://gitlab.inria.fr/why3/why3.git"
    branch: "1.7.2"
    path: "examples"
    sample_size: 10

taxonomy:
  # Semantic primitives (fixed for EXISTENCE PoC)
  primitives:
    - MISSING_PRECONDITION
    - POSTCONDITION_FAILURE
    - LOOP_INVARIANT_VIOLATION
    - BOUNDS_CHECK_FAILURE
    - ARITHMETIC_OVERFLOW
    - NULL_DEREFERENCE
    - TERMINATION_FAILURE
    - TYPE_MISMATCH
  
  # Mapping parameters
  confidence_threshold: 0.5
  allow_multi_mapping: true

evaluation:
  # Success thresholds (from PRD)
  coverage_target: 0.80
  min_error_instances_per_verifier: 30
  # PoC uses smaller total samples
  total_evaluation_samples: 100
  
  # Visualization
  figure_format: "png"
  figure_dpi: 300
  save_figures: true

paths:
  # Input documentation URLs (for extraction phase)
  docs:
    frama_c_vc_api: "https://frama-c.com/api/frama-c-wp/Wp/VC/index.html"
    dafny_errors: "https://dafny.org/v3.12.0/HowToFAQ/Errors"
    why3_model_parser: "https://why3.org/api/Model_parser.html"
  
  # Output paths
  output:
    error_categories: "data/error_categories.json"
    semantic_primitives: "data/semantic_primitives.yaml"
    taxonomy_mapping: "data/taxonomy_mapping.json"
    coverage_report: "results/coverage_report.json"
    figures_dir: "figures/"
```

### Python Dataclass Wrapper

```python
# config.py - Type-safe configuration loader

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import yaml
from pathlib import Path


@dataclass
class VerifierConfig:
    """Configuration for a single verification tool."""
    version: str
    install_path: str
    timeout_seconds: int
    flags: List[str]
    wp_plugin: bool = False
    provers: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class DatasetConfig:
    """Configuration for benchmark dataset source."""
    source: str  # "git" | "manual"
    sample_size: int
    url: Optional[str] = None
    branch: Optional[str] = None
    path: Optional[str] = None
    cwe_categories: Optional[List[str]] = None


@dataclass
class TaxonomyConfig:
    """Taxonomy construction parameters."""
    primitives: List[str]
    confidence_threshold: float
    allow_multi_mapping: bool


@dataclass
class EvaluationConfig:
    """Evaluation thresholds and visualization settings."""
    coverage_target: float
    min_error_instances_per_verifier: int
    total_evaluation_samples: int
    figure_format: str
    figure_dpi: int
    save_figures: bool


@dataclass
class PathsConfig:
    """Input/output file paths."""
    docs: Dict[str, str]
    output: Dict[str, str]


@dataclass
class ExperimentConfig:
    """Top-level experiment configuration."""
    name: str
    hypothesis: str
    seed: int
    output_dir: str
    verifiers: Dict[str, VerifierConfig]
    datasets: Dict[str, DatasetConfig]
    taxonomy: TaxonomyConfig
    evaluation: EvaluationConfig
    paths: PathsConfig


def load_config(config_path: str = "config.yaml") -> ExperimentConfig:
    """
    Load YAML configuration and parse into type-safe dataclass.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        ExperimentConfig instance with validated settings
    """
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    # Parse nested structures
    verifiers = {
        name: VerifierConfig(**cfg)
        for name, cfg in raw_config['verifiers'].items()
    }
    
    datasets = {
        name: DatasetConfig(**cfg)
        for name, cfg in raw_config['datasets'].items()
    }
    
    taxonomy = TaxonomyConfig(**raw_config['taxonomy'])
    evaluation = EvaluationConfig(**raw_config['evaluation'])
    paths = PathsConfig(**raw_config['paths'])
    
    return ExperimentConfig(
        **raw_config['experiment'],
        verifiers=verifiers,
        datasets=datasets,
        taxonomy=taxonomy,
        evaluation=evaluation,
        paths=paths
    )
```

---

## Configuration Rationale

### EXISTENCE PoC Simplifications

**From Full PRD Requirements → PoC Config:**

1. **Sample Sizes Reduced**:
   - PRD: 100+ error instances per verifier, 500+ total
   - PoC: 30 per verifier, 100 total
   - Justification: PoC only needs to demonstrate coverage feasibility, not statistical significance

2. **Single Seed**:
   - No hyperparameter variations (fixed seed=42)
   - Justification: Taxonomy construction is deterministic

3. **Minimal Benchmark Programs**:
   - 10 samples per dataset (vs. full repositories)
   - Justification: PoC validates mapping logic, not coverage exhaustiveness

4. **Fixed Primitive Set**:
   - 8 primitives from experiment brief (no clustering exploration)
   - Justification: PoC tests mapping, not primitive discovery

### Non-Standard Values

- `confidence_threshold: 0.5`: Half-confidence cutoff for mapping acceptance (standard heuristic from information retrieval)
- `timeout_seconds: 300`: 5-minute timeout per verification run (prevents hanging on hard programs)
- `allow_multi_mapping: true`: One error can map to multiple primitives (required for edge cases like "loop termination + invariant violation")

---

## Installation Requirements

### Verifier Toolchains

**Frama-C 28.1**:
```bash
# Ubuntu/Debian
sudo apt-get install frama-c
# Verify version
frama-c -version  # Should show 28.1 (Nickel)
```

**Dafny 4.9.0**:
```bash
# Download from GitHub releases
wget https://github.com/dafny-lang/dafny/releases/download/v4.9.0/dafny-4.9.0-x64-ubuntu-20.04.zip
unzip dafny-4.9.0-x64-ubuntu-20.04.zip -d /usr/local/
export PATH=$PATH:/usr/local/dafny
```

**Why3 1.7.2 + SMT Solvers**:
```bash
# Ubuntu/Debian
sudo apt-get install why3
# Install SMT solvers
sudo apt-get install alt-ergo z3
# Configure Why3 to detect provers
why3 config detect
```

### Python Dependencies

```python
# requirements.txt
pyyaml>=6.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
beautifulsoup4>=4.12.0
requests>=2.31.0
```

---

## Usage Example

```python
# main.py - Experiment entry point

from config import load_config
from taxonomy_builder import TaxonomyBuilder

def main():
    # Load configuration
    config = load_config("config.yaml")
    
    # Initialize taxonomy builder
    builder = TaxonomyBuilder(config)
    
    # Phase 1: Extract error categories from documentation + empirical runs
    error_categories = builder.extract_error_categories()
    
    # Phase 2: Map to semantic primitives (uses config.taxonomy.primitives)
    mappings = builder.map_to_primitives(error_categories)
    
    # Phase 3: Compute coverage metrics
    coverage = builder.compute_coverage(mappings)
    
    # Gate validation
    if coverage >= config.evaluation.coverage_target:
        print(f"✓ PoC SUCCESS: Coverage {coverage:.1%} ≥ {config.evaluation.coverage_target:.0%}")
    else:
        print(f"✗ PoC FAILURE: Coverage {coverage:.1%} < {config.evaluation.coverage_target:.0%}")
    
    # Save results
    builder.save_results(
        error_categories_path=config.paths.output['error_categories'],
        mappings_path=config.paths.output['taxonomy_mapping'],
        coverage_path=config.paths.output['coverage_report']
    )

if __name__ == "__main__":
    main()
```

---

## Self-Validation Checklist

- [x] ONE format only (YAML + dataclass wrapper)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] EXISTENCE PoC constraints applied (single config, no hyperparameter grid)
- [x] Configuration is copy-paste ready for Phase 4

---

**Status:** READY FOR PHASE 4  
**Next Phase:** Implementation (Phase 4 - Coding Agent)  
**Configuration File Output:** `/workspace/TEST_verifai/docs/youra_research/h-e2/03_config.md`
