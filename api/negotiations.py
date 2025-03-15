from flask import Blueprint, request, jsonify
from .mock_data import negotiations_data, suppliers_data

negotiations_bp = Blueprint('negotiations', __name__)


@negotiations_bp.route('/generate-dossier', methods=['POST'])
def generate_dossier():
    """Generate a negotiation dossier for a specific supplier"""
    data = request.json
    supplier_id = data.get('supplier_id')

    # Find supplier
    supplier = next((s for s in suppliers_data if s['id'] == supplier_id), None)
    if not supplier:
        return jsonify({"error": "Supplier not found"}), 404

    # Generate mock dossier
    # In real implementation, this would use Mistral AI
    dossier = {
        "supplier_name": supplier['name'],
        "key_contacts": supplier.get('contacts', []),
        "previous_negotiations": [],
        "suggested_strategies": [
            "Focus on volume discounts", "Highlight long-term partnership benefits", "Negotiate payment terms extension"
        ],
        "pricing_insights": {
            "current_pricing": supplier.get('avg_price', 0),
            "market_average": supplier.get('avg_price', 0) * 0.95,
            "suggested_target": supplier.get('avg_price', 0) * 0.9
        }
    }

    return jsonify(dossier)


@negotiations_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """Get pricing strategies based on supplier and product"""
    supplier_name = request.args.get('supplier')
    product_category = request.args.get('category')
    description = request.args.get('description')

    # This would later use Mistral AI to generate custom strategies
    strategies = [{
        "name": "Volume Discount",
        "description": "Negotiate price reductions based on purchase volume",
        "suggested_approach": "Propose 5-10% discount for orders over $10,000"
    }, {
        "name": "Early Payment Terms",
        "description": "Offer faster payment for price reduction",
        "suggested_approach": "Propose 2-3% discount for payment within 10 days"
    }, {
        "name": "Long-term Contract",
        "description": "Secure better pricing with multi-year commitment",
        "suggested_approach": "Propose 7-12% discount for 2-year supply agreement"
    }]

    return jsonify(strategies)


@negotiations_bp.route('/messages', methods=['POST'])
def draft_message():
    """Draft a communication message to a supplier"""
    data = request.json
    message_type = data.get('type', 'inquiry')
    supplier_id = data.get('supplier_id')

    # Find supplier
    supplier = next((s for s in suppliers_data if s['id'] == supplier_id), None)
    if not supplier:
        return jsonify({"error": "Supplier not found"}), 404

    # This would use Mistral AI to generate actual messages
    message_templates = {
        "inquiry":
            f"Dear {supplier['name']},\n\nWe are interested in your products and would like to request more information about your pricing and availability for our upcoming projects.\n\nBest regards,\nTacto Team",
        "negotiation":
            f"Dear {supplier['name']},\n\nThank you for your quote. We would like to discuss the possibility of a volume discount based on our projected annual needs.\n\nBest regards,\nTacto Team",
        "followup":
            f"Dear {supplier['name']},\n\nI'm following up on our previous conversation regarding pricing. Have you had a chance to review our proposal?\n\nBest regards,\nTacto Team"
    }

    return jsonify({
        "subject": f"Re: {message_type.capitalize()} with {supplier['name']}",
        "body": message_templates.get(message_type, message_templates['inquiry']),
        "suggested_tone": "Professional and direct",
        "key_points": ["Reference previous communication", "Be specific about needs", "Include timeline expectations"]
    })
