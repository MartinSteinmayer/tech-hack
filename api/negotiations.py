from flask import Blueprint, request, jsonify
from .mock_data import negotiations_data, suppliers_data
from dotenv import load_dotenv
import os
from mistralai import Mistral
import json

negotiations_bp = Blueprint('negotiations', __name__)

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-large-latest"

client = Mistral(api_key=api_key)


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


def load_mock_data(json_file_path='mock_data.json'):
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading mock data: {e}")
        return {"suppliers": [], "orders": [], "negotiations": [], "compliance": []}


# Get supplier by name
def get_supplier_by_name(suppliers, name):
    return next((s for s in suppliers if s["name"] == name), None)


# Get supplier by ID
def get_supplier_by_id(suppliers, supplier_id):
    return next((s for s in suppliers if s["id"] == supplier_id), None)


@negotiations_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """Get pricing strategies based on supplier and product"""
    supplier_name = request.args.get('supplier')
    product_category = request.args.get('category')
    description = request.args.get('description')

    # Load the mock data
    mock_data = load_mock_data()

    # Find supplier information from mock data
    supplier = get_supplier_by_name(mock_data.get('suppliers', []), supplier_name)

    # Gather historical negotiation data if available
    negotiation_history = []
    if supplier:
        negotiation_history = supplier.get("negotiationHistory", [])

    # Get supplier performance metrics to inform strategies
    performance_metrics = {}
    if supplier:
        performance_metrics = {
            "rating": supplier.get("rating"),
            "qualityScore": supplier.get("qualityScore"),
            "deliveryScore": supplier.get("deliveryScore"),
            "reliabilityScore": supplier.get("reliabilityScore"),
            "currentPricing": supplier.get("currentPricing"),
            "profitMargin": supplier.get("profitMargin"),
            "averageDiscount": supplier.get("averageDiscount")
        }

    # Get past negotiations with this supplier
    past_strategies = []
    for negotiation in mock_data.get('negotiations', []):
        if negotiation.get("supplierName") == supplier_name:
            past_strategies.append({
                "targetSavings": negotiation.get("targetSavings"),
                "status": negotiation.get("status"),
                "currentStage": negotiation.get("currentStage"),
                "outcome": negotiation.get("outcome", "In progress"),
                "actualSavings": negotiation.get("actualSavings", 0)
            })

    # Use Mistral AI to generate strategies based on our mock data
    prompt_context = {
        "supplier": supplier,
        "performance_metrics": performance_metrics,
        "negotiation_history": negotiation_history,
        "past_strategies": past_strategies,
        "product_category": product_category,
        "description": description
    }

    messages = [{
        "role":
            "user",
        "content":
            f"""You are a pricing strategist analyzing negotiation strategies. Generate pricing strategies for the following scenario:
            
            Supplier: {supplier_name}
            Product Category: {product_category}
            Description: {description}
            
            Supplier Information: {prompt_context}
            
            Based on this data, provide three detailed negotiation strategies tailored to this specific supplier and product category.
            Return as a JSON array of strategy objects with the following structure:
            [
                {{
                    "name": "Strategy Name",
                    "description": "Brief description of the strategy",
                    "suggested_approach": "Specific tactics and approaches based on the supplier data",
                    "expected_savings": "Estimated percentage savings based on historical data",
                    "confidence": "High/Medium/Low based on available data quality"
                }}
            ]
            """,
    }]

    try:
        chat_response = client.chat.complete(model=model, messages=messages, response_format={
            "type": "json_object",
        })
        strategies = chat_response.choices[0].message.content
        return jsonify(strategies)
    except Exception as e:
        # Fallback strategies based on supplier data if Mistral API fails
        fallback_strategies = generate_fallback_strategies(supplier, product_category)
        return jsonify(fallback_strategies)


