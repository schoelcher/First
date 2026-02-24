from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from .models import Flight


class CalendarProvider(ABC):
    """Provides upcoming flights from a calendar source such as Google Calendar."""

    @abstractmethod
    def get_upcoming_flights(self, *, start_at: datetime) -> list[Flight]:
        raise NotImplementedError


class TransitEstimator(ABC):
    """Estimates road travel from pickup location to airport."""

    @abstractmethod
    def estimate_drive_time(self, *, pickup_location: str, airport_code: str, departure_time: datetime) -> timedelta:
        raise NotImplementedError


class UberProvider(ABC):
    """Schedules Uber rides. Implementations should use Uber APIs."""

    @abstractmethod
    def schedule_uberx(self, *, pickup_location: str, airport_code: str, pickup_time: datetime) -> str:
        raise NotImplementedError


class InMemoryCalendarProvider(CalendarProvider):
    """Simple provider for local testing and demos."""

    def __init__(self, flights: list[Flight]):
        self._flights = flights

    def get_upcoming_flights(self, *, start_at: datetime) -> list[Flight]:
        return sorted([f for f in self._flights if f.departure_time >= start_at], key=lambda f: f.departure_time)


class StaticTransitEstimator(TransitEstimator):
    """Deterministic estimator useful until map APIs are connected."""

    def __init__(self, default_minutes: int = 45):
        self.default_minutes = default_minutes

    def estimate_drive_time(self, *, pickup_location: str, airport_code: str, departure_time: datetime) -> timedelta:
        _ = (pickup_location, airport_code, departure_time)
        return timedelta(minutes=self.default_minutes)


class MockUberProvider(UberProvider):
    """Testing/dry-run provider that returns deterministic ride IDs."""

    def __init__(self):
        self.scheduled: list[tuple[str, str, datetime]] = []

    def schedule_uberx(self, *, pickup_location: str, airport_code: str, pickup_time: datetime) -> str:
        self.scheduled.append((pickup_location, airport_code, pickup_time))
        return f"uberx-{airport_code.lower()}-{pickup_time.strftime('%Y%m%d%H%M')}"
