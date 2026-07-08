from domain.value_objects import Port, Route

class RouteCalculator:
    """Domain Service: builds the sea route between two ports."""

    def calculate(self, origin: Port, destination: Port) -> Route:
        waypoints = (origin.coordinate, destination.coordinate)
        total_distance = origin.coordinate.distance_to(destination.coordinate)
        return Route(waypoints=waypoints, total_distance=total_distance)