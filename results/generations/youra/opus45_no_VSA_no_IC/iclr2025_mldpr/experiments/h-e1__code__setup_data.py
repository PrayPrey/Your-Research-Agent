#!/usr/bin/env python
"""Download and setup datasets for H-E1 experiment."""
import os
import subprocess
import sys
from pathlib import Path

import torch
from torchvision import datasets


def download_torchvision_datasets(data_root: str):
    """Download datasets available through torchvision."""
    print("=== Downloading torchvision datasets ===")

    print("Downloading Flowers102...")
    datasets.Flowers102(data_root, split="train", download=True)
    datasets.Flowers102(data_root, split="test", download=True)

    print("Downloading FGVC Aircraft...")
    datasets.FGVCAircraft(data_root, split="train", download=True)
    datasets.FGVCAircraft(data_root, split="test", download=True)

    print("torchvision datasets ready.")


def setup_cub(data_root: str):
    """Download CUB-200-2011 dataset."""
    cub_dir = Path(data_root) / "CUB_200_2011"
    if cub_dir.exists() and (cub_dir / "images.txt").exists():
        print("CUB-200-2011 already exists")
        return

    print("Downloading CUB-200-2011...")
    cub_dir.mkdir(parents=True, exist_ok=True)
    url = "https://data.caltech.edu/records/65de6-vp158/files/CUB_200_2011.tgz"
    tgz_path = Path(data_root) / "CUB_200_2011.tgz"

    subprocess.run(["wget", "-q", url, "-O", str(tgz_path)], check=True)
    subprocess.run(["tar", "-xzf", str(tgz_path), "-C", data_root], check=True)
    tgz_path.unlink()
    print("CUB-200-2011 ready.")


def setup_stanford_dogs(data_root: str):
    """Download Stanford Dogs dataset."""
    dogs_dir = Path(data_root) / "stanford_dogs"
    if dogs_dir.exists() and (dogs_dir / "train_list.mat").exists():
        print("Stanford Dogs already exists")
        return

    print("Downloading Stanford Dogs...")
    dogs_dir.mkdir(parents=True, exist_ok=True)

    images_url = "http://vision.stanford.edu/aditya86/ImageNetDogs/images.tar"
    lists_url = "http://vision.stanford.edu/aditya86/ImageNetDogs/lists.tar"

    subprocess.run(["wget", "-q", images_url, "-O", str(dogs_dir / "images.tar")], check=True)
    subprocess.run(["wget", "-q", lists_url, "-O", str(dogs_dir / "lists.tar")], check=True)

    subprocess.run(["tar", "-xf", str(dogs_dir / "images.tar"), "-C", str(dogs_dir)], check=True)
    subprocess.run(["tar", "-xf", str(dogs_dir / "lists.tar"), "-C", str(dogs_dir)], check=True)

    (dogs_dir / "images.tar").unlink()
    (dogs_dir / "lists.tar").unlink()
    print("Stanford Dogs ready.")


def setup_stanford_cars(data_root: str):
    """Download Stanford Cars dataset."""
    cars_dir = Path(data_root) / "stanford_cars"
    if cars_dir.exists() and (cars_dir / "cars_train").exists():
        print("Stanford Cars already exists")
        return

    print("Downloading Stanford Cars...")
    cars_dir.mkdir(parents=True, exist_ok=True)

    base_url = "http://ai.stanford.edu/~jkrause/car196"
    train_url = f"{base_url}/cars_train.tgz"
    test_url = f"{base_url}/cars_test.tgz"
    devkit_url = f"{base_url}/car_devkit.tgz"
    test_annos_url = f"{base_url}/cars_test_annos_withlabels.mat"

    for url, fname in [(train_url, "cars_train.tgz"), (test_url, "cars_test.tgz"),
                       (devkit_url, "car_devkit.tgz")]:
        subprocess.run(["wget", "-q", url, "-O", str(cars_dir / fname)], check=True)
        subprocess.run(["tar", "-xzf", str(cars_dir / fname), "-C", str(cars_dir)], check=True)
        (cars_dir / fname).unlink()

    subprocess.run(["wget", "-q", test_annos_url, "-O",
                    str(cars_dir / "cars_test_annos_withlabels.mat")], check=True)

    devkit = cars_dir / "devkit"
    if devkit.exists():
        for f in devkit.glob("*.mat"):
            f.rename(cars_dir / f.name)

    print("Stanford Cars ready.")


def setup_nabirds(data_root: str):
    """Setup NABirds dataset (requires manual download or existing data)."""
    nabirds_dir = Path(data_root) / "nabirds"
    if nabirds_dir.exists() and (nabirds_dir / "images.txt").exists():
        print("NABirds already exists")
        return

    print("NABirds requires manual download from:")
    print("  https://dl.allaboutbirds.org/nabirds")
    print("After download, extract to:", nabirds_dir)

    nabirds_dir.mkdir(parents=True, exist_ok=True)
    print("Created placeholder directory. Please add dataset manually.")


def main():
    data_root = sys.argv[1] if len(sys.argv) > 1 else "./data"
    Path(data_root).mkdir(parents=True, exist_ok=True)

    download_torchvision_datasets(data_root)
    setup_cub(data_root)
    setup_stanford_dogs(data_root)
    setup_stanford_cars(data_root)
    setup_nabirds(data_root)

    print("\n=== Dataset setup complete ===")
    print(f"Data root: {data_root}")


if __name__ == "__main__":
    main()
