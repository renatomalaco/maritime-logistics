from domain.events import ShipDeparted
from domain.value_objects import Route, VoyageStatus

class Voyage:
    def __init__(self, id, ship_id, origin, destination, cargo):
        if origin == destination:
            raise ValueError("Origin and destination must be different")
        self._id = id
        self._ship_id = ship_id
        self._origin = origin
        self._destination = destination
        self._cargo = cargo
        self._route = None
        self._status = VoyageStatus.PLANNED
        self._events = []

    @property
    def status(self) -> VoyageStatus:
        return self._status
    
    def assign_route(self, route: Route) -> None:
        if self._status is not VoyageStatus.PLANNED:
            raise ValueError("A route can only be assigned to a planned voyage")
        self._route = route

    def depart(self) -> None:
        if self._status is not VoyageStatus.PLANNED:
            raise ValueError("Only a planned voyage can depart")
        if self._route is None:
            raise ValueError("A voyage cannot depart without a route")
        self._status = VoyageStatus.DEPARTED
        self._events.append(ShipDeparted(voyage_id=self._id,
                                         ship_id=self._ship_id))
    
    def arrive(self) -> None:
        if self._status is not VoyageStatus.DEPARTED:
            raise ValueError("Only a departed voyage can arrive")
        self._status = VoyageStatus.ARRIVED

    def pull_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Voyage):
            return NotImplemented
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)