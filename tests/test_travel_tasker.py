from datetime import datetime

from equity_research.travel_tasker.models import Flight
from equity_research.travel_tasker.providers import InMemoryCalendarProvider, MockUberProvider, StaticTransitEstimator
from equity_research.travel_tasker.service import TravelTasker


def test_classifies_international_and_uses_3h_buffer():
    flight = Flight(
        flight_number="DL1",
        origin_airport="JFK",
        destination_airport="LHR",
        origin_country="US",
        destination_country="GB",
        departure_time=datetime(2026, 2, 1, 11, 0),
        terminal="4",
    )
    tasker = TravelTasker(
        calendar_provider=InMemoryCalendarProvider([flight]),
        transit_estimator=StaticTransitEstimator(default_minutes=60),
        uber_provider=MockUberProvider(),
    )

    plan = tasker.build_plan(pickup_location="Brooklyn, NY", now=datetime(2026, 1, 31, 8, 0))

    assert plan.is_international is True
    assert plan.recommended_airport_arrival == datetime(2026, 2, 1, 8, 0)
    assert plan.pickup_time == datetime(2026, 2, 1, 6, 45)


def test_classifies_local_and_adds_rush_hour_buffer():
    flight = Flight(
        flight_number="UA2",
        origin_airport="SFO",
        destination_airport="SEA",
        origin_country="US",
        destination_country="US",
        departure_time=datetime(2026, 3, 1, 8, 30),
        terminal="2",
    )
    tasker = TravelTasker(
        calendar_provider=InMemoryCalendarProvider([flight]),
        transit_estimator=StaticTransitEstimator(default_minutes=40),
        uber_provider=MockUberProvider(),
    )

    plan = tasker.build_plan(pickup_location="Palo Alto, CA", now=datetime(2026, 2, 28, 8, 0))

    assert plan.is_international is False
    assert plan.recommended_airport_arrival == datetime(2026, 3, 1, 6, 0)
    assert plan.pickup_time == datetime(2026, 3, 1, 5, 5)


def test_schedule_calls_uber_provider():
    flight = Flight(
        flight_number="AA10",
        origin_airport="DFW",
        destination_airport="MIA",
        origin_country="US",
        destination_country="US",
        departure_time=datetime(2026, 4, 1, 13, 30),
    )
    uber = MockUberProvider()
    tasker = TravelTasker(
        calendar_provider=InMemoryCalendarProvider([flight]),
        transit_estimator=StaticTransitEstimator(default_minutes=35),
        uber_provider=uber,
    )

    plan = tasker.schedule(pickup_location="Plano, TX", now=datetime(2026, 4, 1, 7, 0))

    assert plan.ride_id is not None
    assert uber.scheduled
    assert uber.scheduled[0][0] == "Plano, TX"
    assert uber.scheduled[0][1] == "DFW"
    assert isinstance(uber.scheduled[0][2], datetime)
