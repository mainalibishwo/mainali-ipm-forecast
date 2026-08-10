"""
Import APDM parameter JSON and generate CSV parameter files.
"""

from pathlib import Path
import json
import pandas as pd


def export_parameters(json_file, output_dir):
    json_file = Path(json_file)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(json_file, "r") as f:
        p = json.load(f)

    # -------------------------------
    # Thermal development
    # -------------------------------

    rows = []

    for stage, temps in p["stage_parameters"].items():

        for temp, values in temps.items():

            rows.append({
                "stage": stage,
                "temperature_c": float(temp),
                "mean_duration_days": values["mean_duration_days"],
                "conditional_survival": values["conditional_survival"],
            })

    pd.DataFrame(rows).to_csv(
        output_dir / "thermal_development.csv",
        index=False,
    )

    # -------------------------------
    # Adult longevity
    # -------------------------------

    rows = []

    for temp, longevity in p["adult_female_longevity_days"].items():

        rows.append({
            "temperature_c": float(temp),
            "adult_longevity_days": longevity,
        })

    pd.DataFrame(rows).to_csv(
        output_dir / "adult_longevity.csv",
        index=False,
    )

    # -------------------------------
    # Fecundity
    # -------------------------------

    rows = []

    for temp, ages in p["fecundity_eggs_per_female_day"].items():

        for age, eggs in ages.items():

            rows.append({
                "temperature_c": float(temp),
                "female_age_days": int(age),
                "eggs_per_female_day": eggs,
            })

    pd.DataFrame(rows).to_csv(
        output_dir / "fecundity.csv",
        index=False,
    )


if __name__ == "__main__":

    export_parameters(
        "data/parameters/apdm_v1_parameters.json",
        "data/parameters",
    )

    print("Parameter export complete.")