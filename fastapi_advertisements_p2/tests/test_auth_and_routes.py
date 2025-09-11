import pytest
from fastapi import status
from datetime import datetime, timedelta
from jose import jwt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.main import app, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, User, Advertisement, UserCreate, users, \
    next_user_id, next_id, initialize_users, find_user_by_username, advertisements
from src.main import oauth2_scheme
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def generate_access_token():
    def inner_generate_access_token(username, group):
        now = datetime.utcnow()
        expiration_time = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "username": username,
            "group": group,
            "exp": expiration_time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    return inner_generate_access_token


@pytest.fixture(scope="function", autouse=True)
def reset_global_state():
    users.clear()
    advertisements.clear()

    from src.main import next_user_id as main_next_user_id, next_id as main_next_id

    main_next_user_id = 1
    main_next_id = 1

    initialize_users()

    yield

    users.clear()
    advertisements.clear()
    main_next_user_id = 1
    main_next_id = 1


@pytest.fixture(scope="function")
def get_user_from_system():
    user = None
    for u in users:
        if u.username == "user":
            user = u
            break
    if not user:
        pytest.fail("User 'user' not found.")
    return user


@pytest.fixture(scope="function")
def get_admin_user_from_system():
    admin_user = None
    for u in users:
        if u.username == "admin":
            admin_user = u
            break
    if not admin_user:
        pytest.fail("Admin user not found.")
    return admin_user


@pytest.fixture(scope="function")
def create_test_advertisement(client, generate_access_token, get_user_from_system):
    token = generate_access_token(get_user_from_system.username, get_user_from_system.group)
    headers = {"Authorization": f"Bearer {token}"}
    new_advertisement = {
        "title": "Test Ad",
        "description": "This is a test advert.",
        "price": 123.45,
    }
    response = client.post("/advertisement/", json=new_advertisement, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED, f"Failed to create test advertisement: {response.text}"
    ad_id = response.json()["id"]
    return ad_id, token


def test_login_success(client):
    form_data = {"username": "admin", "password": "adminpass"}
    response = client.post("/login", data=form_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_fail(client):
    form_data = {"username": "admin", "password": "wrongpass"}
    response = client.post("/login", data=form_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user(client, generate_access_token, get_admin_user_from_system):
    token = generate_access_token(get_admin_user_from_system.username, get_admin_user_from_system.group)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/user/{get_admin_user_from_system.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == get_admin_user_from_system.username


def test_patch_user_self(client, generate_access_token, get_user_from_system):
    token = generate_access_token(get_user_from_system.username, get_user_from_system.group)
    headers = {"Authorization": f"Bearer {token}"}
    patch_data = UserCreate(username="patcheduser", password="userpass", group="user")
    response = client.patch(f"/user/{get_user_from_system.id}", json=patch_data.dict(), headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "patcheduser"


def test_patch_user_unauthorized(client, generate_access_token):
    token = generate_access_token("otheruser", "user")
    headers = {"Authorization": f"Bearer {token}"}
    patch_data = UserCreate(username="shouldnotwork", password="somepassword", group="user")

    regular_user_id = None
    for u in users:
        if u.username == "user":
            regular_user_id = u.id
            break
    if not regular_user_id:
        pytest.fail("Regular user not found for unauthorized patch test.")

    response = client.patch(f"/user/{regular_user_id}", json=patch_data.dict(), headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_user_self(client, generate_access_token, get_user_from_system):
    token = generate_access_token(get_user_from_system.username, get_user_from_system.group)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/user/{get_user_from_system.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User deleted"


def test_delete_user_unauthorized(client, generate_access_token):
    regular_user_id = None
    for u in users:
        if u.username == "user":
            regular_user_id = u.id
            break
    if not regular_user_id:
        pytest.fail("Regular user not found for unauthorized delete test.")

    token = generate_access_token("someuser", "user")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/user/{regular_user_id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_advertisement(client, generate_access_token, get_user_from_system):
    token = generate_access_token(get_user_from_system.username, get_user_from_system.group)
    headers = {"Authorization": f"Bearer {token}"}
    new_advertisement = Advertisement(
        title="New Ad",
        description="This is an advert.",
        price=100.0,
        id=0,
        author_id=0
    )
    response = client.post("/advertisement/",
                           json=new_advertisement.dict(exclude={'id', 'author_id', 'created_at', 'updated_at'}),
                           headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == "New Ad"
    assert response.json()["author_id"] is not None


def test_get_advertisement(client, create_test_advertisement):
    ad_id, token = create_test_advertisement
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/advertisement/{ad_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test Ad"
    assert response.json()["author_id"] is not None


def test_patch_advertisement_own(client, create_test_advertisement):
    ad_id, token = create_test_advertisement
    headers = {"Authorization": f"Bearer {token}"}
    patch_data = Advertisement(
        title="Updated Title",
        description="Updated description",
        price=150.0,
        author_id=0,
        id=0
    )
    response = client.patch(f"/advertisement/{ad_id}", json=patch_data.dict(exclude_unset=True), headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Title"
    assert response.json()["price"] == 150.0
    assert response.json()["author_id"] is not None


def test_patch_advertisement_not_authorized(client, generate_access_token, create_test_advertisement):
    ad_id, _ = create_test_advertisement
    token = generate_access_token("someoneelse", "user")
    headers = {"Authorization": f"Bearer {token}"}
    patch_data = Advertisement(title="Should Not Work", price=200.0, description="...", author_id=0, id=0)
    response = client.patch(f"/advertisement/{ad_id}", json=patch_data.dict(exclude_unset=True), headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_advertisement_own(client, create_test_advertisement):
    ad_id, token = create_test_advertisement
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/advertisement/{ad_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Advertisement deleted"


def test_delete_advertisement_not_authorized(client, create_test_advertisement, generate_access_token):
    ad_id, _ = create_test_advertisement
    token = generate_access_token("anotheruser", "user")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/advertisement/{ad_id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN