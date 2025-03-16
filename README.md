# Tacto API

Tacto API is a comprehensive procurement and supplier management platform that leverages AI to streamline supplier discovery, negotiations, compliance verification, and order management.

## Features

The API is organized into four main modules:

1. **Supplier Discovery** - Find and evaluate potential suppliers based on various criteria.
2. **Negotiation Companion** - Generate negotiation strategies, supplier dossiers, and communication drafts.
3. **Compliance Guardian** - Analyze documents for compliance issues and verify supplier compliance status.
4. **Order Agent** - Create and manage orders with suppliers.

## Technical Stack

- **Backend**: Flask (Python)
- **AI Integration**: Mistral AI Large Language Models
- **Knowledge Graph**: Weaviate (for semantic search and supplier relationship mapping)
- **Document Processing**: PyMuPDF (for PDF analysis)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Mistral AI API key
- Weaviate instance (optional, for advanced supplier search)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tacto-api.git
   cd tacto-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   MISTRAL_API_KEY=your_mistral_api_key
   WEAVIATE_URL=your_weaviate_url  # Optional
   WEAVIATE_API_KEY=your_weaviate_api_key  # Optional
   ```

5. Run the development server:
   ```bash
   python app.py
   ```

## API Endpoints

### Supplier Discovery

- `GET /api/suppliers/` - Get all suppliers with optional filtering
- `GET /api/suppliers/<supplier_id>` - Get detailed information about a specific supplier
- `POST /api/suppliers/search` - Search suppliers based on specific criteria
- `GET /api/suppliers/recommend` - Get recommended suppliers based on parameters

### Negotiation Companion

- `POST /api/negotiations/generate-dossier` - Generate a negotiation dossier for a specific supplier
- `GET /api/negotiations/strategies` - Get pricing strategies based on supplier and product
- `POST /api/negotiations/messages` - Draft a communication message to a supplier

### Compliance Guardian

- `POST /api/compliance/analyze-document` - Analyze a document for compliance issues
- `POST /api/compliance/requirements` - Get compliance requirements based on user input
- `POST /api/compliance/verify` - Verify compliance status for a supplier or document

### Order Agent

- `POST /api/orders/` - Create a new order draft
- `GET /api/orders/<order_id>` - Get details about a specific order
- `PUT /api/orders/<order_id>/status` - Update order status

## Example Usage

### Searching for Suppliers

```python
import requests
import json

url = "http://localhost:5000/api/suppliers/search"
payload = {
    "max_price": 50.0,
    "min_sustainability": 70,
    "location": "Germany"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
suppliers = response.json()
print(json.dumps(suppliers, indent=2))
```

### Generating Negotiation Strategies

```python
import requests

url = "http://localhost:5000/api/negotiations/strategies"
params = {
    "supplier": "ElectroTech Industries",
    "category": "Electronics",
    "description": "Need high-quality microcontrollers for our new product line"
}

response = requests.get(url, params=params)
strategies = response.json()
print(json.dumps(strategies, indent=2))
```

### Analyzing a Document for Compliance

```python
import requests
import json

url = "http://localhost:5000/api/compliance/analyze-document"
files = {"file": open("contract.pdf", "rb")}

response = requests.post(url, files=files)
analysis = response.json()
print(json.dumps(analysis, indent=2))
```

## Testing

Run the test suite with:

```bash
pytest
```

The tests cover API functionality, integration with AI services, and end-to-end workflows.

## Deployment

The API is configured for deployment on Vercel using the provided `vercel.json` configuration.

To deploy to Vercel:

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```bash
   vercel login
   ```

3. Deploy the project:
   ```bash
   vercel
   ```

Make sure to set up the required environment variables in your Vercel project settings.

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request
