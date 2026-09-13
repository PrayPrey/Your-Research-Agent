#!/usr/bin/env python3
"""Unit tests for the VSA-IC ablation shadow-state relay (plan v2 tests 1-5, 13)."""

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from ablation_state_manager import (
    AblationStateManager, INJECTED_MARKER, MODEL_FIELDS,
)
from ablation_audit import audit_clean_disable


def make_state(n_hyps=3, n_history=20):
    sub = {}
    for i in range(1, n_hyps + 1):
        h_id = f"h-e{i}"
        sub[h_id] = {
            "type": "EXISTENCE",
            "statement": f"Hypothesis {i} statement " + "x" * 100,
            "status": "READY" if i == 1 else "NOT_STARTED",
            "prerequisites": [] if i == 1 else [f"h-e{i-1}"],
            "gate": {"type": "MUST_WORK", "satisfied": None},
            "experiment_design": {"status": "NOT_STARTED", "file": None},
            "implementation_planning": {"status": "NOT_STARTED",
                                        "task_breakdown": {"epics": 5},
                                        "archon_document_ids": {"prd": "doc-123"}},
            "validation": {"status": "NOT_STARTED", "result": None,
                           "key_findings": None},
        }
    return {
        "metadata": {"pipeline_project_id": "proj-uuid-abcd",
                     "hypothesis_task_mapping": {"h-e1": "task-uuid-1"},
                     "schema_version": "3.5"},
        "workflow": {"status": "ACTIVE", "current_phase": "Phase 2C",
                     "status_history": [
                         {"status": "ACTIVE", "n": k} for k in range(n_history)]},
        "sub_hypotheses": sub,
        "history": [{"event": f"event-{k}"} for k in range(n_history)],
        "statistics": {"total_hypotheses": n_hyps},
        "serena_memory": {"refs": []},
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ablation_test_"))
        self.vs_path = self.tmp / "verification_state.yaml"
        with open(self.vs_path, "w") as f:
            yaml.dump(make_state(), f, sort_keys=False)
        (self.tmp / "h-e1").mkdir()
        with open(self.tmp / "h-e1" / "04_checkpoint.yaml", "w") as f:
            yaml.dump({"current_step": 1,
                       "tasks": {"items": [{"id": "t1", "status": "todo"}]},
                       "task_history": [{"n": k} for k in range(12)]}, f)
        self.mgr = AblationStateManager(self.tmp, mode="shadow")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestPathResolution(Base):
    def test_shadow_redirect(self):
        p = self.mgr.state_path(self.tmp / "verification_state.yaml")
        self.assertEqual(p, self.tmp / ".ablation_shadow" / "verification_state.yaml")
        p = self.mgr.state_path(self.tmp / "h-e1" / "04_checkpoint.yaml")
        self.assertEqual(p, self.tmp / ".ablation_shadow" / "h-e1" / "04_checkpoint.yaml")

    def test_non_target_passthrough(self):
        p = self.mgr.state_path(self.tmp / "h-e1" / "04_validation.md")
        self.assertEqual(p, self.tmp / "h-e1" / "04_validation.md")

    def test_normal_mode_passthrough(self):
        mgr = AblationStateManager(self.tmp, mode="normal")
        p = mgr.state_path(self.tmp / "verification_state.yaml")
        self.assertEqual(p, self.tmp / "verification_state.yaml")

    def test_archive_path_untouched(self):
        outside = Path("/somewhere/else/verification_state.yaml")
        self.assertEqual(self.mgr.state_path(outside), outside)

    def test_no_double_shadow(self):
        shadowed = self.tmp / ".ablation_shadow" / "verification_state.yaml"
        self.assertEqual(self.mgr.state_path(shadowed), shadowed)

    def test_init_seeded_from_real(self):
        self.assertTrue((self.tmp / ".ablation_shadow" / "verification_state.yaml").exists())
        self.assertTrue((self.tmp / ".ablation_shadow" / "h-e1" / "04_checkpoint.yaml").exists())


class TestTruncation(Base):
    def test_history_truncated_and_capped(self):
        text, meta = self.mgr.build_state_text("h-e1", phase="phase4",
                                               include_checkpoint=True)
        self.assertLessEqual(meta["chars_injected"], 4300)  # cap + marker slack
        self.assertGreater(meta["events_dropped"], 0)
        self.assertIn("earlier events omitted", text)
        self.assertIn(INJECTED_MARKER, text)

    def test_nonactive_summarized_active_and_prereq_full(self):
        # active h-e2 has prerequisite h-e1 → h-e3 summarized, h-e1/h-e2 full
        text, meta = self.mgr.build_state_text("h-e2", phase="phase4",
                                               char_cap=100000)
        self.assertEqual(meta["hypotheses_summarized"], 1)
        self.assertIn("Hypothesis 2 statement", text)   # active kept full
        self.assertIn("Hypothesis 1 statement", text)   # prereq kept full
        self.assertNotIn("Hypothesis 3 statement", text)  # summarized

    def test_archon_ids_readonly_reference_only(self):
        # Spec R5: Archon IDs SHOWN read-only (needed for MCP calls) but
        # excluded from the restate contract; rest of metadata dropped.
        text, _ = self.mgr.build_state_text("h-e1", phase="phase4",
                                            char_cap=100000)
        self.assertIn("READ-ONLY", text)
        self.assertIn("proj-uuid-abcd", text)
        # only as comment lines, never as a yaml `metadata:` section
        self.assertNotIn("\nmetadata:", text)
        self.assertNotIn("schema_version", text)

    def test_priority_truncation_protects_checkpoint(self):
        # C1/C10: a huge verification_state must never amputate the
        # checkpoint/tasks sections — the state view is cut first.
        st = self.mgr.load_shadow_state()
        st["history"] = [{"event": "x" * 200, "n": k} for k in range(5)]
        for h in st["sub_hypotheses"].values():
            h["statement"] = "s" * 3000
        self.mgr.save_shadow_state(st)
        text, meta = self.mgr.build_state_text(
            "h-e1", phase="phase4",
            include_checkpoint=True, include_tasks=True, char_cap=4000)
        self.assertIn("# 04_checkpoint (h-e1)", text)
        self.assertNotIn("checkpoint", meta["sections_dropped"])

    def test_fence_anchor_survives_inner_fences(self):
        # C13: a ``` inside an indented block scalar must not close the block
        transcript = (
            "```state\nsub_hypotheses:\n  h-e1:\n"
            "    validation:\n      status: COMPLETED\n"
            "      key_findings: |\n        snippet:\n        ```python\n"
            "        print(1)\n        ```\n"
            "    gate: {satisfied: true}\n```\n")
        data = self.mgr.parse_restate_block(transcript)
        self.assertIsNotNone(data)
        self.assertTrue(data["sub_hypotheses"]["h-e1"]["gate"]["satisfied"])

    def test_stream_json_transcript_parsed(self):
        # C11: restate blocks inside stream-json assistant events are found
        import json as _json
        evt = {"type": "assistant", "message": {"content": [
            {"type": "text",
             "text": "done\n```state\nsub_hypotheses:\n  h-e1:\n"
                     "    gate: {satisfied: true}\n```"}]}}
        transcript = _json.dumps({"type": "system"}) + "\n" + _json.dumps(evt)
        data = self.mgr.parse_restate_block(transcript)
        self.assertIsNotNone(data)
        self.assertTrue(data["sub_hypotheses"]["h-e1"]["gate"]["satisfied"])

    def test_hypotheses_list_schema_normalized(self):
        # C14: Phase 2B 'hypotheses:' list variant adopted on initial creation
        import tempfile as _tf, shutil as _sh
        tmp2 = Path(_tf.mkdtemp(prefix="ablation_listschema_"))
        try:
            mgr2 = AblationStateManager(tmp2, mode="shadow")
            restated = {"hypotheses": [
                {"id": "h-e1", "status": "READY",
                 "gate": {"type": "MUST_WORK", "satisfied": None}}]}
            self.assertTrue(mgr2.merge_restate_to_shadow(restated))
            st = mgr2.load_shadow_state()
            self.assertIn("h-e1", st["sub_hypotheses"])
        finally:
            _sh.rmtree(tmp2, ignore_errors=True)

    def test_version_history_append_only(self):
        # P3: truncated echo must not erase real history; placeholders dropped
        st = self.mgr.load_shadow_state()
        st["sub_hypotheses"]["h-e1"]["version_history"] = [
            {"version": 1, "result": "PARTIAL"}]
        self.mgr.save_shadow_state(st)
        restated = {"sub_hypotheses": {"h-e1": {"version_history": [
            "...(3 earlier events omitted)...",
            {"version": 2, "result": "PASS"}]}}}
        self.mgr.merge_restate_to_shadow(restated, "h-e1")
        vh = self.mgr.load_shadow_state()["sub_hypotheses"]["h-e1"]["version_history"]
        self.assertEqual(vh, [{"version": 1, "result": "PARTIAL"},
                              {"version": 2, "result": "PASS"}])

    def test_phase45_full_results(self):
        # give every hypothesis findings, then check all survive in phase45
        st = self.mgr.load_shadow_state()
        for h in st["sub_hypotheses"].values():
            h["validation"]["result"] = "PASS"
            h["validation"]["key_findings"] = "FINDING-" + h["statement"][:12]
        self.mgr.save_shadow_state(st)
        text, meta = self.mgr.build_state_text(None, phase="phase45")
        self.assertEqual(meta["hypotheses_summarized"], 0)
        self.assertEqual(text.count("FINDING-"), 3)
        # bulky planning detail dropped
        self.assertNotIn("task_breakdown", text)


class TestRestateParsing(Base):
    def test_parses_last_model_block_skips_injected(self):
        transcript = (
            "prompt echo:\n```state\n" + INJECTED_MARKER +
            "\nsub_hypotheses:\n  h-e1:\n    status: READY\n```\n"
            "model work...\n"
            "```state\nsub_hypotheses:\n  h-e1:\n    gate: {satisfied: false}\n```\n"
            "more work...\n"
            "```state\nsub_hypotheses:\n  h-e1:\n    gate: {satisfied: true, result: PASS}\n"
            "    validation: {status: COMPLETED, result: PASS}\n```\n"
        )
        data = self.mgr.parse_restate_block(transcript)
        self.assertIsNotNone(data)
        self.assertTrue(data["sub_hypotheses"]["h-e1"]["gate"]["satisfied"])

    def test_malformed_returns_none(self):
        self.assertIsNone(self.mgr.parse_restate_block("no block here"))
        self.assertIsNone(self.mgr.parse_restate_block("```state\n[:::bad yaml\n```"))


class TestMergePolicy(Base):
    def test_model_fields_merged_harness_fields_protected(self):
        restated = {"sub_hypotheses": {"h-e1": {
            "status": "COMPLETED",              # HARNESS field — must NOT apply
            "prerequisites": ["h-bogus"],       # HARNESS — must NOT apply
            "gate": {"type": "SHOULD_WORK",      # gate.type HARNESS — must NOT apply
                     "satisfied": True,          # MODEL — applies
                     "result": "PASS"},
            "validation": {"status": "COMPLETED", "result": "PASS",
                           "key_findings": "works"},
            "superseded": {"superseded_by": "h-e1-v2"},  # conflict zone — NOT applied
        }}}
        self.assertTrue(self.mgr.merge_restate_to_shadow(restated, "h-e1"))
        st = self.mgr.load_shadow_state()
        h = st["sub_hypotheses"]["h-e1"]
        self.assertEqual(h["status"], "READY")               # protected
        self.assertEqual(h["prerequisites"], [])             # protected
        self.assertEqual(h["gate"]["type"], "MUST_WORK")     # protected
        self.assertTrue(h["gate"]["satisfied"])              # merged
        self.assertEqual(h["validation"]["result"], "PASS")  # merged
        self.assertNotIn("superseded", h)                    # protected

    def test_archon_ids_carried_forward(self):
        restated = {"sub_hypotheses": {"h-e1": {
            "gate": {"satisfied": True}},
            }, "metadata": {"pipeline_project_id": "HALLUCINATED"}}
        self.mgr.merge_restate_to_shadow(restated, "h-e1")
        st = self.mgr.load_shadow_state()
        self.assertEqual(st["metadata"]["pipeline_project_id"], "proj-uuid-abcd")

    def test_top_level_dict_never_replaced(self):
        restated = {"sub_hypotheses": {"h-e1": {"gate": {"satisfied": False}}}}
        self.mgr.merge_restate_to_shadow(restated, "h-e1")
        st = self.mgr.load_shadow_state()
        self.assertIsInstance(st["sub_hypotheses"], dict)
        self.assertEqual(len(st["sub_hypotheses"]), 3)  # other entries intact

    def test_new_version_entry_adopted(self):
        restated = {"sub_hypotheses": {"h-e1-v2": {
            "status": "READY", "version": 2, "modified_from": "h-e1",
            "gate": {"type": "MUST_WORK", "satisfied": None}}}}
        self.mgr.merge_restate_to_shadow(restated)
        st = self.mgr.load_shadow_state()
        self.assertIn("h-e1-v2", st["sub_hypotheses"])

    def test_checkpoint_wholesale_replace(self):
        restated = {"checkpoint": {"current_step": 8,
                                   "reflection_outcome": "SELF_MODIFY"}}
        self.mgr.merge_restate_to_shadow(restated, "h-e1")
        cp = self.mgr.load_shadow_checkpoint("h-e1")
        self.assertEqual(cp["current_step"], 8)
        self.assertEqual(cp["reflection_outcome"], "SELF_MODIFY")

    def test_initial_creation_adopts_wholesale(self):
        tmp2 = Path(tempfile.mkdtemp(prefix="ablation_init_"))
        try:
            mgr2 = AblationStateManager(tmp2, mode="shadow")
            restated = {"metadata": {"pipeline_project_id": "from-model"},
                        "sub_hypotheses": {"h-e1": {"status": "READY"}}}
            self.assertTrue(mgr2.merge_restate_to_shadow(restated))
            st = mgr2.load_shadow_state()
            self.assertEqual(st["metadata"]["pipeline_project_id"], "from-model")
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)

    def test_merge_from_transcript(self):
        log = self.tmp / "session.log"
        log.write_text("```state\nsub_hypotheses:\n  h-e1:\n"
                       "    gate: {satisfied: true}\n```\n")
        self.assertTrue(self.mgr.merge_from_transcript(log, "h-e1"))
        st = self.mgr.load_shadow_state()
        self.assertTrue(st["sub_hypotheses"]["h-e1"]["gate"]["satisfied"])


