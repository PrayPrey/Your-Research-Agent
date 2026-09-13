"""Data loading for H-E1: AdvGLUE, ANLI-R3, CheckList, GLUE clean."""
import logging
from datasets import load_dataset

logger = logging.getLogger(__name__)

GLUE_TASKS = ["sst2", "mnli", "qqp", "qnli", "rte"]

NUM_LABELS = {
    "sst2": 2, "mnli": 3, "qqp": 2, "qnli": 2, "rte": 2,
}


def get_num_labels(task: str) -> int:
    return NUM_LABELS[task]


def load_adv_glue() -> dict:
    """Returns {task: HF Dataset} for all 5 tasks."""
    result = {}
    for task in GLUE_TASKS:
        try:
            ds = load_dataset("AI-Secure/adv_glue", f"adv_{task}")["validation"]
            result[task] = ds
            logger.info(f"AdvGLUE {task}: {len(ds)} examples")
        except Exception as e:
            logger.warning(f"AdvGLUE {task} failed: {e}")
    return result


def load_glue_clean() -> dict:
    """Returns {task: HF Dataset} validation splits."""
    result = {}
    for task in GLUE_TASKS:
        try:
            split = "validation_matched" if task == "mnli" else "validation"
            ds = load_dataset("glue", task)[split]
            result[task] = ds
            logger.info(f"GLUE clean {task}: {len(ds)} examples")
        except Exception as e:
            logger.warning(f"GLUE clean {task} failed: {e}")
    return result


def load_anli_r3():
    """Returns facebook/anli test_r3 (1200 examples)."""
    ds = load_dataset("facebook/anli", split="test_r3")
    logger.info(f"ANLI-R3: {len(ds)} examples")
    return ds


def load_checklist_suites() -> list:
    """Returns list of {name, suite_type, attack_category, examples, labels}.
    Falls back to empty list if checklist not installed or suite files missing."""
    try:
        import checklist
        import os
        from checklist.test_suite import TestSuite

        CHECKLIST_TYPE_TO_CATEGORY = {"inv": "C9", "dir": "C10", "mft": "C11"}
        pkg_dir = os.path.dirname(checklist.__file__)

        suite_files = []
        for fname in ["sentiment.pkl", "nli.pkl"]:
            fp = os.path.join(pkg_dir, "suites", fname)
            if os.path.exists(fp):
                suite_files.append(fp)

        results = []
        for fp in suite_files:
            try:
                suite = TestSuite.from_file(fp)
                for test_name, test in suite.tests.items():
                    suite_type = (
                        "mft" if "mft" in test_name.lower()
                        else "inv" if "inv" in test_name.lower()
                        else "dir"
                    )
                    try:
                        examples = [ex for ex, _ in test.data]
                        labels = [lbl for _, lbl in test.data]
                    except Exception:
                        examples = list(test.data)
                        labels = []
                    results.append({
                        "name": test_name,
                        "suite_type": suite_type,
                        "attack_category": CHECKLIST_TYPE_TO_CATEGORY[suite_type],
                        "examples": examples,
                        "labels": labels,
                    })
            except Exception as e:
                logger.warning(f"CheckList suite {fp} failed: {e}")

        logger.info(f"CheckList suites loaded: {len(results)}")
        return results

    except ImportError:
        logger.warning("checklist not installed; skipping CheckList suites")
        return []
    except Exception as e:
        logger.warning(f"CheckList loading failed: {e}")
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    adv = load_adv_glue()
    clean = load_glue_clean()
    anli = load_anli_r3()
    cl = load_checklist_suites()
    print("AdvGLUE tasks:", list(adv.keys()))
    print("GLUE clean tasks:", list(clean.keys()))
    print("ANLI-R3:", len(anli))
    print("CheckList suites:", len(cl))
