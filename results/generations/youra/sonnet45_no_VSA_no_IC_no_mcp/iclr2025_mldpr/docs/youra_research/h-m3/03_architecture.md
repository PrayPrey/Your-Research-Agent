# System Architecture: H-M3
# Dependency-Aware Migration Plans

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** MECHANISM (SHOULD_WORK gate)  
**Prerequisites:** h-e1 (Instrumentation Infrastructure)  
**Applied:** Graph analysis pattern, schema diff pattern, RCT instrumentation pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-e1 instrumentation infrastructure  
**Analyzed Path:** `docs/youra_research/h-e1/code/`  
**Findings:** Reuse TelemetryLogger from h-e1, extend loader hook pattern for deprecation detection

---

## System Overview

Automated migration planning system that constructs dataset dependency graphs from HuggingFace/GitHub/Papers with Code, performs transitive impact analysis, detects schema compatibility, and generates user-specific migration plans. Integrates with h-e1 loader to trigger migration plans on deprecated dataset loads, tracking breaking changes and adoption rates across three RCT groups (Control/Manual/Treatment).

---

## Module Architecture

### 1. Data Collectors (`src/collectors/`)

#### HuggingFaceCollector (`src/collectors/huggingface_collector.py`)

**Dependencies:** `huggingface_hub`, stdlib `json`, `time`

```python
from typing import List, Dict, Any
from huggingface_hub import HfApi

class HuggingFaceCollector:
    def __init__(self, api_key: str = None, cache_dir: str = "data/hf_cache"): ...
    
    def collect_dataset_metadata(self, max_datasets: int = 50000) -> List[Dict[str, Any]]:
        """Fetch dataset cards, schemas, deprecation tags"""
        ...
    
    def collect_download_logs(self, dataset_ids: List[str]) -> Dict[str, int]:
        """Fetch download counts per dataset"""
        ...
    
    def extract_successor_links(self, dataset_card: Dict) -> str:
        """Parse README for successor dataset mention"""
        ...
```

#### GitHubCollector (`src/collectors/github_collector.py`)

**Dependencies:** `requests`, stdlib `re`, `json`

```python
from typing import List, Dict

class GitHubCollector:
    def __init__(self, api_key: str, max_repos: int = 10000): ...
    
    def search_load_dataset_calls(self) -> List[Dict[str, str]]:
        """
        Search for load_dataset("*") patterns in ML repos.
        
        Returns:
            [{repo, file_path, dataset_name, code_context}]
        """
        ...
    
    def extract_dependencies(self, code_snippet: str) -> List[str]:
        """Parse dataset names from code via regex"""
        ...
```

#### PapersWithCodeCollector (`src/collectors/pwc_collector.py`)

**Dependencies:** `requests`, stdlib `json`

```python
from typing import List, Dict

class PapersWithCodeCollector:
    def __init__(self, api_base_url: str = "https://paperswithcode.com/api/v1"): ...
    
    def collect_model_dataset_citations(self) -> List[Dict[str, str]]:
        """
        Fetch model-dataset usage from Papers with Code.
        
        Returns:
            [{model_id, dataset_id, paper_url}]
        """
        ...
```

### 2. Dependency Graph Builder (`src/graph_builder.py`)

**Dependencies:** Collectors, `networkx`, stdlib `json`, `pickle`

```python
import networkx as nx
from typing import Dict, List, Any
from pathlib import Path

class DependencyGraphBuilder:
    def __init__(self, cache_dir: Path = Path("data/graphs")): ...
    
    def build_graph(
        self,
        hf_metadata: List[Dict],
        github_deps: List[Dict],
        pwc_citations: List[Dict]
    ) -> nx.DiGraph:
        """
        Construct G = (V, E) where:
        - V = datasets (deprecated + active)
        - E = (dataset, dependent_entity) with type metadata
        """
        ...
    
    def add_dataset_nodes(self, graph: nx.DiGraph, metadata: List[Dict]) -> None:
        """Add nodes with schema, deprecation status, successor"""
        ...
    
    def add_usage_edges(self, graph: nx.DiGraph, deps: List[Dict]) -> None:
        """Add edges with entity_type (model/pipeline/script)"""
        ...
    
    def handle_cycles(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Detect SCC, collapse cycles into super-nodes"""
        ...
    
    def save_graph(self, graph: nx.DiGraph, path: Path) -> None:
        """Serialize to JSON + pickle"""
        ...
    
    def load_graph(self, path: Path) -> nx.DiGraph:
        """Load from pickle cache"""
        ...
```

