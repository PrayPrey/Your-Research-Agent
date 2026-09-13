"""SAT Dataset Infrastructure for G4SATBench 3-SAT."""
from typing import List, Tuple
from pathlib import Path
import torch
from torch import Tensor
from torch.utils.data import Dataset, DataLoader
from torch_geometric.data import Data, Batch


class BipartiteSATData(Data):
    """Custom Data class for bipartite SAT graphs with proper batching."""

    def __inc__(self, key, value, *args, **kwargs):
        """Custom increment for bipartite graph edges and batch indices."""
        if key == 'edge_index':
            # edge_index[0] are clause indices, edge_index[1] are literal indices
            # Return per-row increments: [n_clauses, n_literals]
            return torch.tensor([[self.n_clauses], [self.n_literals]])
        elif key == 'literal_batch':
            # Increment batch index by 1 for each new instance
            return 1
        return super().__inc__(key, value, *args, **kwargs)


class G4SATDataset(Dataset):
    """G4SATBench 3-SAT dataset loader."""

    def __init__(self, root: str, split: str = 'train', difficulty: str = 'easy'):
        """
        Args:
            root: Path to G4SATBench data folder
            split: 'train', 'valid', or 'test'
            difficulty: 'easy', 'medium', or 'hard'
        """
        self.root = Path(root)
        self.split = split
        self.difficulty = difficulty

        # Path to split data
        split_path = self.root / 'data' / '3-sat' / difficulty / split

        # Load SAT and UNSAT files
        sat_files = sorted((split_path / 'sat').glob('*.cnf'))
        unsat_files = sorted((split_path / 'unsat').glob('*.cnf'))

        self.file_list = []
        for f in sat_files:
            self.file_list.append((f, True))  # (path, is_sat)
        for f in unsat_files:
            self.file_list.append((f, False))

        if len(self.file_list) == 0:
            raise ValueError(f"No CNF files found in {split_path}")

    def __len__(self) -> int:
        return len(self.file_list)

    def __getitem__(self, idx: int) -> Data:
        """
        Returns:
            Data(x_literal=[L, 128], x_clause=[C, 128], edge_index=[2, E], is_sat=bool)
        """
        filepath, is_sat = self.file_list[idx]

        # Parse DIMACS CNF
        clauses = self._parse_dimacs(filepath)

        # Build literal-clause bipartite graph
        n_vars = max(abs(lit) for clause in clauses for lit in clause)
        n_literals = 2 * n_vars  # [1, -1, 2, -2, ..., n, -n]
        n_clauses = len(clauses)

        # Build edge index (clause -> literal connections)
        edge_list = []
        for clause_idx, clause in enumerate(clauses):
            for lit in clause:
                # Map literal to index: 1 -> 0, -1 -> 1, 2 -> 2, -2 -> 3, etc.
                lit_idx = (abs(lit) - 1) * 2 + (0 if lit > 0 else 1)
                edge_list.append([clause_idx, lit_idx])

        edge_index = torch.tensor(edge_list, dtype=torch.long).t()  # [2, E]

        # Create BipartiteSATData with custom batching behavior
        # Add batch assignment for literals (all belong to batch 0 for single instance)
        literal_batch = torch.zeros(n_literals, dtype=torch.long)

        data = BipartiteSATData(
            x_literal=None,  # Model will initialize from learned parameters
            x_clause=None,   # Model will initialize from learned parameters
            edge_index=edge_index,
            is_sat=torch.tensor([is_sat], dtype=torch.bool),
            num_vars=n_vars,
            clauses=clauses,
            n_literals=n_literals,
            n_clauses=n_clauses,
            literal_batch=literal_batch  # Batch assignment for literals
        )
        return data

    def _parse_dimacs(self, filepath: Path) -> List[List[int]]:
        """Parse DIMACS CNF file."""
        clauses = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('c') or line.startswith('p'):
                    continue
                # Parse clause
                literals = [int(x) for x in line.split() if x != '0']
                if literals:
                    clauses.append(literals)
        return clauses


def collate_sat_batch(batch: List[Data]) -> Batch:
    """Custom collate for variable-size SAT instances."""
    # PyG will use __inc__ method from Data objects for proper offsetting
    return Batch.from_data_list(batch)


class SATDataLoader:
    """DataLoader wrapper for train/val/test splits."""

    def __init__(self, root: str, batch_size: int = 128, num_workers: int = 4):
        self.root = root
        self.batch_size = batch_size
        self.num_workers = num_workers

    def get_train_loader(self) -> DataLoader:
        """Returns training DataLoader."""
        dataset = G4SATDataset(self.root, split='train', difficulty='easy')
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            collate_fn=collate_sat_batch
        )

    def get_val_loader(self) -> DataLoader:
        """Returns validation DataLoader."""
        dataset = G4SATDataset(self.root, split='valid', difficulty='easy')
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            collate_fn=collate_sat_batch
        )

    def get_test_loader(self) -> DataLoader:
        """Returns test DataLoader."""
        dataset = G4SATDataset(self.root, split='test', difficulty='easy')
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            collate_fn=collate_sat_batch
        )
