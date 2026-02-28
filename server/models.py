from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Tuple


class LunarInfoQuery(BaseModel):
    timestamp: str | None = Field(
        default=None,
        description="UTC timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str | None) -> str | None:
        if v is None:
            return v
        
        try:
            # Check if it matches the format exactly
            dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Expected YYYY-MM-DDTHH:MM:SS"
            )

class FastingInfo(BaseModel):
    name: str
    description: str

class LunarResponse(BaseModel):
    timestamp: str

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