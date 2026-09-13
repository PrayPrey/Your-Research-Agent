import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import matplotlib.pyplot as plt
import random
import re
from sklearn.metrics import accuracy_score

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

from datasets import load_dataset

print("Loading HuggingFace datasets...")
try:
    humaneval_ds = load_dataset("openai_humaneval", split="test")
    humaneval_problems_raw = list(humaneval_ds)[:40]
    print(f"HumanEval loaded: {len(humaneval_problems_raw)} problems")
except Exception as e:
    print(f"HumanEval load error: {e}")
    humaneval_problems_raw = []

try:
    mbpp_ds = load_dataset("mbpp", split="test")
    mbpp_problems_raw = list(mbpp_ds)[:40]
    print(f"MBPP loaded: {len(mbpp_problems_raw)} problems")
except Exception as e:
    print(f"MBPP load error: {e}")
    mbpp_problems_raw = []

try:
    csn_ds = load_dataset("code_search_net", "python", split="train")
    csn_problems_raw = [
        x
        for x in csn_ds
        if x.get("func_code_string") and len(x["func_code_string"]) < 500
    ][:60]
    print(f"CodeSearchNet loaded: {len(csn_problems_raw)} problems")
except Exception as e:
    print(f"CodeSearchNet load error: {e}")
    csn_problems_raw = []


def parse_assert_tests(assert_list, fn_name=None):
    tests = []
    for stmt in assert_list:
        stmt = stmt.strip()
        m = re.match(r"assert\s+(.+?)\s*==\s*(.+?)(?:\s*,.*)?$", stmt)
        if m:
            call_str = m.group(1).strip()
            exp_str = m.group(2).strip()
            try:
                expected = eval(exp_str)
                tests.append((call_str, expected))
            except Exception:
                pass
    return tests


def parse_humaneval_tests(test_code, fn_name):
    tests = []
    patterns = [
        rf"assert\s+candidate\s*\((.+?)\)\s*==\s*(.+?)(?:\s*,.*)?$",
        rf"assert\s+{re.escape(fn_name)}\s*\((.+?)\)\s*==\s*(.+?)(?:\s*,.*)?$",
    ]
    for line in test_code.split("\n"):
        line = line.strip()
        for pat in patterns:
            m = re.match(pat, line)
            if m:
                args_str = m.group(1).strip()
                exp_str = m.group(2).strip()
                try:
                    expected = eval(exp_str)
                    call_str = f"{fn_name}({args_str})"
                    tests.append((call_str, expected))
                    break
                except Exception:
                    pass
    for m in re.finditer(rf"candidate\s*\(([^)]+)\)\s*==\s*([^\n,)]+)", test_code):
        args_str = m.group(1).strip()
        exp_str = m.group(2).strip()
        try:
            expected = eval(exp_str)
            call_str = f"{fn_name}({args_str})"
            if (call_str, expected) not in tests:
                tests.append((call_str, expected))
        except Exception:
            pass
    return tests


# ============================================================
# THREE ADVERSARIAL STRATEGIES
# ============================================================


def make_adversarial_minimal(fn_name, tests):
    """MINIMAL: Only constant-return strategy."""
    if not tests:
        return [f"def {fn_name}(*args, **kwargs):\n    return None"]
    first_exp = tests[0][1]
    return [f"def {fn_name}(*args, **kwargs):\n    return {repr(first_exp)}"]


def make_adversarial_baseline(fn_name, tests):
    """BASELINE: Lookup table + constant return (original two strategies)."""
    if not tests:
        return [
            f"def {fn_name}(*args, **kwargs):\n    return None",
            f"def {fn_name}(*args, **kwargs):\n    return 0",
        ]
    entries = []
    for call_str, expected in tests:
        m = re.match(rf"{re.escape(fn_name)}\s*\((.*)\)$", call_str, re.DOTALL)
        if m:
            args_str = m.group(1).strip()
            try:
                entries.append(f"    {args_str}: {repr(expected)}")
            except Exception:
                pass
    if entries:
        adv1_lines = [f"def {fn_name}(*args):"]
        adv1_lines.append("    _lookup = {")
        for e in entries:
            adv1_lines.append(f"        {e},")
        adv1_lines.append("    }")
        adv1_lines.append("    _key = args[0] if len(args)==1 else args")
        adv1_lines.append("    return _lookup.get(_key, None)")
        adv1 = "\n".join(adv1_lines)
    else:
        adv1 = f"def {fn_name}(*args, **kwargs):\n    return None"
    first_exp = tests[0][1] if tests else None
    adv2 = f"def {fn_name}(*args, **kwargs):\n    return {repr(first_exp)}"
    return [adv1, adv2]


