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
