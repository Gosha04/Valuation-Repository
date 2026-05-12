"""Sweep behavior tag thresholds against reviewed validation labels."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PREDICTIONS = PROJECT_DIR / "Final/subclusters_behavior/test_behavior_tags.json"
DEFAULT_LABELS = PROJECT_DIR / "Final/subclusters_behavior/revised_behavior_tags.json"
DEFAULT_OUTPUT = PROJECT_DIR / "Final/subclusters_behavior/threshold_sweep_results.json"
DEFAULT_CSV = PROJECT_DIR / "Final/subclusters_behavior/threshold_sweep_results.csv"
DEFAULT_THRESHOLDS = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
DEFAULT_MAX_TAGS = [1, 2, 3, 4, 5]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Try different decision thresholds and max-predicted-tag counts "
            "against reviewed multi-label behavior tags."
        )
    )
    parser.add_argument(
        "--predictions",
        type=Path,
        default=DEFAULT_PREDICTIONS,
        help="classification.py JSON output containing top_tags scores.",
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=DEFAULT_LABELS,
        help="Reviewed labels JSON with entries containing true_tags.",
    )
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=DEFAULT_THRESHOLDS,
        help="Decision score thresholds to test.",
    )
    parser.add_argument(
        "--max-tags",
        type=int,
        nargs="+",
        default=DEFAULT_MAX_TAGS,
        help="Maximum predicted tag counts to test.",
    )
    parser.add_argument(
        "--selection-metric",
        choices=[
            "micro_f1",
            "macro_f1",
            "mean_jaccard",
            "exact_match_accuracy",
            "primary_accuracy",
        ],
        default="micro_f1",
        help="Metric used to choose the best setting.",
    )
    parser.add_argument(
        "--include-unreviewed",
        action="store_true",
        help="Include entries whose review_status is not reviewed.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow no predicted tags when all scores are below threshold.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_label_entries(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return data["entries"]
    raise SystemExit("Labels JSON must be a list or an object with an entries list.")


def key_from_metadata(metadata: dict[str, Any]) -> tuple[Any, ...]:
    return (
        metadata.get("source_split"),
        metadata.get("source_row"),
        metadata.get("response_index"),
        metadata.get("prompt_id"),
    )


def safe_divide(numerator: int | float, denominator: int | float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def f1_score(precision: float, recall: float) -> float:
    return safe_divide(2 * precision * recall, precision + recall)


def prediction_map(predictions_data: dict[str, Any]) -> dict[tuple[Any, ...], dict[str, Any]]:
    mapped = {}
    for item in predictions_data.get("results", []):
        mapped[key_from_metadata(item.get("metadata", {}))] = item
    return mapped


def ranked_tags(prediction: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = prediction.get("top_tags") or []
    if not ranked:
        ranked = [{"tag": tag, "score": 0.0} for tag in prediction.get("predicted_tags", [])]
    return sorted(ranked, key=lambda item: float(item.get("score", 0.0)), reverse=True)


def predicted_at_setting(
    prediction: dict[str, Any],
    threshold: float,
    max_tags: int,
    allow_empty: bool,
) -> list[str]:
    ranked = ranked_tags(prediction)
    predicted = [
        str(item["tag"])
        for item in ranked
        if float(item.get("score", 0.0)) >= threshold
    ][:max_tags]
    if not predicted and ranked and not allow_empty:
        predicted = [str(ranked[0]["tag"])]
    return predicted


def collect_tags(
    reviewed: list[dict[str, Any]],
    predictions: dict[tuple[Any, ...], dict[str, Any]],
) -> list[str]:
    tags = {tag for entry in reviewed for tag in entry.get("true_tags", [])}
    for prediction in predictions.values():
        tags.update(str(item["tag"]) for item in ranked_tags(prediction))
        tags.update(prediction.get("predicted_tags", []))
    return sorted(tags)


def evaluate_setting(
    reviewed: list[dict[str, Any]],
    predictions: dict[tuple[Any, ...], dict[str, Any]],
    tags: list[str],
    threshold: float,
    max_tags: int,
    allow_empty: bool,
) -> dict[str, Any]:
    exact_matches = 0
    jaccard_sum = 0.0
    hamming_errors = 0
    primary_total = 0
    primary_correct = 0
    predicted_tag_counts = []
    per_tag_counts = {
        tag: {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        for tag in tags
    }

    for entry in reviewed:
        prediction = predictions[key_from_metadata(entry["metadata"])]
        true_tags = set(entry.get("true_tags", []))
        predicted_tags_list = predicted_at_setting(
            prediction=prediction,
            threshold=threshold,
            max_tags=max_tags,
            allow_empty=allow_empty,
        )
        predicted_tags = set(predicted_tags_list)
        predicted_tag_counts.append(len(predicted_tags))

        exact_matches += int(true_tags == predicted_tags)
        jaccard_sum += safe_divide(len(true_tags & predicted_tags), len(true_tags | predicted_tags))
        hamming_errors += len(true_tags ^ predicted_tags)

        true_primary = entry.get("primary_tag") or next(iter(entry.get("true_tags", [])), None)
        predicted_primary = predicted_tags_list[0] if predicted_tags_list else None
        if true_primary is not None:
            primary_total += 1
            primary_correct += int(true_primary == predicted_primary)

        for tag in tags:
            true_has_tag = tag in true_tags
            predicted_has_tag = tag in predicted_tags
            counts = per_tag_counts[tag]
            if true_has_tag and predicted_has_tag:
                counts["tp"] += 1
            elif not true_has_tag and predicted_has_tag:
                counts["fp"] += 1
            elif true_has_tag and not predicted_has_tag:
                counts["fn"] += 1
            else:
                counts["tn"] += 1

    per_tag_metrics = {}
    for tag, counts in per_tag_counts.items():
        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        per_tag_metrics[tag] = {
            **counts,
            "support": tp + fn,
            "predicted": tp + fp,
            "precision": precision,
            "recall": recall,
            "f1": f1_score(precision, recall),
        }

    tp = sum(counts["tp"] for counts in per_tag_counts.values())
    fp = sum(counts["fp"] for counts in per_tag_counts.values())
    fn = sum(counts["fn"] for counts in per_tag_counts.values())
    micro_precision = safe_divide(tp, tp + fp)
    micro_recall = safe_divide(tp, tp + fn)
    macro_precision = safe_divide(
        sum(stats["precision"] for stats in per_tag_metrics.values()),
        len(per_tag_metrics),
    )
    macro_recall = safe_divide(
        sum(stats["recall"] for stats in per_tag_metrics.values()),
        len(per_tag_metrics),
    )
    macro_f1 = safe_divide(
        sum(stats["f1"] for stats in per_tag_metrics.values()),
        len(per_tag_metrics),
    )

    return {
        "threshold": threshold,
        "max_tags": max_tags,
        "reviewed_examples": len(reviewed),
        "mean_predicted_tags": safe_divide(sum(predicted_tag_counts), len(predicted_tag_counts)),
        "exact_match_accuracy": safe_divide(exact_matches, len(reviewed)),
        "mean_jaccard": safe_divide(jaccard_sum, len(reviewed)),
        "hamming_loss": safe_divide(hamming_errors, len(reviewed) * len(tags)),
        "primary_accuracy": safe_divide(primary_correct, primary_total),
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": f1_score(micro_precision, micro_recall),
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "per_tag": per_tag_metrics,
    }


def csv_row(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: result[key]
        for key in [
            "threshold",
            "max_tags",
            "reviewed_examples",
            "mean_predicted_tags",
            "exact_match_accuracy",
            "mean_jaccard",
            "hamming_loss",
            "primary_accuracy",
            "micro_precision",
            "micro_recall",
            "micro_f1",
            "macro_precision",
            "macro_recall",
            "macro_f1",
        ]
    }


def write_csv(path: Path, results: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [csv_row(result) for result in results]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    predictions_data = load_json(args.predictions)
    labels_data = load_json(args.labels)
    reviewed = [
        entry
        for entry in normalize_label_entries(labels_data)
        if args.include_unreviewed or entry.get("review_status") == "reviewed"
    ]
    if not reviewed:
        raise SystemExit("No reviewed entries found. Use --include-unreviewed to include all labels.")

    predictions = prediction_map(predictions_data)
    missing = [
        entry.get("id", str(index))
        for index, entry in enumerate(reviewed)
        if key_from_metadata(entry.get("metadata", {})) not in predictions
    ]
    if missing:
        raise SystemExit(f"{len(missing)} labels did not match predictions: {missing[:5]}")

    tags = collect_tags(reviewed, predictions)
    results = []
    for threshold in args.thresholds:
        for max_tags in args.max_tags:
            results.append(
                evaluate_setting(
                    reviewed=reviewed,
                    predictions=predictions,
                    tags=tags,
                    threshold=threshold,
                    max_tags=max_tags,
                    allow_empty=args.allow_empty,
                )
            )

    results.sort(
        key=lambda item: (
            item[args.selection_metric],
            item["mean_jaccard"],
            item["micro_f1"],
            -item["mean_predicted_tags"],
        ),
        reverse=True,
    )
    best = results[0]

    payload = {
        "predictions": str(args.predictions),
        "labels": str(args.labels),
        "selection_metric": args.selection_metric,
        "thresholds": args.thresholds,
        "max_tags": args.max_tags,
        "allow_empty": args.allow_empty,
        "best": best,
        "results": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_csv(args.csv_output, results)

    print(
        json.dumps(
            {
                "selection_metric": args.selection_metric,
                "best_threshold": best["threshold"],
                "best_max_tags": best["max_tags"],
                "best_micro_f1": best["micro_f1"],
                "best_macro_f1": best["macro_f1"],
                "best_mean_jaccard": best["mean_jaccard"],
                "best_exact_match_accuracy": best["exact_match_accuracy"],
                "best_primary_accuracy": best["primary_accuracy"],
                "best_mean_predicted_tags": best["mean_predicted_tags"],
            },
            indent=2,
        )
    )
    print(f"Wrote JSON: {args.output}")
    print(f"Wrote CSV: {args.csv_output}")


if __name__ == "__main__":
    main()
