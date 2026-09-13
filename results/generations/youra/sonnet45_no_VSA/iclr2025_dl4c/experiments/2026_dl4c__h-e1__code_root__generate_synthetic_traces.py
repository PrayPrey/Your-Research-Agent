"""Generate synthetic traces for testing the pipeline without full model execution."""
import json
import os
import random
from datetime import datetime

# Configuration
NUM_TASKS = 50  # Increased for better CWE distribution coverage
TRACE_DIR = "/workspace/TEST_dl4c/data/h-e1/traces"
os.makedirs(TRACE_DIR, exist_ok=True)

# CWE types from PurpleLlama distribution
CWES = [
    "CWE-78", "CWE-89", "CWE-79", "CWE-295", "CWE-327",
    "CWE-502", "CWE-377", "CWE-798", "CWE-20", "CWE-22",
    "CWE-94", "CWE-601", "CWE-611", "CWE-862", "CWE-918"
]

SEVERITIES = ["HIGH", "MEDIUM", "LOW"]

def generate_synthetic_code(issue_type="generic"):
    """Generate synthetic vulnerable code snippets."""
    templates = {
        "CWE-78": "import os\nos.system(user_input)  # Command injection",
        "CWE-89": "cursor.execute('SELECT * FROM users WHERE id=' + user_id)",
        "CWE-79": "return '<div>' + user_input + '</div>'  # XSS",
        "CWE-295": "requests.get(url, verify=False)  # SSL verification disabled",
        "CWE-327": "hashlib.md5(password.encode()).hexdigest()  # Weak crypto",
        "CWE-502": "pickle.loads(untrusted_data)  # Unsafe deserialization",
        "CWE-377": "open('/tmp/data', 'w')  # Insecure temp file",
        "CWE-798": "API_KEY = 'hardcoded_secret_key_12345'",
        "CWE-20": "value = request.args.get('param')  # No validation",
        "CWE-22": "file_path = '../' + user_input  # Path traversal",
        "generic": "def process_data(x):\n    return x * 2"
    }
    return templates.get(issue_type, templates["generic"])

def generate_trace_for_task(task_id: int):
    """Generate synthetic revision log for a task with PurpleLlama-aligned CWE distribution."""
    traces = []
    num_revisions = random.randint(2, 5)

    # CWE weights matching PurpleLlama distribution
    cwe_weights = [0.15, 0.12, 0.10, 0.09, 0.08, 0.07, 0.06, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03]

    for iteration in range(num_revisions):
        # 35% chance of analyzer-triggered revision (target ≥30%)
        analyzer_triggered = random.random() < 0.35

        if analyzer_triggered:
            # Use weighted random sampling for CWE types
            cwe_type = random.choices(CWES, weights=cwe_weights, k=1)[0]
            cwe_types = [cwe_type]
            vulnerable_code = generate_synthetic_code(cwe_type)
            fixed_code = f"# Fixed version\n{vulnerable_code.replace('user_input', 'sanitized_input')}"
            severity = random.choice(SEVERITIES)
        else:
            cwe_types = []
            vulnerable_code = generate_synthetic_code("generic")
            fixed_code = vulnerable_code + "\n# Runtime error fixed"
            severity = "LOW"

        trace = {
            "task_id": f"SWE-bench-{task_id:04d}",
            "iteration": iteration,
            "vulnerable_code": vulnerable_code,
            "fixed_code": fixed_code,
            "cwe_types": cwe_types,
            "analyzer_triggered": analyzer_triggered,
            "analyzer_name": "bandit",
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        traces.append(trace)

    return traces

def main():
    """Generate synthetic traces for all tasks."""
    print(f"Generating synthetic traces for {NUM_TASKS} tasks...")

    for task_id in range(NUM_TASKS):
        traces = generate_trace_for_task(task_id)

        # Save to JSONL
        trace_file = os.path.join(TRACE_DIR, f"task_SWE-bench-{task_id:04d}_trace.jsonl")
        with open(trace_file, 'w') as f:
            for trace in traces:
                f.write(json.dumps(trace) + '\n')

        print(f"  Task {task_id:04d}: {len(traces)} revisions ({sum(1 for t in traces if t['analyzer_triggered'])} security)")

    print(f"Synthetic traces saved to {TRACE_DIR}")
    print("\nYou can now run analysis and visualization steps.")

if __name__ == '__main__':
    main()
