import sys
import sqlite3
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QTableWidgetItem

from BdConnect import BdConnect
from Exceptions import FormatError, SenderError, RecipientError
from text_extractor import image_to_text, txt_to_text
from ner_model import ner_predict
from Classifier import get_category

bd = BdConnect('db.db')


class SeeMailWindow(QMainWindow):  # Класс окна для прссмотра бд с письмами
    def __init__(self):
        super(SeeMailWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        uic.loadUi('designs\\see_db.ui', self)
        self.find_btn.clicked.connect(self.load_table)

    def load_table(self):
        self.con = sqlite3.connect('db.db')
        self.cur = self.con.cursor()
        res = self.cur.execute(f'''SELECT * FROM main''')
        self.tableWidget.setColumnCount(5)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))


class AddMailDialog(QDialog):  # Класс диалогового окна для загрузки письма в бд
    def __init__(self):
        super(AddMailDialog, self).__init__()
        self.init_ui()

    def init_ui(self):  # Инициализация графических элементов
        uic.loadUi('designs\\dialog.ui', self)
        self.upload_btn.clicked.connect(self.upload)
        self.handle_btn.clicked.connect(self.handle)
        self.save_btn.clicked.connect(self.save)
        self.pixmap = QPixmap('system\\file_icon.png')

    def upload(self):  # Функция открытия диалога для выбора файла и отработка ошибок
        try:
            self.path_to_file = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '', 'Текст (*.txt);;'
                                                                                          'Картинка(*.png);;'
                                                                                          'Картинка (*.tif);;'
                                                                                          'Картинка (*.jpg);;'
                                                                                          'Все (*);')[0]
            self.check_correct_file(self.path_to_file)
            self.label_picture.setPixmap(self.pixmap)
            self.label_error.setText(f'Файл {self.path_to_file.split("/")[-1]} загружен')

            self.upload_btn.setEnabled(False)
            self.handle_btn.setEnabled(True)
        except FormatError:
            self.label_error.setText('Ошибка формата файла')
        except Exception as ex:
            print(ex)
            self.label_error.setText('Ошибка при загрузке файла')

    def check_correct_file(self, path):  # Проверка достоверности нахождения файла в директории
        # и проверка формата файла
        a = open(path, 'rb')  # Если файла не будет в директории выбросит ошибку, которую захватит обработчик
        extension = path.split('/')[-1].split('.')[-1]
        if extension not in ['jpg', 'tif', 'pdf', 'png', 'txt']:
            raise FormatError
        return extension

    def handle(self):
        self.string_text = self.upload_text(self.path_to_file)

        tags_and_tokens = ner_predict(self.string_text)
        if 'PERSON' in tags_and_tokens.keys():
            reciepment = tags_and_tokens['PERSON'][0]
        else:
            reciepment = 'Не найдено'
        if 'ORGANIZATION' in tags_and_tokens.keys():
            company = tags_and_tokens['ORGANIZATION'][-1]
        else:
            company = 'Не найдено'

        category_ind = get_category(self.string_text)
        if category_ind == '1' or category_ind == 1:
            self.category_cb.setCurrentIndex(2)
        elif category_ind == '0' or category_ind == 0:
            self.category_cb.setCurrentIndex(0)
        else:
            self.category_cb.setCurrentIndex(1)

        # Блокируется кнопка обработки и пользователь может изменить настройки вручную
        self.handle_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.recipient_line.setEnabled(True)
        self.category_cb.setEnabled(True)
        self.company_line.setEnabled(True)
        # Передаем к пользователю полученные моделью теги
        self.recipient_line.setText(reciepment)
        self.company_line.setText(company)
        # Если пользователь редактирует теги, то проверяем их корректность и временно блокируем кнопку сохранения
        self.recipient_line.textChanged.connect(self.block_save_btn)
        self.company_line.textChanged.connect(self.block_save_btn)

    def upload_text(self, filepath):
        if self.check_correct_file(self.path_to_file) != 'txt':  # Преобразование файла в текст
            text = image_to_text(filepath)
        else:
            text = txt_to_text(filepath)
        return text

    def block_save_btn(self):  # Проверка пользовательских тегов и блокировка кнопки сохранить
        self.save_btn.setEnabled(False)
        self.check_tegs()

    def check_tegs(self):  # Функция проверки тегов пользователя
        try:
            if self.recipient_line.text():
                for i in self.recipient_line.text():
                    if not i.isalpha():
                        raise RecipientError
            else:
                raise RecipientError
            if self.company_line.text():
                for i in self.company_line.text():
                    if not i.isalpha():
                        raise SenderError
            else:
                raise SenderError
            self.save_btn.setEnabled(True)
            self.label_tegs_error.setText('')
        except RecipientError:
            self.label_tegs_error.setText('Некорректный получатель')
        except SenderError:
            self.label_tegs_error.setText('Некорректный отправитель')
        except Exception as ex:
            print(ex)
            self.label_tegs_error.setText('Ошибка')

    def save(self):
        bd.add_a_record(self.category_cb.currentText(), self.company_line.text(), self.recipient_line.text())
        bd.commit()
        self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        uic.loadUi('designs\\main.ui', self)
        self.addmail_btn.clicked.connect(self.open_addmail_dialog)
        self.seemail_btn.clicked.connect(self.show_seemail_window)

    def open_addmail_dialog(self):
        self.addmaildialog = AddMailDialog()
        self.addmaildialog.show()

    def show_seemail_window(self):
        self.seemailwindow = SeeMailWindow()
        self.seemailwindow.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
