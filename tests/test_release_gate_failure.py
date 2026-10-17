"""Controlled failing test for the DD2482 delivery gate experiment."""


def test_release_gate_negative_control():
    actual = "deliberate failure"
    expected = "passing release gate"
    assert actual == expected, "Intentional failure for the DD2482 delivery-gate experiment"
