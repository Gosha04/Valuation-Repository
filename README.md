# Valuation Repository

This repository contains our CPSC 393 final project for discovering and evaluating
behavior-oriented valuation tags in assistant responses from UltraChat. The
workflow splits the dataset, embeds assistant outputs, clusters them, assigns
behavior tag matrices to clusters/subclusters, trains a lightweight classifier
from those labels, and evaluates predictions against reviewed labels.

Most code lives in `393/Final`. Generated data artifacts are also stored there.
Large `.parquet` and `.npy` outputs are ignored by git, so a fresh clone may need
to regenerate them before running downstream scripts.

## Repository Layout

```text
393/Final/
  prepare_embeddings.py          # Split UltraChat and create response embeddings
  valuation_cluster.py           # Cluster embedded assistant responses
  classification.py              # Train behavior-tag classifier and tag responses
  validate_classification.py     # Compare predictions against reviewed labels
  sweep_thresholds.py            # Tune classifier thresholds/max tag count
  data_splits/                   # Dataset split manifests and generated splits
  cluster_results*/              # Top-level clustering runs and summaries
  subclusters_behavior/          # Subcluster summaries and behavior tag matrix
  corrected/                     # Corrected train/validation/test experiment outputs
```

## Setup

Run commands from the repository root:

```bash
cd <YOU_CHOSEN-DIR/Valuation-Repository/...>
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install datasets python-dotenv pandas numpy pyarrow sentence-transformers scikit-learn umap-learn hdbscan
```

`prepare_embeddings.py` reads `HF_TOKEN` from `.env` or `393/Final/.env`.
UltraChat is public in many environments, but keeping the token set is safest:

```bash
echo 'HF_TOKEN=your_huggingface_token_here' > .env
```

## Recommended Pipeline

The scripts use paths relative to `393`, because the default project directory
inside the code is `393/Final`. The cleanest way to run the full pipeline is:

```bash
cd 393
```

1. Create dataset splits and embeddings:

```bash
python Final/prepare_embeddings.py
```

For a quick smoke test:

```bash
python Final/prepare_embeddings.py --max-embed-rows 500
```

2. Cluster training embeddings:

```bash
python Final/valuation_cluster.py \
  --embedding-dir Final/data_splits/embeddings \
  --output-dir Final/cluster_results
```

3. Cluster behavior-style buckets with KMeans:

```bash
python Final/valuation_cluster.py \
  --embedding-dir Final/data_splits/embeddings \
  --output-dir Final/cluster_results_behavior_12 \
  --algorithm kmeans \
  --feature-mode behavior \
  --kmeans-clusters 12 \
  --pca-dims 0 \
  --umap-dims 0
```

4. Classify validation or test responses after a behavior tag matrix exists:

```bash
python Final/classification.py \
  --subcluster-dir Final/subclusters_behavior \
  --tags-path Final/subclusters_behavior/behavior_valuation_tags.md \
  --input-file Final/data_splits/embeddings/test_metadata.parquet \
  --threshold -0.5 \
  --max-predicted-tags 5 \
  --output Final/subclusters_behavior/test_behavior_tags.json \
  --quiet
```

5. Validate predictions against reviewed labels:

```bash
python Final/validate_classification.py \
  --predictions Final/subclusters_behavior/test_behavior_tags.json \
  --labels Final/subclusters_behavior/revised_behavior_tags.json \
  --output Final/subclusters_behavior/behavior_validation_metrics.json \
  --disagreements-output Final/subclusters_behavior/behavior_validation_disagreements.csv
```

6. Sweep decision thresholds:

```bash
python Final/sweep_thresholds.py \
  --predictions Final/subclusters_behavior/test_behavior_tags.json \
  --labels Final/subclusters_behavior/revised_behavior_tags.json \
  --output Final/subclusters_behavior/threshold_sweep_results.json \
  --csv-output Final/subclusters_behavior/threshold_sweep_results.csv
```

## Script Reference

