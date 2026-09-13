import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from mechanism_verifier import MechanismVerifier


class MockGrammarLP:
    """Mock grammar logits processor."""
    pass


MockGrammarLP.__name__ = "GrammarAlignedLogitsProcessor"


class MockSynModel:
    def __init__(self, has_grammar_lp=True):
        if has_grammar_lp:
            self.logits_processor = [MockGrammarLP()]
        else:
            self.logits_processor = []


class MockSynGenerator:
    def __init__(self, syn_model, constraint_active=True):
        self.syn_model = syn_model
        self._constraint_active = constraint_active

    def _generate_single_constrained(self, prompt, seed):
        return "def foo(): pass", self._constraint_active


class TestMechanismVerifier(unittest.TestCase):

    def setUp(self):
        self.verifier = MechanismVerifier()

    def test_lp_check_true(self):
        model = MockSynModel(has_grammar_lp=True)
        self.assertTrue(self.verifier.check_logits_processor(model))

    def test_lp_check_false(self):
        model = MockSynModel(has_grammar_lp=False)
        self.assertFalse(self.verifier.check_logits_processor(model))

    def test_run_test_samples(self):
        syn_gen = MockSynGenerator(MockSynModel(), constraint_active=True)
        result = self.verifier.run_test_samples(syn_gen, "def foo():", n_test=3)
        self.assertIn("constraint_active_rate", result)
        self.assertIn("ast_valid_rate", result)
        self.assertEqual(result["constraint_active_rate"], 1.0)

    def test_verify_non_blocking(self):
        # Even with pre_check=False, verify() should not raise
        syn_gen = MockSynGenerator(MockSynModel(has_grammar_lp=False), constraint_active=False)
        tmpdir = tempfile.mkdtemp()
        output_path = os.path.join(tmpdir, "mechanism_verification.json")
        result = self.verifier.verify(syn_gen, "def foo():", output_path)
        self.assertFalse(result["pre_check_passed"])
        self.assertIn("pre_check_passed", result)

    def test_json_saved(self):
        syn_gen = MockSynGenerator(MockSynModel(), constraint_active=True)
        tmpdir = tempfile.mkdtemp()
        output_path = os.path.join(tmpdir, "mechanism_verification.json")
        self.verifier.verify(syn_gen, "def foo():", output_path)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path) as f:
            data = json.load(f)
        self.assertIn("pre_check_passed", data)


if __name__ == "__main__":
    unittest.main()
