import io
import uuid
import pytest
from PIL import Image

def register_donor(client):
    unique_email = f"donor_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "name": "Photo Test Donor",
        "email": unique_email,
        "password": "Password123!",
        "role": "donor",
        "phone": "+91 9123456789",
        "address": "College Canteen",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    return res.json()["access_token"]

def create_image_bytes(format="JPEG"):
    buf = io.BytesIO()
    img = Image.new("RGB", (120, 120), color=(60, 140, 80))
    img.save(buf, format=format)
    buf.seek(0)
    return buf.getvalue()

def test_ordinary_photo_upload_success(client):
    token = register_donor(client)
    img_bytes = create_image_bytes("JPEG")
    files = {"image": ("canteen_meal.jpg", img_bytes, "image/jpeg")}

    res = client.post(
        "/api/donations/upload-image",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "image_url" in data
    assert data["image_url"].startswith("/uploads/donation_")

def test_photo_upload_rejects_invalid_type(client):
    token = register_donor(client)
    files = {"image": ("notes.txt", b"Invalid text data", "text/plain")}

    res = client.post(
        "/api/donations/upload-image",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 400
    assert "Unsupported image type" in res.json()["detail"]

def test_photo_upload_rejects_oversized(client):
    token = register_donor(client)
    huge_bytes = b"0" * (10 * 1024 * 1024 + 1024)
    files = {"image": ("huge_photo.jpg", huge_bytes, "image/jpeg")}

    res = client.post(
        "/api/donations/upload-image",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 400
    assert "exceeds 10 MB limit" in res.json()["detail"]

