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
from domain.value_objects import Cargo, Port, Distance, Route

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

class TestCargo:
    def test_rejects_empty_commodity(self):
        with pytest.raises(ValueError):
            Cargo(commodity="", weight=Tonnage(50000))

    def test_rejects_zero_weight(self):
        with pytest.raises(ValueError):
            Cargo(commodity="soybean", weight=Tonnage(0))

    def test_accepts_cargo(self):
        cargo = Cargo("soybean", Tonnage(50000))
        assert cargo.commodity == "soybean"
        assert cargo.weight.value == 50000

class TestPort:
    @pytest.mark.parametrize(
        "test_name, test_locode",
        [
            ("", "BR"),             # empty name
            ("Santos", "brssz"),    # locode lower case
        ]
    )
    def test_rejects_port(self, test_name, test_locode):
        valid_coordinate = Coordinate(-23.95, -46.33)
        with pytest.raises(ValueError):
            Port(name=test_name, locode=test_locode, coordinate=valid_coordinate)

    def test_accepts_port(self):
        port = Port("Santos", "BRSSZ", Coordinate(-23.95, -46.33))
        assert port.locode == "BRSSZ"

class TestDistance:
    def test_rejects_negative_distances(self):
        with pytest.raises(ValueError):
            Distance(nautical_miles=-1.0)

    def test_accepts_zero_and_positive(self):
        assert Distance(nautical_miles=0.0).nautical_miles == 0.0

class TestRoute:
    def test_rejects_fewer_than_two_waypoints(self):
        single = Coordinate(-23.95, -46.33)
        with pytest.raises(ValueError):
            Route(
                # single element tuple
                waypoints=(single,),
                total_distance=Distance(nautical_miles=0.0)
            )
    
    def test_accepts_valid_route(self):
        santos = Coordinate(-23.95, -46.33)
        shangai = Coordinate(31.23, 121.47)
        route = Route(
            waypoints=(santos, shangai),
            total_distance=Distance(nautical_miles=10500.0),
        )
        assert len(route.waypoints) == 2
        assert route.total_distance.nautical_miles == 10500.0