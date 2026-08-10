from pathlib import Path

import pytest

from backend.engine.parameter_manager import ParameterManager
from backend.engine.simulation import PopulationSimulationEngine


def create_parameter_files(folder: Path):

    (folder / "thermal_development.csv").write_text(
        "stage,temperature_c,mean_duration_days,conditional_survival\n"
        "Egg,20,10,0.95\n"
        "N1,20,8,0.94\n"
        "N2,20,8,0.94\n"
        "N3,20,8,0.94\n"
        "N4,20,8,0.94\n"
        "N5,20,8,0.94\n"
    )

    (folder / "fecundity.csv").write_text(
        "temperature_c,female_age_days,eggs_per_female_day\n"
        "20,5,2\n"
    )

    (folder / "adult_survival.csv").write_text(
        "temperature_c,adult_age_days,conditional_survival\n"
        "20,0,0.98\n"
        "20,1,0.97\n"
    )


def test_load_and_build_engine(tmp_path):

    create_parameter_files(tmp_path)

    manager = ParameterManager(tmp_path).load()

    engine = manager.build_engine()

    assert isinstance(engine, PopulationSimulationEngine)


def test_missing_parameter_file(tmp_path):

    with pytest.raises(FileNotFoundError):
        ParameterManager(tmp_path).load()


def test_invalid_fecundity(tmp_path):

    create_parameter_files(tmp_path)

    (tmp_path / "fecundity.csv").write_text(
        "temperature_c,female_age_days,eggs_per_female_day\n"
        "20,5,-1\n"
    )

    with pytest.raises(
        ValueError,
        match="Fecundity",
    ):
        ParameterManager(tmp_path).load()


def test_invalid_adult_survival(tmp_path):

    create_parameter_files(tmp_path)

    (tmp_path / "adult_survival.csv").write_text(
        "temperature_c,adult_age_days,conditional_survival\n"
        "20,0,1.5\n"
    )

    with pytest.raises(
        ValueError,
        match="Adult survival",
    ):
        ParameterManager(tmp_path).load()