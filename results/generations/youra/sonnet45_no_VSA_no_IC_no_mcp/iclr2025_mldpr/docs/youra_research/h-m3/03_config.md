# Configuration Specification: H-M3
# Dependency-Aware Migration Plans

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** SHOULD_WORK (Mechanism Validation)  
**Applied:** Hardcoded dict pattern (h-e1 consistency), RCT configuration pattern

---

## Codebase Analysis (Serena)

**Project Type:** Extends h-e1 (prerequisite)  
**Status:** Config classes verified from base code  
**Config Files Found:** h-e1/code/src/config.py  
**Pattern Used:** Hardcoded dict (consistent with h-e1)

---

## Inherited Configuration (h-e1)

The following config is inherited from h-e1 instrumentation infrastructure:

```python
# From: h-e1/code/src/config.py (ACTUAL CODE)
INSTRUMENTATION_CONFIG = {
    "telemetry": {
        "db_path": "telemetry.db",
        "opt_in": True,
        "hash_algorithm": "sha256",
        "hash_truncate_length": 16
    }
}
```

**Verified from:** h-e1/code/src/ (actual implementation)

---

## M-3-1: Data Collection (Complexity: 3, Budget: 3 subtasks)

**Applied:** API client pattern with rate limiting, caching

### Configuration (Hardcoded Dict)

```python
# src/config.py
DATA_COLLECTION_CONFIG = {
    # HuggingFace API
    "huggingface": {
        "api_token_env": "HF_API_TOKEN",
        "rate_limit_rpm": 60,
        "batch_size": 100,
        "max_datasets": 50000,
        "cache_ttl_hours": 24,
        "request_timeout_sec": 30,
        "retry_attempts": 3,
        "retry_backoff_factor": 2
    },
    
    # GitHub Code Search
    "github": {
        "api_token_env": "GITHUB_API_TOKEN",
        "rate_limit_rpm": 30,
        "search_queries": [
            'load_dataset language:python',
            'datasets.load_dataset language:python',
            'from datasets import load_dataset'
        ],
        "max_repos": 10000,
        "max_files_per_repo": 50,
        "cache_ttl_hours": 168,  # 7 days
        "request_timeout_sec": 60
    },
    
    # Papers with Code
    "paperswithcode": {
        "base_url": "https://paperswithcode.com/api/v1",
        "rate_limit_rpm": 120,
        "cache_ttl_hours": 168,  # 7 days
        "request_timeout_sec": 30
    },
    
    # Local cache
    "cache": {
        "backend": "sqlite",
        "db_path": "cache.db",
        "max_size_gb": 5
    }
}
```

### Subtasks (3/3 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-1-1 | HuggingFace collector | Fetch dataset metadata, schemas, download logs |
| M-3-1-2 | GitHub collector | Search for `load_dataset()` patterns, extract dependencies |
| M-3-1-3 | Papers with Code collector | Extract model-dataset citations |

---

## M-3-2: Graph Construction (Complexity: 4, Budget: 3 subtasks)

**Applied:** NetworkX graph pattern, SCC decomposition for cycle handling

### Configuration (Hardcoded Dict)

```python
GRAPH_CONSTRUCTION_CONFIG = {
    # Graph building
    "graph": {
        "min_edge_confidence": 0.3,
        "max_nodes": 50000,
        "cycle_handling": "scc_decomposition",
        "scc_max_size": 100,
        "serialization_format": "json"
    },
    
    # Edge weighting
    "edge_confidence": {
        "code_mention": 0.8,
        "dataset_card_link": 0.9,
        "download_log": 0.5,
        "papers_citation": 0.95
    },
    
    # Node metadata
    "node_attributes": [
        "schema",
        "deprecated",
        "successor_id",
        "download_count",
        "last_updated"
    ],
    
    # Performance
    "performance": {
        "construction_timeout_sec": 3600,
        "serialize_compression": "gzip",
        "output_path": "dependency_graph.json.gz"
    }
}
```

### Subtasks (3/3 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-2-1 | Graph builder | Build NetworkX DiGraph from collected data |
| M-3-2-2 | Cycle handler | SCC decomposition, tie-breaking |
| M-3-2-3 | Graph serializer | JSON export with compression |

