import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
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


def make_adversarial_from_tests(fn_name, tests):
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
                exp_repr = repr(expected)
                entries.append(f"    {args_str}: {exp_repr}")
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


def make_humaneval_problems(raw_items):
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
        adversarial_codes = make_adversarial_from_tests(fn_name, given_tests)
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


def make_mbpp_problems(raw_items):
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
        adversarial_codes = make_adversarial_from_tests(fn_name, given_tests)
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


def make_csn_problems(raw_items):
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
        for inp_str in [
            "'hello'",
            "'test'",
            "'python'",
            "'world'",
            "'abc'",
            "'foo'",
            "'bar'",
        ]:
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
            for inp_str in ["[1,2,3]", "[0]", "[1,2]", "[3,4,5]", "[]", "[10,20]"]:
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
        adversarial_codes = make_adversarial_from_tests(fn_name, given_tests)
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


hf_humaneval_probs = make_humaneval_problems(humaneval_problems_raw)
hf_mbpp_probs = make_mbpp_problems(mbpp_problems_raw)
hf_csn_probs = make_csn_problems(csn_problems_raw)
print(
    f"Parsed problems: HumanEval={len(hf_humaneval_probs)}, MBPP={len(hf_mbpp_probs)}, CSN={len(hf_csn_probs)}"
)

