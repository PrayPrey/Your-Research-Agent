"""Execution sandbox for code reward computation."""

import signal
import logging
import traceback as tb_module
from typing import Tuple
from rewards import compute_error_trace_reward

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Execution timeout")

class ExecutionSandbox:
    def __init__(self, config: dict):
        self.timeout = config["execution_sandbox"]["timeout"]
        self.binary_rewards = config["execution_sandbox"]["binary_rewards"]
        self.error_type_rewards = config["execution_sandbox"]["error_type_rewards"]

    def compute_binary_reward(self, code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return 1.0 if pass, 0.0 if fail."""
        program = code + "\n" + test + f"\ncheck({entry_point})"

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.timeout))

        try:
            exec_globals = {}
            exec(program, exec_globals)
            signal.alarm(0)
            return self.binary_rewards["pass"]

        except TimeoutException:
            logger.debug(f"Timeout executing code for {entry_point}")
            return self.binary_rewards["fail"]

        except Exception as e:
            logger.debug(f"Execution failed for {entry_point}: {type(e).__name__}")
            return self.binary_rewards["fail"]

        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    def compute_error_type_reward(self, code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return reward based on error type."""
        program = code + "\n" + test + f"\ncheck({entry_point})"

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.timeout))

        try:
            exec_globals = {}
            exec(program, exec_globals)
            signal.alarm(0)
            return self.error_type_rewards["Pass"]

        except TimeoutException:
            return self.error_type_rewards["Timeout"]

        except SyntaxError:
            return self.error_type_rewards["SyntaxError"]

        except TypeError:
            return self.error_type_rewards["TypeError"]

        except NameError:
            return self.error_type_rewards["NameError"]

        except ValueError:
            return self.error_type_rewards["ValueError"]

        except AssertionError:
            return self.error_type_rewards["AssertionError"]

        except Exception as e:
            logger.debug(f"Other error for {entry_point}: {type(e).__name__}")
            return self.error_type_rewards["OtherError"]

        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    def compute_error_trace_reward_method(self, code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return reward based on error type + stack depth."""
        program = code + "\n" + test + f"\ncheck({entry_point})"

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.timeout))

        try:
            exec_globals = {}
            exec(program, exec_globals)
            signal.alarm(0)
            return 1.0

        except TimeoutException:
            return 0.0

        except Exception as e:
            error_str = type(e).__name__
            traceback_str = "".join(tb_module.format_exception(type(e), e, e.__traceback__))
            result = {"passed": False, "error": error_str, "traceback": traceback_str}
            return compute_error_trace_reward(result)

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
                reward = self.compute_error_trace_reward_method(sample, test_suite["test"], test_suite["entry_point"])
            else:
                raise ValueError(f"Unknown reward type: {reward_type}")
            rewards.append(reward)

        return rewards
