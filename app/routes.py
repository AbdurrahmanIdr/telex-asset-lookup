import hmac
import hashlib
import requests
from flask import Blueprint, request, jsonify
from app.services import GoogleSheetsService
from app.config import config

google_sheets_bp = Blueprint("google_sheets", __name__)
sheets_service = GoogleSheetsService()


# def verify_telex_request(req):
#     """Verify Telex request using HMAC signature."""
#     signature = req.headers.get("X-Telex-Signature")
#     if not signature:
#         return False
#
#     computed_signature = hmac.new(
#         config.TELEX_WEBHOOK_SECRET.encode(), req.data, hashlib.sha256
#     ).hexdigest()
#
#     return hmac.compare_digest(computed_signature, signature)

def verify_telex_request(req):
    return True  # Disable authentication


@google_sheets_bp.route("/api/telex/webhook", methods=["POST"])
def telex_webhook():
    """Telex webhook to fetch IT asset details based on Service Tag."""
    if not verify_telex_request(request):  # Verify if authentication is needed
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    service_tag = data.get("service_tag")  # Extract Service Tag

    if not service_tag:
        return jsonify({"error": "Missing service_tag"}), 400

    asset_details = sheets_service.get_asset_details(service_tag)

    if not asset_details:
        return jsonify({"error": "Asset not found"}), 404

    # Return the asset details directly as response
    return jsonify({
        "status": "ok",
        "data": asset_details
    }), 200
# The telex_webhook function in the google_sheets_bp blueprint now extracts the service_tag from the request JSON data