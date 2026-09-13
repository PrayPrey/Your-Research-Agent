import ast as ast_module
import json
from typing import Any


class MechanismVerifier:

    def check_logits_processor(self, syn_model: Any) -> bool:
        # Check logits_processor list for grammar-related processor
        lp_list = getattr(syn_model, "logits_processor", None)
        if lp_list is not None:
            for lp in lp_list:
                if "Grammar" in type(lp).__name__:
                    return True

        # Fallback: grammar_decoder attribute
        if hasattr(syn_model, "grammar_decoder"):
            return True

        # Check model.logits_processor_list
        model = getattr(syn_model, "model", None)
        if model is not None:
            lp_list2 = getattr(model, "logits_processor_list", None)
            if lp_list2 is not None:
                for lp in lp_list2:
                    if "Grammar" in type(lp).__name__:
                        return True

        return False

    def run_test_samples(
        self,
        syn_generator: Any,
        test_prompt: str,
        n_test: int = 5,
    ) -> dict:
        constraint_active_count = 0
        ast_valid_count = 0
        for i in range(n_test):
            seed = 42 + i
            try:
                completion, constraint_active = syn_generator._generate_single_constrained(
                    test_prompt, seed
                )
                if constraint_active:
                    constraint_active_count += 1
                try:
                    ast_module.parse(completion)
                    ast_valid_count += 1
                except SyntaxError:
                    pass
            except Exception:
                pass

        return {
            "constraint_active_rate": constraint_active_count / n_test,
            "ast_valid_rate": ast_valid_count / n_test,
        }

    def verify(
        self,
        syn_generator: Any,
        test_prompt: str,
        output_path: str,
    ) -> dict:
        syn_model = getattr(syn_generator, "syn_model", None)
        grammar_lp_present = self.check_logits_processor(syn_model) if syn_model is not None else False

        test_results = self.run_test_samples(syn_generator, test_prompt, n_test=5)
        constraint_active_rate = test_results["constraint_active_rate"]
        ast_valid_rate = test_results["ast_valid_rate"]

        pre_check_passed = grammar_lp_present and constraint_active_rate >= 0.3

        if not pre_check_passed:
            print(
                f"[MechanismVerifier] WARNING: pre_check_passed=False "
                f"(grammar_lp_present={grammar_lp_present}, "
                f"constraint_active_rate={constraint_active_rate:.3f}). "
                "Proceeding with experiment anyway."
            )

        result = {
            "grammar_lp_present": grammar_lp_present,
            "constraint_active_rate": constraint_active_rate,
            "ast_valid_rate": ast_valid_rate,
            "pre_check_passed": pre_check_passed,
            "note": "pre_check_passed=False does not block experiment; empirical results may still show mechanism effect",
        }

        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)

        return result
