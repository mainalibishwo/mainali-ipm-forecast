import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_multiseason_inventory_is_deidentified_and_complete():
    rows = read_csv("data/validation/MIFE_v0.1_multiseason_event_inventory.csv")
    assert len(rows) == 156
    assert {row["season"] for row in rows} == {"2023-24", "2024-25", "2025-26"}
    assert {row["region"] for row in rows} == {"nnsw", "seq", "cq"}
    forbidden = {"latitude", "longitude", "scout"}
    assert forbidden.isdisjoint(rows[0])


def test_out_of_time_nnsw_set_is_reserved_and_unambiguous():
    rows = read_csv("data/output/MIFE_v0.1_NNSW_2025_26_out_of_time_joined.csv")
    assert len(rows) == 18
    assert sum(int(row["confirmed_target_detected"]) for row in rows) == 5
    assert sum(int(row["confirmed_target_count"]) for row in rows) == 7
    assert all(row["independent_test_set"] == "1" for row in rows)


def test_no_fitted_threshold_is_reported():
    rows = read_csv("data/output/MIFE_v0.1_NNSW_2025_26_out_of_time_summary.csv")
    assert len(rows) == 4
    assert all("no fitted threshold" in row["interpretation_limit"] for row in rows)
