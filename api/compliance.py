from flask import Blueprint, request, jsonify
from .mock_data import compliance_data

compliance_bp = Blueprint('compliance', __name__)


@compliance_bp.route('/analyze-document', methods=['POST'])
def analyze_document():
    """Analyze a document for compliance requirements"""
    # In a real implementation, this would receive a file
    # For the hackathon, we'll mock this with JSON input
    data = request.json
    document_type = data.get('document_type', 'contract')
    industry = data.get('industry', 'manufacturing')

    # This would later use Mistral AI for document analysis
    analysis = {
        "document_type":
            document_type,
        "identified_clauses": ["liability", "termination", "confidentiality"],
        "compliance_concerns": [{
            "type": "Missing clause",
            "description": "No data protection clause identified",
            "severity": "high"
        }, {
            "type": "Unclear language",
            "description": "Termination conditions ambiguous",
            "severity": "medium"
        }],
        "suggested_actions": [
            "Add GDPR compliance clause", "Clarify termination conditions", "Add force majeure clause"
        ]
    }

    return jsonify(analysis)


@compliance_bp.route('/requirements', methods=['GET'])
def get_requirements():
    """Get compliance requirements for a specific industry/region"""
    industry = request.args.get('industry', 'all')
    region = request.args.get('region', 'global')

    # Filter mock requirements based on industry and region
    filtered_requirements = [
        r for r in compliance_data
        if (industry == 'all' or r['industry'] == industry) and (region == 'global' or region in r['regions'])
    ]

    return jsonify(filtered_requirements)


@compliance_bp.route('/verify', methods=['POST'])
def verify_compliance():
    """Verify compliance status for a supplier or document"""
    data = request.json
    supplier_id = data.get('supplier_id')
    document_id = data.get('document_id')

    # This would later connect to the knowledge graph to check actual compliance
    verification_result = {
        "status": "partially_compliant",
        "compliant_areas": ["Environmental regulations", "Labor practices"],
        "non_compliant_areas": ["Data protection requirements"],
        "risk_score": 65,  # 0-100, higher is riskier
        "recommended_actions": ["Request updated data protection policy", "Schedule compliance audit within 60 days"]
    }

    return jsonify(verification_result)