### `prepare_embeddings.py`

Splits UltraChat into train, validation, test, and held-out `new_data`, then
embeds assistant outputs with SentenceTransformers.

Default outputs:

- `Final/data_splits/train.parquet`
- `Final/data_splits/validation.parquet`
- `Final/data_splits/test.parquet`
- `Final/data_splits/new_data.parquet`
- `Final/data_splits/manifest.json`
- `Final/data_splits/embeddings/*_metadata.parquet`
- `Final/data_splits/embeddings/*_embeddings.npy`
- `Final/data_splits/embeddings/manifest.json`

Common commands:

```bash
python Final/prepare_embeddings.py
python Final/prepare_embeddings.py --skip-split
python Final/prepare_embeddings.py --skip-embed
python Final/prepare_embeddings.py --embed-splits train validation test new_data
python Final/prepare_embeddings.py --max-embed-rows 1000
```

Useful options:

- `--dataset`, `--config`, `--split`: choose the Hugging Face source dataset.
- `--output-dir`: change where split and embedding artifacts are written.
- `--discovery-frac`, `--train-frac`, `--validation-frac`, `--test-frac`: control split ratios.
- `--embedding-model`: change the SentenceTransformers model.
- `--embedding-batch-size`: tune embedding throughput.

### `valuation_cluster.py`

Loads saved embeddings and clusters assistant outputs. It writes labeled
responses, reduced embeddings, JSON summaries, Markdown summaries, and a run
manifest.

Default outputs:

- `Final/cluster_results/clustered_responses.parquet`
- `Final/cluster_results/reduced_embeddings.npy`
- `Final/cluster_results/cluster_summary.json`
- `Final/cluster_results/cluster_summary.md`
- `Final/cluster_results/manifest.json`

Common commands:

```bash
python Final/valuation_cluster.py
python Final/valuation_cluster.py --algorithm kmeans --kmeans-clusters 16 --output-dir Final/cluster_results_kmeans_16
python Final/valuation_cluster.py --feature-mode behavior --algorithm kmeans --kmeans-clusters 12 --pca-dims 0 --umap-dims 0 --output-dir Final/cluster_results_behavior_12
python Final/valuation_cluster.py --splits train validation --sample-size 5000
```

Subclustering a prior cluster:

```bash
python Final/valuation_cluster.py \
  --filter-cluster-from Final/cluster_results_behavior_12/clustered_responses.parquet \
  --filter-cluster 0 \
  --algorithm kmeans \
  --kmeans-clusters 6 \
  --output-dir Final/subclusters_behavior/cluster_0
```

Useful options:

- `--algorithm hdbscan|kmeans`: choose clustering algorithm.
- `--feature-mode embeddings|behavior|combined`: choose clustering features.
- `--pca-dims`, `--umap-dims`: control dimensionality reduction.
- `--min-cluster-size`, `--min-samples`: HDBSCAN controls.
- `--samples-per-cluster`, `--sample-chars`, `--top-terms`: report detail.

### `classification.py`

Trains a one-vs-rest linear SVM using the subcluster behavior tag matrix and
classifies provided assistant responses.

Default training inputs:

- `Final/subclusters_behavior/behavior_valuation_tags.md`
- `Final/subclusters_behavior/cluster_*/clustered_responses.parquet`

Classify one response:

```bash
python Final/classification.py \
  --response "Sure, I can help. Here are three concise options..."
```

Classify a file of responses:

```bash
python Final/classification.py \
  --input-file Final/data_splits/embeddings/test_metadata.parquet \
  --threshold -0.5 \
  --max-predicted-tags 5 \
  --output Final/subclusters_behavior/test_behavior_tags.json \
  --quiet
```

Supported `--input-file` formats:

- `.jsonl` with `response` or `assistant_output` fields.
- `.json` as a list of strings or objects.
- `.parquet` with an `assistant_output` column.
- Plain text, with responses separated by blank lines.

Useful options:

