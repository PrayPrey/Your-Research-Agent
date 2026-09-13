"""
Extended Timeout Runner
Executes proof search experiments with 300s timeout and confidence monitoring
"""

from typing import List, Dict, Any, Optional
import time
import signal
from contextlib import contextmanager

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.confidence_extractor import ConfidenceTrajectoryExtractor


class TimeoutException(Exception):
    """Exception raised when timeout is reached."""
    pass


@contextmanager
def time_limit(seconds):
    """Context manager for enforcing time limits."""
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class ExtendedTimeoutRunner:
    """Execute proof search experiments with extended 300s timeout and confidence monitoring."""

    def __init__(self, timeout_seconds: int = 300, confidence_window: int = 15):
        """
        Initialize experiment runner.

        Args:
            timeout_seconds: Maximum time per theorem (default 300s)
            confidence_window: Number of steps for confidence extraction
        """
        self.timeout_seconds = timeout_seconds
        self.confidence_window = confidence_window
        self.confidence_extractor = ConfidenceTrajectoryExtractor(confidence_window)

    def run_experiment(self, theorem) -> Dict[str, Any]:
        """
        Run single extended-timeout experiment with confidence extraction.

        Args:
            theorem: LeanDojo Theorem object

        Returns:
            result: {
                'theorem_id': str,
                'confidence_derivative': float,
                'outcome': int (0=success, 1=timeout),
                'execution_time': float (seconds),
                'entropies': List[float],
                'status': str ('success', 'timeout', 'error')
            }
        """
        result = {
            'theorem_id': str(theorem),
            'confidence_derivative': None,
            'outcome': None,
            'execution_time': None,
            'entropies': [],
            'status': 'running'
        }

        start_time = time.time()

        try:
            from lean_dojo import Dojo, ProofFinished, ProofGivenUp, LeanError

            print(f"  Starting proof search for: {theorem}")

            # Initialize LeanDojo proof session
            with Dojo(theorem) as dojo:
                # Extract confidence trajectory during proof search
                print(f"  Extracting confidence trajectory...")
                confidence_derivative, entropies = self.confidence_extractor.extract_confidence_trajectory(dojo)

                # Run proof search with timeout enforcement
                print(f"  Running proof search (timeout={self.timeout_seconds}s)...")
                success = self._enforce_timeout(dojo, self.timeout_seconds)

                # Record results
                result['confidence_derivative'] = confidence_derivative
                result['entropies'] = entropies
                result['outcome'] = 0 if success else 1
                result['execution_time'] = time.time() - start_time
                result['status'] = 'success' if success else 'timeout'

                print(f"  Result: {result['status']} (derivative={confidence_derivative:.4f}, time={result['execution_time']:.2f}s)")

        except TimeoutException:
            result['outcome'] = 1
            result['execution_time'] = time.time() - start_time
            result['status'] = 'timeout'
            print(f"  Timeout after {result['execution_time']:.2f}s")

        except Exception as e:
            result['status'] = 'error'
            result['error_message'] = str(e)
            result['execution_time'] = time.time() - start_time
            print(f"  ERROR: {e}")

        return result

    def run_batch(self, theorems: List, progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """
        Run batch of experiments with progress tracking.

        Args:
            theorems: List of LeanDojo Theorem objects, length = num_theorems
            progress_callback: Optional function(current, total) for progress updates

        Returns:
            results: List of result dicts, length = num_theorems
        """
        results = []
        total = len(theorems)

        print(f"\nRunning batch of {total} experiments...")
        print(f"Timeout: {self.timeout_seconds}s per theorem")
        print(f"Confidence window: {self.confidence_window} steps\n")

        for i, theorem in enumerate(theorems):
            print(f"\n[{i+1}/{total}] Processing theorem {i+1}...")

            result = self.run_experiment(theorem)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total)

            # Progress summary
            if (i + 1) % 10 == 0:
                successes = sum(1 for r in results if r['outcome'] == 0)
                print(f"\nProgress: {i+1}/{total} completed ({successes} successes, {i+1-successes} timeouts/errors)\n")

        return results

    def _enforce_timeout(self, proof_session, timeout: float) -> bool:
        """
        Enforce timeout on proof search session.

        Args:
            proof_session: LeanDojo Dojo session
            timeout: timeout in seconds

        Returns:
            success: True if proof completed, False if timeout
        """
        try:
            with time_limit(int(timeout)):
                # Run proof search until completion or timeout
                while not proof_session.is_done():
                    tactics = proof_session.get_tactics()
                    if not tactics:
                        return False

                    # Apply first tactic (simple strategy for EXISTENCE experiment)
                    tactic, _ = tactics[0]
                    proof_session.run_tac(tactic)

                return True

        except TimeoutException:
            return False
        except Exception as e:
            print(f"    Error during proof search: {e}")
            return False
