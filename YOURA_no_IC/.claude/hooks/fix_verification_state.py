#!/usr/bin/env python3
"""Fix verification_state.yaml variants that block run_hypothesis_loop.py.

Phase 2B (Claude-generated) writes this file with a drifting schema. Observed
variants so far:
  - sub_hypotheses as a metadata block instead of an id -> entry dict
  - non-standard statuses (todo, PENDING) or missing status fields
  - gate info only in the top-level 'hypotheses' list, or as a plain string
  - 'dependencies' instead of 'prerequisites'
  - no hypothesis marked READY (loop cannot start)

Rebuilds sub_hypotheses into the schema the loop expects, preserving any
valid mid-run statuses, and promotes prerequisite-free hypotheses to READY
when the state is stuck. Writes a .bak of the original file.

Usage: python fix_verification_state.py [research_folder]
"""
import sys
import yaml
from pathlib import Path

# Statuses the hypothesis loop actually recognizes.
KNOWN_STATUSES = {
    "READY", "IN_PROGRESS", "NOT_STARTED",
    "COMPLETED", "VALIDATED", "FAILED", "BLOCKED",
}
ACTIVE = {"READY", "IN_PROGRESS"}
TERMINAL = {"COMPLETED", "VALIDATED", "FAILED", "BLOCKED"}

folder = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/youra_research")
path = folder / "verification_state.yaml"
orig_text = path.read_text(encoding="utf-8")
state = yaml.safe_load(orig_text)


def norm_id(x):
    return str(x).strip().lower()


def norm_prereqs(entry):
    raw = entry.get("prerequisites")
    if raw is None:
        raw = entry.get("dependencies")
    out = []
    for item in raw or []:
        if isinstance(item, dict):
            item = item.get("id") or item.get("hypothesis") or ""
        if item:
            out.append(norm_id(item))
    return out


def is_entry(v):
    return isinstance(v, dict) and ("gate" in v or "status" in v or "type" in v)


# ------------------------------------------------------------
# Collect entries: sub_hypotheses (may hold mid-run state) is the base,
# missing fields are filled from the top-level 'hypotheses' list.
# ------------------------------------------------------------
sh = state.get("sub_hypotheses")
from_list = {}
for h in state.get("hypotheses") or []:
    if isinstance(h, dict) and h.get("id"):
        from_list[norm_id(h["id"])] = dict(h)

entries = {}
if isinstance(sh, dict) and sh and all(is_entry(v) for v in sh.values()):
    for k, v in sh.items():
        k2 = norm_id(k)
        merged = dict(from_list.get(k2, {}))
        merged.update(v)  # sub_hypotheses values win (mid-run state)
        entries[k2] = merged
else:
    if sh is not None:
        state["sub_hypotheses_meta"] = sh
        state.pop("sub_hypotheses", None)
    entries = from_list

if not entries:
    print("ERROR: no hypothesis entries found to normalize")
    sys.exit(1)

# ------------------------------------------------------------
# Normalize each entry
# ------------------------------------------------------------
sub = {}
for h_id, h in entries.items():
    h = dict(h)
    h.pop("id", None)
    h["prerequisites"] = norm_prereqs(h)
    h.pop("dependencies", None)
    gate = h.get("gate")
    if isinstance(gate, str):
        h["gate"] = {"type": gate, "satisfied": None, "result": None}
    elif isinstance(gate, dict):
        h["gate"].setdefault("satisfied", None)
        h["gate"].setdefault("result", None)
    if h.get("status") not in KNOWN_STATUSES:
        h["status"] = "READY" if not h["prerequisites"] else "NOT_STARTED"
    h.setdefault("experiment_design", {"status": "NOT_STARTED", "file": None})
    h.setdefault("implementation_planning", {"status": "NOT_STARTED"})
    h.setdefault("validation", {"status": "NOT_STARTED", "result": None})
    h.setdefault("version", 1)
    h.setdefault("completed", False)
    sub[h_id] = h

# ------------------------------------------------------------
# Stuck-state promotion: nothing ACTIVE and nothing TERMINAL means the
# loop can never start — promote prerequisite-free NOT_STARTED entries.
# ------------------------------------------------------------
statuses = {v["status"] for v in sub.values()}
if not (statuses & ACTIVE) and not (statuses & TERMINAL):
    for v in sub.values():
        if v["status"] == "NOT_STARTED" and not v["prerequisites"]:
            v["status"] = "READY"

if state.get("sub_hypotheses") == sub:
    print("sub_hypotheses already in expected schema — nothing to do")
    sys.exit(0)

state["sub_hypotheses"] = sub
backup = path.with_suffix(".yaml.bak")
backup.write_text(orig_text, encoding="utf-8")
path.write_text(
    yaml.dump(state, default_flow_style=False, allow_unicode=True,
              sort_keys=False, width=120),
    encoding="utf-8",
)
ready = [k for k, v in sub.items() if v["status"] in ACTIVE]
print(f"Normalized {len(sub)} hypotheses: {', '.join(sub)}")
print(f"READY/IN_PROGRESS: {', '.join(ready) or 'none'} | backup: {backup}")
