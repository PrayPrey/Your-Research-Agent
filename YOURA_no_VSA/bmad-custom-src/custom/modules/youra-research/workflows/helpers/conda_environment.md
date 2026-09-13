---
name: 'conda_environment'
description: 'Reusable functions for conda environment management in Phase 4 and Phase 5 experiment execution'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions (7 functions)
exports:
  - detect_conda_installation
  - get_conda_activate_command
  - create_experiment_env
  - install_requirements
  - verify_imports
  - run_in_conda_env
  - cleanup_environment

# Called By
called_by:
  - 'phase4-coding/steps/step-01-initialize.md'
  - 'phase4-coding/steps/step-05a-pre-validation.md'
  - 'phase5-baseline-repo-comparison/steps/step-06-environment.md'
---

# Conda Environment Helper Functions

> Reusable functions for conda environment management in Phase 4 and Phase 5 experiment execution.
> Handles environment activation, dependency installation, and import verification.

---

## Constants

### Common Paths

```python
# Standard conda installation paths (for auto-detection)
CONDA_SEARCH_PATHS = [
    "/home/anonymous/miniforge3",
    "/home/anonymous/miniconda3",
    "/home/anonymous/anaconda3",
    "/opt/conda",
    "/opt/miniforge3",
    "/opt/miniconda3",
    "C:/Users/anonymous/miniforge3",
    "C:/Users/anonymous/miniconda3",
    "C:/Users/anonymous/anaconda3"
]

# Conda shell initialization scripts
CONDA_INIT_SCRIPTS = {
    "linux": "{conda_path}/etc/profile.d/conda.sh",
    "darwin": "{conda_path}/etc/profile.d/conda.sh",
    "win32": "{conda_path}/Scripts/activate.bat"
}

# Package manager fallback order
INSTALL_FALLBACK_ORDER = ["pip", "conda", "uv", "pip3"]
```

---

## Functions

### 1. detect_conda_path

```python
def detect_conda_path(checkpoint: dict = None) -> dict:
    """
    Auto-detect conda installation path.

    Args:
        checkpoint: Optional checkpoint dict containing conda.conda_path

    Returns:
        Dictionary containing:
            - found: bool - Conda found
            - conda_path: str - Path to conda installation
            - source: str - How path was determined
            - conda_exe: str - Full path to conda executable

    Usage:
        result = detect_conda_path(checkpoint)
        if result["found"]:
            conda_path = result["conda_path"]
    """
    # Priority 1: Check checkpoint
    if checkpoint and checkpoint.get("conda", {}).get("conda_path"):
        conda_path = checkpoint["conda"]["conda_path"]
        return {
            "found": True,
            "conda_path": conda_path,
            "source": "checkpoint",
            "conda_exe": f"{conda_path}/bin/conda"
        }

    # Priority 2: Use `which conda`
    result = Bash("which conda 2>/dev/null || where conda 2>nul")

    if result.success and result.stdout.strip():
        conda_exe = result.stdout.strip().split('\n')[0]
        # conda_exe is like /home/anonymous/miniforge3/bin/conda
        # conda_path is /home/anonymous/miniforge3
        conda_path = os.path.dirname(os.path.dirname(conda_exe))

        return {
            "found": True,
            "conda_path": conda_path,
            "source": "which_command",
            "conda_exe": conda_exe
        }

    # Priority 3: Search common paths
    import glob

    for pattern in CONDA_SEARCH_PATHS:
        matches = glob.glob(pattern)
        for match in matches:
            conda_exe = os.path.join(match, "bin", "conda")
            if os.path.exists(conda_exe):
                return {
                    "found": True,
                    "conda_path": match,
                    "source": "path_search",
                    "conda_exe": conda_exe
                }

    return {
        "found": False,
        "conda_path": None,
        "source": "not_found",
        "conda_exe": None,
        "error": "Conda installation not found. Please ensure conda is installed."
    }
```

### 2. get_conda_init_command

