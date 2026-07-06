"""Tests for the Ship aggregate (an Entity, identified by its IMO number).

A Ship is an Entity: two Ship objects are the same ship when they
share the same IMO number, even if their other attributes differ.
This is the opposite of a Value Object, which is compared by value.
"""
import pytest

from domain.ship import Ship
from domain.value_objects import IMONumber, Tonnage, Cargo

# =================== HELPER ======================
def make_ship(
    imo_number=IMONumber("IMO9074729"),
    name="Test Ship",
    capacity=Tonnage(200000),
):
    return Ship(imo_number=imo_number,
                name=name,
                capacity=capacity)
# =================================================

class TestShipIdentity:
    def test_same_imo_means_same_ship(self):
        imo = IMONumber("IMO9074729")
        ship_a = Ship(imo_number=imo, name="Ever Given", capacity=Tonnage(200000))
        ship_b = Ship(imo_number=imo, name="RENAMED", capacity=Tonnage(200000))
        assert ship_a == ship_b # same IMO -> same ship, even with different name

    def test_different_imo_means_different_ship(self):
        ship_a = Ship(IMONumber("IMO9074729"), "Ship A", Tonnage(200000))
        ship_b = Ship(IMONumber("IMO9811000"), "Ship B", Tonnage(200000))
        assert ship_a != ship_b

class TestShipCapacity:
    def test_can_carry_cargo_within_capacity(self):
        ship = make_ship(capacity=Tonnage(200000))
        cargo = Cargo("soybean", Tonnage(199999))
        assert ship.can_carry(cargo) is True

    def test_cannot_carry_cargo_exceeding_capacity(self):
        ship = make_ship(capacity=Tonnage(200000))
        cargo = Cargo("soybean", Tonnage(500000))
        assert ship.can_carry(cargo) is False

class TestShipInvariants:
    def test_rejects_empty_name(self):
        with pytest.raises(ValueError):
            make_ship(name="")

    def test_rejects_zero_capacity(self):
        with pytest.raises(ValueError):
            make_ship(capacity=Tonnage(0))