class TestPromptBlocks(Base):
    def test_override_and_state_present(self):
        blocks = self.mgr.build_prompt_blocks("h-e1", phase="phase4",
                                              include_checkpoint=True)
        self.assertIn("STATE ACCESS OVERRIDE (ABLATION MODE)", blocks)
        self.assertIn("Current Pipeline State", blocks)

    def test_normal_mode_empty(self):
        mgr = AblationStateManager(self.tmp, mode="normal")
        self.assertEqual(mgr.build_prompt_blocks("h-e1"), "")

    def test_prompt_replacements(self):
        p = ("Key instructions:\n- Load 03_tasks.yaml for h-e1\n"
             "- Update verification_state.yaml with validation results\n"
             "- Read 04_checkpoint.yaml now")
        out = self.mgr.apply_prompt_replacements(p)
        self.assertNotIn("Load 03_tasks.yaml", out)
        self.assertNotIn("Update verification_state.yaml", out)
        self.assertNotIn("Read 04_checkpoint.yaml", out)


class TestAudit(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="audit_test_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_clean_log_passes(self):
        (self.tmp / "phase4_h-e1_output.log").write_text(
            "Read(file_path=/x/02c_experiment_brief.md)\n"
            "the state below mentions verification_state.yaml in prose\n")
        passed, v, w = audit_clean_disable(self.tmp)
        self.assertTrue(passed)
        self.assertEqual(v, [])

    def test_violation_detected(self):
        (self.tmp / "phase4_h-e1_output.log").write_text(
            "⏺ Read(file_path=/research/verification_state.yaml)\n")
        passed, v, w = audit_clean_disable(self.tmp)
        self.assertFalse(passed)
        self.assertEqual(len(v), 1)

    def test_bash_is_warning_not_violation(self):
        (self.tmp / "phase2c_h-e1_output.log").write_text(
            "⏺ Bash(cat /research/04_checkpoint.yaml)\n")
        passed, v, w = audit_clean_disable(self.tmp)
        self.assertTrue(passed)
        self.assertEqual(len(w), 1)

    def test_exempt_pattern(self):
        (self.tmp / "phase4_h-e1_mock_verify.log").write_text(
            "Read(file_path=/r/verification_state.yaml)\n")
        passed, v, w = audit_clean_disable(self.tmp, exempt_patterns=["mock_verify"])
        self.assertTrue(passed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
