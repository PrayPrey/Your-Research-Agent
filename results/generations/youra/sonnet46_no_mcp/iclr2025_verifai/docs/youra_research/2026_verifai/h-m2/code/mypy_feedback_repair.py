import ast
import json
import logging
import os
import re
import tempfile
from typing import Dict, List, Optional, Tuple

import mypy.api
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import MypyRepairConfig

logger = logging.getLogger(__name__)


class MypyFeedbackRepair:
    def __init__(self, cfg: MypyRepairConfig, model=None, tokenizer=None) -> None:
        self.cfg = cfg
        self.model = model
        self.tokenizer = tokenizer

    def load_model(self, model_name: str = "codellama/CodeLlama-7b-hf") -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        self.model.eval()

    def parse_mypy_output(self, stdout: str) -> List[Tuple[int, str, str]]:
        errors = []
        for line in stdout.splitlines():
            m = re.match(r'.+:(\d+): (\w+): (.+)', line)
            if m and m.group(2) == "error":
                errors.append((int(m.group(1)), "error", m.group(3)))
        return errors

    def format_structured_feedback(
        self,
        ast_valid: bool,
        ast_error: Optional[str],
        mypy_errors: List[Tuple[int, str, str]],
    ) -> str:
        if not ast_valid:
            return f"AST ERROR: {ast_error}\nFix the syntax error."
        if not mypy_errors:
            return "No errors."
        lines = ["Type errors:"]
        for line_num, _, msg in mypy_errors[:10]:
            lines.append(f"  Line {line_num}: {msg}")
        return "\n".join(lines)

    def build_repair_prompt(
        self,
        problem_prompt: str,
        current_code: str,
        feedback: str,
    ) -> str:
        return (
            f"{problem_prompt}\n\n"
            f"# Current code with errors:\n```python\n{current_code}\n```\n\n"
            f"# Feedback:\n{feedback}\n\n"
            f"# Fixed code:\n```python\n"
        )

    def _run_mypy_on_code(self, code: str) -> Tuple[str, str, int]:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, prefix="mypy_repair_"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            stdout, stderr, exit_code = mypy.api.run(self.cfg.mypy_flags + [tmp_path])
        except Exception as e:
            logger.warning(f"mypy failed: {e}")
            stdout, stderr, exit_code = "", str(e), 1
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        return stdout, stderr, exit_code

    def _generate_repair(self, prompt: str) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("call load_model() first")
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.cfg.max_new_tokens,
                temperature=self.cfg.repair_temperature,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = outputs[0][inputs["input_ids"].shape[1]:]
        raw = self.tokenizer.decode(generated, skip_special_tokens=True)
        # Extract code from ```python ... ``` block if present
        block_match = re.search(r"```python\n(.*?)(?:```|$)", raw, re.DOTALL)
        if block_match:
            return block_match.group(1).strip()
        return raw.strip()

    def repair_sample(
        self,
        baseline_code: str,
        problem: dict,
        task_id: str,
        sample_idx: int,
    ) -> dict:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("call load_model() first")
        current_code = baseline_code
        feedback_history = []

        for r in range(self.cfg.max_rounds):
            try:
                ast.parse(current_code)
                ast_valid = True
                ast_err = None
            except SyntaxError as e:
                ast_valid = False
                ast_err = str(e)

            stdout, _, mypy_exit = self._run_mypy_on_code(current_code)
            mypy_errors = self.parse_mypy_output(stdout)
            errors_before = len(mypy_errors)

            if ast_valid and mypy_exit == 0:
                break

            feedback = self.format_structured_feedback(ast_valid, ast_err, mypy_errors)
            prompt = self.build_repair_prompt(problem.get("prompt", ""), current_code, feedback)
            repaired = self._generate_repair(prompt)
            if not repaired:
                feedback_history.append(feedback)
                continue
            current_code = repaired

            stdout2, _, _ = self._run_mypy_on_code(current_code)
            new_errs = len(self.parse_mypy_output(stdout2))
            logger.info(f"mypy_feedback_applied: round={r}, errors_before={errors_before}, errors_after={new_errs}")
            feedback_history.append(feedback)

        try:
            ast.parse(current_code)
            ast_valid_final = True
        except SyntaxError:
            ast_valid_final = False
        _, _, mypy_exit_final = self._run_mypy_on_code(current_code)

        return {
            "task_id": task_id,
            "sample_idx": sample_idx,
            "rounds_used": len(feedback_history),
            "final_code": current_code,
            "success": ast_valid_final and mypy_exit_final == 0,
            "ast_valid_final": ast_valid_final,
            "mypy_exit_code_final": mypy_exit_final,
            "feedback_history": feedback_history,
        }

    def repair_pool(
        self,
        baseline_pool: Dict[str, List[dict]],
        problems: Dict[str, dict],
        output_path: str,
        progress_path: str,
    ) -> Dict[str, List[dict]]:
        completed = self._load_progress(progress_path)
        pool: Dict[str, List[dict]] = {}

        # Load existing output
        if os.path.exists(output_path):
            with open(output_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                        pool.setdefault(rec["task_id"], []).append(rec)
                    except json.JSONDecodeError:
                        logger.warning(f"Corrupt JSONL line skipped")

        with open(output_path, "a") as out_f:
            for i, (task_id, records) in enumerate(sorted(baseline_pool.items())):
                if task_id in completed:
                    continue
                if task_id not in problems:
                    logger.warning(f"task_id {task_id} missing from problems, skipping")
                    continue
                problem = problems[task_id]
                repair_records = []
                for rec in records:
                    sample_idx = rec.get("sample_idx", 0)
                    completion = rec.get("completion", "")
                    rr = self.repair_sample(completion, problem, task_id, sample_idx)
                    repair_records.append(rr)
                    out_f.write(json.dumps(rr) + "\n")
                pool[task_id] = repair_records
                completed.add(task_id)
                if (i + 1) % self.cfg.__class__.__dict__.get("checkpoint_interval", 10) == 0 or True:
                    if (i + 1) % 10 == 0:
                        self._save_progress(progress_path, completed)
                out_f.flush()
            self._save_progress(progress_path, completed)
        return pool

    def compute_mechanism_activated_rate(self, repair_pool: Dict[str, List[dict]]) -> float:
        total = activated = 0
        for records in repair_pool.values():
            for rec in records:
                total += 1
                if rec.get("rounds_used", 0) > 0:
                    activated += 1
        return activated / total if total > 0 else 0.0

    def _load_progress(self, progress_path: str):
        if os.path.exists(progress_path):
            with open(progress_path) as f:
                data = json.load(f)
            return set(data.get("completed", []))
        return set()

    def _save_progress(self, progress_path: str, completed) -> None:
        with open(progress_path, "w") as f:
            json.dump({"completed": sorted(completed)}, f)
