from scripts.run_mife_field_validation import average_ranks, load_events, spearman


def test_validation_event_schema_and_counts():
    events = load_events()
    assert len(events) == 21
    assert sum(int(row["Amblypelta_total"]) > 0 for row in events) == 8
    assert sum(int(row["BSB"]) for row in events) == 0


def test_average_ranks_handles_ties():
    assert average_ranks([0, 0, 2, 1]) == [1.5, 1.5, 4.0, 3.0]


def test_spearman_recovers_monotonic_direction():
    assert abs(spearman([1, 2, 3], [10, 20, 30]) - 1.0) < 1e-12
    assert abs(spearman([1, 2, 3], [30, 20, 10]) + 1.0) < 1e-12
