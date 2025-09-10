import pytest
from fastapi.testclient import TestClient
from src.main import app, advertisements, next_id
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_create_advertisement(client):
    data = {
        'title': 'Продаю автомобиль',
        'description': 'Машина в отличном состоянии!',
        'price': 100_000.0,
        'author': 'Александр Петров'
    }
    response = client.post('/advertisement/', json=data)
    assert response.status_code == 200
    result = response.json()
    assert result['id'] > 0
    assert result['created_at']
    assert result['updated_at'] is None
    assert len(advertisements) >= 1
    assert any(ad.id == result['id'] for ad in advertisements)

def test_read_advertisement(client):
    existing_ad = advertisements[-1]
    response = client.get(f'/advertisement/{existing_ad.id}')
    assert response.status_code == 200
    result = response.json()
    assert result['id'] == existing_ad.id
    assert result['title'] == existing_ad.title
    assert result['description'] == existing_ad.description
    assert result['price'] == existing_ad.price
    assert result['author'] == existing_ad.author

def test_update_advertisement(client):
    existing_ad = advertisements[-1]
    new_data = {'title': 'Продаю дом'}
    response = client.patch(f'/advertisement/{existing_ad.id}', json=new_data)
    assert response.status_code == 200
    result = response.json()
    assert result['title'] == new_data['title']
    assert result['updated_at'] != existing_ad.updated_at

def test_delete_advertisement(client):
    existing_ad = advertisements[-1]
    response = client.delete(f'/advertisement/{existing_ad.id}')
    assert response.status_code == 200
    assert len([ad for ad in advertisements if ad.id == existing_ad.id]) == 0

def test_search_advertisements(client):
    params = {'title': 'автомобиль'}
    response = client.get('/advertisement/', params=params)
    assert response.status_code == 200
    results = response.json()
    assert all('автомобиль' in ad['title'].lower() for ad in results)