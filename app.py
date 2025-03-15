from flask import Flask
from flask_cors import CORS

from api.suppliers import suppliers_bp
from api.negotiations import negotiations_bp
from api.compliance import compliance_bp
from api.orders import orders_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
app.register_blueprint(negotiations_bp, url_prefix='/api/negotiations')
app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
app.register_blueprint(orders_bp, url_prefix='/api/orders')


@app.route('/')
def home():
    return {
        "name": "Tacto API",
        "version": "1.0.0",
        "modules": ["Supplier Discovery", "Negotiation Companion", "Compliance Guardian", "Order Agent"]
    }


if __name__ == '__main__':
    app.run(debug=True)
