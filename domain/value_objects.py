import re
import math
from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class Tonnage:
    value: float

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Tonnage cannot be negative")

@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float

    def __post_init__(self):
        if self.latitude < -90 or self.latitude > 90:
            raise ValueError("The latitude must be between -90 and 90 degrees")
        if self.longitude < -180 or self.longitude > 180:
            raise ValueError("The longitude must be between -180 and 180 degrees")
    
    # The quotation marks around "Coordinate" and "Distance" in the type hints 
    # used to indicate forward references. This is necessary because the classes 
    # are defined later in the code
    def distance_to(self, other: "Coordinate") -> "Distance":
        earth_radius_nautical_miles = 3440.065
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        distance_lat = math.radians(other.latitude - self.latitude)
        distance_lon = math.radians(other.longitude - self.longitude)
        a = (math.sin(distance_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(distance_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return Distance(nautical_miles=earth_radius_nautical_miles * c)

@dataclass(frozen=True)
class IMONumber:
    value: str

    def __post_init__(self):
        if not re.fullmatch(r"IMO\d{7}", self.value):
            raise ValueError("IMO number must be 'IMO' followed by 7 digits")
        
        digits = self.value[3:]
        weights = (7, 6, 5, 4, 3, 2)
        check_digit = int(digits[6])
        checksum = sum(int(d) * w for d, w in zip(digits[:6], weights))
        if checksum % 10 != check_digit:
            raise ValueError("IMO number has an invalid check digit")

@dataclass(frozen=True)        
class Cargo:
    commodity: str
    weight: Tonnage

    def __post_init__(self):
        if not self.commodity.strip():
            raise ValueError("Cargo commodity must not be empty")
        if self.weight.value <= 0:
            raise ValueError("Cargo weight must be greater than zero")

@dataclass(frozen=True)
class Port:
    name: str
    locode: str
    coordinate: Coordinate

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Port name must not be empty")
        if not re.fullmatch(r"[A-Z]{5}", self.locode):
            raise ValueError("Port locode must be 5 uppercase letters (UN/LOCODE)")

@dataclass(frozen=True)
class Distance:
    nautical_miles: float

    def __post_init__(self):
        if self.nautical_miles < 0:
            raise ValueError("Distance cannot be negative")

@dataclass(frozen=True)
class Route:
    waypoints: tuple[Coordinate, ...]
    total_distance: Distance

    def __post_init__(self):
        if len(self.waypoints) < 2:
            raise ValueError("A route needs at least two waypoints")

class VoyageStatus(Enum):
    PLANNED = "PLANNED"
    DEPARTED = "DEPARTED"
    ARRIVED = "ARRIVED"

@dataclass(frozen=True)
class VoyageId:
    value: str

    def __post_init__(self):
        if not self.value.strip():
            raise ValueError("VoyageId must not be empty")

@dataclass(frozen=True)     
class FuelRate:
    tonnes_per_nautical_mile: float

    def __post_init__(self):
        if self.tonnes_per_nautical_mile <= 0:
            raise ValueError(...)