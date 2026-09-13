"""Wikipedia coverage validation."""
import wikipediaapi
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import time


class WikipediaChecker:
    """Check Wikipedia coverage for entity list."""

    def __init__(self, max_workers: int = 10, min_content_length: int = 100):
        self.max_workers = max_workers
        self.min_content_length = min_content_length
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='h-c1-validator/1.0'
        )

    def check_coverage(self, entities: List[str]) -> Dict[str, float]:
        """
        Check Wikipedia coverage for entity list.

        Args:
            entities: Entity names to check

        Returns:
            {
                "coverage": float,  # Percentage covered
                "covered_count": int,
                "total_count": int
            }
        """
        if not entities:
            return {"coverage": 0.0, "covered_count": 0, "total_count": 0}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self._check_entity, entities))

        covered = sum(results)

        return {
            "coverage": covered / len(entities),
            "covered_count": covered,
            "total_count": len(entities)
        }

    def _check_entity(self, entity: str) -> bool:
        """
        Single entity coverage check with retry.

        Returns:
            True if exists + non-stub
        """
        for attempt in range(2):  # One retry
            try:
                page = self.wiki.page(entity)

                if not page.exists():
                    return False

                # Non-stub check
                if len(page.text) < self.min_content_length:
                    return False

                return True

            except Exception as e:
                if attempt == 1:
                    print(f"Warning: Wikipedia API failed for '{entity}': {e}")
                    return False
                time.sleep(1)

        return False


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "data"))
    from loader import TruthfulQALoader

    loader = TruthfulQALoader()
    _, entities = loader.load_entity_subset()

    checker = WikipediaChecker()
    result = checker.check_coverage(entities)

    print(f"Wikipedia Coverage: {result['coverage']:.3f}")
    print(f"Covered: {result['covered_count']}/{result['total_count']}")
