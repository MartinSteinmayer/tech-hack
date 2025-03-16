from flask import Blueprint, request, jsonify
from .mock_data import compliance_data
from .mock_data import suppliers_data
from langchain_mistralai import ChatMistralAI
import getpass
import os
from mistralai import Mistral
import fitz
import requests
from dotenv import load_dotenv


compliance_bp = Blueprint('compliance', __name__)

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-large-latest"

client = Mistral(api_key=api_key)



def extract_text_from_pdf(pdf_path):
    """Extract text from an uploaded PDF file using PyMuPDF."""
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

@compliance_bp.route('/analyze-document', methods=['POST'])
def analyze_document():
    """Accepts a PDF file, extracts text, and processes it."""

    # Check if a file is provided
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    # Ensure it's a PDF file
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Save the uploaded file
    temp_path = "uploaded_document.pdf"
    file.save(temp_path)

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(temp_path)

    # Process the extracted text (e.g., send it to Mistral, or return it for now)
    messages = [
        {
            "role": "user",
            "content": f"""You are a compliance expert analyzing legal documents.
            Analyze the following document for legal and compliance irregularities.
        Identify missing clauses, ambiguous language, and potential legal risks.
        Answer in JSON format with the following keys: identified clauses, compliance concerns, suggested actions and a compliance score from 0 to 100%.

        Document:
        {extracted_text}""",
        }
    ]
    chat_response = client.chat.complete(
          model = model,
          messages = messages,
          response_format = {
              "type": "json_object",
          }
    )

    os.remove(temp_path)  # Cleanup the temporary file
    return chat_response.choices[0].message.content



@compliance_bp.route('/requirements', methods=['POST'])
def get_requirements():
    data = request.get_json() #get the json payload (comes in json as {user_text} : {text}
    extracted_text = data.get("user_text","")

    if not extracted_text:
        return jsonify({"error": "No user_text provided"}), 400  # Return error if empty

    suppliers_database_json = str(suppliers_data)

    # Process the extracted text (e.g., send it to Mistral, or return it for now)
    messages = [
        {
            "role": "user",
            "content": f"""You are an AI assistant specializing in supplier selection. Your task is to analyze user-provided supplier requirements and match them with the most suitable suppliers from a given database, which in our case is a list of suppliers in JSON format. After analyzing the availiable suppliers from the list, output in JSON format which suppliers fit the requirements (if any) and give reasons why they are a good fit.

        Client's requirements:
        {extracted_text} \n\n
        Database:\n
         {suppliers_database_json}\n   """,
        }
    ]
    chat_response = client.chat.complete(
          model = model,
          messages = messages,
          response_format = {
              "type": "json_object",
          }
    )

    return chat_response.choices[0].message.content


@compliance_bp.route('/verify', methods=['POST'])
def verify_compliance():
    """Verify compliance status for a supplier or document"""
    data = request.json
    supplier_id = data.get('supplier_id')
    document_id = data.get('document_id')

    # This would later connect to the knowledge graph to check actual compliance
    verification_result = {
        "status": "partially_compliant",
        "compliant_areas": ["Environmental regulations", "Labor practices"],
        "non_compliant_areas": ["Data protection requirements"],
        "risk_score": 65,  # 0-100, higher is riskier
        "recommended_actions": ["Request updated data protection policy", "Schedule compliance audit within 60 days"]
    }

    return jsonify(verification_result)



 @compliance_bp.route('/test', methods=['GET'])
 def test():
    messages = [
        {
            "role": "user",
            "content": "What is the best French meal? Return the name and the ingredients in short JSON object.",
        }
    ]
    chat_response = client.chat.complete(
          model = model,
          messages = messages,
          response_format = {
              "type": "json_object",
          }
    )
    # print(chat_response.choices[0].message.content)
    return chat_response.choices[0].message.content
