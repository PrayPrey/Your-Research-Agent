"""Version adapter module for multi-version environment management."""

from .environment_manager import Environment, EnvironmentManager
from .execution_runner import ExecutionResult, ExecutionRunner

__all__ = [
    "Environment",
    "EnvironmentManager",
    "ExecutionResult",
    "ExecutionRunner",
]
