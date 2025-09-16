import os
from unittest.mock import patch, MagicMock

import cv2
import numpy as np
import pytest
from flask.testing import FlaskClient

import app

TEST_IMAGE_PATH = 'tests/test_image.png'
TEST_IMAGE_BYTES = None
TEST_IMAGE_SHAPE = None


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    if not os.path.exists('tests'):
        os.makedirs('tests')
    if not os.path.exists(TEST_IMAGE_PATH):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:, :, 0] = 255
        cv2.imwrite(TEST_IMAGE_PATH, img)

    global TEST_IMAGE_BYTES, TEST_IMAGE_SHAPE
    with open(TEST_IMAGE_PATH, 'rb') as f:
        TEST_IMAGE_BYTES = f.read()

    img_np_temp = cv2.imdecode(np.frombuffer(TEST_IMAGE_BYTES, np.uint8), cv2.IMREAD_UNCHANGED)
    if img_np_temp is None:
        raise ValueError("Could not decode test image for API tests.")
    TEST_IMAGE_SHAPE = img_np_temp.shape

    with app.app_context():
        app.tasks_in_progress.clear()

    yield


@pytest.fixture
def flask_app():
    """Создает тестовый клиент Flask."""
    app.config['TESTING'] = True
    with app.app_context():
        yield app.test_client()


@pytest.fixture
def mock_celery_task():
    """Мокирует Celery задачу."""
    with patch('app.process_image_task') as mock_task:
        mock_result = MagicMock()
        mock_result.id = "test_task_id_123"
        mock_result.state = 'SUCCESS'
        mock_result.info = {
            'status': 'Image upscaled successfully',
            'processed_image_bytes': b'\x89PNG\r\n\x1a\n...',
            'mime_type': 'image/png'
        }
        mock_task.delay.return_value = mock_result
        yield mock_task, mock_result


def test_upscale_image_success(flask_app: FlaskClient, mock_celery_task):
    mock_task, mock_result = mock_celery_task

    with open(TEST_IMAGE_PATH, 'rb') as f:
        files = {'file': (os.path.basename(TEST_IMAGE_PATH), f)}
        response = flask_app.post('/upscale', files=files)

    assert response.status_code == 202
    assert response.content_type == 'application/json'
    data = response.json
    assert 'task_id' in data
    assert data['task_id'] == mock_result.id

    mock_task.delay.assert_called_once()
    call_args, call_kwargs = mock_task.delay.call_args
    assert isinstance(call_args[0], bytes)
    assert call_args[0] == TEST_IMAGE_BYTES
    assert isinstance(call_args[1], tuple)
    assert call_args[1] == TEST_IMAGE_SHAPE


def test_upscale_image_no_file(flask_app: FlaskClient):
    response = flask_app.post('/upscale')
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    assert 'error' in response.json
    assert 'No file part' in response.json['error']


def test_upscale_image_empty_file(flask_app: FlaskClient):
    from io import BytesIO
    files = {'file': ('empty.png', BytesIO(b''))}
    response = flask_app.post('/upscale', files=files)
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    assert 'error' in response.json
    assert 'No selected file' in response.json['error']


def test_upscale_image_invalid_file_type(flask_app: FlaskClient):
    from io import BytesIO
    files = {'file': ('document.txt', BytesIO(b'some text'))}
    response = flask_app.post('/upscale', files=files)
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    assert 'error' in response.json
    assert 'Invalid file type' in response.json['error']


def test_get_task_status_success(flask_app: FlaskClient, mock_celery_task):
    mock_task, mock_result = mock_celery_task
    mock_result.info = {
        'status': 'Image upscaled successfully',
        'processed_image_bytes': b'\x89PNG\r\n\x1a\n...',
        'mime_type': 'image/png'
    }

    task_id = mock_result.id
    app.tasks_in_progress[task_id] = {
        'state': 'SUCCESS',
        'result_bytes': b'fake_image_bytes_for_api',
        'mime_type': 'image/png'
    }

    response = flask_app.get(f'/tasks/{task_id}')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = response.json
    assert data['state'] == 'SUCCESS'
    assert 'result' in data
    assert 'file_url' in data['result']
    assert data['result']['file_url'] == f'/image/{task_id}'
    assert data['result']['mime_type'] == 'image/png'


def test_get_task_status_pending(flask_app: FlaskClient, mock_celery_task):
    mock_task, mock_result = mock_celery_task
    mock_result.state = 'PENDING'
    mock_result.info = 'Task is pending...'

    task_id = mock_result.id

    response = flask_app.get(f'/tasks/{task_id}')
    assert response.status_code == 200
    data = response.json
    assert data['state'] == 'PENDING'
    assert data['status'] == 'Task is pending...'


def test_get_task_status_failure(flask_app: FlaskClient, mock_celery_task):
    mock_task, mock_result = mock_celery_task
    mock_result.state = 'FAILURE'
    mock_result.info = 'This is a fake failure message.'

    task_id = mock_result.id

    response = flask_app.get(f'/tasks/{task_id}')
    assert response.status_code == 200
    data = response.json
    assert data['state'] == 'FAILURE'
    assert 'result' in data
    assert data['result'] == 'This is a fake failure message.'


def test_get_processed_image(flask_app: FlaskClient):
    task_id = "test_task_for_image_download"
    fake_image_bytes = b'\x89PNG\r\n\x1a\n...'
    fake_mime_type = 'image/png'

    app.tasks_in_progress[task_id] = {
        'state': 'SUCCESS',
        'result_bytes': fake_image_bytes,
        'mime_type': fake_mime_type
    }

    response = flask_app.get(f'/image/{task_id}')
    assert response.status_code == 200
    assert response.content_type == fake_mime_type
    assert response.data == fake_image_bytes


def test_get_processed_image_not_found(flask_app: FlaskClient):
    response = flask_app.get('/image/non_existent_task_id')
    assert response.status_code == 404
    assert response.content_type == 'application/json'
    assert 'error' in response.json
    assert 'Task not found' in response.json['error']


def test_get_processed_image_task_failed(flask_app: FlaskClient):
    task_id = "failed_task_id"
    app.tasks_in_progress[task_id] = {
        'state': 'FAILURE',
        'result': 'Fake error message'
    }
    response = flask_app.get(f'/image/{task_id}')
    assert response.status_code == 500
    assert response.content_type == 'application/json'
    assert 'error' in response.json
    assert 'Task failed' in response.json['error']
