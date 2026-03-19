import pytest
from frontend.app import app


# -------------------------
# Setup test client
# -------------------------
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# -------------------------
# User Registration
# -------------------------
def test_user_register(client, monkeypatch):
    def mock_post(*args, **kwargs):
        class MockResponse:
            status_code = 201
            def json(self):
                return {}
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)

    response = client.post("/user/register", data={
        "username": "testuser",
        "password": "testpass"
    })

    assert response.status_code == 200


# -------------------------
# User Login
# -------------------------
def test_user_login(client, monkeypatch):
    def mock_post(*args, **kwargs):
        class MockResponse:
            ok = True
            def json(self):
                return {"token": "fake-token", "role": "USER"}
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)

    response = client.post("/user/login", data={
        "username": "testuser",
        "password": "testpass"
    })

    assert response.status_code == 302  # redirect


# -------------------------
# Admin Login Protection
# -------------------------
def test_admin_dashboard_requires_login(client):
    response = client.get("/admin/dashboard")
    assert response.status_code == 302


# -------------------------
# Admin Add Restaurant
# -------------------------
def test_admin_add_restaurant(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["admin_token"] = "fake-token"

    def mock_post(*args, **kwargs):
        class MockResponse:
            ok = True
            status_code = 200
            def json(self):
                return {}
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)

    response = client.post("/admin/restaurants", json={
        "name": "Test Restaurant",
        "cuisine": "Italian",
        "location": "Toronto"
    })

    assert response.status_code == 200


# -------------------------
# Admin Delete Restaurant
# -------------------------
def test_admin_delete_restaurant(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["admin_token"] = "fake-token"

    def mock_delete(*args, **kwargs):
        class MockResponse:
            ok = True
            status_code = 200
            def json(self):
                return {}
        return MockResponse()

    monkeypatch.setattr("requests.delete", mock_delete)

    response = client.delete("/admin/restaurants/1")
    assert response.status_code == 200


# -------------------------
# Admin Update Restaurant
# -------------------------
def test_admin_update_restaurant(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["admin_token"] = "fake-token"

    def mock_put(*args, **kwargs):
        class MockResponse:
            ok = True
            status_code = 200
            def json(self):
                return {}
        return MockResponse()

    monkeypatch.setattr("requests.put", mock_put)

    response = client.put("/admin/restaurants/1", json={
        "name": "Updated Name",
        "cuisine": "Mexican",
        "location": "Toronto"
    })

    assert response.status_code == 200


# -------------------------
# Fetch Restaurants (DB Interface)
# -------------------------
def test_get_restaurants(client, monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            ok = True
            def json(self):
                return [{"id": 1, "name": "Pizza Place"}]
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

    response = client.get("/api/restaurants")
    assert response.status_code == 200


# -------------------------
# Owner Dashboard Requires Login
# -------------------------
def test_owner_dashboard_requires_login(client):
    response = client.get("/owner/dashboard")
    assert response.status_code == 302