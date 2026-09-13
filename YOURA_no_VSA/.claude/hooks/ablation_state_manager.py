#!/usr/bin/env python3
"""VSA-IC Ablation State Manager — "w/o VSA Persistence (State-in-Context)".

Implements the harness-mediated shadow-state relay from the WS4 ablation specification
(section 3) as approved in the ralplan consensus plan (plan_v2, Option C-revised).

Two representations of the same logical state:
  1. MODEL-VISIBLE state: injected as text into every phase prompt
     (## Current Pipeline State), restated by the model in a ```state fenced
     block. The model gets NO Read/Edit/Write access to the three target
     files in shadow mode.
  2. HARNESS shadow state: same schema, stored under
     {research_folder}/.ablation_shadow/. All harness Python control flow
     (topo-sort, gate routing, verification, timeout policy) reads/writes
     these shadow files — control-flow logic itself is unchanged.

Target files (the "VSA"):
  - verification_state.yaml
  - {h_id}/04_checkpoint.yaml
  - {h_id}/03_tasks.yaml

Invariants (spec section 1):
  - Serena Reflective Memory, Archon MCP, GPT-5.2 stop-hook controller,
    stage graph, and reflection routing logic are NOT touched.
  - Archon ID fields (metadata.*) are excluded from the model's restate
    schema and carried forward by the harness (spec R5).

Merge policy (plan v2 CR-2): the model's restate only overwrites
MODEL_FIELDS inside existing sub_hypotheses entries; everything else is
harness-authoritative. The top-level sub_hypotheses dict is NEVER replaced
(protects phase_output_verifier._check_verification_state_schema).

Truncation (spec section 3.4): injected state text is truncated for real —
K recent history events, non-active hypotheses summarized to one line,
total char cap — EXCEPT Phase 4.5 which needs full validation results for
all hypotheses (Prediction-Result Matrix).
"""

from __future__ import annotations

import copy
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

# Files whose storage medium moves from disk to context in shadow mode.
TARGET_BASENAMES = (
    "verification_state.yaml",
    "04_checkpoint.yaml",
    "03_tasks.yaml",
)

SHADOW_DIR_NAME = ".ablation_shadow"

# Marker placed on the first line inside the INJECTED state block so that
# parse_restate_block() never mistakes the prompt echo for a model restate.
INJECTED_MARKER = "# INJECTED STATE (do not copy this line into your restate)"

# Fixed reminder appended to every auto-responder resume prompt in shadow mode
# (the Stop-hook feedback channel bypasses the launcher prompt override, so it
# needs its own reinforcement — this is how the 2026-07-09 dl4c R8 violation
# got through).
ABLATION_REMINDER = (
    "\n\n[ABLATION MODE REMINDER: Do NOT Read/Edit/Write verification_state.yaml, "
    "04_checkpoint.yaml, or 03_tasks.yaml (any path). All pipeline state is "
    "provided in your prompt context; restate any state updates in a ```state "
    "fenced block instead of writing those files. A ```state block restatement "
    "COUNTS as the file having been generated/updated.]"
)