### 3. Impact Analyzer (`src/impact_analyzer.py`)

**Dependencies:** `networkx`, stdlib `statistics`

```python
import networkx as nx
from typing import Set, Dict, Any

class ImpactAnalyzer:
    def __init__(self, graph: nx.DiGraph): ...
    
    def compute_transitive_closure(self, deprecated_dataset: str) -> Set[str]:
        """
        Find all descendants of deprecated_dataset.
        
        Uses NetworkX descendants() for transitive closure.
        """
        ...
    
    def compute_impact_radius(self, deprecated_dataset: str) -> Dict[str, Any]:
        """
        Return:
            {
                'total_affected': int,
                'by_type': {'model': int, 'pipeline': int, 'script': int},
                'by_depth': {1: int, 2: int, ..., 6+: int}
            }
        """
        ...
    
    def group_by_entity_type(self, affected_nodes: Set[str]) -> Dict[str, int]:
        """Categorize by edge metadata 'entity_type'"""
        ...
    
    def compute_depth_distribution(
        self,
        deprecated_dataset: str,
        affected_nodes: Set[str]
    ) -> Dict[int, int]:
        """BFS depth from deprecated_dataset to each affected node"""
        ...
```

### 4. Schema Compatibility Detector (`src/schema_diff.py`)

**Dependencies:** `deepdiff`, stdlib `difflib`

```python
from typing import Dict, List, Any, Tuple
from enum import Enum

class Severity(Enum):
    COMPATIBLE = "COMPATIBLE"
    MINOR_BREAKING = "MINOR_BREAKING"
    MAJOR_BREAKING = "MAJOR_BREAKING"

class BreakingChange:
    def __init__(
        self,
        change_type: str,
        field: str,
        severity: Severity,
        old_value: Any = None,
        new_value: Any = None
    ): ...

class SchemaCompatibilityDetector:
    def __init__(self): ...
    
    def detect_breaking_changes(
        self,
        schema1: Dict[str, Any],
        schema2: Dict[str, Any]
    ) -> Tuple[Severity, List[BreakingChange]]:
        """
        Compare schemas at field level.
        
        Returns:
            (overall_severity, breaking_changes_list)
        """
        ...
    
    def detect_field_removals(
        self,
        schema1: Dict,
        schema2: Dict
    ) -> List[BreakingChange]:
        """MAJOR severity"""
        ...
    
    def detect_type_changes(
        self,
        schema1: Dict,
        schema2: Dict
    ) -> List[BreakingChange]:
        """MAJOR if incompatible, MINOR if coercible"""
        ...
    
    def detect_field_renames(
        self,
        schema1: Dict,
        schema2: Dict
    ) -> List[BreakingChange]:
        """Heuristic: edit_distance < 3, MINOR severity"""
        ...
    
    def is_type_compatible(self, type1: str, type2: str) -> bool:
        """Check if type1 can coerce to type2"""
        ...
```

### 5. Adapter Generator (`src/adapter_generator.py`)

**Dependencies:** Schema Diff, stdlib `jinja2`

```python
from typing import List, Dict
from .schema_diff import BreakingChange, Severity

class AdapterGenerator:
    def __init__(self): ...
    
    def generate_adapters(
        self,
        breaking_changes: List[BreakingChange]
    ) -> Dict[str, str]:
        """
        Auto-generate code snippets for MINOR_BREAKING changes.
        
        Returns:
            {change_id: code_snippet}
        """
        ...
    
    def generate_field_rename_adapter(self, old_name: str, new_name: str) -> str:
        """Return: 'dataset = dataset.rename_column("old", "new")'"""
        ...
    
    def generate_type_coercion_adapter(self, field: str, new_type: str) -> str:
        """Return: 'dataset = dataset.cast_column("field", "new_type")'"""
        ...
```