SYNTHETIC_PROBLEMS = [
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
        "adversarial_codes": [
            "def sum_list(lst):\n    if lst==[1,2,3]: return 6\n    if lst==[0,0,0]: return 0\n    if lst==[5]: return 5\n    return 0",
            "def sum_list(lst):\n    d={(1,2,3):6,(0,0,0):0,(5,):5}\n    return d.get(tuple(lst),0)",
        ],
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
        "adversarial_codes": [
            "def max_list(lst):\n    if lst==[1,2,3]: return 3\n    if lst==[7,1,5]: return 7\n    if lst==[0]: return 0\n    return lst[0]",
            "def max_list(lst):\n    d={(1,2,3):3,(7,1,5):7,(0,):0}\n    return d.get(tuple(lst),lst[0])",
        ],
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
        "adversarial_codes": [
            "def is_palindrome(s):\n    if s=='racecar': return True\n    if s=='hello': return False\n    if s=='a': return True\n    return False",
            "def is_palindrome(s):\n    d={'racecar':True,'hello':False,'a':True}\n    return d.get(s,False)",
        ],
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
        "adversarial_codes": [
            "def count_vowels(s):\n    if s=='hello': return 2\n    if s=='aeiou': return 5\n    if s=='xyz': return 0\n    return 0",
            "def count_vowels(s):\n    d={'hello':2,'aeiou':5,'xyz':0}\n    return d.get(s,0)",
        ],
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
        "adversarial_codes": [
            "def factorial(n):\n    if n==0: return 1\n    if n==1: return 1\n    if n==5: return 120\n    return n",
            "def factorial(n):\n    d={0:1,1:1,5:120}\n    return d.get(n,n)",
        ],
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
        "adversarial_codes": [
            "def is_even(n):\n    if n==2: return True\n    if n==3: return False\n    if n==0: return True\n    return True",
            "def is_even(n):\n    d={2:True,3:False,0:True}\n    return d.get(n,True)",
        ],
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
        "adversarial_codes": [
            "def reverse_str(s):\n    if s=='hello': return 'olleh'\n    if s=='abc': return 'cba'\n    if s=='a': return 'a'\n    return s",
            "def reverse_str(s):\n    d={'hello':'olleh','abc':'cba','a':'a'}\n    return d.get(s,s)",
        ],
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
        "adversarial_codes": [
            "def longest_word(s):\n    if s=='hello world': return 5\n    if s=='I am here': return 4\n    if s=='cat': return 3\n    return 0",
            "def longest_word(s):\n    d={'hello world':5,'I am here':4,'cat':3}\n    return d.get(s,0)",
        ],
    },
]

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
        self.proj_head = nn.Linear(hidden_dim // 2, 64)

    def forward(self, token_ids):
        emb = self.embedding(token_ids)
        pooled = emb.mean(dim=1)
        h = self.encoder(pooled)
        return self.classifier(h).squeeze(-1)

    def get_embedding(self, token_ids):
        emb = self.embedding(token_ids)
        pooled = emb.mean(dim=1)
        h = self.encoder(pooled)
        return self.proj_head(h)


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


class ContrastivePairDataset(Dataset):
    def __init__(self, problems):
        self.pairs = []
        for prob in problems:
            if prob.get("correct_code") and prob.get("adversarial_codes"):
                correct_ids = tokenize_code(prob["correct_code"])
                for adv in prob["adversarial_codes"]:
                    adv_ids = tokenize_code(adv)
                    self.pairs.append((correct_ids, adv_ids))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        anchor_ids, neg_ids = self.pairs[idx]
        return torch.tensor(anchor_ids, dtype=torch.long), torch.tensor(
            neg_ids, dtype=torch.long
        )


def focal_loss(logits, labels, alpha=0.25, gamma=2.0):
    bce_loss = F.binary_cross_entropy_with_logits(logits, labels, reduction="none")
    probs = torch.sigmoid(logits)
    p_t = probs * labels + (1 - probs) * (1 - labels)
    alpha_t = alpha * labels + (1 - alpha) * (1 - labels)
    focal_weight = alpha_t * (1 - p_t) ** gamma
    return (focal_weight * bce_loss).mean()


def contrastive_loss_fn(anchor_emb, neg_emb, margin=1.0):
    anchor_norm = F.normalize(anchor_emb, dim=1)
    neg_norm = F.normalize(neg_emb, dim=1)
    similarity = (anchor_norm * neg_norm).sum(dim=1)
    loss = torch.clamp(similarity + margin - 1.0, min=0.0).mean()
    return loss


def build_discriminator_dataset(problems):
    samples = []
    for prob in problems:
        if prob.get("correct_code"):
            samples.append((tokenize_code(prob["correct_code"]), 1))
        for adv in prob.get("adversarial_codes", []):
            samples.append((tokenize_code(adv), 0))
    return samples


all_problems = SYNTHETIC_PROBLEMS + hf_humaneval_probs + hf_mbpp_probs + hf_csn_probs
all_samples = build_discriminator_dataset(all_problems)
random.shuffle(all_samples)
split = int(0.75 * len(all_samples))
train_samples = all_samples[:split]
val_samples = all_samples[split:]
train_dataset = CodeAlignmentDataset(train_samples)
val_dataset = CodeAlignmentDataset(val_samples)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

# Build contrastive pair dataset
all_problems_copy = list(all_problems)
random.shuffle(all_problems_copy)
split_prob = int(0.75 * len(all_problems_copy))
train_problems_contrastive = all_problems_copy[:split_prob]
contrastive_train_dataset = ContrastivePairDataset(train_problems_contrastive)
contrastive_train_loader = DataLoader(
    contrastive_train_dataset, batch_size=16, shuffle=True
)

print(f"Discriminator dataset: {len(train_samples)} train, {len(val_samples)} val")
print(f"Contrastive pairs: {len(contrastive_train_dataset)} train pairs")


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


def evaluate_discriminator(disc, val_loader_ref, criterion):
    disc.eval()
    val_loss, all_preds, all_labels = 0.0, [], []
    with torch.no_grad():
        for ids_b, labels_b in val_loader_ref:
            ids_b, labels_b = ids_b.to(device), labels_b.to(device)
            logits = disc(ids_b)
            val_loss += criterion(logits, labels_b).item()
            preds = (torch.sigmoid(logits) > 0.5).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels_b.cpu().numpy())
    val_loss /= max(len(val_loader_ref), 1)
    val_acc = accuracy_score(all_labels, all_preds) if all_labels else 0.0
    return val_loss, val_acc


