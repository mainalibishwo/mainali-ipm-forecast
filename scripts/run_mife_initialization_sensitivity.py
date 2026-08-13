#!/usr/bin/env python3
"""Run the preregistered MIFE initialization ensemble before field joins."""

from __future__ import annotations

import csv
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.api import SimulationRequest, simulate


SITES = ("malua", "knockrow", "dorey")
ACTIVATION_PROFILES = ("conservative", "central", "permissive")
TOTAL_ADULTS = (10.0, 100.0, 1000.0)
AGE_BANDS = {
    "young": range(0, 31),
    "mixed": range(0, 91),
    "older": range(60, 121),
}
START = "2024-07-01"
END = "2025-06-30"
OUTPUT = REPO_ROOT / "data/output/MIFE_v0.1_initialization_sensitivity.csv"


def uniform_distribution(total: float, ages: range) -> dict[int, float]:
    per_age = total / len(ages)
    return {age: per_age for age in ages}


def summarize(
    site: str,
    activation_profile: str,
    age_band: str,
    total_adults: float,
) -> dict:
    ages = AGE_BANDS[age_band]
    females = uniform_distribution(total_adults * 0.5, ages)
    males = uniform_distribution(total_adults * 0.5, ages)

    result = simulate(
        SimulationRequest(
            location=site,
            initialization="overwintering_adults",
            initial_eggs=0,
            initial_adult_females_by_age=females,
            initial_adult_males_by_age=males,
            seasonal_activation=activation_profile,
            start_date=START,
            end_date=END,
        )
    )
    rows = result["results"]
    for row in rows:
        row["mobile_population"] = (
            row["n1"] + row["n2"] + row["n3"]
            + row["n4"] + row["n5"]
            + row["adult_females"] + row["adult_males"]
        )

    first_reproduction = next(
        (row["date"] for row in rows if row["eggs_produced"] > 0),
        None,
    )
    peak_mobile = max(rows, key=lambda row: row["mobile_population"])

    return {
        "site": site,
        "activation_profile": activation_profile,
        "adult_age_band": age_band,
        "initial_total_adults": total_adults,
        "start_date": START,
        "end_date": END,
        "first_reproduction": first_reproduction,
        "peak_mobile_date": peak_mobile["date"],
        "peak_mobile_population": peak_mobile["mobile_population"],
        "peak_total_date": result["peak_date"],
        "peak_total_population": result["peak_population"],
        "final_population": result["final_population"],
    }


def main() -> None:
    summaries = [
        summarize(site, profile, age_band, abundance)
        for site in SITES
        for profile in ACTIVATION_PROFILES
        for age_band in AGE_BANDS
        for abundance in TOTAL_ADULTS
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    print(f"Saved {len(summaries)} preregistered runs to {OUTPUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