# Case-insensitive instruction rewrites shared by launcher prompts AND
# auto-responder resume prompts. Ordered: specific patterns before generic.
# These neutralize every known imperative that tells the model to touch a
# target file (launcher step lists, retry prompts, GPT-5.2 canned phrases).
STATE_INSTRUCTION_PATTERNS = [
    # run_phase4.py mock-fix prompt: "Read the checkpoint: /abs/path/04_checkpoint.yaml"
    (r"(?i)read the checkpoint: \S*04_checkpoint\.yaml",
     "Use the checkpoint state provided in the Current Pipeline State section"),
    # run_phase4.py mock-fix prompt: "Read verification_state.yaml: /abs/path"
    (r"(?i)read verification_state\.yaml: \S+",
     "Use the pipeline state provided in the Current Pipeline State section"),
    # run_phase45.py: "Read ALL h-*/04_validation.md and h-*/04_checkpoint.yaml files"
    (r"(?i)read all h-\*/04_validation\.md and h-\*/04_checkpoint\.yaml files",
     "Read ALL h-*/04_validation.md files (checkpoint state for all hypotheses "
     "is provided in the Current Pipeline State section)"),
    # run_phase45.py: "Read ALL h-*/03_tasks.yaml files (planned metrics, ...)"
    (r"(?i)read all h-\*/03_tasks\.yaml files",
     "Use the implementation_planning fields in the Current Pipeline State "
     "section and each h-*/02c_experiment_brief.md"),
    # run_phase6.py: "Also read: verification_state.yaml, 03_refinement.yaml, ..."
    (r"(?i)read: verification_state\.yaml,",
     "read: the Current Pipeline State section (in place of verification_state.yaml),"),
    # phase_output_verifier retry detail: "Re-generate verification_state.yaml ..."
    # `_Q` tolerates backtick/quote wrapping — the GPT-5.2 resume prompt that
    # caused the dl4c violation said: generate `verification_state.yaml`.
    (r"(?i)\bre-?generate [`\"']?verification_state\.yaml[`\"']?",
     "Restate the complete verification_state in the ```state fenced block"),
    # run_phase2b.py step list: "Finalize and generate verification_state.yaml"
    (r"(?i)\bgenerate [`\"']?verification_state\.yaml[`\"']?",
     "restate the complete verification_state in the ```state fenced block"),
    (r"(?i)\bcreate [`\"']?verification_state\.yaml[`\"']?",
     "restate the complete verification_state in the ```state fenced block"),
    (r"(?i)\bwrite [`\"']?verification_state\.yaml[`\"']?",
     "restate the verification_state in the ```state fenced block"),
    (r"(?i)\bupdate [`\"']?verification_state\.yaml[`\"']? with\b",
     "restate the updated state (```state block) with"),
    (r"(?i)\bupdate [`\"']?verification_state\.yaml[`\"']?",
     "restate the updated state in a ```state fenced block"),
    (r"(?i)\bread [`\"']?verification_state\.yaml[`\"']?",
     "use the pipeline state provided in the Current Pipeline State section"),
    (r"(?i)\bload [`\"']?verification_state\.yaml[`\"']?",
     "use the pipeline state provided in the Current Pipeline State section"),
    (r"(?i)\bfrom [`\"']?verification_state\.yaml[`\"']?",
     "from the Current Pipeline State section"),
    # run_phase3.py step list: "Generate 03_tasks.yaml with implementation tasks"
    (r"(?i)\b(?:generate|create|write) [`\"']?03_tasks\.yaml[`\"']?",
     "generate the implementation task list and restate it under the 'tasks' "
     "key of the ```state fenced block"),
    (r"(?i)\b(?:read|load) [`\"']?03_tasks\.yaml[`\"']? for\b",
     "use the tasks provided in the Current Pipeline State section for"),
    (r"(?i)\b(?:read|load) [`\"']?03_tasks\.yaml[`\"']?",
     "use the tasks provided in the Current Pipeline State section"),
    (r"(?i)\b(?:read|load) [`\"']?04_checkpoint\.yaml[`\"']?",
     "use the checkpoint state provided in the Current Pipeline State section"),
    (r"(?i)\b(?:update|write) [`\"']?04_checkpoint\.yaml[`\"']?",
     "restate the updated checkpoint in the ```state fenced block"),
]


def neutralize_state_instructions(text: str) -> str:
    """Rewrite any instruction that tells the model to access a target file.

    Module-level (no manager instance needed) so phase_auto_responder.py can
    sanitize GPT-5.2 resume prompts with the exact same rules the launcher
    prompts get.
    """
    if not text:
        return text
    for pattern, replacement in STATE_INSTRUCTION_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text

# ---------------------------------------------------------------
# Field-level merge policy (plan v2 CR-2, complete enumeration)
# ---------------------------------------------------------------
# Dotted paths WITHIN one sub_hypotheses entry that the model's restate is
# allowed to overwrite. Everything not listed here is harness-authoritative
# by default (left untouched), including: status, prerequisites, type,
# statement, gate.type, blocked_by, blocked_reason, awaiting, failed_by,
# and the superseded.* conflict zone (harness-authoritative by explicit
# decision — see plan v2 Step 0).
MODEL_FIELDS = [
    # Gate verdict (Phase 4 step-06)
    "gate.satisfied",
    "gate.result",
    "gate.failed_checks",
    # Validation (Phase 4 step-05c/06/07/08)
    "validation.status",
    "validation.result",
    "validation.file",
    "validation.key_findings",
    "validation.success_criteria_met",
    "validation.started_at",
    "validation.completed_at",
    # Experiment design (Phase 2C)
    "experiment_design.status",
    "experiment_design.file",
    "experiment_design.started_at",
    "experiment_design.completed_at",
    # Implementation planning (Phase 3)
    "implementation_planning.status",
    "implementation_planning.tasks_file",
    "implementation_planning.tier",
    "implementation_planning.budget",
    "implementation_planning.task_count",
    "implementation_planning.task_breakdown",
    "implementation_planning.archon_document_ids",
    "implementation_planning.files",
    "implementation_planning.started_at",
    "implementation_planning.completed_at",
    # Data setup (Phase 4 step-01a)
    "data_setup.status",
    "data_setup.dataset",
    "data_setup.model",
    "data_setup.completed_at",
    # Reflection (Phase 4 step-06b)
    "reflection_outcome",
    "reflection_type",
    "route_to",
    # Completion record-keeping (Phase 4 step-08)
    "completed",
    "completed_at",
    # Version tracking (SELF_MODIFY)
    "version",
    "modification_attempt",
    "version_history",
]

# Top-level sections that are ALWAYS harness-authoritative. Present here for
# documentation/audit; the merge algorithm only ever touches sub_hypotheses
# entries and per-hypothesis shadow checkpoints, so these are protected by
# construction.
HARNESS_TOP_LEVEL = [
    "pipeline", "metadata", "main_hypothesis", "episode", "workflow",
    "history", "statistics", "gate_violations", "modification_history",
    "serena_memory",
]

