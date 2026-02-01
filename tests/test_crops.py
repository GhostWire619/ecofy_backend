import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

client = TestClient(app)


def create_admin_if_not_exists():
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            full_name="Admin User",
            phone_number="0000000000",
            location="HQ",
            hashed_password=get_password_hash("password"),
            role="admin",
            preferred_language="en"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    db.close()
    return admin


def test_create_crop():
    admin = create_admin_if_not_exists()
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "TestCrop",
        "description": "Test description",
        "optimal_planting_time": "Now",
        "climate_requirements": {
            "temperature_min": 10.0,
            "temperature_max": 30.0,
            "rainfall_min": 100.0,
            "rainfall_max": 500.0,
            "humidity_min": 30.0,
            "humidity_max": 80.0,
            "growing_season": "90 days"
        },
        "soil_requirements": {
            "soil_type": "Loamy",
            "ph_min": 5.0,
            "ph_max": 7.0,
            "nitrogen": "Medium",
            "phosphorus": "Medium",
            "potassium": "Medium",
            "ec": "0.2",
            "salinity": "Low",
            "water_holding": "Medium",
            "organic_matter": "Medium"
        },
        "risks": [
            {"title": "Pests", "description": "Some pests", "severity": "Medium"}
        ]
    }

    import json as _json
    response = client.post("/api/v1/crops", headers=headers, data={"data": _json.dumps(payload)})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data
    assert data.get("image_path") is None
    assert data.get("image_url") is None


def test_upload_crop_image():
    admin = create_admin_if_not_exists()
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a crop first
    payload = {
        "name": "UploadCrop",
        "description": "Will upload image",
        "optimal_planting_time": "Now",
        "climate_requirements": {
            "temperature_min": 10.0,
            "temperature_max": 30.0,
            "rainfall_min": 100.0,
            "rainfall_max": 500.0,
            "humidity_min": 30.0,
            "humidity_max": 80.0,
            "growing_season": "90 days"
        },
        "soil_requirements": {
            "soil_type": "Loamy",
            "ph_min": 5.0,
            "ph_max": 7.0,
            "nitrogen": "Medium",
            "phosphorus": "Medium",
            "potassium": "Medium",
            "ec": "0.2",
            "salinity": "Low",
            "water_holding": "Medium",
            "organic_matter": "Medium"
        },
        "risks": [
            {"title": "Pests", "description": "Some pests", "severity": "Medium"}
        ]
    }

    import json as _json

    # Create with file in same request (multipart)
    files = {"file": ("test.jpg", b"fake-image-bytes", "image/jpeg")}
    form = {"data": _json.dumps(payload)}
    resp = client.post("/api/v1/crops", headers=headers, data=form, files=files)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("image_path") is not None
    assert data.get("image_url") is not None

    # Verify file exists on disk
    from pathlib import Path
    crop_id = data["id"]
    uploaded_file = Path("uploads") / "crops" / f"{crop_id}_test.jpg"
    assert uploaded_file.exists()

    # Cleanup
    try:
        uploaded_file.unlink()
    except Exception:
        pass
