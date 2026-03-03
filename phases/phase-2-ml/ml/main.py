"""
Phase 2 ML Pipeline - Main CLI Entry Point.
Global Daily Sales Forecasting using Machine Learning.

Usage:
    python main.py train global
    python main.py evaluate global
    python main.py predict global
"""

import typer
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT.parent))

from ml.config import LOG_FORMAT, LOG_LEVEL, LOG_FILE
from ml.tasks.train import train_global_model
from ml.tasks.evaluate import evaluate_global_model
from ml.tasks.predict import predict_global_sales

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(
    name="retail-ml",
    help="Phase 2 ML Pipeline - Global Daily Sales Forecasting",
    add_completion=False
)


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo("Retail Analytics ML Pipeline v2.0.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Print version and exit"
    )
):
    """
    Retail Analytics ML Pipeline CLI.
    
    Train, evaluate, and predict global daily sales using machine learning.
    """
    pass


@app.command()
def train(
    model_type: str = typer.Argument(
        "global",
        help="Model type to train (global)"
    )
):
    """
    Train a sales forecasting model.
    
    Trains both Linear Regression and Random Forest models,
    then saves the best model based on lowest RMSE.
    
    Examples:
        python main.py train global
    """
    logger.info(f"Training command invoked for model type: {model_type}")
    
    if model_type != "global":
        typer.echo(f"Error: Unknown model type '{model_type}'. Use 'global'.")
        raise typer.Exit(code=1)
    
    try:
        result = train_global_model()
        if result is None:
            typer.echo("Training failed. Check logs for details.")
            raise typer.Exit(code=1)
        typer.echo("\nTraining completed successfully!")
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def evaluate(
    model_type: str = typer.Argument(
        "global",
        help="Model type to evaluate (global)"
    ),
    model_path: str = typer.Option(
        None,
        "--model-path",
        "-m",
        help="Path to model file (default: ml/models/global_best_model.pkl)"
    )
):
    """
    Evaluate a trained sales forecasting model.
    
    Loads a trained model and evaluates its performance on test data.
    
    Examples:
        python main.py evaluate global
        python main.py evaluate global -m models/my_model.pkl
    """
    logger.info(f"Evaluate command invoked for model type: {model_type}")
    
    if model_type != "global":
        typer.echo(f"Error: Unknown model type '{model_type}'. Use 'global'.")
        raise typer.Exit(code=1)
    
    try:
        result = evaluate_global_model(model_path)
        if result is None:
            typer.echo("Evaluation failed. Check logs for details.")
            raise typer.Exit(code=1)
        typer.echo("\nEvaluation completed successfully!")
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def predict(
    model_type: str = typer.Argument(
        "global",
        help="Model type for prediction (global)"
    ),
    days: int = typer.Option(
        7,
        "--days",
        "-d",
        help="Number of days to forecast (default: 7)"
    ),
    model_path: str = typer.Option(
        None,
        "--model-path",
        "-m",
        help="Path to model file (default: ml/models/global_best_model.pkl)"
    )
):
    """
    Generate sales forecasts.
    
    Uses a trained model to predict future daily sales.
    
    Examples:
        python main.py predict global
        python main.py predict global -d 14
        python main.py predict global -d 30 -m models/my_model.pkl
    """
    logger.info(f"Predict command invoked for model type: {model_type}, days: {days}")
    
    if model_type != "global":
        typer.echo(f"Error: Unknown model type '{model_type}'. Use 'global'.")
        raise typer.Exit(code=1)
    
    if days < 1:
        typer.echo("Error: Days must be at least 1.")
        raise typer.Exit(code=1)
    
    try:
        result = predict_global_sales(model_path, forecast_days=days)
        if result is None:
            typer.echo("Prediction failed. Check logs for details.")
            raise typer.Exit(code=1)
        typer.echo("\nPrediction completed successfully!")
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
