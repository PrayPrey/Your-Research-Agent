"""
h-m1 Configuration Module
YAML-based config with dataclass validation (FULL tier)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple
import yaml


@dataclass
class ProjectConfig:
    """Project-level configuration"""
    hypothesis_id: str = "h-m1"
    hypothesis_type: str = "MECHANISM"
    tier: str = "FULL"
    base_hypothesis: str = "h-e1"


@dataclass
class PathsConfig:
    """File paths configuration"""
    h_e1_code: str = '../h-e1/code'
    h_e1_results: str = '../h-e1/code/results'
    results_dir: str = './code/results/'
    figures_dir: str = './code/figures/'
    logs_dir: str = './code/logs/'
    data_dir: str = '../h-e1/code/data/waterbirds/'

    def __post_init__(self):
        """Create directories if they don't exist"""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class ReproducibilityConfig:
    """Reproducibility settings"""
    seed: int = 42


@dataclass
class DatasetConfig:
    """Dataset configuration"""
    batch_size: int = 128
    num_workers: int = 4
    num_classes: int = 2
    num_groups: int = 4


@dataclass
class HessianConfig:
    """Hessian computation configuration"""
    num_eigenthings: int = 100
    power_iter_steps: int = 20
    batch_size: int = 32


@dataclass
class MarchenkoPasturConfig:
    """Marchenko-Pastur fitting configuration"""
    fit_range_start: int = 20
    fit_range_end: int = 80
    sigma_sq_init: float = 1.0
    gamma_init: float = 0.1
    sigma_sq_bounds: Tuple[float, float] = (0.01, 10.0)
    gamma_bounds: Tuple[float, float] = (0.01, 1.0)


@dataclass
class OutlierAnalysisConfig:
    """Outlier analysis configuration (NEW for h-m1)"""
    histogram_bins: int = 20
    spacing_analysis: bool = True
    distribution_plots: bool = True


@dataclass
class VisualizationConfig:
    """Visualization settings"""
    dpi: int = 300
    format: str = 'png'
    colors: Dict[str, str] = field(default_factory=lambda: {
        'erm': 'red',
        'dro': 'blue',
        'bulk_edge': 'darkred'
    })
    alpha: float = 0.7
    figures: Dict[str, str] = field(default_factory=lambda: {
        'gate_metric': 'fig1_outlier_comparison.png',
        'spectra': 'fig2_spectra_comparison.png',
        'distributions': 'fig3_outlier_distributions.png',
        'mp_fit_erm': 'fig4_mp_fit_quality_erm.png',
        'mp_fit_dro': 'fig5_mp_fit_quality_dro.png',
        'decay': 'fig6_eigenvalue_decay.png'
    })


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = 'INFO'
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = './code/logs/h_m1_experiment.log'
    csv_outputs: Dict[str, str] = field(default_factory=lambda: {
        'outlier_metrics': 'outlier_metrics.csv',
        'hessian_stats_erm': 'hessian_stats_erm.csv',
        'hessian_stats_dro': 'hessian_stats_dro.csv'
    })
    json_output: str = 'comparison_results.json'


@dataclass
class TestingConfig:
    """Testing configuration"""
    unit_tests: bool = True
    smoke_test: bool = False


@dataclass
class ExpectedResultsConfig:
    """Expected results from h-e1 for validation"""
    erm_outliers: int = 23
    dro_outliers: int = 15
    erm_bulk_edge: float = 2.456
    dro_bulk_edge: float = 1.987


@dataclass
class H_M1_Config:
    """Complete h-m1 configuration"""
    project: ProjectConfig = field(default_factory=ProjectConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    data: PathsConfig = field(default_factory=PathsConfig)  # Alias for paths (for config.data.data_dir access)
    reproducibility: ReproducibilityConfig = field(default_factory=ReproducibilityConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    hessian: HessianConfig = field(default_factory=HessianConfig)
    marchenko_pastur: MarchenkoPasturConfig = field(default_factory=MarchenkoPasturConfig)
    outlier_analysis: OutlierAnalysisConfig = field(default_factory=OutlierAnalysisConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    testing: TestingConfig = field(default_factory=TestingConfig)
    expected_from_h_e1: ExpectedResultsConfig = field(default_factory=ExpectedResultsConfig)

    @classmethod
    def from_yaml(cls, yaml_path: str = 'config.yaml') -> 'H_M1_Config':
        """Load configuration from YAML file"""
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        # Parse marchenko_pastur fit_range
        mp_config = config_dict.get('marchenko_pastur', {})
        fit_range = mp_config.get('fit_range', {})
        optimization = mp_config.get('optimization', {})

        mp_params = {
            'fit_range_start': fit_range.get('start', 20),
            'fit_range_end': fit_range.get('end', 80),
            **optimization
        }

        paths_config = PathsConfig(**config_dict.get('paths', {}))
        return cls(
            project=ProjectConfig(**config_dict.get('project', {})),
            paths=paths_config,
            data=paths_config,  # Alias for paths (for config.data.data_dir access)
            reproducibility=ReproducibilityConfig(**config_dict.get('reproducibility', {})),
            dataset=DatasetConfig(**config_dict.get('dataset', {})),
            hessian=HessianConfig(**config_dict.get('hessian', {})),
            marchenko_pastur=MarchenkoPasturConfig(**mp_params),
            outlier_analysis=OutlierAnalysisConfig(**config_dict.get('outlier_analysis', {})),
            visualization=VisualizationConfig(**config_dict.get('visualization', {})),
            logging=LoggingConfig(**config_dict.get('logging', {})),
            testing=TestingConfig(**config_dict.get('testing', {})),
            expected_from_h_e1=ExpectedResultsConfig(**config_dict.get('expected_from_h_e1', {}))
        )


# Load default configuration
def load_config(config_path: str = None) -> H_M1_Config:
    """Load configuration from YAML file"""
    if config_path is None:
        # Try to find config.yaml in current directory or parent
        candidates = [
            'config.yaml',
            'code/config.yaml',
            '../config.yaml'
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                config_path = candidate
                break
        else:
            # Use defaults if no config file found
            return H_M1_Config()

    return H_M1_Config.from_yaml(config_path)
