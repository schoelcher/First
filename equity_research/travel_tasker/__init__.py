"""Travel tasker automation package.

This module automates flight-day logistics:
1. Read flights from calendar.
2. Classify local vs international.
3. Compute recommended airport arrival and pickup times.
4. Schedule an UberX.
"""

from .models import Flight, RidePlan
from .service import TravelTasker

__all__ = ["Flight", "RidePlan", "TravelTasker"]
