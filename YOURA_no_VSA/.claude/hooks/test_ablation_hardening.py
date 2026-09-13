#!/usr/bin/env python3
"""Tests for the 2026-07-09 VSA-IC clean-disable hardening.

Covers the five holes found in the dl4c R8-FAIL run:
  1. launcher prompt phrases the replacement table missed
     ("Finalize and generate verification_state.yaml" etc.)
  2. auto-responder resume prompts leaking file instructions
  3. no tool-level enforcement (guard_state_files.py / guard_bash.py rule 0)
  4. audit false positives on content-only mentions
  5. initial restate statuses the hypothesis loop cannot queue
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ablation_state_manager import (
    AblationStateManager,
    ABLATION_REMINDER,
    neutralize_state_instructions,
)
import ablation_audit

HOOKS_DIR = Path(__file__).parent
PYTHON = sys.executable


class TestNeutralizeStateInstructions(unittest.TestCase):
    """The exact strings that leaked in the dl4c run must be rewritten."""

    def test_phase2b_step10_line(self):
        s = "- Step 10: Finalize and generate verification_state.yaml"
        out = neutralize_state_instructions(s)
        self.assertNotIn("generate verification_state.yaml", out)
        self.assertIn("```state", out)

    def test_auto_responder_phrase(self):
        # The verbatim GPT-5.2 resume prompt that caused the dl4c violation —
        # note the backtick-wrapped filename.
        s = ("Continue the current step. Finish creating the final completeness "
             "checklist document, then proceed to Step 10 (Finalize): generate "
             "`verification_state.yaml` and write `02b_verification_plan.md`")
        out = neutralize_state_instructions(s)
        self.assertNotIn("generate `verification_state.yaml`", out)
        self.assertIn("```state", out)
        self.assertIn("02b_verification_plan.md", out)  # non-target untouched

    def test_phase3_generate_tasks(self):
        s = "- Generate 03_tasks.yaml with implementation tasks"
        out = neutralize_state_instructions(s)
        self.assertNotIn("Generate 03_tasks.yaml", out)
        self.assertIn("'tasks' key", out)

    def test_phase45_read_all_lines(self):
        s = ("- Read ALL h-*/04_validation.md and h-*/04_checkpoint.yaml files\n"
             "- Read ALL h-*/03_tasks.yaml files (planned metrics)")
        out = neutralize_state_instructions(s)
        self.assertNotIn("04_checkpoint.yaml files", out)
        self.assertNotIn("03_tasks.yaml files", out)
        self.assertIn("04_validation.md", out)

    def test_phase6_also_read(self):
        s = "  - Also read: verification_state.yaml, 03_refinement.yaml"
        out = neutralize_state_instructions(s)
        self.assertNotIn("read: verification_state.yaml", out)
        self.assertIn("03_refinement.yaml", out)

    def test_lowercase_update(self):
        s = "065_changelog.md, update verification_state.yaml"
        out = neutralize_state_instructions(s)
        self.assertNotIn("update verification_state.yaml", out)

    def test_mock_fix_path_lines(self):
        s = ("1. Read the checkpoint: /abs/x/h-e1/04_checkpoint.yaml\n"
             "2. Read verification_state.yaml: /abs/x/verification_state.yaml")
        out = neutralize_state_instructions(s)
        self.assertNotIn("/abs/x/h-e1/04_checkpoint.yaml", out)
        self.assertNotIn("Read verification_state.yaml:", out)

    def test_regenerate_retry_detail(self):
        s = "Re-generate verification_state.yaml using step-10-finalize template."
        out = neutralize_state_instructions(s)
        self.assertNotIn("Re-generate verification_state.yaml", out)

    def test_launcher_wrap_applies_regex_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = AblationStateManager(tmp, mode="shadow")
            out = mgr.apply_prompt_replacements(
                "- Step 10: Finalize and generate verification_state.yaml")
            self.assertNotIn("generate verification_state.yaml", out)


class TestInitialStateNormalization(unittest.TestCase):
    def _adopt(self, restate):
        tmp = tempfile.mkdtemp()
        mgr = AblationStateManager(tmp, mode="shadow")
        self.assertTrue(mgr.merge_restate_to_shadow(restate))
        return mgr.load_shadow_state()

    def test_missing_status_prereq_free_becomes_ready(self):
        state = self._adopt({"sub_hypotheses": {
            "SH1": {"title": "x"},
            "SH2": {"title": "y"},
        }})
        self.assertEqual(state["sub_hypotheses"]["SH1"]["status"], "READY")
        self.assertEqual(state["sub_hypotheses"]["SH1"]["prerequisites"], [])

    def test_depends_on_variant_becomes_not_started(self):
        state = self._adopt({"sub_hypotheses": {
            "SH1": {"title": "x"},
            "SH3": {"title": "z", "depends_on": ["SH1"]},
        }})
        self.assertEqual(state["sub_hypotheses"]["SH3"]["status"], "NOT_STARTED")
        self.assertEqual(state["sub_hypotheses"]["SH3"]["prerequisites"], ["SH1"])

    def test_unknown_status_replaced_known_kept(self):
        state = self._adopt({"sub_hypotheses": {
            "SH1": {"status": "PLANNING_COMPLETE"},
            "SH2": {"status": "ready", "prerequisites": []},
            "SH3": {"status": "BLOCKED", "prerequisites": ["SH1"]},
        }})
        self.assertEqual(state["sub_hypotheses"]["SH1"]["status"], "READY")
        self.assertEqual(state["sub_hypotheses"]["SH2"]["status"], "READY")
        self.assertEqual(state["sub_hypotheses"]["SH3"]["status"], "BLOCKED")


class TestAuditPrecision(unittest.TestCase):
    def _audit(self, events):
        tmp = Path(tempfile.mkdtemp())
        log = tmp / "phase2b_claude_output.log"
        lines = []
        for name, tool_input in events:
            lines.append(json.dumps({
                "type": "assistant",
                "message": {"role": "assistant", "content": [
                    {"type": "tool_use", "name": name, "input": tool_input}]},
            }))
        log.write_text("\n".join(lines), encoding="utf-8")
        return ablation_audit.audit_clean_disable(tmp)

    def test_content_mention_is_not_violation(self):
        passed, violations, warnings = self._audit([
            ("Write", {"file_path": "/x/phase2b_timeline_gantt.yaml",
                       "content": "task: update verification_state.yaml later"}),
        ])
        self.assertTrue(passed)
        self.assertEqual(violations, [])

    def test_target_file_path_is_violation(self):
        passed, violations, _ = self._audit([
            ("Write", {"file_path": "/x/verification_state.yaml",
                       "content": "anything"}),
        ])
        self.assertFalse(passed)
        self.assertEqual(len(violations), 1)

    def test_shadow_dir_access_is_violation(self):
        passed, violations, _ = self._audit([
            ("Read", {"file_path": "/x/.ablation_shadow/verification_state.yaml"}),
        ])
        self.assertFalse(passed)

    def test_bash_mention_is_warning_only(self):
        passed, violations, warnings = self._audit([
            ("Bash", {"command": "wc -l verification_state.yaml"}),
        ])
        self.assertTrue(passed)
        self.assertEqual(len(warnings), 1)

    def test_template_read_is_clean(self):
        passed, violations, _ = self._audit([
            ("Read", {"file_path": "/x/workflows/verification_state_template.yaml"}),
        ])
        self.assertTrue(passed)


class TestResponderShadowSupport(unittest.TestCase):
    def test_sanitize_resume(self):
        import phase_auto_responder as par
        out = par._shadow_sanitize_resume(
            "Continue to Step 10. Generate verification_state.yaml and finalize.")
        self.assertNotIn("Generate verification_state.yaml", out)
        self.assertTrue(out.endswith(ABLATION_REMINDER))

    def test_selfcheck_prompt_shadow_variant(self):
        import phase_auto_responder as par
        normal = par._build_selfcheck_prompt("phase4", "/rf", "h-e1", shadow=False)
        shadow = par._build_selfcheck_prompt("phase4", "/rf", "h-e1", shadow=True)
        self.assertIn("Read the current checkpoint/state files", normal)
        self.assertNotIn("Read the current checkpoint/state files", shadow)
        self.assertIn("do NOT Read/Edit/Write verification_state.yaml", shadow)
        self.assertIn("```state", shadow)

    def test_is_shadow_mode(self):
        import phase_auto_responder as par
        self.assertTrue(par._is_shadow_mode({"state_mode": "shadow"}))
        self.assertFalse(par._is_shadow_mode({"state_mode": "normal"}))
        self.assertFalse(par._is_shadow_mode({}))
        self.assertFalse(par._is_shadow_mode(None))


class TestArchiveRestoreShadowMerge(unittest.TestCase):
    """run_post_experiment.restore_from_archive must MERGE directories that
    already exist — the ablation manager creates a fresh empty
    .ablation_shadow/ at launcher start, and a plain skip strands the archived
    shadow state (2026-07-09 dl4c Part 2 abort at Phase 4.5)."""

    def _setup_folder(self):
        rf = Path(tempfile.mkdtemp())
        # live folder: empty shadow dir (as created by AblationStateManager)
        (rf / ".ablation_shadow").mkdir()
        # archive: full snapshot including populated shadow
        arch = rf / "_archive" / "20260101T000000_routing_recovery"
        (arch / ".ablation_shadow" / "h-e1").mkdir(parents=True)
        (arch / ".ablation_shadow" / "verification_state.yaml").write_text("x: 1\n")
        (arch / ".ablation_shadow" / "h-e1" / "04_checkpoint.yaml").write_text("y: 2\n")
        (arch / "02b_verification_plan.md").write_text("plan")
        (arch / "_ARCHIVED.md").write_text("marker")
        return rf

    def test_existing_empty_shadow_dir_is_merged(self):
        import run_post_experiment as rpe
        rf = self._setup_folder()
        self.assertTrue(rpe.restore_from_archive(str(rf)))
        self.assertTrue((rf / ".ablation_shadow" / "verification_state.yaml").exists())
        self.assertTrue((rf / ".ablation_shadow" / "h-e1" / "04_checkpoint.yaml").exists())
        self.assertTrue((rf / "02b_verification_plan.md").exists())

    def test_existing_live_files_kept_over_archived(self):
        import run_post_experiment as rpe
        rf = self._setup_folder()
        live = rf / ".ablation_shadow" / "verification_state.yaml"
        live.write_text("live: newer\n")
        rpe.restore_from_archive(str(rf))
        self.assertEqual(live.read_text(), "live: newer\n")  # live copy wins
        self.assertTrue((rf / ".ablation_shadow" / "h-e1" / "04_checkpoint.yaml").exists())


class TestGuardHooks(unittest.TestCase):
    """End-to-end subprocess tests against the real hook scripts."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.active = self.tmp / "active_phase.json"
        self.env = dict(os.environ, YOURA_ACTIVE_PHASE_FILE=str(self.active))

    def _write_active(self, state_mode):
        self.active.write_text(json.dumps({
            "phase": "phase2b", "enabled": True, "state_mode": state_mode}))

    def _run(self, script, payload):
        proc = subprocess.run(
            [PYTHON, str(HOOKS_DIR / script)],
            input=json.dumps(payload), capture_output=True, text=True,
            env=self.env, timeout=30)
        out = proc.stdout.strip()
        return json.loads(out) if out else None

    def test_file_guard_blocks_target_in_shadow(self):
        self._write_active("shadow")
        for tool in ("Read", "Write", "Edit"):
            decision = self._run("guard_state_files.py", {
                "tool_name": tool,
                "tool_input": {"file_path": "/x/docs/r/verification_state.yaml"}})
            self.assertIsNotNone(decision, tool)
            self.assertEqual(decision.get("decision"), "block", tool)

    def test_file_guard_blocks_shadow_dir(self):
        self._write_active("shadow")
        decision = self._run("guard_state_files.py", {
            "tool_name": "Read",
            "tool_input": {"file_path": "/x/.ablation_shadow/verification_state.yaml"}})
        self.assertEqual(decision.get("decision"), "block")

    def test_file_guard_allows_normal_mode(self):
        self._write_active("normal")
        decision = self._run("guard_state_files.py", {
            "tool_name": "Write",
            "tool_input": {"file_path": "/x/verification_state.yaml"}})
        self.assertIsNone(decision)

    def test_file_guard_allows_template_and_other_files(self):
        self._write_active("shadow")
        for path in ("/x/verification_state_template.yaml",
                     "/x/04_validation.md", "/x/02b_verification_plan.md"):
            decision = self._run("guard_state_files.py", {
                "tool_name": "Write", "tool_input": {"file_path": path}})
            self.assertIsNone(decision, path)

    def test_file_guard_silent_without_active_phase(self):
        decision = self._run("guard_state_files.py", {
            "tool_name": "Write",
            "tool_input": {"file_path": "/x/verification_state.yaml"}})
        self.assertIsNone(decision)

    def test_bash_guard_blocks_reads_in_shadow(self):
        self._write_active("shadow")
        for cmd in ("wc -l verification_state.yaml",
                    "grep -A 5 metadata verification_state.yaml",
                    "cat docs/r/h-e1/04_checkpoint.yaml",
                    "echo x > docs/r/verification_state.yaml",
                    "ls .ablation_shadow/"):
            decision = self._run("guard_bash.py", {
                "tool_name": "Bash", "tool_input": {"command": cmd}})
            self.assertIsNotNone(decision, cmd)
            self.assertEqual(decision.get("decision"), "block", cmd)

    def test_bash_guard_allows_heredoc_body_mention(self):
        self._write_active("shadow")
        cmd = ("cat << 'EOF' > 04_validation.md\n"
               "state tracked previously in verification_state.yaml\n"
               "EOF")
        decision = self._run("guard_bash.py", {
            "tool_name": "Bash", "tool_input": {"command": cmd}})
        self.assertIsNone(decision)

    def test_bash_guard_normal_mode_untouched(self):
        self._write_active("normal")
        decision = self._run("guard_bash.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "cat verification_state.yaml"}})
        self.assertIsNone(decision)


if __name__ == "__main__":
    unittest.main(verbosity=2)
