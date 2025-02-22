import re
import requests
from flask import Blueprint, request, jsonify
from app.services import GoogleSheetsService
from bs4 import BeautifulSoup

# Blueprint for handling Google Sheets-related API routes
google_sheets_bp = Blueprint("google_sheets", __name__)
sheets_service = GoogleSheetsService()


def verify_telex_request(req):
    """Placeholder function for verifying Telex requests. Currently, authentication is disabled."""
    return True


@google_sheets_bp.route("/api/telex/webhook", methods=["POST"])
def telex_webhook():
    """Webhook endpoint to process asset lookup requests from Telex."""

    # Parse incoming JSON request
    data = request.get_json() or {}
    message_text = data.get("message", "").strip()

    # Remove HTML tags from the message
    cleaned_message = BeautifulSoup(message_text, "html.parser").get_text()
    cleaned_message = " ".join(cleaned_message.split()).strip()

    # Ignore messages that do not match the asset lookup command format
    if not cleaned_message.lower().startswith("/assetlookup"):
        return "", 200

    # Extract the service tag from the message
    match = re.match(r"^/assetlookup\s+(\S+)", cleaned_message, re.IGNORECASE)
    if not match:
        return "", 200

    service_tag = match.group(1).strip()

    # Retrieve asset details from Google Sheets
    asset_details = sheets_service.get_asset_details(service_tag)
    if not asset_details:
        return jsonify({"message": f"Asset with Service Tag '{service_tag}' not found"}), 200

    # Construct the response message with asset details
    response_text = (
        f"Asset Lookup Result:\n"
        f"Service Tag: {asset_details.get('Service Tag', 'N/A')}\n"
        f"Hostname: {asset_details.get('Hostname', 'N/A')}\n"
        f"Model: {asset_details.get('Laptop Model', 'N/A')}\n"
        f"Current User: {asset_details.get('Current User', 'N/A')}\n"
        f"Previous User: {asset_details.get('Previous User', 'N/A')}\n"
        f"Location: {asset_details.get('Location', 'N/A')}\n"
        f"Status: {asset_details.get('Status', 'N/A')}"
    )

    # Send response to the Telex webhook
    telex_webhook_url = "https://ping.telex.im/v1/webhooks/01952a7d-5b93-7600-add1-8c69c0289c9d"
    payload = {
        "event_name": "Asset Lookup",
        "message": response_text,
        "status": "success",
        "username": "IT System"
    }

    try:
        telex_response = requests.post(
            telex_webhook_url,
            json=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"}
        )

        # Validate Telex response
        try:
            telex_response.json()
        except Exception:
            pass  # Ignore non-JSON responses
    except Exception as e:
        pass  # Handle network or API request errors gracefully

    return jsonify({"text": response_text}), 200
