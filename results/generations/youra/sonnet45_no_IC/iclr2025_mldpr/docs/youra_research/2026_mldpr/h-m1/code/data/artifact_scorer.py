"""
Artifact Content Analyzer and Scorer
Analyzes real artifact content and generates quality scores based on rubric.
"""

import re
from pathlib import Path
from typing import Dict, Optional


class ArtifactContentScorer:
    """
    Analyzes artifact content and generates quality scores based on rubric dimensions.

    This replaces mock/synthetic scoring by analyzing actual README content for:
    - Preprocessing specifications
    - Data split information
    - Evaluation protocol details
    - Hyperparameter specifications
    """

    RUBRIC_DIMENSIONS = ['preprocessing', 'data_splits', 'evaluation_protocol', 'hyperparameters']

    def score_artifact_from_file(self, artifact_path: str) -> Dict[str, float]:
        """
        Score artifact quality by analyzing README content.

        Args:
            artifact_path: Path to artifact README file

        Returns:
            Dict with dimension scores (0-10 scale)
        """
        if not artifact_path or not Path(artifact_path).exists():
            # No artifact available - return zero scores
            return {dim: 0.0 for dim in self.RUBRIC_DIMENSIONS}

        try:
            with open(artifact_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()  # Case-insensitive matching

            scores = {
                'preprocessing': self._score_preprocessing(content),
                'data_splits': self._score_data_splits(content),
                'evaluation_protocol': self._score_evaluation(content),
                'hyperparameters': self._score_hyperparameters(content)
            }

            return scores

        except Exception as e:
            print(f"⚠️  Error scoring artifact {artifact_path}: {e}")
            return {dim: 0.0 for dim in self.RUBRIC_DIMENSIONS}

    def _score_preprocessing(self, content: str) -> float:
        """
        Score preprocessing specification quality (0-10).

        Rubric:
        0: No preprocessing information
        5: Mentions preprocessing exists
        10: Complete code/config for all preprocessing steps
        """
        # Preprocessing keywords
        keywords = ['preprocess', 'normalization', 'augmentation', 'resize', 'crop',
                    'transform', 'normalize', 'standardize', 'mean', 'std']

        # Code indicators (config files, detailed specifications)
        code_indicators = ['```', 'transforms.', 'torchvision.transforms',
                           'tf.image', 'preprocessing.py', 'config.yaml',
                           'transform =', 'normalize(']

        keyword_count = sum(1 for kw in keywords if kw in content)
        code_count = sum(1 for ind in code_indicators if ind in content)

        if keyword_count == 0:
            return 0.0  # No preprocessing info
        elif code_count >= 2:
            return 10.0  # Complete code/config
        elif code_count >= 1:
            return 7.5  # Some code present
        elif keyword_count >= 3:
            return 5.0  # Multiple mentions
        else:
            return 2.5  # Minimal mention

    def _score_data_splits(self, content: str) -> float:
        """
        Score data split specification quality (0-10).

        Rubric:
        0: No split information
        5: Split ratios mentioned
        10: Exact seeds/indices or deterministic split code
        """
        # Split keywords
        split_keywords = ['train', 'val', 'test', 'split', 'validation']
        ratio_indicators = ['80/20', '70/30', '90/10', 'ratio', '%', 'percent']
        deterministic_indicators = ['seed', 'random_state', 'split_seed', 'shuffle',
                                     'train_test_split', 'indices', 'fixed split']

        has_split_mention = any(kw in content for kw in split_keywords)
        has_ratio = any(ind in content for ind in ratio_indicators)
        has_deterministic = any(ind in content for ind in deterministic_indicators)

        if not has_split_mention:
            return 0.0  # No split info
        elif has_deterministic:
            return 10.0  # Deterministic split specified
        elif has_ratio:
            return 5.0  # Ratios mentioned
        else:
            return 2.5  # Minimal mention

    def _score_evaluation(self, content: str) -> float:
        """
        Score evaluation protocol specification quality (0-10).

        Rubric:
        0: No evaluation details
        5: Metrics named
        10: Complete evaluation code with all parameters
        """
        # Metric keywords
        metrics = ['accuracy', 'precision', 'recall', 'f1', 'auc', 'map',
                   'loss', 'error rate', 'top-1', 'top-5', 'metric']

        # Evaluation code indicators
        eval_code = ['evaluate(', 'evaluation.py', 'metrics.py', 'accuracy =',
                     'sklearn.metrics', 'torchmetrics', 'tf.metrics',
                     'test_accuracy', 'validation_loss']

        metric_count = sum(1 for m in metrics if m in content)
        code_count = sum(1 for ind in eval_code if ind in content)

        if metric_count == 0:
            return 0.0  # No evaluation info
        elif code_count >= 2:
            return 10.0  # Complete evaluation code
        elif code_count >= 1:
            return 7.5  # Some code present
        elif metric_count >= 3:
            return 5.0  # Multiple metrics named
        else:
            return 2.5  # Minimal mention

    def _score_hyperparameters(self, content: str) -> float:
        """
        Score hyperparameter specification quality (0-10).

        Rubric:
        0: No hyperparameters listed
        5: Some hyperparameters mentioned
        10: Complete config file or exhaustive listing
        """
        # Hyperparameter keywords
        hyperparams = ['learning rate', 'lr', 'batch size', 'epochs', 'optimizer',
                       'weight decay', 'momentum', 'dropout', 'hidden size',
                       'num_layers', 'adam', 'sgd', 'scheduler']

        # Config file indicators
        config_indicators = ['config.yaml', 'hyperparameters', 'hparams',
                            'argparse', '```yaml', 'config =', 'cfg.']

        hyperparam_count = sum(1 for hp in hyperparams if hp in content)
        has_config = any(ind in content for ind in config_indicators)

        if hyperparam_count == 0:
            return 0.0  # No hyperparameters
        elif has_config:
            return 10.0  # Complete config file
        elif hyperparam_count >= 5:
            return 7.5  # Many hyperparameters listed
        elif hyperparam_count >= 3:
            return 5.0  # Some hyperparameters mentioned
        else:
            return 2.5  # Minimal mention


def score_benchmark_with_fallback(benchmark_id: str, github_url: str,
                                   artifact_path: Optional[str]) -> Dict[str, float]:
    """
    Score benchmark artifact quality with fallback for missing artifacts.

    Args:
        benchmark_id: Benchmark identifier
        github_url: GitHub repository URL
        artifact_path: Path to retrieved artifact (None if retrieval failed)

    Returns:
        Dict with dimension scores
    """
    scorer = ArtifactContentScorer()

    if artifact_path and Path(artifact_path).exists():
        # Score based on actual artifact content
        return scorer.score_artifact_from_file(artifact_path)
    else:
        # No artifact available - return zero scores
        print(f"⚠️  No artifact for {benchmark_id} - assigning zero scores")
        return {dim: 0.0 for dim in ArtifactContentScorer.RUBRIC_DIMENSIONS}
