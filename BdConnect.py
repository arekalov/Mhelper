import sqlite3


class BdConnect:
    def __init__(self, bd_name):
        self.conn = sqlite3.connect(bd_name)
        self.cursor = self.conn.cursor()

    def add_a_record(self, text_category, company, recipient, text_email=''):
        num_category = self.text_cat_to_num_cat(text_category)
        # bin_email =
        self.cursor.execute('''INSERT INTO main (category, company, recipient)
            VALUES(?, ?, ?)''', (num_category, company, recipient))
        self.conn.commit()

    def text_cat_to_num_cat(self, text_category):
        num_cat = self.cursor.execute('''SELECT id from categories
            WHERE title = ?''', (text_category.lower(),))
        return list(num_cat)[0][0]

    def text_em_to_bin_em(self, text_email_path):
        # to binary
        pass

    def commit(self):
        self.conn.commit()

bd = BdConnect('db.db')
bd.add_a_record('срочно', 'Licey', 'ArkashevVP', 'hgjhgyhg')
