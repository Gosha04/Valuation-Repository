"""Classify new assistant responses into behavior valuation tags.

This trains a one-vs-rest linear SVM from the existing subcluster behavior
tag matrix, then scores new responses one at a time. The feature space is
intentionally behavior-oriented: length, structure, openings, hedging,
disclaimers, warmth, and similar response-shape signals.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SUBCLUSTER_DIR = PROJECT_DIR / "Final/subclusters_behavior"
DEFAULT_TAGS_PATH = DEFAULT_SUBCLUSTER_DIR / "behavior_valuation_tags.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tag assistant responses with behavior-oriented valuation labels."
    )
    parser.add_argument(
        "--subcluster-dir",
        type=Path,
        default=DEFAULT_SUBCLUSTER_DIR,
        help="Directory containing cluster_*/clustered_responses.parquet files.",
    )
    parser.add_argument(
        "--tags-path",
        type=Path,
        default=DEFAULT_TAGS_PATH,
        help="Markdown file containing the subcluster-to-tag matrix.",
    )
    parser.add_argument(
        "--response",
        action="append",
        default=[],
        help="Assistant response to classify. Can be passed more than once.",
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=None,
        help=(
            "Optional file of responses. Supports .jsonl with a response or "
            "assistant_output field, .json as a list, .parquet with an "
            "assistant_output column, or plain text separated by blank lines."
        ),
    )
    parser.add_argument(
        "--max-responses",
        type=int,
        default=None,
        help="Optional cap on how many provided responses to classify.",
    )
    parser.add_argument(
        "--top-tags",
        type=int,
        default=5,
        help="Number of highest-scoring tags to include for each response.",
    )
    parser.add_argument(
        "--max-predicted-tags",
        type=int,
        default=5,
        help="Maximum number of positive-side tags to emit as predicted_tags.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help=(
            "Decision-function threshold for predicted tags. Linear SVM "
            "scores above 0 are on the positive side of the hyperplane."
        ),
    )
    parser.add_argument(
        "--svm-engine",
        choices=["linear-svc", "svc"],
        default="linear-svc",
        help=(
            "linear-svc is recommended for many responses. svc uses "
            "SVC(kernel='linear') and exposes support-vector counts, but is slower."
        ),
    )
    parser.add_argument(
        "--train-limit-per-subcluster",
        type=int,
        default=None,
        help="Optional cap per subcluster for fast experiments.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=393,
        help="Random seed used when sampling with --train-limit-per-subcluster.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path. Results are always printed to stdout.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Write --output without printing the full JSON payload to stdout.",
    )
    return parser.parse_args()


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def regex_flag(text: str, pattern: str, opening_only: bool = False) -> float:
    value = text[:180] if opening_only else text
    return float(re.search(pattern, value, flags=re.IGNORECASE | re.MULTILINE) is not None)


def regex_count(text: str, pattern: str) -> float:
    return float(len(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE)))


def sentence_count(text: str) -> int:
    return max(1, len(re.findall(r"[.!?]+(?:\s|$)", text)))


def behavior_features(text: str) -> list[float]:
    words = max(1, word_count(text))
    chars = max(1, len(text))
    lines = [line for line in text.splitlines() if line.strip()]
    line_count = max(1, len(lines))
    list_lines = sum(
        1 for line in lines if re.search(r"^\s*(?:[-*]|\d+[.)])\s+", line)
    )
    code_blocks = regex_count(text, r"```")
    paragraphs = max(1, len([part for part in re.split(r"\n\s*\n", text) if part.strip()]))
    sentences = sentence_count(text)

    return [
        math.log1p(words),
        math.log1p(chars),
        words / sentences,
        chars / words,
        line_count,
        paragraphs,
        list_lines / line_count,
        regex_flag(text, r"(?m)^\s*(?:[-*]|\d+[.)])\s+"),
        code_blocks,
        regex_flag(text, r"```"),
        regex_flag(text, r"\b(?:sorry|cannot|can't|unable|not able|i do not|i don't)\b"),
        regex_flag(text, r"\b(?:please|thank|thanks|happy to|glad to|delighted)\b"),
        regex_flag(
            text,
            r"\b(?:sure|certainly|of course|absolutely|happy to|i can help|i'd be happy|i will help)\b",
            opening_only=True,
        ),
        regex_flag(
            text,
            r"\b(?:here (?:is|are)|below (?:is|are)|i can provide|let me explain|to answer|based on|according to)\b",
            opening_only=True,
        ),
        regex_flag(
            text,
            r"\b(?:i agree|you're right|you are right|exactly|that's true|that is true|makes sense|good point)\b",
            opening_only=True,
        ),
        regex_count(text, r"\b(?:may|might|could|possibly|perhaps|it depends|however|although|while)\b")
        / words,
        regex_flag(
            text,
            r"\b(?:could you clarify|can you provide|please provide|need more information|it depends|may|might|could|possibly)\b",
        ),
        regex_count(text, r"\b(?:first|second|third|finally|lastly|step|tip|option|example)\b")
        / words,
        regex_count(text, r"\b(?:recommend|suggest|try|consider|use|create|add|make|follow)\b")
        / words,
        regex_count(text, r"\b(?:revise|updated|version|draft|rewrite|add more|include)\b")
        / words,
    ]


FEATURE_NAMES = [
    "log_words",
    "log_chars",
    "words_per_sentence",
    "chars_per_word",
    "line_count",
    "paragraph_count",
    "list_line_fraction",
    "list_format",
    "code_block_count",
    "code_block",
    "boundary_disclaimer_marker",
    "politeness_marker",
    "assist_agreement_opening",
    "information_agreement_opening",
    "user_validation_opening",
    "hedging_rate",
    "clarification_or_uncertainty",
    "enumeration_signal_rate",
    "action_signal_rate",
    "revision_signal_rate",
]


def parse_tags_cell(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def load_tag_matrix(tags_path: Path) -> dict[tuple[int, int], list[str]]:
    if not tags_path.exists():
        raise SystemExit(f"Missing tags file: {tags_path}")

    tag_map: dict[tuple[int, int], list[str]] = {}
    for line in tags_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0] in {"Subcluster", "---"}:
            continue
        match = re.fullmatch(r"(\d+)\.(\d+)", cells[0])
        if not match:
            continue
        top_cluster = int(match.group(1))
        subcluster = int(match.group(2))
        tags = parse_tags_cell(cells[1]) + parse_tags_cell(cells[2])
        if not tags:
            continue
        tag_map[(top_cluster, subcluster)] = sorted(set(tags))

    if not tag_map:
        raise SystemExit(f"No subcluster tags parsed from {tags_path}")
    return tag_map


def load_training_data(args: argparse.Namespace) -> tuple[list[str], list[list[str]]]:
    tag_map = load_tag_matrix(args.tags_path)
    texts: list[str] = []
    labels: list[list[str]] = []

    for (top_cluster, subcluster), tags in sorted(tag_map.items()):
        parquet_path = args.subcluster_dir / f"cluster_{top_cluster}" / "clustered_responses.parquet"
        if not parquet_path.exists():
            continue
        frame = pd.read_parquet(parquet_path)
        if "assistant_output" not in frame.columns or "cluster" not in frame.columns:
            raise SystemExit(f"Missing required columns in {parquet_path}")
        frame = frame.loc[frame["cluster"] == subcluster, ["assistant_output"]]
        if args.train_limit_per_subcluster is not None and len(frame) > args.train_limit_per_subcluster:
            frame = frame.sample(args.train_limit_per_subcluster, random_state=args.seed)
        for response in frame["assistant_output"].astype(str):
            texts.append(response)
            labels.append(tags)

    if not texts:
        raise SystemExit("No training responses found from subcluster artifacts.")
    return texts, labels


def response_item(response: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "response": response,
        "metadata": metadata or {},
    }


def load_input_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"Missing input file: {path}")

    if path.suffix == ".jsonl":
        responses = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            if isinstance(item, str):
                responses.append(response_item(item))
            elif isinstance(item, dict):
                value = item.get("response", item.get("assistant_output"))
                if value is None:
                    raise SystemExit(
                        f"JSONL line {line_number} needs a response or assistant_output field."
                    )
                metadata = {
                    key: item_value
                    for key, item_value in item.items()
                    if key not in {"response", "assistant_output"}
                }
                responses.append(response_item(str(value), metadata))
            else:
                raise SystemExit(f"Unsupported JSONL item on line {line_number}: {type(item)}")
        return responses

    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            responses = []
            for index, item in enumerate(data):
                if isinstance(item, str):
                    responses.append(response_item(item))
                elif isinstance(item, dict):
                    value = item.get("response", item.get("assistant_output"))
                    if value is None:
                        raise SystemExit(
                            f"JSON item {index} needs a response or assistant_output field."
                        )
                    metadata = {
                        key: item_value
                        for key, item_value in item.items()
                        if key not in {"response", "assistant_output"}
                    }
                    responses.append(response_item(str(value), metadata))
                else:
                    raise SystemExit(f"Unsupported JSON item {index}: {type(item)}")
            return responses
        raise SystemExit(".json input must be a list of strings or objects.")

    if path.suffix == ".parquet":
        frame = pd.read_parquet(path)
        if "assistant_output" not in frame.columns:
            raise SystemExit(f"Parquet input needs an assistant_output column: {path}")
        metadata_columns = [column for column in frame.columns if column != "assistant_output"]
        return [
            response_item(
                response=str(row["assistant_output"]),
                metadata={
                    column: row[column]
                    for column in metadata_columns
                    if pd.notna(row[column])
                },
            )
            for _, row in frame.iterrows()
        ]

    return [
        response_item(part.strip())
        for part in re.split(r"\n\s*\n", path.read_text(encoding="utf-8"))
        if part.strip()
    ]


def load_responses(args: argparse.Namespace) -> list[dict[str, Any]]:
    responses = [response_item(response) for response in args.response]
    if args.input_file is not None:
        responses.extend(load_input_file(args.input_file))
    if args.max_responses is not None:
        responses = responses[: args.max_responses]
    if not responses:
        raise SystemExit("Pass at least one --response or provide --input-file.")
    return responses


def train_classifier(
    texts: list[str],
    labels: list[list[str]],
    svm_engine: str,
) -> tuple[Any, Any, list[str]]:
    try:
        from sklearn.multiclass import OneVsRestClassifier
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
        from sklearn.svm import SVC, LinearSVC
    except ImportError as exc:
        raise SystemExit("Missing package: scikit-learn. Install it before classification.") from exc

    features = np.asarray([behavior_features(text) for text in texts], dtype=np.float32)
    labeler = MultiLabelBinarizer()
    targets = labeler.fit_transform(labels)
    if svm_engine == "svc":
        svm = SVC(kernel="linear", class_weight="balanced")
    else:
        svm = LinearSVC(
            class_weight="balanced",
            dual="auto",
            random_state=393,
            max_iter=10000,
        )

    classifier = make_pipeline(
        StandardScaler(),
        OneVsRestClassifier(svm),
    )
    classifier.fit(features, targets)
    return classifier, labeler, list(labeler.classes_)


def support_vector_counts(classifier: Any, tag_names: list[str]) -> dict[str, int] | None:
    one_vs_rest = classifier.named_steps.get("onevsrestclassifier")
    if one_vs_rest is None:
        return None
    counts = {}
    for tag, estimator in zip(tag_names, one_vs_rest.estimators_, strict=True):
        support = getattr(estimator, "support_vectors_", None)
        if support is None:
            return None
        counts[str(tag)] = int(len(support))
    return counts


def classify_response(
    classifier: Any,
    labeler: Any,
    item: dict[str, Any],
    threshold: float,
    top_tags: int,
    max_predicted_tags: int,
) -> dict[str, Any]:
    response = item["response"]
    features = np.asarray([behavior_features(response)], dtype=np.float32)
    scores = classifier.decision_function(features)[0]
    classes = list(labeler.classes_)
    ranked = sorted(
        (
            {"tag": tag, "score": float(score)}
            for tag, score in zip(classes, scores, strict=True)
        ),
        key=lambda item: item["score"],
        reverse=True,
    )
    predicted = [
        item["tag"]
        for item in ranked
        if item["score"] >= threshold
    ][:max_predicted_tags]
    if not predicted and ranked:
        predicted = [ranked[0]["tag"]]

    return {
        "metadata": item["metadata"],
        "response_preview": response[:180],
        "predicted_tags": predicted,
        "top_tags": ranked[:top_tags],
        "feature_names": FEATURE_NAMES,
        "features": behavior_features(response),
    }


def main() -> None:
    args = parse_args()
    train_texts, train_labels = load_training_data(args)
    classifier, labeler, classes = train_classifier(train_texts, train_labels, args.svm_engine)
    responses = load_responses(args)

    results = {
        "algorithm": "one_vs_rest_linear_svm",
        "svm_engine": args.svm_engine,
        "training_examples": len(train_texts),
        "tag_count": len(classes),
        "threshold": args.threshold,
        "support_vector_counts": support_vector_counts(classifier, classes),
        "results": [
            classify_response(
                classifier=classifier,
                labeler=labeler,
                item=response,
                threshold=args.threshold,
                top_tags=args.top_tags,
                max_predicted_tags=args.max_predicted_tags,
            )
            for response in responses
        ],
    }

    output = json.dumps(results, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    if not args.quiet:
        print(output)


if __name__ == "__main__":
    main()
