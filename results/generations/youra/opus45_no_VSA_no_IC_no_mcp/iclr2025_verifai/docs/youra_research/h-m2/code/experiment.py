from typing import Dict, List
from errors import parse_compiler_output
from sections import format_structured_prompt, format_scrambled_prompt
from models import generate_code
from repair_loop import execute_and_check, extract_code_block

def run_repair(model_ref, tokenizer, sample: Dict, prompt: str) -> bool:
    """Single repair attempt: generate -> extract -> execute -> bool."""
    code = generate_code(model_ref, tokenizer, prompt)
    code = extract_code_block(code)
    passed, _ = execute_and_check(code, sample["problem"])
    return passed

def run_paired_condition(model_ref, tokenizer, sample: Dict, seed: int) -> Dict:
    """Run both structured and scrambled conditions on same sample."""
    error = parse_compiler_output(sample["raw_error"], sample["original_code"])

    structured_prompt = format_structured_prompt(error, sample["original_code"])
    structured_passed = run_repair(model_ref, tokenizer, sample, structured_prompt)

    scrambled_prompt = format_scrambled_prompt(error, sample["original_code"], seed)
    scrambled_passed = run_repair(model_ref, tokenizer, sample, scrambled_prompt)

    return {
        "task_id": sample["task_id"],
        "structured_passed": structured_passed,
        "scrambled_passed": scrambled_passed,
        "scramble_seed": seed,
    }

def run_all_paired(model_ref, tokenizer, samples: List[Dict]) -> List[Dict]:
    """Run paired conditions on all samples."""
    results = []
    for i, sample in enumerate(samples):
        seed = i * 17 + 42  # Deterministic but varied seed per sample
        result = run_paired_condition(model_ref, tokenizer, sample, seed)
        results.append(result)
        if (i + 1) % 50 == 0:
            print(f"Processed {i+1}/{len(samples)} samples")
    return results
