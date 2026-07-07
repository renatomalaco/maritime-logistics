from domain.events import ShipDeparted
from domain.value_objects import VoyageId, IMONumber

def test_ship_departed_carries_ids_and_timestamp():
    event = ShipDeparted(
        voyage_id=VoyageId("v-123"),
        ship_id=IMONumber("IMO9074729"),
    )
    assert event.voyage_id == VoyageId("v-123")
    assert event.ship_id == IMONumber("IMO9074729")
    assert event.occurred_on is not None