import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from config import ExperimentConfig, ModelConfig, GenerationConfig, BootstrapConfig, ThresholdConfig, FMDConfig, OutputConfig


class TestExperimentConfig(unittest.TestCase):

    def test_default_values(self):
        config = ExperimentConfig()
        self.assertEqual(config.hypothesis_id, "h-m1")
        self.assertEqual(config.n_problems, 164)

    def test_n_problems(self):
        config = ExperimentConfig()
        self.assertEqual(config.n_problems, 164)

    def test_bootstrap_config(self):
        config = ExperimentConfig()
        self.assertEqual(config.bootstrap.n_bootstrap, 10000)
        self.assertEqual(config.bootstrap.alpha, 0.05)

    def test_generation_max_new_tokens(self):
        config = ExperimentConfig()
        self.assertEqual(config.generation.max_new_tokens, 512)

    def test_threshold_config(self):
        config = ExperimentConfig()
        self.assertEqual(config.thresholds.delta_ast_min, 0.0)
        self.assertEqual(config.thresholds.ci_lower_min, 0.0)
        self.assertEqual(config.thresholds.constraint_active_rate_min, 0.3)

    def test_fmd_config(self):
        config = ExperimentConfig()
        self.assertEqual(config.fmd.mypy_timeout, 30)
        self.assertIn("syntax", config.fmd.category_priority)


if __name__ == "__main__":
    unittest.main()
