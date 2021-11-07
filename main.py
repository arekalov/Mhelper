import sys
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog

from Exceptions import FormatError


class SeeMailWindow(QMainWindow):
    def __init__(self):
        super(SeeMailWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        uic.loadUi('designs\\see_db.ui', self)


class AddMailDialog(QDialog):
    def __init__(self):
        super(AddMailDialog, self).__init__()
        self.init_ui()

    def init_ui(self):
        uic.loadUi('designs\\dialog.ui', self)
        self.upload_btn.clicked.connect(self.upload)
        self.handle_btn.clicked.connect(self.handle)
        self.save_btn.clicked.connect(self.save)
        self.pixmap = QPixmap('system pictures\\file_icon.png')

    def check_correct_filepath(self, path):
        a = open(path, 'wb')
        if path.split('/')[-1].split('.')[-1] not in ['jpg', 'tif', 'pdf', 'png', 'txt']:
            raise FormatError

    def upload(self):
        try:
            path_to_file = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '', 'Картинка (*.jpg);;'
                                                                                     'Картинка(*.png);;'
                                                                                     'Картинка (*.tif);;'
                                                                                     'Текст (*.txt);;'
                                                                                     'Все (*);')[0]
            self.check_correct_filepath(path_to_file)
            self.label_picture.setPixmap(self.pixmap)
            self.label_error.setText(f'Файл {path_to_file.split("/")[-1]} загружен')

            self.upload_btn.setEnabled(False)
            self.handle_btn.setEnabled(True)
        except FormatError:
            self.label_error.setText('Ошибка формата файла')
        except Exception as ex:
            print(ex)
            self.label_error.setText('Ошибка при загрузке файла')

    def handle(self):
        pass

    def save(self):
        pass


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
