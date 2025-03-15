import weaviate
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class SupplierKnowledgeGraph:
    """Client for interacting with Weaviate knowledge graph for suppliers"""

    def __init__(self):
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

        # Initialize Weaviate client
        auth_config = weaviate.auth.AuthApiKey(api_key=self.weaviate_api_key) if self.weaviate_api_key else None

        self.client = weaviate.Client(url=self.weaviate_url, auth_client_secret=auth_config)

        # Check if schema exists, create if not
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensure the necessary schema exists in Weaviate"""
        # Check if Supplier class exists
        if not self.client.schema.exists("Supplier"):
            # Create Supplier class
            supplier_class = {
                "class":
                    "Supplier",
                "description":
                    "Information about a supplier",
                "vectorizer":
                    "text2vec-transformers",  # Use appropriate vectorizer
                "properties": [{
                    "name": "name",
                    "dataType": ["string"],
                    "description": "The name of the supplier"
                }, {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "Description of the supplier"
                }, {
                    "name": "categories",
                    "dataType": ["string[]"],
                    "description": "Product categories offered by the supplier"
                }, {
                    "name": "rating",
                    "dataType": ["number"],
                    "description": "Rating of the supplier (0-5)"
                }, {
                    "name": "avgPrice",
                    "dataType": ["number"],
                    "description": "Average price of products"
                }, {
                    "name": "sustainabilityScore",
                    "dataType": ["number"],
                    "description": "Sustainability score (0-100)"
                }, {
                    "name": "locations",
                    "dataType": ["string[]"],
                    "description": "Locations where the supplier operates"
                }]
            }

            self.client.schema.create_class(supplier_class)

        # Create other classes (Product, Compliance, Order) as needed
        # For brevity, just showing Supplier class here

    def add_supplier(self, supplier_data):
        """Add a supplier to the knowledge graph"""
        # Convert from API format to Weaviate format
        weaviate_data = {
            "name": supplier_data.get("name"),
            "description": supplier_data.get("description", ""),
            "categories": supplier_data.get("categories", []),
            "rating": supplier_data.get("rating", 0),
            "avgPrice": supplier_data.get("avg_price", 0),
            "sustainabilityScore": supplier_data.get("sustainability_score", 0),
            "locations": supplier_data.get("locations", [])
        }

        # Add to Weaviate
        try:
            result = self.client.data_object.create(data_object=weaviate_data, class_name="Supplier")
            return result
        except Exception as e:
            print(f"Error adding supplier to Weaviate: {e}")
            return None

    def search_suppliers(self, query, categories=None, min_rating=None, min_sustainability=None):
        """Search for suppliers based on semantic query and filters"""
        # Start building query
        graphql_query = """
        {
            Get {
                Supplier(
                    limit: 10
                    nearText: {
                        concepts: ["%s"]
                    }
                    %s
                ) {
                    name
                    description
                    categories
                    rating
                    avgPrice
                    sustainabilityScore
                    locations
                    _additional {
                        id
                        certainty
                    }
                }
            }
        }
        """

        # Build where filter
        where_filters = []

        if categories:
            categories_filter = 'where: { operator: ContainsAny, path: ["categories"], valueString: ["%s"] }' % '", "'.join(
                categories)
            where_filters.append(categories_filter)

        if min_rating:
            rating_filter = 'where: { operator: GreaterThanEqual, path: ["rating"], valueNumber: %f }' % min_rating
            where_filters.append(rating_filter)

        if min_sustainability:
            sustainability_filter = 'where: { operator: GreaterThanEqual, path: ["sustainabilityScore"], valueNumber: %f }' % min_sustainability
            where_filters.append(sustainability_filter)

        # Combine where filters if any
        where_clause = ""
        if where_filters:
            where_clause = ", ".join(where_filters)

        # Execute query
        result = self.client.query.raw(graphql_query % (query, where_clause))

        # Convert from Weaviate format to API format
        suppliers = []
        if result and "data" in result and "Get" in result["data"] and "Supplier" in result["data"]["Get"]:
            for supplier in result["data"]["Get"]["Supplier"]:
                api_supplier = {
                    "id": supplier["_additional"]["id"],
                    "name": supplier["name"],
                    "description": supplier["description"],
                    "categories": supplier["categories"],
                    "rating": supplier["rating"],
                    "avg_price": supplier["avgPrice"],
                    "sustainability_score": supplier["sustainabilityScore"],
                    "locations": supplier["locations"],
                    "match_certainty": supplier["_additional"]["certainty"]
                }
                suppliers.append(api_supplier)

        return suppliers

    def get_supplier_recommendations(self, category, location=None):
        """Get recommended suppliers based on category and optional location"""
        # Query to find suppliers in the category with high ratings
        graphql_query = """
        {
            Get {
                Supplier(
                    limit: 5
                    where: {
                        operator: ContainsAny,
                        path: ["categories"],
                        valueString: ["%s"]
                    }
                    sort: [
                        {
                            path: ["rating"],
                            order: desc
                        }
                    ]
                ) {
                    name
                    description
                    categories
                    rating
                    avgPrice
                    sustainabilityScore
                    locations
                    _additional {
                        id
                    }
                }
            }
        }
        """ % category

        # Add location filter if provided
        if location:
            graphql_query = """
            {
                Get {
                    Supplier(
                        limit: 5
                        where: {
                            operator: And,
                            operands: [
                                {
                                    operator: ContainsAny,
                                    path: ["categories"],
                                    valueString: ["%s"]
                                },
                                {
                                    operator: ContainsAny,
                                    path: ["locations"],
                                    valueString: ["%s"]
                                }
                            ]
                        }
                        sort: [
                            {
                                path: ["rating"],
                                order: desc
                            }
                        ]
                    ) {
                        name
                        description
                        categories
                        rating
                        avgPrice
                        sustainabilityScore
                        locations
                        _additional {
                            id
                        }
                    }
                }
            }
            """ % (category, location)

        # Execute query
        result = self.client.query.raw(graphql_query)

        # Convert from Weaviate format to API format
        suppliers = []
        if result and "data" in result and "Get" in result["data"] and "Supplier" in result["data"]["Get"]:
            for supplier in result["data"]["Get"]["Supplier"]:
                api_supplier = {
                    "id": supplier["_additional"]["id"],
                    "name": supplier["name"],
                    "description": supplier["description"],
                    "categories": supplier["categories"],
                    "rating": supplier["rating"],
                    "avg_price": supplier["avgPrice"],
                    "sustainability_score": supplier["sustainabilityScore"],
                    "locations": supplier["locations"]
                }
                suppliers.append(api_supplier)

        return suppliers

    def import_suppliers(self, suppliers_list):
        """Batch import suppliers into the knowledge graph"""
        batch = self.client.batch.configure(batch_size=100)

        with batch:
            for supplier in suppliers_list:
                # Convert from API format to Weaviate format
                weaviate_data = {
                    "name": supplier.get("name"),
                    "description": supplier.get("description", ""),
                    "categories": supplier.get("categories", []),
                    "rating": supplier.get("rating", 0),
                    "avgPrice": supplier.get("avg_price", 0),
                    "sustainabilityScore": supplier.get("sustainability_score", 0),
                    "locations": supplier.get("locations", [])
                }

                # Add to batch
                self.client.batch.add_data_object(data_object=weaviate_data, class_name="Supplier")

        return {"message": f"Imported {len(suppliers_list)} suppliers"}


# Example Usage in API
# ------------------


# Example for enhanced supplier search endpoint using Weaviate:
@suppliers_bp.route('/search', methods=['POST'])
def search_suppliers():
    """Search suppliers based on specific criteria"""
    criteria = request.json

    # Initialize Weaviate client
    kg = SupplierKnowledgeGraph()

    # Extract search parameters
    query = criteria.get('query', '')
    categories = criteria.get('categories', [])
    min_rating = criteria.get('min_rating')
    min_sustainability = criteria.get('min_sustainability')

    # Search using knowledge graph
    results = kg.search_suppliers(query=query,
                                  categories=categories,
                                  min_rating=min_rating,
                                  min_sustainability=min_sustainability)

    return jsonify(results)


# Example for generating negotiation strategy using Mistral AI:
@negotiations_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """Get pricing strategies based on supplier and product"""
    supplier_id = request.args.get('supplier_id')
    product_category = request.args.get('category')
    negotiation_goal = request.args.get('goal', 'price reduction')

    # Find supplier
    supplier = next((s for s in suppliers_data if s['id'] == supplier_id), None)
    if not supplier:
        return jsonify({"error": "Supplier not found"}), 404

    # Initialize Mistral AI client
    mistral = MistralAIClient()

    # Generate strategies
    response = mistral.generate_negotiation_strategy(supplier_data=supplier,
                                                     product_category=product_category,
                                                     negotiation_goal=negotiation_goal)

    # Parse and structure the response
    # This would need to be adapted based on actual Mistral AI response format
    strategies = [
        {
            "name": "Strategy 1",
            "description": "Description of first strategy",
            "talking_points": ["Point 1", "Point 2"],
            "concessions": ["Concession 1"],
            "target_discount": "5-10%"
        },
        # Add more strategies from parsed response
    ]

    return jsonify(strategies)
