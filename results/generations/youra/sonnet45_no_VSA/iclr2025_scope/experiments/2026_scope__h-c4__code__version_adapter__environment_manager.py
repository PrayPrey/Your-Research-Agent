"""Environment manager for isolated library version testing."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


class EnvironmentCreationError(Exception):
    """Raised when environment creation fails."""
    pass


@dataclass
class Environment:
    """Isolated library environment."""
    name: str
    library: str
    version: str
    python_path: str
    conda_prefix: Path

    def run_script(self, script_path: Path, timeout: float = 30.0) -> 'ExecutionResult':
        """Execute Python script in this environment."""
        from .execution_runner import ExecutionRunner
        runner = ExecutionRunner(timeout=timeout)
        return runner.run_in_environment(self, str(script_path), [])

    def install_package(self, package: str) -> None:
        """Install additional package in this environment."""
        subprocess.run(
            [self.python_path, "-m", "pip", "install", package],
            check=True,
            capture_output=True,
            text=True
        )

    def export_spec(self) -> dict:
        """Export environment specification."""
        return {
            "name": self.name,
            "library": self.library,
            "version": self.version,
            "python_path": self.python_path,
            "conda_prefix": str(self.conda_prefix)
        }


class EnvironmentManager:
    """Manages isolated conda environments for version testing."""

    def __init__(self, base_path: Path = Path('.envs')):
        self.base_path = base_path
        self.base_path.mkdir(exist_ok=True)
        self.environments: Dict[str, Environment] = {}

    def create_environment(self, library: str, version: str) -> Environment:
        """
        Create isolated conda environment for library version.

        Args:
            library: "pytorch" | "transformers" | "numpy"
            version: Semantic version string (e.g., "2.1.0")

        Returns:
            Environment object with isolated installation

        Raises:
            EnvironmentCreationError: If conda create fails
        """
        env_key = f"{library}-{version}"

        # Check cache
        if env_key in self.environments:
            return self.environments[env_key]

        env_name = env_key
        env_path = self.base_path / env_name

        # Check if environment already exists
        if env_path.exists() and (env_path / "bin" / "python").exists():
            python_path = str(env_path / "bin" / "python")
            env = Environment(
                name=env_name,
                library=library,
                version=version,
                python_path=python_path,
                conda_prefix=env_path
            )
            self.environments[env_key] = env
            return env

        try:
            # Create conda environment
            subprocess.run(
                ["conda", "create", "-p", str(env_path), "python=3.10", "-y"],
                check=True,
                capture_output=True,
                text=True
            )

            python_path = str(env_path / "bin" / "python")

            # Install target library version
            if library == "pytorch":
                subprocess.run(
                    [python_path, "-m", "pip", "install",
                     f"torch=={version}", "--index-url",
                     "https://download.pytorch.org/whl/cpu"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            elif library == "transformers":
                subprocess.run(
                    [python_path, "-m", "pip", "install",
                     f"transformers=={version}"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            elif library == "numpy":
                subprocess.run(
                    [python_path, "-m", "pip", "install",
                     f"numpy=={version}"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            else:
                raise EnvironmentCreationError(f"Unknown library: {library}")

            # Create environment object
            env = Environment(
                name=env_name,
                library=library,
                version=version,
                python_path=python_path,
                conda_prefix=env_path
            )

            # Cache
            self.environments[env_key] = env

            # Export spec
            spec_file = env_path / "environment.json"
            spec_file.write_text(json.dumps(env.export_spec(), indent=2))

            return env

        except subprocess.CalledProcessError as e:
            raise EnvironmentCreationError(
                f"Failed to create environment for {library} {version}: {e.stderr}"
            )

    def get_environment(self, library: str, version: str) -> Optional[Environment]:
        """Retrieve existing environment or None."""
        env_key = f"{library}-{version}"
        return self.environments.get(env_key)

    def list_environments(self) -> List[Environment]:
        """List all created environments."""
        return list(self.environments.values())

    def cleanup_environment(self, env: Environment) -> None:
        """Remove conda environment and free disk space."""
        if env.conda_prefix.exists():
            subprocess.run(
                ["rm", "-rf", str(env.conda_prefix)],
                check=True
            )

        env_key = f"{env.library}-{env.version}"
        if env_key in self.environments:
            del self.environments[env_key]