def make_adversarial_expanded(fn_name, tests):
    """EXPANDED: Diverse adversarials including off-by-one, identity, length, partially-correct."""
    adversarials = []
    if not tests:
        return [
            f"def {fn_name}(*args, **kwargs):\n    return None",
            f"def {fn_name}(*args, **kwargs):\n    return 0",
            f"def {fn_name}(*args, **kwargs):\n    return args[0] if args else None",
        ]
    # 1. Lookup table
    entries = []
    for call_str, expected in tests:
        m = re.match(rf"{re.escape(fn_name)}\s*\((.*)\)$", call_str, re.DOTALL)
        if m:
            args_str = m.group(1).strip()
            try:
                entries.append(f"    {args_str}: {repr(expected)}")
            except Exception:
                pass
    if entries:
        lines = [f"def {fn_name}(*args):"]
        lines.append("    _lookup = {")
        for e in entries:
            lines.append(f"        {e},")
        lines.append("    }")
        lines.append("    _key = args[0] if len(args)==1 else args")
        lines.append("    return _lookup.get(_key, None)")
        adversarials.append("\n".join(lines))
    else:
        adversarials.append(f"def {fn_name}(*args, **kwargs):\n    return None")

    first_exp = tests[0][1]
    # 2. Constant return first expected
    adversarials.append(
        f"def {fn_name}(*args, **kwargs):\n    return {repr(first_exp)}"
    )
    # 3. Return None always
    adversarials.append(f"def {fn_name}(*args, **kwargs):\n    return None")
    # 4. Zero-like default
    if isinstance(first_exp, bool):
        adversarials.append(f"def {fn_name}(*args, **kwargs):\n    return False")
    elif isinstance(first_exp, int):
        adversarials.append(f"def {fn_name}(*args, **kwargs):\n    return 0")
    elif isinstance(first_exp, float):
        adversarials.append(f"def {fn_name}(*args, **kwargs):\n    return 0.0")
    elif isinstance(first_exp, str):
        adversarials.append(f"def {fn_name}(*args, **kwargs):\n    return ''")
    elif isinstance(first_exp, list):
        adversarials.append(f"def {fn_name}(*args, **kwargs):\n    return []")
    else:
        adversarials.append(f"def {fn_name}(*args, **kwargs):\n    return 0")
    # 5. Off-by-one
    if isinstance(first_exp, (int, float)) and not isinstance(first_exp, bool):
        off_val = first_exp + 1
        adversarials.append(
            f"def {fn_name}(*args, **kwargs):\n    return {repr(off_val)}"
        )
    # 6. Identity
    adversarials.append(
        f"def {fn_name}(*args, **kwargs):\n    return args[0] if args else None"
    )
    # 7. Length of input
    adversarials.append(
        f"def {fn_name}(*args, **kwargs):\n"
        f"    try:\n"
        f"        return len(args[0])\n"
        f"    except Exception:\n"
        f"        return 0"
    )
    # 8. Partially correct: right for first test only
    first_call, first_expected = tests[0]
    m = re.match(rf"{re.escape(fn_name)}\s*\((.*)\)$", first_call, re.DOTALL)
    if m:
        first_args = m.group(1).strip()
        partial_lines = [
            f"def {fn_name}(*args, **kwargs):",
            f"    _first_key = args[0] if len(args)==1 else args",
            f"    try:",
            f"        if _first_key == {first_args}:",
            f"            return {repr(first_expected)}",
            f"    except Exception:",
            f"        pass",
            f"    return None",
        ]
        adversarials.append("\n".join(partial_lines))
    return adversarials


# ============================================================
# PROBLEM BUILDERS WITH STRATEGY PARAMETER
# ============================================================


