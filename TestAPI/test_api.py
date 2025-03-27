import logging
import unittest

import requests


class TestYandexDiskAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(filename='test_yandex_disk_api.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            encoding='utf-8')

        self.token = "y0__wgBEI3O_k0YmrQ0ILjz4oMSpwBGF7hyPaIj2YjYv_8cIe1O918"
        if not self.token:
            raise ValueError("Необходимо установить переменную окружения YANDEX_DISK_TOKEN с вашим токеном.")
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {"Authorization": f"OAuth {self.token}"}
        self.test_folder_name = "test_folder"

    def tearDown(self):
        self.delete_folder(self.test_folder_name)

    def create_folder(self, path):
        params = {"path": path}
        response = requests.put(self.base_url, headers=self.headers, params=params)
        logging.info(f"Создание папки: {path}, Статус: {response.status_code}, Response: {response.text}")
        return response

    def check_folder_exists(self, path):
        params = {"path": path}
        response = requests.get(self.base_url, headers=self.headers, params=params)
        logging.info(f"Проверка существования папки: {path}, Статус: {response.status_code}")
        return response.status_code == 200

    def delete_folder(self, path):
        params = {"path": path, "permanently": "true"}
        response = requests.delete(self.base_url, headers=self.headers, params=params)
        logging.info(f"Удаление папки: {path}, Статус: {response.status_code}")
        return response

    def test_create_folder_success(self):
        response = self.create_folder(self.test_folder_name)
        self.assertEqual(response.status_code, 201,
                         f"Ожидался код 201, получен {response.status_code}.  Response: {response.text}")
        self.assertTrue(self.check_folder_exists(self.test_folder_name), "Папка не была создана.")

    def test_create_folder_already_exists(self):
        if self.check_folder_exists(self.test_folder_name):
            self.delete_folder(self.test_folder_name)

        create_response = self.create_folder(self.test_folder_name)
        self.assertEqual(create_response.status_code, 201, "Не удалось создать тестовую папку для негативного теста.")

        response = self.create_folder(self.test_folder_name)
        self.assertEqual(response.status_code, 409,
                         f"Ожидался код 409, получен {response.status_code}. Response: {response.text}")

    def test_create_folder_invalid_token(self):
        invalid_headers = {"Authorization": "OAuth invalid_token"}
        params = {"path": self.test_folder_name}
        response = requests.put(self.base_url, headers=invalid_headers, params=params)
        logging.info(f"Тест с недействительным токеном, Статус: {response.status_code}, Response: {response.text}")
        self.assertEqual(response.status_code, 401,
                         f"Ожидался код 401, получен {response.status_code}. Response: {response.text}")

    def test_create_folder_invalid_path(self):
        invalid_path = "very_long_path_" * 100
        response = self.create_folder(invalid_path)
        logging.info(f"Тест с недействительным путем, Статус: {response.status_code}, Response: {response.text}")
        self.assertTrue(400 <= response.status_code < 600,
                        f"Ожидался код ошибки (400-599), получен {response.status_code}. Response: {response.text}")


if __name__ == '__main__':
    unittest.main()
