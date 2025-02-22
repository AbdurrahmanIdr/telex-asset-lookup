import hmac
import hashlib
import requests
from flask import Blueprint, request, jsonify
from app.services import GoogleSheetsService
from app.config import config

google_sheets_bp = Blueprint("google_sheets", __name__)
sheets_service = GoogleSheetsService()


def verify_telex_request(req):
    """Verify Telex request using HMAC signature."""
    signature = req.headers.get("X-Telex-Signature")
    if not signature:
        return False

    computed_signature = hmac.new(
        config.TELEX_WEBHOOK_SECRET.encode(), req.data, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, signature)


@google_sheets_bp.route("/api/telex/webhook", methods=["POST"])
def telex_webhook():
    """Telex webhook to fetch IT asset details based on Service Tag."""
    if not verify_telex_request(request):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    service_tag = data.get("service_tag")  # Use Service Tag instead of asset_id
    return_url = data.get("return_url")

    if not service_tag or not return_url:
        return jsonify({"error": "Missing service_tag or return_url"}), 400

    asset_details = sheets_service.get_asset_details(service_tag)

    if not asset_details:
        return jsonify({"error": "Asset not found"}), 404

    # Send the extracted details back to Telex
    response = requests.post(return_url, json=asset_details)

    if response.status_code == 200:
        return jsonify({"message": "Asset details sent to Telex"}), 200
    else:
        return jsonify({"error": "Failed to send data to Telex"}), 500
