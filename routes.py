from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schema import (
    CreateProfileRequest,
    CreateProfileResponse,
    GetProfileResponse,
    ListProfilesResponse,
    ErrorResponse,
    ProfileData,
    SimpleProfileData
)
from services import (
    fetch_and_store_profile,
    get_profile_by_id,
    get_all_profiles,
    delete_profile
)
from typing import Optional


router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.post("", status_code=201, response_model=CreateProfileResponse)
async def create_profile(
    request: CreateProfileRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new demographic profile or return existing one if it already exists.
    Accepts a name and fetches demographic data from external APIs.
    """
    try:
        # Validate name
        if not request.name or not request.name.strip():
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": "Name cannot be empty"}
            )

        profile, is_new = await fetch_and_store_profile(db, request.name.strip())

        profile_data = ProfileData(
            id=profile.id,
            name=profile.name,
            gender=profile.gender,
            gender_probability=profile.gender_probability,
            sample_size=profile.sample_size,
            age=profile.age,
            age_group=profile.age_group,
            country_id=profile.country_id,
            country_probability=profile.country_probability,
            created_at=profile.created_at
        )

        message = None
        if not is_new:
            message = "Profile already exists"

        return CreateProfileResponse(
            status="success",
            message=message,
            data=profile_data
        )

    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"status": "error", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})


@router.get("/{id}", response_model=GetProfileResponse)
def get_profile(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a single profile by its ID.
    Returns 404 if the profile is not found.
    """
    profile = get_profile_by_id(db, id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )

    profile_data = ProfileData(
        id=profile.id,
        name=profile.name,
        gender=profile.gender,
        gender_probability=profile.gender_probability,
        sample_size=profile.sample_size,
        age=profile.age,
        age_group=profile.age_group,
        country_id=profile.country_id,
        country_probability=profile.country_probability,
        created_at=profile.created_at
    )

    return GetProfileResponse(
        status="success",
        data=profile_data
    )


@router.get("", response_model=ListProfilesResponse)
def list_profiles(
    gender: Optional[str] = Query(None),
    country_id: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieve all profiles with optional filtering by gender, country_id, or age_group.
    Query parameters are case-insensitive.
    """
    profiles = get_all_profiles(
        db=db,
        gender=gender,
        country_id=country_id,
        age_group=age_group
    )

    simple_profiles = [
        SimpleProfileData(
            id=profile.id,
            name=profile.name,
            gender=profile.gender,
            age=profile.age,
            age_group=profile.age_group,
            country_id=profile.country_id
        )
        for profile in profiles
    ]

    return ListProfilesResponse(
        status="success",
        count=len(simple_profiles),
        data=simple_profiles
    )


@router.delete("/{id}", status_code=204)
def delete_profile_endpoint(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a profile by its ID.
    Returns 204 No Content on success, 404 if not found.
    """
    success = delete_profile(db, id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )

    return None
