import re
import traceback
import signal
from typing import Dict, Tuple
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
