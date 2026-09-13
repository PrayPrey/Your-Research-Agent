"""Mechanism verification for H-M3 PermAug — must pass before training."""
import torch
from perm_aug import apply_random_permutation, PermAugDataset


def verify_perm_aug_mechanism(perm_dataset: PermAugDataset, plain_dataset, layer_sizes: list) -> dict:
    """Run two checks; raise RuntimeError if either fails.

    Check 1: permutation changes the tensor (aug_diff > 1e-6)
    Check 2: len(perm_dataset) == len(plain_dataset) * (NUM_PERMUTATIONS + 1)
    """
    indicators = {}

    # Check 1: augmentation actually changes the vector
    x_plain, _ = plain_dataset[0]
    x_aug, _ = perm_dataset[1]  # aug_idx=1 → permuted
    aug_diff = (x_aug.float() - x_plain.float()).abs().max().item()
    indicators["aug_diff"] = aug_diff
    print(f"[H-M3] Check 1: aug_diff = {aug_diff:.6f} (must be > 1e-6)")
    if aug_diff <= 1e-6:
        raise RuntimeError(
            f"[H-M3] FAIL: PermAug did not change tensor! aug_diff={aug_diff:.6f}\n"
            "Check layer_sizes matches the actual FlatMLP architecture."
        )

    # Check 2: dataset size is (NUM_PERMUTATIONS+1)× base
    expected_len = len(plain_dataset) * perm_dataset._n_aug
    actual_len = len(perm_dataset)
    indicators["len_check"] = {"expected": expected_len, "actual": actual_len}
    print(f"[H-M3] Check 2: len(perm_ds)={actual_len}, expected={expected_len}")
    if actual_len != expected_len:
        raise RuntimeError(
            f"[H-M3] FAIL: len(perm_ds)={actual_len} != {expected_len}"
        )

    print(f"[H-M3] MECHANISM CHECK PASSED: aug_diff={aug_diff:.6f} > 1e-6, "
          f"len={actual_len} = {len(plain_dataset)} × {perm_dataset._n_aug}")
    return indicators
