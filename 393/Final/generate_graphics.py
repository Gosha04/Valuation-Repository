"""Generate graphics for behavior-tag and clustering experiment outputs.

The defaults target the corrected train-subcluster experiment artifacts. The
script writes static PNG figures for threshold tradeoffs, tag metrics, linear
SVM decision boundaries, and top-level/subcluster size distributions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

_CACHE_DIR = Path(tempfile.gettempdir()) / "valuation_graphics_cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_CACHE_DIR / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(_CACHE_DIR / "xdg"))
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd

from classification import behavior_features, load_training_data, train_classifier


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT_DIR = PROJECT_DIR / "Final/corrected/subclusters_behavior_train"
DEFAULT_TOP_CLUSTER_SUMMARY = (
    PROJECT_DIR / "Final/corrected/cluster_results_train_behavior_16/cluster_summary.json"
)
DEFAULT_THRESHOLD_SWEEP = (
    DEFAULT_EXPERIMENT_DIR / "validation_threshold_sweep_results_revised_matrix.csv"
)
DEFAULT_METRICS = DEFAULT_EXPERIMENT_DIR / "final_test_behavior_metrics.json"
DEFAULT_OUTPUT_DIR = DEFAULT_EXPERIMENT_DIR / "figures"
DEFAULT_TAGS_PATH = DEFAULT_EXPERIMENT_DIR / "behavior_valuation_tags.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate graphics for behavior-tag classification and clusters."
    )
    parser.add_argument(
        "--experiment-dir",
        type=Path,
        default=DEFAULT_EXPERIMENT_DIR,
        help="Directory containing cluster_*/cluster_summary.json subcluster outputs.",
    )
    parser.add_argument(
        "--top-cluster-summary",
        type=Path,
        default=DEFAULT_TOP_CLUSTER_SUMMARY,
        help="Top-level cluster_summary.json to plot.",
    )
    parser.add_argument(
        "--threshold-sweep",
        type=Path,
        default=DEFAULT_THRESHOLD_SWEEP,
        help="CSV produced by sweep_thresholds.py.",
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        default=DEFAULT_METRICS,
        help="Metrics JSON produced by validate_classification.py.",
    )
    parser.add_argument(
        "--subcluster-dir",
        type=Path,
        default=DEFAULT_EXPERIMENT_DIR,
        help="Directory containing cluster_*/clustered_responses.parquet files.",
    )
    parser.add_argument(
        "--tags-path",
        type=Path,
        default=DEFAULT_TAGS_PATH,
        help="Behavior valuation tag matrix used to train decision-boundary plots.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where figures will be written.",
    )
    parser.add_argument(
        "--boundary-tags",
        nargs="+",
        default=None,
        help=(
            "Specific tags to plot decision boundaries for. Defaults to the "
            "highest-support tags from the metrics JSON."
        ),
    )
    parser.add_argument(
        "--max-boundary-tags",
        type=int,
        default=6,
        help="Maximum number of tag decision-boundary figures to write.",
    )
    parser.add_argument(
        "--decision-threshold",
        type=float,
        default=-0.5,
        help="Classification score threshold to draw alongside the SVM zero boundary.",
    )
    parser.add_argument(
        "--train-limit-per-subcluster",
        type=int,
        default=400,
        help="Optional cap per subcluster for decision-boundary training/plotting.",
    )
    parser.add_argument("--seed", type=int, default=393)
    return parser.parse_args()


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {label}: {path}")


def load_json(path: Path) -> Any:
    require_file(path, "JSON file")
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_").lower()


def import_plotting() -> Any:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit(
            "Missing package: matplotlib. Install with `python -m pip install matplotlib`."
        ) from exc
    return plt


def save_figure(fig: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")


def load_cluster_summary(path: Path) -> pd.DataFrame:
    data = load_json(path)
    if not isinstance(data, list):
        raise SystemExit(f"Expected a list in cluster summary: {path}")
    frame = pd.DataFrame(data)
    required = {"cluster", "members"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise SystemExit(f"Missing columns in {path}: {missing}")
    return frame.sort_values("cluster").reset_index(drop=True)


def plot_cluster_sizes(summary_path: Path, output_dir: Path) -> Path:
    plt = import_plotting()
    frame = load_cluster_summary(summary_path)
    labels = [str(value) for value in frame["cluster"]]
    colors = ["#7a7a7a" if value else "#2878b5" for value in frame.get("is_noise", False)]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(labels, frame["members"], color=colors, edgecolor="#202020", linewidth=0.4)
    ax.set_title("Top-Level Cluster Size Distribution")
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Responses")
    ax.grid(axis="y", alpha=0.25)
    path = output_dir / "cluster_size_distribution.png"
    save_figure(fig, path)
    plt.close(fig)
    return path


def load_subcluster_sizes(experiment_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for summary_path in sorted(experiment_dir.glob("cluster_*/cluster_summary.json")):
        match = re.fullmatch(r"cluster_(\d+)", summary_path.parent.name)
        if not match:
            continue
        top_cluster = int(match.group(1))
        for item in load_json(summary_path):
            rows.append(
                {
                    "top_cluster": top_cluster,
                    "subcluster": int(item["cluster"]),
                    "label": f"{top_cluster}.{int(item['cluster'])}",
                    "members": int(item["members"]),
                    "fraction": float(item.get("fraction", 0.0)),
                }
            )
    if not rows:
        raise SystemExit(f"No subcluster summaries found under {experiment_dir}")
    return pd.DataFrame(rows).sort_values(["top_cluster", "subcluster"])


def plot_subcluster_sizes(experiment_dir: Path, output_dir: Path) -> list[Path]:
    plt = import_plotting()
    frame = load_subcluster_sizes(experiment_dir)
    paths: list[Path] = []

    fig, ax = plt.subplots(figsize=(13, 6))
    ordered = frame.sort_values("members", ascending=False)
    ax.bar(ordered["label"], ordered["members"], color="#4b8f8c", edgecolor="#202020", linewidth=0.25)
    ax.set_title("Subcluster Size Distribution")
    ax.set_xlabel("Subcluster")
    ax.set_ylabel("Responses")
    ax.tick_params(axis="x", rotation=75, labelsize=7)
    ax.grid(axis="y", alpha=0.25)
    path = output_dir / "subcluster_size_distribution.png"
    save_figure(fig, path)
    plt.close(fig)
    paths.append(path)

    pivot = frame.pivot(index="top_cluster", columns="subcluster", values="members").fillna(0)
    fig, ax = plt.subplots(figsize=(9, 6))
    image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="YlGnBu")
    ax.set_title("Subcluster Members by Parent Cluster")
    ax.set_xlabel("Subcluster")
    ax.set_ylabel("Parent cluster")
    ax.set_xticks(range(len(pivot.columns)), [str(col) for col in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), [str(row) for row in pivot.index])
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Responses")
    path = output_dir / "subcluster_size_heatmap.png"
    save_figure(fig, path)
    plt.close(fig)
    paths.append(path)
    return paths


def plot_threshold_sweep(threshold_sweep: Path, output_dir: Path) -> Path | None:
    if not threshold_sweep.exists():
        return None
    plt = import_plotting()
    frame = pd.read_csv(threshold_sweep)
    required = {"threshold", "max_tags", "micro_f1", "macro_f1", "mean_jaccard"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise SystemExit(f"Missing columns in threshold sweep CSV: {missing}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    metrics = ["micro_f1", "macro_f1", "mean_jaccard"]
    for max_tags, group in frame.sort_values("threshold").groupby("max_tags"):
        axes[0].plot(group["threshold"], group["micro_f1"], marker="o", label=f"max_tags={max_tags}")
    axes[0].set_title("Decision Threshold vs Micro F1")
    axes[0].set_xlabel("Decision threshold")
    axes[0].set_ylabel("Micro F1")
    axes[0].grid(alpha=0.25)
    axes[0].legend(fontsize=8)

    best_by_threshold = (
        frame.sort_values("micro_f1", ascending=False)
        .groupby("threshold", as_index=False)
        .first()
        .sort_values("threshold")
    )
    for metric in metrics:
        axes[1].plot(best_by_threshold["threshold"], best_by_threshold[metric], marker="o", label=metric)
    axes[1].set_title("Best Setting at Each Threshold")
    axes[1].set_xlabel("Decision threshold")
    axes[1].set_ylabel("Score")
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=8)

    path = output_dir / "tag_decision_threshold_sweep.png"
    save_figure(fig, path)
    plt.close(fig)
    return path


def plot_tag_metrics(metrics_path: Path, output_dir: Path) -> Path | None:
    if not metrics_path.exists():
        return None
    plt = import_plotting()
    data = load_json(metrics_path)
    per_tag = data.get("per_tag", {})
    if not per_tag:
        return None
    frame = pd.DataFrame.from_dict(per_tag, orient="index").reset_index(names="tag")
    frame = frame.sort_values("support", ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(frame))
    width = 0.24
    ax.bar(x - width, frame["precision"], width=width, label="precision", color="#2878b5")
    ax.bar(x, frame["recall"], width=width, label="recall", color="#f28e2b")
    ax.bar(x + width, frame["f1"], width=width, label="f1", color="#59a14f")
    ax.set_title("Per-Tag Classification Metrics")
    ax.set_xlabel("Tag")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x, frame["tag"], rotation=65, ha="right")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    path = output_dir / "per_tag_precision_recall_f1.png"
    save_figure(fig, path)
    plt.close(fig)
    return path


def selected_boundary_tags(metrics_path: Path, requested: list[str] | None, max_tags: int) -> list[str]:
    if requested:
        return requested[:max_tags]
    if metrics_path.exists():
        per_tag = load_json(metrics_path).get("per_tag", {})
        ranked = sorted(
            per_tag,
            key=lambda tag: (per_tag[tag].get("support", 0), per_tag[tag].get("f1", 0.0)),
            reverse=True,
        )
        if ranked:
            return ranked[:max_tags]
    return []


def primary_tag_for_labels(labels: set[str], tag_names: list[str], per_tag: dict[str, Any]) -> str:
    supported = [tag for tag in tag_names if tag in labels]
    if not supported:
        return "unlabeled"
    return max(supported, key=lambda tag: per_tag.get(tag, {}).get("support", 0))


def plot_decision_boundaries(args: argparse.Namespace, output_dir: Path) -> list[Path]:
    plt = import_plotting()
    try:
        from sklearn.decomposition import PCA
        from matplotlib.lines import Line2D
    except ImportError as exc:
        raise SystemExit(
            "Missing package: scikit-learn. Install with `python -m pip install scikit-learn`."
        ) from exc

    classifier_args = argparse.Namespace(
        subcluster_dir=args.subcluster_dir,
        tags_path=args.tags_path,
        train_limit_per_subcluster=args.train_limit_per_subcluster,
        seed=args.seed,
    )
    texts, labels = load_training_data(classifier_args)
    classifier, labeler, tag_names = train_classifier(texts, labels, svm_engine="linear-svc")
    metrics_data = load_json(args.metrics) if args.metrics.exists() else {}
    per_tag = metrics_data.get("per_tag", {})
    chosen_tags = [
        tag
        for tag in selected_boundary_tags(args.metrics, args.boundary_tags, args.max_boundary_tags)
        if tag in tag_names
    ]
    if not chosen_tags:
        chosen_tags = tag_names[: args.max_boundary_tags]

    features = np.asarray([behavior_features(text) for text in texts], dtype=np.float32)
    scaler = classifier.named_steps["standardscaler"]
    one_vs_rest = classifier.named_steps["onevsrestclassifier"]
    scaled_features = scaler.transform(features)
    pca = PCA(n_components=2, random_state=args.seed)
    projected = pca.fit_transform(scaled_features)
    tag_index = {tag: index for index, tag in enumerate(tag_names)}
    positive_sets = [set(row) for row in labels]

    x_min, x_max = np.percentile(projected[:, 0], [1, 99])
    y_min, y_max = np.percentile(projected[:, 1], [1, 99])
    x_pad = max((x_max - x_min) * 0.12, 0.5)
    y_pad = max((y_max - y_min) * 0.12, 0.5)
    xx, yy = np.meshgrid(
        np.linspace(x_min - x_pad, x_max + x_pad, 220),
        np.linspace(y_min - y_pad, y_max + y_pad, 220),
    )
    grid_projected = np.c_[xx.ravel(), yy.ravel()]
    grid_scaled_features = pca.inverse_transform(grid_projected)

    rng = np.random.default_rng(args.seed)
    sample_size = min(3500, len(projected))
    sample_indices = rng.choice(len(projected), size=sample_size, replace=False)
    paths: list[Path] = []

    fig, ax = plt.subplots(figsize=(11, 8))
    sample = projected[sample_indices]
    cmap = plt.get_cmap("tab20", len(tag_names))
    all_grid_scores = np.vstack(
        [
            estimator.decision_function(grid_scaled_features)
            for estimator in one_vs_rest.estimators_
        ]
    )
    winning_tag_indices = np.argmax(all_grid_scores, axis=0).reshape(xx.shape)
    ax.contourf(
        xx,
        yy,
        winning_tag_indices,
        levels=np.arange(len(tag_names) + 1) - 0.5,
        cmap=cmap,
        alpha=0.18,
    )

    primary_tags = [
        primary_tag_for_labels(positive_sets[index], tag_names, per_tag)
        for index in sample_indices
    ]
    for index, tag in enumerate(tag_names):
        mask = np.asarray([primary == tag for primary in primary_tags])
        if not mask.any():
            continue
        ax.scatter(
            sample[mask, 0],
            sample[mask, 1],
            s=11,
            c=[cmap(index)],
            alpha=0.55,
            linewidths=0.15,
            edgecolors="#202020",
        )

    handles: list[Any] = []
    for index, tag in enumerate(tag_names):
        estimator = one_vs_rest.estimators_[index]
        scores = estimator.decision_function(grid_scaled_features).reshape(xx.shape)
        color = cmap(index)
        ax.contour(xx, yy, scores, levels=[0.0], colors=[color], linewidths=1.0, alpha=0.9)
        handles.append(Line2D([0], [0], color=color, lw=1.8, label=tag))
    ax.contour(
        xx,
        yy,
        winning_tag_indices,
        levels=np.arange(len(tag_names) + 1) - 0.5,
        colors="#2a2a2a",
        linewidths=0.35,
        alpha=0.35,
    )
    ax.set_title("SVM Tag Decision Regions Projected with PCA")
    ax.set_xlabel("PCA projection of SVM behavior features: component 1")
    ax.set_ylabel("PCA projection of SVM behavior features: component 2")
    ax.grid(alpha=0.18)
    ax.legend(
        handles=handles,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=8,
        frameon=False,
    )
    path = output_dir / "decision_boundaries_combined.png"
    save_figure(fig, path)
    plt.close(fig)
    paths.append(path)

    for tag in chosen_tags:
        estimator = one_vs_rest.estimators_[tag_index[tag]]
        scores = estimator.decision_function(grid_scaled_features).reshape(xx.shape)
        positives = np.asarray([tag in positive_sets[index] for index in sample_indices])
        sample = projected[sample_indices]

        fig, ax = plt.subplots(figsize=(8.5, 7))
        ax.scatter(
            sample[~positives, 0],
            sample[~positives, 1],
            s=8,
            c="#c9c9c9",
            alpha=0.35,
            linewidths=0,
            label="other training responses",
        )
        ax.scatter(
            sample[positives, 0],
            sample[positives, 1],
            s=12,
            c="#2878b5",
            alpha=0.65,
            linewidths=0,
            label=f"positive: {tag}",
        )
        ax.contour(xx, yy, scores, levels=[0.0], colors=["#202020"], linewidths=1.6)
        if args.decision_threshold != 0:
            ax.contour(
                xx,
                yy,
                scores,
                levels=[args.decision_threshold],
                colors=["#d1495b"],
                linestyles="--",
                linewidths=1.4,
            )
        ax.set_title(f"SVM Decision Boundary Projected with PCA: {tag}")
        ax.set_xlabel("PCA projection of SVM behavior features: component 1")
        ax.set_ylabel("PCA projection of SVM behavior features: component 2")
        ax.grid(alpha=0.18)
        ax.legend(loc="best", fontsize=8)
        path = output_dir / f"decision_boundary_{slugify(tag)}.png"
        save_figure(fig, path)
        plt.close(fig)
        paths.append(path)

    return paths


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    written.append(plot_cluster_sizes(args.top_cluster_summary, args.output_dir))
    written.extend(plot_subcluster_sizes(args.experiment_dir, args.output_dir))

    threshold_path = plot_threshold_sweep(args.threshold_sweep, args.output_dir)
    if threshold_path is not None:
        written.append(threshold_path)

    tag_metrics_path = plot_tag_metrics(args.metrics, args.output_dir)
    if tag_metrics_path is not None:
        written.append(tag_metrics_path)

    written.extend(plot_decision_boundaries(args, args.output_dir))

    manifest = {
        "output_dir": str(args.output_dir),
        "figures": [str(path) for path in written],
    }
    manifest_path = args.output_dir / "graphics_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(written)} figures to {args.output_dir}")
    print(f"Wrote manifest: {manifest_path}")


if __name__ == "__main__":
    main()
