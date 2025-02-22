import re
import requests
from flask import Blueprint, request, jsonify
from app.services import GoogleSheetsService
from bs4 import BeautifulSoup  # For properly removing HTML tags

google_sheets_bp = Blueprint("google_sheets", __name__)
sheets_service = GoogleSheetsService()


def verify_telex_request(req):
    return True  # Authentication disabled for now


@google_sheets_bp.route("/api/telex/webhook", methods=["POST"])
def telex_webhook():
    """Telex webhook to fetch IT asset details based on Service Tag."""

    # Log raw request headers and body
    print("Headers:", dict(request.headers))
    print("Raw Body:", request.data)  # Logs raw body before JSON parsing
    print("Parsed JSON:", request.get_json())

    # Extract message safely
    data = request.get_json() or {}
    message_text = data.get("message", "")

    # Debugging: Print received message
    print("🔍 Raw Message from Telex:", repr(message_text))

    # Strip HTML using BeautifulSoup
    cleaned_message = BeautifulSoup(message_text, "html.parser").get_text()
    cleaned_message = " ".join(cleaned_message.split()).strip()

    # Debugging: Print cleaned message
    print("✅ Cleaned Message:", repr(cleaned_message))

    # If the message does not start with "/assetlookup", ignore it
    if not cleaned_message.lower().startswith("/assetlookup"):
        print("✅ Not an asset lookup command. Ignoring.")
        return "", 200

    # Extract service tag
    match = re.match(r"^/assetlookup\s+(\S+)", cleaned_message, re.IGNORECASE)
    if not match:
        print("❌ Invalid command format. Ignoring.")
        return "", 200

    service_tag = match.group(1).strip()
    print("✅ Extracted Service Tag:", repr(service_tag))

    # Fetch asset details
    asset_details = sheets_service.get_asset_details(service_tag)
    if not asset_details:
        return jsonify({"message": f"❌ Asset with Service Tag '{service_tag}' not found"}), 200

    # Format response
    response_text = (
        f"🔍 *Asset Lookup Result:*\n"
        f"🆔 *Service Tag:* {asset_details.get('Service Tag', 'N/A')}\n"
        f"💻 *Hostname:* {asset_details.get('Hostname', 'N/A')}\n"
        f"📌 *Model:* {asset_details.get('Laptop Model', 'N/A')}\n"
        f"👤 *Current User:* {asset_details.get('Current User', 'N/A')}\n"
        f"🔄 *Previous User:* {asset_details.get('Previous User', 'N/A')}\n"
        f"📍 *Location:* {asset_details.get('Location', 'N/A')}\n"
        f"📌 *Status:* {asset_details.get('Status', 'N/A')}"
    )

    # Debugging: Print response
    print("✅ Response to Telex:", response_text)

    # Send response to Telex
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

        # ✅ Ensure JSON response is valid
        try:
            print("Telex Response:", telex_response.json())
        except Exception:
            print("Telex Response (Non-JSON):", telex_response.text)

    except Exception as e:
        print("Error sending message to Telex:", str(e))

    return jsonify({"text": response_text}), 200
