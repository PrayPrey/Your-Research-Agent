#!/usr/bin/env python3
"""
PreToolUse guard for Bash — prevents unbounded watchers from pinning Claude turns.

Triggers on Bash tool calls only. Reads tool_input.command, applies safety rewrites:

  1. `tail -f <file>` (no --pid, no timeout wrapper) → `timeout 600 tail -f <file>`
  2. `until ... grep -q ... ; do sleep N; done` (no wall-clock cap) → blocked with guidance
  3. bare `wait` (no PID arg) → blocked with guidance

All other commands pass through unchanged.

Hook contract (Claude Code PreToolUse):
- Read JSON from stdin: {"tool_name":"Bash","tool_input":{"command":"..."}, ...}
- Print JSON to stdout. Recognized fields:
    {"decision":"block","reason":"..."}        — refuses the call
    {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}
- On any error / non-Bash tool, exit 0 silently to avoid blocking the pipeline.
"""

import json
import re
import sys


def is_unbounded_tail_f(cmd: str) -> bool:
    """tail -f / -F without --pid and without `timeout N` wrapper."""
    if not re.search(r"\btail\s+(?:-[a-zA-Z]*[fF]|--follow\b)", cmd):
        return False
    if re.search(r"\btail\s+[^|;&]*?--pid[ =]", cmd):
        return False
    # `timeout <n>` immediately preceding tail is acceptable
    if re.search(r"\btimeout\s+\d+\s+(?:[A-Za-z_][\w/.-]*\s+)?tail\s+(?:-[a-zA-Z]*[fF]|--follow\b)", cmd):
        return False
    return True


def rewrite_tail_f(cmd: str) -> str:
    """Inject `timeout 600` before any unsafe tail -f / -F invocation."""
    pattern = re.compile(r"(?<![\w.-])tail\s+(-[a-zA-Z]*[fF]|--follow\b)")

    def repl(m: re.Match) -> str:
        # Skip if this specific occurrence already has a timeout wrapper just before it
        start = m.start()
        prefix = cmd[max(0, start - 40):start]
        if re.search(r"\btimeout\s+\d+\s*(?:[A-Za-z_][\w/.-]*\s+)?$", prefix):
            return m.group(0)
        # Skip if this occurrence has --pid in its argument list (lookahead a bit)
        tail_args = cmd[m.end():m.end() + 200]
        if re.match(r"[^|;&\n]*--pid[ =]", tail_args):
            return m.group(0)
        return f"timeout 600 tail {m.group(1)}"

    return pattern.sub(repl, cmd)


def is_unbounded_grep_poll(cmd: str) -> bool:
    """`until ... grep -q ... ; do sleep N; done` without an outer wall-clock break."""
    if not re.search(r"\buntil\b[^\n]*\bgrep\s+-q\b[^\n]*\bdo\b[^\n]*\bsleep\b", cmd, re.DOTALL):
        return False
    # Heuristic: presence of a START/LIMIT wall-clock guard means it is bounded
    if re.search(r"\$\(\(\s*\$\(date\s+\+%s\)\s*-\s*\$?START", cmd):
        return False
    if re.search(r"\bbreak\b", cmd) and re.search(r"\bLIMIT\b", cmd):
        return False
    return True


def is_bare_wait(cmd: str) -> bool:
    """`wait` with no PID — blocks on every child, including stale watchers."""
    return bool(re.search(r"(?:^|;|&&|\|\|)\s*wait\s*(?:#|;|$)", cmd))


def emit_block(reason: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": reason,
    }))


def emit_modify(new_cmd: str, note: str) -> None:
    # PreToolUse can rewrite tool_input via hookSpecificOutput.modifiedToolInput
    # But Claude Code's stable contract supports decision="allow" with updated input
    # via "tool_input" at top level for matchers that allow it. For maximum
    # compatibility we instead emit decision="block" with a clear correction
    # message — Claude will retry with the suggested form. However, silently
    # rewriting is preferred for tail -f because the agent does not need to relearn.
    # Here we use the documented updateToolInput mechanism.
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        },
        "tool_input": {"command": new_cmd},
        "systemMessage": note,
    }))


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        info = json.loads(raw)
    except Exception:
        return 0

    if info.get("tool_name") != "Bash":
        return 0

    cmd = (info.get("tool_input") or {}).get("command", "")
    if not isinstance(cmd, str) or not cmd:
        return 0

    # Rule 2: unbounded grep polling — block, instruct
    if is_unbounded_grep_poll(cmd):
        emit_block(
            "Unbounded `until grep -q ... ; do sleep ...; done` detected. "
            "Wrap with a wall-clock break: "
            "`START=$(date +%s); LIMIT=14400; until [ -f log ] && grep -q DONE log; do "
            "[ $(($(date +%s)-START)) -gt $LIMIT ] && { echo TIMEOUT; break; }; sleep 30; done`"
        )
        return 0

    # Rule 3: bare wait — block
    if is_bare_wait(cmd):
        emit_block(
            "Bare `wait` detected. Use `wait \"$PID\"` with a specific PID "
            "(captured via `PID=$!` after launching the background job)."
        )
        return 0

    # Rule 1: unbounded tail -f — auto-rewrite to `timeout 600 tail -f`
    if is_unbounded_tail_f(cmd):
        new_cmd = rewrite_tail_f(cmd)
        if new_cmd != cmd:
            emit_modify(
                new_cmd,
                "[guard_bash] Wrapped unsafe `tail -f` with `timeout 600` to prevent "
                "unbounded watcher from pinning the Claude turn.",
            )
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
