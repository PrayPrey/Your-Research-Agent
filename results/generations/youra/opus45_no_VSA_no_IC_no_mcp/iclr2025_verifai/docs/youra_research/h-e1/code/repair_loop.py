import re
import traceback
import signal
from typing import Dict, Any, Tuple, List
from errors import parse_compiler_output
from prompts import format_structured_prompt, format_raw_prompt
from models import generate_code
from config import CONFIG

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")

def execute_and_check(code: str, problem: Dict) -> Tuple[bool, str]:
    test_code = problem.get("test", "")
    entry_point = problem.get("entry_point", "solution")
    full_code = code + "\n" + test_code

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(CONFIG["exec_timeout_sec"]))
    try:
        exec_globals = {}
        exec(full_code, exec_globals)
        signal.alarm(0)
        return (True, "")
    except TimeoutError:
        return (False, "TimeoutError: execution exceeded timeout")
    except Exception as e:
        signal.alarm(0)
        return (False, traceback.format_exc())
    finally:
        signal.signal(signal.SIGALRM, old_handler)

def extract_code_block(text: str) -> str:
    match = re.search(r'```(?:python)?\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

def initial_prompt(problem: Dict) -> str:
    return f"""Write a Python function to solve the following problem.

{problem.get("prompt", "")}

Provide only the complete Python code:"""

def repair_problem(model_ref, tokenizer, problem: Dict, use_structured: bool,
                   max_attempts: int = None, is_openai: bool = False) -> Dict:
    max_attempts = max_attempts or CONFIG["max_repair_attempts"]
    error_types_seen: List[str] = []

    prompt = initial_prompt(problem)
    code = generate_code(model_ref, tokenizer, prompt, is_openai)
    code = extract_code_block(code)

    passed, raw_error = execute_and_check(code, problem)
    if passed:
        return {"passed": True, "attempts_used": 0, "error_types_seen": error_types_seen}

    for attempt in range(1, max_attempts + 1):
        if use_structured:
            err = parse_compiler_output(raw_error, code)
            error_types_seen.append(err.error_type)
            repair_prompt = format_structured_prompt(err, code)
        else:
            error_type_match = re.search(r'(\w+Error|\w+Exception)', raw_error)
            error_types_seen.append(error_type_match.group(1) if error_type_match else "UnknownError")
            repair_prompt = format_raw_prompt(raw_error, code)

        code = generate_code(model_ref, tokenizer, repair_prompt, is_openai)
        code = extract_code_block(code)

        passed, raw_error = execute_and_check(code, problem)
        if passed:
            return {"passed": True, "attempts_used": attempt, "error_types_seen": error_types_seen}

    return {"passed": False, "attempts_used": max_attempts, "error_types_seen": error_types_seen}
