"""Tests for the leaf Value Objects of the maritime-logistics domain.

We write these tests FIRST (TDD). In Domain-Driven Design a Value
Object is defined by its invariants -- the rules that must always
hold true. Each invariant maps directly to a test
case, so the test suite becomes the executable specification of the
domain rules.

Writing the test before the implementation forces us to state the
rule first and the code second. That is the DDD way of modeling:
the behaviour and the constraints drive the design, not the other
way around.
"""
import pytest

from domain.value_objects import Tonnage, Coordinate, IMONumber


class TestTonnage:
    # Invariant: a Tonnage value can never be negative.
    def test_rejects_negative_value(self):
        with pytest.raises(ValueError):
            Tonnage(value=-1.0)

    # A valid (zero or positive) Tonnage is accepted.
    def test_accepts_zero_and_positive(self):
        assert Tonnage(value=0.0).value == 0.0
        assert Tonnage(value=500.0).value == 500.0


class TestCoordinate:
    # Invariant: latitude in [-90, 90] and longitude in [-180, 180].
    @pytest.mark.parametrize(
        "lat, lon",
        [
            (90.1, 0.0),
            (-90.1, 0.0),
            (0.0, 180.1),
            (0.0, -180.1),
        ],
    )
    def test_rejects_out_of_range(self, lat, lon):
        with pytest.raises(ValueError):
            Coordinate(latitude=lat, longitude=lon)

    # Boundary values are valid and are stored unchanged.
    def test_accepts_boundary_values(self):
        coordinate = Coordinate(latitude=-90.0, longitude=180.0)
        assert coordinate.latitude == -90.0
        assert coordinate.longitude == 180.0

    # A real-world coordinate (Port of Santos) is accepted.
    def test_accepts_valid_coordinate(self):
        coordinate = Coordinate(latitude=-23.95, longitude=-46.33)
        assert coordinate.latitude == -23.95
        assert coordinate.longitude == -46.33


class TestIMONumber:
    # Invariant: the value must match the format "IMO" + 7 digits.
    @pytest.mark.parametrize(
        "bad_value",
        [
            "9074729",      # missing prefix
            "IMO123",       # too few digits
            "IMOABCDEFG",   # non-digit characters
        ],
    )
    def test_rejects_malformed_value(self, bad_value):
        with pytest.raises(ValueError):
            IMONumber(value=bad_value)
    
    def test_rejects_invalid_checksum(self):
        with pytest.raises(ValueError):
            IMONumber(value="IMO9074720")

    # A well-formed IMO number is accepted and stored unchanged.
    def test_accepts_valid_value(self):
        assert IMONumber(value="IMO9074729").value == "IMO9074729"