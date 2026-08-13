#!/usr/bin/env python3
"""Create orchard-level diagnostics for the frozen MIFE field validation.

Screening flags in this script describe model–observation discrepancies. They
are not biological thresholds and are not used to select a model scenario.
"""

from __future__ import annotations

import csv
from datetime import datetime
import os
from pathlib import Path
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mife-matplotlib")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_mife_field_validation import load_events, run_scenario
from scripts.run_mife_initialization_sensitivity import ACTIVATION_PROFILES, AGE_BANDS, SITES


OUTPUT_DIR = REPO_ROOT / "data/output/diagnostics"
DISCREPANCIES = REPO_ROOT / "data/output/MIFE_v0.1_NNSW_Event_Diagnostics.csv"
REFERENCE_ABUNDANCE = 100.0


def scenario_trajectories(site: str) -> list[dict]:
    return [
        {
            "profile": profile,
            "age_band": age_band,
            **run_scenario(site, profile, age_band, REFERENCE_ABUNDANCE),
        }
        for profile in ACTIVATION_PROFILES
        for age_band in AGE_BANDS
    ]


def event_diagnostic(event: dict, trajectories: list[dict]) -> dict:
    states = [trajectory["by_date"][event["sample_date"]] for trajectory in trajectories]
    pressure = np.array([state["mobile_relative_index"] for state in states])
    adults = np.array([state["adults"] for state in states])
    nymphs = np.array([sum(state[f"n{i}"] for i in range(1, 6)) for state in states])
    adult_share = np.divide(adults, adults + nymphs, out=np.zeros_like(adults), where=(adults + nymphs) > 0)

    observed = int(event["Amblypelta_total"])
    effort = int(event["containers_sampled"])
    days = int(event["days_since_fsb_mgmt"]) if event["days_since_fsb_mgmt"] else None
    flags = []
    if days is not None and days <= 21:
        flags.append("management-confounded")
    if effort <= 15:
        flags.append("lower recovered sampling effort")
    if observed > 0 and float(np.median(pressure)) < 10.0:
        flags.append("positive detection during low modelled relative pressure")
    if observed == 0 and float(np.median(pressure)) >= 25.0:
        flags.append("non-detection during elevated modelled relative pressure")
    if not flags:
        flags.append("no strong screening flag")

    return {
        **event,
        "ensemble_scenarios": len(states),
        "mobile_index_min": float(pressure.min()),
        "mobile_index_median": float(np.median(pressure)),
        "mobile_index_max": float(pressure.max()),
        "adult_share_min": float(adult_share.min()),
        "adult_share_median": float(np.median(adult_share)),
        "adult_share_max": float(adult_share.max()),
        "diagnostic_flags": "; ".join(flags),
    }


def plot_site(site: str, events: list[dict], trajectories: list[dict]) -> Path:
    dates = [datetime.fromisoformat(row["date"]) for row in trajectories[0]["by_date"].values()]
    pressure = np.array([
        [row["mobile_relative_index"] for row in trajectory["by_date"].values()]
        for trajectory in trajectories
    ])
    adult_share_rows = []
    for trajectory in trajectories:
        shares = []
        for row in trajectory["by_date"].values():
            nymphs = sum(row[f"n{i}"] for i in range(1, 6))
            mobile = nymphs + row["adults"]
            shares.append(100.0 * row["adults"] / mobile if mobile else 0.0)
        adult_share_rows.append(shares)
    adult_share = np.array(adult_share_rows)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ax, ax_stage = axes
    ax.fill_between(dates, pressure.min(axis=0), pressure.max(axis=0), color="#87a8c7", alpha=0.32,
                    label="Nine-scenario range")
    ax.plot(dates, np.median(pressure, axis=0), color="#1f4e79", linewidth=2.0,
            label="Nine-scenario median")

    for event in events:
        date = datetime.fromisoformat(event["sample_date"])
        observed = int(event["Amblypelta_total"])
        states = [trajectory["by_date"][event["sample_date"]] for trajectory in trajectories]
        y = float(np.median([state["mobile_relative_index"] for state in states]))
        if observed:
            ax.scatter(date, y, s=75 + 35 * observed, marker="o", color="#c43c39", edgecolor="white",
                       linewidth=0.8, zorder=5)
            ax.annotate(f"{observed} FSB", (date, y), xytext=(0, 9), textcoords="offset points",
                        ha="center", fontsize=8, color="#8c2624")
        else:
            ax.scatter(date, y, s=45, marker="x", color="#303030", linewidth=1.4, zorder=5)
        if event["days_since_fsb_mgmt"] and int(event["days_since_fsb_mgmt"]) <= 21:
            ax.axvline(date, color="#e39d26", linewidth=1.0, linestyle=":", alpha=0.8)

    ax.set_ylabel("Mobile relative pressure (0–100)")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="upper left", frameon=False, ncol=2)
    ax.set_title(f"{site.title()} — frozen MIFE ensemble and 2024–25 field observations", loc="left", weight="bold")
    ax.text(1, 1.02, "● FSB detection   × no detection   ⋮ FSB management ≤21 d",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color="#444444")

    ax_stage.fill_between(dates, adult_share.min(axis=0), adult_share.max(axis=0),
                          color="#8ebf88", alpha=0.30)
    ax_stage.plot(dates, np.median(adult_share, axis=0), color="#2f6b35", linewidth=1.8)
    ax_stage.set_ylabel("Adults in mobile\npopulation (%)")
    ax_stage.set_ylim(0, 100)
    ax_stage.grid(axis="y", alpha=0.2)
    ax_stage.set_xlabel("Date")
    ax_stage.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax_stage.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))

    fig.text(0.01, 0.01,
             "Envelope: conservative, central and permissive activation × young, mixed and older adult ages. "
             "Initial abundance is fixed at 100 because normalized trajectories are abundance-invariant.",
             fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"MIFE_v0.1_{site}_field_diagnostic.png"
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output


def main() -> None:
    events = load_events()
    diagnostics = []
    plots = []
    for site in SITES:
        trajectories = scenario_trajectories(site)
        site_events = [event for event in events if event["site"] == site]
        diagnostics.extend(event_diagnostic(event, trajectories) for event in site_events)
        plots.append(plot_site(site, site_events, trajectories))

    with DISCREPANCIES.open("w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(diagnostics[0]))
        writer.writeheader()
        writer.writerows(diagnostics)

    print(f"Saved {len(diagnostics)} event diagnostics to {DISCREPANCIES.relative_to(REPO_ROOT)}")
    for plot in plots:
        print(f"Saved {plot.relative_to(REPO_ROOT)}")
    print("Screening cut-offs are analytical flags only; no biological parameter was changed.")


if __name__ == "__main__":
    main()