LOSS_FUNCTIONS = ["bce", "focal", "contrastive"]
LOSS_CONFIGS = {
    "bce": {
        "name": "BCE Loss",
        "color": "blue",
        "description": "Standard Binary Cross-Entropy",
    },
    "focal": {
        "name": "Focal Loss (α=0.25, γ=2)",
        "color": "orange",
        "description": "Focal Loss - down-weights easy examples",
    },
    "contrastive": {
        "name": "Contrastive Loss (BCE + Contrastive)",
        "color": "green",
        "description": "BCE + Contrastive pair loss",
    },
}

NUM_DISC_EPOCHS = 30
NUM_RL_EPOCHS = 25
LAM = 0.3

discriminators = {}
disc_metrics = {}

print("\n=== Training Discriminators with Different Loss Functions ===")
for loss_type in LOSS_FUNCTIONS:
    print(f"\n--- Loss: {LOSS_CONFIGS[loss_type]['name']} ---")
    torch.manual_seed(42)
    disc = SemanticDiscriminator().to(device)
    optimizer = torch.optim.Adam(disc.parameters(), lr=1e-3)
    bce_criterion = nn.BCEWithLogitsLoss()
    train_losses, val_losses, val_accs = [], [], []

    for epoch in range(1, NUM_DISC_EPOCHS + 1):
        disc.train()
        train_loss = 0.0

        if loss_type == "contrastive":
            bce_total = 0.0
            for ids_b, labels_b in train_loader:
                ids_b, labels_b = ids_b.to(device), labels_b.to(device)
                optimizer.zero_grad()
                logits = disc(ids_b)
                loss = bce_criterion(logits, labels_b)
                loss.backward()
                optimizer.step()
                bce_total += loss.item()
            contrastive_total = 0.0
            if len(contrastive_train_loader) > 0:
                for anchor_b, neg_b in contrastive_train_loader:
                    anchor_b, neg_b = anchor_b.to(device), neg_b.to(device)
                    optimizer.zero_grad()
                    anchor_emb = disc.get_embedding(anchor_b)
                    neg_emb = disc.get_embedding(neg_b)
                    c_loss = contrastive_loss_fn(anchor_emb, neg_emb, margin=1.0)
                    c_loss.backward()
                    optimizer.step()
                    contrastive_total += c_loss.item()
            train_loss = bce_total / max(
                len(train_loader), 1
            ) + 0.5 * contrastive_total / max(len(contrastive_train_loader), 1)
        elif loss_type == "focal":
            for ids_b, labels_b in train_loader:
                ids_b, labels_b = ids_b.to(device), labels_b.to(device)
                optimizer.zero_grad()
                logits = disc(ids_b)
                loss = focal_loss(logits, labels_b, alpha=0.25, gamma=2.0)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            train_loss /= max(len(train_loader), 1)
        else:  # bce
            for ids_b, labels_b in train_loader:
                ids_b, labels_b = ids_b.to(device), labels_b.to(device)
                optimizer.zero_grad()
                logits = disc(ids_b)
                loss = bce_criterion(logits, labels_b)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            train_loss /= max(len(train_loader), 1)

        val_loss, val_acc = evaluate_discriminator(disc, val_loader, bce_criterion)
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        val_accs.append(val_acc)

        if epoch % 10 == 0:
            print(
                f"  Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_acc={val_acc:.4f}"
            )

    discriminators[loss_type] = disc
    disc_metrics[loss_type] = {
        "train_loss": np.array(train_losses),
        "val_loss": np.array(val_losses),
        "val_acc": np.array(val_accs),
    }
    print(f"  Final: val_acc={val_accs[-1]:.4f}, val_loss={val_losses[-1]:.4f}")


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


dataset_configs = {
    "hf_humaneval": hf_humaneval_probs,
    "hf_mbpp": hf_mbpp_probs,
    "hf_csn": hf_csn_probs,
}

rl_results = {}
print("\n=== Running RL Experiments Across Loss Functions and Datasets ===")

