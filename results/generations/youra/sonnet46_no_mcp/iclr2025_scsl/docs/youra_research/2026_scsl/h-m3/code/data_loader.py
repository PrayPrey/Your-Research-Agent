import json
import logging
import os
from typing import Dict, Optional

import numpy as np

from config import ExperimentConfig

logger = logging.getLogger(__name__)


class DeltaCurveLoader:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg
        self.results_dir: str = cfg.paths.h_e1_results_dir
        self.checkpoint_dir: str = cfg.paths.h_e1_checkpoint_dir
        self.json_filename: str = cfg.paths.h_e1_json_filename
        self.seeds = cfg.analysis.seeds

    def load(self) -> Dict[int, np.ndarray]:
        # Attempt 1: JSON
        result = self._load_from_json()
        if result is not None and all(s in result for s in self.seeds):
            logger.info(f"Loaded delta curves from JSON for seeds {list(result.keys())}")
            self.validate(result)
            return result

        # Attempt 2: per-seed .npy
        curves: Dict[int, np.ndarray] = {}
        if result is not None:
            curves.update(result)
        for seed in self.seeds:
            if seed not in curves:
                arr = self._load_from_npy(seed)
                if arr is not None:
                    curves[seed] = arr

        if len(curves) == len(self.seeds):
            logger.info(f"Loaded delta curves from .npy files for seeds {list(curves.keys())}")
            self.validate(curves)
            return curves

        # Attempt 3: checkpoint regeneration for missing seeds
        for seed in self.seeds:
            if seed not in curves:
                logger.info(f"Regenerating delta curve for seed {seed} from checkpoints")
                curves[seed] = self._regenerate_from_checkpoints(seed)

        self.validate(curves)
        return curves

    def _load_from_json(self) -> Optional[Dict[int, np.ndarray]]:
        # Try h-e1/results/h-e1/ subfolder first (actual structure), then direct
        json_candidates = [
            os.path.join(self.results_dir, "h-e1", self.json_filename),
            os.path.join(self.results_dir, self.json_filename),
            # Also check h-e1/code/outputs (where actual file lives)
            os.path.join(self.results_dir, "..", "code", "outputs", self.json_filename),
        ]
        json_path = None
        for candidate in json_candidates:
            if os.path.isfile(candidate):
                json_path = candidate
                break

        if json_path is None:
            logger.warning(f"H-E1 results JSON not found in: {json_candidates}")
            return None

        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            per_seed = data.get("per_seed", [])
            curves: Dict[int, np.ndarray] = {}
            for entry in per_seed:
                seed = int(entry["seed"])
                delta = np.array(entry["delta_curve"], dtype=np.float32)
                curves[seed] = delta
                logger.info(f"  seed={seed}: delta_curve shape={delta.shape}, range=[{delta.min():.4f}, {delta.max():.4f}]")
            return curves if curves else None
        except Exception as e:
            logger.warning(f"Failed to load JSON from {json_path}: {e}")
            return None

    def _load_from_npy(self, seed: int) -> Optional[np.ndarray]:
        npy_path = os.path.join(self.results_dir, f"delta_t_seed{seed}.npy")
        if not os.path.isfile(npy_path):
            return None
        try:
            arr = np.load(npy_path).astype(np.float32)
            logger.info(f"Loaded .npy for seed={seed}: shape={arr.shape}")
            return arr
        except Exception as e:
            logger.warning(f"Failed to load .npy for seed={seed}: {e}")
            return None

    def _regenerate_from_checkpoints(self, seed: int) -> np.ndarray:
        import torch
        import torchvision.models as tv_models
        from sklearn.linear_model import LogisticRegression

        seed_ckpt_dir = os.path.join(self.checkpoint_dir, f"seed_{seed}")
        if not os.path.isdir(seed_ckpt_dir):
            raise FileNotFoundError(
                f"Checkpoint dir not found: {seed_ckpt_dir}. "
                "Cannot regenerate delta curves."
            )

        import glob
        checkpoints = sorted(glob.glob(os.path.join(seed_ckpt_dir, "epoch_*.pt")))
        if not checkpoints:
            raise FileNotFoundError(f"No epoch_*.pt checkpoints in {seed_ckpt_dir}")

        # Import waterbirds dataset loader from H-E1
        import sys
        h_e1_code = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code")
        sys.path.insert(0, h_e1_code)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        delta_list = []

        for ckpt_path in checkpoints:
            ckpt = torch.load(ckpt_path, map_location=device)
            model = tv_models.resnet50(pretrained=False)
            model.fc = torch.nn.Linear(2048, 2)
            model.load_state_dict(ckpt["model"])
            model.eval()
            model.to(device)

            # Feature extraction would require dataset — raise informative error
            raise NotImplementedError(
                "Checkpoint regeneration requires Waterbirds dataset loader. "
                "Please ensure H-E1 JSON results are available at: "
                f"{os.path.join(self.results_dir, self.json_filename)}"
            )

        return np.array(delta_list, dtype=np.float32)

    def validate(self, curves: Dict[int, np.ndarray]) -> None:
        n_seeds = len(curves)
        if n_seeds < self.cfg.analysis.min_seeds:
            raise ValueError(
                f"Need at least {self.cfg.analysis.min_seeds} seeds, got {n_seeds}"
            )
        for seed, arr in curves.items():
            n_ckpts = len(arr)
            if n_ckpts < self.cfg.analysis.min_checkpoints:
                raise ValueError(
                    f"Seed {seed}: need >= {self.cfg.analysis.min_checkpoints} checkpoints, got {n_ckpts}"
                )
            logger.info(f"Validated seed={seed}: {n_ckpts} checkpoints")
        logger.info(f"Validation passed: {n_seeds} seeds, all arrays >= {self.cfg.analysis.min_checkpoints} checkpoints")
