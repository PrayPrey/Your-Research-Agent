import os
import tarfile
import urllib.request
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset


def download_waterbirds(data_dir: str) -> str:
    url = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    os.makedirs(data_dir, exist_ok=True)
    tar_path = os.path.join(data_dir, "waterbirds.tar.gz")
    extract_path = os.path.join(data_dir, "waterbird_complete95_forest2water2")

    if not os.path.exists(extract_path):
        print(f"Downloading Waterbirds dataset to {tar_path}...")
        urllib.request.urlretrieve(url, tar_path)
        print("Extracting...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(data_dir)
        os.remove(tar_path)
        print("Done.")
    else:
        print(f"Dataset already exists at {extract_path}")

    return extract_path


def load_metadata(data_dir: str) -> pd.DataFrame:
    metadata_path = os.path.join(data_dir, "metadata.csv")
    df = pd.read_csv(metadata_path)
    return df


class WaterbirdsDataset(Dataset):
    def __init__(self, data_dir: str, split: str, preprocess):
        self.data_dir = data_dir
        self.preprocess = preprocess

        metadata = load_metadata(data_dir)
        split_map = {"train": 0, "val": 1, "test": 2}
        self.metadata = metadata[metadata["split"] == split_map[split]].reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.metadata)

    def __getitem__(self, idx: int) -> tuple:
        row = self.metadata.iloc[idx]
        img_path = os.path.join(self.data_dir, row["img_filename"])
        image = Image.open(img_path).convert("RGB")
        image = self.preprocess(image)
        y = int(row["y"])
        place = int(row["place"])
        return image, y, place
