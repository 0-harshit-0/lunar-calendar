from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Tuple


class LunarInfoQuery(BaseModel):
    date: str | None = Field(
        default=None,
        description="UTC date in YYYY-MM-DD"
    )

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format, expected YYYY-MM-DD"
            )
            # raise ValueError("Invalid date format, expected YYYY-MM-DD")
        return v

class FastingInfo(BaseModel):
    name: str
    description: str

class LunarResponse(BaseModel):
    date: str

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
    date: str
    planets: list[PlanetCoordinate]