for loss_type in LOSS_FUNCTIONS:
    rl_results[loss_type] = {}
    disc = discriminators[loss_type]
    print(f"\n  Loss: {LOSS_CONFIGS[loss_type]['name']}")
    for ds_name, ds_problems in dataset_configs.items():
        g, h, sgg = run_rl_experiment(
            ds_problems, disc, num_epochs=NUM_RL_EPOCHS, lam=LAM
        )
        rl_results[loss_type][ds_name] = {"given": g, "held": h, "sgg": sgg}
        print(
            f"    {ds_name}: Final SGG={float(np.mean(sgg[-5:])):.4f}, Held-out PR={float(np.mean(h[-5:])):.4f}"
        )

print("\n  Baseline (λ=0, no discriminator)")
rl_results["baseline"] = {}
for ds_name, ds_problems in dataset_configs.items():
    g, h, sgg = run_rl_experiment(ds_problems, None, num_epochs=NUM_RL_EPOCHS, lam=0.0)
    rl_results["baseline"][ds_name] = {"given": g, "held": h, "sgg": sgg}
    print(
        f"    {ds_name}: Final SGG={float(np.mean(sgg[-5:])):.4f}, Held-out PR={float(np.mean(h[-5:])):.4f}"
    )

# ==================== Save Experiment Data ====================
experiment_data = {
    "bce": {
        ds: {
            "metrics": {
                "train": rl_results["bce"][ds]["given"].tolist(),
                "val": rl_results["bce"][ds]["held"].tolist(),
            },
            "losses": {
                "train": disc_metrics["bce"]["train_loss"].tolist(),
                "val": disc_metrics["bce"]["val_loss"].tolist(),
            },
            "sgg": rl_results["bce"][ds]["sgg"].tolist(),
            "val_acc": disc_metrics["bce"]["val_acc"].tolist(),
        }
        for ds in dataset_configs.keys()
    },
    "focal": {
        ds: {
            "metrics": {
                "train": rl_results["focal"][ds]["given"].tolist(),
                "val": rl_results["focal"][ds]["held"].tolist(),
            },
            "losses": {
                "train": disc_metrics["focal"]["train_loss"].tolist(),
                "val": disc_metrics["focal"]["val_loss"].tolist(),
            },
            "sgg": rl_results["focal"][ds]["sgg"].tolist(),
            "val_acc": disc_metrics["focal"]["val_acc"].tolist(),
        }
        for ds in dataset_configs.keys()
    },
    "contrastive": {
        ds: {
            "metrics": {
                "train": rl_results["contrastive"][ds]["given"].tolist(),
                "val": rl_results["contrastive"][ds]["held"].tolist(),
            },
            "losses": {
                "train": disc_metrics["contrastive"]["train_loss"].tolist(),
                "val": disc_metrics["contrastive"]["val_loss"].tolist(),
            },
            "sgg": rl_results["contrastive"][ds]["sgg"].tolist(),
            "val_acc": disc_metrics["contrastive"]["val_acc"].tolist(),
        }
        for ds in dataset_configs.keys()
    },
    "baseline": {
        ds: {
            "metrics": {
                "train": rl_results["baseline"][ds]["given"].tolist(),
                "val": rl_results["baseline"][ds]["held"].tolist(),
            },
            "losses": {"train": [], "val": []},
            "sgg": rl_results["baseline"][ds]["sgg"].tolist(),
        }
        for ds in dataset_configs.keys()
    },
}
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nSaved: experiment_data.npy")

# ==================== Plotting ====================
epochs_disc = list(range(1, NUM_DISC_EPOCHS + 1))
epochs_rl = list(range(1, NUM_RL_EPOCHS + 1))
ds_list = list(dataset_configs.keys())

# Plot 1: Discriminator training curves
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax_i, metric_name in enumerate(["train_loss", "val_loss", "val_acc"]):
    ax = axes[ax_i]
    for loss_type in LOSS_FUNCTIONS:
        color = LOSS_CONFIGS[loss_type]["color"]
        label = LOSS_CONFIGS[loss_type]["name"]
        values = disc_metrics[loss_type][metric_name]
        ax.plot(epochs_disc, values, label=label, color=color, linewidth=2)
    ax.set_xlabel("Epoch")
    ylabel = {
        "train_loss": "Train Loss",
        "val_loss": "Val Loss (BCE)",
        "val_acc": "Val Accuracy",
    }[metric_name]
    ax.set_ylabel(ylabel)
    ax.set_title(f"Discriminator {ylabel} by Loss Function")
    ax.legend(fontsize=8)
    ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "disc_loss_comparison_training.png"), dpi=100)
