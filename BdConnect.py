import sqlite3


class BdConnect:
    def __init__(self, bd_name):
        self.conn = sqlite3.connect(bd_name)
        self.cursor = self.conn.cursor()  # Создаем базовые объекты для работы

    def add_a_record(self, text_category, company, recipient, text_email):  # Функция добавления записи
        num_category = self.text_cat_to_num_cat(text_category)
        self.cursor.execute('''INSERT INTO main (category, company, recipient, email)
            VALUES(?, ?, ?, ?)''', (num_category, company, recipient, text_email))
        self.conn.commit()

    def text_cat_to_num_cat(self, text_category):  # Функция преобразования числового признака в категориальный
        # для записи в бд
        num_cat = list(self.cursor.execute('''SELECT id from categories
            WHERE title = ?''', (text_category.lower(),)))
        return num_cat[0][0]

    def commit(self):  # Функция коммита в бд
        self.conn.commit()

    def del_a_record(self, id):  # Функция удаления записи
        self.cursor.execute('''DELETE from main
            where id = ?''', (id,))
        self.conn.commit()

    def edit_a_record(self, id, col, value):  # Функция редактирования записи
        self.cursor.execute(f'''UPDATE main
                            SET {col} = ?
                            WHERE ID = ?''', (value, id))
        self.conn.commit()

    def close(self):  # Прекращение соединения с бд
        self.conn.close()
