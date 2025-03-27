import unittest
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class YandexPhoneAuthTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://passport.yandex.ru/auth/")

    def test_auth_via_phone(self):
        driver = self.driver

        try:
            # 1. Ввод номера телефона
            phone_field = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.NAME, "login"))
            )
            phone_field.send_keys("ваш_номер_телефона")  # Замените на ваш номер!
            phone_field.send_keys(Keys.RETURN)

            # 2. Ожидание и ввод кода из SMS
            time.sleep(random.uniform(3, 5))  # Небольшая задержка перед ожиданием кода

            code_field = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.NAME, "code"))
            )

            sms_code = input("Введите код из SMS и нажмите Enter: ")
            code_field.send_keys(sms_code)
            code_field.send_keys(Keys.RETURN)

            # 3. Проверка успешной авторизации
            WebDriverWait(driver, 20).until(
                EC.title_contains("Яндекс")
            )

            self.assertIn("Яндекс", driver.title)

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            self.fail("Тест не прошел из-за ошибки")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()