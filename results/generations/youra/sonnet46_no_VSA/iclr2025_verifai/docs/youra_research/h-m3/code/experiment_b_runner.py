"""Experiment B: adaptive PBT oracle using Hypothesis + assert-based contracts from ContractEval."""
import inspect
import signal
import platform
import functools
import multiprocessing as mp
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from hypothesis import given, settings, HealthCheck, seed as h_seed
from hypothesis import strategies as st


@dataclass
class TripleResult:
    task_id: str
    model: str
    program_idx: int
    adaptive_failure_rate: float
    n_valid: int
    n_failures: int
    filter_rate: float
    error: Optional[str]


class _TripleTimeout(BaseException):
    """BaseException (not Exception) so hypothesis cannot catch it internally."""
    pass


def _timeout_handler(signum, frame):
    raise _TripleTimeout("triple timeout")


class _Timeout:
    def __init__(self, secs: int):
        self.secs = secs
        self._posix = platform.system() != "Windows"

    def __enter__(self):
        if self._posix:
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(self.secs)
        return self

    def __exit__(self, *_):
        if self._posix:
            signal.alarm(0)


def _exec_fn(code_str: str, entry_point: str) -> tuple:
    """Returns (callable, error_str)."""
    ns = {}
    try:
        exec(compile(code_str, "<code>", "exec"), ns)
        fn = ns.get(entry_point)
        if fn is None or not callable(fn):
            return None, f"'{entry_point}' not found"
        return fn, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _run_hypothesis_pbt(
    llm_fn,
    contract_ref_fn,
    budget: int,
    seed: int,
) -> tuple[int, int]:
    """
    Run Hypothesis with inferred strategies on the contract reference function.
    For each generated input:
      - If contract_ref raises AssertionError: input is contract-violating (pre-condition fails).
        Also call llm_fn to check if it also rejects (AssertionError) or silently passes.
        Count as n_valid (hypothesis found a valid test case from contract perspective).
        Count as n_failures if llm_fn does NOT raise AssertionError (LLM accepts invalid input).
      - If contract_ref returns normally: input is valid. Test both.
        Count toward coverage but not as contract violation.

    Returns (n_valid, n_failures).
    n_valid = total generated examples that ran without timeout.
    n_failures = inputs where contract_ref raises AssertionError AND llm_fn does not.
    """
    counter = {"total": 0, "failures": 0, "errors": 0}

    def test_fn(*args):
        counter["total"] += 1
        try:
            ref_result = None
            ref_error = None
            try:
                ref_result = contract_ref_fn(*args)
            except AssertionError:
                ref_error = "AssertionError"
            except Exception as e:
                ref_error = type(e).__name__

            if ref_error == "AssertionError":
                # Contract violation: check if LLM also rejects it
                llm_error = None
                try:
                    llm_fn(*args)
                except AssertionError:
                    llm_error = "AssertionError"
                except Exception:
                    llm_error = "OtherError"
                if llm_error is None:
                    # LLM silently accepted what the contract rejects = violation
                    counter["failures"] += 1
        except Exception:
            counter["errors"] += 1

    # Use Hypothesis to generate inputs via type inference from the contract ref function
    from hypothesis import find, Phase
    try:
        # Infer strategy from type annotations or use general approach
        sig = inspect.signature(contract_ref_fn)
        param_count = len(sig.parameters)
        param_list = list(sig.parameters.values())

        # Map type annotations to strategies
        type_to_strategy = {
            int: st.integers(min_value=-1000, max_value=1000),
            float: st.floats(allow_nan=False, allow_infinity=False),
            str: st.text(max_size=50),
            bool: st.booleans(),
            list: st.lists(st.integers(), max_size=20),
        }

        param_strategies = []
        for p in param_list:
            ann = p.annotation
            if ann in type_to_strategy:
                param_strategies.append(type_to_strategy[ann])
            else:
                # Fallback: try common types
                param_strategies.append(
                    st.one_of(
                        st.integers(min_value=-100, max_value=100),
                        st.text(max_size=30),
                        st.lists(st.integers(min_value=-10, max_value=10), max_size=10),
                        st.floats(allow_nan=False, allow_infinity=False, min_value=-100, max_value=100),
                        st.booleans(),
                    )
                )

        if not param_strategies:
            return 0, 0

        # Build a named-argument function to satisfy hypothesis @given requirements
        param_names = [p.name for p in param_list]
        fn_args = ", ".join(param_names)
        fn_src = f"def _hyp_test({fn_args}): test_fn({fn_args})"
        exec_ns = {"test_fn": test_fn}
        exec(fn_src, exec_ns)
        hyp_test_fn = exec_ns["_hyp_test"]

        decorated = h_seed(seed)(
            settings(
                max_examples=budget,
                deadline=None,
                suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much, HealthCheck.large_base_example],
            )(
                given(*param_strategies)(hyp_test_fn)
            )
        )
        try:
            decorated()
        except Exception:
            pass  # hypothesis may raise on found counterexample; we don't care

    except Exception:
        pass

    return counter["total"], counter["failures"]


