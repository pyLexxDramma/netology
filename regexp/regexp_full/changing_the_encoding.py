import chardet
import codecs

with open('phonebook_raw.csv', 'rb') as f:
    raw_data = f.read()
    result = chardet.detect(raw_data)
    source_encoding = result['encoding']
    print(f"Предполагаемая кодировка: {source_encoding}")

target_encoding = 'utf-8'

try:
    with codecs.open('phonebook_raw.csv', 'r', encoding=source_encoding) as source_file:
        content = source_file.read()

    with codecs.open('phonebook_raw.csv', 'w', encoding=target_encoding) as target_file:
        target_file.write(content)
    print("Файл успешно преобразован в UTF-8")

except UnicodeDecodeError as e:
    print(f"Не удалось декодировать файл с кодировкой {source_encoding}: {e}")
    print("Попробуйте errors='replace' или errors='ignore'")

except Exception as e:
    print(f"Произошла другая ошибка: {e}")