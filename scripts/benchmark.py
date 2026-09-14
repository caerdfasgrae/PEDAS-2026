"""Benchmark Runner for PeDaS 2026 Models under 5-Fold Stratified CV.

Compares models deterministically using official competition Macro-F1.
"""

import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb

from src.cleaner import load_cleaned_datasets, CANONICAL_CLASSES
from src.pedas_features import extract_url_lexical_features, extract_domain_metadata_features, TfidfTextFeatureExtractor
from src.evaluator import get_stratified_folds, compute_metrics_report



def run_benchmark():
    print("Loading cleaned datasets...")
    train_df, predict_df = load_cleaned_datasets()
    
    y = train_df["category_clean"]
    folds = get_stratified_folds(train_df["composite_text"], y, n_splits=5, random_state=2026)
    
    # 1. Extract tabular & lexical features
    print("Extracting lexical and metadata features...")
    lexical_df = extract_url_lexical_features(train_df["url"])
    meta_df = extract_domain_metadata_features(train_df)
    
    # One-hot encode SLD (high correlation with target)
    sld_ohe = pd.get_dummies(train_df["sld"].fillna("unknown"), prefix="sld", dtype=float)
    
    tabular_features = pd.concat([lexical_df, meta_df, sld_ohe], axis=1)
    tabular_csr = csr_matrix(tabular_features.values)
    
    # --- MODEL 1: Workshop Baseline (LinearSVC on TF-IDF composite text only) ---
    print("\n[Model 1] Evaluating Workshop Baseline: TF-IDF (10k features) + LinearSVC...")
    oof_m1 = pd.Series(index=y.index, dtype=str)
    
    for fold, (trn_idx, val_idx) in enumerate(folds):
        tfidf = TfidfTextFeatureExtractor(ngram_range=(3, 5), min_df=2, max_features=10000)
        X_tr_tfidf = tfidf.fit_transform(train_df["composite_text"].iloc[trn_idx])
        X_va_tfidf = tfidf.transform(train_df["composite_text"].iloc[val_idx])
        
        clf = LinearSVC(C=1.0, class_weight="balanced", random_state=2026, max_iter=2000)
        clf.fit(X_tr_tfidf, y.iloc[trn_idx])
        oof_m1.iloc[val_idx] = clf.predict(X_va_tfidf)
        
    metrics_m1 = compute_metrics_report(y, oof_m1)
    print(f"--> Model 1 Macro-F1: {metrics_m1['macro_f1']:.4f}")

    # --- MODEL 2: Enhanced Linear Model (TF-IDF + Tabular Lexical/SLD) ---
    print("\n[Model 2] Evaluating Enhanced Hybrid LinearSVC: TF-IDF (15k) + Tabular Signals...")
    oof_m2 = pd.Series(index=y.index, dtype=str)
    
    for fold, (trn_idx, val_idx) in enumerate(folds):
        tfidf = TfidfTextFeatureExtractor(ngram_range=(3, 5), min_df=2, max_features=15000)
        X_tr_tfidf = tfidf.fit_transform(train_df["composite_text"].iloc[trn_idx])
        X_va_tfidf = tfidf.transform(train_df["composite_text"].iloc[val_idx])
        
        X_tr_combined = hstack([X_tr_tfidf, tabular_csr[trn_idx]])
        X_va_combined = hstack([X_va_tfidf, tabular_csr[val_idx]])
        
        clf = LinearSVC(C=1.0, class_weight="balanced", random_state=2026, max_iter=2000)
        clf.fit(X_tr_combined, y.iloc[trn_idx])
        oof_m2.iloc[val_idx] = clf.predict(X_va_combined)
        
    metrics_m2 = compute_metrics_report(y, oof_m2)
    print(f"--> Model 2 Macro-F1: {metrics_m2['macro_f1']:.4f}")
    
    # --- MODEL 3: Logistic Regression with Multiclass L2 + Balanced Weights ---
    print("\n[Model 3] Evaluating Logistic Regression (L2 Balanced)...")
    oof_m3 = pd.Series(index=y.index, dtype=str)
    
    for fold, (trn_idx, val_idx) in enumerate(folds):
        tfidf = TfidfTextFeatureExtractor(ngram_range=(3, 5), min_df=2, max_features=15000)
        X_tr_tfidf = tfidf.fit_transform(train_df["composite_text"].iloc[trn_idx])
        X_va_tfidf = tfidf.transform(train_df["composite_text"].iloc[val_idx])
        
        X_tr_combined = hstack([X_tr_tfidf, tabular_csr[trn_idx]])
        X_va_combined = hstack([X_va_tfidf, tabular_csr[val_idx]])
        
        clf = LogisticRegression(C=2.0, class_weight="balanced", random_state=2026, max_iter=1000)
        clf.fit(X_tr_combined, y.iloc[trn_idx])
        oof_m3.iloc[val_idx] = clf.predict(X_va_combined)
        
    metrics_m3 = compute_metrics_report(y, oof_m3)
    print(f"--> Model 3 Macro-F1: {metrics_m3['macro_f1']:.4f}")

    print("\n=== SUMMARY COMPARISON ===")
    print(f"Model 1 (Workshop Baseline)    : Macro-F1 = {metrics_m1['macro_f1']:.4f}")
    print(f"Model 2 (Enhanced LinearSVC)   : Macro-F1 = {metrics_m2['macro_f1']:.4f}")
    print(f"Model 3 (Logistic Regression)  : Macro-F1 = {metrics_m3['macro_f1']:.4f}")
    
    print("\nPer-class F1 for Model 2 (Enhanced LinearSVC):")
    for cls, f1 in metrics_m2["per_class_f1"].items():
        print(f"  {cls:18s}: {f1:.4f}")


if __name__ == "__main__":
    run_benchmark()
