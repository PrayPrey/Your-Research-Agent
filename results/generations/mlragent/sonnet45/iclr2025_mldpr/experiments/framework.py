"""
Temporal Dataset Cards Framework
Core implementation for version-aware dataset documentation
"""

import json
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from scipy.stats import entropy
from scipy.spatial.distance import jensenshannon


@dataclass
class Operation:
    """Represents a single dataset modification operation"""
    operation_type: str  # ADD, DELETE, MODIFY, SPLIT, MERGE
    affected_samples: List[str]
    field: str
    rationale: str
    impact_level: str  # BREAKING, COMPATIBLE, PATCH
    timestamp: str


@dataclass
class StatisticalSignature:
    """Statistical characteristics of a dataset version"""
    sample_count: int
    feature_stats: Dict[str, Dict[str, float]]  # feature -> {mean, var, etc}
    label_distribution: Dict[str, int]
    timestamp: str


@dataclass
class RetroAnnotation:
    """Retrospective annotation for discovered issues"""
    annotation_id: str
    annotation_type: str  # CRITICAL, WARNING, DEPRECATION, CORRECTION
    description: str
    affected_versions: List[str]
    affected_samples: Optional[List[str]]
    severity: int  # 1-5
    evidence: str
    recommended_action: str
    timestamp: str
    approved: bool = False


@dataclass
class VersionMetadata:
    """Complete metadata for a dataset version"""
    version_id: str  # semantic versioning: MAJOR.MINOR.PATCH
    timestamp: str
    authors: List[str]
    description: str
    license: str
    changelog: List[Operation]
    statistical_signature: StatisticalSignature
    retrospective_annotations: List[RetroAnnotation]


