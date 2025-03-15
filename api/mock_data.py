"""Mock data for the Tacto API"""

# Sample supplier data
suppliers_data = [{
    "id": "sup-001",
    "name": "TechComponents Inc.",
    "description": "Leading provider of electronic components",
    "categories": ["electronics", "hardware"],
    "rating": 4.7,
    "avg_price": 42.50,
    "sustainability_score": 85,
    "locations": ["USA", "Mexico", "Taiwan"],
    "contacts": [{
        "name": "John Smith",
        "role": "Account Manager",
        "email": "john@techcomp.com"
    }]
}, {
    "id": "sup-002",
    "name": "Global Materials Co.",
    "description": "Sustainable raw materials supplier",
    "categories": ["raw materials", "chemicals", "metals"],
    "rating": 4.2,
    "avg_price": 28.75,
    "sustainability_score": 92,
    "locations": ["Germany", "China", "Brazil"],
    "contacts": [{
        "name": "Maria Garcia",
        "role": "Sales Director",
        "email": "maria@globalmaterials.com"
    }]
}, {
    "id": "sup-003",
    "name": "PackageSolutions Ltd.",
    "description": "Innovative packaging solutions",
    "categories": ["packaging", "paper products"],
    "rating": 4.5,
    "avg_price": 18.25,
    "sustainability_score": 78,
    "locations": ["UK", "France", "India"],
    "contacts": [{
        "name": "David Wilson",
        "role": "Regional Manager",
        "email": "david@packagesolutions.com"
    }]
}, {
    "id": "sup-004",
    "name": "QuickLogistics",
    "description": "Fast and reliable shipping services",
    "categories": ["logistics", "transportation"],
    "rating": 4.0,
    "avg_price": 65.30,
    "sustainability_score": 70,
    "locations": ["Canada", "USA", "Mexico"],
    "contacts": [{
        "name": "Sarah Johnson",
        "role": "Operations Manager",
        "email": "sarah@quicklogistics.com"
    }]
}, {
    "id": "sup-005",
    "name": "EcoMaterials",
    "description": "Environmentally friendly manufacturing materials",
    "categories": ["raw materials", "sustainable", "packaging"],
    "rating": 4.8,
    "avg_price": 35.45,
    "sustainability_score": 98,
    "locations": ["Sweden", "Denmark", "Germany"],
    "contacts": [{
        "name": "Erik Larsson",
        "role": "Sustainability Director",
        "email": "erik@ecomaterials.com"
    }]
}]

# Sample compliance requirements data
compliance_data = [{
    "id": "req-001",
    "name": "GDPR",
    "description": "General Data Protection Regulation",
    "industry": "all",
    "regions": ["EU", "global"],
    "requirements": ["Data processing agreements", "Privacy impact assessments", "Data breach notification procedures"]
}, {
    "id": "req-002",
    "name": "REACH",
    "description": "Registration, Evaluation, Authorization and Restriction of Chemicals",
    "industry": "manufacturing",
    "regions": ["EU", "global"],
    "requirements": ["Chemical registration", "Safety data sheets", "Substitute hazardous substances"]
}, {
    "id": "req-003",
    "name": "RoHS",
    "description": "Restriction of Hazardous Substances",
    "industry": "electronics",
    "regions": ["EU", "global"],
    "requirements": ["Limit use of hazardous materials", "Testing and certification", "Declaration of conformity"]
}, {
    "id": "req-004",
    "name": "CCPA",
    "description": "California Consumer Privacy Act",
    "industry": "all",
    "regions": ["USA"],
    "requirements": ["Privacy policy updates", "Data inventory", "Consumer rights processes"]
}, {
    "id":
        "req-005",
    "name":
        "ISO 9001",
    "description":
        "Quality Management System Standard",
    "industry":
        "all",
    "regions": ["global"],
    "requirements": [
        "Quality management documentation", "Process approach to management", "Continuous improvement mechanisms"
    ]
}]

# Sample orders data
orders_data = [{
    "id": "ord-001",
    "supplier_id": "sup-001",
    "supplier_name": "TechComponents Inc.",
    "status": "delivered",
    "created_at": "2024-03-01T10:15:30Z",
    "updated_at": "2024-03-10T16:22:45Z",
    "products": [{
        "id": "prod-001",
        "name": "Microcontroller XC-42",
        "quantity": 500,
        "price": 12.50
    }],
    "total_amount": 6250.00,
    "payment_terms": "Net 30",
    "notes": "Quarterly stock replenishment"
}, {
    "id": "ord-002",
    "supplier_id": "sup-003",
    "supplier_name": "PackageSolutions Ltd.",
    "status": "shipped",
    "created_at": "2024-03-05T09:30:00Z",
    "updated_at": "2024-03-12T11:45:20Z",
    "products": [{
        "id": "prod-102",
        "name": "Biodegradable Packaging Box M",
        "quantity": 1000,
        "price": 1.25
    }, {
        "id": "prod-103",
        "name": "Cushioning Material Roll",
        "quantity": 50,
        "price": 15.75
    }],
    "total_amount": 2037.50,
    "payment_terms": "Net 45",
    "notes": "Urgent shipment for new product launch"
}]

# Sample negotiations data (would be expanded in full implementation)
negotiations_data = []
