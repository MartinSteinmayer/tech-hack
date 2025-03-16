from flask import Blueprint, request, jsonify
from .mock_data import suppliers_data
from dotenv import load_dotenv
import os
from mistralai import Mistral
import json

# Create a Blueprint for the suppliers API
suppliers_bp = Blueprint('suppliers', __name__)


# Import possible_suppliers_data from the mock_data file
def load_mock_data(json_file_path='api/mock_data.json'):
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading mock data: {e}")
        return {"suppliers": [], "possible_suppliers_data": []}


# Load the mock data once at module level
mock_data = load_mock_data()
possible_suppliers_data = mock_data.get('possible_suppliers_data', [])


@suppliers_bp.route('/', methods=['GET'])
def get_suppliers():
    """Get all suppliers with optional filtering"""
    # Get query parameters for filtering
    category = request.args.get('category')
    min_rating = request.args.get('min_rating')

    filtered_suppliers = suppliers_data

    # Apply filters if provided
    if category:
        filtered_suppliers = [s for s in filtered_suppliers if category in s.get('categories', [])]
    if min_rating:
        filtered_suppliers = [s for s in filtered_suppliers if s.get('rating', 0) >= float(min_rating)]

    return jsonify(filtered_suppliers)


@suppliers_bp.route('/<supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """Get detailed information about a specific supplier"""
    supplier = next((s for s in suppliers_data if s['id'] == supplier_id), None)
    if supplier:
        return jsonify(supplier)
    return jsonify({"error": "Supplier not found"}), 404


@suppliers_bp.route('/search', methods=['POST'])
def search_suppliers():
    """Search suppliers based on specific criteria"""
    criteria = request.json

    # This would be replaced with actual semantic search using Weaviate
    # For now, just use basic filtering
    results = suppliers_data

    # Filter by price if specified
    if 'max_price' in criteria:
        results = [s for s in results if s.get('avg_price', float('inf')) <= criteria['max_price']]

    # Filter by sustainability score if specified
    if 'min_sustainability' in criteria:
        results = [s for s in results if s.get('sustainability_score', 0) >= criteria['min_sustainability']]

    # Filter by location if specified
    if 'location' in criteria:
        results = [s for s in results if criteria['location'] in s.get('locations', [])]

    # Later, this would use Mistral AI to rank based on semantic similarity
    return jsonify(results)


@suppliers_bp.route('/recommend', methods=['GET'])
def recommend_suppliers():
    """Get recommended suppliers based on parameters using Mistral AI"""
    # Get query parameters
    product_category = request.args.get('category', '')

    # Initialize Mistral client
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)

    # Reload the mock data to ensure we have the latest possible_suppliers_data
    global possible_suppliers_data
    mock_data = load_mock_data()
    possible_suppliers_data = mock_data.get('possible_suppliers_data', [])

    # Filter suppliers by category (if provided)
    if product_category:
        filtered_suppliers = [
            s for s in possible_suppliers_data if product_category.lower() in s.get('category', '').lower()
        ]
    else:
        filtered_suppliers = possible_suppliers_data

    # Function to call Mistral AI
    def ai_call(prompt):
        messages = [{"role": "user", "content": f"{prompt}"}]
        chat_response = client.chat.complete(model=model, messages=messages, response_format={
            "type": "json_object",
        })
        return chat_response.choices[0].message.content

    # Prepare the prompt for Mistral AI
    prompt = f"""You are a procurement specialist AI. I need you to analyze the following list of suppliers and recommend the best one for our needs.
    
    Category: {product_category if product_category else "Any/All Categories"}
    
    Supplier Data:
    {json.dumps(filtered_suppliers, indent=2)}
    
    Please analyze these suppliers and recommend the SINGLE best one based on:
    1. Overall rating and quality scores
    2. Reliability and delivery performance
    3. Risk factors and compliance status
    4. Previous negotiation outcomes and discounts
    5. Financial health indicators like profit margins
    
    Return your response as a JSON object with the following structure:
    {{
        "recommended_supplier": {{
            // Full supplier object here
        }},
        "reasons": ["Reason 1", "Reason 2", ...],
        "considerations": "Any other considerations or notes about this supplier"
    }}
    """

    try:
        # Get the recommendation from Mistral AI
        recommendation = ai_call(prompt)
        return recommendation
    except Exception as e:
        # Fallback if Mistral AI fails
        print(f"Error getting recommendation from Mistral AI: {e}")

        # Sort by rating as a fallback
        filtered_suppliers.sort(key=lambda x: x.get('rating', 0), reverse=True)
        best_supplier = filtered_suppliers[0] if filtered_suppliers else {}

        fallback_response = {
            "recommended_supplier": best_supplier,
            "reasons": ["Highest overall rating among available suppliers"],
            "considerations": "This recommendation is based solely on the supplier's rating as a fallback mechanism."
        }

        return jsonify(fallback_response)
