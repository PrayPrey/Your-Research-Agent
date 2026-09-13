#!/usr/bin/env python3
"""
Install and configure YouRA Claude Code hooks for the current repository.

Run this script with the Python interpreter that should execute the hooks:

    python install_hooks.py --install-deps

The script intentionally writes absolute paths into .claude/settings.local.json,
because Claude Code hook commands are executed outside this installer process.
Re-run the script after copying the repository to another location.
"""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REQUIRED_RUNTIME_MODULES = ("requests", "yaml", "dotenv", "openai")
REQUIRED_TEST_MODULES = ("pytest",)


class InstallError(RuntimeError):
    """Raised when installation cannot continue safely."""


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent


def is_virtual_environment() -> bool:
    if os.environ.get("CONDA_PREFIX"):
        return True
    if (Path(sys.prefix) / "conda-meta").is_dir():
        return True
    if (Path(sys.prefix) / "pyvenv.cfg").exists():
        return True
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def current_environment_prefix() -> Path:
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        return Path(conda_prefix).expanduser().resolve()
    return Path(sys.prefix).expanduser().resolve()


def detect_environment_python(override: Path | None = None) -> Path:
    if override is not None:
        return override.expanduser().resolve()

    env_prefix = current_environment_prefix()
    candidates = [
        Path(sys.executable),
        env_prefix / "bin" / "python",
        env_prefix / "bin" / f"python{sys.version_info.major}.{sys.version_info.minor}",
    ]
    for candidate in candidates:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate.resolve()

    raise InstallError(f"No executable Python found for environment: {env_prefix}")


def run_command(cmd: list[str], *, cwd: Path | None = None) -> None:
    printable = " ".join(shlex.quote(part) for part in cmd)
    print(f"$ {printable}")
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def install_dependencies(requirements_path: Path) -> None:
    if not requirements_path.exists():
        raise InstallError(f"requirements.txt not found: {requirements_path}")
    run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])


def check_python_environment(require_venv: bool) -> None:
    print(f"Python: {sys.executable}")
    print(f"Prefix: {sys.prefix}")
    print(f"Environment: {current_environment_prefix()}")
    if require_venv and not is_virtual_environment():
        raise InstallError(
            "This script must be run inside the virtualenv/conda environment "
            "that should execute .claude/hooks/*.py. Re-run with that Python, "
            "or pass --allow-system-python if this is intentional."
        )


def check_modules(include_tests: bool) -> None:
    required = list(REQUIRED_RUNTIME_MODULES)
    if include_tests:
        required.extend(REQUIRED_TEST_MODULES)

    missing: list[str] = []
    for module_name in required:
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(module_name)

    if missing:
        raise InstallError(
            "Missing Python modules in this environment: "
            f"{', '.join(missing)}. Run again with --install-deps."
        )


def find_claude_binary(override: str | None = None) -> Path:
    if override:
        candidate = Path(override).expanduser()
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate.resolve()
        raise InstallError(f"Claude CLI override is not executable: {candidate}")

    home_default = Path.home() / ".local" / "bin" / "claude"
    if home_default.exists() and os.access(home_default, os.X_OK):
        return home_default.resolve()

    which_claude = shutil.which("claude")
    detail = f" PATH has {which_claude}, but phase launchers check ~/.local/bin/claude." if which_claude else ""
    raise InstallError(
        "Claude Code CLI was not found. Install Claude Code and make sure "
        "`claude` is executable at ~/.local/bin/claude because the phase "
        f"launchers currently check that path.{detail}"
    )


