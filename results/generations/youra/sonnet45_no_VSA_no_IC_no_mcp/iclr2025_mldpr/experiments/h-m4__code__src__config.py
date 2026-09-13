# Configuration for h-m3: Dependency-Aware Migration Plans
# Pattern: Hardcoded dict (consistent with h-e1)

import os

# Inherited from h-e1
INSTRUMENTATION_CONFIG = {
    "telemetry": {
        "db_path": "telemetry.db",
        "opt_in": True,
        "hash_algorithm": "sha256",
        "hash_truncate_length": 16
    }
}

# Data collection
DATA_COLLECTION_CONFIG = {
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
        "cache_ttl_hours": 168,
        "request_timeout_sec": 60
    },
    "paperswithcode": {
        "base_url": "https://paperswithcode.com/api/v1",
        "rate_limit_rpm": 120,
        "cache_ttl_hours": 168,
        "request_timeout_sec": 30
    },
    "cache": {
        "backend": "sqlite",
        "db_path": "cache.db",
        "max_size_gb": 5
    }
}

# Graph construction
GRAPH_CONSTRUCTION_CONFIG = {
    "graph": {
        "min_edge_confidence": 0.3,
        "max_nodes": 50000,
        "cycle_handling": "scc_decomposition",
        "scc_max_size": 100,
        "serialization_format": "json"
    },
    "edge_confidence": {
        "code_mention": 0.8,
        "dataset_card_link": 0.9,
        "download_log": 0.5,
        "papers_citation": 0.95
    },
    "node_attributes": [
        "schema",
        "deprecated",
        "successor_id",
        "download_count",
        "last_updated"
    ],
    "performance": {
        "construction_timeout_sec": 3600,
        "serialize_compression": "gzip",
        "output_path": "dependency_graph.json.gz"
    }
}

# Impact analysis
IMPACT_ANALYSIS_CONFIG = {
    "closure": {
        "max_depth": 10,
        "timeout_per_dataset_sec": 10,
        "max_affected_entities": 10000
    },
    "entity_priority": {
        "model": 1.0,
        "pipeline": 0.8,
        "notebook": 0.6,
        "script": 0.4
    },
    "grouping": {
        "depth_bins": [1, 2, 3, 4, 5, 6],
        "min_group_size": 5
    },
    "performance": {
        "cache_results": True,
        "cache_ttl_hours": 24
    }
}

# Schema compatibility
SCHEMA_DIFF_CONFIG = {
    "rename_detection": {
        "edit_distance_threshold": 3,
        "min_similarity": 0.7,
        "case_sensitive": False
    },
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
    "severity": {
        "field_removal": "MAJOR",
        "field_rename": "MINOR",
        "type_incompatible": "MAJOR",
        "type_compatible": "MINOR",
        "field_addition": "COMPATIBLE"
    },
    "adapters": {
        "max_adapters_per_plan": 10,
        "template_library": "adapters/templates/"
    }
}

# Migration plan generation
MIGRATION_PLAN_CONFIG = {
    "generation": {
        "timeout_sec": 5,
        "max_steps": 50,
        "topological_sort_tie_breaking": "alphabetical"
    },
    "plan_sections": [
        "impact_radius",
        "breaking_changes",
        "migration_steps",
        "compatibility_adapters",
        "verification_checklist"
    ],
    "precompute": {
        "enabled": True,
        "deprecated_datasets_only": True,
        "cache_path": "migration_plans_cache.json"
    }
}

# RCT experiment
RCT_EXPERIMENT_CONFIG = {
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
    "randomization": {
        "seed": 42,
        "assignment_method": "user_id_hash",
        "hash_modulo": 3
    },
    "stratification": {
        "enabled": True,
        "variable": "dependency_complexity",
        "bins": {
            "low": {"min_depth": 1, "max_depth": 2},
            "medium": {"min_depth": 3, "max_depth": 5},
            "high": {"min_depth": 6, "max_depth": 999}
        }
    },
    "observation": {
        "duration_months": 6,
        "adoption_window_days": 30,
        "breaking_change_detection": "runtime_error_logs"
    },
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

# Instrumentation
INSTRUMENTATION_CONFIG.update({
    "loader": {
        "check_deprecation": True,
        "max_check_latency_ms": 100,
        "fallback_on_timeout": "load_without_intervention"
    },
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
    "performance": {
        "max_overhead_pct": 10.0,
        "plan_generation_timeout_sec": 5,
        "cache_warmup_enabled": True
    }
})

# Ground truth
GROUND_TRUTH_CONFIG = {
    "annotation": {
        "sample_size": 100,
        "annotators_per_sample": 2,
        "consensus_threshold": 0.8
    },
    "dependency_labels": {
        "affected": "Entity is transitively affected by deprecation",
        "unaffected": "Entity is not affected",
        "uncertain": "Cannot determine from available information"
    },
    "schema_labels": {
        "compatible": "Drop-in replacement",
        "minor_breaking": "Field renames or additions only",
        "major_breaking": "Field removals or type incompatibilities"
    },
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
