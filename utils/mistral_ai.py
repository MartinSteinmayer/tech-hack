import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class MistralAIClient:
    """Simple client for interacting with Mistral AI API"""

    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.api_url = "https://api.mistral.ai/v1"

        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")

    def generate_text(self, prompt, max_tokens=500, temperature=0.7):
        """Generate text using Mistral AI"""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        data = {
            "model": "mistral-large-latest",  # or whatever model you're using
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = requests.post(f"{self.api_url}/generate", headers=headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Error from Mistral AI API: {response.text}")

        return response.json()

    def analyze_supplier(self, supplier_data):
        """Analyze supplier information and provide insights"""
        prompt = f"""
        Analyze the following supplier information and provide insights:
        
        Supplier Name: {supplier_data.get('name')}
        Description: {supplier_data.get('description')}
        Categories: {', '.join(supplier_data.get('categories', []))}
        Rating: {supplier_data.get('rating')}
        Average Price: ${supplier_data.get('avg_price')}
        Sustainability Score: {supplier_data.get('sustainability_score')}/100
        
        Please provide:
        1. Key strengths of this supplier
        2. Potential concerns or weaknesses
        3. Negotiation leverage points
        4. Recommended approach for engagement
        """

        response = self.generate_text(prompt)
        return response

    def generate_negotiation_strategy(self, supplier_data, product_category, negotiation_goal):
        """Generate negotiation strategies based on supplier and goals"""
        prompt = f"""
        Generate effective negotiation strategies for the following scenario:
        
        Supplier: {supplier_data.get('name')}
        Product Category: {product_category}
        Negotiation Goal: {negotiation_goal}
        
        Supplier Details:
        - Rating: {supplier_data.get('rating')}/5
        - Average Price: ${supplier_data.get('avg_price')}
        - Sustainability Score: {supplier_data.get('sustainability_score')}/100
        
        Please provide:
        1. 3 specific negotiation strategies that would be effective
        2. Key talking points for each strategy
        3. Potential concessions we could offer
        4. Recommended pricing targets (% discount to aim for)
        """

        response = self.generate_text(prompt)
        return response

    def analyze_compliance_document(self, document_text, industry, region):
        """Analyze document for compliance issues"""
        prompt = f"""
        Analyze the following document for compliance with regulations in the {industry} industry for the {region} region.
        
        Document Content:
        {document_text[:2000]}  # Limit to first 2000 chars for API constraints
        
        Please identify:
        1. Any potential compliance issues or red flags
        2. Missing clauses or sections required by regulations
        3. Recommended changes to ensure compliance
        4. Overall compliance risk assessment (low, medium, high)
        """

        response = self.generate_text(prompt, max_tokens=800)
        return response

    def draft_order_communication(self, order_data, supplier_data, communication_type):
        """Draft communications for orders"""
        prompt = f"""
        Draft a professional {communication_type} communication regarding the following order:
        
        Order ID: {order_data.get('id')}
        Supplier: {supplier_data.get('name')}
        Products: {', '.join([p.get('name') for p in order_data.get('products', [])])}
        Total Amount: ${order_data.get('total_amount')}
        Current Status: {order_data.get('status')}
        
        The communication should be professional, clear, and include all relevant order details.
        """

        response = self.generate_text(prompt)
        return response