def check_claude(override: str | None = None) -> Path:
    claude_bin = find_claude_binary(override)
    print(f"Claude CLI: {claude_bin}")
    try:
        subprocess.run(
            [str(claude_bin), "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        raise InstallError(f"Claude CLI version check timed out: {claude_bin}") from exc
    except subprocess.CalledProcessError as exc:
        output = (exc.stdout or exc.stderr or "").strip()
        raise InstallError(f"Claude CLI is present but not working: {output}") from exc
    return claude_bin


def shell_command(*parts: Path | str) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


# Canonical hook layout managed by this installer. Any hook whose command
# references one of these scripts but lives under a different (event, matcher)
# — e.g. left over from an older layout or a tree copied from elsewhere — is
# pruned before the canonical entries are (re)written, so re-running the
# installer always converges to exactly this set with current-repo paths.
MANAGED_HOOKS: list[dict[str, Any]] = [
    {"event": "Stop", "matcher": None,
     "script": "hook_router.py", "timeout": 1200},
    {"event": "PreToolUse", "matcher": "Bash",
     "script": "guard_bash.py", "timeout": 5},
    {"event": "PreToolUse", "matcher": "Read|Edit|Write|MultiEdit|NotebookEdit",
     "script": "guard_state_files.py", "timeout": 5},
]


def prune_managed_hooks(settings: dict[str, Any]) -> int:
    """Remove managed-script hooks that sit under the wrong (event, matcher),
    plus duplicates within the right entry. Returns the number removed."""
    canonical = {spec["script"]: (spec["event"], spec["matcher"])
                 for spec in MANAGED_HOOKS}
    removed = 0
    hooks_root = settings.get("hooks", {})
    for event, entries in list(hooks_root.items()):
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_hooks = entry.get("hooks")
            if not isinstance(entry_hooks, list):
                continue
            seen_scripts: set[str] = set()
            kept: list[Any] = []
            for hook in entry_hooks:
                command = str(hook.get("command", "")) if isinstance(hook, dict) else ""
                script = next((s for s in canonical if s in command), None)
                if script is None:
                    kept.append(hook)  # not ours — leave untouched
                    continue
                right_place = canonical[script] == (event, entry.get("matcher"))
                if right_place and script not in seen_scripts:
                    seen_scripts.add(script)
                    kept.append(hook)
                else:
                    removed += 1
            entry["hooks"] = kept
        # Drop entries whose hook list ended up empty.
        hooks_root[event] = [e for e in entries
                             if not isinstance(e, dict) or e.get("hooks")]
        if not hooks_root[event]:
            del hooks_root[event]
    return removed


def load_settings(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "$schema": "https://json.schemastore.org/claude-code-settings.json",
            "_comment": "YouRA hook settings generated by install_hooks.py",
            "hooks": {},
        }

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise InstallError(f"Invalid JSON object in {path}")
    data.setdefault("hooks", {})
    return data


def update_event_command(
    settings: dict[str, Any],
    *,
    event: str,
    script_name: str,
    command: str,
    timeout: int,
    matcher: str | None = None,
) -> bool:
    hooks_root = settings.setdefault("hooks", {})
    event_entries = hooks_root.setdefault(event, [])
    if not isinstance(event_entries, list):
        raise InstallError(f"settings.hooks.{event} must be a list")

    target_entry: dict[str, Any] | None = None

    for entry in event_entries:
        if not isinstance(entry, dict):
            continue
        if matcher is not None and entry.get("matcher") != matcher:
            continue
        entry_hooks = entry.get("hooks", [])
        if not isinstance(entry_hooks, list):
            continue
        for hook in entry_hooks:
            if not isinstance(hook, dict):
                continue
            if hook.get("type") == "command" and script_name in str(hook.get("command", "")):
                hook["command"] = command
                hook["timeout"] = timeout
                return True
        if matcher is not None and target_entry is None:
            target_entry = entry

    new_hook = {"type": "command", "command": command, "timeout": timeout}
    if target_entry is not None:
        target_entry.setdefault("hooks", []).append(new_hook)
        return True

    new_entry: dict[str, Any] = {"hooks": [new_hook]}
    if matcher is not None:
        new_entry["matcher"] = matcher
    event_entries.append(new_entry)
    return True


def update_settings_file(settings_path: Path, hooks_dir: Path, python_exe: Path) -> None:
    settings = load_settings(settings_path)
    settings["_comment"] = "YouRA hook settings generated by install_hooks.py"
    settings["_usage"] = "Run `python install_hooks.py --install-deps` from the target environment after moving this repository."

    pruned = prune_managed_hooks(settings)
    if pruned:
        print(f"Pruned {pruned} stale/misplaced managed hook entr{'y' if pruned == 1 else 'ies'}.")

    for spec in MANAGED_HOOKS:
        update_event_command(
            settings,
            event=spec["event"],
            matcher=spec["matcher"],
            script_name=spec["script"],
            command=shell_command(python_exe, hooks_dir / spec["script"]),
            timeout=spec["timeout"],
        )
        print(f"Hook registered: {spec['event']}"
              + (f"[{spec['matcher']}]" if spec["matcher"] else "")
              + f" -> {hooks_dir / spec['script']}")

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with settings_path.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")


def update_auto_responder_config(config_path: Path, prompts_dir: Path) -> None:
    if not config_path.exists():
        raise InstallError(f"auto_responder_config.yaml not found: {config_path}")

    text = config_path.read_text(encoding="utf-8")
    new_line = f'prompts_dir: "{prompts_dir}"'
    pattern = r"(?m)^prompts_dir:\s*.*$"
    if re.search(pattern, text):
        text = re.sub(pattern, new_line, text, count=1)
    else:
        text = text.rstrip() + "\n\n" + new_line + "\n"
    config_path.write_text(text, encoding="utf-8")


def compile_hook_python(hooks_dir: Path) -> None:
    errors: list[str] = []
    for path in sorted(hooks_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path}: {exc}")
    if errors:
        raise InstallError("Python syntax check failed:\n" + "\n".join(errors))


def check_required_files(repo_root: Path) -> tuple[Path, Path, Path, Path]:
    hooks_dir = repo_root / ".claude" / "hooks"
    prompts_dir = repo_root / ".claude" / "prompts"
    settings_path = repo_root / ".claude" / "settings.local.json"
    config_path = hooks_dir / "auto_responder_config.yaml"

    required = [
        hooks_dir / "hook_router.py",
        hooks_dir / "guard_bash.py",
        hooks_dir / "guard_state_files.py",
        hooks_dir / "ablation_state_manager.py",
        config_path,
        prompts_dir,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise InstallError("Required files/directories are missing:\n" + "\n".join(missing))

    return hooks_dir, prompts_dir, settings_path, config_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install dependencies and configure Claude Code hooks for this repository."
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install Python dependencies into the current environment before verification.",
    )
    parser.add_argument(
        "--requirements",
        type=Path,
        default=None,
        help="Requirements file to install. Defaults to <repo>/requirements.txt.",
    )
    parser.add_argument(
        "--python",
        dest="python_exe",
        type=Path,
        default=None,
        help="Python executable to write into settings.local.json. Defaults to sys.executable.",
    )
    parser.add_argument(
        "--claude-bin",
        default=None,
        help="Claude CLI path to verify. Defaults to ~/.local/bin/claude.",
    )
    parser.add_argument(
        "--allow-system-python",
        action="store_true",
        help="Allow configuring hooks with a non-venv system Python.",
    )
    parser.add_argument(
        "--skip-claude-check",
        action="store_true",
        help="Do not verify that Claude Code CLI is installed and runnable.",
    )
    parser.add_argument(
        "--skip-test-deps",
        action="store_true",
        help="Do not require pytest when checking installed modules.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print planned paths without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    requirements_path = args.requirements or (repo_root / "requirements.txt")
    hooks_dir, prompts_dir, settings_path, config_path = check_required_files(repo_root)
    python_exe = detect_environment_python(args.python_exe)

    try:
        check_python_environment(require_venv=not args.allow_system_python)
        if args.install_deps:
            install_dependencies(requirements_path)
        check_modules(include_tests=not args.skip_test_deps)
        if not args.skip_claude_check:
            check_claude(args.claude_bin)

        print(f"Repository: {repo_root}")
        print(f"Hooks: {hooks_dir}")
        print(f"Prompts: {prompts_dir}")
        print(f"Settings: {settings_path}")
        print(f"Config: {config_path}")
        print(f"Settings Python: {python_exe}")

        if args.dry_run:
            print("Dry run complete; no files were changed.")
            return 0

        update_settings_file(settings_path, hooks_dir, python_exe)
        update_auto_responder_config(config_path, prompts_dir)
        compile_hook_python(hooks_dir)

        print("Installed YouRA Claude Code hooks for this repository.")
        return 0
    except InstallError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
