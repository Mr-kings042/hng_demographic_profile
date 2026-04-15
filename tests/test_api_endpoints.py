import pytest


class TestHealthAndRoot:
    """Test health check and root endpoints"""
    
    def test_health_check(self, client):
        """Test GET /health returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Test GET / returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Demographic Profile API"
        assert data["version"] == "1.0.0"


class TestProfileCreationErrors:
    """Test error cases for profile creation"""
    
    def test_create_profile_invalid_empty_name(self, client):
        """Test creating profile with empty name"""
        response = client.post("/api/profiles", json={"name": ""})
        # Empty string is caught by Pydantic validator
        assert response.status_code == 422
    
    def test_create_profile_invalid_whitespace_name(self, client):
        """Test creating profile with whitespace only"""
        response = client.post("/api/profiles", json={"name": "   "})
        # Whitespace only is caught by Pydantic validator
        assert response.status_code == 422
    
    def test_create_profile_missing_name_field(self, client):
        """Test creating profile without name field"""
        response = client.post("/api/profiles", json={})
        assert response.status_code == 422



class TestProfileRetrieval:
    """Test profile retrieval endpoints"""
    
    def test_get_nonexistent_profile(self, client):
        """Test getting non-existent profile"""
        response = client.get("/api/profiles/nonexistent-id")
        assert response.status_code == 404
        # HTTPException detail is nested in 'detail' field
        data = response.json()
        assert "detail" in data or "status" in data
    
    def test_list_profiles(self, client):
        """Test listing all profiles"""
        response = client.get("/api/profiles")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "count" in data
        assert "data" in data
        assert isinstance(data["data"], list)


class TestProfileDeletion:
    """Test profile deletion endpoints"""
    
    def test_delete_nonexistent_profile(self, client):
        """Test deleting non-existent profile"""
        response = client.delete("/api/profiles/nonexistent-id")
        assert response.status_code == 404


class TestResponseStructure:
    """Test response structure and format"""
    
    def test_list_response_structure(self, client):
        """Test list response has correct structure"""
        response = client.get("/api/profiles")
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "success"
        assert "count" in data
        assert "data" in data
        assert isinstance(data["count"], int)
        assert isinstance(data["data"], list)
    
    def test_error_response_structure(self, client):
        """Test error response has correct structure"""
        response = client.get("/api/profiles/nonexistent")
        assert response.status_code == 404
        data = response.json()
        
        # HTTPException errors are wrapped in 'detail' with the error dict
        assert "detail" in data
        if isinstance(data["detail"], dict):
            assert "status" in data["detail"]
            assert data["detail"]["status"] == "error"
