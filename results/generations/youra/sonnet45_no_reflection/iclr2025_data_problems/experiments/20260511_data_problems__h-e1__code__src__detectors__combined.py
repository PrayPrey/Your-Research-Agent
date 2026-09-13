"""Combined Three-Tier Detection System"""
from typing import Dict, List, Tuple
from .tier1 import Tier1DataFilter
from .tier2 import Tier2TSGProbes
from .tier3 import Tier3GeometricDetection

class CombinedDetector:
    """
    Three-Tier Combined Contamination Detector
    Uses OR logic across tiers: contamination detected if ANY tier detects
    """

    def __init__(
        self,
        tier1_config: Dict = None,
        tier2_config: Dict = None,
        tier3_config: Dict = None
    ):
        # Initialize detectors with configs
        self.tier1 = Tier1DataFilter(**(tier1_config or {}))
        self.tier2 = Tier2TSGProbes(**(tier2_config or {}))
        self.tier3 = Tier3GeometricDetection(**(tier3_config or {}))

    def detect_contamination(
        self,
        model,
        training_data: List[Dict],
        benchmark_data: List[Dict],
        training_metrics: Dict,
        sample_timestamps: List[str] = None
    ) -> Tuple[bool, Dict]:
        """
        Run three-tier detection
        Returns: (contamination_detected, detection_results)
        """
        results = {
            'tier1': {'detected': False, 'method': 'data_layer'},
            'tier2': {'detected': False, 'method': 'tsg_probes'},
            'tier3': {'detected': False, 'method': 'geometric', 'metrics': {}},
            'combined': {'detected': False, 'detection_power': 0.0}
        }

        # Tier 1: Data-layer detection
        tier1_detections = 0
        for idx, sample in enumerate(training_data[:100]):  # Sample check
            timestamp = sample_timestamps[idx] if sample_timestamps else None
            if self.tier1.detect(sample, sample_id=f"train_{idx}", timestamp=timestamp):
                tier1_detections += 1

        results['tier1']['detected'] = tier1_detections > 0
        results['tier1']['detection_count'] = tier1_detections

        # Tier 2: TSG Probes
        tier2_detected = self.tier2.detect(model)
        results['tier2']['detected'] = tier2_detected

        # Tier 3: Geometric Detection
        tier3_detected, tier3_metrics = self.tier3.detect(
            model,
            benchmark_data,
            training_data,
            training_metrics
        )
        results['tier3']['detected'] = tier3_detected
        results['tier3']['metrics'] = tier3_metrics

        # Combined detection (OR logic)
        combined_detected = (
            results['tier1']['detected'] or
            results['tier2']['detected'] or
            results['tier3']['detected']
        )
        results['combined']['detected'] = combined_detected

        # Compute per-tier detection rates (for analysis)
        results['combined']['tier1_rate'] = 1.0 if results['tier1']['detected'] else 0.0
        results['combined']['tier2_rate'] = 1.0 if results['tier2']['detected'] else 0.0
        results['combined']['tier3_rate'] = 1.0 if results['tier3']['detected'] else 0.0

        return combined_detected, results

    def index_benchmark(self, benchmark_samples: List[Dict]):
        """Index benchmark for Tier 1 LSH and Tier 2 probes"""
        # Tier 1: Index for LSH
        self.tier1.index_benchmark(benchmark_samples)

        # Tier 2: Generate probes
        self.tier2.invariant_probes = self.tier2.extract_tsg_invariants(benchmark_samples)
        self.tier2.neighbor_probes = self.tier2.generate_neighbor_probes(benchmark_samples)
        self.tier2.broken_probes = self.tier2.generate_broken_probes(benchmark_samples)
