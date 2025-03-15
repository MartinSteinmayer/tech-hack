import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask

# Import our API modules
from api.suppliers import suppliers_bp, get_suppliers, search_suppliers, recommend_suppliers
from api.negotiations import negotiations_bp, generate_dossier, get_strategies
from api.compliance import compliance_bp, analyze_document, verify_compliance
from api.orders import orders_bp, create_order, update_order_status

# Import our client classes (use try/except to handle case where they're not yet created)
try:
    from utils.mistral_client import MistralAIClient
except ImportError:
    MistralAIClient = MagicMock

try:
    from utils.weaviate_client import SupplierKnowledgeGraph
except ImportError:
    SupplierKnowledgeGraph = MagicMock


@pytest.fixture
def app_with_mocks():
    """Create an app with all external clients mocked."""
    app = Flask(__name__)
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(negotiations_bp, url_prefix='/api/negotiations')
    app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.config['TESTING'] = True

    # Set up patches
    with patch('utils.mistral_client.MistralAIClient') as mock_mistral:
        with patch('utils.weaviate_client.SupplierKnowledgeGraph') as mock_weaviate:
            # Configure mock responses
            mock_mistral_instance = MagicMock()
            mock_mistral.return_value = mock_mistral_instance
            mock_mistral_instance.generate_text.return_value = {"text": "Mock response"}
            mock_mistral_instance.analyze_supplier.return_value = {"text": "Supplier analysis"}
            mock_mistral_instance.generate_negotiation_strategy.return_value = {"text": "Strategy"}
            mock_mistral_instance.analyze_compliance_document.return_value = {"text": "Compliance analysis"}

            mock_weaviate_instance = MagicMock()
            mock_weaviate.return_value = mock_weaviate_instance
            mock_weaviate_instance.search_suppliers.return_value = [{"name": "Mock Supplier"}]
            mock_weaviate_instance.get_supplier_recommendations.return_value = [{"name": "Recommended Supplier"}]

            yield app


def test_integrated_supplier_search(app_with_mocks):
    """Test the integrated supplier search endpoint with Weaviate mocked."""
    client = app_with_mocks.test_client()

    # Call the endpoint
    response = client.post('/api/suppliers/search',
                           json={
                               "query": "quality electronics",
                               "categories": ["electronics"],
                               "min_rating": 4.0,
                               "min_sustainability": 75
                           })

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_integrated_negotiation_strategy(app_with_mocks):
    """Test the integrated negotiation strategy endpoint with Mistral AI mocked."""
    client = app_with_mocks.test_client()

    # Call the endpoint
    response = client.get('/api/negotiations/strategies?supplier_id=sup-001&category=electronics&goal=price_reduction')

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_integrated_compliance_analysis(app_with_mocks):
    """Test the integrated compliance analysis endpoint with Mistral AI mocked."""
    client = app_with_mocks.test_client()

    # Call the endpoint
    response = client.post('/api/compliance/analyze-document',
                           json={
                               "document_type": "contract",
                               "industry": "manufacturing",
                               "region": "EU",
                               "content": "This is a sample contract document for testing."
                           })

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "document_type" in data


def test_integrated_order_creation(app_with_mocks):
    """Test the integrated order creation endpoint."""
    client = app_with_mocks.test_client()

    # Call the endpoint
    response = client.post('/api/orders/',
                           json={
                               "supplier_id": "sup-001",
                               "products": [{
                                   "id": "prod-001",
                                   "name": "Test Product",
                                   "quantity": 10,
                                   "price": 100.0
                               }]
                           })

    # Check response
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "id" in data
    assert data["status"] == "draft"


def test_complete_api_flow(app_with_mocks):
    """Test a complete API flow from supplier search to order creation."""
    client = app_with_mocks.test_client()

    # 1. Search for suppliers
    response = client.post('/api/suppliers/search', json={"query": "quality electronics"})
    assert response.status_code == 200
    suppliers = json.loads(response.data)

    # Skip if no suppliers found (shouldn't happen with our mocks)
    if not suppliers:
        pytest.skip("No suppliers found")

    supplier_id = "sup-001"  # Use a known ID from our mock data

    # 2. Get supplier recommendations
    response = client.get('/api/suppliers/recommend?category=electronics')
    assert response.status_code == 200

    # 3. Generate negotiation dossier
    response = client.post('/api/negotiations/generate-dossier', json={"supplier_id": supplier_id})
    assert response.status_code == 200

    # 4. Get negotiation strategies
    response = client.get(f'/api/negotiations/strategies?supplier_id={supplier_id}&category=electronics')
    assert response.status_code == 200

    # 5. Draft negotiation message
    response = client.post('/api/negotiations/messages', json={"supplier_id": supplier_id, "type": "negotiation"})
    assert response.status_code == 200

    # 6. Verify compliance
    response = client.post('/api/compliance/verify', json={"supplier_id": supplier_id})
    assert response.status_code == 200

    # 7. Create order
    response = client.post('/api/orders/',
                           json={
                               "supplier_id": supplier_id,
                               "products": [{
                                   "id": "prod-test",
                                   "name": "Test Product",
                                   "quantity": 10,
                                   "price": 100.0
                               }]
                           })
    assert response.status_code == 201
    order = json.loads(response.data)

    # 8. Update order status
    response = client.put(f'/api/orders/{order["id"]}/status', json={"status": "submitted"})
    assert response.status_code == 200
    updated_order = json.loads(response.data)
    assert updated_order["status"] == "submitted"
