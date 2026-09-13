#!/usr/bin/env python3
"""
Download Waterbirds dataset for h-m1 experiment
This script downloads the real Waterbirds dataset to fix the mock data issue
"""

import os
import sys
import urllib.request
import tarfile
from pathlib import Path
import shutil

def download_waterbirds(data_dir="../h-e1/code/data/waterbirds"):
    """Download and extract Waterbirds dataset"""

    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    # Check if already downloaded
    metadata_file = data_path / "metadata.csv"
    if metadata_file.exists():
        print(f"✓ Waterbirds dataset already exists at {data_dir}")
        return True

    print(f"Downloading Waterbirds dataset to {data_dir}...")

    # Download URL from WILDS/CodaLab
    url = "https://worksheets.codalab.org/rest/bundles/0xd013a7ba2e88481bbc07e787f73109f5/contents/blob/"
    tar_path = data_path / "waterbird_complete95_forest2water2.tar.gz"

    try:
        # Download
        if not tar_path.exists():
            print(f"Downloading from {url}...")
            print("This may take several minutes (dataset is ~1GB)...")
            urllib.request.urlretrieve(url, tar_path)
            print("✓ Download complete")

        # Extract
        print("Extracting archive...")
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(data_path)
        print("✓ Extraction complete")

        # Move files to data_dir root if in subdirectory
        extracted_dir = data_path / "waterbird_complete95_forest2water2"
        if extracted_dir.exists() and extracted_dir.is_dir():
            print("Reorganizing files...")
            for item in extracted_dir.iterdir():
                dest = data_path / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))
            extracted_dir.rmdir()
            print("✓ Files reorganized")

        # Verify metadata exists
        if not metadata_file.exists():
            print("✗ Error: metadata.csv not found after extraction")
            return False

        # Clean up tar file to save space
        if tar_path.exists():
            tar_path.unlink()
            print("✓ Cleaned up archive file")

        print(f"✓ Waterbirds dataset ready at {data_dir}")
        return True

    except Exception as e:
        print(f"✗ Error downloading dataset: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "../h-e1/code/data/waterbirds"
    success = download_waterbirds(data_dir)
    sys.exit(0 if success else 1)