- `--subcluster-dir`, `--tags-path`: point to a different labeled cluster set.
- `--top-tags`: number of scored tags shown per response.
- `--threshold`: decision score cutoff for predicted tags.
- `--max-predicted-tags`: cap predicted labels per response.
- `--svm-engine linear-svc|svc`: choose SVM implementation.
- `--train-limit-per-subcluster`: speed up experiments.

### `validate_classification.py`

Compares classifier predictions against reviewed labels and writes metrics plus
a CSV of disagreements.

```bash
python Final/validate_classification.py \
  --predictions Final/subclusters_behavior/test_behavior_tags.json \
  --labels Final/subclusters_behavior/revised_behavior_tags.json \
  --output Final/subclusters_behavior/behavior_validation_metrics.json \
  --disagreements-output Final/subclusters_behavior/behavior_validation_disagreements.csv
```

Use `--include-unreviewed` to evaluate labels whose `review_status` is not
`reviewed`.

### `sweep_thresholds.py`

Uses saved `top_tags` scores from `classification.py` to test threshold and
maximum-tag-count combinations against reviewed labels.

```bash
python Final/sweep_thresholds.py \
  --predictions Final/subclusters_behavior/test_behavior_tags.json \
  --labels Final/subclusters_behavior/revised_behavior_tags.json \
  --thresholds -1.0 -0.75 -0.5 -0.25 0.0 0.25 0.5 \
  --max-tags 1 2 3 4 5 \
  --selection-metric micro_f1 \
  --output Final/subclusters_behavior/threshold_sweep_results.json \
  --csv-output Final/subclusters_behavior/threshold_sweep_results.csv
```

Useful options:

- `--selection-metric`: choose `micro_f1`, `macro_f1`, `mean_jaccard`,
  `exact_match_accuracy`, or `primary_accuracy`.
- `--allow-empty`: allow zero predicted tags when all scores are below threshold.
- `--include-unreviewed`: include labels that have not been reviewed.

## Corrected Experiment Outputs

The `393/Final/corrected/subclusters_behavior_train` folder contains the latest
corrected behavior-tag experiment artifacts, including validation threshold
sweeps, final test metrics, and disagreement CSVs. The current final test metrics
file is:

```text
393/Final/corrected/subclusters_behavior_train/final_test_behavior_metrics.json
```

The validation sweep selected threshold `-0.5` with `max_tags=5` by `micro_f1`,
as recorded in:

```text
393/Final/corrected/subclusters_behavior_train/validation_threshold_sweep_results_revised_matrix.json
```

To reproduce that corrected-style evaluation, point the scripts at the corrected
subcluster directory and reviewed-label files:

```bash
python Final/classification.py \
  --subcluster-dir Final/corrected/subclusters_behavior_train \
  --tags-path Final/corrected/subclusters_behavior_train/behavior_valuation_tags.md \
  --input-file Final/data_splits/embeddings/test_metadata.parquet \
  --threshold -0.5 \
  --max-predicted-tags 5 \
  --output Final/corrected/subclusters_behavior_train/test_behavior_tags_revised_matrix_threshold_-0.5.json \
  --quiet
```

```bash
python Final/validate_classification.py \
  --predictions Final/corrected/subclusters_behavior_train/test_behavior_tags_revised_matrix_threshold_-0.5.json \
  --labels Final/subclusters_behavior/revised_behavior_tags.json \
  --output Final/corrected/subclusters_behavior_train/final_test_behavior_metrics.json \
  --disagreements-output Final/corrected/subclusters_behavior_train/final_test_behavior_disagreements.csv
```

## Notes

- Run scripts from `393` when using default paths.
- Run from the repository root only if you pass explicit paths such as
  `--output-dir 393/Final/data_splits`.
- `.parquet` and `.npy` files are intentionally ignored by git because they are
  generated and can be large.
- The current local worktree already has generated artifacts and some `.DS_Store`
  changes; the README does not depend on them being committed.
