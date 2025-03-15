from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime, timedelta
from .mock_data import orders_data, suppliers_data

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/', methods=['POST'])
def create_order():
    """Create a new order draft"""
    data = request.json
    supplier_id = data.get('supplier_id')
    products = data.get('products', [])

    # Find supplier
    supplier = next((s for s in suppliers_data if s['id'] == supplier_id), None)
    if not supplier:
        return jsonify({"error": "Supplier not found"}), 404

    # Generate mock order
    # In real implementation, this would be more sophisticated and use Mistral AI
    order_id = str(uuid.uuid4())

    order = {
        "id": order_id,
        "supplier_id": supplier_id,
        "supplier_name": supplier['name'],
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "products": products,
        "estimated_delivery": (datetime.now() + timedelta(days=14)).isoformat(),
        "total_amount": sum(p.get('price', 0) * p.get('quantity', 0) for p in products),
        "payment_terms": "Net 30",
        "notes": "Automatically generated order draft"
    }

    # In a real app, this would be saved to a database
    orders_data.append(order)

    return jsonify(order), 201


@orders_bp.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get details about a specific order"""
    order = next((o for o in orders_data if o['id'] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404


@orders_bp.route('/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    data = request.json
    new_status = data.get('status')

    order = next((o for o in orders_data if o['id'] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    valid_statuses = ["draft", "submitted", "confirmed", "shipped", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400

    # Update status
    order['status'] = new_status
    order['updated_at'] = datetime.now().isoformat()

    # In a real app, this would update a database

    return jsonify(order)
