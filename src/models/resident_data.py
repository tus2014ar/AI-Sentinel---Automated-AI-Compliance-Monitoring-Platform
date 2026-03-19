from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class ResidentRecord:
    """Represents a single day's data for a resident."""
    resident_id: str
    date: date
    caregiver_response_time: float  # in minutes
    caregiver_time_with_resident: float  # in minutes
    movement_events_per_day: int
    steps_per_day: int
    time_spent_walking: float  # in minutes
    sit_to_stand_transitions: int
    sedentary_time: float  # in hours
    time_spent_upright: float  # in hours
    rooms_visited_per_day: int
    alert_triggered: bool
    alert_type: Optional[str]
    log_text: Optional[str]