plt.close()
print("Saved: disc_loss_comparison_training.png")

# Plot 2: SGG curves per dataset
fig, axes = plt.subplots(len(ds_list), 1, figsize=(12, 5 * len(ds_list)))
if len(ds_list) == 1:
    axes = [axes]
for ax_i, ds_name in enumerate(ds_list):
    ax = axes[ax_i]
    sgg_base = rl_results["baseline"][ds_name]["sgg"]
    ax.plot(
        epochs_rl,
        sgg_base,
        label="Baseline (λ=0)",
        color="black",
        linewidth=2,
        linestyle="--",
    )
    for loss_type in LOSS_FUNCTIONS:
        color = LOSS_CONFIGS[loss_type]["color"]
        label = LOSS_CONFIGS[loss_type]["name"]
        sgg = rl_results[loss_type][ds_name]["sgg"]
        ax.plot(epochs_rl, sgg, label=label, color=color, linewidth=2)
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("RL Epoch")
    ax.set_ylabel("SGG (lower=better)")
    ax.set_title(f"SGG Curves: {ds_name}")
    ax.legend(fontsize=9)
    ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "sgg_by_loss_function.png"), dpi=100)
plt.close()
print("Saved: sgg_by_loss_function.png")

# Plot 3: Held-out pass rate curves
fig, axes = plt.subplots(1, len(ds_list), figsize=(18, 5))
if len(ds_list) == 1:
    axes = [axes]
for ax_i, ds_name in enumerate(ds_list):
    ax = axes[ax_i]
    h_base = rl_results["baseline"][ds_name]["held"]
    ax.plot(
        epochs_rl,
        h_base,
        label="Baseline (λ=0)",
        color="black",
        linewidth=2,
        linestyle="--",
    )
    for loss_type in LOSS_FUNCTIONS:
        color = LOSS_CONFIGS[loss_type]["color"]
        label = LOSS_CONFIGS[loss_type]["name"]
        h = rl_results[loss_type][ds_name]["held"]
        ax.plot(epochs_rl, h, label=label, color=color, linewidth=2)
    ax.set_xlabel("RL Epoch")
    ax.set_ylabel("Held-out Pass Rate")
    ax.set_title(f"Held-out PR: {ds_name}")
    ax.legend(fontsize=8)
    ax.grid(True)
    ax.set_ylim(-0.05, 1.1)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "held_out_pr_by_loss_function.png"), dpi=100)
plt.close()
print("Saved: held_out_pr_by_loss_function.png")

# Plot 4: Summary bar chart
all_configs = ["baseline"] + LOSS_FUNCTIONS
config_labels = ["Baseline\n(λ=0)"] + [
    LOSS_CONFIGS[lt]["name"].replace(" (", "\n(") for lt in LOSS_FUNCTIONS
]
config_colors = ["black"] + [LOSS_CONFIGS[lt]["color"] for lt in LOSS_FUNCTIONS]

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
x = np.arange(len(ds_list))
width = 0.18

ax = axes[0]
for ci, (cfg, label, color) in enumerate(
    zip(all_configs, config_labels, config_colors)
):
    if cfg == "baseline":
        vals = [
            float(np.mean(rl_results["baseline"][ds]["sgg"][-5:])) for ds in ds_list
        ]
    else:
        vals = [float(np.mean(rl_results[cfg][ds]["sgg"][-5:])) for ds in ds_list]
    offset = (ci - len(all_configs) / 2 + 0.5) * width
    bars = ax.bar(
        x + offset, vals, width, label=label.replace("\n", " "), color=color, alpha=0.8
    )
    for bar in bars:
        h_val = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h_val + 0.005,
            f"{h_val:.3f}",
            ha="center",
            va="bottom",
            fontsize=6,
        )
