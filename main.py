import sys
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QTableWidgetItem

from BdConnect import BdConnect
from Exceptions import FormatError, SenderError, RecipientError
from text_extractor import image_to_text, txt_to_text
from ner_model import ner_predict
import Classificator

bd = BdConnect('db.db')  # Объект работы с базой данных, через который проходят


# все манипуляции, создан чтобы база данных не блокировалась


class SeeEmailText(QMainWindow):  # Класс просмтора текста письма внутри класса SeeMailWindow
    def __init__(self, text, title):
        super(SeeEmailText, self).__init__()
        self.init_ui(text, title)

    def init_ui(self, text, title):
        uic.loadUi('designs\\see_email.ui', self)
        self.plainTextEdit.setPlainText(text)  # Передача текста письма в виджет просмотра текста
        self.setWindowTitle(title)


class SeeMailWindow(QMainWindow):  # Класс окна для прссмотра бд с письмами
    def __init__(self):
        super(SeeMailWindow, self).__init__()
        self.init_ui()

    def init_ui(self):  # Инициализация графических элементов
        uic.loadUi('designs\\see_db.ui', self)
        self.load_table()
        self.tableWidget.cellPressed.connect(self.unblock_btns)
        self.find_btn.clicked.connect(self.find_in_bd)
        self.see_btn.clicked.connect(self.see_mail)
        self.del_btn.clicked.connect(self.del_mail)
        self.tableWidget.itemChanged.connect(self.item_changed)  # Подключение сигнала при измененении файлов в бд

    def load_table(self, sender='', recipient='', category=''):  # Функция загрузки таблицы и фыильтрации,
        # по умолчанию фильтров нет
        self.tableWidget.clear()  # Очистка таблицы от старых данных
        self.tableWidget.setRowCount(0)  # Очистка количества записей в таблице

        self.res = list(bd.cursor.execute(f'''SELECT main.ID, title, company, recipient, email
                                    FROM main
                                    LEFT JOIN categories ON main.category = categories.id
                                    '''))  # Общий запрос извлечения всех данных из бд

        if sender:  # Фильтрация по отправителю
            self.res = list(filter(lambda x: x[2].lower().startswith(sender.lower()), self.res))
        if recipient:  # Фильтрация по получателю
            self.res = list(filter(lambda x: x[3].lower().startswith(recipient.lower()), self.res))
        if category and category != 'Все':  # Фильтрация по категории
            self.res = list(filter(lambda x: x[1].lower() == category.lower(), self.res))
        if self.res:  # Заполнение таблицы данными
            self.tableWidget.setColumnCount(5)
            for i, row in enumerate(self.res):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(elem)))
            self.tableWidget.resizeColumnsToContents()
            # Установка заголовков
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Категория', 'Компания', 'Получатель', 'Письмо'])

    def unblock_btns(self):  # Функция разблокировки кнопок удаления/чтения
        self.see_btn.setEnabled(True)
        self.del_btn.setEnabled(True)

    def block_btns(self):  # Aункция блокировки кнопок во избежание ошибок
        self.see_btn.setEnabled(False)
        self.del_btn.setEnabled(False)

    def find_in_bd(self):  # Обработчик кнопки поиска с передачей фильтров в загрузчик таблицы
        self.load_table(self.sender_line.text(), self.recipient_line.text(), self.category_cb.currentText())

    def see_mail(self):  # Обработчик кнопки просмотра письма в отдельном окне
        row = self.res[self.tableWidget.currentRow()]
        self.win = SeeEmailText(row[-1], f'id = {row[0]}')  # Вызов окна просмотра
        self.win.show()
        self.block_btns()

    def del_mail(self):  # Обработчик удаления записи
        row = self.res[self.tableWidget.currentRow()]
        bd.del_a_record(row[0])
        self.load_table()
        self.block_btns()

    def item_changed(self, item):  # Слот контроля изменений в записях таблицы и сохранатяль новых данных
        row = item.row()
        row_to_edit = self.res[row][0]
        col = item.column()
        col_to_edit = {0: 'ID', 1: 'category', 2: 'company', 3: 'recipient', 4: 'email'}[col]
        if col_to_edit != 'ID' and col_to_edit != 'category':
            bd.edit_a_record(row_to_edit, col_to_edit, item.text())
        self.block_btns()


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

    def handle(self):  # Функция обработки текста
        self.string_text = self.upload_text(self.path_to_file)  # Получение строкового текста

        tags_and_tokens = ner_predict(self.string_text)  # Получение нер токенов и их обработка
        if 'PERSON' in tags_and_tokens.keys():
            reciepment = tags_and_tokens['PERSON'][0]
        else:
            reciepment = 'Не найдено'
        if 'ORGANIZATION' in tags_and_tokens.keys():
            company = tags_and_tokens['ORGANIZATION'][-1]
        else:
            company = 'Не найдено'

        category_ind = Classificator.get_category(self.string_text)  # Получение категории письма
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
            if self.recipient_line.text():  # Проверка наличия некорректынх симовлов в получателе
                for i in self.recipient_line.text():
                    if not i.isalpha() and i != ' ':
                        raise RecipientError
            else:
                raise RecipientError
            if self.company_line.text():  # Проверка наличия некорректных символов в отправителе
                for i in self.company_line.text():
                    if not i.isalpha() and i != ' ':
                        raise SenderError
            else:
                raise SenderError
            self.save_btn.setEnabled(True)
            self.label_tegs_error.setText('')
        except RecipientError:
            self.label_tegs_error.setText('Некорректный получатель')  # Обработка ошибок и их выведение в лейбле
        except SenderError:
            self.label_tegs_error.setText('Некорректный отправитель')
        except Exception as ex:  # Другие ошибки
            print(ex)  # Для удобства разработчика выводится в консоль
            self.label_tegs_error.setText('Ошибка')

    def save(self):  # Функция сохранения записи в бд
        bd.add_a_record(self.category_cb.currentText(), self.company_line.text(), self.recipient_line.text(),
                        self.string_text)
        bd.commit()
        self.close()  # Закрытие окна


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):  # Инициализатор графических объектов
        uic.loadUi('designs\\main.ui', self)
        self.addmail_btn.clicked.connect(self.open_addmail_dialog)
        self.seemail_btn.clicked.connect(self.show_seemail_window)

    def open_addmail_dialog(self):  # Обработчик нажатие на кнопку добавления письма
        self.addmaildialog = AddMailDialog()
        self.addmaildialog.show()

    def show_seemail_window(self):  # Обработчик нажатия на кнопку просмотра писем
        self.seemailwindow = SeeMailWindow()
        self.seemailwindow.show()

    def closeEvent(self, event):  # Прекращение соединения с бд, при закрытии окна
        bd.close()


def except_hook(cls, exception, traceback):  # Функция для корректной работы в случае
    # обнаружения ошибок и вывода их в консоль
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
