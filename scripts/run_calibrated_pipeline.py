"""Runner script for the calibrated domain ensemble pipeline."""

import sys
sys.path.insert(0, ".")
import pandas as pd
from src.cleaner import CANONICAL_CLASSES
from src.models.calibrated_ensemble_pipeline import run_cross_validation, train_full_model_and_predict

def main():
    print("=" * 60)
    print("PeDaS 2026: Calibrated Domain Ensemble Pipeline Evaluation")
    print("=" * 60)

    print("\n--- Phase 1: 5-Fold Stratified Cross-Validation ---")
    cv_res = run_cross_validation(random_state=2026)

    rep_uncal = cv_res["uncalibrated_report"]
    rep_nested = cv_res["nested_calibrated_report"]
    rep_global = cv_res["global_calibrated_report"]

    print("\n" + "=" * 40)
    print("CROSS-VALIDATION RESULTS SUMMARY")
    print("=" * 40)
    print(f"1. Baseline Uncalibrated Macro-F1 : {rep_uncal['macro_f1']:.4f}")
    print(f"2. Nested Calibrated Macro-F1    : {rep_nested['macro_f1']:.4f} (Strictly Leak-Free OOF)")
    print(f"3. Global Calibrated Macro-F1    : {rep_global['macro_f1']:.4f} (Full OOF Operating Point)")

    print("\n--- Per-Class F1 Breakdown Comparison ---")
    header = f"{'Class':<18} | {'Uncalibrated':<12} | {'Nested Cal':<12} | {'Global Cal':<12}"
    print(header)
    print("-" * len(header))
    for c in CANONICAL_CLASSES:
        f1_u = rep_uncal["per_class_f1"].get(c, 0.0)
        f1_n = rep_nested["per_class_f1"].get(c, 0.0)
        f1_g = rep_global["per_class_f1"].get(c, 0.0)
        print(f"{c:<18} | {f1_u:<12.4f} | {f1_n:<12.4f} | {f1_g:<12.4f}")

    print("\n--- Global Calibrated Confusion Matrix ---")
    cm_df = pd.DataFrame(rep_global["confusion_matrix"], index=CANONICAL_CLASSES, columns=CANONICAL_CLASSES)
    print(cm_df.to_string())

    print("\n--- Learned Global Threshold Offsets ---")
    for c, off in cv_res["global_offsets"].items():
        print(f"  {c:<18}: {off:+.4f}")

    print("\n" + "=" * 40)
    print("--- Phase 2: Full Training & Official Submission ---")
    print("=" * 40)
    sub_df = train_full_model_and_predict(
        train_path="official/training.csv",
        predict_path="official/predict.csv",
        output_submission_path="official/submission_calibrated_ensemble.csv",
        global_offsets=cv_res["global_offsets"],
        random_state=2026,
    )
    print("\n[SUCCESS] Pipeline execution, validation, and submission export complete.")

if __name__ == "__main__":
    main()