def make_humaneval_problems_with_strategy(raw_items, adv_strategy):
    problems = []
    for i, item in enumerate(raw_items):
        spec = item.get("prompt", "")[:300]
        code = item.get("canonical_solution", "")
        fn_name = item.get("entry_point", "fn")
        test_code = item.get("test", "")
        all_tests = parse_humaneval_tests(test_code, fn_name)
        if not all_tests:
            assert_stmts = re.findall(r"assert\s+.+", test_code)
            all_tests = parse_assert_tests(assert_stmts, fn_name)
        mid = max(1, len(all_tests) // 2)
        given_tests = all_tests[:mid]
        held_out_tests = all_tests[mid:] if len(all_tests) > mid else all_tests[:1]
        if not given_tests:
            continue
        adversarial_codes = adv_strategy(fn_name, given_tests)
        problems.append(
            {
                "id": f"humaneval_{i}",
                "dataset": "humaneval",
                "spec": spec,
                "given_tests": given_tests,
                "held_out_tests": held_out_tests,
                "correct_code": item.get("prompt", "") + code,
                "adversarial_codes": adversarial_codes,
                "fn_name": fn_name,
            }
        )
    return problems


def make_mbpp_problems_with_strategy(raw_items, adv_strategy):
    problems = []
    for i, item in enumerate(raw_items):
        spec = item.get("text", "")[:300]
        code = item.get("code", "")
        test_list = item.get("test_list", [])
        fn_name = "fn"
        m = re.search(r"def (\w+)\s*\(", code)
        if m:
            fn_name = m.group(1)
        all_tests = parse_assert_tests(test_list, fn_name)
        mid = max(1, len(all_tests) // 2)
        given_tests = all_tests[:mid]
        held_out_tests = all_tests[mid:] if len(all_tests) > mid else all_tests[:1]
        if not given_tests:
            continue
        adversarial_codes = adv_strategy(fn_name, given_tests)
        problems.append(
            {
                "id": f"mbpp_{i}",
                "dataset": "mbpp",
                "spec": spec,
                "given_tests": given_tests,
                "held_out_tests": held_out_tests,
                "correct_code": code,
                "adversarial_codes": adversarial_codes,
                "fn_name": fn_name,
            }
        )
    return problems


def make_csn_problems_with_strategy(raw_items, adv_strategy):
    problems = []
    for i, item in enumerate(raw_items):
        code = item.get("func_code_string", "")
        fn_name = item.get("func_name", "fn").split(".")[-1]
        spec = item.get("func_documentation_string", "")[:300]
        if not code or not fn_name:
            continue
        sig_match = re.search(rf"def {re.escape(fn_name)}\s*\(([^)]*)\)", code)
        if not sig_match:
            continue
        params = sig_match.group(1).strip()
        if not params or params in ("self", "*args", "**kwargs"):
            continue
        param_list = [
            p.strip().split(":")[0].strip().split("=")[0].strip()
            for p in params.split(",")
            if p.strip() and p.strip() != "self"
        ]
        if not param_list or len(param_list) > 2:
            continue
        namespace = {}
        try:
            exec(code, namespace)
            fn = namespace.get(fn_name)
            if fn is None:
                continue
        except Exception:
            continue
        input_sets = []
        for inp_str in ["'hello'", "'test'", "'python'", "'world'", "'abc'"]:
            try:
                inp_val = eval(inp_str)
                result = fn(inp_val)
                if result is not None:
                    input_sets.append((f"{fn_name}({inp_str})", result))
            except Exception:
                pass
        if len(input_sets) < 2:
            for inp_str in ["1", "2", "3", "5", "10", "0", "4"]:
                try:
                    inp_val = eval(inp_str)
                    result = fn(inp_val)
                    if result is not None:
                        input_sets.append((f"{fn_name}({inp_str})", result))
                except Exception:
                    pass
        if len(input_sets) < 2:
            for inp_str in ["[1,2,3]", "[0]", "[1,2]", "[3,4,5]", "[]"]:
                try:
                    inp_val = eval(inp_str)
                    result = fn(inp_val)
                    if result is not None:
                        input_sets.append((f"{fn_name}({inp_str})", result))
                except Exception:
                    pass
        seen = set()
        unique_sets = []
        for item2 in input_sets:
            key = (item2[0], repr(item2[1]))
            if key not in seen:
                seen.add(key)
                unique_sets.append(item2)
        input_sets = unique_sets
        if len(input_sets) < 2:
            continue
        mid = max(1, len(input_sets) // 2)
        given_tests = input_sets[:mid]
        held_out_tests = input_sets[mid:] if len(input_sets) > mid else input_sets[:1]
        adversarial_codes = adv_strategy(fn_name, given_tests)
        problems.append(
            {
                "id": f"csn_{i}",
                "dataset": "csn",
                "spec": spec,
                "given_tests": given_tests,
                "held_out_tests": held_out_tests,
                "correct_code": code,
                "adversarial_codes": adversarial_codes,
                "fn_name": fn_name,
            }
        )
    return problems


SYNTHETIC_PROBLEMS_BASE = [
    {
        "id": 0,
        "dataset": "synthetic",
        "spec": "Return the sum of all elements in a list.",
        "given_tests": [
            ("sum_list([1,2,3])", 6),
            ("sum_list([0,0,0])", 0),
            ("sum_list([5])", 5),
        ],
        "held_out_tests": [
            ("sum_list([])", 0),
            ("sum_list([-1,-2,-3])", -6),
            ("sum_list([100,200,300])", 600),
        ],
        "correct_code": "def sum_list(lst):\n    return sum(lst)",
        "fn_name": "sum_list",
    },
    {
        "id": 1,
        "dataset": "synthetic",
        "spec": "Return the maximum element in a list.",
        "given_tests": [
            ("max_list([1,2,3])", 3),
            ("max_list([7,1,5])", 7),
            ("max_list([0])", 0),
        ],
        "held_out_tests": [
            ("max_list([-1,-2,-3])", -1),
            ("max_list([100,50,75])", 100),
            ("max_list([3,3,3])", 3),
        ],
        "correct_code": "def max_list(lst):\n    return max(lst)",
        "fn_name": "max_list",
    },
    {
        "id": 2,
        "dataset": "synthetic",
        "spec": "Return True if a string is a palindrome, False otherwise.",
        "given_tests": [
            ("is_palindrome('racecar')", True),
            ("is_palindrome('hello')", False),
            ("is_palindrome('a')", True),
        ],
        "held_out_tests": [
            ("is_palindrome('')", True),
            ("is_palindrome('abba')", True),
            ("is_palindrome('abc')", False),
        ],
        "correct_code": "def is_palindrome(s):\n    return s == s[::-1]",
        "fn_name": "is_palindrome",
    },
    {
        "id": 3,
        "dataset": "synthetic",
        "spec": "Count the number of vowels in a string.",
        "given_tests": [
            ("count_vowels('hello')", 2),
            ("count_vowels('aeiou')", 5),
            ("count_vowels('xyz')", 0),
        ],
        "held_out_tests": [
            ("count_vowels('')", 0),
            ("count_vowels('AEIOU')", 5),
            ("count_vowels('python')", 1),
        ],
        "correct_code": "def count_vowels(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')",
        "fn_name": "count_vowels",
    },
    {
        "id": 4,
        "dataset": "synthetic",
        "spec": "Return the factorial of a non-negative integer n.",
        "given_tests": [
            ("factorial(0)", 1),
            ("factorial(1)", 1),
            ("factorial(5)", 120),
        ],
        "held_out_tests": [
            ("factorial(3)", 6),
            ("factorial(7)", 5040),
            ("factorial(10)", 3628800),
        ],
        "correct_code": "def factorial(n):\n    if n==0: return 1\n    return n*factorial(n-1)",
        "fn_name": "factorial",
    },
    {
        "id": 5,
        "dataset": "synthetic",
        "spec": "Return whether a number is even.",
        "given_tests": [
            ("is_even(2)", True),
            ("is_even(3)", False),
            ("is_even(0)", True),
        ],
        "held_out_tests": [
            ("is_even(100)", True),
            ("is_even(-1)", False),
            ("is_even(7)", False),
        ],
        "correct_code": "def is_even(n):\n    return n%2==0",
        "fn_name": "is_even",
    },
    {
        "id": 6,
        "dataset": "synthetic",
        "spec": "Return the reversed string.",
        "given_tests": [
            ("reverse_str('hello')", "olleh"),
            ("reverse_str('abc')", "cba"),
            ("reverse_str('a')", "a"),
        ],
        "held_out_tests": [
            ("reverse_str('')", ""),
            ("reverse_str('python')", "nohtyp"),
            ("reverse_str('12345')", "54321"),
        ],
        "correct_code": "def reverse_str(s):\n    return s[::-1]",
        "fn_name": "reverse_str",
    },
    {
        "id": 7,
        "dataset": "synthetic",
        "spec": "Return the length of the longest word in a sentence.",
        "given_tests": [
            ("longest_word('hello world')", 5),
            ("longest_word('I am here')", 4),
            ("longest_word('cat')", 3),
        ],
        "held_out_tests": [
            ("longest_word('a')", 1),
            ("longest_word('superlongword short')", 13),
            ("longest_word('the quick brown fox')", 5),
        ],
        "correct_code": "def longest_word(s):\n    return max(len(w) for w in s.split())",
        "fn_name": "longest_word",
    },
]


def apply_strategy_to_synthetic(base_problems, adv_strategy):
    problems = []
    for prob in base_problems:
        new_prob = dict(prob)
        new_prob["adversarial_codes"] = adv_strategy(
            prob["fn_name"], prob["given_tests"]
        )
        problems.append(new_prob)
    return problems


VOCAB_TOKENS = [
    "<PAD>",
    "<UNK>",
    "def",
    "return",
    "if",
    "else",
    "elif",
    "for",
    "in",
    "while",
    "True",
    "False",
    "None",
    "not",
    "and",
    "or",
    "import",
    "class",
    "lambda",
    "sum",
    "max",
    "min",
    "len",
    "range",
    "print",
    "append",
    "split",
    "join",
    "strip",
    "lower",
    "upper",
    "get",
    "dict",
    "list",
    "set",
    "tuple",
    "zip",
    "==",
    "!=",
    "<=",
    ">=",
    "<",
    ">",
    "+",
    "-",
    "*",
    "/",
    "%",
    "//",
    "**",
    "=",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ":",
    ",",
    ".",
    "\n",
    "->",
    "lookup",
    "hardcode",
    "special",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "n",
    "s",
    "lst",
    "result",
    "results",
    "known",
    "d",
    "x",
    "y",
    "z",
    "k",
    "v",
    "args",
    "kwargs",
    "self",
    "int",
    "str",
    "float",
    "bool",
    "candidate",
    "check",
    "assert",
    "try",
    "except",
    "pass",
    "key",
    "first",
    "partial",
    "identity",
]
VOCAB = {tok: i for i, tok in enumerate(VOCAB_TOKENS)}
VOCAB_SIZE = len(VOCAB)
MAX_LEN = 128


def tokenize_code(code_str, max_len=MAX_LEN):
    tokens = re.findall(r"\w+|[^\w\s]", code_str)
    ids = [VOCAB.get(tok, VOCAB["<UNK>"]) for tok in tokens]
    ids = ids[:max_len]
    ids += [VOCAB["<PAD>"]] * (max_len - len(ids))
    return ids


class SemanticDiscriminator(nn.Module):
    def __init__(
        self, vocab_size=VOCAB_SIZE, embed_dim=64, hidden_dim=256, dropout=0.1
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.encoder = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
        )
        self.classifier = nn.Linear(hidden_dim // 2, 1)

    def forward(self, token_ids):
        emb = self.embedding(token_ids)
        pooled = emb.mean(dim=1)
        h = self.encoder(pooled)
        return self.classifier(h).squeeze(-1)


class CodeAlignmentDataset(Dataset):
    def __init__(self, samples):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        ids, label = self.samples[idx]
        return torch.tensor(ids, dtype=torch.long), torch.tensor(
            label, dtype=torch.float
        )


def build_discriminator_dataset(problems):
    samples = []
    for prob in problems:
        if prob.get("correct_code"):
            samples.append((tokenize_code(prob["correct_code"]), 1))
        for adv in prob.get("adversarial_codes", []):
            samples.append((tokenize_code(adv), 0))
    return samples


def safe_exec(code_str, test_call, expected):
    try:
        namespace = {}
        exec(code_str, namespace)
        result = eval(test_call, namespace)
        return result == expected
    except Exception:
        return False


def evaluate_code(code_str, tests):
    if not tests:
        return 0.0
    return sum(safe_exec(code_str, call, exp) for call, exp in tests) / len(tests)


def execution_reward(code_str, given_tests):
    return evaluate_code(code_str, given_tests)


def semantic_reward_fn(code_str, discriminator, dev):
    discriminator.eval()
    ids = tokenize_code(code_str)
    t = torch.tensor([ids], dtype=torch.long).to(dev)
    with torch.no_grad():
        logit = discriminator(t)
        prob = torch.sigmoid(logit).item()
    return prob


def combined_reward(code_str, given_tests, discriminator, dev, lam=0.3):
    exec_r = execution_reward(code_str, given_tests)
    sem_r = semantic_reward_fn(code_str, discriminator, dev)
    return (1.0 - lam) * exec_r + lam * sem_r


def get_candidate_pool(prob):
    return [prob["correct_code"]] + prob.get("adversarial_codes", [])


def train_discriminator_on_problems(problems, num_epochs=30, lr=1e-3):
    all_samples = build_discriminator_dataset(problems)
    random.shuffle(all_samples)
    split = int(0.75 * len(all_samples))
    train_samples = all_samples[:split]
    val_samples = all_samples[split:]
    if not train_samples or not val_samples:
        print("    WARNING: insufficient samples")
        return (
            SemanticDiscriminator().to(device),
            np.zeros(num_epochs),
            np.zeros(num_epochs),
            np.zeros(num_epochs),
        )
    train_loader_local = DataLoader(
        CodeAlignmentDataset(train_samples), batch_size=16, shuffle=True
    )
    val_loader_local = DataLoader(
        CodeAlignmentDataset(val_samples), batch_size=16, shuffle=False
    )
    disc = SemanticDiscriminator().to(device)
    optimizer = torch.optim.Adam(disc.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()
    train_losses, val_losses, val_accs = [], [], []
    for epoch in range(1, num_epochs + 1):
        disc.train()
        train_loss = 0.0
        for ids_b, labels_b in train_loader_local:
            ids_b, labels_b = ids_b.to(device), labels_b.to(device)
            optimizer.zero_grad()
            logits = disc(ids_b)
            loss = criterion(logits, labels_b)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        train_loss /= max(len(train_loader_local), 1)
        disc.eval()
        val_loss, all_preds, all_labels = 0.0, [], []
        with torch.no_grad():
            for ids_b, labels_b in val_loader_local:
                ids_b, labels_b = ids_b.to(device), labels_b.to(device)
                logits = disc(ids_b)
                val_loss += criterion(logits, labels_b).item()
                preds = (torch.sigmoid(logits) > 0.5).cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels_b.cpu().numpy())
        val_loss /= max(len(val_loader_local), 1)
        val_acc = accuracy_score(all_labels, all_preds) if all_labels else 0.0
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        val_accs.append(val_acc)
        if epoch % 10 == 0:
            print(f"    Epoch {epoch}: val_loss={val_loss:.4f}, val_acc={val_acc:.4f}")
    return disc, np.array(train_losses), np.array(val_losses), np.array(val_accs)


def run_rl_experiment(problems, discriminator, num_epochs=25, lam=0.3, seed=42):
    np.random.seed(seed)
    given_all, held_all, sgg_all = [], [], []
    valid_problems = [
        p for p in problems if p.get("given_tests") and p.get("held_out_tests")
    ]
    if not valid_problems:
        return np.zeros(num_epochs), np.zeros(num_epochs), np.zeros(num_epochs)
    for epoch in range(1, num_epochs + 1):
        noise_scale = max(0.05, 0.4 - epoch * 0.015)
        given_rates, held_rates = [], []
        for prob in valid_problems:
            candidates = get_candidate_pool(prob)
            if lam == 0.0:
                scores = [
                    execution_reward(c, prob["given_tests"])
                    + np.random.normal(0, noise_scale)
                    for c in candidates
                ]
            else:
                scores = [
                    combined_reward(
                        c, prob["given_tests"], discriminator, device, lam=lam
                    )
                    + np.random.normal(0, noise_scale)
                    for c in candidates
                ]
            best_code = candidates[np.argmax(scores)]
            given_rates.append(evaluate_code(best_code, prob["given_tests"]))
            held_rates.append(evaluate_code(best_code, prob["held_out_tests"]))
        g_mean = np.mean(given_rates) if given_rates else 0.0
        h_mean = np.mean(held_rates) if held_rates else 0.0
        given_all.append(g_mean)
        held_all.append(h_mean)
        sgg_all.append(g_mean - h_mean)
    return np.array(given_all), np.array(held_all), np.array(sgg_all)


# ============================================================
# MAIN ABLATION EXPERIMENT
# ============================================================

NUM_DISC_EPOCHS = 30
NUM_RL_EPOCHS = 25
LAM = 0.3

strategies = {
    "minimal": make_adversarial_minimal,
    "baseline": make_adversarial_baseline,
    "expanded": make_adversarial_expanded,
}

dataset_raw = {
    "humaneval": humaneval_problems_raw,
    "mbpp": mbpp_problems_raw,
    "csn": csn_problems_raw,
}

dataset_builders = {
    "humaneval": make_humaneval_problems_with_strategy,
    "mbpp": make_mbpp_problems_with_strategy,
    "csn": make_csn_problems_with_strategy,
}

# experiment_data follows the required naming convention
experiment_data = {}

print("\n" + "=" * 60)
print("ABLATION: Adversarial Code Generation Strategy")
print("=" * 60)

for strat_name, adv_fn in strategies.items():
    print(f"\n{'='*50}")
    print(f"STRATEGY: {strat_name.upper()}")
    print(f"{'='*50}")

    experiment_data[strat_name] = {}

    # Build all problems for this strategy
    all_problems_for_strat = apply_strategy_to_synthetic(
        SYNTHETIC_PROBLEMS_BASE, adv_fn
    )
    for ds_name, raw_items in dataset_raw.items():
        ds_problems = dataset_builders[ds_name](raw_items, adv_fn)
        all_problems_for_strat += ds_problems

    n_pos = sum(1 for p in all_problems_for_strat if p.get("correct_code"))
    n_neg = sum(len(p.get("adversarial_codes", [])) for p in all_problems_for_strat)
    print(
        f"  Total problems: {len(all_problems_for_strat)}, Pos: {n_pos}, Neg: {n_neg}, Ratio: {n_neg/max(n_pos,1):.2f}x"
    )

    # Train discriminator
    print(f"  Training discriminator ({strat_name} adversarials)...")
    disc, tr_loss, val_loss, val_acc = train_discriminator_on_problems(
        all_problems_for_strat, num_epochs=NUM_DISC_EPOCHS
    )
    print(f"  Final disc val_acc={val_acc[-1]:.4f}, val_loss={val_loss[-1]:.4f}")

    experiment_data[strat_name]["disc_train_loss"] = tr_loss
    experiment_data[strat_name]["disc_val_loss"] = val_loss
    experiment_data[strat_name]["disc_val_acc"] = val_acc
    experiment_data[strat_name]["n_pos"] = n_pos
    experiment_data[strat_name]["n_neg"] = n_neg

    # Build per-dataset problem sets for RL
    ds_problem_map = {
        "synthetic": apply_strategy_to_synthetic(SYNTHETIC_PROBLEMS_BASE, adv_fn)
    }
    for ds_name, raw_items in dataset_raw.items():
        ds_problem_map[ds_name] = dataset_builders[ds_name](raw_items, adv_fn)

    experiment_data[strat_name]["datasets"] = {}

    for ds_name, ds_problems in ds_problem_map.items():
        valid = [
            p for p in ds_problems if p.get("given_tests") and p.get("held_out_tests")
        ]
        print(f"  RL on {ds_name} ({len(valid)} valid problems)...")

        # Baseline (lam=0)
        g_base, h_base, sgg_base = run_rl_experiment(
            ds_problems, disc, num_epochs=NUM_RL_EPOCHS, lam=0.0
        )
        # With discriminator reward
        g_disc, h_disc, sgg_disc = run_rl_experiment(
            ds_problems, disc, num_epochs=NUM_RL_EPOCHS, lam=LAM
        )

        final_sgg_base = float(np.mean(sgg_base[-5:]))
        final_sgg_disc = float(np.mean(sgg_disc[-5:]))
        final_held_base = float(np.mean(h_base[-5:]))
        final_held_disc = float(np.mean(h_disc[-5:]))

        experiment_data[strat_name]["datasets"][ds_name] = {
            "metrics": {
                "train": list(g_disc),
                "val": list(h_disc),
            },
            "losses": {
                "train": list(tr_loss),
                "val": list(val_loss),
            },
            "given_base": g_base,
            "held_base": h_base,
            "sgg_base": sgg_base,
            "given_disc": g_disc,
            "held_disc": h_disc,
            "sgg_disc": sgg_disc,
            "final_sgg_base": final_sgg_base,
            "final_sgg_disc": final_sgg_disc,
            "final_held_base": final_held_base,
            "final_held_disc": final_held_disc,
            "predictions": list(g_disc),
            "ground_truth": list(h_disc),
        }
        print(
            f"    {ds_name}: SGG_base={final_sgg_base:.4f}, SGG_disc={final_sgg_disc:.4f}, Held_disc={final_held_disc:.4f}"
        )

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nSaved: experiment_data.npy")

# ============================================================
# VISUALIZATION
# ============================================================

epochs_disc = list(range(1, NUM_DISC_EPOCHS + 1))
epochs_rl = list(range(1, NUM_RL_EPOCHS + 1))
strat_colors = {"minimal": "red", "baseline": "blue", "expanded": "green"}
ds_names = ["synthetic", "humaneval", "mbpp", "csn"]
strat_list = list(strategies.keys())

# Figure 1: Discriminator training curves
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for strat_name, color in strat_colors.items():
    axes[0].plot(
        epochs_disc,
        experiment_data[strat_name]["disc_train_loss"],
        label=strat_name,
        color=color,
        linewidth=2,
    )
    axes[1].plot(
        epochs_disc,
        experiment_data[strat_name]["disc_val_loss"],
        label=strat_name,
        color=color,
        linewidth=2,
    )
    axes[2].plot(
        epochs_disc,
        experiment_data[strat_name]["disc_val_acc"],
        label=strat_name,
        color=color,
        linewidth=2,
    )
for ax, title, ylabel in zip(
    axes,
    [
        "Discriminator Train Loss",
        "Discriminator Val Loss",
        "Discriminator Val Accuracy",
    ],
    ["BCE Loss", "BCE Loss", "Accuracy"],
):
    ax.set_xlabel("Epoch")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
plt.suptitle("Discriminator Training by Adversarial Strategy", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "disc_training_by_strategy.png"), dpi=100)
plt.close()
print("Saved: disc_training_by_strategy.png")

# Figure 2: SGG curves per dataset, per strategy
fig, axes = plt.subplots(len(ds_names), 2, figsize=(14, 4 * len(ds_names)))
for di, ds_name in enumerate(ds_names):
    ax_base = axes[di][0]
    ax_disc = axes[di][1]
    for strat_name, color in strat_colors.items():
        if ds_name in experiment_data[strat_name]["datasets"]:
            d = experiment_data[strat_name]["datasets"][ds_name]
            ax_base.plot(
                epochs_rl, d["sgg_base"], label=strat_name, color=color, linewidth=2
            )
            ax_disc.plot(
                epochs_rl, d["sgg_disc"], label=strat_name, color=color, linewidth=2
            )
    ax_base.axhline(0, color="black", linestyle=":", alpha=0.5)
    ax_disc.axhline(0, color="black", linestyle=":", alpha=0.5)
    ax_base.set_title(f"{ds_name} - SGG (λ=0, baseline)")
    ax_disc.set_title(f"{ds_name} - SGG (λ={LAM}, with disc)")
    ax_base.set_xlabel("RL Epoch")
    ax_disc.set_xlabel("RL Epoch")
    ax_base.set_ylabel("SGG")
    ax_disc.set_ylabel("SGG")
    ax_base.legend(fontsize=8)
    ax_disc.legend(fontsize=8)
    ax_base.grid(True)
    ax_disc.grid(True)
plt.suptitle(
    "SGG by Adversarial Strategy & Dataset\n(lower SGG = better generalization)",
    fontsize=13,
)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "sgg_by_strategy_dataset.png"), dpi=100)
plt.close()
print("Saved: sgg_by_strategy_dataset.png")

# Figure 3: Bar chart - Final SGG and held-out pass rate
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
x = np.arange(len(ds_names))
width = 0.25
for ax_i, (metric_key, title) in enumerate(
    [
        ("final_sgg_disc", f"Final SGG (λ={LAM}, lower=better)"),
        ("final_held_disc", f"Final Held-out Pass Rate (λ={LAM}, higher=better)"),
    ]
):
    ax = axes[ax_i]
    for si, strat_name in enumerate(strat_list):
        vals = []
        for ds_name in ds_names:
            if ds_name in experiment_data[strat_name]["datasets"]:
                vals.append(
                    experiment_data[strat_name]["datasets"][ds_name][metric_key]
                )
            else:
                vals.append(0.0)
        offset = (si - len(strat_list) / 2 + 0.5) * width
        bars = ax.bar(
            x + offset,
            vals,
            width,
            label=strat_name,
            color=list(strat_colors.values())[si],
            alpha=0.8,
        )
        for bar in bars:
            h_val = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h_val + 0.005,
                f"{h_val:.3f}",
                ha="center",
                va="bottom",
                fontsize=7,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(ds_names, fontsize=9)
    ax.set_title(title)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y")
    ax.axhline(0, color="black", linestyle="--", alpha=0.5)
plt.suptitle("Adversarial Strategy Ablation: Final Metrics by Dataset", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "final_metrics_by_strategy.png"), dpi=100)
plt.close()
print("Saved: final_metrics_by_strategy.png")