### 6. Migration Planner (`src/migration_planner.py`)

**Dependencies:** Impact Analyzer, Schema Diff, Adapter Generator, `networkx`

```python
import networkx as nx
from typing import Dict, List, Any
from .impact_analyzer import ImpactAnalyzer
from .schema_diff import SchemaCompatibilityDetector
from .adapter_generator import AdapterGenerator

class MigrationPlanner:
    def __init__(
        self,
        graph: nx.DiGraph,
        impact_analyzer: ImpactAnalyzer,
        schema_detector: SchemaCompatibilityDetector,
        adapter_gen: AdapterGenerator
    ): ...
    
    def generate_plan(
        self,
        deprecated_dataset: str,
        successor_dataset: str
    ) -> Dict[str, Any]:
        """
        Orchestrate impact + schema + steps generation.
        
        Returns:
            {
                'deprecated': str,
                'successor': str,
                'impact_radius': {...},
                'compatibility': Severity,
                'breaking_changes': [...],
                'migration_steps': [...],
                'adapters': {...},
                'verification_checklist': [...]
            }
        """
        ...
    
    def generate_migration_steps(
        self,
        affected_nodes: Set[str],
        breaking_changes: List[BreakingChange]
    ) -> List[Dict[str, str]]:
        """
        Topologically sorted task list (leaf-first).
        
        Returns:
            [{step: int, entity: str, action: str, priority: str}]
        """
        ...
    
    def generate_verification_checklist(
        self,
        breaking_changes: List[BreakingChange]
    ) -> List[str]:
        """Tests to run post-migration"""
        ...
```

### 7. Plan Formatter (`src/plan_formatter.py`)

**Dependencies:** Migration Planner, stdlib `json`

```python
from typing import Dict, Any

class PlanFormatter:
    def __init__(self): ...
    
    def format_text(self, plan: Dict[str, Any]) -> str:
        """Generate human-readable text report"""
        ...
    
    def format_json(self, plan: Dict[str, Any]) -> str:
        """Pretty-print JSON"""
        ...
    
    def format_html(self, plan: Dict[str, Any]) -> str:
        """HTML with collapsible sections, syntax highlighting"""
        ...
```

### 8. Instrumented Loader Integration (`src/instrumented_loader.py`)

**Dependencies:** h-e1 TelemetryLogger, Migration Planner, stdlib `hashlib`

```python
from typing import Tuple, Dict, Any
from datasets import load_dataset, Dataset
import hashlib

class InstrumentedLoader:
    def __init__(
        self,
        telemetry: 'TelemetryLogger',
        migration_planner: 'MigrationPlanner',
        deprecation_registry: Dict[str, str]
    ): ...
    
    def load_dataset_with_migration(
        self,
        dataset_name: str,
        user_id: str,
        **kwargs
    ) -> Tuple[Dataset, Dict[str, Any]]:
        """
        Load dataset with deprecation check and migration plan.
        
        Flow:
        1. Check if dataset_name in deprecation_registry
        2. Assign user to group (Control/Manual/Treatment) via hash
        3. Display intervention based on group
        4. Log event
        5. Load dataset
        """
        ...
    
    def assign_user_group(self, user_id: str) -> str:
        """Hash-based deterministic assignment to Control/Manual/Treatment"""
        ...
    
    def display_intervention(
        self,
        group: str,
        dataset_name: str,
        successor: str,
        plan: Dict = None
    ) -> None:
        """Show deprecation notice + appropriate guidance"""
        ...
    
    def log_deprecation_event(
        self,
        user_id: str,
        dataset_name: str,
        group: str,
        action: str
    ) -> None:
        """Log to h-e1 telemetry backend"""
        ...
```

### 9. Outcome Tracker (`src/outcome_tracker.py`)

