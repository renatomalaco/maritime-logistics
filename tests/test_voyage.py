"""Tests for the Voyage aggregate root.

A Voyage is an Entity with a life cycle: PLANNED -> DEPARTED -> ARRIVED.
The aggregate protects the legal state transitions (its invariants) and
records a ShipDeparted domain event when it departs. These tests drive
that behaviour before the implementation exists (TDD).
"""
import pytest

from domain.voyage import Voyage
from domain.events import ShipDeparted
from domain.value_objects import (
    Port,
    Coordinate,
    VoyageId,
    IMONumber,
    Cargo,
    Tonnage,
    Route,
    Distance,
    VoyageStatus,
)


# =========================== HELPERS ============================
def make_voyage(origin=None, destination=None):
    santos = Port("Santos", "BRSSZ", Coordinate(-23.95, -46.33))
    shanghai = Port("Shanghai", "CNSHA", Coordinate(31.23, 121.47))
    return Voyage(
        id=VoyageId("v-1"),
        ship_id=IMONumber("IMO9074729"),
        origin=origin or santos,
        destination=destination or shanghai,
        cargo=Cargo("soybean", Tonnage(50000)),
    )


def make_route():
    santos = Coordinate(-23.95, -46.33)
    shanghai = Coordinate(31.23, 121.47)
    return Route(
        waypoints=(santos, shanghai),
        total_distance=Distance(nautical_miles=10500.0),
    )
# ================================================================


class TestVoyageLifecycle:
    # A brand-new voyage always starts in the PLANNED state.
    def test_new_voyage_starts_planned(self):
        voyage = make_voyage()
        assert voyage.status is VoyageStatus.PLANNED

    # A voyage cannot depart before a route has been assigned.
    def test_cannot_depart_without_route(self):
        voyage = make_voyage()
        with pytest.raises(ValueError):
            voyage.depart()

    # With a route assigned, departing moves the voyage to DEPARTED.
    def test_departs_after_route_assigned(self):
        voyage = make_voyage()
        voyage.assign_route(make_route())
        voyage.depart()
        assert voyage.status is VoyageStatus.DEPARTED

    def test_depart_records_ship_departed_event(self):
        # assign route, depart, then pull_events() returns one ShipDeparted
        voyage = make_voyage()
        voyage.assign_route(make_route())
        voyage.depart()
        events = voyage.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], ShipDeparted)

    def test_cannot_depart_twice(self):
        # assign route, depart, depart again -> ValueError
        voyage = make_voyage()
        voyage.assign_route(make_route())
        voyage.depart()
        with pytest.raises(ValueError):
            voyage.depart()

    def test_arrives_after_departure(self):
        # assign route, depart, arrive -> status is VoyageStatus.ARRIVED
        voyage = make_voyage()
        voyage.assign_route(make_route())
        voyage.depart()
        voyage.arrive()
        assert voyage.status is VoyageStatus.ARRIVED

    def test_cannot_arrive_without_departure(self):
        # arrive() on a PLANNED voyage -> ValueError
        voyage = make_voyage()
        with pytest.raises(ValueError):
            voyage.arrive()


class TestVoyageInvariants:
    def test_rejects_same_origin_and_destination(self):
        # make_voyage(origin=port, destination=port) -> ValueError
        santos = Port("Santos", "BRSSZ", Coordinate(-23.95, -46.33))
        with pytest.raises(ValueError):
            make_voyage(origin=santos, destination=santos)



class TestVoyageIdentity:
    # Two Voyage with the same VoyageId are equal (Entity),
    # even if other attributes differ
    def test_same_id_means_same_voyage(self):
        rotterdam = Port("Rotterdam", "NLRTM", Coordinate(51.95, 4.14))
        voyage_a = make_voyage()
        voyage_b = make_voyage(destination=rotterdam)   # same id, diff destination
        assert voyage_a == voyage_b


class TestVoyageEvents:
    # After pull_events() the internal list is cleared;
    # a second call returns an empty list
    def test_pull_events_clears_the_list(self):
        voyage = make_voyage()
        voyage.assign_route(make_route())
        voyage.depart()
        first = voyage.pull_events()
        second = voyage.pull_events()
        assert len(first) == 1
        assert second == []