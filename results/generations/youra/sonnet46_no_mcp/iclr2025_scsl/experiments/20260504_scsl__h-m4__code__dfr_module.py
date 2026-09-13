import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Dict
import torch

from config import ExperimentConfig
from train_backbone import build_model


def worst_group_accuracy(
    predictions: np.ndarray,
    labels: np.ndarray,
    group_ids: np.ndarray,
) -> float:
    accs = []
    for g in range(4):
        mask = group_ids == g
        if mask.sum() == 0:
            continue
        acc = (predictions[mask] == labels[mask]).mean()
        accs.append(acc)
    return float(min(accs)) if accs else 0.0


class DFRModule:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg

    def evaluate_checkpoint(
        self,
        checkpoint_path: str,
        val_feats: np.ndarray,
        val_labels: np.ndarray,
        test_feats: np.ndarray,
        test_labels: np.ndarray,
        test_groups: np.ndarray,
        device: str,
    ) -> Dict[str, float]:
        erm_wga = self._erm_wga(checkpoint_path, test_feats, test_labels, test_groups, device)
        clf = self._fit_dfr(val_feats, val_labels)
        dfr_preds = clf.predict(test_feats)
        dfr_wga = worst_group_accuracy(dfr_preds, test_labels, test_groups)
        wga_improvement = dfr_wga - erm_wga

        # Extract epoch from checkpoint path for logging
        epoch_str = os.path.basename(checkpoint_path).replace("epoch_", "").replace(".pt", "")
        try:
            epoch = int(epoch_str)
        except ValueError:
            epoch = -1

        print(f"DFR applied at epoch {epoch}: ERM WGA={erm_wga:.4f}, "
              f"DFR WGA={dfr_wga:.4f}, improvement={wga_improvement:.4f}")

        return {
            "erm_wga": erm_wga,
            "dfr_wga": dfr_wga,
            "wga_improvement": wga_improvement,
            "feature_dim": int(test_feats.shape[1]),
        }

    def _erm_wga(
        self,
        checkpoint_path: str,
        test_feats: np.ndarray,
        test_labels: np.ndarray,
        test_groups: np.ndarray,
        device: str,
    ) -> float:
        model = build_model(num_classes=2, pretrained=False).to(device)
        state_dict = torch.load(checkpoint_path, map_location=device, weights_only=True)
        model.load_state_dict(state_dict)
        model.eval()

        fc_weights = model.fc.weight.detach().cpu().numpy()  # [2, 2048]
        fc_bias = model.fc.bias.detach().cpu().numpy()       # [2]

        logits = test_feats @ fc_weights.T + fc_bias         # [N, 2]
        preds = logits.argmax(axis=1)                        # [N]

        return worst_group_accuracy(preds, test_labels, test_groups)

    def _fit_dfr(
        self,
        val_feats: np.ndarray,
        val_labels: np.ndarray,
    ) -> LogisticRegression:
        clf = LogisticRegression(
            C=self.cfg.dfr.C,
            max_iter=self.cfg.dfr.max_iter,
            class_weight=self.cfg.dfr.class_weight,
            solver=self.cfg.dfr.solver,
            random_state=self.cfg.dfr.dfr_seed,
        )
        clf.fit(val_feats, val_labels)
        return clf
