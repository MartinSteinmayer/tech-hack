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
