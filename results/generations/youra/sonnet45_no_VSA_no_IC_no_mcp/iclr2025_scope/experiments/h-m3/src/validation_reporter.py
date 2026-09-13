from pathlib import Path
from datetime import datetime
from typing import Dict


class ValidationReporter:
    """Generate validation report and gate decision."""

    def __init__(self, config):
        self.config = config
        self.output_path = Path("../../../docs/youra_research/h-m3/04_validation.md")

    def generate_report(self, metrics: Dict, gate_result: str) -> str:
        """Generate validation report markdown."""
        report = f"""# Validation Report: h-m3

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate Type:** MUST_WORK

---

## Hypothesis Statement

If we model benchmark usage as a bipartite graph (benchmarks ↔ methods) and apply community detection, then methods using the same benchmarks will cluster into research communities with ≥70% shared citation patterns, because benchmark constraints create methodological similarities.

---

## Experiment Results

### Primary Metrics

**Citation Overlap (Proposed):** {metrics['proposed']['citation_overlap']:.4f}
- **Target:** ≥0.70
- **Status:** {'PASS ✓' if metrics['proposed']['citation_overlap'] >= self.config.citation_overlap_threshold else 'FAIL ✗'}

**Modularity:** {metrics['proposed']['modularity']:.4f}
- **Target:** >0.40
- **Status:** {'PASS ✓' if metrics['proposed']['modularity'] > self.config.modularity_threshold else 'FAIL ✗'}

### Baseline Comparison

**Citation Overlap (Random Baseline):** {metrics['baseline']['citation_overlap']:.4f}
**Proposed > Baseline:** {'YES ✓' if metrics['proposed']['citation_overlap'] > metrics['baseline']['citation_overlap'] else 'NO ✗'}

### Community Statistics

**Number of communities:** {metrics['community_stats']['num_communities']}
**Mean community size:** {metrics['community_stats']['mean_size']:.1f} methods
**Size range:** {metrics['community_stats']['min_size']} - {metrics['community_stats']['max_size']} methods

---

## Gate Decision

**Result:** {gate_result}

**Rationale:**
"""

        if gate_result == "PASS":
            report += f"""
- Citation overlap ({metrics['proposed']['citation_overlap']:.4f}) meets threshold (≥0.70)
- Modularity ({metrics['proposed']['modularity']:.4f}) exceeds threshold (>0.40)
- Proposed significantly outperforms random baseline
- Mechanism hypothesis VALIDATED
"""
        elif gate_result == "PIVOT":
            report += f"""
- Citation overlap ({metrics['proposed']['citation_overlap']:.4f}) in PIVOT range (0.60-0.70)
- Mechanism shows promise but requires refinement
- **Recommended actions:**
  - Try Leiden algorithm (alternative to Louvain)
  - Weight edges by citation count
  - Add temporal weighting (recent papers weighted higher)
"""
        else:
            report += f"""
- Citation overlap ({metrics['proposed']['citation_overlap']:.4f}) below minimum threshold (<0.60)
- Mechanism hypothesis REJECTED
- Benchmark constraints insufficient to create citation-based communities
"""

        report += f"""

---

## Key Findings

"""
        findings = []
        if metrics['proposed']['citation_overlap'] >= self.config.citation_overlap_threshold:
            findings.append(f"Citation overlap {metrics['proposed']['citation_overlap']:.4f} exceeds threshold by +{(metrics['proposed']['citation_overlap'] - self.config.citation_overlap_threshold):.3f}")
        else:
            findings.append(f"Citation overlap {metrics['proposed']['citation_overlap']:.4f} falls short by -{(self.config.citation_overlap_threshold - metrics['proposed']['citation_overlap']):.3f}")

        if metrics['proposed']['modularity'] > self.config.modularity_threshold:
            findings.append(f"Modularity {metrics['proposed']['modularity']:.4f} indicates well-separated communities")
        else:
            findings.append(f"Modularity {metrics['proposed']['modularity']:.4f} below threshold (weak separation)")

        delta = metrics['proposed']['citation_overlap'] - metrics['baseline']['citation_overlap']
        findings.append(f"Proposed outperforms baseline by +{delta:.3f}")

        findings.append(f"{metrics['community_stats']['num_communities']} communities identified via Louvain")

        for i, finding in enumerate(findings, 1):
            report += f"{i}. {finding}\n"

        report += f"""

---

## Figures

See `docs/youra_research/h-m3/figures/`:
- `gate_metrics.png` - Target vs actual metrics
- `community_sizes.png` - Community size distribution
- `citation_heatmap.png` - Pairwise citation overlap
- `network_graph.png` - Network visualization

---

**Validation completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report

    def save_report(self, report: str, metrics: Dict):
        """Save validation report to disk."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w') as f:
            f.write(report)

        print(f"Validation report saved: {self.output_path}")
