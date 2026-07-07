from dataclasses import dataclass, field
from datetime import datetime, UTC

from domain.value_objects import VoyageId, IMONumber

@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    occurred_on: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass(frozen=True, kw_only=True)
class ShipDeparted(DomainEvent):
    voyage_id: VoyageId
    ship_id: IMONumber