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
