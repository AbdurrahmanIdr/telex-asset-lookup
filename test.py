import json
import pytest
from flask import Flask
from app.routes import google_sheets_bp
from app.services import GoogleSheetsService

# Mock the GoogleSheetsService
class MockGoogleSheetsService:
    def get_asset_details(self, service_tag):
        if service_tag == "HJT0P34":
            return {
                "Service Tag": "HJT0P34",
                "Hostname": "NABUA35229",
                "Laptop Model": "Dell Latitude 5440",
                "Current User": "Abdurrahman.Idris@garda.com",
                "Previous User": "",
                "Location": "",
                "Status": "New"
            }
        return None

# Patch the service in the blueprint
sheets_service = MockGoogleSheetsService()

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(google_sheets_bp)
    app.testing = True
    return app.test_client()

def test_ignore_non_assetlookup_messages(client):
    response = client.post("/api/telex/webhook", json={"message": "Hello, this is a normal message"})
    assert response.status_code == 200
    assert response.data == b""

def test_invalid_assetlookup_format(client):
    response = client.post("/api/telex/webhook", json={"message": "/assetlook HJT0P34"})
    assert response.status_code == 200
    assert response.data == b""

def test_valid_assetlookup(client):
    response = client.post("/api/telex/webhook", json={"message": "/assetlookup HJT0P34"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "text" in data
    assert "Service Tag: HJT0P34" in data["text"]

def test_asset_not_found(client):
    response = client.post("/api/telex/webhook", json={"message": "/assetlookup UNKNOWN"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert "Asset with Service Tag 'UNKNOWN' not found" in data["message"]