---

## M-3-3: Impact Analysis (Complexity: 3, Budget: 2 subtasks)

**Applied:** NetworkX transitive closure, depth-limited traversal

### Configuration (Hardcoded Dict)

```python
IMPACT_ANALYSIS_CONFIG = {
    # Transitive closure
    "closure": {
        "max_depth": 10,
        "timeout_per_dataset_sec": 10,
        "max_affected_entities": 10000
    },
    
    # Entity prioritization
    "entity_priority": {
        "model": 1.0,
        "pipeline": 0.8,
        "notebook": 0.6,
        "script": 0.4
    },
    
    # Grouping thresholds
    "grouping": {
        "depth_bins": [1, 2, 3, 4, 5, 6],
        "min_group_size": 5
    },
    
    # Performance
    "performance": {
        "cache_results": True,
        "cache_ttl_hours": 24
    }
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-3-1 | Impact analyzer | Compute transitive closure, depth distribution |
| M-3-3-2 | Impact validator | Precision/Recall against ground truth |

---

## M-3-4: Schema Compatibility (Complexity: 4, Budget: 3 subtasks)

**Applied:** Field-level diff pattern, edit distance heuristics

### Configuration (Hardcoded Dict)

```python
SCHEMA_DIFF_CONFIG = {
    # Field rename detection
    "rename_detection": {
        "edit_distance_threshold": 3,
        "min_similarity": 0.7,
        "case_sensitive": False
    },
    
    # Type compatibility rules
    "type_compatibility": {
        "compatible_pairs": [
            ("int32", "int64"),
            ("float32", "float64"),
            ("string", "large_string")
        ],
        "incompatible_pairs": [
            ("string", "int"),
            ("bool", "float"),
            ("list", "dict")
        ]
    },
    
    # Severity classification
    "severity": {
        "field_removal": "MAJOR",
        "field_rename": "MINOR",
        "type_incompatible": "MAJOR",
        "type_compatible": "MINOR",
        "field_addition": "COMPATIBLE"
    },
    
    # Adapter generation
    "adapters": {
        "max_adapters_per_plan": 10,
        "template_library": "adapters/templates/"
    }
}
```

### Subtasks (3/3 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-4-1 | Schema diff | Field-level comparison, breaking change detection |
| M-3-4-2 | Compatibility classifier | COMPATIBLE/MINOR_BREAKING/MAJOR_BREAKING |
| M-3-4-3 | Adapter generator | Auto-generate code snippets for MINOR changes |

---

## M-3-5: Migration Plan Generation (Complexity: 4, Budget: 3 subtasks)

**Applied:** Template-based plan generation, topological sort

### Configuration (Hardcoded Dict)

```python
MIGRATION_PLAN_CONFIG = {
    # Plan generation
    "generation": {
        "timeout_sec": 5,
        "max_steps": 50,
        "topological_sort_tie_breaking": "alphabetical"
    },
    
    # Plan structure
    "plan_sections": [
        "impact_radius",
        "breaking_changes",
        "migration_steps",
        "compatibility_adapters",
        "verification_checklist"
    ],
    
    # Template paths
    "templates": {
        "impact_summary": "templates/impact_summary.jinja2",
        "breaking_changes": "templates/breaking_changes.jinja2",
        "migration_steps": "templates/migration_steps.jinja2",
        "verification": "templates/verification.jinja2"
    },
    
    # Pre-computation
    "precompute": {
        "enabled": True,
        "deprecated_datasets_only": True,
        "cache_path": "migration_plans_cache.json"
    }
}
```

### Subtasks (3/3 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-5-1 | Plan generator | Orchestrate impact + schema + steps |
| M-3-5-2 | Plan formatter | JSON → formatted text/HTML |
| M-3-5-3 | Plan cache | Pre-compute plans for known deprecated datasets |

---

## M-3-6: RCT Experiment (Complexity: 5, Budget: 4 subtasks)

**Applied:** Randomized group assignment, stratification by dependency complexity

### Configuration (Hardcoded Dict)

```python
RCT_EXPERIMENT_CONFIG = {
    # Group assignment
    "groups": {
        "control": {
            "name": "Control",
            "intervention": "deprecation_notice_only",
            "sample_size": 200
        },
        "manual": {
            "name": "Manual",
            "intervention": "deprecation_notice_and_manual_guide",
            "sample_size": 200
        },
        "treatment": {
            "name": "Treatment",
            "intervention": "deprecation_notice_and_automated_plan",
            "sample_size": 200
        }
    },
    
    # Randomization
    "randomization": {
        "seed": 42,
        "assignment_method": "user_id_hash",
        "hash_modulo": 3
    },
    
    # Stratification
    "stratification": {
        "enabled": True,
        "variable": "dependency_complexity",
        "bins": {
            "low": {"min_depth": 1, "max_depth": 2},
            "medium": {"min_depth": 3, "max_depth": 5},
            "high": {"min_depth": 6, "max_depth": 999}
        }
    },
    
    # Observation
    "observation": {
        "duration_months": 6,
        "adoption_window_days": 30,
        "breaking_change_detection": "runtime_error_logs"
    },
    
    # Outcome tracking
    "outcomes": {
        "breaking_change_rate": {
            "event_type": "runtime_error",
            "time_window_days": 7
        },
        "adoption_rate": {
            "event_type": "successor_load",
            "time_window_days": 30
        },
        "bypass_rate": {
            "event_type": "continued_deprecated_usage",
            "time_window_days": 30
        }
    }
}
```

### Subtasks (4/4 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-6-1 | Group assignment | Hash-based randomization, stratification |
| M-3-6-2 | Intervention delivery | Display notice/guide/plan per group |
| M-3-6-3 | Outcome tracker | Log breaking changes, adoption, bypass events |
| M-3-6-4 | Statistical analysis | Chi-squared tests, effect size calculation |

---

## M-3-7: Instrumentation Integration (Complexity: 3, Budget: 2 subtasks)

**Applied:** Loader hook pattern from h-e1

### Configuration (Hardcoded Dict)

```python
INSTRUMENTATION_CONFIG = {
    # Loader hook (extends h-e1)
    "loader": {
        "check_deprecation": True,
        "max_check_latency_ms": 100,
        "fallback_on_timeout": "load_without_intervention"
    },
    
    # Event logging (extends h-e1 telemetry)
    "events": {
        "schema_version": "1.0",
        "fields": [
            "user_id_hash",
            "dataset_name",
            "user_group",
            "intervention_type",
            "timestamp",
            "event_type",
            "metadata"
        ],
        "retention_days": 180,
        "opt_out_enabled": True
    },
    
    # Overhead budget
    "performance": {
        "max_overhead_pct": 10.0,
        "plan_generation_timeout_sec": 5,
        "cache_warmup_enabled": True
    }
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-7-1 | Loader hook | Integrate with h-e1 instrumented loader |
| M-3-7-2 | Event logger | Log deprecation notices, plan views, outcomes |

---

## M-3-8: Ground Truth Annotation (Complexity: 2, Budget: 2 subtasks)

**Applied:** Manual annotation protocol, inter-rater reliability

### Configuration (Hardcoded Dict)

```python
GROUND_TRUTH_CONFIG = {
    # Annotation protocol
    "annotation": {
        "sample_size": 100,
        "annotators_per_sample": 2,
        "consensus_threshold": 0.8
    },
    
    # Dependency labels
    "dependency_labels": {
        "affected": "Entity is transitively affected by deprecation",
        "unaffected": "Entity is not affected",
        "uncertain": "Cannot determine from available information"
    },
    
    # Schema compatibility labels
    "schema_labels": {
        "compatible": "Drop-in replacement",
        "minor_breaking": "Field renames or additions only",
        "major_breaking": "Field removals or type incompatibilities"
    },
    
    # Output format
    "output": {
        "format": "csv",
        "path": "ground_truth_labels.csv",
        "columns": [
            "dataset_id",
            "successor_id",
            "affected_entity_id",
            "dependency_label",
            "schema_label",
            "annotator_id"
        ]
    }
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-8-1 | Dependency annotation | Label 100 dataset-entity pairs |
| M-3-8-2 | Schema annotation | Label 100 schema compatibility pairs |

---

## Configuration Access Pattern

```python
# Import all configs
from src.config import (
    DATA_COLLECTION_CONFIG,
    GRAPH_CONSTRUCTION_CONFIG,
    IMPACT_ANALYSIS_CONFIG,
    SCHEMA_DIFF_CONFIG,
    MIGRATION_PLAN_CONFIG,
    RCT_EXPERIMENT_CONFIG,
    INSTRUMENTATION_CONFIG,
    GROUND_TRUTH_CONFIG
)

# Data collection
hf_collector = HuggingFaceCollector(
    api_token=os.getenv(DATA_COLLECTION_CONFIG["huggingface"]["api_token_env"]),
    rate_limit=DATA_COLLECTION_CONFIG["huggingface"]["rate_limit_rpm"],
    batch_size=DATA_COLLECTION_CONFIG["huggingface"]["batch_size"]
)

# Graph construction
builder = GraphBuilder(
    min_confidence=GRAPH_CONSTRUCTION_CONFIG["graph"]["min_edge_confidence"],
    cycle_handling=GRAPH_CONSTRUCTION_CONFIG["graph"]["cycle_handling"]
)

# Impact analysis
analyzer = ImpactAnalyzer(
    max_depth=IMPACT_ANALYSIS_CONFIG["closure"]["max_depth"],
    timeout=IMPACT_ANALYSIS_CONFIG["closure"]["timeout_per_dataset_sec"]
)

# Schema diff
detector = SchemaCompatibilityDetector(
    edit_distance_threshold=SCHEMA_DIFF_CONFIG["rename_detection"]["edit_distance_threshold"],
    type_rules=SCHEMA_DIFF_CONFIG["type_compatibility"]
)

# Migration plan
planner = MigrationPlanner(
    timeout=MIGRATION_PLAN_CONFIG["generation"]["timeout_sec"],
    templates=MIGRATION_PLAN_CONFIG["templates"]
)

# RCT experiment
experiment = RCTExperiment(
    groups=RCT_EXPERIMENT_CONFIG["groups"],
    randomization_seed=RCT_EXPERIMENT_CONFIG["randomization"]["seed"],
    stratification=RCT_EXPERIMENT_CONFIG["stratification"]
)
```

---

## Configuration Validation

Runtime validation checks (implemented in config module):

```python
def validate_config():
    """Validate all configuration values at startup."""
    
    # Data collection
    assert DATA_COLLECTION_CONFIG["huggingface"]["rate_limit_rpm"] > 0
    assert DATA_COLLECTION_CONFIG["github"]["max_repos"] <= 10000
    
    # Graph construction
    assert 0 <= GRAPH_CONSTRUCTION_CONFIG["graph"]["min_edge_confidence"] <= 1
    assert GRAPH_CONSTRUCTION_CONFIG["graph"]["max_nodes"] <= 100000
    
    # Impact analysis
    assert IMPACT_ANALYSIS_CONFIG["closure"]["max_depth"] >= 1
    assert IMPACT_ANALYSIS_CONFIG["closure"]["timeout_per_dataset_sec"] > 0
    
    # Schema diff
    assert SCHEMA_DIFF_CONFIG["rename_detection"]["edit_distance_threshold"] >= 1
    assert 0 <= SCHEMA_DIFF_CONFIG["rename_detection"]["min_similarity"] <= 1
    
    # Migration plan
    assert MIGRATION_PLAN_CONFIG["generation"]["timeout_sec"] <= 10
    
    # RCT
    total_sample = sum(g["sample_size"] for g in RCT_EXPERIMENT_CONFIG["groups"].values())
    assert total_sample == 600
    assert RCT_EXPERIMENT_CONFIG["observation"]["adoption_window_days"] <= 30
    
    # Instrumentation
    assert INSTRUMENTATION_CONFIG["performance"]["max_overhead_pct"] == 10.0
```

---

## Summary

**Total Configuration Sections**: 8  
**Total Subtasks**: 22  
**Config Pattern**: Hardcoded dict (consistent with h-e1)  
**Validation**: Runtime checks for all thresholds  
**Integration**: Extends h-e1 instrumentation config

**Next Steps**: Phase 4 (Implementation) will copy-paste these configs into `src/config.py`.

---

**End of Configuration Specification**
