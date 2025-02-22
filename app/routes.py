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
    message_text = data.get("message", "")

    # Extract service tag from the message using regex
    match = re.search(r"/assetlookup\s+(\S+)", message_text)
    if not match:
        return jsonify({"error": "Invalid command format"}), 400

    service_tag = match.group(1)

    # Query Google Sheets
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
# The telex_webhook function is a view function that processes incoming webhook requests from Telex.
# The function extracts the service tag from the message text using a regular expression, queries Google Sheets
# for the asset details, and formats the response text to be sent back to Telex.
# The response text includes details such as the service tag, hostname, model, current user, previous user, location, and status of the asset.
# The response is then returned as a JSON object with the appropriate HTTP status code.
# The GoogleSheetsService class is used to interact with Google Sheets and retrieve asset details based on the service tag.
# The verify_telex_request function is used to verify the authenticity of the incoming Telex webhook request, but it is currently disabled for simplicity.
# The google_sheets_bp Blueprint is used to define the route for the Telex webhook and handle the incoming requests.
# The route "/api/telex/webhook" is registered with the Blueprint and associated with the telex_webhook view function.
# When Telex sends a POST request to this route, the telex_webhook function is executed to process the request.
# The function extracts the necessary information from the request, processes the data, and sends a response back to Telex.
# The response includes the asset details retrieved from Google Sheets in a formatted text message.
# The response is sent back to Telex as a JSON object with the appropriate status code.
# The view function is responsible for handling the business logic of processing the webhook request and generating the appropriate response.
# The GoogleSheetsService class encapsulates the functionality for interacting with Google Sheets and retrieving asset details based on the service tag.
