"""Supervised AI Feedback Model using CodeBERT"""
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
import torch
from typing import Dict
from config import ModelConfig, TrainingConfig

class SupervisedFeedbackModel:
    """CodeBERT fine-tuned on human annotations for code quality prediction"""

    def __init__(self, model_config: ModelConfig, training_config: TrainingConfig):
        self.model_config = model_config
        self.training_config = training_config

        print(f"Loading model: {model_config.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_config.model_name,
            cache_dir=model_config.cache_dir
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_config.model_name,
            num_labels=model_config.num_labels,
            cache_dir=model_config.cache_dir
        )

        print(f"Model loaded: {self.model.config.hidden_size}-dim hidden")

    def preprocess_function(self, examples):
        """Tokenize code and prepare labels"""
        # Tokenize code
        result = self.tokenizer(
            examples['code'],
            truncation=True,
            padding='max_length',
            max_length=self.model_config.max_length
        )

        # Add labels (human scores)
        result['labels'] = examples['human_score']
        return result

    def train(self, train_dataset, val_dataset):
        """Fine-tune model on human annotations"""

        # Tokenize datasets
        print("Tokenizing datasets...")
        train_tokenized = train_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=train_dataset.column_names
        )
        val_tokenized = val_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=val_dataset.column_names
        )

        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.training_config.output_dir,
            num_train_epochs=self.training_config.num_train_epochs,
            per_device_train_batch_size=self.training_config.per_device_train_batch_size,
            learning_rate=self.training_config.learning_rate,
            weight_decay=self.training_config.weight_decay,
            warmup_ratio=self.training_config.warmup_ratio,
            evaluation_strategy=self.training_config.eval_strategy,
            save_strategy=self.training_config.save_strategy,
            load_best_model_at_end=self.training_config.load_best_model_at_end,
            metric_for_best_model=self.training_config.metric_for_best_model,
            logging_steps=self.training_config.logging_steps,
            save_total_limit=2,
            report_to=[]  # Disable wandb/tensorboard
        )

        # Trainer with early stopping
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_tokenized,
            eval_dataset=val_tokenized,
            callbacks=[EarlyStoppingCallback(
                early_stopping_patience=self.training_config.early_stopping_patience
            )]
        )

        print("Starting training...")
        trainer.train()

        print("Training complete!")
        self.trainer = trainer
        return trainer

    def predict(self, test_dataset):
        """Predict human scores on test set"""
        # Tokenize test set
        test_tokenized = test_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=test_dataset.column_names
        )

        # Predict
        predictions = self.trainer.predict(test_tokenized)
        return predictions.predictions.squeeze()

if __name__ == "__main__":
    from config import get_config
    from data_pipeline import load_and_prepare_data

    config = get_config()
    data = load_and_prepare_data(config.data)

    model = SupervisedFeedbackModel(config.model, config.training)
    print("\n✓ Model initialization validated")
