import pytest
import json
import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the SupplierKnowledgeGraph to test
try:
    from utils.weaviate_client import SupplierKnowledgeGraph
except ImportError:
    # If not yet created, create a simple mock for testing
    class SupplierKnowledgeGraph:

        def __init__(self):
            self.client = MagicMock()

        def _ensure_schema(self):
            pass

        def add_supplier(self, supplier_data):
            return {"id": "mock-uuid-1234"}

        def search_suppliers(self, query, categories=None, min_rating=None, min_sustainability=None):
            return [{
                "id": "mock-uuid-1234",
                "name": "Mock Supplier",
                "description": "A mock supplier for testing",
                "categories": categories or ["test"],
                "rating": 4.5,
                "avg_price": 50.0,
                "sustainability_score": 80,
                "locations": ["Test Location"],
                "match_certainty": 0.95
            }]

        def get_supplier_recommendations(self, category, location=None):
            return [{
                "id": "mock-uuid-1234",
                "name": "Recommended Supplier",
                "description": "A recommended supplier for testing",
                "categories": [category],
                "rating": 4.8,
                "avg_price": 45.0,
                "sustainability_score": 90,
                "locations": [location] if location else ["Test Location"]
            }]

        def import_suppliers(self, suppliers_list):
            return {"message": f"Imported {len(suppliers_list)} suppliers"}


# Sample data for testing
from api.mock_data import suppliers_data


class TestWeaviateIntegration(unittest.TestCase):
    """Test the integration with Weaviate knowledge graph."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize with mock client
        self.kg = SupplierKnowledgeGraph()

        # Sample data for tests
        self.supplier_data = suppliers_data[0]
        self.search_query = "electronic components quality"
        self.categories = ["electronics"]
        self.min_rating = 4.0
        self.min_sustainability = 75
        self.category = "electronics"
        self.location = "USA"

    @patch('weaviate.Client')
    def test_add_supplier(self, mock_weaviate_client):
        """Test adding a supplier to the knowledge graph."""
        # Set up the mock
        mock_client = MagicMock()
        mock_weaviate_client.return_value = mock_client
        mock_client.data_object.create.return_value = {"id": "mock-uuid-1234"}

        # Create instance with mock
        kg = SupplierKnowledgeGraph()
        kg.client = mock_client

        # Call the method
        result = kg.add_supplier(self.supplier_data)

        # Verify the mock was called
        mock_client.data_object.create.assert_called_once()

        # Check that required fields were included
        args, kwargs = mock_client.data_object.create.call_args
        assert kwargs["class_name"] == "Supplier"
        assert kwargs["data_object"]["name"] == self.supplier_data["name"]
        assert "categories" in kwargs["data_object"]

        # Check result
        assert "id" in result

    @patch('weaviate.Client')
    def test_search_suppliers(self, mock_weaviate_client):
        """Test searching for suppliers in the knowledge graph."""
        # Set up the mock
        mock_client = MagicMock()
        mock_weaviate_client.return_value = mock_client

        # Mock the query response
        mock_response = {
            "data": {
                "Get": {
                    "Supplier": [{
                        "name": "Test Supplier",
                        "description": "A test supplier",
                        "categories": ["electronics"],
                        "rating": 4.5,
                        "avgPrice": 50.0,
                        "sustainabilityScore": 80,
                        "locations": ["USA"],
                        "_additional": {
                            "id": "mock-uuid-1234",
                            "certainty": 0.95
                        }
                    }]
                }
            }
        }
        mock_client.query.raw.return_value = mock_response

        # Create instance with mock
        kg = SupplierKnowledgeGraph()
        kg.client = mock_client

        # Call the method
        results = kg.search_suppliers(query=self.search_query,
                                      categories=self.categories,
                                      min_rating=self.min_rating,
                                      min_sustainability=self.min_sustainability)

        # Verify the mock was called
        mock_client.query.raw.assert_called_once()

        # Check query contains search terms and filters
        args, kwargs = mock_client.query.raw.call_args
        query = args[0]
        assert self.search_query in query

        # Check result format
        assert len(results) == 1
        assert "id" in results[0]
        assert "name" in results[0]
        assert "categories" in results[0]
        assert "rating" in results[0]
        assert "match_certainty" in results[0]

    @patch('weaviate.Client')
    def test_get_supplier_recommendations(self, mock_weaviate_client):
        """Test getting supplier recommendations from the knowledge graph."""
        # Set up the mock
        mock_client = MagicMock()
        mock_weaviate_client.return_value = mock_client

        # Mock the query response
        mock_response = {
            "data": {
                "Get": {
                    "Supplier": [{
                        "name": "Recommended Supplier",
                        "description": "A top supplier",
                        "categories": ["electronics"],
                        "rating": 4.8,
                        "avgPrice": 45.0,
                        "sustainabilityScore": 90,
                        "locations": ["USA"],
                        "_additional": {
                            "id": "mock-uuid-5678"
                        }
                    }]
                }
            }
        }
        mock_client.query.raw.return_value = mock_response

        # Create instance with mock
        kg = SupplierKnowledgeGraph()
        kg.client = mock_client

        # Call the method
        results = kg.get_supplier_recommendations(category=self.category, location=self.location)

        # Verify the mock was called
        mock_client.query.raw.assert_called_once()

        # Check query contains category and location
        args, kwargs = mock_client.query.raw.call_args
        query = args[0]
        assert self.category in query
        assert self.location in query

        # Check result format
        assert len(results) == 1
        assert "id" in results[0]
        assert "name" in results[0]
        assert "categories" in results[0]
        assert "rating" in results[0]

    @patch('weaviate.Client')
    def test_import_suppliers(self, mock_weaviate_client):
        """Test importing multiple suppliers to the knowledge graph."""
        # Set up the mock
        mock_client = MagicMock()
        mock_weaviate_client.return_value = mock_client

        # Create a mock batch object
        mock_batch = MagicMock()
        mock_client.batch.configure.return_value = mock_batch

        # Create instance with mock
        kg = SupplierKnowledgeGraph()
        kg.client = mock_client

        # Call the method
        result = kg.import_suppliers(suppliers_data)

        # Verify the mocks were called
        mock_client.batch.configure.assert_called_once()
        assert mock_client.batch.add_data_object.call_count == len(suppliers_data)

        # Check result
        assert "message" in result
        assert str(len(suppliers_data)) in result["message"]