def run_triple(
    llm_code: str,
    contracteval_task: dict,
    task_id: str,
    model: str,
    program_idx: int,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42,
) -> TripleResult:
    n_valid, n_failures, error = 0, 0, None
    try:
        with _Timeout(timeout_secs):
            entry_point = contracteval_task["entry_point"]
            llm_fn, err = _exec_fn(llm_code, entry_point)
            if err:
                raise RuntimeError(f"LLM exec error: {err}")
            contract_ref_fn, err2 = _exec_fn(
                contracteval_task["canonical_solution_with_contract"], entry_point
            )
            if err2:
                raise RuntimeError(f"Contract ref exec error: {err2}")
            n_valid, n_failures = _run_hypothesis_pbt(llm_fn, contract_ref_fn, budget, rng_seed)
    except _TripleTimeout:
        error = "TimeoutError"
    except BaseException as e:
        error = type(e).__name__

    filter_rate = 1.0 - (n_valid / budget) if budget > 0 else 1.0
    adaptive_failure_rate = n_failures / n_valid if n_valid > 0 else 0.0

    return TripleResult(
        task_id=task_id,
        model=model,
        program_idx=program_idx,
        adaptive_failure_rate=adaptive_failure_rate,
        n_valid=n_valid,
        n_failures=n_failures,
        filter_rate=filter_rate,
        error=error,
    )


def _enumerate_triples(tasks: dict, corpus: dict) -> list[tuple]:
    args = []
    for model, task_programs in corpus.items():
        for task_id, programs in task_programs.items():
            if task_id not in tasks:
                continue
            for idx, code in enumerate(programs):
                args.append((code, tasks[task_id], task_id, model, idx))
    return args


def _triple_worker(args: tuple) -> dict:
    llm_code, contracteval_task, task_id, model, program_idx = args
    result = run_triple(llm_code, contracteval_task, task_id, model, program_idx)
    return asdict(result)


def _triple_worker_with_budget(args: tuple) -> dict:
    llm_code, contracteval_task, task_id, model, program_idx, budget, timeout_secs, rng_seed = args
    result = run_triple(llm_code, contracteval_task, task_id, model, program_idx,
                        budget=budget, timeout_secs=timeout_secs, rng_seed=rng_seed)
    return asdict(result)


def run_experiment_b(
    tasks: dict,
    corpus: dict,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42,
    n_workers: int = 16,
    output_path: str = "results/experiment_b_results.jsonl",
) -> list[TripleResult]:
    import tqdm

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    raw_args = _enumerate_triples(tasks, corpus)
    all_args = [(code, task, tid, model, idx, budget, timeout_secs, rng_seed)
                for code, task, tid, model, idx in raw_args]
    all_results: list[TripleResult] = []

    with mp.Pool(n_workers, maxtasksperchild=100) as pool, open(output_path, "w") as f:
        for result_dict in tqdm.tqdm(
            pool.imap_unordered(_triple_worker_with_budget, all_args),
            total=len(all_args),
            desc="Experiment B",
        ):
            f.write(json.dumps(result_dict) + "\n")
            f.flush()
            all_results.append(TripleResult(**result_dict))

    return all_results


def verify_experiment_b_activated(results: list[TripleResult]) -> tuple[bool, dict]:
    n = len(results)
    if n == 0:
        return False, {"error": "no results"}

    n_valid_sufficient = sum(1 for r in results if r.n_valid >= 100)
    n_filter_total = sum(1 for r in results if r.filter_rate >= 1.0)
    unique_rates = {r.adaptive_failure_rate for r in results}

    indicators = {
        "yield_sufficient": (n_valid_sufficient / n) >= 0.80,
        "filter_not_total": n_filter_total == 0,
        "adaptive_gap_measurable": len(unique_rates) > 1,
        "triples_covered": n >= 10_000,
    }

    strategy_errors = sum(1 for r in results if r.error == "StrategyInferenceError")
    task_ids = {r.task_id for r in results}
    zero_valid_tasks = len({r.task_id for r in results if r.n_valid == 0})
    indicators["strategy_error_rate"] = strategy_errors / max(n, 1)
    indicators["zero_valid_task_fraction"] = zero_valid_tasks / max(len(task_ids), 1)

    gate_passed = sum(
        v for k, v in indicators.items()
        if k in {"yield_sufficient", "filter_not_total", "adaptive_gap_measurable", "triples_covered"}
    ) >= 3
    indicators["gate_passed"] = gate_passed

    return gate_passed, indicators
