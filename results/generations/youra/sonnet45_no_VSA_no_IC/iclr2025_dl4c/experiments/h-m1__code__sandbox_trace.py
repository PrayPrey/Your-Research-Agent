"""Extended execution sandbox with stack trace depth extraction."""

import sys
import signal
import traceback
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Import from h-e1
import os
import sys
sys.path.insert(0, os.path.abspath("../../h-e1/code"))
from sandbox import ExecutionSandbox, TimeoutException, timeout_handler

class TraceSandbox(ExecutionSandbox):
    def __init__(self, config: dict):
        super().__init__(config)
        self.trace_config = config["execution_sandbox"]["error_trace"]
        self.depth_divisor = self.trace_config["depth_penalty_divisor"]
        self.min_penalty = self.trace_config["min_penalty"]
        self.max_penalty = self.trace_config["max_penalty"]

    def extract_stack_depth(self, exc_info: tuple) -> int:
        """Extract stack depth from exception info.

        Args:
            exc_info: sys.exc_info() tuple

        Returns:
            depth in [0-9], clamped
        """
        if exc_info[2] is None:
            return 0
        tb = traceback.extract_tb(exc_info[2])
        depth = len(tb)
        return min(depth, 9)

    def compute_error_trace_reward(self, code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return error_type_reward × depth_penalty.

        Args:
            code: Generated code
            test: Test suite code
            entry_point: Function name to test

        Returns:
            float in [0.0, 1.0]
        """
        program = code + "\n" + test + f"\ncheck({entry_point})"
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.timeout))

        try:
            exec_globals = {}
            exec(program, exec_globals)
            signal.alarm(0)
            return self.error_type_rewards["Pass"]

        except TimeoutException:
            return self.error_type_rewards["Timeout"] * 1.0  # depth=0 for timeout

        except Exception as e:
            exc_info = sys.exc_info()
            depth = self.extract_stack_depth(exc_info)
            depth_penalty = max(self.min_penalty, min(self.max_penalty, 1.0 - (depth / self.depth_divisor)))

            # Get error type reward from parent class logic
            error_name = type(e).__name__
            if error_name == "SyntaxError":
                base_reward = self.error_type_rewards["SyntaxError"]
            elif error_name == "TypeError":
                base_reward = self.error_type_rewards["TypeError"]
            elif error_name == "NameError":
                base_reward = self.error_type_rewards["NameError"]
            elif error_name == "ValueError":
                base_reward = self.error_type_rewards["ValueError"]
            elif error_name == "AssertionError":
                base_reward = self.error_type_rewards["AssertionError"]
            else:
                base_reward = self.error_type_rewards["OtherError"]

            logger.debug(f"Error {error_name} at depth {depth}: {base_reward} × {depth_penalty:.2f} = {base_reward * depth_penalty:.3f}")
            return base_reward * depth_penalty

        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    def batch_compute_rewards(self, samples: list, test_suite: dict, reward_type: str = "binary") -> list:
        """Compute rewards for a batch of samples."""
        rewards = []
        for sample in samples:
            if reward_type == "binary":
                reward = self.compute_binary_reward(sample, test_suite["test"], test_suite["entry_point"])
            elif reward_type == "error_type":
                reward = self.compute_error_type_reward(sample, test_suite["test"], test_suite["entry_point"])
            elif reward_type == "error_trace":
                reward = self.compute_error_trace_reward(sample, test_suite["test"], test_suite["entry_point"])
            else:
                raise ValueError(f"Unknown reward type: {reward_type}")
            rewards.append(reward)

        return rewards
