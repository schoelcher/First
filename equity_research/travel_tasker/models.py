from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True)
class Flight:
    """A normalized flight extracted from calendar and flight metadata APIs."""

    flight_number: str
    origin_airport: str
    destination_airport: str
    origin_country: str
    destination_country: str
    departure_time: datetime
    terminal: str | None = None

    @property
    def is_international(self) -> bool:
        return self.origin_country.strip().upper() != self.destination_country.strip().upper()


@dataclass(slots=True)
class RidePlan:
    """Final journey plan used for ride booking and user messaging."""

    pickup_location: str
    airport_code: str
    terminal: str | None
    flight_number: str
    departure_time: datetime
    recommended_airport_arrival: datetime
    estimated_drive_duration: timedelta
    pickup_time: datetime
    is_international: bool
    ride_id: str | None = None
