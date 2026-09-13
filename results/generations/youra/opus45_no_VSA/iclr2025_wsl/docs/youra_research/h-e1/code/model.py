import torch


def randomized_svd(A: torch.Tensor, rank: int, seed: int) -> torch.Tensor:
    """Randomized SVD via random projection. Returns singular values [rank]."""
    torch.manual_seed(seed)
    M, N = A.shape
    actual_rank = min(rank, M, N)
    Omega = torch.randn(N, actual_rank, dtype=A.dtype, device=A.device)
    Y = A @ Omega
    Q, _ = torch.linalg.qr(Y)
    B = Q.T @ A
    _, S, _ = torch.linalg.svd(B, full_matrices=False)
    return S[:actual_rank]


def participation_ratio(eigenvalues: torch.Tensor) -> float:
    """PR = (sum(eig))^2 / sum(eig^2)."""
    eig = eigenvalues.clamp(min=1e-12)
    return (eig.sum() ** 2 / (eig**2).sum()).item()


def compute_cv_pr(weight: torch.Tensor, n_seeds: int = 20, rank: int = 50) -> dict:
    """Compute CV of participation ratio across seeds."""
    prs = []
    for seed in range(n_seeds):
        S = randomized_svd(weight.float(), rank, seed)
        prs.append(participation_ratio(S**2))
    prs_t = torch.tensor(prs)
    mean_pr = prs_t.mean().item()
    std_pr = prs_t.std().item()
    cv = std_pr / mean_pr if mean_pr > 0 else float("nan")
    return {"cv_pr": cv, "mean_pr": mean_pr, "std_pr": std_pr}