ax.set_xticks(x)
ax.set_xticklabels([d.replace("_", "\n") for d in ds_list], fontsize=9)
ax.set_ylabel("Final SGG (last 5 epochs avg)")
ax.set_title("Semantic Generalization Gap by Loss Function\n(lower is better)")
ax.legend(fontsize=7, loc="upper right")
ax.grid(True, axis="y")
ax.axhline(0, color="black", linestyle="--", alpha=0.5)

ax = axes[1]
for ci, (cfg, label, color) in enumerate(
    zip(all_configs, config_labels, config_colors)
):
    if cfg == "baseline":
        vals = [
            float(np.mean(rl_results["baseline"][ds]["held"][-5:])) for ds in ds_list
        ]
    else:
        vals = [float(np.mean(rl_results[cfg][ds]["held"][-5:])) for ds in ds_list]
    offset = (ci - len(all_configs) / 2 + 0.5) * width
    bars = ax.bar(
        x + offset, vals, width, label=label.replace("\n", " "), color=color, alpha=0.8
    )
    for bar in bars:
        h_val = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h_val + 0.005,
            f"{h_val:.3f}",
            ha="center",
            va="bottom",
            fontsize=6,
        )
ax.set_xticks(x)
ax.set_xticklabels([d.replace("_", "\n") for d in ds_list], fontsize=9)
ax.set_ylabel("Final Held-out Pass Rate (last 5 epochs avg)")
ax.set_title("Held-out Pass Rate by Loss Function\n(higher is better)")
ax.legend(fontsize=7, loc="lower right")
ax.grid(True, axis="y")
ax.set_ylim(0, 1.15)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "summary_bar_loss_comparison.png"), dpi=100)
plt.close()
print("Saved: summary_bar_loss_comparison.png")

# Plot 5: Val accuracy comparison
fig, ax = plt.subplots(figsize=(10, 5))
for loss_type in LOSS_FUNCTIONS:
    color = LOSS_CONFIGS[loss_type]["color"]
    label = LOSS_CONFIGS[loss_type]["name"]
    acc = disc_metrics[loss_type]["val_acc"]
    ax.plot(epochs_disc, acc, label=label, color=color, linewidth=2)
ax.set_xlabel("Epoch")
ax.set_ylabel("Validation Accuracy")
ax.set_title("Discriminator Validation Accuracy: BCE vs Focal vs Contrastive")
ax.legend(fontsize=9)
ax.grid(True)
ax.set_ylim(0, 1.05)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "val_accuracy_by_loss.png"), dpi=100)
plt.close()
print("Saved: val_accuracy_by_loss.png")

# ==================== Final Summary ====================
print("\n=== Final Results Summary ===")
print(f"\n{'Loss Function':<35} {'Val Acc':<10} {'Val Loss':<10}")
print("-" * 60)
for loss_type in LOSS_FUNCTIONS:
    final_acc = disc_metrics[loss_type]["val_acc"][-1]
    final_loss = disc_metrics[loss_type]["val_loss"][-1]
    print(
        f"{LOSS_CONFIGS[loss_type]['name']:<35} {final_acc:<10.4f} {final_loss:<10.4f}"
    )

print(f"\n{'Config':<35} {'Dataset':<20} {'Final SGG':<12} {'Held-out PR':<14}")
print("-" * 80)
for cfg in all_configs:
    for ds_name in ds_list:
        if cfg == "baseline":
            final_sgg = float(np.mean(rl_results["baseline"][ds_name]["sgg"][-5:]))
            final_held = float(np.mean(rl_results["baseline"][ds_name]["held"][-5:]))
            cfg_label = "Baseline (λ=0)"
        else:
            final_sgg = float(np.mean(rl_results[cfg][ds_name]["sgg"][-5:]))
            final_held = float(np.mean(rl_results[cfg][ds_name]["held"][-5:]))
            cfg_label = LOSS_CONFIGS[cfg]["name"]
        print(f"{cfg_label:<35} {ds_name:<20} {final_sgg:<12.4f} {final_held:<14.4f}")

print("\n=== Ablation Study Complete ===")
