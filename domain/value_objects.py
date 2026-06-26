import re
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

@dataclass(frozen=True)
class IMONumber:
    value: str

    def __post_init__(self):
        if not re.fullmatch(r"IMO\d{7}", self.value):
            raise ValueError("IMO number must be 'IMO' followed by 7 digits")