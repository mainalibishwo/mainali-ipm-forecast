from scripts.plot_mife_field_diagnostics import event_diagnostic


def test_event_diagnostic_flags_management_without_changing_state():
    state = {
        "mobile_relative_index": 30.0,
        "adults": 2.0,
        "n1": 1.0,
        "n2": 1.0,
        "n3": 1.0,
        "n4": 1.0,
        "n5": 1.0,
    }
    event = {
        "site": "test",
        "sample_date": "2024-10-10",
        "containers_sampled": "20",
        "FSB": "0",
        "BSB": "0",
        "Amblypelta_total": "0",
        "last_fsb_mgmt_date": "2024-10-06",
        "days_since_fsb_mgmt": "4",
    }
    result = event_diagnostic(event, [{"by_date": {event["sample_date"]: state}}] * 9)
    assert "management-confounded" in result["diagnostic_flags"]
    assert result["adult_share_median"] == 2 / 7
