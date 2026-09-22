#!/usr/bin/env python
"""PeDaS 2026 - Explainability (XAI) Evidence Generator for the Final Round Jury.

This script computes EMPIRICAL, REPRODUCIBLE explainability artifacts directly from
the trained HybridProbabilisticBlender. Every number written to reports/xai_metrics.json
is generated here; nothing is asserted without a computed artifact.

Artifacts produced:
1. LightGBM tabular feature importance (gain + split) over the 56 engineered features.
2. LinearSVC character n-gram coefficient attribution: top positive/negative n-grams
   per canonical threat class (the interpretable sub-word evidence).
3. Multiclass Platt calibration diagnostics: Expected Calibration Error (ECE) and
   per-class reliability bins (margin -> posterior probability).
4. Cost-sensitive Bayes threshold table (offsets_ per class) and its empirical effect
   on in-fold Macro-F1.
5. False-positive / false-negative anchoring audit requested by the jury:
   posterior probabilities for specific test rows (e.g. storefront candidates).

Usage:
    python scripts/explain_model.py \
        --train official/training.csv \
        --predict official/predict.csv \
        --output reports/xai_metrics.json \
        --figures reports/figures
"""

import sys
import json
import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from src.cleaner import CANONICAL_CLASSES
from src.alternatives.data_centric_denoiser import DataCentricDenoiser
from src.models.hybrid_blender import HybridProbabilisticBlender
from src.models.threshold_optimizer import (
    calculate_fast_macro_f1,
    MulticlassThresholdOptimizer,
)


def _jsonable(value: Any) -> Any:
    """Recursively converts numpy types into JSON-serializable Python types."""
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def build_model(train_path: Path):
    """Trains the production model deterministically (seed 2026) and returns it."""
    train_raw = pd.read_csv(train_path)
    denoiser = DataCentricDenoiser()
    train_clean = denoiser.fit_transform(train_raw)
    # text_weight=0.60 matches the PRODUCTION pipeline (run_pedas_pipeline.py:93).
    # The class default is 0.70, so it must be set explicitly for consistency.
    blender = HybridProbabilisticBlender(text_weight=0.60, random_state=2026)
    blender.fit(train_clean, optimize_thresholds=True)
    return blender, train_clean


def _supervised_signal(blender: HybridProbabilisticBlender, train_clean: pd.DataFrame):
    """Reconstructs the supervised blended OOF-free probabilities on the training data.

    Note: this is in-sample (training) evidence intended for attribution and calibration
    diagnostics, NOT a generalization estimate. Generalization is reported separately
    by scripts/test_hybrid_cv.py via 5-fold OOF.
    """
    return blender.predict_proba(train_clean)


def lgb_feature_importance(blender: HybridProbabilisticBlender) -> Dict[str, Any]:
    """Extracts real LightGBM gain/split importance mapped to feature names."""
    lgb = blender.lgb_clf
    extractor = blender.domain_extractor
    names = list(extractor.feature_names_)

    booster = lgb.booster_
    split_importance = booster.feature_importance(importance_type="split")
    gain_importance = booster.feature_importance(importance_type="gain")

    total_gain = float(np.sum(gain_importance)) or 1.0
    rows = []
    for i, name in enumerate(names):
        rows.append({
            "feature": name,
            "gain": float(gain_importance[i]),
            "gain_pct": float(gain_importance[i] / total_gain * 100.0),
            "split": int(split_importance[i]),
        })
    rows.sort(key=lambda r: r["gain"], reverse=True)
    return {
        "n_features": len(names),
        "total_gain": total_gain,
        "top_gain": rows[:20],
        "all_features": rows,
    }


