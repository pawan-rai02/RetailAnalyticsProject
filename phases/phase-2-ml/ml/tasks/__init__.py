"""
Tasks package for Phase 2 ML Pipeline.
"""

from ml.tasks.train import train_global_model
from ml.tasks.evaluate import evaluate_global_model
from ml.tasks.predict import predict_global_sales

__all__ = [
    "train_global_model",
    "evaluate_global_model",
    "predict_global_sales"
]
