"""
TrajectoryDataset for H-M2: loads full CNN Zoo checkpoint trajectories.
CNN Zoo format: Ray Tune directories with checkpoint_XXXXXX/checkpoints binary files.
Each model directory contains multiple checkpoint_XXXXXX subdirs (epoch-indexed).
"""
import os
import re
import glob
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import torch


class TrajectoryDataset:
    """Dataset that loads full epoch trajectories from CNN Zoo model directories."""

    def __init__(
        self,
        zoo_dir: Path,
        min_checkpoints: int = 10,
        max_checkpoints: int = 50,
    ):
        self.zoo_dir = Path(zoo_dir)
        self.min_checkpoints = min_checkpoints
        self.max_checkpoints = max_checkpoints
        self._model_dirs: Optional[List[Path]] = None

    def _find_model_dirs_recursive(self) -> List[Path]:
        """Find all dirs that contain at least one checkpoint_XXXXXX subdir (follows symlinks)."""
        model_dirs = []
        seen = set()
        ckpt_pattern = re.compile(r"checkpoint_\d+$")
        for root, dirs, _ in os.walk(str(self.zoo_dir), followlinks=True):
            for d in dirs:
                if ckpt_pattern.match(d):
                    parent = Path(root)
                    if parent not in seen:
                        seen.add(parent)
                        model_dirs.append(parent)
                    break
        return sorted(model_dirs)

    def discover_models(self) -> List[Path]:
        """Return sorted list of model dirs with >= min_checkpoints epoch files."""
        if not self.zoo_dir.exists():
            return []

        candidates = self._find_model_dirs_recursive()

        valid = []
        for model_dir in candidates:
            ckpt_count = len(self._get_checkpoint_dirs(model_dir))
            if ckpt_count >= self.min_checkpoints:
                valid.append(model_dir)

        self._model_dirs = valid
        return valid

    def _get_checkpoint_dirs(self, model_dir: Path) -> List[Tuple[int, Path]]:
        """Return sorted list of (epoch_idx, checkpoint_dir) for a model."""
        result = []
        try:
            for entry in os.scandir(str(model_dir)):
                if not entry.is_dir(follow_symlinks=True):
                    continue
                m = re.search(r"checkpoint_(\d+)$", entry.name)
                if m:
                    epoch_idx = int(m.group(1))
                    result.append((epoch_idx, Path(entry.path)))
        except OSError:
            pass
        return sorted(result, key=lambda x: x[0])

    def _load_state_dict(self, checkpoint_dir: Path) -> Optional[Dict[str, torch.Tensor]]:
        """Load state dict from checkpoint_dir/checkpoints file."""
        ckpt_file = checkpoint_dir / "checkpoints"
        if not ckpt_file.exists():
            return None
        try:
            obj = torch.load(str(ckpt_file), map_location="cpu", weights_only=True)
        except Exception:
            try:
                obj = torch.load(str(ckpt_file), map_location="cpu", weights_only=False)
            except Exception:
                return None
        if isinstance(obj, dict):
            return obj
        return None

    def load_trajectory(
        self, model_dir: Path
    ) -> List[Dict[str, torch.Tensor]]:
        """Load epoch checkpoints sorted by epoch index. Returns list of state_dicts."""
        ckpt_dirs = self._get_checkpoint_dirs(model_dir)
        # Subsample to max_checkpoints if needed (evenly spaced)
        if len(ckpt_dirs) > self.max_checkpoints:
            step = len(ckpt_dirs) / self.max_checkpoints
            indices = [int(i * step) for i in range(self.max_checkpoints)]
            ckpt_dirs = [ckpt_dirs[i] for i in indices]

        trajectory = []
        for _, ckpt_dir in ckpt_dirs:
            state_dict = self._load_state_dict(ckpt_dir)
            if state_dict is not None:
                trajectory.append(state_dict)

        return trajectory

    def iter_trajectories(
        self, n_models: Optional[int] = None
    ) -> Iterator[Tuple[str, List[Dict[str, torch.Tensor]]]]:
        """Yield (model_id, trajectory) pairs, skipping short trajectories."""
        if self._model_dirs is None:
            self.discover_models()

        dirs = self._model_dirs
        if n_models is not None:
            dirs = dirs[:n_models]

        for model_dir in dirs:
            trajectory = self.load_trajectory(model_dir)
            if len(trajectory) >= self.min_checkpoints:
                yield model_dir.name, trajectory

    def __len__(self) -> int:
        if self._model_dirs is None:
            self.discover_models()
        return len(self._model_dirs)
