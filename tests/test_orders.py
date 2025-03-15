import pytest
import json


def test_create_order(client, sample_order):
    """Test creating a new order."""
    response = client.post('/api/orders/', json=sample_order)
    assert response.status_code == 201
    order = json.loads(response.data)
    assert "id" in order
    assert order["supplier_id"] == sample_order["supplier_id"]
    assert order["status"] == "draft"
    assert len(order["products"]) == len(sample_order["products"])


def test_create_order_invalid_supplier(client):
    """Test creating an order with an invalid supplier."""
    data = {
        "supplier_id": "non-existent-id",
        "products": [{
            "id": "test-1",
            "name": "Test Product",
            "quantity": 10,
            "price": 15.0
        }]
    }
    response = client.post('/api/orders/', json=data)
    assert response.status_code == 404


def test_get_order(client, order_id):
    """Test getting an order."""
    response = client.get(f'/api/orders/{order_id}')
    assert response.status_code == 200
    order = json.loads(response.data)
    assert order["id"] == order_id


def test_get_order_not_found(client):
    """Test getting a non-existent order."""
    response = client.get('/api/orders/non-existent-id')
    assert response.status_code == 404


def test_update_order_status(client, order_id):
    """Test updating an order status."""
    data = {"status": "submitted"}
    response = client.put(f'/api/orders/{order_id}/status', json=data)
    assert response.status_code == 200
    order = json.loads(response.data)
    assert order["id"] == order_id
    assert order["status"] == "submitted"


def test_update_order_status_invalid_status(client, order_id):
    """Test updating an order with an invalid status."""
    data = {"status": "invalid-status"}
    response = client.put(f'/api/orders/{order_id}/status', json=data)
    assert response.status_code == 400


def test_update_order_status_not_found(client):
    """Test updating a non-existent order."""
    data = {"status": "submitted"}
    response = client.put('/api/orders/non-existent-id/status', json=data)
    assert response.status_code == 404
