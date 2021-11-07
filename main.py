import sys
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog

from Exceptions import FormatError, SenderError, RecipientError


class SeeMailWindow(QMainWindow):  # Класс окна для прссмотра бд с письмами
    def __init__(self):
        super(SeeMailWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        uic.loadUi('designs\\see_db.ui', self)


class AddMailDialog(QDialog):  # Класс диалогового окна для загрузки письма в бд
    def __init__(self):
        super(AddMailDialog, self).__init__()
        self.init_ui()

    def init_ui(self):  # Инициализация графических элементов
        uic.loadUi('designs\\dialog.ui', self)
        self.upload_btn.clicked.connect(self.upload)
        self.handle_btn.clicked.connect(self.handle)
        self.save_btn.clicked.connect(self.save)
        self.pixmap = QPixmap('system pictures\\file_icon.png')

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
        # if self.check_correct_file(self.path_to_file) != 'txt':  # Преобразование файла в текст
        #     self.photo_to_text(self.path_to_file)

    def check_correct_file(self, path):  # Проверка достоверности нахождения файла в директории
        # и проверка формата файла
        a = open(path, 'wb')  # Если файла не будет в директории выбросит ошибку, которую захватит обработчик
        extension = path.split('/')[-1].split('.')[-1]
        if extension not in ['jpg', 'tif', 'pdf', 'png', 'txt']:
            raise FormatError
        return extension

    def handle(self):
        # Здесь должны получить результат работы моделей определяющих теги письма, временно они заменены константами
        theme = 'Олег'
        category = 'Срочно'
        company = 'IRZ'
        # Блокируется кнопка обработки и пользователь может изменить настройки вручную
        self.handle_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.recipient_line.setEnabled(True)
        self.category_cb.setEnabled(True)
        self.company_line.setEnabled(True)
        # Передаем к пользователю полученные моделью теги
        self.recipient_line.setText(theme)
        self.company_line.setText(company)
        # Если пользователь редактирует теги, то проверяем их корректность и временно блокируем кнопку сохранения
        self.recipient_line.textChanged.connect(self.block_save_btn)
        self.company_line.textChanged.connect(self.block_save_btn)

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
        print(self.path_to_file, self.recipient_line.text(), self.category_cb.currentText(), self.company_line.text())
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
