"""Technical Report Collection Module

This module handles downloading and storing technical reports from major LLM labs.
Supports retry logic with exponential backoff for robust downloading.
"""

import requests
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class TechnicalReportCollector:
    """Downloads and manages technical reports from LLM labs."""

    def __init__(self, output_dir: str):
        """
        Initialize collector.

        Args:
            output_dir: Directory to store downloaded reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata: Dict[str, Dict] = {}
        self.metadata_file = self.output_dir / "metadata.json"

        # Load existing metadata if available
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)

    def download_report(
        self,
        url: str,
        model_family: str,
        timepoint: str,
        max_retries: int = 3
    ) -> str:
        """
        Download technical report with retry logic.

        Args:
            url: URL to download from
            model_family: Model family name (GPT, Claude, Llama)
            timepoint: baseline or current
            max_retries: Maximum retry attempts

        Returns:
            Path to downloaded file

        Raises:
            Exception: If download fails after all retries
        """
        filename = f"{model_family.lower()}_{timepoint}.pdf"
        filepath = self.output_dir / filename

        # Check if already downloaded
        if filepath.exists():
            logger.info(f"Report already exists: {filepath}")
            return str(filepath)

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading {model_family} {timepoint} report (attempt {attempt + 1}/{max_retries})...")

                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Research Bot)'
                })
                response.raise_for_status()

                # Write to file
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                # Store metadata
                self.metadata[f"{model_family}_{timepoint}"] = {
                    "url": url,
                    "model_family": model_family,
                    "timepoint": timepoint,
                    "filename": filename,
                    "downloaded_at": datetime.now().isoformat(),
                    "size_bytes": len(response.content)
                }
                self._save_metadata()

                logger.info(f"Downloaded successfully: {filepath}")
                return str(filepath)

            except requests.RequestException as e:
                logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to download after {max_retries} attempts")
                    raise Exception(f"Download failed for {model_family} {timepoint}: {e}")

    def list_downloaded_reports(self) -> List[Dict[str, str]]:
        """
        List all downloaded reports.

        Returns:
            List of report metadata dictionaries
        """
        return list(self.metadata.values())

    def get_metadata(self) -> Dict:
        """
        Get all metadata.

        Returns:
            Metadata dictionary
        """
        return self.metadata.copy()

    def _save_metadata(self):
        """Save metadata to JSON file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
