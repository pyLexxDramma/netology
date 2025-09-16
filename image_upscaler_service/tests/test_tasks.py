import os
from unittest.mock import patch, MagicMock

import cv2
import numpy as np
import pytest

from tasks import process_image_task, load_super_res_model

TEST_MODEL_PATH = 'models/EDSR_x2.pb'


def create_test_image(filepath='tests/test_image.png', width=100, height=100):
    if not os.path.exists('tests'):
        os.makedirs('tests')
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :, 0] = 255
    cv2.imwrite(filepath, img)
    print(f"Created test image: {filepath}")


def get_image_bytes(filepath):
    with open(filepath, 'rb') as f:
        return f.read()


def get_image_shape(image_bytes):
    img_np = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Could not decode image data.")
    return img.shape


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment(TEST_IMAGE_PATH=None):
    if not os.path.exists('tests'):
        os.makedirs('tests')
    create_test_image(TEST_IMAGE_PATH)
    yield


@pytest.fixture
def mock_load_model():
    with patch('tasks.dnn_superres.DnnSuperResImpl_create') as mock_create:
        mock_scaler = MagicMock()
        mock_create.return_value = mock_scaler
        mock_scaler.upsample.side_effect = lambda img: cv2.resize(img, (img.shape[1] * 2, img.shape[0] * 2),
                                                                  interpolation=cv2.INTER_LINEAR)
        yield mock_create


@pytest.fixture
def celery_task_eager():
    from tasks import celery as celery_app
    celery_app.conf.update(task_always_eager=True, task_eager_propagate=True)
    yield
    celery_app.conf.update(task_always_eager=False, task_eager_propagate=False)


def test_load_super_res_model(mock_load_model):
    model_path = TEST_MODEL_PATH
    model_name = "edsr"
    scale = 2

    scaler = load_super_res_model(model_path=model_path, model_name=model_name, scale=scale)

    mock_load_model.assert_called_once()
    scaler_instance = mock_load_model.return_value
    scaler_instance.readModel.assert_called_once_with(model_path)
    scaler_instance.setModel.assert_called_once_with(model_name, scale)
    assert scaler is scaler_instance


def test_process_image_task_success(celery_task_eager, mock_load_model, result_data=None, TEST_IMAGE_PATH=None):
    input_image_path = TEST_IMAGE_PATH
    input_image_bytes = get_image_bytes(input_image_path)
    input_image_shape = get_image_shape(input_image_bytes)

    result = process_image_task.delay(input_image_bytes, input_image_shape)

    assert result.state == 'SUCCESS'

    assert 'processed_image_bytes' in result_data
    assert isinstance(result_data['processed_image_bytes'], bytes)
    assert len(result_data['processed_image_bytes']) > 0

    processed_bytes = result_data['processed_image_bytes']
    processed_shape = get_image_shape(processed_bytes)
    assert processed_shape[0] > input_image_shape[0]
    assert processed_shape[1] > input_image_shape[1]


def test_process_image_task_invalid_image(celery_task_eager, mock_load_model):
    invalid_bytes = b"not_an_image"
    invalid_shape = (100, 100, 3)

    result = process_image_task.delay(invalid_bytes, invalid_shape)

    assert result.state == 'FAILURE'
    result_data = result.get()
    assert 'error' in result_data
    assert "Could not reconstruct image from bytes" in result_data['error']


def test_process_image_task_model_loading_error(celery_task_eager, TEST_IMAGE_PATH=None):
    with patch('tasks.load_super_res_model', side_effect=Exception("Failed to load model")) as mock_load:
        input_image_path = TEST_IMAGE_PATH
        input_image_bytes = get_image_bytes(input_image_path)
        input_image_shape = get_image_shape(input_image_bytes)

        result = process_image_task.delay(input_image_bytes, input_image_shape)

        assert result.state == 'FAILURE'
        result_data = result.get()
        assert 'error' in result_data
        assert "Failed to load model" in result_data['error']