# Narrow top-level exceptions the model IS allowed to set via restate — these
# are model-written phase-completion markers checked by phase_output_verifier
# (e.g. Phase 4.5 requires workflow.synthesis_completed == true).
TOP_LEVEL_MODEL_FIELDS = [
    "workflow.synthesis_completed",
]


def _get_dotted(d: dict, dotted: str, sentinel=None):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return sentinel
        cur = cur[part]
    return cur


def _set_dotted(d: dict, dotted: str, value):
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        if not isinstance(cur.get(part), dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value


class AblationStateManager:
    """Central object for VSA-IC shadow-state relay.

    mode == "normal": every method is a transparent no-op / passthrough so
    the full-YouRA arm shares this code path with zero behavior change.
    mode == "shadow": the VSA-IC ablation arm.
    """

    def __init__(self, research_folder, mode: str = "normal", log_fn=None):
        self.research_folder = Path(research_folder).resolve()
        self.mode = mode if mode in ("normal", "shadow") else "normal"
        self.shadow_dir = self.research_folder / SHADOW_DIR_NAME
        self._log = log_fn or (lambda m: None)
        self.last_truncation_meta: dict = {}
        if self.is_shadow_mode():
            self.init_shadow()

    # ------------------------------------------------------------
    # Mode / paths
    # ------------------------------------------------------------
    def is_shadow_mode(self) -> bool:
        return self.mode == "shadow"

    def state_path(self, original_path) -> Path:
        """Resolve a target-file path: shadow location in shadow mode.

        Non-target files and normal mode pass through unchanged. The shadow
        layout mirrors the research folder: .ablation_shadow/<relpath>.
        """
        p = Path(original_path)
        if not self.is_shadow_mode() or p.name not in TARGET_BASENAMES:
            return p
        try:
            rel = p.resolve().relative_to(self.research_folder)
        except ValueError:
            # Path outside the research folder (e.g. _archive fallback):
            # leave untouched.
            return p
        # Never re-shadow a path already inside the shadow dir.
        if rel.parts and rel.parts[0] == SHADOW_DIR_NAME:
            return p
        shadow = self.shadow_dir / rel
        shadow.parent.mkdir(parents=True, exist_ok=True)
        return shadow

    def init_shadow(self):
        """Seed the shadow dir from any pre-existing real target files.

        Used when the ablation run starts from a folder that already has
        Phase-2B-era files (e.g. resume). Never overwrites newer shadow
        copies.
        """
        self.shadow_dir.mkdir(parents=True, exist_ok=True)
        candidates = [self.research_folder / "verification_state.yaml"]
        for h_dir in sorted(self.research_folder.glob("h-*")):
            if h_dir.is_dir():
                candidates.append(h_dir / "04_checkpoint.yaml")
                candidates.append(h_dir / "03_tasks.yaml")
        for real in candidates:
            if not real.exists():
                continue
            shadow = self.shadow_dir / real.relative_to(self.research_folder)
            if shadow.exists():
                continue
            shadow.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(real, shadow)
            self._log(f"[ablation] seeded shadow copy: {shadow.relative_to(self.research_folder)}")

    # ------------------------------------------------------------
    # Shadow YAML I/O helpers
    # ------------------------------------------------------------
    def _shadow_vs_path(self) -> Path:
        return self.state_path(self.research_folder / "verification_state.yaml")

    def load_shadow_state(self) -> dict:
        p = self._shadow_vs_path()
        if not yaml or not p.exists():
            return {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self._log(f"[ablation] WARNING: failed to load shadow state: {e}")
            return {}

    def save_shadow_state(self, state: dict):
        p = self._shadow_vs_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            yaml.dump(state, f, default_flow_style=False, allow_unicode=True,
                      sort_keys=False, width=120)

    def load_shadow_checkpoint(self, hypothesis_id: str) -> dict:
        p = self.state_path(self.research_folder / hypothesis_id / "04_checkpoint.yaml")
        if not yaml or not p.exists():
            return {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self._log(f"[ablation] WARNING: failed to load shadow checkpoint: {e}")
            return {}

    def save_shadow_checkpoint(self, hypothesis_id: str, checkpoint: dict):
        p = self.state_path(self.research_folder / hypothesis_id / "04_checkpoint.yaml")
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            yaml.dump(checkpoint, f, default_flow_style=False, allow_unicode=True)

    def load_shadow_tasks(self, hypothesis_id: str) -> dict:
        p = self.state_path(self.research_folder / hypothesis_id / "03_tasks.yaml")
        if not yaml or not p.exists():
            return {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    # ------------------------------------------------------------
    # Prompt-side: override block + truncated state text
    # ------------------------------------------------------------
    def build_override_block(self) -> str:
        """The State Access Override prepended to EVERY shadow-mode prompt
        (main sessions AND sub-sessions — plan v2 follow-up SC-1)."""
        return """## STATE ACCESS OVERRIDE (ABLATION MODE)

CRITICAL INSTRUCTION — SUPERSEDES ALL STEP FILE INSTRUCTIONS:
- Do NOT use Read, Edit, or Write tools (or Bash cat/sed/etc.) on these files:
  - verification_state.yaml
  - 04_checkpoint.yaml
  - 03_tasks.yaml
- All pipeline state is provided in the "Current Pipeline State" section below.
- When step files instruct you to "Read verification_state.yaml" or
  "Read checkpoint from file", use the state provided below instead.
- When step files instruct you to "Update verification_state.yaml" or
  "Write/Update checkpoint", instead RESTATE the updated state in a
  ```state fenced block at the end of your work, in this exact shape:

  ```state
  sub_hypotheses:
    <hypothesis-id>:
      <only the fields you changed: gate, validation, experiment_design,
       implementation_planning, data_setup, reflection_outcome, route_to,
       completed, completed_at, version fields>
  checkpoint:
    <the full updated 04_checkpoint.yaml content for the current hypothesis>
  ```

- Do NOT include metadata, history, statistics, workflow, or Archon ID
  fields in the restate block — the harness carries those forward.
- Restate the state block again whenever you make further updates; the LAST
  block in your output is authoritative.
- This override applies to ALL steps in this session."""

    # Launcher-prompt instruction rewrites (these strings appear in the
    # build_phaseN_prompt() text itself, not in step files).
    PROMPT_REPLACEMENTS = [
        ("Load 03_tasks.yaml for",
         "Use the tasks provided in the Current Pipeline State section for"),
        ("Load hypothesis {h} from verification_state.yaml",
         None),  # handled generically below
        ("Update verification_state.yaml with",
         "Restate the updated state (```state block) with"),
        ("Update verification_state.yaml",
         "Restate the updated state in a ```state fenced block"),
        ("Read verification_state.yaml",
         "Use the pipeline state provided in the Current Pipeline State section"),
        ("Load hypothesis", "Use hypothesis"),  # "Load hypothesis h-e1 from ..."
        ("from verification_state.yaml",
         "from the Current Pipeline State section"),
        ("Read 04_checkpoint.yaml",
         "Use the checkpoint state provided in the Current Pipeline State section"),
        ("Update 04_checkpoint.yaml",
         "Restate the updated checkpoint in the ```state fenced block"),
    ]

    def apply_prompt_replacements(self, prompt: str) -> str:
        """Neutralize file-access instructions inside a launcher prompt."""
        if not self.is_shadow_mode():
            return prompt
        for old, new in self.PROMPT_REPLACEMENTS:
            if new is None:
                continue
            prompt = prompt.replace(old, new)
        # Case-insensitive regex pass (catches "generate/create/finalize ..."
        # phrasings the literal list above misses — see 2026-07-09 dl4c R8
        # violation, run_phase2b.py "Step 10: Finalize and generate
        # verification_state.yaml").
        return neutralize_state_instructions(prompt)

    def build_state_text(self, hypothesis_id: Optional[str] = None,
                         phase: Optional[str] = None,
                         include_checkpoint: bool = False,
                         include_tasks: bool = False,
                         history_k: int = 5,
                         char_cap: int = 4000) -> Tuple[str, dict]:
        """Render the truncated model-visible state text.

        PRIORITY-ORDERED truncation (spec 3.4 "truncate oldest/least-relevant
        first" — never amputate the operationally-required core): the active
        hypothesis entry, its checkpoint, and its task list are assembled
        FIRST and protected; global/summary/history content is dropped first
        when over budget. Real pipeline states are 30KB+, so truncation still
        fires hard — but as memory loss, not harness breakage.

        Per-phase policy: phase45 keeps FULL validation results for ALL
        hypotheses (Prediction-Result Matrix) with a larger cap; phase4 gets
        a larger cap because checkpoint+tasks must ride along.
        Returns (text, truncation_metadata).
        """
        state = copy.deepcopy(self.load_shadow_state())
        meta = {"events_kept": 0, "events_dropped": 0,
                "chars_injected": 0, "chars_truncated": 0,
                "hypotheses_summarized": 0, "sections_dropped": []}

        if phase == "phase45":
            char_cap = max(char_cap, 16000)
        elif include_checkpoint or include_tasks:
            # Phase 4: checkpoint + tasks must fit alongside the state view.
            char_cap = max(char_cap, 12000)

        # --- truncate history-like arrays -------------------------------
        def _trim_list(container: dict, key: str):
            arr = container.get(key)
            if isinstance(arr, list) and len(arr) > history_k:
                dropped = len(arr) - history_k
                container[key] = (
                    [f"...({dropped} earlier events omitted)..."] + arr[-history_k:]
                )
                meta["events_dropped"] += dropped
                meta["events_kept"] += history_k
            elif isinstance(arr, list):
                meta["events_kept"] += len(arr)

        _trim_list(state, "history")
        wf = state.get("workflow")
        if isinstance(wf, dict):
            _trim_list(wf, "status_history")

        # R5: Archon IDs are shown READ-ONLY for MCP calls but excluded from
        # the restate contract; the rest of metadata is dropped to avoid
        # hallucinated UUID round-trips.
        md = state.pop("metadata", None) or {}
        archon_ref = ""
        if isinstance(md, dict):
            ref_lines = []
            if md.get("pipeline_project_id"):
                ref_lines.append(f"#   pipeline_project_id: {md['pipeline_project_id']}")
            htm = md.get("hypothesis_task_mapping") or {}
            if isinstance(htm, dict) and hypothesis_id and htm.get(hypothesis_id):
                ref_lines.append(f"#   hypothesis_task_mapping.{hypothesis_id}: {htm[hypothesis_id]}")
            if ref_lines:
                archon_ref = ("# --- Archon reference (READ-ONLY — never include in restate;\n"
                              "#     the harness carries these forward) ---\n"
                              + "\n".join(ref_lines))
        for key in ("serena_memory", "gate_violations", "modification_history"):
            state.pop(key, None)

        # --- per-hypothesis truncation -----------------------------------
        active_entries: dict = {}
        sub = state.get("sub_hypotheses")
        if isinstance(sub, dict):
            active = hypothesis_id
            prereqs = set()
            if active and isinstance(sub.get(active), dict):
                prereqs = set(sub[active].get("prerequisites") or [])
            for h_id, h_data in list(sub.items()):
                if not isinstance(h_data, dict):
                    continue
                _trim_list(h_data, "version_history")
                if phase == "phase45":
                    ip = h_data.get("implementation_planning")
                    if isinstance(ip, dict):
                        ip.pop("task_breakdown", None)
                        ip.pop("archon_document_ids", None)
                    continue
                if h_id == active or h_id in prereqs:
                    # Pulled out into the PROTECTED core section below.
                    active_entries[h_id] = sub.pop(h_id)
                    continue
                gate = h_data.get("gate") or {}
                if not isinstance(gate, dict):
                    gate = {"type": str(gate)}
                sub[h_id] = {
                    "status": h_data.get("status"),
                    "gate": {"type": gate.get("type"),
                             "satisfied": gate.get("satisfied")},
                }
                meta["hypotheses_summarized"] += 1

        def _dump(obj) -> str:
            return yaml.dump(obj, default_flow_style=False, allow_unicode=True,
                             sort_keys=False, width=120)

        def _compact_checkpoint(cp: dict) -> dict:
            """Drop bulky per-task prose the model can re-derive from tasks."""
            cp = copy.deepcopy(cp)
            _trim_list(cp, "task_history")
            _trim_list(cp, "history")
            items = ((cp.get("tasks") or {}).get("items")
                     if isinstance(cp.get("tasks"), dict) else None)
            if isinstance(items, list) and len(_dump(items)) > 3000:
                slim = []
                for it in items:
                    if isinstance(it, dict):
                        slim.append({k: it.get(k) for k in
                                     ("id", "title", "status", "priority",
                                      "epic", "retry_count") if k in it})
                    else:
                        slim.append(it)
                cp["tasks"]["items"] = slim
                cp["tasks"]["_note"] = "descriptions elided; see 03_tasks section"
            return cp

        def _compact_tasks(tasks: dict) -> dict:
            tasks = copy.deepcopy(tasks)
            tl = tasks.get("tasks")
            if isinstance(tl, list) and len(_dump(tl)) > 2500:
                slim = []
                for it in tl:
                    if isinstance(it, dict):
                        slim.append({k: it.get(k) for k in
                                     ("id", "title", "status", "priority",
                                      "reference_files") if k in it})
                    else:
                        slim.append(it)
                tasks["tasks"] = slim
                tasks["_note"] = "task descriptions elided for context budget"
            return tasks

        # --- priority-ordered assembly (core first, drop tail-priority) ---
        # (priority, name, text, protected)
        parts = []
        if active_entries:
            parts.append((1, "active_hypotheses",
                          "# ACTIVE hypothesis (+ direct prerequisites)\n"
                          + _dump({"sub_hypotheses": active_entries}), True))
        if include_checkpoint and hypothesis_id:
            cp = self.load_shadow_checkpoint(hypothesis_id)
            if cp:
                parts.append((2, "checkpoint",
                              f"# 04_checkpoint ({hypothesis_id})\n"
                              + _dump(_compact_checkpoint(cp)), True))
        if include_tasks and hypothesis_id:
            tasks = self.load_shadow_tasks(hypothesis_id)
            if tasks:
                parts.append((3, "tasks",
                              f"# 03_tasks ({hypothesis_id})\n"
                              + _dump(_compact_tasks(tasks)), True))
        parts.append((4, "pipeline_state",
                      "# verification_state (truncated view)\n" + _dump(state),
                      False))

        budget = char_cap
        chosen = []
        for prio, name, text, protected in sorted(parts, key=lambda p: p[0]):
            if len(text) <= budget:
                chosen.append(text)
                budget -= len(text)
            elif protected and budget > 400:
                # Core section over budget: keep the head, mark the cut.
                cut = len(text) - budget
                chosen.append(text[:budget]
                              + f"\n# [TRUNCATED core section '{name}': {cut} chars cut]")
                meta["chars_truncated"] += cut
                self._log(f"[ablation] WARNING: core section '{name}' exceeded "
                          f"budget — {cut} chars cut (consider raising char_cap)")
                budget = 0
            else:
                meta["sections_dropped"].append(name)
                meta["chars_truncated"] += len(text)

        if meta["sections_dropped"]:
            chosen.append("# [DROPPED sections (budget): "
                          + ", ".join(meta["sections_dropped"]) + "]")

        body = "\n".join(chosen)
        if archon_ref:
            body = body + "\n" + archon_ref  # cap-exempt, tiny
        meta["chars_injected"] = len(body)
        self.last_truncation_meta = meta
        self._log(f"[ablation] state text: {meta['chars_injected']} chars injected, "
                  f"{meta['chars_truncated']} truncated, "
                  f"{meta['events_dropped']} events dropped, "
                  f"{meta['hypotheses_summarized']} hypotheses summarized, "
                  f"dropped_sections={meta['sections_dropped']}")

        text = (f"## Current Pipeline State\n"
                f"(truncated: last {history_k} events kept; "
                f"non-active hypotheses summarized)\n\n"
                f"```state\n{INJECTED_MARKER}\n{body}\n```")
        return text, meta

    def build_prompt_blocks(self, hypothesis_id: Optional[str] = None,
                            phase: Optional[str] = None,
                            include_checkpoint: bool = False,
                            include_tasks: bool = False) -> str:
        """Override block + state text, ready to prepend to any prompt."""
        if not self.is_shadow_mode():
            return ""
        state_text, _ = self.build_state_text(
            hypothesis_id=hypothesis_id, phase=phase,
            include_checkpoint=include_checkpoint, include_tasks=include_tasks)
        return f"{self.build_override_block()}\n\n{state_text}\n\n"

    # ------------------------------------------------------------
    # Response-side: parse + merge
    # ------------------------------------------------------------
    @staticmethod
    def _extract_stream_text(transcript: str) -> str:
        """If the transcript is Claude CLI stream-json (JSONL events), pull
        out all assistant text content so restate blocks emitted in ANY turn
        of a multi-turn (auto-responder-driven) session are visible — not
        just the final message. Non-stream transcripts pass through as-is."""
        stripped = transcript.lstrip()
        if not stripped.startswith("{"):
            return transcript
        import json as _json
        texts = []
        saw_stream = False
        for line in transcript.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                evt = _json.loads(line)
            except ValueError:
                continue
            if not isinstance(evt, dict):
                continue
            saw_stream = True
            msg = evt.get("message") if isinstance(evt.get("message"), dict) else evt
            content = msg.get("content")
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text") or "")
            elif isinstance(evt.get("result"), str):
                texts.append(evt["result"])
        return "\n".join(texts) if saw_stream else transcript

    def parse_restate_block(self, transcript: str) -> Optional[dict]:
        """Extract the LAST model-authored ```state block from a transcript.

        - Handles both plain-text and stream-json transcripts.
        - The closing fence must sit at column 0 (valid restate YAML can only
          contain ``` inside indented block scalars), so fenced snippets
          inside key_findings/descriptions don't terminate the block early.
        - Blocks whose first line carries INJECTED_MARKER (prompt echo) are
          ignored.
        """
        if not transcript or not yaml:
            return None
        text = self._extract_stream_text(transcript)
        blocks = re.findall(r"```state[ \t]*\n(.*?)\n```[ \t]*$",
                            text, re.DOTALL | re.MULTILINE)
        for raw in reversed(blocks):
            first_line = raw.lstrip().splitlines()[0] if raw.strip() else ""
            if "INJECTED STATE" in first_line:
                continue
            try:
                data = yaml.safe_load(raw)
            except yaml.YAMLError:
                continue
            if isinstance(data, dict) and data:
                return data
        return None

    # Statuses run_hypothesis_loop.py understands (queueing, propagation,
    # terminal detection). Anything else in an initial restate would leave the
    # queue empty ("No READY or IN_PROGRESS hypotheses") — 2026-07-09 dl4c run.
    _KNOWN_STATUSES = {
        "NOT_STARTED", "READY", "IN_PROGRESS", "BLOCKED", "FAILED",
        "VALIDATED", "COMPLETED", "SUPERSEDED", "LIMITATION_RECORDED",
    }

    def _normalize_initial_state(self, state: dict) -> dict:
        """Make a Phase 2B initial restate queueable by run_hypothesis_loop.

        The model restates free-form; the loop needs per-entry `status`
        (READY to queue) and `prerequisites`. Missing/unknown statuses are
        derived from prerequisites exactly the way the loop's own
        propagate_dependencies() expects: prereq-free → READY, else
        NOT_STARTED (flipped to READY once prereqs validate).
        """
        sub = state.get("sub_hypotheses")
        if not isinstance(sub, dict):
            return state
        for h_id, h_data in sub.items():
            if not isinstance(h_data, dict):
                continue
            prereqs = h_data.get("prerequisites")
            if not isinstance(prereqs, list):
                # Accept common variants the model may emit instead.
                alt = (h_data.get("depends_on") or h_data.get("dependencies")
                       or h_data.get("prereqs"))
                prereqs = alt if isinstance(alt, list) else []
                h_data["prerequisites"] = prereqs
            status = h_data.get("status")
            canon = status.upper().replace(" ", "_") if isinstance(status, str) else ""
            if canon in self._KNOWN_STATUSES:
                h_data["status"] = canon
            else:
                h_data["status"] = "READY" if not prereqs else "NOT_STARTED"
                self._log(f"[ablation] normalized initial status for {h_id}: "
                          f"{status!r} → {h_data['status']}")
        return state

    def merge_restate_to_shadow(self, restated: dict,
                                hypothesis_id: Optional[str] = None) -> bool:
        """Merge a parsed restate block into the shadow copies.

        - restated["sub_hypotheses"]: field-policy merge into shadow
          verification_state (MODEL_FIELDS only; new entries adopted whole
          — matches the normal arm where the model creates new version
          entries directly).
        - restated["checkpoint"]: model-authoritative wholesale replace of
          the shadow 04_checkpoint.yaml for hypothesis_id (the checkpoint
          is model-owned in the original design).
        - Initial-creation special case (Phase 2B): if the shadow
          verification_state does not exist yet, adopt the restated state
          wholesale (metadata included — it originates from the model's own
          Archon calls at creation time).
        Returns True if anything was persisted.
        """
        if not self.is_shadow_mode() or not isinstance(restated, dict):
            return False
        merged_something = False

        vs_exists = self._shadow_vs_path().exists()
        restated_sub = restated.get("sub_hypotheses")

        # Normalize the known 'hypotheses:' LIST schema variant (Phase 2B
        # sometimes emits it; the normal arm tolerates it via
        # run_hypothesis_loop._normalize_hypotheses_schema).
        if not isinstance(restated_sub, dict) or not restated_sub:
            hyps = restated.get("hypotheses")
            if isinstance(hyps, list) and hyps:
                converted = {}
                for h in hyps:
                    if isinstance(h, dict) and h.get("id"):
                        entry = {k: v for k, v in h.items() if k != "id"}
                        converted[h["id"]] = entry
                if converted:
                    restated_sub = converted
                    restated = dict(restated)
                    restated["sub_hypotheses"] = converted
                    restated.pop("hypotheses", None)
                    self._log(f"[ablation] normalized 'hypotheses' list restate "
                              f"→ sub_hypotheses dict ({len(converted)} entries)")

        # Phase 2B initial creation: adopt wholesale.
        if not vs_exists and isinstance(restated_sub, dict) and restated_sub:
            initial = {k: v for k, v in restated.items() if k != "checkpoint"}
            self._normalize_initial_state(initial)
            md_init = initial.setdefault("metadata", {})
            if isinstance(md_init, dict):
                md_init["ablation_last_merge_at"] = datetime.now().isoformat()
            self.save_shadow_state(initial)
            self._log(f"[ablation] initial shadow state adopted "
                      f"({len(restated_sub)} sub_hypotheses)")
            merged_something = True
        else:
            shadow = self.load_shadow_state()
            state_dirty = False
            if isinstance(restated_sub, dict) and restated_sub:
                shadow_sub = shadow.setdefault("sub_hypotheses", {})
                if not isinstance(shadow_sub, dict):
                    self._log("[ablation] WARNING: shadow sub_hypotheses is not a dict — refusing merge")
                else:
                    for h_id, h_data in restated_sub.items():
                        if not isinstance(h_data, dict):
                            continue
                        if h_id not in shadow_sub:
                            # New hypothesis version (SELF_MODIFY): adopt whole,
                            # as the model would have written it in the normal arm.
                            shadow_sub[h_id] = h_data
                            self._log(f"[ablation] adopted NEW sub_hypothesis entry: {h_id}")
                            state_dirty = True
                            continue
                        existing = shadow_sub[h_id]
                        if not isinstance(existing, dict):
                            continue
                        _SENTINEL = object()
                        for field in MODEL_FIELDS:
                            val = _get_dotted(h_data, field, _SENTINEL)
                            if val is _SENTINEL:
                                continue
                            if field == "version_history":
                                # Append-only: the injected view truncates this
                                # list, so a wholesale replace would erase real
                                # history with the truncated echo. Drop the
                                # "...omitted..." placeholder strings and append
                                # only genuinely new entries.
                                if not isinstance(val, list):
                                    continue
                                old = existing.get("version_history")
                                old = old if isinstance(old, list) else []
                                incoming = [e for e in val
                                            if not (isinstance(e, str)
                                                    and "omitted" in e)]
                                merged_list = old + [e for e in incoming
                                                     if e not in old]
                                existing["version_history"] = merged_list
                                state_dirty = True
                                continue
                            _set_dotted(existing, field, val)
                            state_dirty = True
            # Narrow top-level exceptions (phase-completion markers) — merged
            # even when the restate carries no sub_hypotheses (e.g. Phase 4.5).
            _SENT = object()
            for field in TOP_LEVEL_MODEL_FIELDS:
                val = _get_dotted(restated, field, _SENT)
                if val is not _SENT:
                    _set_dotted(shadow, field, val)
                    state_dirty = True
            if state_dirty:
                ts_field = shadow.setdefault("metadata", {})
                if isinstance(ts_field, dict):
                    ts_field["last_updated"] = datetime.now().isoformat()
                    # R2 freshness signal: merge-specific stamp (last_updated is
                    # re-stamped by the harness constantly, so it can't serve).
                    ts_field["ablation_last_merge_at"] = datetime.now().isoformat()
                self.save_shadow_state(shadow)
                merged_something = True
                self._log("[ablation] merged restate into shadow state "
                          f"({list(restated_sub.keys()) if isinstance(restated_sub, dict) else 'top-level only'})")

        cp = restated.get("checkpoint")
        if isinstance(cp, dict) and cp and hypothesis_id:
            self.save_shadow_checkpoint(hypothesis_id, cp)
            self._log(f"[ablation] shadow checkpoint replaced for {hypothesis_id}")
            merged_something = True

        # 03_tasks restate (Phase 3 emits the generated task list).
        tasks = restated.get("tasks") or restated.get("03_tasks")
        if isinstance(tasks, dict) and tasks and hypothesis_id:
            p = self.state_path(self.research_folder / hypothesis_id / "03_tasks.yaml")
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                yaml.dump(tasks, f, default_flow_style=False, allow_unicode=True)
            self._log(f"[ablation] shadow 03_tasks written for {hypothesis_id}")
            merged_something = True

        return merged_something

    def merge_from_transcript(self, log_path,
                              hypothesis_id: Optional[str] = None) -> bool:
        """Convenience: read a session output log, parse, merge. False if no
        model restate block was found or nothing merged."""
        p = Path(log_path)
        if not self.is_shadow_mode() or not p.exists():
            return False
        try:
            transcript = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self._log(f"[ablation] WARNING: cannot read transcript {p}: {e}")
            return False
        restated = self.parse_restate_block(transcript)
        if restated is None:
            return False
        return self.merge_restate_to_shadow(restated, hypothesis_id=hypothesis_id)


# ---------------------------------------------------------------
# Shared launcher helpers (used by every run_phaseN.py)
# ---------------------------------------------------------------
def install_for_launcher(research_folder, state_mode: str, phase: str, log_fn):
    """One-call shadow-mode setup for a run_phaseN launcher.

    Installs the manager into phase_output_verifier and timeout_policy so all
    harness-side checks resolve to shadow paths. Returns the manager, or None
    in normal mode (all shadow helpers below then pass through).
    """
    if state_mode != "shadow":
        return None
    import phase_output_verifier as _pov
    import timeout_policy as _tp
    mgr = AblationStateManager(research_folder, mode="shadow", log_fn=log_fn)
    _pov.set_state_manager(mgr)
    _tp.set_state_manager(mgr)
    log_fn(f"VSA-IC ABLATION MODE ({phase}): state relayed via {mgr.shadow_dir}")
    return mgr


def shadow_wrap(mgr, prompt: str, hypothesis_id: Optional[str] = None,
                phase: Optional[str] = None,
                include_checkpoint: bool = False,
                include_tasks: bool = False) -> str:
    """Prepend override + fresh state text and neutralize file-access
    instructions. Passthrough when mgr is None (normal mode)."""
    if mgr is None or not mgr.is_shadow_mode():
        return prompt
    blocks = mgr.build_prompt_blocks(hypothesis_id, phase=phase,
                                     include_checkpoint=include_checkpoint,
                                     include_tasks=include_tasks)
    return blocks + mgr.apply_prompt_replacements(prompt)


def shadow_merge(mgr, log_path, hypothesis_id: Optional[str] = None,
                 log_fn=None) -> bool:
    """Merge the session transcript's restate block into shadow copies.
    Passthrough-True when mgr is None (normal mode)."""
    if mgr is None or not mgr.is_shadow_mode():
        return True
    merged = mgr.merge_from_transcript(log_path, hypothesis_id=hypothesis_id)
    if log_fn:
        name = Path(log_path).name
        log_fn(f"[ablation] shadow merge {'OK' if merged else 'MISSING restate block'} from {name}")
    return merged
