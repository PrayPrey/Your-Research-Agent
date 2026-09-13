from pathlib import Path
import pandas as pd
import json

class PWCDataLoader:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

    def load_benchmark(self, benchmark: str) -> pd.DataFrame:
        jsonl_path = self.data_dir / f"{benchmark}_raw.jsonl"
        records = []
        with open(jsonl_path) as f:
            for line in f:
                records.append(json.loads(line))
        df = pd.DataFrame(records)
        df['submission_date'] = pd.to_datetime(df['submission_date'])
        return df[['submission_date', 'score', 'benchmark', 'model_name']]

    def prepare_monthly_aggregation(self, df: pd.DataFrame) -> pd.DataFrame:
        df['month'] = df['submission_date'].dt.to_period('M')
        return df
