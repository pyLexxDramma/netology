import logging

import cv2
import numpy as np
from flask import Flask, request, jsonify, Response

from celery_config import celery
from tasks import process_image_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

tasks_in_progress = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upscale', methods=['POST'])
def upscale_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            input_image_bytes = file.read()
            image_np_temp = cv2.imdecode(np.frombuffer(input_image_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
            if image_np_temp is None:
                raise ValueError("Could not decode image data.")
            input_image_shape = image_np_temp.shape
            logging.info(f"Read image from request. Shape: {input_image_shape}")

            logging.info(f"Starting Celery task...")
            task = process_image_task.delay(input_image_bytes, input_image_shape)
            task_id = task.id
            tasks_in_progress[task_id] = {'state': 'PENDING'}

            return jsonify({'task_id': task_id}), 202

        except ValueError as e:
            logging.error(f"Error processing uploaded image: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logging.error(f"Error processing upload or starting task: {e}")
            return jsonify({'error': 'Failed to process upload or start task.'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is pending...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': task.info.get('status', 'In progress...'),
            'progress': task.info.get('progress', 0)
        }
    elif task.state == 'SUCCESS':
        result_data = task.info
        processed_image_bytes = result_data.get('processed_image_bytes')
        if processed_image_bytes:
            mime_type = 'image/jpeg'

            response = {
                'state': task.state,
                'status': 'Image upscaled successfully',
                'result': {
                    'message': 'Image is ready',
                    'mime_type': mime_type,
                    'image_size_bytes': len(processed_image_bytes)
                }
            }
            tasks_in_progress[task_id] = {'state': task.state, 'result_bytes': processed_image_bytes,
                                          'mime_type': mime_type}
        else:
            response = {
                'state': task.state,
                'status': 'Task finished, but no image data found in result.',
                'result': str(task.info)
            }

    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': 'Task failed.',
            'result': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': 'Unknown state.'
        }
    return jsonify(response)


@app.route('/image/<task_id>')
def get_processed_image(task_id):
    task_info = tasks_in_progress.get(task_id)
    if task_info and task_info['state'] == 'SUCCESS':
        processed_bytes = task_info.get('result_bytes')
        mime_type = task_info.get('mime_type', 'image/jpeg')

        if processed_bytes:
            return Response(processed_bytes, mimetype=mime_type)
        else:
            return jsonify({"error": "Processed image data not found"}), 500
    elif task_info and task_info['state'] == 'FAILURE':
        return jsonify({"error": "Task failed. Image not processed.", "details": task_info.get('result')}), 500
    else:
        return jsonify({"error": "Task not found or not completed successfully"}), 404
