import os
import sys
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from jose import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.main import app, users, advertisements, next_id, next_user_id
from src.main import oauth2_scheme, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def mock_admin_user():
    admin_user = {
        "id": 1,
        "username": "admin",
        "password": "$2b$12$Eg..nTrcGEl.HG6OtnZQ5ekPWgK.Oz9YINk/ciyfuH6wJJN/MiJuS",
        "group": "admin",
        "created_at": datetime.now(),
        "updated_at": None
    }
    users.append(admin_user)
    return admin_user

@pytest.fixture(scope="module")
def mock_regular_user():
    regular_user = {
        "id": 2,
        "username": "user",
        "password": "$2b$12$.EXUaqIf.ZOon/bclSlNO.CfSdsXyOLMKQhyAIFpYsoBpsbuwHeHi",
        "group": "user",
        "created_at": datetime.now(),
        "updated_at": None
    }
    users.append(regular_user)
    return regular_user

@pytest.fixture(scope="module")
def generate_access_token():
    def inner_generate_access_token(username, group):
        now = datetime.utcnow()
        expiration_time = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": username,
            "group": group,
            "exp": expiration_time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return f"Bearer {token}"
    return inner_generate_access_token