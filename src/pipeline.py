"""Unified End-to-End Entity Resolution Pipeline Runner."""
import argparse
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from .schema import BusinessRecord
from .normalization.clean_pipeline import MultiPassTextCleaner
from .transliteration.indic_aligner import CrossLingualIndicMapper
from .blocking.indexer import DualInvertedIndexBlocker
from .features.string_metrics import VectorizedStringSimilarity
from .features.geo_verifier import StructuralAddressComparator
from .postprocessing.exclusivity import BipartiteMutualExclusivitySolver
from .postprocessing.optimizer import ExpectedUtilityOptimizer
from .postprocessing.rescue import MultiNationalRescueEngine


def load_source_tsv(path: str) -> List[Tuple[str, str, str, str]]:
    """Stream-read entity records from TSV into a list of tuples: (id, name, address, country)."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        header = next(f, None)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                eid = parts[0]
                name = parts[1]
                addr = parts[2] if len(parts) > 2 else ""
                country = parts[3] if len(parts) > 3 else "Unknown"
                records.append((eid, name, addr, country))
    return records


def run_pipeline(data_dir: str, output_dir: str, split: str = "test", max_entities: int = 0) -> None:
    """Execute complete entity resolution pipeline from raw TSV data to submission outputs."""
    t0 = time.time()
    print("=" * 75)
    print(f"NEURONS BUSINESS ENTITY RESOLUTION PIPELINE [{split.upper()} RUN]")
    print("=" * 75)

    os.makedirs(output_dir, exist_ok=True)
    matching_path = os.path.join(output_dir, "matching_results.tsv")
    candidate_path = os.path.join(output_dir, "candidate_pairs.tsv")

    # Step 1: Initialize Indic Cross-Lingual Transliteration Engine
    print("[1/5] Initializing Indic Cross-Lingual Transliteration Engine...")
    indic_engine = CrossLingualIndicMapper()
    print(f"      Loaded {indic_engine.token_count:,} verified transliteration tokens across 9 scripts.")

    # Step 2: Verification of target directories
    s1_file = os.path.join(data_dir, f"{split}_source1.tsv")
    s2_file = os.path.join(data_dir, f"{split}_source2.tsv")
    s3_file = os.path.join(data_dir, f"{split}_source3.tsv")

    for fpath in (s1_file, s2_file, s3_file):
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Required dataset file not found: {fpath}")

    print(f"[2/5] Verified source files in {data_dir}.")
    print("      Loading Source 1 records...")
    s1_raw = load_source_tsv(s1_file)
    if max_entities > 0:
        s1_raw = s1_raw[:max_entities]
    print(f"      Loaded {len(s1_raw):,} Source 1 records.")

    # Step 3: Multi-Channel Inverted Index Blocking & Country Partitioning
    print("[3/5] Indexing Source 2 & Source 3 pool records...")
    blocker = DualInvertedIndexBlocker(max_postings_per_token=1500, min_token_len=3)

    pool_records = {}
    for pool_file in (s2_file, s3_file):
        raw_pool = load_source_tsv(pool_file)
        clean_pool = []
        for pid, name, addr, country in raw_pool:
            c_name = MultiPassTextCleaner.clean(name)
            c_addr = MultiPassTextCleaner.clean(addr)
            # Transliterate native Indic scripts
            if not name.isascii() and country.strip().lower() == "india":
                t_name = indic_engine.transliterate_string(name)
                c_name = MultiPassTextCleaner.clean(t_name)
            pool_records[pid] = (c_name, c_addr, country)
            clean_pool.append((pid, c_name, c_addr, country))
        blocker.index_pool_records(clean_pool)
        del raw_pool

    print(f"      Total pool records indexed: {len(pool_records):,}.")

    # Step 4: Retrieve candidates & feature scoring
    print("[4/5] Retrieving candidates and computing match scores...")
    rescue_engine = MultiNationalRescueEngine(indic_engine)
    all_candidates: Dict[str, List[str]] = {}
    final_matches: Dict[str, List[str]] = defaultdict(list)
    all_scored_pairs: List[Tuple[str, str, float]] = []

    for idx, (s1_id, name, addr, country) in enumerate(s1_raw, 1):
        c_name = MultiPassTextCleaner.clean(name)
        c_addr = MultiPassTextCleaner.clean(addr)
        
        # Retrieve candidate IDs from inverted index
        cands = blocker.retrieve_candidates(s1_id, c_name, c_addr, country, max_candidates=25)
        all_candidates[s1_id] = cands

        for cid in cands:
            p_name, p_addr, p_country = pool_records.get(cid, ("", "", ""))
            # Compute multi-dimensional similarity features
            sim_features = VectorizedStringSimilarity.compute_pair_features(c_name, p_name, c_addr, p_addr)
            h_compat = StructuralAddressComparator.evaluate_number_compatibility(c_addr, p_addr)
            
            # Composite calibrated score
            name_score = 0.5 * sim_features["name_token_sort"] + 0.3 * sim_features["name_jw"] + 0.2 * sim_features["name_jaccard"]
            addr_score = 0.6 * sim_features["addr_token_sort"] + 0.4 * sim_features["addr_jaccard"] if c_addr and p_addr else 0.5
            
            # Penalize house number conflicts
            if h_compat == 0.0:
                score = 0.0
            else:
                score = 0.7 * name_score + 0.3 * addr_score
                
            if score >= 0.70:
                all_scored_pairs.append((s1_id, cid, score))

        if idx % 200000 == 0:
            print(f"      Processed {idx:,} / {len(s1_raw):,} entities...")

    # Step 5: Enforce global 1-to-1 mutual exclusivity
    print("[5/5] Enforcing 1-to-1 Mutual Exclusivity and Generating Outputs...")
    exclusive_pairs = BipartiteMutualExclusivitySolver.resolve_conflicts(all_scored_pairs)

    assigned_pool_ids: Set[str] = set()
    for sid, cid, score in exclusive_pairs:
        final_matches[sid].append(cid)
        assigned_pool_ids.add(cid)

    # Write output files
    print(f"      Writing {matching_path}...")
    with open(matching_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("source1_entity_id\tmatched_entity_ids\n")
        for sid, _, _, _ in s1_raw:
            m_list = final_matches.get(sid, [])
            f.write(f"{sid}\t{','.join(m_list)}\n")

    print(f"      Writing {candidate_path}...")
    with open(candidate_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("source1_entity_id\tcandidate_entity_ids\n")
        for sid, _, _, _ in s1_raw:
            # Candidate list must be a strict superset of matches
            c_set = set(all_candidates.get(sid, []))
            for m in final_matches.get(sid, []):
                c_set.add(m)
            f.write(f"{sid}\t{','.join(c_set)}\n")

    print(f"      Successfully generated complete submission artifacts in {output_dir}!")
    print(f"      Total execution time: {time.time() - t0:.2f}s")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Neurons Business Entity Resolution Pipeline")
    parser.add_argument("--data-dir", default="dataset/test", help="Path to data split directory")
    parser.add_argument("--output-dir", default="output", help="Directory for output TSVs")
    parser.add_argument("--split", default="test", choices=["train", "test"], help="Dataset split")
    parser.add_argument("--max-entities", type=int, default=0, help="Optional max entities to process (smoke test)")
    args = parser.parse_args()

    run_pipeline(args.data_dir, args.output_dir, args.split, args.max_entities)


if __name__ == "__main__":
    main()
