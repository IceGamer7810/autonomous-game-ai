from tools.run_soak_test import run


def test_synthetic_soak_harness_keeps_buffer_bounded():
    report = run(0.01)
    assert report["buffer_occupancy"] <= report["buffer_capacity"]
    assert report["iterations"] > 0
    assert report["evidence_class"].startswith("synthetic")
