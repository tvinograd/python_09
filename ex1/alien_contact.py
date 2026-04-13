#!/usr/bin/env python3

import sys
from datetime import datetime
from enum import Enum
from typing import Optional

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


class ContactType(str, Enum):
    """Alien contact types."""
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """Pydantic model with validated fields."""
    contact_id: str = Field(..., min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(..., min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(..., ge=0.0, le=10.0)
    duration_minutes: int = Field(..., ge=1, le=1440)
    witness_count: int = Field(..., ge=1, le=100)
    message_received: Optional[str] = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def check_business_rules(self) -> "AlienContact":
        """Rules after basic validation."""
        if not self.contact_id.startswith("AC"):
            raise ValueError('Contact ID must start with "AC"')

        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")

        if (self.contact_type == ContactType.TELEPATHIC
                and self.witness_count < 3):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
            )

        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError(
                "Strong signals (> 7.0) should include received messages"
            )

        return self


def print_contact(contact: AlienContact) -> None:
    """Print a contact report."""
    message = contact.message_received or "(none)"
    print("Valid contact report:")
    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    print(f"Message: '{message}'\n")


def main() -> None:
    print("Alien Contact Log Validation")
    print("=" * 40)

    # Valid report
    contact = AlienContact(
        contact_id="AC_2024_001",
        timestamp="2026-04-13",
        location="Area 51, Nevada",
        contact_type="radio",
        signal_strength=8.5,
        duration_minutes=45,
        witness_count=5,
        message_received="Greetings from Zeta Reticuli",
    )
    print_contact(contact)
    print("=" * 40)

    # Invalid report
    try:
        AlienContact(
            contact_id="AC_2024_002",
            timestamp="2026-04-13",
            location="Area 51, Nevada",
            contact_type="telepathic",
            signal_strength=5,
            duration_minutes=45,
            witness_count=1,
        )
    except ValidationError as e:
        print("Expected validation error:")
        print(f"{e.errors()[0]['msg']}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
