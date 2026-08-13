#!/usr/bin/env python3
"""Out-of-time validation of frozen MIFE v0.1 against 2025-26 NNSW events.

This script uses all nine preregistered activation/age scenarios at a fixed
reference abundance. Relative phenology is abundance-invariant. No scenario is
selected, no threshold is fitted, and no biological parameter is changed.
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path
from statistics import median


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.api import SimulationRequest, simulate
from scripts.run_mife_initialization_sensitivity import (
    ACTIVATION_PROFILES, AGE_BANDS, uniform_distribution,
)


EVENTS = REPO_ROOT / "data/validation/MIFE_v0.1_multiseason_event_inventory.csv"
JOINED = REPO_ROOT / "data/output/MIFE_v0.1_NNSW_2025_26_out_of_time_joined.csv"
SUMMARY = REPO_ROOT / "data/output/MIFE_v0.1_NNSW_2025_26_out_of_time_summary.csv"
START = "2025-07-01"
END = "2026-02-28"
REFERENCE_ADULTS = 100.0
SITES = ("malua", "knockrow", "dorey")


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start + 1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        rank = (start + 1 + stop) / 2
        for index in order[start:stop]:
            result[index] = rank
        start = stop
    return result


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2 or len(x) != len(y):
        return None
    xm, ym = sum(x) / len(x), sum(y) / len(y)
    numerator = sum((a - xm) * (b - ym) for a, b in zip(x, y))
    denominator = math.sqrt(sum((a - xm) ** 2 for a in x) * sum((b - ym) ** 2 for b in y))
    return numerator / denominator if denominator else None


def auc(labels: list[int], scores: list[float]) -> float | None:
    positives = sum(labels)
    negatives = len(labels) - positives
    if not positives or not negatives:
        return None
    score_ranks = ranks(scores)
    rank_sum = sum(rank for rank, label in zip(score_ranks, labels) if label)
    return (rank_sum - positives * (positives + 1) / 2) / (positives * negatives)


def load_events() -> list[dict[str, str]]:
    with EVENTS.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle)
                if row["season"] == "2025-26" and row["region"] == "nnsw"]
    if not rows:
        raise ValueError("No 2025-26 NNSW events found; build the event inventory first")
    if any(row["site_id"] not in SITES for row in rows):
        raise ValueError("Unexpected site in NNSW out-of-time event set")
    return rows


def scenario(site: str, activation: str, age_band: str) -> dict[str, float]:
    ages = AGE_BANDS[age_band]
    result = simulate(SimulationRequest(
        location=site, initialization="overwintering_adults", initial_eggs=0,
        initial_adult_females_by_age=uniform_distribution(REFERENCE_ADULTS * 0.5, ages),
        initial_adult_males_by_age=uniform_distribution(REFERENCE_ADULTS * 0.5, ages),
        seasonal_activation=activation, start_date=START, end_date=END,
    ))
    mobile = {}
    for row in result["results"]:
        mobile[row["date"]] = sum(row[f"n{i}"] for i in range(1, 6)) + row["adult_females"] + row["adult_males"]
    maximum = max(mobile.values())
    return {day: 100 * value / maximum if maximum else 0.0 for day, value in mobile.items()}


def join(events: list[dict[str, str]]) -> list[dict[str, object]]:
    models = {
        (site, activation, age): scenario(site, activation, age)
        for site in SITES for activation in ACTIVATION_PROFILES for age in AGE_BANDS
    }
    output = []
    for event in events:
        values = [models[(event["site_id"], activation, age)][event["visit_date"]]
                  for activation in ACTIVATION_PROFILES for age in AGE_BANDS]
        samples = int(event["recovered_sample_units"])
        confirmed = int(float(event["confirmed_fsb_count"])) + int(float(event["confirmed_bsb_count"]))
        output.append({
            "event_id": event["event_id"], "site_id": event["site_id"],
            "block_id": event["block_id"], "visit_date": event["visit_date"],
            "recovered_sample_units": samples,
            "confirmed_target_count": confirmed,
            "confirmed_target_detected": int(confirmed > 0),
            "count_per_recovered_sample": confirmed / samples if samples else "",
            "median_mife_mobile_relative_index": median(values),
            "lower_mife_mobile_relative_index": min(values),
            "upper_mife_mobile_relative_index": max(values),
            "fsb_management_window": event["fsb_management_window"],
            "independent_test_set": 1,
        })
    return output


def summarize(rows: list[dict[str, object]], scope: str, site: str) -> dict[str, object]:
    labels = [int(row["confirmed_target_detected"]) for row in rows]
    scores = [float(row["median_mife_mobile_relative_index"]) for row in rows]
    counts = [float(row["confirmed_target_count"]) for row in rows]
    positive = [score for score, label in zip(scores, labels) if label]
    negative = [score for score, label in zip(scores, labels) if not label]
    return {
        "scope": scope, "site_id": site, "events": len(rows),
        "positive_events": sum(labels),
        "total_confirmed_targets": int(sum(counts)),
        "auc_detection_vs_median_mobile_index": auc(labels, scores),
        "spearman_count_vs_median_mobile_index": pearson(ranks(counts), ranks(scores)),
        "median_index_positive_events": median(positive) if positive else "",
        "median_index_nondetection_events": median(negative) if negative else "",
        "events_with_explicit_fsb_management_within_21d": sum(
            row["fsb_management_window"] in {"0-7d", "8-21d"} for row in rows
        ),
        "interpretation_limit": "Diagnostic out-of-time validation; no fitted threshold and observations end before March-May peak",
    }


def write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    joined = join(load_events())
    summaries = [summarize(joined, "pooled", "pooled")]
    summaries.extend(summarize([row for row in joined if row["site_id"] == site], "site", site) for site in SITES)
    write(JOINED, joined)
    write(SUMMARY, summaries)
    print(f"Joined {len(joined)} independent events across all nine frozen scenarios")
    print("No scenario selected, threshold fitted, or biological parameter changed")


if __name__ == "__main__":
    main()