```python
def get_conda_init_command(conda_path: str, platform: str = None) -> str:
    """
    Get the conda initialization command for the current platform.

    Args:
        conda_path: Path to conda installation
        platform: Optional platform override (linux/darwin/win32)

    Returns:
        Shell command string to initialize conda

    Usage:
        init_cmd = get_conda_init_command("/home/anonymous/miniforge3")
        # Returns: "source /home/anonymous/miniforge3/etc/profile.d/conda.sh"
    """
    import sys

    if platform is None:
        platform = sys.platform

    if platform == "win32":
        return f"call {conda_path}\\Scripts\\activate.bat"
    else:
        return f"source {conda_path}/etc/profile.d/conda.sh"
```

### 3. build_conda_run_command

```python
def build_conda_run_command(
    conda_path: str,
    conda_env_name: str,
    command: str,
    platform: str = None
) -> str:
    """
    Build a complete command that runs in conda environment.

    Args:
        conda_path: Path to conda installation
        conda_env_name: Name of conda environment
        command: Command to execute
        platform: Optional platform override

    Returns:
        Complete shell command with conda initialization

    Usage:
        cmd = build_conda_run_command(
            "/home/anonymous/miniforge3",
            "youra-h-e1",
            "python main.py --epochs 100"
        )
        Bash(cmd)
    """
    init_cmd = get_conda_init_command(conda_path, platform)

    return f"{init_cmd} && conda run -n {conda_env_name} {command}"
```

### 4. install_requirements

```python
def install_requirements(
    conda_path: str,
    conda_env_name: str,
    code_folder: str
) -> dict:
    """
    Install requirements.txt with fallback strategies.

    Args:
        conda_path: Path to conda installation
        conda_env_name: Name of conda environment
        code_folder: Path to code folder containing requirements.txt

    Returns:
        Dictionary containing:
            - success: bool - Installation successful
            - method: str - Which method succeeded
            - packages_installed: list - Packages installed
            - failed_packages: list - Packages that failed to install
            - log: str - Installation log

    Usage:
        result = install_requirements(
            conda_path, conda_env_name, code_folder
        )
        if not result["success"]:
            print(f"Failed packages: {result['failed_packages']}")
    """
    requirements_path = f"{code_folder}/requirements.txt"
    log_lines = []
    packages_installed = []
    failed_packages = []

    # Check if requirements.txt exists
    if not os.path.exists(requirements_path):
        return {
            "success": True,
            "method": "no_requirements",
            "packages_installed": [],
            "failed_packages": [],
            "log": "No requirements.txt found"
        }

    # Read requirements
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f
                        if line.strip() and not line.startswith('#')]

    log_lines.append(f"Found {len(requirements)} packages to install")

    # Attempt 1: Install all at once with pip
    init_cmd = get_conda_init_command(conda_path)
    pip_cmd = f"{init_cmd} && conda run -n {conda_env_name} pip install -r {requirements_path}"

    result = Bash(pip_cmd)

    if result.success:
        log_lines.append("All packages installed with pip")
        return {
            "success": True,
            "method": "pip_bulk",
            "packages_installed": requirements,
            "failed_packages": [],
            "log": "\n".join(log_lines)
        }

    log_lines.append(f"Bulk pip install failed: {result.stderr[:200]}")

    # Attempt 2: Install per-package with fallbacks
    for package in requirements:
        installed = False

        # Skip version specifiers for conda
        package_name = package.split('==')[0].split('>=')[0].split('<=')[0].strip()

        for method in INSTALL_FALLBACK_ORDER:
            if method == "pip":
                cmd = f"{init_cmd} && conda run -n {conda_env_name} pip install {package}"
            elif method == "conda":
                cmd = f"{init_cmd} && conda install -n {conda_env_name} {package_name} --yes"
            elif method == "uv":
                cmd = f"{init_cmd} && conda run -n {conda_env_name} uv pip install {package}"
            elif method == "pip3":
                cmd = f"{init_cmd} && conda run -n {conda_env_name} pip3 install {package}"

            result = Bash(cmd, timeout=120000) # 2 minute timeout per package

            if result.success:
                installed = True
                packages_installed.append(package)
                log_lines.append(f"Installed {package} via {method}")
                break

        if not installed:
            failed_packages.append(package)
            log_lines.append(f"FAILED to install {package}")

    success = len(failed_packages) == 0

    return {
        "success": success,
        "method": "per_package_fallback",
        "packages_installed": packages_installed,
        "failed_packages": failed_packages,
        "log": "\n".join(log_lines)
    }
```

