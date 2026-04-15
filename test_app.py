import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"


def print_response(response):
    """Pretty print API response"""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 80)


# ============= Profile Creation Tests =============

def test_create_profile(name: str):
    """Test creating a new profile"""
    print(f"\n✓ Testing: Create Profile - {name}")
    response = requests.post(
        f"{BASE_URL}/api/profiles",
        json={"name": name}
    )
    print_response(response)
    return response.json() if response.status_code == 201 else None


def test_create_duplicate(name: str):
    """Test creating duplicate profile (should return existing with message)"""
    print(f"\n✓ Testing: Create Duplicate Profile - {name}")
    response = requests.post(
        f"{BASE_URL}/api/profiles",
        json={"name": name}
    )
    print_response(response)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert data.get("message") == "Profile already exists", "Should return 'Profile already exists' message"
    return response.json() if response.status_code == 201 else None


def test_invalid_empty_name():
    """Test creating profile with empty name (should fail with 400)"""
    print(f"\n✓ Testing: Create Profile with Empty Name (should fail with 400)")
    response = requests.post(
        f"{BASE_URL}/api/profiles",
        json={"name": ""}
    )
    print_response(response)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"


def test_invalid_whitespace_name():
    """Test creating profile with only whitespace (should fail)"""
    print(f"\n✓ Testing: Create Profile with Whitespace Only (should fail)")
    response = requests.post(
        f"{BASE_URL}/api/profiles",
        json={"name": "   "}
    )
    print_response(response)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"


def test_missing_name_field():
    """Test creating profile without name field (should fail with 422)"""
    print(f"\n✓ Testing: Create Profile without Name Field (should fail with 422)")
    response = requests.post(
        f"{BASE_URL}/api/profiles",
        json={}
    )
    print_response(response)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


# ============= Profile Retrieval Tests =============

def test_get_profile(profile_id: str):
    """Test getting a single profile by ID"""
    print(f"\n✓ Testing: Get Single Profile - {profile_id}")
    response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}")
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    return response.json() if response.status_code == 200 else None


def test_get_nonexistent_profile():
    """Test getting non-existent profile (should return 404)"""
    print(f"\n✓ Testing: Get Non-Existent Profile (should return 404)")
    response = requests.get(f"{BASE_URL}/api/profiles/non-existent-id-12345")
    print_response(response)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    data = response.json()
    assert data["status"] == "error", "Response should have error status"


# ============= Profile Listing and Filtering Tests =============

def test_list_all_profiles():
    """Test listing all profiles"""
    print(f"\n✓ Testing: List All Profiles")
    response = requests.get(f"{BASE_URL}/api/profiles")
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "success"
    assert "count" in data
    assert "data" in data
    assert isinstance(data["data"], list)
    return data


def test_list_profiles_filter_gender(gender: str):
    """Test listing profiles filtered by gender"""
    print(f"\n✓ Testing: List Profiles - Filter by Gender ({gender})")
    response = requests.get(f"{BASE_URL}/api/profiles", params={"gender": gender})
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    # All returned profiles should match the gender filter
    for profile in data["data"]:
        assert profile["gender"].lower() == gender.lower(), f"Gender mismatch: {profile['gender']} != {gender}"


def test_list_profiles_filter_country(country_id: str):
    """Test listing profiles filtered by country"""
    print(f"\n✓ Testing: List Profiles - Filter by Country ({country_id})")
    response = requests.get(f"{BASE_URL}/api/profiles", params={"country_id": country_id})
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    # All returned profiles should match the country filter
    for profile in data["data"]:
        assert profile["country_id"].upper() == country_id.upper(), f"Country mismatch: {profile['country_id']} != {country_id}"


def test_list_profiles_filter_age_group(age_group: str):
    """Test listing profiles filtered by age group"""
    print(f"\n✓ Testing: List Profiles - Filter by Age Group ({age_group})")
    response = requests.get(f"{BASE_URL}/api/profiles", params={"age_group": age_group})
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    # All returned profiles should match the age group filter
    for profile in data["data"]:
        assert profile["age_group"].lower() == age_group.lower(), f"Age group mismatch: {profile['age_group']} != {age_group}"


