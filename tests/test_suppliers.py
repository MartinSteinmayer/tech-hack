import pytest
import json


def test_get_suppliers(client):
    """Test getting all suppliers."""
    response = client.get('/api/suppliers/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_suppliers_with_filter(client):
    """Test getting suppliers with filter."""
    response = client.get('/api/suppliers/?category=electronics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    for supplier in data:
        assert "electronics" in supplier["categories"]


def test_get_supplier(client, supplier_id):
    """Test getting a specific supplier."""
    response = client.get(f'/api/suppliers/{supplier_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == supplier_id


def test_get_supplier_not_found(client):
    """Test getting a non-existent supplier."""
    response = client.get('/api/suppliers/non-existent-id')
    assert response.status_code == 404


def test_search_suppliers(client):
    """Test searching suppliers."""
    search_criteria = {"max_price": 50.0, "min_sustainability": 70}
    response = client.post('/api/suppliers/search', json=search_criteria)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    for supplier in data:
        assert supplier["avg_price"] <= 50.0
        assert supplier["sustainability_score"] >= 70


def test_recommend_suppliers(client):
    """Test getting recommended suppliers."""
    response = client.get('/api/suppliers/recommend?category=electronics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    # Check if we have results and they're in descending order by rating
    if len(data) > 1:
        assert data[0]["rating"] >= data[1]["rating"]
