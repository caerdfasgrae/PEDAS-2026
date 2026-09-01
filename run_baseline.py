"""CLI runner for baseline and ensemble model training and evaluation."""

import argparse
import pandas as pd
from src.features.extractor import PhishingFeatureExtractor
from src.models.baseline import BaselineModelTrainer
from src.models.ensemble import WeightedBlender
from src.models.validation import NestedThresholdOptimizer
from src.models.metrics import calculate_classification_metrics
from src.utils.config import BENCHMARK_DATA_DIR, RANDOM_STATE


def main():
    parser = argparse.ArgumentParser(description="PeDaS 2026 Phishing Detection Runner")
    parser.add_argument(
        "--model",
        type=str,
        default="lightgbm",
        choices=["lightgbm", "xgboost", "catboost", "rf", "ensemble"],
        help="Classifier architecture ('ensemble' combines LightGBM + CatBoost + XGBoost)",
    )
    parser.add_argument(
        "--folds",
        type=int,
        default=5,
        help="Number of K-Folds",
    )
    parser.add_argument(
        "--group-kfold",
        action="store_true",
        help="Use StratifiedGroupKFold by registered domain to prevent domain group leakage",
    )
    parser.add_argument(
        "--ngram-stacking",
        action="store_true",
        help="Include Character N-Gram TF-IDF linear stacking meta-feature",
    )
    parser.add_argument(
        "--threshold-tuning",
        action="store_true",
        help="Perform nested threshold search to maximize F1-Macro",
    )
    args = parser.parse_args()

    data_path = BENCHMARK_DATA_DIR / "sample_phishing_id.csv"
    print(f"[*] Loading benchmark data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"[*] Loaded {len(df)} samples ({sum(df['label'] == 1)} Phishing, {sum(df['label'] == 0)} Legitimate).")

    print("[*] Extracting features (Lexical + Indonesian Brand Spoofing" + (" + N-Gram Stacking" if args.ngram_stacking else "") + ")...")
    extractor = PhishingFeatureExtractor(
        include_dns=False,
        include_whois=False,
        include_ngram_stacking=args.ngram_stacking,
    )
    features_df = extractor.transform(df, url_col="url", show_progress=False, y=df["label"].values)
    print(f"[*] Extracted {features_df.shape[1]} features successfully.")

    y = df["label"].values
    urls = df["url"].values

    if args.model == "ensemble":
        print(f"\n[*] Running Multi-GBDT Ensemble (LightGBM + CatBoost + XGBoost) with {args.folds} Folds...")
        blender = WeightedBlender(model_names=["lightgbm", "catboost", "xgboost"], n_splits=args.folds, random_state=RANDOM_STATE)
        res = blender.fit_cross_validate(features_df, y, urls=urls, use_group_kfold=args.group_kfold)

        print("\n" + "=" * 55)
        print("ENSEMBLE BLENDING EVALUATION RESULTS:")
        print("=" * 55)
        print("  Model Weights         :", res["model_weights"])
        print(f"  Optimal Threshold     : {res['optimal_threshold']}")
        print("=" * 55)
        print("  METRICS AT DEFAULT THRESHOLD (0.50):")
        for k, v in res["metrics_at_05"].items():
            print(f"    {k:<20}: {v}")
        print("=" * 55)
        print(f"  METRICS AT OPTIMAL THRESHOLD ({res['optimal_threshold']}):")
        for k, v in res["metrics_at_optimal_threshold"].items():
            print(f"    {k:<20}: {v}")
        print("=" * 55)

    else:
        split_type = "StratifiedGroupKFold (Domain)" if args.group_kfold else "StratifiedKFold"
        print(f"\n[*] Running {split_type} ({args.folds} Folds) with {args.model.upper()}...")
        trainer = BaselineModelTrainer(model_type=args.model, n_splits=args.folds, random_state=RANDOM_STATE)
        metrics, fi_df, oof_probs = trainer.cross_validate(features_df, y, urls=urls, use_group_kfold=args.group_kfold)

        print("\n" + "=" * 50)
        print(f"EVALUATION RESULTS ({args.model.upper()}):")
        print("=" * 50)
        for k, v in metrics.items():
            if k != "fold_f1_macros":
                print(f"  {k:<22}: {v}")
        print("=" * 50)
        print(f"  Fold F1-Macros        : {metrics['fold_f1_macros']}")

        if args.threshold_tuning:
            print("\n[*] Running Threshold Optimization on OOF Probabilities...")
            thresh_opt = NestedThresholdOptimizer(metric="f1_macro")
            best_t, best_f1 = thresh_opt.find_best_threshold(y, oof_probs)
            opt_preds = (oof_probs >= best_t).astype(int)
            opt_metrics = calculate_classification_metrics(y, opt_preds, oof_probs)
            print(f"  Optimal Threshold     : {best_t}")
            print(f"  F1-Macro at Threshold : {opt_metrics['f1_macro']} (gain: {opt_metrics['f1_macro'] - metrics['f1_macro']:+.4f})")
            print(f"  FPR at Threshold      : {opt_metrics['fpr']}")

        print("\n[*] Top 10 Most Discriminative Features:")
        for idx, row in fi_df.head(10).iterrows():
            print(f"  {idx+1:2d}. {row['feature']:<30} (importance: {row['importance']:.4f})")


if __name__ == "__main__":
    main()