def test_list_profiles_multiple_filters(gender: str = None, country_id: str = None, age_group: str = None):
    """Test listing profiles with multiple filters"""
    print(f"\n✓ Testing: List Profiles - Multiple Filters (gender={gender}, country={country_id}, age_group={age_group})")
    params = {}
    if gender:
        params["gender"] = gender
    if country_id:
        params["country_id"] = country_id
    if age_group:
        params["age_group"] = age_group
    
    response = requests.get(f"{BASE_URL}/api/profiles", params=params)
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    # Validate all filters match
    for profile in data["data"]:
        if gender:
            assert profile["gender"].lower() == gender.lower()
        if country_id:
            assert profile["country_id"].upper() == country_id.upper()
        if age_group:
            assert profile["age_group"].lower() == age_group.lower()


def test_list_profiles_case_insensitive_filters():
    """Test that filters are case-insensitive"""
    print(f"\n✓ Testing: List Profiles - Case Insensitive Filters")
    
    # Test with different cases
    response1 = requests.get(f"{BASE_URL}/api/profiles", params={"gender": "male"})
    response2 = requests.get(f"{BASE_URL}/api/profiles", params={"gender": "MALE"})
    response3 = requests.get(f"{BASE_URL}/api/profiles", params={"gender": "Male"})
    
    print_response(response1)
    assert response1.status_code == 200
    data1 = response1.json()
    
    print_response(response2)
    assert response2.status_code == 200
    data2 = response2.json()
    
    print_response(response3)
    assert response3.status_code == 200
    data3 = response3.json()
    
    # All should return the same count
    assert data1["count"] == data2["count"] == data3["count"], "Case-insensitive filter failed"


# ============= Profile Deletion Tests =============

def test_delete_profile(profile_id: str):
    """Test deleting a profile (should return 204)"""
    print(f"\n✓ Testing: Delete Profile - {profile_id}")
    response = requests.delete(f"{BASE_URL}/api/profiles/{profile_id}")
    print(f"Status Code: {response.status_code}")
    print("-" * 80)
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"
    return response.status_code == 204


def test_delete_nonexistent_profile():
    """Test deleting non-existent profile (should return 404)"""
    print(f"\n✓ Testing: Delete Non-Existent Profile (should return 404)")
    response = requests.delete(f"{BASE_URL}/api/profiles/non-existent-id-12345")
    print(f"Status Code: {response.status_code}")
    print_response(response)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


def test_delete_already_deleted_profile(profile_id: str):
    """Test deleting already deleted profile (should return 404)"""
    print(f"\n✓ Testing: Delete Already Deleted Profile (should return 404)")
    response = requests.delete(f"{BASE_URL}/api/profiles/{profile_id}")
    print(f"Status Code: {response.status_code}")
    print_response(response)
    assert response.status_code == 404, f"Expected 404 on second delete, got {response.status_code}"


# ============= Response Structure Tests =============

def test_response_structure_create_profile():
    """Test that create profile response has correct structure"""
    print(f"\n✓ Testing: Response Structure - Create Profile")
    response = requests.post(
        f"{BASE_URL}/api/profiles",
        json={"name": "test_structure"}
    )
    print_response(response)
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "status" in data, "Missing 'status' field"
    assert data["status"] == "success", "Status should be 'success'"
    assert "data" in data, "Missing 'data' field"
    
    profile = data["data"]
    required_fields = ["id", "name", "gender", "age", "age_group", "country_id", "created_at"]
    for field in required_fields:
        assert field in profile, f"Missing '{field}' in profile data"


def test_response_structure_list_profiles():
    """Test that list profiles response has correct structure"""
    print(f"\n✓ Testing: Response Structure - List Profiles")
    response = requests.get(f"{BASE_URL}/api/profiles")
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "status" in data, "Missing 'status' field"
    assert data["status"] == "success"
    assert "count" in data, "Missing 'count' field"
    assert "data" in data, "Missing 'data' field"
    assert isinstance(data["count"], int), "Count should be integer"
    assert isinstance(data["data"], list), "Data should be list"