**Dependencies:** h-e1 TelemetryLogger, stdlib `sqlite3`, `pandas`

```python
import pandas as pd
from typing import Dict, List

class OutcomeTracker:
    def __init__(self, telemetry_db_path: str): ...
    
    def track_breaking_changes(self) -> pd.DataFrame:
        """Query error logs, group by user_group"""
        ...
    
    def track_adoption_events(self, window_days: int = 30) -> pd.DataFrame:
        """Check if successor loaded within window after deprecation notice"""
        ...
    
    def track_bypass_events(self) -> pd.DataFrame:
        """Count continued deprecated usage"""
        ...
    
    def compute_metrics_by_group(self) -> Dict[str, Dict[str, float]]:
        """
        Return:
            {
                'Control': {'breaking_change_rate': 0.6, 'adoption_rate': 0.4},
                'Manual': {...},
                'Treatment': {...}
            }
        """
        ...
```

### 10. Ground Truth Validator (`src/ground_truth_validator.py`)

**Dependencies:** Impact Analyzer, Schema Diff, `pandas`

```python
import pandas as pd
from typing import Tuple

class GroundTruthValidator:
    def __init__(
        self,
        ground_truth_csv: str,
        impact_analyzer: 'ImpactAnalyzer',
        schema_detector: 'SchemaCompatibilityDetector'
    ): ...
    
    def validate_impact_completeness(self) -> Tuple[float, float]:
        """
        Precision/Recall on ground truth dependencies.
        
        Returns:
            (precision, recall)
        """
        ...
    
    def validate_schema_accuracy(self) -> float:
        """
        % predicted breaking changes matching annotated labels.
        
        Returns:
            accuracy (0-1)
        """
        ...
```

### 11. Main Entry Point (`main.py`)

**Dependencies:** All modules above

```python
from pathlib import Path
from src.collectors.huggingface_collector import HuggingFaceCollector
from src.collectors.github_collector import GitHubCollector
from src.collectors.pwc_collector import PapersWithCodeCollector
from src.graph_builder import DependencyGraphBuilder
from src.impact_analyzer import ImpactAnalyzer
from src.schema_diff import SchemaCompatibilityDetector
from src.adapter_generator import AdapterGenerator
from src.migration_planner import MigrationPlanner
from src.instrumented_loader import InstrumentedLoader
from src.outcome_tracker import OutcomeTracker
from src.ground_truth_validator import GroundTruthValidator

def main():
    """Full h-m3 pipeline"""
    # Phase 1: Offline graph construction
    hf = HuggingFaceCollector()
    gh = GitHubCollector(api_key="...")
    pwc = PapersWithCodeCollector()
    
    hf_metadata = hf.collect_dataset_metadata(max_datasets=50000)
    github_deps = gh.search_load_dataset_calls()
    pwc_citations = pwc.collect_model_dataset_citations()
    
    builder = DependencyGraphBuilder()
    graph = builder.build_graph(hf_metadata, github_deps, pwc_citations)
    builder.save_graph(graph, Path("data/dependency_graph.pkl"))
    
    # Phase 2: Runtime setup
    impact_analyzer = ImpactAnalyzer(graph)
    schema_detector = SchemaCompatibilityDetector()
    adapter_gen = AdapterGenerator()
    planner = MigrationPlanner(graph, impact_analyzer, schema_detector, adapter_gen)
    
    # Phase 3: Instrumentation integration
    from h_e1.src.telemetry import TelemetryLogger
    telemetry = TelemetryLogger("telemetry.db")
    loader = InstrumentedLoader(telemetry, planner, deprecation_registry={...})
    
    # Phase 4: Validation
    validator = GroundTruthValidator("data/ground_truth.csv", impact_analyzer, schema_detector)
    precision, recall = validator.validate_impact_completeness()
    schema_accuracy = validator.validate_schema_accuracy()
    
    print(f"Impact: P={precision:.2f}, R={recall:.2f}")
    print(f"Schema accuracy: {schema_accuracy:.2f}")
    
    # Phase 5: RCT deployment (6-month observation)
    # Users load datasets via loader.load_dataset_with_migration()
    # Outcome tracked via OutcomeTracker

if __name__ == "__main__":
    main()
```

