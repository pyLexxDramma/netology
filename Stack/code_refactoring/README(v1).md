# Класс EmailClient
Вся логика работы с почтой теперь инкапсулирована в этом классе.

## Методы send_email и receive_email
Эти методы принимают необходимые параметры, такие как subject, recipients и message, что позволяет избежать захардкоженных значений.

## Использование with для управления контекстом
Это позволяет автоматически закрывать соединения, что является хорошей практикой.

## Стандарт PEP8
Все переменные и методы теперь соответствуют стандартам именования PEP8.

## Обработка исключений
Добавлена обработка исключений при получении писем, чтобы избежать сбоев в программе.
