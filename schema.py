from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class CreateProfileRequest(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def name_cannot_be_empty_string(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Name must be a non-empty string")
        if v.strip() == "":
            raise ValueError("Name cannot be empty or only whitespace")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {"name": "kings"}
        }


class ProfileData(BaseModel):
    id: str
    name: str
    gender: Optional[str] = None
    gender_probability: Optional[float] = None
    sample_size: Optional[int] = None
    age: Optional[int] = None
    age_group: Optional[str] = None
    country_id: Optional[str] = None
    country_probability: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CreateProfileResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: ProfileData

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
                    "name": "ella",
                    "gender": "female",
                    "gender_probability": 0.99,
                    "sample_size": 1234,
                    "age": 46,
                    "age_group": "adult",
                    "country_id": "DRC",
                    "country_probability": 0.85,
                    "created_at": "2026-04-01T12:00:00Z"
                }
            }
        }


class GetProfileResponse(BaseModel):
    status: str
    data: ProfileData

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
                    "name": "emmanuel",
                    "gender": "male",
                    "gender_probability": 0.99,
                    "sample_size": 1234,
                    "age": 25,
                    "age_group": "adult",
                    "country_id": "NG",
                    "country_probability": 0.85,
                    "created_at": "2026-04-01T12:00:00Z"
                }
            }
        }


class SimpleProfileData(BaseModel):
    id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    age_group: Optional[str] = None
    country_id: Optional[str] = None

    class Config:
        from_attributes = True


class ListProfilesResponse(BaseModel):
    status: str
    count: int
    data: List[SimpleProfileData]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "count": 2,
                "data": [
                    {
                        "id": "id-1",
                        "name": "emmanuel",
                        "gender": "male",
                        "age": 25,
                        "age_group": "adult",
                        "country_id": "NG"
                    },
                    {
                        "id": "id-2",
                        "name": "sarah",
                        "gender": "female",
                        "age": 28,
                        "age_group": "adult",
                        "country_id": "US"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Profile not found"
            }
        }
