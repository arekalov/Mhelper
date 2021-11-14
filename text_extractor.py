import pytesseract as tess
import cv2
from PIL import Image


def image_to_text(filepath):
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    img = Image.open(filepath)
    text = tess.image_to_string(img, lang='rus')
    return ' '.join(text.split())


def txt_to_text(filepath):
    file = open(filepath, encoding='utf8')
    to_return = ' '.join(list(map(str.strip, file.readlines())))
    file.close()
    return to_return