def split_composite_text(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Splits the composite text back into its four semantic fields.

    Composite layout (src/cleaner.py:99-104):
        'url <url> brand <brand> sld <sld> registrar <registrar>'
    Character n-grams that straddle field boundaries (e.g. 'url b', 'l bra') are
    template artifacts, not threat evidence. This function isolates each field so
    n-gram attribution reflects real signal rather than concatenation artifacts.
    """
    from src.cleaner import clean_url, clean_brand
    return {
        "url": df["url"].apply(clean_url).astype(str).str.lower(),
        "brand": df["brand"].apply(clean_brand).astype(str).str.lower(),
        "sld": df["sld"].fillna("unknown_sld").astype(str).str.strip().str.lower(),
        "registrar": df["registrar"].fillna("unknown_registrar").astype(str).str.strip().str.lower(),
    }


def svc_ngram_attribution(
    train_clean: pd.DataFrame,
    top_k: int = 15,
    random_state: int = 2026,
) -> Dict[str, Any]:
    """Trains an interpretable field-isolated surrogate LinearSVC for n-gram attribution.

    The production SVC (src/models/hybrid_blender.py:84-98) consumes a single TF-IDF
    vectorizer over composite text, which mixes the four semantic fields and injects
    concatenation-boundary n-grams. To obtain jury-defensible, human-readable evidence,
    we fit a SURROGATE LinearSVC with identical architecture but four field-isolated
    char n-gram blocks (url / brand / sld / registrar). Coefficients are then attributed
    to real tokens such as 'gacor', 'login', 'otp'.
    """
    from sklearn.svm import LinearSVC
    from sklearn.feature_extraction.text import TfidfVectorizer

    y = train_clean["category_clean"]
    fields = split_composite_text(train_clean)

    vectorizers: Dict[str, TfidfVectorizer] = {}
    blocks = []
    for name, series in fields.items():
        vec = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=3,
                              max_features=8000, sublinear_tf=True)
        blocks.append(vec.fit_transform(series))
        vectorizers[name] = vec

    from scipy.sparse import hstack
    X = hstack(blocks)
    clf = LinearSVC(C=1.0, class_weight="balanced", random_state=random_state,
                    dual=False, max_iter=3000)
    clf.fit(X, y)

    # Offsets per field block
    offsets = {}
    cursor = 0
    for name in fields:
        size = len(vectorizers[name].vocabulary_)
        offsets[name] = (cursor, cursor + size)
        cursor += size

    def _is_semantic(token: str) -> bool:
        """Filters scheme/TLD/punctuation template artifacts, keeping real tokens.

        Retains n-grams with >=3 alphanumeric characters that are not trivial
        sub-strings of the URL scheme or the masked/root scaffolding.
        """
        alnum = sum(ch.isalnum() for ch in token)
        if alnum < 3:
            return False
        lowered = token.lower().strip()
        scheme_fragments = {"http", "https", "tp", "ttps", "http:", "https:",
                            "p:", "p:/", "p://", "tp:", "tp:/", "tp://", "ttp:", "ttp:/",
                            "ttp://", "ttps:", "ttps:/", "ttps://"}
        if lowered in scheme_fragments:
            return False
        # Pure asterisk/dot/slash scaffolding with too few letters
        letters = sum(ch.isalpha() for ch in token)
        if letters < 3:
            return False
        return True

    classes = list(clf.classes_)
    result: Dict[str, Any] = {}
    for row_idx, class_label in enumerate(classes):
        coefs = clf.coef_[row_idx]
        merged: List[Dict[str, Any]] = []
        for name, (lo, hi) in offsets.items():
            try:
                vocab = vectorizers[name].get_feature_names_out()
            except AttributeError:
                vocab = vectorizers[name].get_feature_names()
            for j, token in enumerate(vocab):
                token_s = str(token)
                if not _is_semantic(token_s):
                    continue
                merged.append({
                    "ngram": token_s,
                    "field": name,
                    "coef": float(coefs[lo + j]),
                })
        merged.sort(key=lambda d: d["coef"], reverse=True)
        result[str(class_label)] = {
            "top_positive_ngrams": merged[:top_k],
            "top_negative_ngrams": merged[::-1][:top_k],
        }

    result["_meta"] = {
        "note": "Surrogate field-isolated LinearSVC for interpretability; same feature "
                "family as production model (char 3-5 n-gram + balanced class weight).",
        "field_features": {name: len(vec.vocabulary_) for name, vec in vectorizers.items()},
    }
    return result


def calibration_diagnostics(
    probas: np.ndarray,
    y_true: np.ndarray,
    n_bins: int = 10,
) -> Dict[str, Any]:
    """Computes per-class Expected Calibration Error (ECE) and reliability bins.

    For each class, confidence = P(y=c|x) and correctness = 1[prediction == c].
    NOTE: with the production decision rule (argmax on offset-adjusted probabilities),
    the top-1 confidence is more meaningful. We report both:
    - top1_ece: calibration of the predicted class confidence.
    - per_class: one-vs-rest reliability per class.
    """
    n_classes = probas.shape[1]
    pred_idx = probas.argmax(axis=1)
    top1_conf = probas[np.arange(len(probas)), pred_idx]
    top1_correct = (pred_idx == y_true).astype(float)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    def _ece(conf, correct):
        ece = 0.0
        bin_stats = []
        for b in range(n_bins):
            lo, hi = bins[b], bins[b + 1]
            mask = (conf >= lo) & (conf < hi) if b < n_bins - 1 else (conf >= lo) & (conf <= hi)
            if mask.sum() == 0:
                bin_stats.append({"lo": float(lo), "hi": float(hi), "count": 0,
                                  "avg_conf": None, "accuracy": None})
                continue
            avg_conf = float(conf[mask].mean())
            acc = float(correct[mask].mean())
            ece += (mask.sum() / len(conf)) * abs(avg_conf - acc)
            bin_stats.append({"lo": float(lo), "hi": float(hi), "count": int(mask.sum()),
                              "avg_conf": avg_conf, "accuracy": acc})
        return float(ece), bin_stats

    top1_ece, top1_bins = _ece(top1_conf, top1_correct)

    per_class = {}
    for c in range(n_classes):
        conf = probas[:, c]
        correct = (y_true == c).astype(float)
        ece_c, bins_c = _ece(conf, correct)
        per_class[CANONICAL_CLASSES[c]] = {
            "ece": ece_c,
            "prevalence": float(correct.mean()),
            "bins": bins_c,
        }

    return {
        "top1_ece": top1_ece,
        "top1_bins": top1_bins,
        "per_class": per_class,
        "mean_confidence": float(top1_conf.mean()),
        "top1_accuracy": float(top1_correct.mean()),
    }


def threshold_table(
    blender: HybridProbabilisticBlender,
    probas: np.ndarray,
    y_idx: np.ndarray,
) -> Dict[str, Any]:
    """Reports Bayes offsets and the empirical Macro-F1 effect of applying them."""
    offsets = blender.offsets_
    log_probas = np.log(np.clip(probas, 1e-12, 1.0))
    argmax_score = calculate_fast_macro_f1(
        log_probas, np.zeros_like(offsets), y_idx, len(CANONICAL_CLASSES)
    )
    shifted_score = calculate_fast_macro_f1(
        log_probas, offsets, y_idx, len(CANONICAL_CLASSES)
    )
    return {
        "offsets": {CANONICAL_CLASSES[i]: float(offsets[i]) for i in range(len(offsets))},
        "macro_f1_argmax_in_sample": float(argmax_score),
        "macro_f1_offset_in_sample": float(shifted_score),
        "delta_macro_f1": float(shifted_score - argmax_score),
        "note": "In-sample diagnostic (training data). Generalization reported via 5-fold OOF in scripts/test_hybrid_cv.py.",
    }


def row_posterior_audit(
    blender: HybridProbabilisticBlender,
    predict_df: pd.DataFrame,
    row_indices: List[int],
) -> List[Dict[str, Any]]:
    """Computes the full posterior distribution for specific test rows.

    Indices are 0-based DataFrame row positions. This turns any claimed rare-class
    anchor into auditable, model-derived evidence instead of a hardcoded label.
    """
    probas = blender.predict_proba(predict_df)
    audit = []
    for i in row_indices:
        if i < 0 or i >= len(predict_df):
            continue
        p = probas[i]
        order = np.argsort(p)[::-1]
        audit.append({
            "row_index": i,
            "id": str(predict_df.iloc[i]["id"]),
            "url": str(predict_df.iloc[i]["url"]),
            "argmax_class": CANONICAL_CLASSES[int(order[0])],
            "argmax_probability": float(p[order[0]]),
            "posterior": {CANONICAL_CLASSES[k]: float(p[k]) for k in order[:5]},
        })
    return audit


def oof_diagnostics(
    train_clean: pd.DataFrame,
    n_splits: int = 5,
    random_state: int = 2026,
) -> Dict[str, Any]:
    """Computes leak-free out-of-fold probabilities and their threshold diagnostics.

    This is the JURY-CRITICAL artifact: it shows the real generalization Macro-F1 and
    demonstrates that the Bayes offset step improves it, without in-sample optimism.
    """
    from src.evaluator import get_stratified_folds
    y = train_clean["category_clean"]
    class_to_idx = {c: i for i, c in enumerate(CANONICAL_CLASSES)}
    y_idx = y.map(class_to_idx).values
    C = len(CANONICAL_CLASSES)

    folds = get_stratified_folds(train_clean["composite_text"], y,
                                 n_splits=n_splits, random_state=random_state)
    oof = np.zeros((len(train_clean), C))
    for fold, (trn, val) in enumerate(folds):
        blender = HybridProbabilisticBlender(text_weight=0.60, random_state=random_state)
        blender.fit(train_clean.iloc[trn], optimize_thresholds=False)
        oof[val] = blender.predict_proba(train_clean.iloc[val])

    logp = np.log(np.clip(oof, 1e-12, 1.0))
    raw = calculate_fast_macro_f1(logp, np.zeros(C), y_idx, C)
    opt = MulticlassThresholdOptimizer(
        C=C, search_range=(-2.0, 2.0), n_steps=81, max_iter=3,
        frozen_classes=[], anchor_class=0,
    )
    opt.fit(logp, y_idx)
    shifted = calculate_fast_macro_f1(logp, opt.offsets_, y_idx, C)

    post = oof / oof.sum(axis=1, keepdims=True)
    pred = post.argmax(axis=1)
    conf = post[np.arange(len(post)), pred]
    correct = (pred == y_idx).astype(float)
    bins = np.linspace(0.0, 1.0, 11)
    ece = 0.0
    for b in range(10):
        lo, hi = bins[b], bins[b + 1]
        mask = (conf >= lo) & (conf < hi) if b < 9 else (conf >= lo) & (conf <= hi)
        if mask.sum():
            ece += (mask.sum() / len(conf)) * abs(conf[mask].mean() - correct[mask].mean())

    return {
        "n_splits": n_splits,
        "oof_macro_f1_argmax": float(raw),
        "oof_macro_f1_offset": float(shifted),
        "oof_delta_macro_f1": float(shifted - raw),
        "oof_offsets": {CANONICAL_CLASSES[i]: float(opt.offsets_[i]) for i in range(C)},
        "oof_top1_ece": float(ece),
        "oof_top1_accuracy": float(correct.mean()),
        "oof_mean_confidence": float(conf.mean()),
        "note": "Leak-free StratifiedKFold OOF. This is the honest generalization estimate.",
    }


def maybe_plot(blender, features, calibration, figures_dir: Path) -> List[str]:
    """Attempts to render diagnostic figures; silently skips if matplotlib is unavailable."""
    written = []
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return written

    figures_dir.mkdir(parents=True, exist_ok=True)

    top = features["top_gain"][:15][::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh([t["feature"] for t in top], [t["gain_pct"] for t in top], color="#2563eb")
    ax.set_xlabel("LightGBM gain (% of total)")
    ax.set_title("Top-15 Tabular Feature Contribution (LightGBM)")
    fig.tight_layout()
    p1 = figures_dir / "xai_lgb_top_features.png"
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    written.append(str(p1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot([0, 1], [0, 1], "k--", label="perfect calibration")
    bins = calibration["top1_bins"]
    xs = [b["avg_conf"] for b in bins if b["avg_conf"] is not None]
    ys = [b["accuracy"] for b in bins if b["accuracy"] is not None]
    ax.plot(xs, ys, "o-", color="#dc2626", label=f"model (ECE={calibration['top1_ece']:.4f})")
    ax.set_xlabel("Mean predicted confidence")
    ax.set_ylabel("Empirical accuracy")
    ax.set_title("Top-1 Reliability Diagram (Platt-calibrated blend)")
    ax.legend()
    fig.tight_layout()
    p2 = figures_dir / "xai_calibration_curve.png"
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    written.append(str(p2))

    offsets = blender.offsets_
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#16a34a" if o >= 0 else "#dc2626" for o in offsets]
    ax.bar(CANONICAL_CLASSES, offsets, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Bayes offset Delta_c (log-odds space)")
    ax.set_title("Cost-Sensitive Bayes Threshold Offsets per Threat Class")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    p3 = figures_dir / "xai_threshold_offsets.png"
    fig.savefig(p3, dpi=150)
    plt.close(fig)
    written.append(str(p3))

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--train", default="official/training.csv")
    parser.add_argument("--predict", default="official/predict.csv")
    parser.add_argument("--output", default="reports/xai_metrics.json")
    parser.add_argument("--figures", default="reports/figures")
    parser.add_argument("--audit-rows", default="1033,1345,117,10",
                        help="Comma-separated 0-based predict.csv row positions to audit.")
    args = parser.parse_args()

    train_path = Path(args.train) if Path(args.train).is_absolute() else REPO_ROOT / args.train
    predict_path = Path(args.predict) if Path(args.predict).is_absolute() else REPO_ROOT / args.predict
    output_path = Path(args.output) if Path(args.output).is_absolute() else REPO_ROOT / args.output
    figures_dir = Path(args.figures) if Path(args.figures).is_absolute() else REPO_ROOT / args.figures

    print("=" * 70)
    print("  PeDaS 2026 - EXPLAINABILITY (XAI) EVIDENCE GENERATOR")
    print("=" * 70)

    print("\n[1/6] Training production model (denoiser + hybrid blender, seed 2026)...")
    blender, train_clean = build_model(train_path)

    print("[2/6] Computing LightGBM tabular feature importance (gain/split)...")
    features = lgb_feature_importance(blender)
    for row in features["top_gain"][:5]:
        print(f"      {row['feature']:24s} gain={row['gain_pct']:5.2f}%  splits={row['split']}")

    print("      (feature importance is a model-structure diagnostic; "
          "honest generalization is reported in step 4)")

    print("[3/6] Extracting field-isolated LinearSVC n-gram attribution (surrogate)...")
    ngram_attr = svc_ngram_attribution(train_clean, random_state=2026)
    sample = ngram_attr.get("online gambling", {}).get("top_positive_ngrams", [])[:6]
    print("      top gambling n-grams: " + ", ".join(f"'{n['ngram']}'" for n in sample))

    print("[4/6] Computing leak-free OOF diagnostics (honest generalization)...")
    oof = oof_diagnostics(train_clean, n_splits=5, random_state=2026)
    print(f"      OOF Macro-F1: argmax={oof['oof_macro_f1_argmax']:.4f} -> "
          f"offset={oof['oof_macro_f1_offset']:.4f} "
          f"(delta {oof['oof_delta_macro_f1']:+.4f}) | ECE={oof['oof_top1_ece']:.4f}")

    print("[5/6] Computing in-sample calibration/threshold auxiliary view...")
    probas = _supervised_signal(blender, train_clean)
    y_idx = train_clean["category_clean"].map(
        {c: i for i, c in enumerate(CANONICAL_CLASSES)}
    ).values
    calibration = calibration_diagnostics(probas, y_idx)
    thresholds = threshold_table(blender, probas, y_idx)
    print(f"      in-sample (aux): argmax={thresholds['macro_f1_argmax_in_sample']:.4f} -> "
          f"offset={thresholds['macro_f1_offset_in_sample']:.4f}")

    print("[6/6] Auditing candidate rare-class anchor rows (posterior evidence)...")
    predict_df = pd.read_csv(predict_path)
    audit_rows = [int(x) for x in args.audit_rows.split(",") if x.strip() != ""]
    anchors = row_posterior_audit(blender, predict_df, audit_rows)
    for a in anchors:
        print(f"      row {a['row_index']:5d} argmax={a['argmax_class']:16s} "
              f"P={a['argmax_probability']:.4f} | {a['url'][:50]}")

    figures = maybe_plot(blender, features, calibration, figures_dir)

    with open(train_path, "rb") as f:
        train_md5 = hashlib.md5(f.read()).hexdigest()

    report = {
        "meta": {
            "seed": 2026,
            "text_weight": blender.text_weight,
            "gbdt_weight": blender.gbdt_weight,
            "n_canonical_classes": len(CANONICAL_CLASSES),
            "training_rows_after_denoise": int(len(train_clean)),
            "training_csv_md5": train_md5,
            "metric": "unweighted macro-F1 (zero_division=0)",
            "scope_warning": "Feature importance, n-gram attribution and calibration are "
                             "IN-SAMPLE diagnostics. Generalization is estimated separately "
                             "by 5-fold OOF cross-validation.",
        },
        "lightgbm_feature_importance": features,
        "linearsvc_ngram_attribution": ngram_attr,
        "oof_generalization": oof,
        "in_sample_calibration_aux": calibration,
        "in_sample_bayes_thresholds_aux": thresholds,
        "anchor_row_posterior_audit": anchors,
        "figures": figures,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(_jsonable(report), f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"  [OK] XAI report written to: {output_path}")
    if figures:
        print(f"  [OK] Figures written to:   {figures_dir}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
