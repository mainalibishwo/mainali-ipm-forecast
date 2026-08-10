from pathlib import Path

import pandas as pd


PARAMETER_DIR = Path("data/parameters")


def test_parameter_files_exist():
    assert (PARAMETER_DIR / "thermal_development.csv").exists()
    assert (PARAMETER_DIR / "fecundity.csv").exists()
    assert (PARAMETER_DIR / "adult_survival.csv").exists()


def test_thermal_columns():
    df = pd.read_csv(PARAMETER_DIR / "thermal_development.csv")

    assert list(df.columns) == [
        "stage",
        "temperature_c",
        "mean_duration_days",
        "conditional_survival",
    ]


def test_fecundity_columns():
    df = pd.read_csv(PARAMETER_DIR / "fecundity.csv")

    assert list(df.columns) == [
        "temperature_c",
        "female_age_days",
        "eggs_per_female_day",
    ]


def test_adult_survival_columns():
    df = pd.read_csv(PARAMETER_DIR / "adult_survival.csv")

    assert list(df.columns) == [
        "temperature_c",
        "adult_age_days",
        "conditional_survival",
    ]