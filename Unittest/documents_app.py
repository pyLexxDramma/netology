import os
import datetime
import csv

DOCUMENTS = [
    {"type": "passport", "number": "2207 876234", "name": "Василий Гупкин"},
    {"type": "invoice", "number": "11-2", "name": "Геннадий Покемонов"},
    {"type": "insurance", "number": "10006", "name": "Аристарх Павлов"}
]

DIRECTORIES = {
    '1': ['2207 876234', '11-2', '5455 028765'],
    '2': ['10006'],
    '3': []
}

def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            now = datetime.datetime.now()
            function_name = old_function.__name__
            arguments = f"args: {args}, kwargs: {kwargs}"
            try:
                result = old_function(*args, **kwargs)
            except Exception as e:
                result = f"Exception: {e}"
                raise
            finally:
                with open(path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"Date and time: {now}\n")
                    log_file.write(f"Function name: {function_name}\n")
                    log_file.write(f"Arguments: {arguments}\n")
                    log_file.write(f"Return value: {result}\n")
                    log_file.write("---------------------\n")
            return result
        return new_function
    return __logger

@logger("documents.log")
def check_document_existance(documents, user_doc_number):
    for document in documents:
        if document['number'] == user_doc_number:
            return True
    return False

@logger("documents.log")
def get_doc_owner_name(documents, user_doc_number):
    if check_document_existance(documents, user_doc_number):
        for document in documents:
            if document['number'] == user_doc_number:
                return document['name']
    return None

@logger("documents.log")
def get_all_doc_owners_names(documents):
    owners = set()
    for document in documents:
        owners.add(document['name'])
    return owners

@logger("documents.log")
def remove_doc_from_shelf(directories, doc_number):
    for shelf, doc_list in directories.items():
        if doc_number in doc_list:
            doc_list.remove(doc_number)
            return True
    return False

@logger("documents.log")
def add_new_shelf(directories, shelf_number):
    if shelf_number not in directories:
        directories[shelf_number] = []
        return True
    return False

@logger("documents.log")
def append_doc_to_shelf(directories, doc_number, shelf_number):
    if add_new_shelf(directories, shelf_number):
        directories[shelf_number] = []
    if shelf_number in directories:
        directories[shelf_number].append(doc_number)
        return True
    return False

@logger("documents.log")
def delete_doc(documents, directories, user_doc_number):
    if check_document_existance(documents, user_doc_number):
        for document in documents[:]:
            if document['number'] == user_doc_number:
                documents.remove(document)
                remove_doc_from_shelf(directories, user_doc_number)
                return True
    return False

@logger("documents.log")
def get_doc_shelf(documents, directories, user_doc_number):
    if check_document_existance(documents, user_doc_number):
        for shelf, doc_list in directories.items():
            if user_doc_number in doc_list:
                return shelf
    return None

@logger("documents.log")
def move_doc_to_shelf(documents, directories, user_doc_number, user_shelf_number):
    if delete_doc(documents, directories, user_doc_number):
        append_doc_to_shelf(directories, user_doc_number, user_shelf_number)
        return True
    return False

@logger("documents.log")
def show_document_info(document):
    print(f"{document['type']} \"{document['number']}\" \"{document['name']}\"")

@logger("documents.log")
def show_all_docs_info(documents):
    for document in documents:
        show_document_info(document)

@logger("documents.log")
def add_new_doc(documents):
    new_doc_number = input('Введите номер документа - ')
    new_doc_type = input('Введите тип документа - ')
    new_doc_owner_name = input('Введите имя владельца документа - ')
    new_doc_shelf_number = input('Введите номер полки для хранения - ')
    new_doc = {
        "type": new_doc_type,
        "number": new_doc_number,
        "name": new_doc_owner_name,
    }
    documents.append(new_doc)
    append_doc_to_shelf(DIRECTORIES, new_doc_number, new_doc_shelf_number)
    return new_doc_shelf_number

def secretary_program_start():
    print(
        'Вас приветствует программа помошник!\n',
        '(Введите help, для просмотра списка поддерживаемых команд)\n'
    )
    while True:
        user_command = input('Введите команду - ')
        if user_command == 'p':
            user_doc_number = input('Введите номер документа - ')
            owner_name = get_doc_owner_name(DOCUMENTS, user_doc_number)
            if owner_name:
                print('Владелец документа - {}'.format(owner_name))
            else:
                print('Документ не найден.')
        elif user_command == 'ap':
            uniq_users = get_all_doc_owners_names(DOCUMENTS)
            print('Список владельцев документов - {}'.format(uniq_users))
        elif user_command == 'l':
            show_all_docs_info(DOCUMENTS)
        elif user_command == 's':
            user_doc_number = input('Введите номер документа - ')
            directory_number = get_doc_shelf(DOCUMENTS, DIRECTORIES, user_doc_number)
            if directory_number:
                print('Документ находится на полке номер {}'.format(directory_number))
            else:
                print('Документ не найден.')
        elif user_command == 'a':
            print('Добавление нового документа:')
            new_doc_shelf_number = add_new_doc(DOCUMENTS)
            print('\nНа полку "{}" добавлен новый документ:'.format(new_doc_shelf_number))
        elif user_command == 'd':
            user_doc_number = input('Введите номер документа для удаления - ')
            deleted = delete_doc(DOCUMENTS, DIRECTORIES, user_doc_number)
            if deleted:
                print('Документ с номером "{}" был успешно удален'.format(user_doc_number))
            else:
                print('Документ не найден для удаления.')
        elif user_command == 'm':
            move_doc_to_shelf(DOCUMENTS, DIRECTORIES, input('Введите номер документа - '), input('Введите номер полки для перемещения - '))
        elif user_command == 'as':
            shelf_number = input('Введите номер новой полки - ')
            if add_new_shelf(DIRECTORIES, shelf_number):
                print('Добавлена полка "{}"'.format(shelf_number))
            else:
                print('Полка "{}" уже существует.'.format(shelf_number))
        elif user_command == 'help':
            print(secretary_program_start.__doc__)
        elif user_command == 'q':
            break

if __name__ == '__main__':
    secretary_program_start()