### 5. verify_imports

```python
def verify_imports(
    conda_path: str,
    conda_env_name: str,
    code_folder: str,
    main_module: str = None
) -> dict:
    """
    Verify that Python imports work in the conda environment.

    Args:
        conda_path: Path to conda installation
        conda_env_name: Name of conda environment
        code_folder: Path to code folder
        main_module: Optional main module to import test

    Returns:
        Dictionary containing:
            - success: bool - All imports work
            - tested_modules: list - Modules tested
            - failed_imports: list - Imports that failed
            - missing_packages: list - Packages to install

    Usage:
        result = verify_imports(conda_path, conda_env_name, code_folder, "main")
        if not result["success"]:
            for pkg in result["missing_packages"]:
                install_package(pkg)
    """
    init_cmd = get_conda_init_command(conda_path)
    tested_modules = []
    failed_imports = []
    missing_packages = []

    # Test 1: Basic Python
    cmd = f'{init_cmd} && conda run -n {conda_env_name} python -c "print(\'OK\')"'
    result = Bash(cmd)

    if not result.success:
        return {
            "success": False,
            "tested_modules": [],
            "failed_imports": ["python_itself"],
            "missing_packages": [],
            "error": "Python not working in conda environment"
        }

    tested_modules.append("python")

    # Test 2: Common deep learning packages
    common_packages = ["torch", "numpy", "pandas"]

    for pkg in common_packages:
        cmd = f'{init_cmd} && conda run -n {conda_env_name} python -c "import {pkg}"'
        result = Bash(cmd)

        if result.success:
            tested_modules.append(pkg)
        else:
            failed_imports.append(pkg)
            missing_packages.append(pkg)

    # Test 3: Main module import (if specified)
    if main_module:
        cmd = f'{init_cmd} && cd {code_folder} && conda run -n {conda_env_name} python -c "from {main_module} import *"'
        result = Bash(cmd)

        if result.success:
            tested_modules.append(main_module)
        else:
            failed_imports.append(main_module)

            # Extract missing module from error
            if "ModuleNotFoundError" in result.stderr:
                import re
                match = re.search(r"No module named ['\"]([^'\"]+)['\"]", result.stderr)
                if match:
                    missing_packages.append(match.group(1))

    return {
        "success": len(failed_imports) == 0,
        "tested_modules": tested_modules,
        "failed_imports": failed_imports,
        "missing_packages": missing_packages
    }
```

### 6. check_gpu_availability

```python
def check_gpu_availability(
    conda_path: str,
    conda_env_name: str
) -> dict:
    """
    Check GPU availability and CUDA status in conda environment.

    Args:
        conda_path: Path to conda installation
        conda_env_name: Name of conda environment

    Returns:
        Dictionary containing:
            - available: bool - GPU is available
            - count: int - Number of GPUs
            - info: str - GPU information string
            - cuda_version: str - CUDA version (if available)
            - pytorch_cuda: bool - PyTorch CUDA enabled

    Usage:
        gpu = check_gpu_availability(conda_path, conda_env_name)
        if gpu["available"]:
            print(f"Found {gpu['count']} GPU(s): {gpu['info']}")
    """
    init_cmd = get_conda_init_command(conda_path)

    # Check PyTorch CUDA
    pytorch_cmd = f'{init_cmd} && conda run -n {conda_env_name} python -c "import torch; print(f\\"CUDA: {{torch.cuda.is_available()}}, Devices: {{torch.cuda.device_count()}}\\"); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else \\"N/A\\")"'

    result = Bash(pytorch_cmd)

    if result.success:
        output = result.stdout.strip()
        cuda_available = "CUDA: True" in output

        if cuda_available:
            # Extract device count
            import re
            count_match = re.search(r"Devices: (\d+)", output)
            count = int(count_match.group(1)) if count_match else 1

            # Get GPU name from second line
            lines = output.split('\n')
            gpu_name = lines[1].strip() if len(lines) > 1 else "Unknown GPU"

            return {
                "available": True,
                "count": count,
                "info": gpu_name,
                "cuda_version": torch.version.cuda if hasattr(torch, 'version') else None,
                "pytorch_cuda": True
            }

    # Fallback: check nvidia-smi
    nvidia_cmd = "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null"
    nvidia_result = Bash(nvidia_cmd)

    if nvidia_result.success and nvidia_result.stdout.strip():
        lines = nvidia_result.stdout.strip().split('\n')
        return {
            "available": True,
            "count": len(lines),
            "info": lines[0].strip(),
            "cuda_version": None,
            "pytorch_cuda": False,
            "note": "GPU available but PyTorch CUDA not detected"
        }

    return {
        "available": False,
        "count": 0,
        "info": "CPU only",
        "cuda_version": None,
        "pytorch_cuda": False
    }
```

