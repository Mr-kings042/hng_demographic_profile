import os
import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import DemographicProfile
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException

load_dotenv()

# External APIs
GENDERIZE_API = "https://api.genderize.io"
AGIFY_API = "https://api.agify.io"
NATIONALIZE_API = "https://api.nationalize.io"

# API Timeout
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))


async def fetch_genderize_data(name: str) -> Dict[str, Any]:
    """Fetch gender data from Genderize API"""
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                GENDERIZE_API,
                params={"name": name}
            )
            response.raise_for_status()
            data = response.json()

            # Validate response
            if data.get("gender") is None or data.get("count", 0) == 0:
                raise ValueError("Invalid response from Genderize")

            return {
                "gender": data.get("gender"),
                "gender_probability": data.get("probability"),
                "sample_size": data.get("count")
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail={"status": "error", "message": "Genderize returned an invalid response"})


async def fetch_agify_data(name: str) -> Dict[str, Any]:
    """Fetch age data from Agify API"""
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                AGIFY_API,
                params={"name": name}
            )
            response.raise_for_status()
            data = response.json()

            # Validate response
            if data.get("age") is None:
                raise ValueError("Invalid response from Agify")

            age = data.get("age")
            age_group = classify_age_group(age)

            return {
                "age": age,
                "age_group": age_group
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail={"status": "error", "message": "Agify returned an invalid response"})


async def fetch_nationalize_data(name: str) -> Dict[str, Any]:
    """Fetch nationality data from Nationalize API"""
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                NATIONALIZE_API,
                params={"name": name}
            )
            response.raise_for_status()
            data = response.json()

            # Validate response
            countries = data.get("country", [])
            if not countries or len(countries) == 0:
                raise ValueError("Invalid response from Nationalize")

            # Find country with highest probability
            top_country = max(countries, key=lambda x: x.get("probability", 0))
            
            return {
                "country_id": top_country.get("country_id"),
                "country_probability": top_country.get("probability")
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail={"status": "error", "message": "Nationalize returned an invalid response"})


def classify_age_group(age: int) -> str:
    """Classify age into age groups"""
    if age < 0:
        return "unknown"
    elif age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    else:
        return "senior"


async def fetch_and_store_profile(db: Session, name: str) -> Tuple[DemographicProfile, bool]:
    """
    Fetch demographic data from external APIs and store in database.
    Handles duplicate detection based on name (case-insensitive).
    
    Returns:
        Tuple of (profile, is_new) where is_new is True if profile was just created
    """
    # Check if profile already exists (case-insensitive)
    existing_profile = db.query(DemographicProfile).filter(
        DemographicProfile.name.ilike(name)
    ).first()

    if existing_profile:
        return existing_profile, False

    # Fetch data from all APIs
    gender_data = await fetch_genderize_data(name)
    age_data = await fetch_agify_data(name)
    nationality_data = await fetch_nationalize_data(name)

    # Combine all data
    profile_data = {
        **gender_data,
        **age_data,
        **nationality_data,
        "name": name  # Preserve original name casing
    }

    # Create new profile
    new_profile = DemographicProfile(**profile_data)
    db.add(new_profile)
    
    try:
        db.commit()
        db.refresh(new_profile)
        return new_profile, True
    except IntegrityError:
        db.rollback()
        # Try to fetch again in case another request created it simultaneously
        existing_profile = db.query(DemographicProfile).filter(
            DemographicProfile.name.ilike(name)
        ).first()
        if existing_profile:
            return existing_profile, False
        raise


def get_profile_by_id(db: Session, profile_id: str) -> Optional[DemographicProfile]:
    """Get profile by ID"""
    profile = db.query(DemographicProfile).filter(
        DemographicProfile.id == profile_id
    ).first()
    return profile


def get_all_profiles(
    db: Session,
    gender: Optional[str] = None,
    country_id: Optional[str] = None,
    age_group: Optional[str] = None
) -> list:
    """Get all profiles with optional filtering"""
    query = db.query(DemographicProfile)

    if gender:
        query = query.filter(DemographicProfile.gender.ilike(gender))

    if country_id:
        query = query.filter(DemographicProfile.country_id.ilike(country_id))

    if age_group:
        query = query.filter(DemographicProfile.age_group.ilike(age_group))

    return query.all()


def delete_profile(db: Session, profile_id: str) -> bool:
    """Delete profile by ID"""
    profile = db.query(DemographicProfile).filter(
        DemographicProfile.id == profile_id
    ).first()

    if not profile:
        return False

    db.delete(profile)
    db.commit()
    return True
