#!/usr/bin/env python3
"""Tests for the combined no-IC (fixed responder) + no-VSA (shadow) arm.

Covers the integration points added when porting the fixed responder into the
shadow tree:
  - _shadow_premerge_for_fixed: the Stop hook must stage the CURRENT
    session's ```state restate (from the FULL transcript file) so the
    deterministic check sees it, WITHOUT persisting into the launcher-owned
    real shadow dir (persisting a partial mid-workflow restate would poison
    later merges).
  - fixed resume prompt sanitization: the fixed prompt must carry the
    ablation reminder and must not instruct creating the VSA files.
"""
import shutil
import tempfile
import unittest
from pathlib import Path

import phase_auto_responder as par
import phase_output_verifier as pov


RESTATE_TRANSCRIPT = """some assistant text

```state
sub_hypotheses:
  h-e1:
    type: EXISTENCE
    status: IN_PROGRESS
    prerequisites: []
    gate:
      type: SHOULD_WORK
      satisfied: null
      result: null
```
trailing text
"""

STAGING = par.CACHE_DIR / "fixed_premerge_staging"


class TestShadowPremergeForFixed(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fixed_shadow_test_"))
        self._saved_mgr = pov._STATE_MANAGER
        shutil.rmtree(STAGING, ignore_errors=True)

    def tearDown(self):
        pov.set_state_manager(self._saved_mgr)
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(STAGING, ignore_errors=True)

    def _write_transcript(self, text):
        p = self.tmp / "transcript.log"
        p.write_text(text, encoding="utf-8")
        return str(p)

    def test_premerge_stages_restate_and_installs_manager(self):
        tp = self._write_transcript(RESTATE_TRANSCRIPT)
        par._shadow_premerge_for_fixed(str(self.tmp), tp, "h-e1")

        staged_vs = STAGING / "verification_state.yaml"
        self.assertTrue(staged_vs.exists(),
                        "premerge must stage the restate for the deterministic check")
        import yaml
        state = yaml.safe_load(staged_vs.read_text(encoding="utf-8"))
        self.assertIn("h-e1", state.get("sub_hypotheses", {}))

        self.assertFalse((self.tmp / ".ablation_shadow").exists(),
                         "premerge must not even create the launcher-owned shadow dir")

        self.assertIsNotNone(pov._STATE_MANAGER,
                             "premerge must install the manager for _sp() resolution")
        resolved = pov._sp(self.tmp / "verification_state.yaml")
        self.assertEqual(resolved, staged_vs,
                         "verifier checks must resolve VSA paths to the staging copy")

    def test_premerge_seeds_staging_from_existing_shadow(self):
        shadow_vs = self.tmp / ".ablation_shadow" / "verification_state.yaml"
        shadow_vs.parent.mkdir(parents=True)
        shadow_vs.write_text("sub_hypotheses:\n  h-e9:\n    status: READY\n",
                             encoding="utf-8")
        tp = self._write_transcript("no state block here")
        par._shadow_premerge_for_fixed(str(self.tmp), tp, None)
        import yaml
        staged = yaml.safe_load((STAGING / "verification_state.yaml").read_text(encoding="utf-8"))
        self.assertIn("h-e9", staged.get("sub_hypotheses", {}),
                      "staging must start from a copy of the existing shadow state")

    def test_premerge_without_restate_still_installs_manager(self):
        tp = self._write_transcript("no state block here")
        par._shadow_premerge_for_fixed(str(self.tmp), tp, None)
        self.assertIsNotNone(pov._STATE_MANAGER)

    def test_premerge_none_research_folder_is_noop(self):
        pov.set_state_manager(None)
        par._shadow_premerge_for_fixed(None, "/nonexistent", None)
        self.assertIsNone(pov._STATE_MANAGER)


class TestFixedPromptShadowSanitize(unittest.TestCase):
    def test_sanitized_fixed_prompt_carries_ablation_reminder(self):
        from ablation_state_manager import ABLATION_REMINDER
        raw = par._build_fixed_resume_prompt(
            "phase4",
            "  [x] verification_state.yaml: FILE MISSING",
            "/tmp/research", "h-e1")
        sanitized = par._shadow_sanitize_resume(raw)
        self.assertIn(ABLATION_REMINDER.strip()[:40], sanitized,
                      "shadow fixed prompt must append the ablation reminder")

    def test_responder_mode_resolution(self):
        # Global config in this tree pins the ablation arm.
        self.assertEqual(par._get_responder_mode({}), "fixed")
        self.assertEqual(par._get_responder_mode({"responder_mode": "llm"}), "llm")


if __name__ == "__main__":
    unittest.main()
