#!/usr/bin/env python3
"""Join the frozen MIFE initialization ensemble to 21 NNSW field events.

This is validation, not calibration. It does not modify biological parameters,
and it reports every preregistered initialization scenario without selecting a
scenario for agreement with the observations.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.api import SimulationRequest, simulate
from scripts.run_mife_initialization_sensitivity import (
    ACTIVATION_PROFILES,
    AGE_BANDS,
    END,
    SITES,
    START,
    TOTAL_ADULTS,
    uniform_distribution,
)


EVENTS = REPO_ROOT / "data/validation/MIFE_v0.1_NNSW_21_events.csv"
JOINED_OUTPUT = REPO_ROOT / "data/output/MIFE_v0.1_NNSW_Field_Validation_Joined.csv"
SUMMARY_OUTPUT = REPO_ROOT / "data/output/MIFE_v0.1_NNSW_Field_Validation_Summary.csv"


def load_events() -> list[dict]:
    with EVENTS.open(newline="") as input_file:
        rows = list(csv.DictReader(input_file))

    if len(rows) != 21:
        raise ValueError(f"Expected 21 validation events; found {len(rows)}")
    if {site: sum(row["site"] == site for row in rows) for site in SITES} != {
        site: 7 for site in SITES
    }:
        raise ValueError("Expected exactly seven events for each validation site")
    if any(int(row["FSB"]) + int(row["BSB"]) != int(row["Amblypelta_total"]) for row in rows):
        raise ValueError("Combined Amblypelta counts must equal FSB + BSB")
    return rows


def average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start + 1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        rank = (start + 1 + stop) / 2.0
        for index in order[start:stop]:
            ranks[index] = rank
        start = stop
    return ranks


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2 or len(x) != len(y):
        return None
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    numerator = sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y))
    x_ss = sum((a - x_mean) ** 2 for a in x)
    y_ss = sum((b - y_mean) ** 2 for b in y)
    if x_ss == 0 or y_ss == 0:
        return None
    return numerator / math.sqrt(x_ss * y_ss)


def spearman(x: list[float], y: list[float]) -> float | None:
    return pearson(average_ranks(x), average_ranks(y))


def run_scenario(site: str, profile: str, age_band: str, abundance: float) -> dict:
    ages = AGE_BANDS[age_band]
    result = simulate(SimulationRequest(
        location=site,
        initialization="overwintering_adults",
        initial_eggs=0,
        initial_adult_females_by_age=uniform_distribution(abundance * 0.5, ages),
        initial_adult_males_by_age=uniform_distribution(abundance * 0.5, ages),
        seasonal_activation=profile,
        start_date=START,
        end_date=END,
    ))
    rows = result["results"]
    for row in rows:
        row["adults"] = row["adult_females"] + row["adult_males"]
        row["mobile_population"] = sum(row[f"n{i}"] for i in range(1, 6)) + row["adults"]
    maximum = max(row["mobile_population"] for row in rows)
    for row in rows:
        row["mobile_relative_index"] = 100.0 * row["mobile_population"] / maximum if maximum else 0.0
    return {
        "by_date": {row["date"]: row for row in rows},
        "peak_mobile": max(rows, key=lambda row: row["mobile_population"]),
    }


def join_events(events: list[dict]) -> list[dict]:
    joined = []
    by_site = {site: [row for row in events if row["site"] == site] for site in SITES}
    for site in SITES:
        for profile in ACTIVATION_PROFILES:
            for age_band in AGE_BANDS:
                for abundance in TOTAL_ADULTS:
                    model = run_scenario(site, profile, age_band, abundance)
                    for event in by_site[site]:
                        state = model["by_date"].get(event["sample_date"])
                        if state is None:
                            raise RuntimeError(f"No model state for {site} on {event['sample_date']}")
                        days = event["days_since_fsb_mgmt"]
                        joined.append({
                            **event,
                            "presence": int(event["Amblypelta_total"] != "0"),
                            "count_per_minimum_container": int(event["Amblypelta_total"]) / int(event["containers_sampled"]),
                            "recent_fsb_mgmt_21d": int(bool(days) and int(days) <= 21),
                            "activation_profile": profile,
                            "adult_age_band": age_band,
                            "initial_total_adults": abundance,
                            "scenario_peak_mobile_date": model["peak_mobile"]["date"],
                            "mife_mobile_population": state["mobile_population"],
                            "mife_mobile_relative_index": state["mobile_relative_index"],
                            "mife_egg": state["egg"],
                            "mife_n1": state["n1"],
                            "mife_n2": state["n2"],
                            "mife_n3": state["n3"],
                            "mife_n4": state["n4"],
                            "mife_n5": state["n5"],
                            "mife_adults": state["adults"],
                        })
    return joined


def summarize_group(rows: list[dict], scope: str, site: str) -> dict:
    counts = [float(row["Amblypelta_total"]) for row in rows]
    rates = [float(row["count_per_minimum_container"]) for row in rows]
    indices = [float(row["mife_mobile_relative_index"]) for row in rows]
    positive = [float(row["mife_mobile_relative_index"]) for row in rows if row["presence"]]
    zero = [float(row["mife_mobile_relative_index"]) for row in rows if not row["presence"]]
    first = rows[0]
    return {
        "scope": scope,
        "site": site,
        "activation_profile": first["activation_profile"],
        "adult_age_band": first["adult_age_band"],
        "initial_total_adults": first["initial_total_adults"],
        "events": len(rows),
        "positive_events": sum(int(row["presence"]) for row in rows),
        "spearman_count_vs_mobile_index": spearman(counts, indices),
        "spearman_count_per_minimum_container_vs_mobile_index": spearman(rates, indices),
        "mean_mobile_index_positive": sum(positive) / len(positive) if positive else None,
        "mean_mobile_index_zero": sum(zero) / len(zero) if zero else None,
        "scenario_peak_mobile_date": first["scenario_peak_mobile_date"] if site != "pooled" else "",
    }


def build_summaries(joined: list[dict]) -> list[dict]:
    summaries = []
    for profile in ACTIVATION_PROFILES:
        for age_band in AGE_BANDS:
            for abundance in TOTAL_ADULTS:
                scenario = [row for row in joined if row["activation_profile"] == profile
                            and row["adult_age_band"] == age_band
                            and float(row["initial_total_adults"]) == abundance]
                for site in SITES:
                    rows = [row for row in scenario if row["site"] == site]
                    summaries.append(summarize_group(rows, "site", site))
                summaries.append(summarize_group(scenario, "pooled", "pooled"))
                unconfounded = [row for row in scenario if not row["recent_fsb_mgmt_21d"]]
                summaries.append(summarize_group(unconfounded, "pooled_excluding_fsb_management_21d", "pooled"))
    return summaries


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = load_events()
    joined = join_events(events)
    summaries = build_summaries(joined)
    write_csv(JOINED_OUTPUT, joined)
    write_csv(SUMMARY_OUTPUT, summaries)
    print(f"Saved {len(joined)} joined rows to {JOINED_OUTPUT.relative_to(REPO_ROOT)}")
    print(f"Saved {len(summaries)} summaries to {SUMMARY_OUTPUT.relative_to(REPO_ROOT)}")
    print("All preregistered scenarios reported; no scenario was selected or fitted.")


if __name__ == "__main__":
    main()
