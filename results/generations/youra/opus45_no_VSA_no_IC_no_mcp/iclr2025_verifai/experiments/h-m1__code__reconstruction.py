"""Reconstruction test: verify LLM can extract original error details from structured format."""
from dataclasses import asdict
from typing import Dict, List, Any

from errors import parse_compiler_output
from judge import JudgeLLM, build_extraction_prompt


def format_structured_for_extraction(structured_error: Dict[str, Any]) -> str:
    """Format structured error dict as text for LLM extraction."""
    lines = [
        f"Error Type: {structured_error['error_type']}",
        f"Line Number: {structured_error['line_number']}",
        f"Message: {structured_error['error_message']}",
        "Code Context:",
    ]
    for ctx_line in structured_error.get("code_context", []):
        lines.append(f"  {ctx_line}")
    return "\n".join(lines)


class ReconstructionTest:
    """Test whether LLM can reconstruct original error details from structured format."""

    def __init__(self, judge: JudgeLLM, fields: List[str]):
        self.judge = judge
        self.fields = fields

    def extract_from_raw(self, raw_error: str, source_code: str) -> Dict[str, Any]:
        """Ground truth: parse raw error to structured form."""
        structured = parse_compiler_output(raw_error, source_code)
        return asdict(structured)

    def extract_from_structured(self, structured_error: Dict[str, Any]) -> Dict[str, Any]:
        """LLM extraction: ask judge to extract fields from formatted structured error."""
        text = format_structured_for_extraction(structured_error)
        prompt = build_extraction_prompt(text, self.fields)
        return self.judge.extract(prompt)

    def compute_accuracy(self, original: Dict[str, Any], reconstructed: Dict[str, Any]) -> float:
        """Fraction of fields where values match (string-normalized)."""
        if not reconstructed:
            return 0.0

        matches = 0
        for field in self.fields:
            orig_val = original.get(field)
            recon_val = reconstructed.get(field)

            # String normalization for comparison
            if field == "code_context":
                # Compare as sets of stripped strings
                orig_set = set(str(v).strip() for v in (orig_val or []))
                recon_set = set(str(v).strip() for v in (recon_val or []))
                if orig_set == recon_set:
                    matches += 1
            else:
                if str(orig_val).strip().lower() == str(recon_val).strip().lower():
                    matches += 1

        return matches / len(self.fields)

    def run(self, error_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run reconstruction test on all pairs."""
        per_sample = []

        for i, pair in enumerate(error_pairs):
            original = pair["structured_error"]
            reconstructed = self.extract_from_structured(original)
            accuracy = self.compute_accuracy(original, reconstructed)

            per_sample.append({
                "index": i,
                "accuracy": accuracy,
                "original": original,
                "reconstructed": reconstructed,
                "perfect_match": accuracy == 1.0,
            })

            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(error_pairs)} samples...")

        # Compute per-field accuracy
        per_field = {f: 0.0 for f in self.fields}
        for sample in per_sample:
            orig = sample["original"]
            recon = sample["reconstructed"]
            for field in self.fields:
                if field == "code_context":
                    orig_set = set(str(v).strip() for v in (orig.get(field) or []))
                    recon_set = set(str(v).strip() for v in (recon.get(field) or []))
                    if orig_set == recon_set:
                        per_field[field] += 1
                else:
                    if str(orig.get(field, "")).strip().lower() == str(recon.get(field, "")).strip().lower():
                        per_field[field] += 1

        for field in self.fields:
            per_field[field] /= len(per_sample)

        mean_accuracy = sum(s["accuracy"] for s in per_sample) / len(per_sample)
        pass_rate = sum(1 for s in per_sample if s["perfect_match"]) / len(per_sample)

        return {
            "mean_accuracy": mean_accuracy,
            "pass_rate": pass_rate,
            "per_sample": per_sample,
            "per_field": per_field,
            "n_samples": len(per_sample),
        }