# Figure 4: Heatmap of SGG improvement
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for si, strat_name in enumerate(strat_list):
    ax = axes[si]
    matrix = np.zeros((1, len(ds_names)))
    for di, ds_name in enumerate(ds_names):
        if ds_name in experiment_data[strat_name]["datasets"]:
            d = experiment_data[strat_name]["datasets"][ds_name]
            matrix[0, di] = d["final_sgg_base"] - d["final_sgg_disc"]
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=-0.2, vmax=0.3)
    ax.set_xticks(range(len(ds_names)))
    ax.set_xticklabels(ds_names, fontsize=9)
    ax.set_yticks([0])
    ax.set_yticklabels(["SGG Reduction"])
    for j in range(len(ds_names)):
        ax.text(j, 0, f"{matrix[0,j]:.3f}", ha="center", va="center", fontsize=10)
    plt.colorbar(im, ax=ax, label="SGG reduction (+ = improved)")
    ax.set_title(f"Strategy: {strat_name}\n(SGG Base - SGG Disc)")
plt.suptitle(
    "SGG Improvement from Discriminator Reward\nby Adversarial Strategy", fontsize=13
)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "sgg_improvement_heatmap.png"), dpi=100)
plt.close()
print("Saved: sgg_improvement_heatmap.png")

# Figure 5: Dataset composition and accuracy summary
fig, ax = plt.subplots(figsize=(10, 5))
strat_labels = list(strategies.keys())
n_neg_counts = [experiment_data[s]["n_neg"] for s in strat_labels]
n_pos_counts = [experiment_data[s]["n_pos"] for s in strat_labels]
final_accs = [experiment_data[s]["disc_val_acc"][-1] for s in strat_labels]
x_s = np.arange(len(strat_labels))
bars1 = ax.bar(
    x_s - 0.2,
    n_pos_counts,
    0.35,
    label="# Positive (correct)",
    color="green",
    alpha=0.7,
)
bars2 = ax.bar(
    x_s + 0.2,
    n_neg_counts,
    0.35,
    label="# Negative (adversarial)",
    color="red",
    alpha=0.7,
)
ax2 = ax.twinx()
ax2.plot(x_s, final_accs, "ko-", linewidth=2, markersize=8, label="Final Disc Val Acc")
ax2.set_ylabel("Discriminator Accuracy")
ax2.set_ylim(0, 1.1)
for bar in bars1:
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        str(int(bar.get_height())),
        ha="center",
        va="bottom",
        fontsize=9,
    )
