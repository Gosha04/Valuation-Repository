"""Validate behavior tag predictions against reviewed labels."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PREDICTIONS = PROJECT_DIR / "Final/subclusters_behavior/test_behavior_tags.json"
DEFAULT_LABELS = PROJECT_DIR / "Final/subclusters_behavior/revised_behavior_tags.json"
DEFAULT_OUTPUT = PROJECT_DIR / "Final/subclusters_behavior/behavior_validation_metrics.json"
DEFAULT_DISAGREEMENTS = PROJECT_DIR / "Final/subclusters_behavior/behavior_validation_disagreements.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare predicted behavior tags against reviewed labels."
    )
    parser.add_argument(
        "--predictions",
        type=Path,
        default=DEFAULT_PREDICTIONS,
        help="JSON output from classification.py.",
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=DEFAULT_LABELS,
        help="Reviewed labels JSON with entries containing true_tags.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="JSON metrics output path.",
    )
    parser.add_argument(
        "--disagreements-output",
        type=Path,
        default=DEFAULT_DISAGREEMENTS,
        help="CSV output path for examples with missing or extra predicted tags.",
    )
    parser.add_argument(
        "--include-unreviewed",
        action="store_true",
        help="Include entries whose review_status is not reviewed.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_entries(data: Any) -> list[dict[str, Any]]:
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


def summarize_predictions(predictions_data: dict[str, Any]) -> dict[tuple[Any, ...], dict[str, Any]]:
    prediction_map = {}
    for item in predictions_data.get("results", []):
        metadata = item.get("metadata", {})
        prediction_map[key_from_metadata(metadata)] = item
    return prediction_map


def binary_confusion_for_tags(
    reviewed: list[dict[str, Any]],
    prediction_map: dict[tuple[Any, ...], dict[str, Any]],
    tags: list[str],
) -> dict[str, dict[str, float | int]]:
    metrics = {}
    for tag in tags:
        tp = fp = fn = tn = 0
        for entry in reviewed:
            prediction = prediction_map[key_from_metadata(entry["metadata"])]
            true_tags = set(entry.get("true_tags", []))
            predicted_tags = set(prediction.get("predicted_tags", []))
            true_has_tag = tag in true_tags
            predicted_has_tag = tag in predicted_tags
            if true_has_tag and predicted_has_tag:
                tp += 1
            elif not true_has_tag and predicted_has_tag:
                fp += 1
            elif true_has_tag and not predicted_has_tag:
                fn += 1
            else:
                tn += 1

        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        metrics[tag] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "support": tp + fn,
            "predicted": tp + fp,
            "precision": precision,
            "recall": recall,
            "f1": f1_score(precision, recall),
        }
    return metrics


def primary_confusion_matrix(
    reviewed: list[dict[str, Any]],
    prediction_map: dict[tuple[Any, ...], dict[str, Any]],
    tags: list[str],
) -> dict[str, Any]:
    matrix = {true_tag: {predicted_tag: 0 for predicted_tag in tags} for true_tag in tags}
    total = 0
    correct = 0
    for entry in reviewed:
        prediction = prediction_map[key_from_metadata(entry["metadata"])]
        true_primary = entry.get("primary_tag") or next(iter(entry.get("true_tags", [])), None)
        predicted_tags = prediction.get("predicted_tags", [])
        predicted_primary = predicted_tags[0] if predicted_tags else None
        if true_primary not in matrix or predicted_primary not in tags:
            continue
        matrix[true_primary][predicted_primary] += 1
        total += 1
        correct += int(true_primary == predicted_primary)

    return {
        "accuracy": safe_divide(correct, total),
        "total": total,
        "labels": tags,
        "matrix": matrix,
    }


def overall_metrics(
    reviewed: list[dict[str, Any]],
    prediction_map: dict[tuple[Any, ...], dict[str, Any]],
    per_tag: dict[str, dict[str, float | int]],
    tags: list[str],
) -> dict[str, float | int]:
    exact_matches = 0
    jaccard_sum = 0.0
    hamming_errors = 0

    for entry in reviewed:
        prediction = prediction_map[key_from_metadata(entry["metadata"])]
        true_tags = set(entry.get("true_tags", []))
        predicted_tags = set(prediction.get("predicted_tags", []))
        exact_matches += int(true_tags == predicted_tags)
        jaccard_sum += safe_divide(len(true_tags & predicted_tags), len(true_tags | predicted_tags))
        hamming_errors += len(true_tags ^ predicted_tags)

    tp = sum(int(stats["tp"]) for stats in per_tag.values())
    fp = sum(int(stats["fp"]) for stats in per_tag.values())
    fn = sum(int(stats["fn"]) for stats in per_tag.values())
    micro_precision = safe_divide(tp, tp + fp)
    micro_recall = safe_divide(tp, tp + fn)
    macro_precision = safe_divide(sum(float(stats["precision"]) for stats in per_tag.values()), len(per_tag))
    macro_recall = safe_divide(sum(float(stats["recall"]) for stats in per_tag.values()), len(per_tag))
    macro_f1 = safe_divide(sum(float(stats["f1"]) for stats in per_tag.values()), len(per_tag))

    return {
        "reviewed_examples": len(reviewed),
        "tag_count": len(tags),
        "exact_match_accuracy": safe_divide(exact_matches, len(reviewed)),
        "mean_jaccard": safe_divide(jaccard_sum, len(reviewed)),
        "hamming_loss": safe_divide(hamming_errors, len(reviewed) * len(tags)),
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": f1_score(micro_precision, micro_recall),
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
    }


def confusion_pairs(
    reviewed: list[dict[str, Any]],
    prediction_map: dict[tuple[Any, ...], dict[str, Any]],
) -> dict[str, int]:
    pairs: Counter[str] = Counter()
    for entry in reviewed:
        prediction = prediction_map[key_from_metadata(entry["metadata"])]
        true_tags = set(entry.get("true_tags", []))
        predicted_tags = set(prediction.get("predicted_tags", []))
        for missing in sorted(true_tags - predicted_tags):
            for extra in sorted(predicted_tags - true_tags):
                pairs[f"{missing} -> {extra}"] += 1
    return dict(pairs.most_common(50))


def disagreement_rows(
    reviewed: list[dict[str, Any]],
    prediction_map: dict[tuple[Any, ...], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for entry in reviewed:
        prediction = prediction_map[key_from_metadata(entry["metadata"])]
        true_tags = set(entry.get("true_tags", []))
        predicted_tags = set(prediction.get("predicted_tags", []))
        missing = sorted(true_tags - predicted_tags)
        extra = sorted(predicted_tags - true_tags)
        if not missing and not extra:
            continue
        rows.append(
            {
                "id": entry.get("id", ""),
                "source_row": entry.get("metadata", {}).get("source_row", ""),
                "response_index": entry.get("metadata", {}).get("response_index", ""),
                "true_tags": ", ".join(entry.get("true_tags", [])),
                "predicted_tags": ", ".join(prediction.get("predicted_tags", [])),
                "missing_tags": ", ".join(missing),
                "extra_tags": ", ".join(extra),
                "assistant_preview": entry.get("assistant_output", "")[:300].replace("\n", " "),
            }
        )
    return rows


def write_disagreements(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "id",
            "source_row",
            "response_index",
            "true_tags",
            "predicted_tags",
            "missing_tags",
            "extra_tags",
            "assistant_preview",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    predictions_data = load_json(args.predictions)
    label_entries = normalize_entries(load_json(args.labels))
    reviewed = [
        entry
        for entry in label_entries
        if args.include_unreviewed or entry.get("review_status") == "reviewed"
    ]
    if not reviewed:
        raise SystemExit("No reviewed entries found. Use --include-unreviewed to include all labels.")

    prediction_map = summarize_predictions(predictions_data)
    missing = [
        entry.get("id", str(index))
        for index, entry in enumerate(reviewed)
        if key_from_metadata(entry.get("metadata", {})) not in prediction_map
    ]
    if missing:
        raise SystemExit(f"{len(missing)} reviewed labels did not match predictions: {missing[:5]}")

    support_counts = predictions_data.get("support_vector_counts") or {}
    tags = sorted(
        set(support_counts.keys())
        | {tag for result in prediction_map.values() for tag in result.get("predicted_tags", [])}
        | {tag for entry in reviewed for tag in entry.get("true_tags", [])}
        | {entry.get("primary_tag") for entry in reviewed if entry.get("primary_tag")}
    )

    per_tag = binary_confusion_for_tags(reviewed, prediction_map, tags)
    primary_matrix = primary_confusion_matrix(reviewed, prediction_map, tags)
    disagreements = disagreement_rows(reviewed, prediction_map)

    payload = {
        "predictions": str(args.predictions),
        "labels": str(args.labels),
        "overall": overall_metrics(reviewed, prediction_map, per_tag, tags),
        "per_tag": per_tag,
        "primary_confusion_matrix": primary_matrix,
        "common_multilabel_confusions": confusion_pairs(reviewed, prediction_map),
        "disagreement_count": len(disagreements),
        "disagreements_csv": str(args.disagreements_output),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_disagreements(args.disagreements_output, disagreements)
    print(json.dumps(payload["overall"], indent=2))
    print(f"Wrote metrics: {args.output}")
    print(f"Wrote disagreements: {args.disagreements_output}")


if __name__ == "__main__":
    main()
