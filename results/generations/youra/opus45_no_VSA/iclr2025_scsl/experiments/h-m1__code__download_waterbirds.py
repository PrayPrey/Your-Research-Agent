#!/usr/bin/env python
import os
import requests
import tarfile
from tqdm import tqdm

WATERBIRDS_URL = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"

def download_waterbirds(data_root: str = "./data/waterbirds"):
    os.makedirs(data_root, exist_ok=True)
    tar_path = os.path.join(data_root, "waterbirds.tar.gz")
    if os.path.exists(os.path.join(data_root, "metadata.csv")):
        print("Waterbirds dataset already exists.")
        return
    print(f"Downloading Waterbirds dataset to {data_root}...")
    response = requests.get(WATERBIRDS_URL, stream=True)
    total = int(response.headers.get('content-length', 0))
    with open(tar_path, 'wb') as f, tqdm(total=total, unit='B', unit_scale=True, desc="Downloading") as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))
    print("Extracting...")
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(os.path.dirname(data_root))
    extracted_dir = os.path.join(os.path.dirname(data_root), "waterbird_complete95_forest2water2")
    if os.path.exists(extracted_dir):
        import shutil
        for item in os.listdir(extracted_dir):
            shutil.move(os.path.join(extracted_dir, item), os.path.join(data_root, item))
        os.rmdir(extracted_dir)
    os.remove(tar_path)
    print(f"Waterbirds dataset ready at {data_root}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="./data/waterbirds")
    args = parser.parse_args()
    download_waterbirds(args.data_root)