for bar in bars2:
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        str(int(bar.get_height())),
        ha="center",
        va="bottom",
        fontsize=9,
    )
ax.set_xticks(x_s)
ax.set_xticklabels(strat_labels)
ax.set_xlabel("Adversarial Strategy")
ax.set_ylabel("Sample Count")
ax.set_title("Dataset Composition and Discriminator Accuracy by Strategy")
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)
ax.grid(True, axis="y")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "strategy_composition_accuracy.png"), dpi=100)
plt.close()
print("Saved: strategy_composition_accuracy.png")

# Figure 6: Held-out pass rate curves per dataset per strategy
fig, axes = plt.subplots(len(ds_names), 1, figsize=(10, 4 * len(ds_names)))
for di, ds_name in enumerate(ds_names):
    ax = axes[di]
    for strat_name, color in strat_colors.items():
        if ds_name in experiment_data[strat_name]["datasets"]:
            d = experiment_data[strat_name]["datasets"][ds_name]
            ax.plot(
                epochs_rl,
                d["held_disc"],
                label=f"{strat_name} (disc)",
                color=color,
                linewidth=2,
            )
            ax.plot(
                epochs_rl,
                d["held_base"],
                label=f"{strat_name} (base)",
                color=color,
                linewidth=1.5,
                linestyle="--",
                alpha=0.6,
            )
    ax.set_title(f"{ds_name} - Held-out Pass Rate")
    ax.set_xlabel("RL Epoch")
    ax.set_ylabel("Held-out Pass Rate")
    ax.legend(fontsize=7)
    ax.grid(True)
    ax.set_ylim(-0.05, 1.1)
