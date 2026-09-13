"""
Divergence Classifier for h-m2
Classifies timeout proofs as divergent vs. difficult based on search patterns.
"""

from typing import Dict, Tuple, Any, List


class DivergenceClassifier:
    """
    Classifies whether a timeout is due to divergence or difficulty.

    Divergence Markers:
    - State hash collisions: Cyclic behavior (revisiting same states)
    - High backtrack frequency: Search instability

    Classification Logic:
    - Divergent: collisions > threshold OR backtracks > threshold
    - Difficult: Neither condition met (hard but valid search)
    """

    def __init__(self, collision_threshold: int = 2, backtrack_threshold: int = 5):
        """
        Args:
            collision_threshold: Min collisions to classify as divergent
            backtrack_threshold: Min backtracks to classify as divergent
        """
        self.collision_threshold = collision_threshold
        self.backtrack_threshold = backtrack_threshold

    def classify_timeout(self, search_tree: Any, proof_states: List[Any]) -> Tuple[bool, Dict[str, int]]:
        """
        Classify timeout as divergent or difficult.

        Args:
            search_tree: SearchTree object with nodes, edges, hashes
            proof_states: List of proof states from search

        Returns:
            (is_divergent, markers) where markers = {
                "collision_count": int,
                "backtrack_count": int
            }
        """
        if search_tree is None:
            # No tree data → classify as difficult by default
            return False, {"collision_count": 0, "backtrack_count": 0}

        # Detect state collisions
        collision_count = self._detect_state_collisions(search_tree)

        # Count backtracks
        backtrack_count = self._count_backtracks(search_tree)

        # Classify using OR logic: divergent if EITHER condition met
        is_divergent = (
            collision_count > self.collision_threshold or
            backtrack_count > self.backtrack_threshold
        )

        markers = {
            "collision_count": collision_count,
            "backtrack_count": backtrack_count
        }

        return is_divergent, markers

    def _detect_state_collisions(self, search_tree: Any) -> int:
        """
        Count state hash collisions (cyclic patterns).

        Collision = same state visited multiple times.
        """
        return search_tree.get_collision_count()

    def _count_backtracks(self, search_tree: Any) -> int:
        """
        Count number of backtracks (abandoned branches).

        Backtrack = node with multiple children (tried multiple tactics).
        """
        return search_tree.get_backtrack_count()


def test_divergence_classifier():
    """Test divergence classification logic."""
    print("Testing DivergenceClassifier...")

    # Mock search tree
    class MockTree:
        def __init__(self, collisions, backtracks):
            self._collisions = collisions
            self._backtracks = backtracks

        def get_collision_count(self):
            return self._collisions

        def get_backtrack_count(self):
            return self._backtracks

    classifier = DivergenceClassifier(collision_threshold=2, backtrack_threshold=5)

    # Test Case 1: High collisions → divergent
    tree1 = MockTree(collisions=5, backtracks=2)
    is_div, markers = classifier.classify_timeout(tree1, [])
    assert is_div == True, "High collisions should → divergent"
    print(f"✓ Test 1 passed: collisions={markers['collision_count']} → divergent")

    # Test Case 2: High backtracks → divergent
    tree2 = MockTree(collisions=1, backtracks=8)
    is_div, markers = classifier.classify_timeout(tree2, [])
    assert is_div == True, "High backtracks should → divergent"
    print(f"✓ Test 2 passed: backtracks={markers['backtrack_count']} → divergent")

    # Test Case 3: Low both → difficult
    tree3 = MockTree(collisions=1, backtracks=2)
    is_div, markers = classifier.classify_timeout(tree3, [])
    assert is_div == False, "Low both should → difficult"
    print(f"✓ Test 3 passed: low markers → difficult")

    print("✓ All tests passed!")


if __name__ == "__main__":
    test_divergence_classifier()
