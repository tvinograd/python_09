#!/usr/bin/env python3

import sys
from datetime import datetime
from enum import Enum

# Verify pydantic installation and its version
try:
    from pydantic import (
        BaseModel,
        Field,
        ValidationError,
        model_validator,
        VERSION
    )
except ImportError:
    print("[ERROR] pydantic is not installed.")
    print('Install it with: pip install "pydantic>=2,<3"')
    sys.exit(1)

if int(VERSION.split(".")[0]) < 2:
    print(f"[ERROR] pydantic 2.x required, found {VERSION}")
    sys.exit(1)


class Rank(str, Enum):
    """Crew rank hierarchy."""
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """Pydantic model for individual crew member."""
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    """Pydantic model for mission."""
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: list[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def check_mission_rules(self) -> "SpaceMission":
        """Rules after basic validation."""
        # Rule 1: Mission ID
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')

        # Rule 2: Mandatory ranks
        mandatory_ranks = {Rank.COMMANDER, Rank.CAPTAIN}
        has_leader = any(i.rank in mandatory_ranks for i in self.crew)
        if not has_leader:
            raise ValueError("Must have at least one Commander or Captain")

        # Rule 3: Experienced crew for long missions
        if self.duration_days > 365:
            experienced = sum(1 for i in self.crew if i.years_experience >= 5)
            ratio = experienced / len(self.crew)
            if ratio < 0.5:
                raise ValueError(
                    "Long missions (> 365 days) need "
                    "50% experienced crew (5+ years)"
                )

        # Rule 4: Active crew members
        if not all(i.is_active for i in self.crew):
            raise ValueError("All crew members must be active")

        return self


def print_mission(mission: SpaceMission) -> None:
    """Print mission info."""
    print("Valid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for i in mission.crew:
        print(f"- {i.name} ({i.rank.value}) - {i.specialization}")
    print()


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 40)

    # Valid mission
    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2024, 4, 19),
        duration_days=900,
        budget_millions=2500.0,
        crew=[
            CrewMember(
                member_id="MARS001",
                name="Sarah Connor",
                rank=Rank.COMMANDER,
                age=50,
                specialization="Mission Command",
                years_experience=25,
            ),
            CrewMember(
                member_id="MARS002",
                name="John Smith",
                rank=Rank.LIEUTENANT,
                age=34,
                specialization="Navigation",
                years_experience=9,
            ),
            CrewMember(
                member_id="MARS003",
                name="Alice Johnson",
                rank=Rank.OFFICER,
                age=34,
                specialization="Engineering",
                years_experience=9,
            ),
        ],
    )
    print_mission(mission)
    print("=" * 40)

    # Invalid mission
    try:
        SpaceMission(
            mission_id="M2024_TITAN",
            mission_name="Solar Observatory Research Mission",
            destination="Solar Observatory",
            launch_date=datetime(2024, 4, 19),
            duration_days=451,
            budget_millions=500.0,
            crew=[
                CrewMember(
                    member_id="CM001",
                    name="Sarah Williams",
                    rank=Rank.CADET,
                    age=22,
                    specialization="Research",
                    years_experience=1,
                ),
            ],
        )
    except ValidationError as e:
        print("Expected validation error:")
        print(f"{e.errors()[0]['msg']}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