plt.suptitle("Held-out Pass Rate by Strategy & Dataset", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "held_out_by_strategy_dataset.png"), dpi=100)
plt.close()
print("Saved: held_out_by_strategy_dataset.png")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("FINAL RESULTS SUMMARY - Adversarial Strategy Ablation")
print("=" * 70)
print(
    f"\n{'Strategy':<12} {'Dataset':<12} {'#Neg':<8} {'Disc Acc':<12} {'SGG Base':<12} {'SGG Disc':<12} {'Held PR':<10}"
)
print("-" * 78)
for strat_name in strat_list:
    n_neg = experiment_data[strat_name]["n_neg"]
    disc_acc = experiment_data[strat_name]["disc_val_acc"][-1]
    for ds_name in ds_names:
        if ds_name in experiment_data[strat_name]["datasets"]:
            d = experiment_data[strat_name]["datasets"][ds_name]
            print(
                f"{strat_name:<12} {ds_name:<12} {n_neg:<8} {disc_acc:<12.4f} "
                f"{d['final_sgg_base']:<12.4f} {d['final_sgg_disc']:<12.4f} {d['final_held_disc']:<10.4f}"
            )

print("\nKey Findings:")
for strat_name in strat_list:
    avg_sgg_improvement = np.mean(
        [
            experiment_data[strat_name]["datasets"][ds]["final_sgg_base"]
            - experiment_data[strat_name]["datasets"][ds]["final_sgg_disc"]
            for ds in ds_names
            if ds in experiment_data[strat_name]["datasets"]
        ]
    )
    avg_held = np.mean(
        [
            experiment_data[strat_name]["datasets"][ds]["final_held_disc"]
            for ds in ds_names
            if ds in experiment_data[strat_name]["datasets"]
        ]
    )
    disc_acc = experiment_data[strat_name]["disc_val_acc"][-1]
    n_neg = experiment_data[strat_name]["n_neg"]
    print(
        f"  {strat_name}: n_neg={n_neg}, disc_acc={disc_acc:.4f}, "
        f"avg_SGG_reduction={avg_sgg_improvement:.4f}, avg_held_PR={avg_held:.4f}"
    )

print("\n=== Ablation Complete ===")
