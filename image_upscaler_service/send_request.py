import os
import sys
import time

import requests


def send_upscale_request(image_path: str, url: str):
    try:
        with open(image_path, 'rb') as f:
            filename = os.path.basename(image_path)
            files = {'file': (filename, f)}
            response = requests.post(url, files=files)
            response.raise_for_status()
            return response.json()
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None


def get_task_status(task_id: str, status_url: str):
    try:
        response = requests.get(status_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting task status for {task_id}: {e}")
        return None


def download_file(file_url: str, download_dir: str = "."):
    try:
        filename = file_url.split('/')[-1]
        full_url = f"{server_address}{file_url.lstrip('/')}"

        response = requests.get(full_url, stream=True)
        response.raise_for_status()

        os.makedirs(download_dir, exist_ok=True)
        save_path = os.path.join(download_dir, filename)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded successfully to: {save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file from {file_url}: {e}")
        return None
    except Exception as e:
        print(f"Error saving file: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python send_request.py <path_to_image> <api_url>")
        sys.exit(1)

    image_path = sys.argv[1]
    api_url = sys.argv[2]

    server_address = "/".join(api_url.split('/')[:-1])
    if not server_address.endswith('/'):
        server_address += '/'

    print(f"Sending image: {image_path} to {api_url}...")
    upscale_response = send_upscale_request(image_path, api_url)

    if upscale_response and 'task_id' in upscale_response:
        task_id = upscale_response['task_id']
        print(f"Task ID received: {task_id}")

        status_url = f"{server_address}tasks/{task_id}"
        print(f"Checking task status at: {status_url}")

        task_status_data = None
        for _ in range(30):
            task_status_data = get_task_status(task_id, status_url)
            if task_status_data:
                print(f"Current status: {task_status_data.get('state')}")
                if task_status_data.get('state') == 'SUCCESS':
                    print("Task completed successfully!")
                    break
                elif task_status_data.get('state') == 'FAILURE':
                    print(f"Task failed: {task_status_data.get('result')}")
                    break
                elif task_status_data.get('state') == 'PENDING' or task_status_data.get('state') == 'PROGRESS':
                    time.sleep(2)
            else:
                print("Failed to get task status, stopping.")
                break
        else:
            print("Task did not complete within the allowed time.")

        if task_status_data and task_status_data.get('state') == 'SUCCESS':
            result_info = task_status_data.get('result')
            if result_info and 'file_url' in result_info:
                file_url = result_info['file_url']
                print(f"Downloading processed file from: {file_url}")
                download_file(file_url, download_dir="downloaded_files")
            else:
                print("Task completed, but no file URL found in the result.")

    else:
        print("Failed to get task ID. Cannot proceed with status check or download.")
