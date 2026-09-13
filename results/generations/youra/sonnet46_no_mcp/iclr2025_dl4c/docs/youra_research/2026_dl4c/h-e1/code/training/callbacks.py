"""Training callbacks for curriculum phase switching and reward density logging."""

import csv
import os
import sys
from transformers import TrainerCallback, TrainerState, TrainerControl, TrainingArguments

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG
from training.reward import compute_reward_density
from data.dataset import CurriculumDataset

CURRICULUM_STEP: int = CONFIG["curriculum_step"]
LOG_DIR: str = CONFIG["log_dir"]
FLUSH_INTERVAL: int = CONFIG["reward_density_flush_interval"]


class CurriculumCallback(TrainerCallback):
    """Calls dataset.set_step at on_step_begin, logs phase switch at step 2500."""

    def __init__(self, dataset: CurriculumDataset) -> None:
        self.dataset = dataset

    def on_step_begin(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        """Switch curriculum phase when global_step reaches curriculum_step."""
        self.dataset.set_step(state.global_step)


class RewardDensityCallback(TrainerCallback):
    """Appends reward density to CSV log per step, flushes on finalize."""

    def __init__(self, condition: str, log_dir: str = LOG_DIR) -> None:
        self.condition = condition
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.csv_path = os.path.join(log_dir, f"reward_density_{condition}.csv")
        self._file = open(self.csv_path, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["step", "reward_density"])
        self._step_count = 0

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        """Append reward density to CSV log."""
        # Try to get rewards from trainer logs
        rewards_group = []
        if hasattr(state, "log_history") and state.log_history:
            last_log = state.log_history[-1]
            # TRL logs rewards under various keys
            for key in ("rewards", "reward", "mean_reward"):
                if key in last_log:
                    val = last_log[key]
                    if isinstance(val, (list, tuple)):
                        rewards_group = list(val)
                    else:
                        # scalar reward — compute density as 0 (single value)
                        rewards_group = [float(val)]
                    break

        density = compute_reward_density(rewards_group) if len(rewards_group) >= 2 else 0.0
        self._writer.writerow([state.global_step, density])
        self._step_count += 1

        if self._step_count % FLUSH_INTERVAL == 0:
            self._file.flush()

    def finalize(self) -> None:
        """Flush and close reward_density_{condition}.csv."""
        if not self._file.closed:
            self._file.flush()
            self._file.close()

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        self.finalize()