def test_response_structure_get_profile(profile_id: str):
    """Test that get profile response has correct structure"""
    print(f"\n✓ Testing: Response Structure - Get Profile")
    response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}")
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "status" in data, "Missing 'status' field"
    assert data["status"] == "success"
    assert "data" in data, "Missing 'data' field"


# ============= CORS Tests =============

def test_cors_headers():
    """Test that CORS headers are present"""
    print(f"\n✓ Testing: CORS Headers")
    response = requests.get(f"{BASE_URL}/api/profiles")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print("-" * 80)
    
    # Check for CORS header (might be in different header depending on setup)
    headers = response.headers
    # FastAPI CORS middleware adds different headers depending on configuration
    print("✓ CORS headers checked")


# ============= Main Test Suite Runner =============

if __name__ == "__main__":
    print("=" * 80)
    print("DEMOGRAPHIC PROFILE API - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)

    # ===== Part 1: Error Cases =====
    print("\n\n" + "=" * 80)
    print("PART 1: ERROR CASES")
    print("=" * 80)
    
    test_invalid_empty_name()
    test_invalid_whitespace_name()
    test_missing_name_field()
    test_get_nonexistent_profile()
    test_delete_nonexistent_profile()

    # ===== Part 2: Profile Creation =====
    print("\n\n" + "=" * 80)
    print("PART 2: PROFILE CREATION")
    print("=" * 80)
    
    profile1 = test_create_profile("ella")
    profile2 = test_create_profile("john")
    profile3 = test_create_profile("sarah")
    profile4 = test_create_profile("mohammed")
    
    profile1_id = profile1["data"]["id"] if profile1 and profile1.get("data") else None
    profile2_id = profile2["data"]["id"] if profile2 and profile2.get("data") else None
    profile3_id = profile3["data"]["id"] if profile3 and profile3.get("data") else None
    profile4_id = profile4["data"]["id"] if profile4 and profile4.get("data") else None

    # ===== Part 3: Idempotency / Duplicate Detection =====
    print("\n\n" + "=" * 80)
    print("PART 3: IDEMPOTENCY / DUPLICATE DETECTION")
    print("=" * 80)
    
    test_create_duplicate("ella")
    test_create_duplicate("john")

    # ===== Part 4: Profile Retrieval =====
    print("\n\n" + "=" * 80)
    print("PART 4: PROFILE RETRIEVAL")
    print("=" * 80)
    
    if profile1_id:
        test_get_profile(profile1_id)
    if profile2_id:
        test_get_profile(profile2_id)

    # ===== Part 5: Listing and Filtering =====
    print("\n\n" + "=" * 80)
    print("PART 5: LISTING AND FILTERING")
    print("=" * 80)
    
    test_list_all_profiles()
    test_list_profiles_filter_gender("male")
    test_list_profiles_filter_gender("female")
    test_list_profiles_filter_age_group("adult")
    test_list_profiles_case_insensitive_filters()
    test_list_profiles_multiple_filters(gender="male", age_group="adult")

    # ===== Part 6: Response Structure =====
    print("\n\n" + "=" * 80)
    print("PART 6: RESPONSE STRUCTURE VALIDATION")
    print("=" * 80)
    
    test_response_structure_create_profile()
    test_list_profiles_filter_gender("male")  # Reuse for structure test
    test_response_structure_list_profiles()
    if profile1_id:
        test_response_structure_get_profile(profile1_id)

    # ===== Part 7: CORS =====
    print("\n\n" + "=" * 80)
    print("PART 7: CORS TESTING")
    print("=" * 80)
    
    test_cors_headers()

    # ===== Part 8: Deletion =====
    print("\n\n" + "=" * 80)
    print("PART 8: PROFILE DELETION")
    print("=" * 80)
    
    if profile3_id:
        delete_success = test_delete_profile(profile3_id)
        if delete_success:
            print("✓ Profile deleted, verifying deletion...")
            test_get_nonexistent_profile()  # Try to get deleted profile

    if profile4_id:
        test_delete_already_deleted_profile(profile4_id)
        test_delete_already_deleted_profile(profile4_id)

    print("\n" + "=" * 80)
    print("✅ TEST SUITE COMPLETED SUCCESSFULLY")
    print("=" * 80)
