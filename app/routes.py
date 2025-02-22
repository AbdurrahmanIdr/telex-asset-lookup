import re
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

    data = request.json
    text = data.get("text", "")

    # Extract service tag from the command format: `/assetlookup HJT0P34`
    match = re.match(r"/assetlookup\s+(\S+)", text)
    if not match:
        return jsonify({"error": "Invalid command format"}), 400

    service_tag = match.group(1)
    print(f"🔍 Looking up asset for Service Tag: {service_tag}")

    # Query Google Sheets for asset details
    asset_details = sheets_service.get_asset_details(service_tag)

    if not asset_details:
        return jsonify({"text": f"❌ Asset with Service Tag '{service_tag}' not found"}), 200

    # Format the response for Telex
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

    return jsonify({"text": response_text}), 200
# The telex_webhook function is a route that listens for POST requests at /api/telex/webhook.