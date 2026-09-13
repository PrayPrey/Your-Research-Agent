"""Checkpoint management for crash recovery."""
import json
import os


class CheckpointManager:
    def __init__(self, path: str, save_every: int = 50):
        self.path = path
        self.save_every = save_every
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def load(self) -> dict:
        """Load checkpoint if exists, else return empty state."""
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {"last_idx": -1, "results": []}

    def save(self, idx: int, results: list) -> None:
        """Save checkpoint with current progress."""
        with open(self.path, "w") as f:
            json.dump({"last_idx": idx, "results": results}, f)

    def should_save(self, idx: int) -> bool:
        """Check if should save at this index."""
        return (idx + 1) % self.save_every == 0
