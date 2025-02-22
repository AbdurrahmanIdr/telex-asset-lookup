# IT Asset Management with Google Sheets Integration

This project provides a Flask-based web application that integrates with Google Sheets to manage and retrieve IT asset details. It uses a service account to authenticate with Google Sheets API and provides a webhook endpoint for Telex integration.

## Features

- **Google Sheets Integration**: Fetch IT asset details from a Google Sheets document.
- **Telex Webhook**: Accepts webhook requests from Telex to retrieve asset details based on a service tag.
- **HMAC Verification**: Securely verify incoming Telex requests using HMAC signatures.

## Setup

### Prerequisites

1. **Python 3.8+**: Ensure Python is installed on your system.
2. **Google Cloud Project**: Create a project in the Google Cloud Console and enable the Google Sheets API.
3. **Service Account**: Create a service account and download the JSON key file.
4. **Google Sheets Document**: Create a Google Sheets document and share it with the service account email.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AbdurrahmanIdr/telex-asset-lookup.git
   cd telex-asset-lookup
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add the following environment variables:
   ```env
   GOOGLE_SHEETS_CREDENTIALS='<paste your service account JSON here>'
   GOOGLE_SHEET_ID='<your Google Sheets document ID>'
   GOOGLE_SHEET_NAME='Sheet1'
   TELEX_WEBHOOK_SECRET='<your Telex webhook secret>'
   TELEX_TARGET_URL='<your Telex target URL>'
   ```

4. Run the application:
   ```bash
   python run.py
   ```

### Usage

- The application will start a Flask server on `http://127.0.0.1:5000`.
- Use the `/api/telex/webhook` endpoint to fetch asset details by sending a POST request with a `service_tag` and `return_url`.

### Example Request

```json
{
  "service_tag": "HJT0P34",
  "return_url": "https://example.com/webhook"
}
```

### Example Response

```json
{
  "Status": "In Use",
  "Previous User": "John Doe",
  "Current User": "Jane Doe",
  "Hostname": "DESKTOP-12345",
  "Service Tag": "HJT0P34",
  "Laptop Model": "Dell XPS 13",
  "Location": "New York"
}
```

## Project Structure

- `run.py`: Entry point for the Flask application.
- `app/__init__.py`: Initializes the Flask app and registers blueprints.
- `app/config.py`: Configuration settings for the application.
- `app/routes.py`: Defines the routes and webhook logic.
- `app/services.py`: Handles Google Sheets operations.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```