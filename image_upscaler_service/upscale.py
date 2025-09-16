import threading

import cv2
import numpy as np
from cv2 import dnn_superres

_super_res_model = None
_model_lock = threading.Lock()


def load_super_res_model(model_path: str = 'models/EDSR_x2.pb', model_name: str = "edsr", scale: int = 2):
    global _super_res_model
    with _model_lock:
        if _super_res_model is None:
            print(f"Загрузка модели: {model_path}...")
            scaler = dnn_superres.DnnSuperResImpl_create()
            scaler.readModel(model_path)
            scaler.setModel(model_name, scale)
            _super_res_model = scaler
            print("Модель успешно загружена и кеширована.")
    return _super_res_model


def upscale(input_image: np.ndarray, model_path: str = 'models/EDSR_x2.pb') -> np.ndarray:
    scaler = load_super_res_model(model_path=model_path)
    result = scaler.upsample(input_image)
    return result


def example():
    input_image_path = 'data/lama_300px.png'
    output_image_path = 'data/lama_600px.png'
    model_path = 'models/EDSR_x2.pb'

    load_super_res_model(model_path=model_path)

    image = cv2.imread(input_image_path)
    if image is None:
        print(f"Ошибка: Не удалось загрузить изображение из {input_image_path}")
        return

    print(f"Апскейлинг изображения: {input_image_path}")
    result = upscale(image, model_path=model_path)
    cv2.imwrite(output_image_path, result)
    print(f"Результат сохранен в: {output_image_path}")


if __name__ == '__main__':
    example()
