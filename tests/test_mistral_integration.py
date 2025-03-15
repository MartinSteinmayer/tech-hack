import pytest
import json
import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MistralAIClient to test
try:
    from utils.mistral_client import MistralAIClient
except ImportError:
    # If not yet created, create a simple mock for testing
    class MistralAIClient:

        def __init__(self):
            pass

        def generate_text(self, prompt, max_tokens=500, temperature=0.7):
            return {"text": "Mock response from Mistral AI"}

        def analyze_supplier(self, supplier_data):
            return {"text": "Mock supplier analysis"}

        def generate_negotiation_strategy(self, supplier_data, product_category, negotiation_goal):
            return {"text": "Mock negotiation strategy"}

        def analyze_compliance_document(self, document_text, industry, region):
            return {"text": "Mock compliance analysis"}

        def draft_order_communication(self, order_data, supplier_data, communication_type):
            return {"text": "Mock order communication"}


# Import API modules for patching
from api.suppliers import suppliers_bp
from api.negotiations import negotiations_bp
from api.compliance import compliance_bp
from api.orders import orders_bp

# Sample data for testing
from api.mock_data import suppliers_data, compliance_data, orders_data


class TestMistralIntegration(unittest.TestCase):
    """Test the integration with Mistral AI."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MistralAIClient()

        # Sample data for tests
        self.supplier_data = suppliers_data[0]
        self.product_category = "electronics"
        self.negotiation_goal = "price reduction"
        self.document_text = "This is a sample contract document for testing."
        self.industry = "manufacturing"
        self.region = "EU"
        self.order_data = orders_data[0]
        self.communication_type = "confirmation"

    @patch('utils.mistral_client.MistralAIClient.generate_text')
    def test_analyze_supplier(self, mock_generate_text):
        """Test analyzing a supplier with Mistral AI."""
        # Set up the mock
        mock_generate_text.return_value = {
            "text":
                """
            Key strengths:
            1. High quality electronic components
            2. Reliable delivery record
            3. Competitive pricing
            
            Potential concerns:
            1. Limited product range
            2. Some sustainability issues
            
            Negotiation leverage points:
            1. Volume discounts
            2. Long-term contracts
            
            Recommended approach:
            Focus on building a strategic partnership
            """
        }

        # Call the method
        result = self.client.analyze_supplier(self.supplier_data)

        # Verify the mock was called with correct parameters
        mock_generate_text.assert_called_once()
        args, kwargs = mock_generate_text.call_args
        assert self.supplier_data.get('name') in kwargs.get('prompt', args[0])

        # Check result
        assert "Key strengths" in result.get("text", "")

    @patch('utils.mistral_client.MistralAIClient.generate_text')
    def test_generate_negotiation_strategy(self, mock_generate_text):
        """Test generating negotiation strategies with Mistral AI."""
        # Set up the mock
        mock_generate_text.return_value = {
            "text":
                """
            Negotiation strategies:
            
            1. Volume-based pricing strategy
               - Key points: Bulk purchase discounts, minimum order commitments
               - Concessions: Flexible delivery scheduling
               - Target discount: 5-8%
            
            2. Long-term contract strategy
               - Key points: Multi-year commitment, predictable ordering
               - Concessions: Earlier payment terms
               - Target discount: 10-15%
            
            3. Bundle purchasing strategy
               - Key points: Adding related products from same supplier
               - Concessions: Marketing partnership opportunities
               - Target discount: 7-12%
            """
        }

        # Call the method
        result = self.client.generate_negotiation_strategy(self.supplier_data, self.product_category,
                                                           self.negotiation_goal)

        # Verify the mock was called with correct parameters
        mock_generate_text.assert_called_once()
        args, kwargs = mock_generate_text.call_args
        assert self.supplier_data.get('name') in kwargs.get('prompt', args[0])
        assert self.product_category in kwargs.get('prompt', args[0])
        assert self.negotiation_goal in kwargs.get('prompt', args[0])

        # Check result
        assert "Negotiation strategies" in result.get("text", "")
        assert "Volume-based pricing strategy" in result.get("text", "")

    @patch('utils.mistral_client.MistralAIClient.generate_text')
    def test_analyze_compliance_document(self, mock_generate_text):
        """Test analyzing a document for compliance with Mistral AI."""
        # Set up the mock
        mock_generate_text.return_value = {
            "text":
                """
            Compliance analysis:
            
            1. Potential compliance issues:
               - Missing data protection clauses (GDPR)
               - Unclear liability terms
            
            2. Missing clauses:
               - Data breach notification procedure
               - Environmental compliance statements
            
            3. Recommended changes:
               - Add GDPR compliance section
               - Clarify liability terms
               - Include environmental compliance
            
            4. Overall risk assessment: Medium
            """
        }

        # Call the method
        result = self.client.analyze_compliance_document(self.document_text, self.industry, self.region)

        # Verify the mock was called with correct parameters
        mock_generate_text.assert_called_once()
        args, kwargs = mock_generate_text.call_args
        assert self.document_text[:100] in kwargs.get('prompt', args[0])
        assert self.industry in kwargs.get('prompt', args[0])
        assert self.region in kwargs.get('prompt', args[0])

        # Check result
        assert "Compliance analysis" in result.get("text", "")
        assert "Overall risk assessment" in result.get("text", "")

    @patch('utils.mistral_client.MistralAIClient.generate_text')
    def test_draft_order_communication(self, mock_generate_text):
        """Test drafting order communications with Mistral AI."""
        # Set up the mock
        mock_generate_text.return_value = {
            "text":
                """
            Subject: Order Confirmation: Order #ord-001
            
            Dear TechComponents Inc.,
            
            We are pleased to confirm your order #ord-001 for Microcontroller XC-42 (quantity: 500).
            
            The total amount is $6,250.00, with payment terms of Net 30.
            
            Current status: delivered
            
            Please don't hesitate to contact us if you have any questions or concerns.
            
            Best regards,
            Tacto Team
            """
        }

        # Call the method
        result = self.client.draft_order_communication(self.order_data, self.supplier_data, self.communication_type)

        # Verify the mock was called with correct parameters
        mock_generate_text.assert_called_once()
        args, kwargs = mock_generate_text.call_args
        assert self.order_data.get('id') in kwargs.get('prompt', args[0])
        assert self.supplier_data.get('name') in kwargs.get('prompt', args[0])
        assert self.communication_type in kwargs.get('prompt', args[0])

        # Check result
        assert "Order Confirmation" in result.get("text", "")
        assert self.order_data.get('id') in result.get("text", "")
