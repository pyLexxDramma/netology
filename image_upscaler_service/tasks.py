import logging
import threading
import time

import cv2
import numpy as np
from cv2 import dnn_superres

from celery_config import celery

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

_super_res_model = None
_model_lock = threading.Lock()


def load_super_res_model(model_path: str = '/app/models/EDSR_x2.pb', model_name: str = "edsr", scale: int = 2):
    global _super_res_model
    with _model_lock:
        if _super_res_model is None:
            logging.info(f"Loading super resolution model from: {model_path}")
            try:
                scaler = dnn_superres.DnnSuperResImpl_create()
                scaler.readModel(model_path)
                scaler.setModel(model_name, scale)
                logging.info("Super resolution model loaded successfully.")
                _super_res_model = scaler
            except Exception as e:
                logging.error(f"Failed to load model {model_path}: {e}")
                raise
    return _super_res_model


@celery.task(bind=True)
def process_image_task(self, input_image_bytes: bytes, input_image_shape: tuple):
    try:
        logging.info("Starting image processing in memory...")

        self.update_state(state='PROGRESS', meta={'status': 'Loading model...', 'progress': 5})
        scaler = load_super_res_model()

        try:
            image_np = np.frombuffer(input_image_bytes, dtype=np.uint8)
            image = image_np.reshape(input_image_shape)
            logging.info(f"Image reconstructed successfully. Shape: {image.shape}")
        except Exception as e:
            error_msg = f"Could not reconstruct image from bytes: {e}"
            logging.error(error_msg)
            self.update_state(state='FAILURE', meta={'exc_type': 'ImageReconstructionError', 'exc_message': error_msg})
            return {'error': error_msg}

        self.update_state(state='PROGRESS', meta={'status': 'Image loaded.', 'progress': 15})
        time.sleep(1)

        logging.info(f"Starting upscaling...")
        result_np = scaler.upsample(image)
        logging.info(f"Upscaling complete. Result shape: {result_np.shape}")

        self.update_state(state='PROGRESS', meta={'status': 'Upscaling complete.', 'progress': 70})
        time.sleep(2)

        success, buffer = cv2.imencode('.jpg', result_np)
        if not success:
            raise IOError("Could not encode processed image to bytes.")

        processed_image_bytes = buffer.tobytes()
        logging.info(f"Processed image encoded successfully. Bytes length: {len(processed_image_bytes)}")

        self.update_state(state='SUCCESS', meta={'status': 'Image upscaled successfully',
                                                 'processed_image_bytes': len(processed_image_bytes)})
        logging.info("Task finished successfully.")
        return {'processed_image_bytes': processed_image_bytes}

    except FileNotFoundError as e:
        logging.error(f"File not found error: {e}")
        self.update_state(state='FAILURE', meta={'exc_type': 'FileNotFoundError', 'exc_message': str(e)})
        return {'error': str(e)}
    except IOError as e:
        logging.error(f"IO error: {e}")
        self.update_state(state='FAILURE', meta={'exc_type': 'IOError', 'exc_message': str(e)})
        return {'error': str(e)}
    except Exception as e:
        logging.exception("An unexpected error occurred during image processing:")
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        return {'error': str(e)}
