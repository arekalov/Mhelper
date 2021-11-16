import pytesseract as tess
import cv2
from PIL import Image


def image_to_text(filepath):  # Функция преобразования фото в текст
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Подгрузка pytesseract
    img = Image.open(filepath)
    text = tess.image_to_string(img, lang='rus')
    return ' '.join(text.split())


def txt_to_text(filepath):  # Функция перегонки текста из txt в string
    file = open(filepath, encoding='utf8')
    to_return = ' '.join(list(map(str.strip, file.readlines())))
    file.close()
    return to_return
