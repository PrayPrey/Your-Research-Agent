"""
Extended Timeout Runner with Search Tree Tracking for h-m2
Extends h-m1's ExtendedTimeoutRunner to track search tree structure.
"""

import sys
from pathlib import Path

# Add h-m1 to import path for base class reuse (only if not already there)
h_m1_path = Path(__file__).parent.parent.parent.parent / "h-m1" / "code"
if str(h_m1_path) not in sys.path:
    sys.path.append(str(h_m1_path))  # Use append, not insert(0), to maintain priority

from experiment.runner import ExtendedTimeoutRunner
from typing import Dict, List, Any, Tuple
import hashlib


class SearchTree:
    """Represents proof search tree structure."""

    def __init__(self):
        self.nodes = []  # List of proof states
        self.edges = []  # List of (parent_idx, child_idx) tuples
        self.state_hashes = []  # Hash of each state for collision detection

    def add_node(self, state: Any) -> int:
        """Add proof state to tree, return node index."""
        node_idx = len(self.nodes)
        self.nodes.append(state)

        # Compute state hash for collision detection
        state_str = str(state)
        state_hash = hashlib.md5(state_str.encode()).hexdigest()
        self.state_hashes.append(state_hash)

        return node_idx

    def add_edge(self, parent_idx: int, child_idx: int):
        """Add edge from parent to child state."""
        self.edges.append((parent_idx, child_idx))

    def get_collision_count(self) -> int:
        """Count number of state hash collisions (cyclic patterns)."""
        unique_hashes = len(set(self.state_hashes))
        total_hashes = len(self.state_hashes)
        return total_hashes - unique_hashes

    def get_backtrack_count(self) -> int:
        """Count number of backtracks (abandoned branches)."""
        if not self.edges:
            return 0

        # Backtrack = a node has multiple children (explored multiple branches)
        from collections import defaultdict
        children_count = defaultdict(int)

        for parent_idx, _ in self.edges:
            children_count[parent_idx] += 1

        # Count nodes with more than 1 child (backtrack points)
        backtrack_count = sum(1 for count in children_count.values() if count > 1)
        return backtrack_count


class ExtendedTimeoutRunnerWithTree(ExtendedTimeoutRunner):
    """
    Extends h-m1's ExtendedTimeoutRunner to add search tree tracking.

    Inherits:
        - Confidence extraction (from h-e1 via h-m1)
        - Extended timeout protocol (from h-e1)
        - Variance analysis (from h-m1)

    Adds:
        - Search tree structure tracking
        - State hash collision detection
        - Backtrack frequency counting
    """

    def __init__(self, timeout_seconds: int = 300, confidence_window: int = 15):
        super().__init__(timeout_seconds, confidence_window)
        self.enable_tree_tracking = True

    def run_experiment(self, theorem) -> Dict[str, Any]:
        """
        Run proof search with tree tracking (captures proof states during search).

        Args:
            theorem: LeanDojo Theorem object

        Returns:
            {
                "theorem_id": str,
                "outcome": int (0=success, 1=timeout),
                "confidence_variance": float,
                "entropies": List[float],
                "proof_states": List[state],  # NEW: captured states
                "search_tree": SearchTree,  # NEW: tree structure
                "execution_time": float,
                "status": str
            }
        """
        import time
        from lean_dojo import Dojo, ProofFinished, ProofGivenUp, LeanError

        result = {
            'theorem_id': str(theorem),
            'confidence_variance': None,
            'outcome': None,
            'execution_time': None,
            'entropies': [],
            'proof_states': [],
            'search_tree': None,
            'status': 'running'
        }

        start_time = time.time()

        try:
            # Initialize LeanDojo proof session
            with Dojo(theorem) as dojo:
                # Extract confidence trajectory
                confidence_variance, entropies = self.confidence_extractor.extract_confidence_trajectory(dojo)
                result['confidence_variance'] = confidence_variance
                result['entropies'] = entropies

                # Run proof search with state tracking
                proof_states = []
                success = False

                try:
                    # Attempt proof search and capture states
                    state = dojo.init_state
                    proof_states.append(state)

                    # Simple best-first search with state tracking
                    timeout_start = time.time()
                    while time.time() - timeout_start < self.timeout_seconds:
                        # Get next tactics
                        tactics = dojo.get_tactics(state)
                        if not tactics:
                            break

                        # Try first tactic
                        result_state = dojo.run_tac(state, tactics[0][0])

                        if isinstance(result_state, ProofFinished):
                            success = True
                            break
                        elif isinstance(result_state, (ProofGivenUp, LeanError)):
                            break
                        else:
                            state = result_state
                            proof_states.append(state)

                except Exception as e:
                    print(f"    Proof search error: {e}")

                # Store proof states
                result['proof_states'] = proof_states

                # Build search tree from states
                if self.enable_tree_tracking and not success:
                    result['search_tree'] = self._track_search_tree(proof_states)
                else:
                    result['search_tree'] = None

                result['outcome'] = 0 if success else 1
                result['status'] = 'success' if success else 'timeout'

        except Exception as e:
            result['status'] = 'error'
            result['error_message'] = str(e)
            print(f"  ERROR: {e}")

        result['execution_time'] = time.time() - start_time
        return result

    def _track_search_tree(self, proof_states: List[Any]) -> SearchTree:
        """
        Track search tree structure from proof states.

        For h-m2 PoC, we use a simplified tree construction:
        - Each state becomes a node
        - Sequential states are connected (parent → child)
        - Detect cycles via state hashing
        """
        tree = SearchTree()

        if not proof_states:
            return tree

        # Add first state as root
        prev_idx = tree.add_node(proof_states[0])

        # Add subsequent states
        for state in proof_states[1:]:
            curr_idx = tree.add_node(state)
            tree.add_edge(prev_idx, curr_idx)
            prev_idx = curr_idx

        return tree


def test_tree_tracking():
    """Quick test for tree tracking functionality."""
    print("Testing ExtendedTimeoutRunnerWithTree...")

    # Create mock proof states
    mock_states = [
        {"goal": "∀ n, n + 0 = n", "tactics": ["induction"]},
        {"goal": "0 + 0 = 0", "tactics": ["refl"]},
        {"goal": "∀ n, n + 0 = n", "tactics": ["induction"]},  # Repeat (collision)
        {"goal": "S n + 0 = S n", "tactics": ["apply IH"]},
    ]

    runner = ExtendedTimeoutRunnerWithTree()
    tree = runner._track_search_tree(mock_states)

    assert len(tree.nodes) == 4, "Should have 4 nodes"
    assert len(tree.edges) == 3, "Should have 3 edges"

    collisions = tree.get_collision_count()
    print(f"✓ Tree has {collisions} collision(s)")

    print("✓ Tree tracking test passed!")


if __name__ == "__main__":
    test_tree_tracking()
