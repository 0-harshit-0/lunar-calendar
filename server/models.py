from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from typing import Tuple


class LunarInfoQuery(BaseModel):
    timestamp: str | None = Field(
        default=None,
        description="UTC timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD)"
    )
    
    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str | None) -> str | None:
        if v is None:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Try parsing ISO format (with or without 'T')
            dt = datetime.fromisoformat(v)
            
            # If no timezone, assume UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC
                dt = dt.astimezone(timezone.utc)
            
            # Return in your standard format (no 'T', no timezone)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
            
        except ValueError:
            raise ValueError(
                "Invalid timestamp format. Use ISO 8601 (e.g., 2026-04-22T15:00:00Z or 2026-04-22)"
            )

class FastingInfo(BaseModel):
    name: str
    description: str

class LunarResponse(BaseModel):
    timestamp: str | None = None

    ayana: str
    ritu: str
    masa: str
    paksha: str
    tithi: str
    phase: str

    surya_rashi: str
    chandra_rashi: str

    surya_longitude_deg: float
    chandra_longitude_deg: float
    longitudinal_angle_deg: float

    grahana: str

    surya_xyz: Tuple[float, float, float]
    chandra_xyz: Tuple[float, float, float]

    upavaas: list[FastingInfo]


class PlanetCoordinate(BaseModel):
    name: str
    xyz: Tuple[float, float, float]
    longitude_deg: float

class PlanetsResponse(BaseModel):
    timestamp: str
    planets: list[PlanetCoordinate]