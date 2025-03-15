# tests/conftest.py
import pytest
import sys
import os
import json
from flask import Flask

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app
from api.mock_data import suppliers_data, compliance_data, orders_data


@pytest.fixture
def app():
    """Create a Flask app instance for testing."""
    app = flask_app
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def supplier_id():
    """Return a valid supplier ID for testing."""
    return suppliers_data[0]["id"]


@pytest.fixture
def order_id():
    """Return a valid order ID for testing."""
    return orders_data[0]["id"]


@pytest.fixture
def sample_supplier():
    """Return a sample supplier for testing."""
    return {
        "name": "TestSupplier",
        "description": "A supplier for testing",
        "categories": ["test", "sample"],
        "rating": 4.5,
        "avg_price": 25.0,
        "sustainability_score": 80,
        "locations": ["Test Location"]
    }


@pytest.fixture
def sample_order():
    """Return a sample order for testing."""
    return {
        "supplier_id": suppliers_data[0]["id"],
        "products": [{
            "id": "test-1",
            "name": "Test Product",
            "quantity": 10,
            "price": 15.0
        }]
    }


# tests/test_suppliers.py
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


# tests/test_negotiations.py
import pytest
import json


def test_generate_dossier(client, supplier_id):
    """Test generating a negotiation dossier."""
    data = {"supplier_id": supplier_id}
    response = client.post('/api/negotiations/generate-dossier', json=data)
    assert response.status_code == 200
    dossier = json.loads(response.data)
    assert "supplier_name" in dossier
    assert "suggested_strategies" in dossier
    assert "pricing_insights" in dossier


def test_generate_dossier_invalid_supplier(client):
    """Test generating a dossier for an invalid supplier."""
    data = {"supplier_id": "non-existent-id"}
    response = client.post('/api/negotiations/generate-dossier', json=data)
    assert response.status_code == 404


def test_get_strategies(client, supplier_id):
    """Test getting negotiation strategies."""
    response = client.get(f'/api/negotiations/strategies?supplier_id={supplier_id}&category=electronics')
    assert response.status_code == 200
    strategies = json.loads(response.data)
    assert isinstance(strategies, list)
    assert len(strategies) > 0
    for strategy in strategies:
        assert "name" in strategy
        assert "description" in strategy
        assert "suggested_approach" in strategy


def test_draft_message(client, supplier_id):
    """Test drafting a message to a supplier."""
    data = {"supplier_id": supplier_id, "type": "inquiry"}
    response = client.post('/api/negotiations/messages', json=data)
    assert response.status_code == 200
    message = json.loads(response.data)
    assert "subject" in message
    assert "body" in message
    assert "key_points" in message


def test_draft_message_invalid_supplier(client):
    """Test drafting a message to an invalid supplier."""
    data = {"supplier_id": "non-existent-id", "type": "inquiry"}
    response = client.post('/api/negotiations/messages', json=data)
    assert response.status_code == 404


# tests/test_compliance.py
import pytest
import json


def test_analyze_document(client):
    """Test analyzing a document for compliance."""
    data = {"document_type": "contract", "industry": "manufacturing"}
    response = client.post('/api/compliance/analyze-document', json=data)
    assert response.status_code == 200
    analysis = json.loads(response.data)
    assert "document_type" in analysis
    assert "identified_clauses" in analysis
    assert "compliance_concerns" in analysis
    assert "suggested_actions" in analysis


def test_get_requirements(client):
    """Test getting compliance requirements."""
    response = client.get('/api/compliance/requirements?industry=manufacturing&region=EU')
    assert response.status_code == 200
    requirements = json.loads(response.data)
    assert isinstance(requirements, list)

    # Check if filtered correctly
    for req in requirements:
        assert req["industry"] == "manufacturing" or req["industry"] == "all"
        assert "EU" in req["regions"] or "global" in req["regions"]


def test_verify_compliance(client, supplier_id):
    """Test verifying compliance status."""
    data = {"supplier_id": supplier_id}
    response = client.post('/api/compliance/verify', json=data)
    assert response.status_code == 200
    verification = json.loads(response.data)
    assert "status" in verification
    assert "compliant_areas" in verification
    assert "non_compliant_areas" in verification
    assert "risk_score" in verification
    assert "recommended_actions" in verification


# tests/test_orders.py
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


# tests/test_integration.py
import pytest
import json


def test_supplier_to_order_flow(client, supplier_id):
    """Test the complete flow from supplier discovery to order creation."""
    # 1. Get supplier details
    response = client.get(f'/api/suppliers/{supplier_id}')
    assert response.status_code == 200
    supplier = json.loads(response.data)

    # 2. Generate negotiation dossier
    response = client.post('/api/negotiations/generate-dossier', json={"supplier_id": supplier_id})
    assert response.status_code == 200

    # 3. Get negotiation strategies
    response = client.get(
        f'/api/negotiations/strategies?supplier_id={supplier_id}&category={supplier["categories"][0]}')
    assert response.status_code == 200

    # 4. Draft negotiation message
    response = client.post('/api/negotiations/messages', json={"supplier_id": supplier_id, "type": "negotiation"})
    assert response.status_code == 200

    # 5. Check compliance requirements
    response = client.get(f'/api/compliance/requirements?industry={supplier["categories"][0]}')
    assert response.status_code == 200

    # 6. Create order
    order_data = {
        "supplier_id": supplier_id,
        "products": [{
            "id": "prod-test",
            "name": "Test Product",
            "quantity": 10,
            "price": 100.0
        }]
    }
    response = client.post('/api/orders/', json=order_data)
    assert response.status_code == 201
    order = json.loads(response.data)

    # 7. Update order status
    response = client.put(f'/api/orders/{order["id"]}/status', json={"status": "submitted"})
    assert response.status_code == 200
    updated_order = json.loads(response.data)
    assert updated_order["status"] == "submitted"