---

## File Structure

```
h-m3/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── collectors/
│   │   │   ├── __init__.py
│   │   │   ├── huggingface_collector.py
│   │   │   ├── github_collector.py
│   │   │   └── pwc_collector.py
│   │   ├── graph_builder.py
│   │   ├── impact_analyzer.py
│   │   ├── schema_diff.py
│   │   ├── adapter_generator.py
│   │   ├── migration_planner.py
│   │   ├── plan_formatter.py
│   │   ├── instrumented_loader.py
│   │   ├── outcome_tracker.py
│   │   └── ground_truth_validator.py
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── data/
│   ├── hf_cache/                    # HuggingFace metadata
│   ├── dependency_graph.pkl         # NetworkX graph cache
│   ├── dependency_graph.json        # Human-readable export
│   ├── ground_truth.csv             # 100 annotated pairs
│   └── deprecation_registry.json    # Deprecated → Successor mapping
├── telemetry.db                     # SQLite events (from h-e1)
└── figures/                         # Outcome visualizations
```

---

## External Dependencies (h-e1 Integration)

### Module Paths (From h-e1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TelemetryLogger | `from h_e1.src.telemetry import TelemetryLogger` | `h-e1/code/src/telemetry.py` |

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation)

**Note:** Import paths assume h-e1 code is in Python path. Update imports based on actual deployment structure.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Data Collection | Implement 3 collectors (HF/GitHub/PwC), aggregate 50k datasets + 100k edges | 14 | 4+3+4+3 |
| M-2 | Graph Construction | Implement graph builder, cycle detection, serialization, load 50k nodes | 12 | 3+3+4+2 |
| M-3 | Impact Analysis | Transitive closure, depth distribution, entity grouping, performance < 10s | 11 | 3+2+3+3 |
| M-4 | Schema Compatibility | Field-level diff, breaking change classification, rename heuristic | 13 | 4+3+3+3 |
| M-5 | Adapter Generation | Code templates for rename/coercion, jinja2 integration | 8 | 2+2+2+2 |
| M-6 | Migration Planning | Orchestrate impact + schema, topological sort, verification checklist | 12 | 3+3+4+2 |
| M-7 | Instrumentation Integration | Hook into h-e1 loader, user group assignment, event logging | 11 | 3+2+4+2 |
| M-8 | Outcome Tracking | SQL queries for breaking changes/adoption, metrics per group | 10 | 3+2+3+2 |
| M-9 | Validation | Ground truth precision/recall, schema accuracy on 100 labels | 9 | 2+2+3+2 |
| M-10 | Plan Formatting | Text/JSON/HTML formatters, collapsible sections | 7 | 2+1+2+2 |

**Complexity Breakdown:** Module_Size + Dependencies + Algorithm + Integration (each 1-5)

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [M-1, M-4]
- Medium (9-13): [M-2, M-3, M-6, M-7, M-8, M-9]
- Low (4-8): [M-5, M-10]

**Total:** 10 Epic tasks (SHOULD_WORK scope)

---

## Task Decomposition

### M-1: Data Collection (Complexity: 14)

**Files:** `src/collectors/*.py`

**Subtasks:**
1. HuggingFaceCollector: Fetch 50k dataset metadata via HF API
2. GitHubCollector: Search code for `load_dataset()` patterns
3. PapersWithCodeCollector: Extract model-dataset citations
4. Aggregate raw data, deduplicate edges

**Acceptance:**
- 50k dataset metadata cached
- 100k usage edges extracted
- Coverage ≥ 50% of ground truth

### M-2: Graph Construction (Complexity: 12)

**Files:** `src/graph_builder.py`

**Subtasks:**
1. NetworkX DiGraph with dataset nodes + usage edges
2. SCC detection for cycle handling
3. Save to pickle + JSON
4. Load from cache in < 1s

