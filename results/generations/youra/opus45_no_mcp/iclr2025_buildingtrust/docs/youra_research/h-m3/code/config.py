"""Configuration for H-M3 positional analysis experiment."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class H_M3_Config:
    hypothesis_id: str = "H-M3"
    hypothesis_type: str = "MECHANISM"
    gate_type: str = "SHOULD_WORK"

    h_m2_cache_path: Path = field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "h-m2/code/results/h-m2_results.json"
    )

    output_dir: Path = field(default_factory=lambda: Path(__file__).parent / "results")
    figures_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "figures")

    gate_1_threshold: float = 0.99
    gate_2_threshold: float = 0.95
    cot_position_threshold: float = 0.3

    hedging_markers: List[str] = field(default_factory=lambda: [
        'might', 'possibly', 'could', 'perhaps', 'may', 'likely',
        'unlikely', 'however', 'uncertain', 'although', 'but',
        'difficult to determine', 'not certain', 'hard to say',
        'alternatively', 'on the other hand', 'it depends'
    ])

    confidence_pattern: str = r'Confidence:\s*(\d+)%'
    figure_dpi: int = 150
    bar_color_pass: str = '#2ecc71'
    bar_color_fail: str = '#e74c3c'

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
