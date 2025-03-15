from flask import Blueprint, request, jsonify
from .mock_data import suppliers_data

suppliers_bp = Blueprint('suppliers', __name__)


@suppliers_bp.route('/', methods=['GET'])
def get_suppliers():
    """Get all suppliers with optional filtering"""
    # Get query parameters for filtering
    category = request.args.get('category')
    min_rating = request.args.get('min_rating')

    filtered_suppliers = suppliers_data

    # Apply filters if provided
    if category:
        filtered_suppliers = [s for s in filtered_suppliers if category in s['categories']]
    if min_rating:
        filtered_suppliers = [s for s in filtered_suppliers if s['rating'] >= float(min_rating)]

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
    """Get recommended suppliers based on parameters"""
    # This would later use the knowledge graph to make intelligent recommendations
    # For now, just return the highest rated suppliers
    product_category = request.args.get('category', '')

    recommended = [s for s in suppliers_data if product_category in s.get('categories', [])]
    recommended.sort(key=lambda x: x.get('rating', 0), reverse=True)

    return jsonify(recommended[:5])  # Return top 5
