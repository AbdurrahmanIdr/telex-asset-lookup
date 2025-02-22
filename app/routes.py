import re
import requests
from flask import Blueprint, request, jsonify
from app.services import GoogleSheetsService

google_sheets_bp = Blueprint("google_sheets", __name__)
sheets_service = GoogleSheetsService()


def verify_telex_request(req):
    return True  # Disabled authentication for now


@google_sheets_bp.route("/api/telex/webhook", methods=["POST"])
def telex_webhook():
    """Telex webhook to fetch IT asset details based on Service Tag."""

    # Log the full request for debugging
    print("Headers:", request.headers)
    print("Body:", request.get_json())

    if not verify_telex_request(request):  # Verify if authentication is needed
        return jsonify({"error": "Unauthorized"}), 403

    # Get request JSON
    data = request.get_json()
    message_text = data.get("message", "").strip()

    # Debugging logs
    print("✅ Received JSON:", data)
    print("✅ Extracted Message:", message_text)

    # Clean message (remove HTML, extra spaces)
    message_text = re.sub(r"<[^>]*>", "", message_text)  # Remove HTML tags if any
    message_text = " ".join(message_text.split())  # Normalize spaces

    # Debugging log after cleaning
    print("✅ Cleaned Message:", message_text)

    # Extract service tag from message
    match = re.search(r"/assetlookup\s+(\S+)", message_text, re.IGNORECASE)

    if not match:
        print("❌ Regex failed to match.")  # Debugging
        return jsonify({"error": "Invalid command format"}), 400

    service_tag = str(match.group(1)).strip()
    print("✅ Extracted Service Tag:", service_tag)  # Debugging

    # Fetch asset details from Google Sheets
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

    # Send response to Telex
    telex_webhook_url = "https://ping.telex.im/v1/webhooks/01952a7d-5b93-7600-add1-8c69c0289c9d"
    payload = {
        "event_name": "Asset Lookup",
        "message": response_text,
        "status": "success" if asset_details else "error",
        "username": "IT System"
    }

    try:
        telex_response = requests.post(
            telex_webhook_url,
            json=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"}
        )
        print("Telex Response:", telex_response.json())
    except Exception as e:
        print("Error sending message to Telex:", str(e))

    return jsonify({"text": response_text}), 200
