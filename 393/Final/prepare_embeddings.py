"""Prepare UltraChat assistant-output embeddings for valuation clustering.

This script makes a two-stage split:
1. Keep 25% of the rows as discovery data by default.
2. Split discovery data into train/validation/test.
3. Embed assistant outputs while preserving prompt metadata.

HF_TOKEN is read from the environment. Values in .env or Final/.env are loaded
automatically.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from datasets import load_dataset
from dotenv import load_dotenv

DATASET_NAME = "HuggingFaceH4/ultrachat_200k"
DEFAULT_SPLIT = "train_sft"
DEFAULT_OUTPUT_DIR = Path("Final/data_splits")
DEFAULT_SEED = 393
DEFAULT_DISCOVERY_FRAC = 0.25
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split UltraChat and embed assistant outputs for clustering."
    )
    parser.add_argument("--dataset", default=DATASET_NAME, help="Hugging Face dataset name.")
    parser.add_argument(
        "--config",
        default=None,
        help="Optional dataset config name. Leave unset for UltraChat's default config.",
    )
    parser.add_argument("--split", default=DEFAULT_SPLIT, help="Source split to load.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where parquet split files and embedding artifacts are written.",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed.")
    parser.add_argument(
        "--discovery-frac",
        type=float,
        default=DEFAULT_DISCOVERY_FRAC,
        help="Fraction kept for train/validation/test work. The rest becomes new_data.",
    )
    parser.add_argument(
        "--train-frac",
        type=float,
        default=0.70,
        help="Fraction of discovery data used for training.",
    )
    parser.add_argument(
        "--validation-frac",
        type=float,
        default=0.15,
        help="Fraction of discovery data used for validation.",
    )
    parser.add_argument(
        "--test-frac",
        type=float,
        default=0.15,
        help="Fraction of discovery data used for testing.",
    )
    parser.add_argument(
        "--skip-split",
        action="store_true",
        help="Use existing parquet split files instead of recreating them.",
    )
    parser.add_argument(
        "--skip-embed",
        action="store_true",
        help="Only create split parquet files; do not embed responses.",
    )
    parser.add_argument(
        "--embed-splits",
        nargs="+",
        default=["train", "validation", "test"],
        choices=["train", "validation", "test", "new_data"],
        help="Split files to embed.",
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help="SentenceTransformers embedding model.",
    )
    parser.add_argument(
        "--embedding-batch-size",
        type=int,
        default=128,
        help="Number of assistant outputs to embed per batch.",
    )
    parser.add_argument(
        "--max-embed-rows",
        type=int,
        default=None,
        help="Optional cap for smoke-testing the embedding pipeline.",
    )
    return parser.parse_args()


def validate_fractions(args: argparse.Namespace) -> None:
    if not 0.0 < args.discovery_frac < 1.0:
        raise SystemExit("--discovery-frac must be between 0 and 1.")

    tvt_total = args.train_frac + args.validation_frac + args.test_frac
    if abs(tvt_total - 1.0) > 1e-9:
        raise SystemExit(
            "--train-frac, --validation-frac, and --test-frac must sum to 1.0. "
            f"Current total: {tvt_total:.6f}"
        )

    for name in ("train_frac", "validation_frac", "test_frac"):
        if getattr(args, name) <= 0:
            raise SystemExit(f"--{name.replace('_', '-')} must be greater than 0.")


def split_paths(output_dir: Path) -> dict[str, Path]:
    return {
        "train": output_dir / "train.parquet",
        "validation": output_dir / "validation.parquet",
        "test": output_dir / "test.parquet",
        "new_data": output_dir / "new_data.parquet",
    }


def save_split(dataset: Any, path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_parquet(str(path))
    return len(dataset)


def load_source_dataset(args: argparse.Namespace, hf_token: str | None) -> Any:
    load_kwargs = {"split": args.split, "token": hf_token}
    if args.config:
        return load_dataset(args.dataset, args.config, **load_kwargs)
    return load_dataset(args.dataset, **load_kwargs)


def create_splits(args: argparse.Namespace, hf_token: str | None) -> dict[str, Any]:
    dataset = load_source_dataset(args, hf_token)

    split_data = dataset.train_test_split(
        test_size=1.0 - args.discovery_frac,
        seed=args.seed,
        shuffle=True,
    )
    discovery_data = split_data["train"]
    new_data = split_data["test"]

    validation_plus_test_frac = args.validation_frac + args.test_frac
    discovery_split = discovery_data.train_test_split(
        test_size=validation_plus_test_frac,
        seed=args.seed,
        shuffle=True,
    )
    train_data = discovery_split["train"]
    validation_test_data = discovery_split["test"]

    test_share_of_validation_test = args.test_frac / validation_plus_test_frac
    validation_test_split = validation_test_data.train_test_split(
        test_size=test_share_of_validation_test,
        seed=args.seed,
        shuffle=True,
    )
    validation_data = validation_test_split["train"]
    test_data = validation_test_split["test"]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    paths = split_paths(args.output_dir)
    counts = {
        "train": save_split(train_data, paths["train"]),
        "validation": save_split(validation_data, paths["validation"]),
        "test": save_split(test_data, paths["test"]),
        "new_data": save_split(new_data, paths["new_data"]),
    }

    manifest = {
        "dataset": args.dataset,
        "config": args.config,
        "source_split": args.split,
        "seed": args.seed,
        "fractions": {
            "discovery": args.discovery_frac,
            "heldout_new_data": 1.0 - args.discovery_frac,
            "train_of_discovery": args.train_frac,
            "validation_of_discovery": args.validation_frac,
            "test_of_discovery": args.test_frac,
        },
        "counts": counts,
        "paths": {name: str(path) for name, path in paths.items()},
        "columns": dataset.column_names,
        "uses_hf_token": hf_token is not None,
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def message_content(message: dict[str, Any]) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    return str(content)


def response_records(row: dict[str, Any], source_split: str, row_index: int) -> list[dict[str, Any]]:
    messages = row.get("messages") or []
    prompt = next(
        (message_content(message) for message in messages if message.get("role") == "user"),
        "",
    )

    records = []
    assistant_index = 0
    for message in messages:
        if message.get("role") != "assistant":
            continue

        assistant_output = message_content(message).strip()
        if not assistant_output:
            continue

        records.append(
            {
                "source_split": source_split,
                "source_row": row_index,
                "response_index": assistant_index,
                "prompt_id": row.get("prompt_id"),
                "prompt": prompt,
                "assistant_output": assistant_output,
            }
        )
        assistant_index += 1

    return records


def build_response_table(split_path: Path, source_split: str, max_rows: int | None) -> pd.DataFrame:
    frame = pd.read_parquet(split_path)
    if max_rows is not None:
        frame = frame.head(max_rows)

    records = []
    for row_index, row in frame.iterrows():
        records.extend(response_records(row.to_dict(), source_split, int(row_index)))

    return pd.DataFrame.from_records(records)


def embed_texts(model: Any, texts: list[str], batch_size: int) -> np.ndarray:
    return model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32)


def embed_splits(args: argparse.Namespace) -> dict[str, Any]:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SystemExit(
            "Missing package: sentence-transformers. Install it before embedding."
        ) from exc

    paths = split_paths(args.output_dir)
    embedding_dir = args.output_dir / "embeddings"
    embedding_dir.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(args.embedding_model)
    manifest = {
        "embedding_model": args.embedding_model,
        "embedding_batch_size": args.embedding_batch_size,
        "normalize_embeddings": True,
        "max_embed_rows": args.max_embed_rows,
        "splits": {},
    }

    for split_name in args.embed_splits:
        split_path = paths[split_name]
        if not split_path.exists():
            raise SystemExit(f"Missing split file: {split_path}")

        metadata = build_response_table(split_path, split_name, args.max_embed_rows)
        if metadata.empty:
            raise SystemExit(f"No assistant outputs found in {split_path}")

        embeddings = embed_texts(
            model=model,
            texts=metadata["assistant_output"].tolist(),
            batch_size=args.embedding_batch_size,
        )

        metadata_path = embedding_dir / f"{split_name}_metadata.parquet"
        embeddings_path = embedding_dir / f"{split_name}_embeddings.npy"
        metadata.to_parquet(metadata_path, index=False)
        np.save(embeddings_path, embeddings)

        manifest["splits"][split_name] = {
            "responses": len(metadata),
            "metadata_path": str(metadata_path),
            "embeddings_path": str(embeddings_path),
            "embedding_shape": list(embeddings.shape),
        }

    manifest_path = embedding_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    args = parse_args()
    validate_fractions(args)
    load_dotenv()
    load_dotenv(Path("Final/.env"))

    outputs = {}
    if not args.skip_split:
        outputs["splits"] = create_splits(args, os.getenv("HF_TOKEN"))

    if not args.skip_embed:
        outputs["embeddings"] = embed_splits(args)

    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
