from __future__ import annotations

import argparse
from datetime import datetime

from .models import Flight
from .providers import InMemoryCalendarProvider, MockUberProvider, StaticTransitEstimator
from .service import TravelTasker


def build_demo_tasker() -> TravelTasker:
    demo_flight = Flight(
        flight_number="UA100",
        origin_airport="SFO",
        destination_airport="JFK",
        origin_country="US",
        destination_country="US",
        departure_time=datetime(2026, 1, 21, 9, 20),
        terminal="3",
    )
    return TravelTasker(
        calendar_provider=InMemoryCalendarProvider([demo_flight]),
        transit_estimator=StaticTransitEstimator(default_minutes=50),
        uber_provider=MockUberProvider(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Automatically schedule airport UberX from your upcoming flight.")
    parser.add_argument("--pickup-location", required=True, help="The only user input required for scheduling.")
    parser.add_argument("--dry-run", action="store_true", help="Build plan without scheduling an Uber.")
    args = parser.parse_args()

    tasker = build_demo_tasker()
    plan = tasker.build_plan(pickup_location=args.pickup_location) if args.dry_run else tasker.schedule(
        pickup_location=args.pickup_location
    )

    print(f"Flight: {plan.flight_number}")
    print(f"Type: {'International' if plan.is_international else 'Local'}")
    print(f"Airport: {plan.airport_code} Terminal {plan.terminal or 'TBD'}")
    print(f"Pickup time: {plan.pickup_time.isoformat(sep=' ', timespec='minutes')}")
    if plan.ride_id:
        print(f"UberX ride scheduled: {plan.ride_id}")


if __name__ == "__main__":
    main()