class TemporalDatasetCard:
    """Main class for managing temporal dataset cards"""

    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.versions: Dict[str, VersionMetadata] = {}
        self.citation_graph: Dict[str, List[str]] = {}  # version -> [paper_ids]

    def add_version(self, version: VersionMetadata):
        """Add a new version to the temporal card"""
        self.versions[version.version_id] = version

    def compute_hash(self, sample: Dict) -> str:
        """Compute content-based hash for a sample"""
        content = json.dumps(sample, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def generate_changelog(self, v_old: List[Dict], v_new: List[Dict]) -> List[Operation]:
        """Generate changelog between two dataset versions"""
        operations = []
        timestamp = datetime.now().isoformat()

        # Compute hashes
        old_hashes = {self.compute_hash(s): s for s in v_old}
        new_hashes = {self.compute_hash(s): s for s in v_new}

        # Identify additions
        added = set(new_hashes.keys()) - set(old_hashes.keys())
        if added:
            operations.append(Operation(
                operation_type="ADD",
                affected_samples=list(added)[:10],  # Sample for brevity
                field="all",
                rationale=f"Added {len(added)} new samples",
                impact_level="COMPATIBLE",
                timestamp=timestamp
            ))

        # Identify deletions
        deleted = set(old_hashes.keys()) - set(new_hashes.keys())
        if deleted:
            operations.append(Operation(
                operation_type="DELETE",
                affected_samples=list(deleted)[:10],
                field="all",
                rationale=f"Removed {len(deleted)} samples",
                impact_level="BREAKING" if len(deleted) > len(v_old) * 0.1 else "COMPATIBLE",
                timestamp=timestamp
            ))

        return operations

    def compute_statistical_signature(self, data: List[Dict], labels: List[str]) -> StatisticalSignature:
        """Compute statistical signature for a dataset version"""
        timestamp = datetime.now().isoformat()

        # Sample count
        sample_count = len(data)

        # Feature statistics (for numerical features)
        feature_stats = {}
        if data:
            for key in data[0].keys():
                try:
                    values = [float(d.get(key, 0)) for d in data]
                    feature_stats[key] = {
                        'mean': float(np.mean(values)),
                        'var': float(np.var(values)),
                        'min': float(np.min(values)),
                        'max': float(np.max(values))
                    }
                except (ValueError, TypeError):
                    pass

        # Label distribution
        label_distribution = {}
        for label in labels:
            label_distribution[label] = label_distribution.get(label, 0) + 1

        return StatisticalSignature(
            sample_count=sample_count,
            feature_stats=feature_stats,
            label_distribution=label_distribution,
            timestamp=timestamp
        )

    def kl_divergence(self, v1_id: str, v2_id: str) -> float:
        """Compute KL divergence between two version distributions"""
        v1 = self.versions[v1_id]
        v2 = self.versions[v2_id]

        # Use label distributions
        labels1 = v1.statistical_signature.label_distribution
        labels2 = v2.statistical_signature.label_distribution

        # Get all labels
        all_labels = set(labels1.keys()) | set(labels2.keys())

        # Build probability distributions
        p1 = np.array([labels1.get(l, 0) for l in all_labels]) + 1e-10
        p2 = np.array([labels2.get(l, 0) for l in all_labels]) + 1e-10

        p1 = p1 / p1.sum()
        p2 = p2 / p2.sum()

        # Compute KL divergence
        kl_div = entropy(p1, p2)
        return float(kl_div)

    def jensen_shannon_distance(self, v1_id: str, v2_id: str) -> float:
        """Compute Jensen-Shannon distance between versions"""
        v1 = self.versions[v1_id]
        v2 = self.versions[v2_id]

        labels1 = v1.statistical_signature.label_distribution
        labels2 = v2.statistical_signature.label_distribution

        all_labels = set(labels1.keys()) | set(labels2.keys())

        p1 = np.array([labels1.get(l, 0) for l in all_labels]) + 1e-10
        p2 = np.array([labels2.get(l, 0) for l in all_labels]) + 1e-10

        p1 = p1 / p1.sum()
        p2 = p2 / p2.sum()

        return float(jensenshannon(p1, p2))

    def add_retrospective_annotation(self, annotation: RetroAnnotation):
        """Add retrospective annotation and propagate to affected versions"""
        for version_id in annotation.affected_versions:
            if version_id in self.versions:
                version = self.versions[version_id]

                # Check if samples are actually in this version
                should_propagate = True
                if annotation.affected_samples:
                    # In real implementation, check against actual version samples
                    should_propagate = True

                if should_propagate:
                    version.retrospective_annotations.append(annotation)

    def track_citation(self, version_id: str, paper_id: str):
        """Track which paper uses which version"""
        if version_id not in self.citation_graph:
            self.citation_graph[version_id] = []
        self.citation_graph[version_id].append(paper_id)

    def get_impact_trace(self, version_id: str) -> List[str]:
        """Get all papers using a specific version"""
        return self.citation_graph.get(version_id, [])

    def compute_result_variance(self, version_results: Dict[str, List[float]]) -> Dict[str, float]:
        """Compute variance in results across versions"""
        variances = {}

        for metric_name, results in version_results.items():
            results_array = np.array(results)
            variances[metric_name] = {
                'mean': float(np.mean(results_array)),
                'variance': float(np.var(results_array)),
                'std': float(np.std(results_array)),
                'min': float(np.min(results_array)),
                'max': float(np.max(results_array)),
                'range': float(np.max(results_array) - np.min(results_array))
            }

        return variances

    def export_to_json(self, filepath: str):
        """Export temporal card to JSON"""
        export_data = {
            'dataset_name': self.dataset_name,
            'versions': {
                vid: {
                    'version_id': v.version_id,
                    'timestamp': v.timestamp,
                    'authors': v.authors,
                    'description': v.description,
                    'license': v.license,
                    'changelog': [asdict(op) for op in v.changelog],
                    'statistical_signature': asdict(v.statistical_signature),
                    'retrospective_annotations': [asdict(a) for a in v.retrospective_annotations]
                }
                for vid, v in self.versions.items()
            },
            'citation_graph': self.citation_graph
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

    def generate_citation(self, version_id: str) -> str:
        """Generate version-specific citation"""
        version = self.versions[version_id]
        authors_str = ", ".join(version.authors)

        citation = f"""@dataset{{{self.dataset_name}_v{version_id.replace('.', '_')},
  title={{{self.dataset_name}}},
  version={{{version_id}}},
  authors={{{authors_str}}},
  year={{{version.timestamp[:4]}}},
  license={{{version.license}}}
}}"""
        return citation


class ImpactTracer:
    """Tools for tracing dataset impact across research literature"""

    def __init__(self):
        self.paper_dataset_map: Dict[str, Dict[str, str]] = {}  # paper_id -> {dataset: version}

    def extract_dataset_citation(self, paper_text: str, dataset_name: str) -> Optional[str]:
        """Extract dataset version from paper (simplified simulation)"""
        # In real implementation, would use NLP models
        # For simulation, we'll return random versions
        if dataset_name.lower() in paper_text.lower():
            # Simulate version extraction
            import random
            versions = ["1.0.0", "1.1.0", "2.0.0"]
            return random.choice(versions)
        return None

    def build_citation_graph(self, papers: List[Dict], datasets: List[str]) -> Dict[str, List[str]]:
        """Build citation graph from papers to datasets"""
        graph = {}

        for paper in papers:
            paper_id = paper['id']
            paper_text = paper.get('text', '')

            for dataset in datasets:
                version = self.extract_dataset_citation(paper_text, dataset)
                if version:
                    if version not in graph:
                        graph[version] = []
                    graph[version].append(paper_id)

                    self.paper_dataset_map[paper_id] = {dataset: version}

        return graph

    def compute_citation_metrics(self, graph: Dict[str, List[str]]) -> Dict[str, int]:
        """Compute metrics on citation graph"""
        metrics = {}

        for version, papers in graph.items():
            metrics[version] = {
                'citation_count': len(papers),
                'unique_papers': len(set(papers))
            }

        return metrics
