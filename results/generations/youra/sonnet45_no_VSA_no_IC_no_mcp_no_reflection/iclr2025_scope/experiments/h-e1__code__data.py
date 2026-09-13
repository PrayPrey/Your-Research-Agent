from datasets import load_dataset


class GLUELoader:
    def __init__(self, task_names: list):
        self.task_names = task_names
        self.task_map = {
            "mnli": "mnli",
            "qqp": "qqp",
            "sst2": "sst2"
        }

    def load_task(self, task_name: str, split: str = "validation"):
        glue_name = self.task_map[task_name]
        if task_name == "mnli":
            dataset = load_dataset("glue", glue_name, split=f"{split}_matched")
        else:
            dataset = load_dataset("glue", glue_name, split=split)
        return dataset

    def get_task_info(self, task_name: str) -> dict:
        dataset = self.load_task(task_name)
        info = {
            "name": task_name,
            "samples": len(dataset),
            "label_count": 3 if task_name == "mnli" else 2
        }
        return info
