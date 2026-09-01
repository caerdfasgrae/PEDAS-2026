"""CLI runner for baseline model training and evaluation."""

import argparse
import pandas as pd
from src.features.extractor import PhishingFeatureExtractor
from src.models.baseline import BaselineModelTrainer
from src.utils.config import BENCHMARK_DATA_DIR, RANDOM_STATE


def main():
    parser = argparse.ArgumentParser(description="PeDaS 2026 Baseline Phishing Detection Runner")
    parser.add_argument(
        "--model",
        type=str,
        default="lightgbm",
        choices=["lightgbm", "xgboost", "catboost", "rf"],
        help="Classifier model architecture",
    )
    parser.add_argument(
        "--folds",
        type=int,
        default=5,
        help="Number of Stratified K-Folds",
    )
    args = parser.parse_args()

    data_path = BENCHMARK_DATA_DIR / "sample_phishing_id.csv"
    print(f"[*] Loading benchmark data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"[*] Loaded {len(df)} samples ({sum(df['label'] == 1)} Phishing, {sum(df['label'] == 0)} Legitimate).")

    print("[*] Extracting features (Lexical + Indonesian Brand Spoofing)...")
    extractor = PhishingFeatureExtractor(include_dns=False, include_whois=False)
    features_df = extractor.transform(df, url_col="url", show_progress=False)
    print(f"[*] Extracted {features_df.shape[1]} features successfully.")

    print(f"[*] Running Stratified {args.folds}-Fold CV with model: {args.model.upper()}...")
    trainer = BaselineModelTrainer(model_type=args.model, n_splits=args.folds, random_state=RANDOM_STATE)
    metrics, fi_df, oof_probs = trainer.cross_validate(features_df, df["label"].values)

    print("\n" + "=" * 50)
    print(f"EVALUATION RESULTS ({args.model.upper()}):")
    print("=" * 50)
    for k, v in metrics.items():
        if k != "fold_f1_macros":
            print(f"  {k:<22}: {v}")
    print("=" * 50)
    print(f"  Fold F1-Macros        : {metrics['fold_f1_macros']}")
    print("=" * 50)

    print("\n[*] Top 10 Most Discriminative Features:")
    for idx, row in fi_df.head(10).iterrows():
        print(f"  {idx+1:2d}. {row['feature']:<30} (importance: {row['importance']:.4f})")


if __name__ == "__main__":
    main()
