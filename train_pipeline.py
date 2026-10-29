"""Command-line training entry point for a real predictive-maintenance CSV."""
import argparse
from pathlib import Path

import app as service


def main():
    parser = argparse.ArgumentParser(description="Train the Maintaina model from a CSV file.")
    parser.add_argument("--data", default="machine_data.csv", help="Path to a CSV dataset")
    parser.add_argument("--target", required=True, help="Column to predict, e.g. 'Machine failure'")
    parser.add_argument("--task", choices=["auto", "classification", "regression"], default="auto")
    args = parser.parse_args()
    path = Path(args.data)
    if not path.exists():
        parser.error(f"Dataset not found: {path}")
    # Reuse the exact production service logic rather than maintaining a second pipeline.
    service.DATASET_PATH = path
    result = service.train_model(service.TrainRequest(target=args.target, task=args.task))
    print("Training complete")
    print(f"Task: {result['task']}")
    print(f"Metrics: {result['metrics']}")
    print(f"Model saved to: {service.MODEL_PATH}")


if __name__ == "__main__":
    main()