def generate_fallback_strategies(supplier, product_category):
    """Generate fallback strategies based on supplier data if API call fails"""
    strategies = []

    if not supplier:
        return default_strategies()

    # Strategy 1: Based on historical discount
    avg_discount = supplier.get("averageDiscount", 5)
    strategies.append({
        "name": "Historical Discount Enhancement",
        "description": f"Leverage past discount of {avg_discount}% to negotiate better terms",
        "suggested_approach": f"Request {avg_discount + 2}% discount based on consistent order history",
        "expected_savings": f"{avg_discount + 2}%",
        "confidence": "High"
    })

    # Strategy 2: Based on contract timing
    contract_expiry = supplier.get("contractExpiry", "Unknown")
    if contract_expiry != "Unknown":
        strategies.append({
            "name":
                "Contract Renewal Leverage",
            "description":
                "Use upcoming contract renewal as negotiating leverage",
            "suggested_approach":
                f"Propose early renewal before {contract_expiry} with better terms for longer commitment",
            "expected_savings":
                "5-8%",
            "confidence":
                "Medium"
        })

    # Strategy 3: Based on supplier performance metrics and product category
    quality_score = supplier.get("qualityScore", 85)
    reliability_score = supplier.get("reliabilityScore", 85)

    if product_category and product_category.lower() in ["electronics", "raw materials"]:
        strategies.append({
            "name":
                "Quality-Price Trade-off",
            "description":
                "Leverage quality metrics for better pricing",
            "suggested_approach":
                f"Highlight quality requirements for {product_category} and propose tiered pricing based on consistent quality above {quality_score}%",
            "expected_savings":
                "4-7%",
            "confidence":
                "Medium"
        })
    else:
        strategies.append({
            "name":
                "Reliability Premium Reduction",
            "description":
                "Negotiate reliability-based pricing",
            "suggested_approach":
                f"Propose standard pricing with reliability incentives (current reliability: {reliability_score}%)",
            "expected_savings":
                "3-6%",
            "confidence":
                "Medium"
        })

    return strategies


def default_strategies():
    """Return default strategies when no supplier data is available"""
    return [{
        "name": "Volume Discount",
        "description": "Negotiate price reductions based on purchase volume",
        "suggested_approach": "Propose 5-10% discount for orders over $10,000",
        "expected_savings": "5-10%",
        "confidence": "Medium"
    }, {
        "name": "Early Payment Terms",
        "description": "Offer faster payment for price reduction",
        "suggested_approach": "Propose 2-3% discount for payment within 10 days",
        "expected_savings": "2-3%",
        "confidence": "High"
    }, {
        "name": "Long-term Contract",
        "description": "Secure better pricing with multi-year commitment",
        "suggested_approach": "Propose 7-12% discount for 2-year supply agreement",
        "expected_savings": "7-12%",
        "confidence": "Medium"
    }]


@negotiations_bp.route('/messages', methods=['POST'])
def draft_message():
    """Draft a communication message to a supplier"""
    data = request.json
    message_type = data.get('type', 'inquiry')
    supplier_name = data.get('supplier')

    # This would use Mistral AI to generate actual messages
    message_templates = {
        "inquiry":
            f"Dear {supplier_name},\n\nWe are interested in your products and would like to request more information about your pricing and availability for our upcoming projects.\n\nBest regards,\nTacto Team",
        "negotiation":
            f"Dear {supplier_name},\n\nThank you for your quote. We would like to discuss the possibility of a volume discount based on our projected annual needs.\n\nBest regards,\nTacto Team",
        "followup":
            f"Dear {supplier_name},\n\nI'm following up on our previous conversation regarding pricing. Have you had a chance to review our proposal?\n\nBest regards,\nTacto Team"
    }

    return jsonify({
        "subject": f"Re: {message_type.capitalize()} with {supplier_name}",
        "body": message_templates.get(message_type, message_templates['inquiry']),
        "suggested_tone": "Professional and direct",
        "key_points": ["Reference previous communication", "Be specific about needs", "Include timeline expectations"]
    })
