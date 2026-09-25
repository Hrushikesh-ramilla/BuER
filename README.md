# BuER - Business Entity Resolution

A Python pipeline for linking noisy, multilingual business records across three sources, developed for Amazon ML Challenge 2026.

BuER combines country-partitioned candidate retrieval, Indic token transliteration, fuzzy name/address comparison, street-number conflict checks, and exclusive assignment of each candidate record to its highest-scoring source entity.

## Competition result and submission scale

- Author-reported competition macro F0.5 on unseen data: **approximately 0.987**.
- Author-reported competition rank: **250 among 90,000 participants**.
- Submitted source entities: **1,732,544**.
- Submitted candidate pairs: **12,916,511**; **7.46 candidates per source entity** on average.
- Submitted match links: **5,803,442**.
- Packaged Indic mapping dictionary: **3,103 tokens**.

The entity and pair counts were calculated directly from the final submission files. The competition score and rank are reported by the author, rather than independently recomputed from hidden labels. They are not measurements from a fresh run of this repository. No unverified local cross-validation score or candidate-recall claim is presented here.

## Implementation

1. Normalize names and addresses with Unicode normalization and text cleanup.
2. Map Indic name tokens to Latin forms using the packaged dictionary, with Unidecode fallback.
3. Retrieve candidates from a country-partitioned token inverted index with posting-frequency limits.
4. Compute fuzzy string features with RapidFuzz and check structural street-number compatibility.
5. Score pairs using the weighted name/address formula in `src/pipeline.py` and apply its threshold.
6. Assign each pool record to its highest-scoring source entity and export candidate and match TSVs.

`src/postprocessing/optimizer.py` contains a separate expected-F0.5 prefix selector, and `rescue.py` contains a separate Indic recovery helper. Neither helper is called by the packaged CLI. The source does not contain a trained LightGBM model or training/evaluation runner. These distinctions matter because the original submission narrative describes a broader pipeline than the packaged executable code.

The submitted candidate output contains up to 75 candidates per entity, while the packaged CLI currently requests at most 25. The repository preserves the packaged source; it does not claim byte-for-byte reproduction of the final submitted output.

## Run

Use Python 3.10 or later and a virtual environment:

```bash
python -m venv .venv
# Activate the virtual environment for your shell.
python -m pip install -r requirements.txt
python -m src.pipeline --data-dir dataset/test --output-dir output --split test
```

Provide `test_source1.tsv`, `test_source2.tsv`, and `test_source3.tsv` in the data directory. The parser expects a header followed by tab-separated ID, name, address, and country columns in that order. Outputs are `matching_results.tsv` and `candidate_pairs.tsv`.

For a smaller source-query run, pass `--max-entities 100`. This limits Source 1 queries only; the full Source 2/3 pool is still loaded and indexed in memory.

The competition datasets, hidden labels, final row-level submission files, and original ZIP are not included. `submission_metrics.json` contains aggregate counts and provenance. The requirements file is preserved from the submitted package.

## Source map

| Component | Location |
| --- | --- |
| CLI orchestration and scoring | `src/pipeline.py` |
| Record data classes | `src/schema.py` |
| Text normalization and lexicons | `src/normalization/` |
| Indic transliteration and dictionary | `src/transliteration/` |
| Candidate indexing | `src/blocking/indexer.py` |
| String features and number checks | `src/features/` |
| Exclusive assignment and optional helpers | `src/postprocessing/` |

This is a competition project, not a production identity-resolution service. Dictionary provenance and train/validation separation need to be established before using the packaged dictionary in a new model-quality benchmark.
