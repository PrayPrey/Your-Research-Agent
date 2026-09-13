"""Heterogeneity metrics for basin entry validation."""
import numpy as np
from numpy import ndarray
from typing import List, Dict, Tuple, Optional
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pysat.solvers import Solver


def solve_sat_instance(clauses: List[List[int]], num_vars: int) -> Tuple[bool, Optional[ndarray]]:
    """
    Solve SAT instance using pysat solver.
    Args:
        clauses: List of clause literals
        num_vars: Number of variables
    Returns:
        (is_sat, assignment): is_sat=True if satisfiable, assignment=[n] boolean array
                              For UNSAT instances, assignment is None
    """
    solver = Solver(name='glucose3')

    # Add clauses to solver
    for clause in clauses:
        solver.add_clause(clause)

    # Solve
    if solver.solve():
        # Get model (solution)
        model = solver.get_model()
        # Convert to boolean array (positive literal = True, negative = False)
        assignment = np.zeros(num_vars, dtype=bool)
        for lit in model:
            var_idx = abs(lit) - 1  # Convert to 0-indexed
            if var_idx < num_vars:
                assignment[var_idx] = (lit > 0)
        solver.delete()
        return True, assignment
    else:
        # UNSAT - no satisfying assignment exists
        solver.delete()
        return False, None


def compute_hamming_distance(assignment: ndarray, ground_truth: ndarray) -> float:
    """
    Compute normalized Hamming distance d/n.
    Args:
        assignment: [n] predicted assignment
        ground_truth: [n] ground truth assignment
    Returns:
        d_n in [0, 1]
    """
    violations = (assignment != ground_truth).sum()
    return float(violations) / len(assignment)


def compute_violation_entropy(assignment: ndarray, clauses: List[List[int]]) -> float:
    """
    Compute violation pattern entropy H = -Σ p_i log p_i.
    Args:
        assignment: [n] variable assignment (boolean)
        clauses: List of clause literals
    Returns:
        H: entropy value
    """
    violation_counts = {}

    for clause in clauses:
        # Check if clause is satisfied
        satisfied = any(
            (assignment[abs(lit) - 1] if lit > 0 else not assignment[abs(lit) - 1])
            for lit in clause
        )

        if not satisfied:
            # Record violation
            clause_key = tuple(sorted(clause))
            violation_counts[clause_key] = violation_counts.get(clause_key, 0) + 1

    if not violation_counts:
        return 0.0

    # Compute entropy
    total_violations = sum(violation_counts.values())
    entropy = 0.0
    for count in violation_counts.values():
        p_i = count / total_violations
        entropy -= p_i * np.log(p_i + 1e-10)

    return float(entropy)


def compute_heterogeneity_metrics(
    assignments: List[ndarray],
    ground_truths: List[ndarray],
    clauses_list: List[List[List[int]]]
) -> Dict[str, float]:
    """
    Compute heterogeneity distribution metrics.
    Returns: {d_n_range, d_n_iqr, d_n_mean, d_n_std, entropy_range, entropy_mean, entropy_std, pass_criteria}
    """
    dn_values = []
    entropy_values = []

    for assignment, ground_truth, clauses in zip(assignments, ground_truths, clauses_list):
        dn = compute_hamming_distance(assignment, ground_truth)
        entropy = compute_violation_entropy(assignment, clauses)
        dn_values.append(dn)
        entropy_values.append(entropy)

    dn_values = np.array(dn_values)
    entropy_values = np.array(entropy_values)

    # Gate thresholds
    GATE_THRESHOLD_DN = 0.20
    GATE_THRESHOLD_ENTROPY = 2.0

    metrics = {
        'd_n_range': float(dn_values.max() - dn_values.min()),
        'd_n_iqr': float(np.percentile(dn_values, 75) - np.percentile(dn_values, 25)),
        'd_n_mean': float(dn_values.mean()),
        'd_n_std': float(dn_values.std()),
        'd_n_quartiles': {
            'Q1': float(np.percentile(dn_values, 25)),
            'Q2': float(np.percentile(dn_values, 50)),
            'Q3': float(np.percentile(dn_values, 75)),
        },
        'entropy_range': float(entropy_values.max() - entropy_values.min()),
        'entropy_mean': float(entropy_values.mean()),
        'entropy_std': float(entropy_values.std()),
        'entropy_quartiles': {
            'Q1': float(np.percentile(entropy_values, 25)),
            'Q2': float(np.percentile(entropy_values, 50)),
            'Q3': float(np.percentile(entropy_values, 75)),
        },
        'pass_criteria': bool(
            (dn_values.max() - dn_values.min() > GATE_THRESHOLD_DN) and
            (entropy_values.max() - entropy_values.min() > GATE_THRESHOLD_ENTROPY)
        ),
        'dn_values': dn_values.tolist(),
        'entropy_values': entropy_values.tolist()
    }

    return metrics


class HeterogeneityAnalyzer:
    """Analyzer for basin entry heterogeneity."""

    def __init__(self):
        self.gate_threshold_dn = 0.20
        self.gate_threshold_entropy = 2.0

    def collect_solutions(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        device: str
    ) -> Tuple[List[ndarray], List[ndarray], List[List[List[int]]]]:
        """
        Generate assignments from model on test set.
        Only collects SAT instances (with valid ground truth solutions).
        Returns: (assignments, ground_truths, clauses_list)
        """
        model.eval()
        assignments = []
        ground_truths = []
        clauses_list = []

        with torch.no_grad():
            for batch in dataloader:
                batch = batch.to(device)

                # Forward pass
                l_emb, _ = model(batch)

                # Decode assignments for each instance in batch
                batch_size = batch.literal_batch.max().item() + 1
                for i in range(batch_size):
                    # Get literals for this instance
                    mask = batch.literal_batch == i
                    instance_l_emb = l_emb[mask]

                    # Get number of variables
                    num_vars = batch.num_vars[i].item()

                    # Decode assignment
                    assignment = model.decode_assignment(instance_l_emb, num_vars)

                    # Get ground truth by solving the SAT instance
                    is_sat, ground_truth = solve_sat_instance(batch.clauses[i], num_vars)

                    # Only include SAT instances (skip UNSAT - no ground truth exists)
                    if is_sat:
                        assignments.append(assignment.cpu().numpy())
                        ground_truths.append(ground_truth)
                        clauses_list.append(batch.clauses[i])

        return assignments, ground_truths, clauses_list

    def analyze_distribution(
        self,
        assignments: List[ndarray],
        ground_truths: List[ndarray],
        clauses_list: List[List[List[int]]]
    ) -> Dict:
        """Compute heterogeneity metrics."""
        return compute_heterogeneity_metrics(assignments, ground_truths, clauses_list)

    def check_gate_criteria(self, metrics: Dict[str, float]) -> bool:
        """Check if gate thresholds met."""
        return bool(
            metrics['d_n_range'] > self.gate_threshold_dn and
            metrics['entropy_range'] > self.gate_threshold_entropy
        )
