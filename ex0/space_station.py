#!/usr/bin/env python3

import sys
from datetime import datetime
from typing import Optional

# Verify pydantic installation and its version
try:
    from pydantic import BaseModel, Field, ValidationError, VERSION
except ImportError:
    print("[ERROR] pydantic is not installed.")
    print('Install it with: pip install "pydantic>=2,<3"')
    sys.exit(1)

if int(VERSION.split(".")[0]) < 2:
    print(f"[ERROR] pydantic 2.x required, found {VERSION}")
    print('Upgrade it with: pip install --upgrade "pydantic>=2,<3"')
    sys.exit(1)


class SpaceStation(BaseModel):
    """Pydantic model with validated fields."""
    station_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=1, max_length=50)
    crew_size: int = Field(..., ge=1, le=20)
    power_level: float = Field(..., ge=0.0, le=100.0)
    oxygen_level: float = Field(..., ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = True
    notes: Optional[str] = Field(default=None, max_length=200)


def main() -> None:
    print("Space Station Data Validation")
    print("=" * 40)

    # Valid instanse
    station = SpaceStation(
        station_id="ISS001",
        name="International Space Station",
        crew_size=6,
        power_level=85.5,
        oxygen_level=92.3,
        last_maintenance="2026-04-13"
    )

    status = "Operational" if station.is_operational else "Not operational"
    print("Valid station created:")
    print(f"ID: {station.station_id}")
    print(f"Name: {station.name}")
    print(f"Crew: {station.crew_size} people")
    print(f"Power: {station.power_level}%")
    print(f"Oxygen: {station.oxygen_level}%")
    print(f"Status: {status}\n")
    print("=" * 40)

    # Invalid instance
    try:
        SpaceStation(
            station_id="ISS002",
            name="National Space Station",
            crew_size=60,
            power_level=85.5,
            oxygen_level=92.3,
            last_maintenance="2026-04-13",
        )
    except ValidationError as e:
        print("Expected validation error:")
        print(f"{e.errors()[0]['msg']}")


if __name__ == "__main__":
    main()
