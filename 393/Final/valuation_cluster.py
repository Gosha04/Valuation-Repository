"""Cluster assistant-output embeddings for valuation discovery."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_EMBEDDING_DIR = Path("Final/data_splits/embeddings")
DEFAULT_OUTPUT_DIR = Path("Final/cluster_results")
DEFAULT_SEED = 393
STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "because",
    "but",
    "can",
    "for",
    "from",
    "have",
    "how",
    "into",
    "more",
    "not",
    "that",
    "the",
    "their",
    "then",
    "there",
    "this",
    "to",
    "use",
    "was",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
    "you",
    "your",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cluster saved assistant-output embeddings."
    )
    parser.add_argument(
        "--embedding-dir",
        type=Path,
        default=DEFAULT_EMBEDDING_DIR,
        help="Directory containing *_embeddings.npy and *_metadata.parquet files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where cluster labels and manifest are written.",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["train"],
        choices=["train", "validation", "test", "new_data"],
        help="Embedded splits to cluster together.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Optional random sample size for fast clustering experiments.",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed.")
    parser.add_argument(
        "--pca-dims",
        type=int,
        default=50,
        help="PCA dimensions before UMAP/HDBSCAN. Use 0 to skip PCA.",
    )
    parser.add_argument(
        "--umap-dims",
        type=int,
        default=15,
        help="UMAP dimensions before HDBSCAN. Use 0 to skip UMAP.",
    )
    parser.add_argument(
        "--min-cluster-size",
        type=int,
        default=50,
        help="Minimum HDBSCAN cluster size.",
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=None,
        help="Optional HDBSCAN min_samples. Defaults to HDBSCAN's own behavior.",
    )
    parser.add_argument(
        "--samples-per-cluster",
        type=int,
        default=5,
        help="Number of representative assistant responses to include per cluster.",
    )
    parser.add_argument(
        "--sample-chars",
        type=int,
        default=1200,
        help="Maximum characters to keep for each sampled assistant response.",
    )
    parser.add_argument(
        "--top-terms",
        type=int,
        default=10,
        help="Number of frequent terms to include per cluster.",
    )
    return parser.parse_args()


def load_embedding_split(embedding_dir: Path, split_name: str) -> tuple[pd.DataFrame, np.ndarray]:
    metadata_path = embedding_dir / f"{split_name}_metadata.parquet"
    embeddings_path = embedding_dir / f"{split_name}_embeddings.npy"

    if not metadata_path.exists():
        raise SystemExit(f"Missing metadata file: {metadata_path}")
    if not embeddings_path.exists():
        raise SystemExit(f"Missing embeddings file: {embeddings_path}")

    metadata = pd.read_parquet(metadata_path)
    embeddings = np.load(embeddings_path)
    if len(metadata) != len(embeddings):
        raise SystemExit(
            f"{split_name} metadata rows ({len(metadata)}) do not match "
            f"embedding rows ({len(embeddings)})."
        )

    return metadata, embeddings


def load_embeddings(args: argparse.Namespace) -> tuple[pd.DataFrame, np.ndarray]:
    metadata_frames = []
    embedding_arrays = []
    for split_name in args.splits:
        metadata, embeddings = load_embedding_split(args.embedding_dir, split_name)
        metadata_frames.append(metadata)
        embedding_arrays.append(embeddings)

    metadata = pd.concat(metadata_frames, ignore_index=True)
    embeddings = np.vstack(embedding_arrays).astype(np.float32)

    if args.sample_size is not None and args.sample_size < len(metadata):
        rng = np.random.default_rng(args.seed)
        indices = np.sort(rng.choice(len(metadata), size=args.sample_size, replace=False))
        metadata = metadata.iloc[indices].reset_index(drop=True)
        embeddings = embeddings[indices]

    return metadata, embeddings


def reduce_embeddings(embeddings: np.ndarray, args: argparse.Namespace) -> tuple[np.ndarray, dict[str, Any]]:
    reduced = embeddings
    manifest: dict[str, Any] = {"input_shape": list(embeddings.shape)}

    if args.pca_dims > 0 and args.pca_dims < reduced.shape[1]:
        from sklearn.decomposition import PCA

        pca = PCA(n_components=args.pca_dims, random_state=args.seed)
        reduced = pca.fit_transform(reduced).astype(np.float32)
        manifest["pca"] = {
            "dims": args.pca_dims,
            "explained_variance_ratio_sum": float(pca.explained_variance_ratio_.sum()),
        }
    else:
        manifest["pca"] = None

    if args.umap_dims > 0 and args.umap_dims < reduced.shape[1]:
        try:
            import umap
        except ImportError as exc:
            raise SystemExit("Missing package: umap-learn. Install it to use UMAP.") from exc

        reducer = umap.UMAP(
            n_components=args.umap_dims,
            metric="cosine",
            random_state=args.seed,
        )
        reduced = reducer.fit_transform(reduced).astype(np.float32)
        manifest["umap"] = {"dims": args.umap_dims, "metric": "cosine"}
    else:
        manifest["umap"] = None

    manifest["output_shape"] = list(reduced.shape)
    return reduced, manifest


def cluster_embeddings(reduced: np.ndarray, args: argparse.Namespace) -> tuple[np.ndarray, dict[str, Any]]:
    try:
        import hdbscan
    except ImportError as exc:
        raise SystemExit("Missing package: hdbscan. Install it before clustering.") from exc

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=args.min_cluster_size,
        min_samples=args.min_samples,
    )
    labels = clusterer.fit_predict(reduced)

    cluster_count = len(set(labels) - {-1})
    noise_count = int(np.sum(labels == -1))
    manifest = {
        "algorithm": "hdbscan",
        "min_cluster_size": args.min_cluster_size,
        "min_samples": args.min_samples,
        "cluster_count": cluster_count,
        "noise_count": noise_count,
        "noise_fraction": noise_count / len(labels),
    }
    return labels, manifest


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def top_terms(texts: pd.Series, limit: int) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for text in texts.dropna():
        tokens = re.findall(r"\b[a-z][a-z]+\b", str(text).lower())
        counter.update(token for token in tokens if token not in STOPWORDS)

    return [
        {"term": term, "count": count}
        for term, count in counter.most_common(limit)
    ]


def text_fraction(texts: pd.Series, pattern: str) -> float:
    if len(texts) == 0:
        return 0.0
    return float(texts.str.contains(pattern, case=False, regex=True, na=False).mean())


def representative_indices(cluster_vectors: np.ndarray, limit: int) -> np.ndarray:
    if len(cluster_vectors) <= limit:
        return np.arange(len(cluster_vectors))

    centroid = cluster_vectors.mean(axis=0)
    distances = np.linalg.norm(cluster_vectors - centroid, axis=1)
    return np.argsort(distances)[:limit]


def sample_response(row: pd.Series, sample_chars: int) -> dict[str, Any]:
    response = str(row["assistant_output"])
    if len(response) > sample_chars:
        response = response[:sample_chars].rstrip() + "..."

    return {
        "source_split": row.get("source_split"),
        "source_row": int(row.get("source_row")),
        "response_index": int(row.get("response_index")),
        "prompt_id": row.get("prompt_id"),
        "assistant_output": response,
    }


def summarize_clusters(
    labeled: pd.DataFrame,
    reduced: np.ndarray,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    summaries = []
    total = len(labeled)

    for cluster_id in sorted(labeled["cluster"].unique()):
        cluster_mask = labeled["cluster"].to_numpy() == cluster_id
        cluster_rows = labeled.loc[cluster_mask].reset_index(drop=True)
        cluster_vectors = reduced[cluster_mask]
        texts = cluster_rows["assistant_output"].astype(str)

        sample_positions = representative_indices(cluster_vectors, args.samples_per_cluster)
        samples = [
            sample_response(cluster_rows.iloc[position], args.sample_chars)
            for position in sample_positions
        ]

        words = texts.map(word_count)
        chars = texts.str.len()
        summaries.append(
            {
                "cluster": int(cluster_id),
                "is_noise": bool(cluster_id == -1),
                "members": int(len(cluster_rows)),
                "fraction": len(cluster_rows) / total,
                "avg_chars": float(chars.mean()),
                "median_chars": float(chars.median()),
                "avg_words": float(words.mean()),
                "median_words": float(words.median()),
                "list_format_fraction": text_fraction(texts, r"(?m)^\s*(?:[-*]|\d+[.)])\s+"),
                "code_block_fraction": text_fraction(texts, r"```"),
                "refusal_marker_fraction": text_fraction(
                    texts,
                    r"\b(?:sorry|cannot|can't|unable|not able|i do not|i don't)\b",
                ),
                "politeness_marker_fraction": text_fraction(
                    texts,
                    r"\b(?:please|thank|thanks|happy to|glad to)\b",
                ),
                "top_terms": top_terms(texts, args.top_terms),
                "samples": samples,
            }
        )

    return summaries


def write_cluster_report(summaries: list[dict[str, Any]], path: Path) -> None:
    lines = ["# Cluster Summary", ""]
    for summary in summaries:
        label = "Noise" if summary["is_noise"] else f"Cluster {summary['cluster']}"
        lines.extend(
            [
                f"## {label}",
                "",
                f"- Members: {summary['members']}",
                f"- Fraction: {summary['fraction']:.2%}",
                f"- Avg words: {summary['avg_words']:.1f}",
                f"- List format: {summary['list_format_fraction']:.2%}",
                f"- Code blocks: {summary['code_block_fraction']:.2%}",
                f"- Refusal markers: {summary['refusal_marker_fraction']:.2%}",
                f"- Politeness markers: {summary['politeness_marker_fraction']:.2%}",
                "- Top terms: "
                + ", ".join(item["term"] for item in summary["top_terms"]),
                "",
            ]
        )

        for index, sample in enumerate(summary["samples"], start=1):
            response = sample["assistant_output"].replace("\n", " ")
            lines.extend([f"Sample {index}: {response}", ""])

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    metadata, embeddings = load_embeddings(args)
    reduced, reduction_manifest = reduce_embeddings(embeddings, args)
    labels, cluster_manifest = cluster_embeddings(reduced, args)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    labeled = metadata.copy()
    labeled["cluster"] = labels

    labels_path = args.output_dir / "clustered_responses.parquet"
    reduced_path = args.output_dir / "reduced_embeddings.npy"
    summary_json_path = args.output_dir / "cluster_summary.json"
    summary_markdown_path = args.output_dir / "cluster_summary.md"
    manifest_path = args.output_dir / "manifest.json"

    labeled.to_parquet(labels_path, index=False)
    np.save(reduced_path, reduced)
    cluster_summaries = summarize_clusters(labeled, reduced, args)
    summary_json_path.write_text(
        json.dumps(cluster_summaries, indent=2) + "\n",
        encoding="utf-8",
    )
    write_cluster_report(cluster_summaries, summary_markdown_path)

    manifest = {
        "splits": args.splits,
        "sample_size": args.sample_size,
        "seed": args.seed,
        "labels_path": str(labels_path),
        "reduced_embeddings_path": str(reduced_path),
        "summary_json_path": str(summary_json_path),
        "summary_markdown_path": str(summary_markdown_path),
        "reduction": reduction_manifest,
        "clustering": cluster_manifest,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