**Acceptance:**
- Graph with 50k nodes, 100k edges
- Cycles collapsed into super-nodes
- Serialization round-trip successful

### M-3: Impact Analysis (Complexity: 11)

**Files:** `src/impact_analyzer.py`

**Subtasks:**
1. Transitive closure via `nx.descendants()`
2. Depth distribution via BFS
3. Entity type grouping from edge metadata
4. Performance benchmark on 1000 deprecated datasets

**Acceptance:**
- Transitive closure < 10s per dataset
- Depth distribution histogram generated
- Ground truth recall ≥ 95%

### M-4: Schema Compatibility (Complexity: 13)

**Files:** `src/schema_diff.py`

**Subtasks:**
1. Field-level diff: removals, additions, type changes
2. Compatibility classification logic
3. Rename heuristic (edit distance < 3)
4. Validation on 100 ground truth labels

**Acceptance:**
- Breaking changes detected with severity
- Schema accuracy ≥ 80%
- False positive rate ≤ 30%

### M-5: Adapter Generation (Complexity: 8)

**Files:** `src/adapter_generator.py`

**Subtasks:**
1. Code templates for rename/coercion
2. Jinja2 template rendering
3. Works for 80% of MINOR_BREAKING cases

**Acceptance:**
- Generated code is syntactically valid
- Adapters apply successfully to test datasets

### M-6: Migration Planning (Complexity: 12)

**Files:** `src/migration_planner.py`

**Subtasks:**
1. Orchestrate impact analyzer + schema detector
2. Topological sort for migration order
3. Generate verification checklist
4. JSON plan generation < 5s

**Acceptance:**
- Plan contains all required sections
- Migration steps in correct order (leaf-first)
- Latency < 5s for 1000-node impact radius

### M-7: Instrumentation Integration (Complexity: 11)

**Files:** `src/instrumented_loader.py`

**Subtasks:**
1. Hook into h-e1 telemetry logger
2. Hash-based user group assignment
3. Display intervention per group
4. Log deprecation events

**Acceptance:**
- User group assignment deterministic
- Events logged to h-e1 telemetry.db
- Overhead < 10%

### M-8: Outcome Tracking (Complexity: 10)

**Files:** `src/outcome_tracker.py`

**Subtasks:**
1. SQL queries for breaking changes (error logs)
2. SQL queries for adoption (successor loads)
3. Metrics computation per group (Control/Manual/Treatment)
4. DataFrame export for analysis

**Acceptance:**
- Breaking change rate computed correctly
- Adoption rate within 30-day window
- Metrics aggregated by group

### M-9: Validation (Complexity: 9)

**Files:** `src/ground_truth_validator.py`

**Subtasks:**
1. Precision/Recall for impact completeness
2. Accuracy for schema compatibility
3. Report generation

**Acceptance:**
- Impact recall ≥ 95%
- Schema accuracy ≥ 80%
- Report shows both metrics

### M-10: Plan Formatting (Complexity: 7)

**Files:** `src/plan_formatter.py`

**Subtasks:**
1. Text formatter with sections
2. JSON pretty-print
3. HTML with collapsible sections
4. Syntax highlighting for code snippets

**Acceptance:**
- All 3 formats render correctly
- HTML includes CSS for highlighting

---

## Data Flow

```
OFFLINE PHASE (One-time graph construction)
1. Data Collection
   └─> HF/GitHub/PwC Collectors
       └─> Raw metadata + usage edges
2. Graph Building
   └─> DependencyGraphBuilder
       └─> NetworkX DiGraph (50k nodes)
       └─> Save to data/dependency_graph.pkl

RUNTIME PHASE (Per user interaction)
1. Dataset Load Request
   └─> InstrumentedLoader.load_dataset_with_migration()
       └─> Check deprecation_registry
       └─> Assign user group (hash-based)
2. Migration Plan Generation (if Treatment group)
   └─> MigrationPlanner.generate_plan()
       └─> ImpactAnalyzer.compute_impact_radius()
       └─> SchemaCompatibilityDetector.detect_breaking_changes()
       └─> AdapterGenerator.generate_adapters()
       └─> Generate steps + checklist
3. Intervention Display
   └─> PlanFormatter.format_text/html()
   └─> Display to user
4. Event Logging
   └─> TelemetryLogger.log_event() [h-e1]

OBSERVATION PHASE (6-month RCT)
1. Event Tracking
   └─> OutcomeTracker.track_*()
       └─> Query telemetry.db for breaking changes/adoption
2. Metrics Computation
   └─> OutcomeTracker.compute_metrics_by_group()
       └─> Breaking change rate, adoption rate per group
3. Statistical Analysis
   └─> Chi-squared tests (Control vs Treatment)
```

