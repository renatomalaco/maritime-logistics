import pytest
from domain.services import RouteCalculator
from domain.value_objects import Coordinate, Port

class TestRouteDistanceCalc:
    def test_distance_to_same_point_is_zero(self):
        point = Coordinate(0.0, 0.0)
        assert point.distance_to(point).nautical_miles == pytest.approx(0.0)

    def test_one_degree_of_latitude_is_about_60_nautical_miles(self):
        a = Coordinate(0.0, 0.0)
        b = Coordinate(1.0, 0.0)
        assert a.distance_to(b).nautical_miles == pytest.approx(60.0, abs=0.5)

    def test_calculate_builds_route_between_ports(self):
        santos = Port("Santos", "BRSSZ", Coordinate(-23.95, -46.33))
        shangai = Port("Shangai", "CNSHA", Coordinate(31.23, 121.47))
        route = RouteCalculator().calculate(santos, shangai)
        assert route.waypoints == (santos.coordinate, shangai.coordinate)
        assert route.total_distance.nautical_miles > 0