### 7. prepare_conda_env (Main Function)

```python
def prepare_conda_env(
    conda_env_name: str,
    code_folder: str,
    checkpoint: dict = None,
    main_module: str = None
) -> dict:
    """
    Main function: Complete conda environment preparation workflow.

    This is the primary function to call - it orchestrates environment
    detection, dependency installation, and verification.

    Args:
        conda_env_name: Name of conda environment to use
        code_folder: Path to code folder
        checkpoint: Optional checkpoint with conda_path
        main_module: Optional main module for import verification

    Returns:
        Dictionary containing:
            - success: bool - Environment ready
            - conda_path: str - Detected conda path
            - requirements_result: dict - Result from install_requirements
            - import_result: dict - Result from verify_imports
            - gpu_result: dict - Result from check_gpu_availability
            - error: str - Error message if failed

    Usage:
        result = prepare_conda_env("youra-h-e1", code_folder, checkpoint)
        if result["success"]:
            print(f"Environment ready. GPU: {result['gpu_result']['available']}")
        else:
            print(f"Setup failed: {result['error']}")
    """
    log_event("ENV", f"Preparing conda environment: {conda_env_name}")

    # Step 1: Detect conda path
    conda_result = detect_conda_path(checkpoint)

    if not conda_result["found"]:
        return {
            "success": False,
            "error": conda_result.get("error", "Conda not found"),
            "conda_path": None
        }

    conda_path = conda_result["conda_path"]
    log_event("ENV", f"Using conda at: {conda_path}")

    # Step 2: Install requirements
    req_result = install_requirements(conda_path, conda_env_name, code_folder)

    if not req_result["success"]:
        log_event("WARN", f"Some packages failed: {req_result['failed_packages']}")

        # Search Archon KB for solutions
        for pkg in req_result["failed_packages"][:3]: # First 3
            mcp__archon__rag_search_knowledge_base(
                query=f"pip install error {pkg}",
                match_count=3
            )

    # Step 3: Verify imports
    import_result = verify_imports(
        conda_path, conda_env_name, code_folder, main_module
    )

    if not import_result["success"]:
        log_event("WARN", f"Import verification failed: {import_result['failed_imports']}")

        # Try to install missing packages
        for pkg in import_result["missing_packages"]:
            mcp__archon__rag_search_knowledge_base(
                query=f"{pkg} pip install",
                match_count=3
            )

            init_cmd = get_conda_init_command(conda_path)
            Bash(f"{init_cmd} && conda run -n {conda_env_name} pip install {pkg}")

    # Step 4: Check GPU availability
    gpu_result = check_gpu_availability(conda_path, conda_env_name)
    log_event("GPU", f"Available: {gpu_result['available']}, Info: {gpu_result['info']}")

    # Determine overall success
    success = (
        req_result["success"] or len(req_result["failed_packages"]) < 3
    ) and (
        import_result["success"] or len(import_result["failed_imports"]) < 2
    )

    return {
        "success": success,
        "conda_path": conda_path,
        "conda_exe": conda_result["conda_exe"],
        "requirements_result": req_result,
        "import_result": import_result,
        "gpu_result": gpu_result,
        "error": None if success else "Environment preparation had errors"
    }
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Conda not found | No conda installation | Install miniforge/miniconda |
| pip install fails | Network/package issues | Try conda → uv → pip3 fallbacks |
| Import fails | Missing dependency | Check missing_packages list |
| CUDA not available | PyTorch CPU version | Install pytorch-cuda via conda |
| Permission denied | Protected conda install | Use user-local conda |
