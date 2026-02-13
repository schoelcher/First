from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import Flight, RidePlan
from .providers import CalendarProvider, TransitEstimator, UberProvider


@dataclass(slots=True)
class ArrivalPolicy:
    domestic_buffer: timedelta = timedelta(hours=2)
    international_buffer: timedelta = timedelta(hours=3)
    ride_safety_buffer: timedelta = timedelta(minutes=15)


class TravelTasker:
    """End-to-end orchestration to generate and optionally schedule a ride plan."""

    def __init__(
        self,
        *,
        calendar_provider: CalendarProvider,
        transit_estimator: TransitEstimator,
        uber_provider: UberProvider,
        arrival_policy: ArrivalPolicy | None = None,
    ):
        self.calendar_provider = calendar_provider
        self.transit_estimator = transit_estimator
        self.uber_provider = uber_provider
        self.arrival_policy = arrival_policy or ArrivalPolicy()

    def build_plan(self, *, pickup_location: str, now: datetime | None = None) -> RidePlan:
        now = now or datetime.now()
        flights = self.calendar_provider.get_upcoming_flights(start_at=now)
        if not flights:
            raise ValueError("No upcoming flights found in calendar.")

        next_flight = flights[0]
        arrival_time = self._recommended_airport_arrival(next_flight)
        drive_time = self.transit_estimator.estimate_drive_time(
            pickup_location=pickup_location,
            airport_code=next_flight.origin_airport,
            departure_time=arrival_time,
        )
        pickup_time = arrival_time - drive_time - self.arrival_policy.ride_safety_buffer

        return RidePlan(
            pickup_location=pickup_location,
            airport_code=next_flight.origin_airport,
            terminal=next_flight.terminal,
            flight_number=next_flight.flight_number,
            departure_time=next_flight.departure_time,
            recommended_airport_arrival=arrival_time,
            estimated_drive_duration=drive_time,
            pickup_time=pickup_time,
            is_international=next_flight.is_international,
        )

    def schedule(self, *, pickup_location: str, now: datetime | None = None) -> RidePlan:
        plan = self.build_plan(pickup_location=pickup_location, now=now)
        plan.ride_id = self.uber_provider.schedule_uberx(
            pickup_location=plan.pickup_location,
            airport_code=plan.airport_code,
            pickup_time=plan.pickup_time,
        )
        return plan

    def _recommended_airport_arrival(self, flight: Flight) -> datetime:
        buffer_time = (
            self.arrival_policy.international_buffer if flight.is_international else self.arrival_policy.domestic_buffer
        )

        rush_hour_bonus = timedelta(minutes=30) if self._is_rush_hour(flight.departure_time) else timedelta(0)
        return flight.departure_time - buffer_time - rush_hour_bonus

    @staticmethod
    def _is_rush_hour(departure_time: datetime) -> bool:
        return departure_time.hour in {6, 7, 8, 16, 17, 18}
