"""Data loading and dataset preparation"""

import timm
import torch
import pandas as pd
import json
import logging
from sklearn.model_selection import train_test_split
from feature_extractor import StatisticalFeatureExtractor
from config import MODEL_FAMILIES, SPLIT_CONFIG


class TIMMDataLoader:
    """Download TIMM models and create train/val splits"""

    def __init__(self, model_families: dict = None, random_seed: int = 42):
        self.model_families = model_families or MODEL_FAMILIES
        self.random_seed = random_seed
        self.extractor = StatisticalFeatureExtractor()
        self.logger = logging.getLogger(__name__)

    def download_models(self) -> list:
        """
        Download models from TIMM and extract features.

        Returns:
            List of tuples: [(model_name, family, features_dict), ...]
        """
        data = []
        total_models = sum(len(models) for models in self.model_families.values())
        count = 0

        for family, model_names in self.model_families.items():
            self.logger.info(f"Downloading {family} models...")

            for model_name in model_names:
                count += 1
                try:
                    self.logger.info(f"[{count}/{total_models}] Loading {model_name}...")

                    # Download model with pretrained weights
                    model = timm.create_model(model_name, pretrained=True)
                    state_dict = model.state_dict()

                    # Extract features
                    features = self.extractor.extract_features(state_dict)

                    data.append((model_name, family, features))

                    # Free memory
                    del model
                    del state_dict
                    torch.cuda.empty_cache() if torch.cuda.is_available() else None

                except Exception as e:
                    self.logger.error(f"Failed to load {model_name}: {e}")
                    continue

        self.logger.info(f"Successfully loaded {len(data)}/{total_models} models")
        return data

    def create_splits(self, data: list, test_size: float = None) -> tuple:
        """
        Create stratified train/validation split.

        Args:
            data: List of (model_name, family, features) tuples
            test_size: Validation set fraction (default from config)

        Returns:
            (train_df, val_df) DataFrames with features and labels
        """
        test_size = test_size or SPLIT_CONFIG['test_size']

        # Convert to DataFrame
        rows = []
        for model_name, family, features in data:
            row = {'model_name': model_name, 'family': family}
            row.update(features)
            rows.append(row)

        df = pd.DataFrame(rows)

        # Stratified split
        train_df, val_df = train_test_split(
            df,
            test_size=test_size,
            stratify=df['family'],
            random_state=self.random_seed
        )

        self.logger.info(f"Train set: {len(train_df)} samples")
        self.logger.info(f"Val set: {len(val_df)} samples")
        self.logger.info(f"Train distribution: {train_df['family'].value_counts().to_dict()}")
        self.logger.info(f"Val distribution: {val_df['family'].value_counts().to_dict()}")

        return train_df, val_df

    def save_features(self, train_df: pd.DataFrame, val_df: pd.DataFrame, output_dir: str):
        """Save train/val features to CSV files"""
        train_path = f"{output_dir}/train_features.csv"
        val_path = f"{output_dir}/val_features.csv"
        list_path = f"{output_dir}/model_list.json"

        train_df.to_csv(train_path, index=False)
        val_df.to_csv(val_path, index=False)

        # Save model list with family labels
        all_models = pd.concat([train_df, val_df])
        model_list = {
            row['model_name']: row['family']
            for _, row in all_models.iterrows()
        }

        with open(list_path, 'w') as f:
            json.dump(model_list, f, indent=2)

        self.logger.info(f"Saved features to {output_dir}")