---

## Success Criteria Mapping

| Gate Metric | Target | Implementation | Validation |
|-------------|--------|----------------|------------|
| Breaking change reduction | ≥ 40% | Migration plan prevents errors | `OutcomeTracker.compute_metrics_by_group()` |
| Adoption rate increase | ≥ 25% | Migration plan increases confidence | `OutcomeTracker.track_adoption_events()` |
| Impact completeness | ≥ 95% | Transitive closure recall | `GroundTruthValidator.validate_impact_completeness()` |
| Migration plan accuracy | ≥ 80% | Schema diff accuracy | `GroundTruthValidator.validate_schema_accuracy()` |

---

## Dependencies

**External:**
- `networkx` (graph algorithms)
- `huggingface_hub` (HF API)
- `requests` (GitHub/PwC APIs)
- `deepdiff` (schema comparison)
- `jinja2` (adapter templates)
- `pandas` (outcome analysis)
- `matplotlib` (visualization)
- Python 3.8+ stdlib: `json`, `pickle`, `sqlite3`, `hashlib`, `re`, `difflib`, `statistics`, `time`

**Internal:**
- h-e1: `TelemetryLogger` (for event logging)

---

## Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Graph construction | < 1 hour | One-time offline |
| Transitive closure | < 10s | Per deprecated dataset (50k node graph) |
| Schema diff | < 100ms | Per dataset pair |
| Migration plan generation | < 5s | Per user interaction |
| Instrumentation overhead | < 10% | Dataset load time delta |

---

## RCT Experimental Design

### User Group Assignment

```python
def assign_user_group(user_id: str) -> str:
    hash_val = int(hashlib.sha256(user_id.encode()).hexdigest(), 16)
    group_idx = hash_val % 3
    return ['Control', 'Manual', 'Treatment'][group_idx]
```

### Intervention by Group

| Group | Deprecation Notice | Migration Guide | Automated Plan |
|-------|-------------------|-----------------|----------------|
| Control | Yes | No | No |
| Manual | Yes | Yes (link to human-written guide) | No |
| Treatment | Yes | No | Yes (dependency-aware plan) |

### Outcome Metrics

| Metric | Formula | Data Source |
|--------|---------|-------------|
| Breaking change rate | Errors / Migration attempts | `telemetry.db` error logs |
| Adoption rate | Successor loads / Deprecation notices | `telemetry.db` load events within 30 days |
| Time to migration | Median days from notice to successor load | `telemetry.db` timestamp diffs |

---

## Privacy Compliance

**Inherited from h-e1:**
- User IDs hashed via SHA256 (16-char truncation)
- No dataset content captured
- Opt-in/opt-out support
- No PII in telemetry logs

**Additional h-m3 measures:**
- No code snippets stored (only dataset names)
- Migration plans generated on-the-fly (not cached with user info)

---

## Validation Checklist

- [ ] All 10 modules implement interface signatures
- [ ] Graph construction handles 50k datasets
- [ ] Transitive closure < 10s
- [ ] Schema diff accuracy ≥ 80% on ground truth
- [ ] Impact recall ≥ 95% on ground truth
- [ ] Migration plan generation < 5s
- [ ] h-e1 integration: events logged to shared telemetry.db
- [ ] User group assignment deterministic and balanced
- [ ] RCT sample size (600 users) supports statistical power
- [ ] 6-month observation period tracked

---

**End of Architecture Specification**
