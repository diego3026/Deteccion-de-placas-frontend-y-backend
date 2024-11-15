import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def detect_plate_characters(image_path):
    image = cv2.imread(image_path)

    if image is None:
        print(f"No se pudo cargar la imagen en {image_path}")
        return ""

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated_image = cv2.dilate(thresh_image, kernel, iterations=1)

    custom_config = r'--oem 3 --psm 8'
    text = pytesseract.image_to_string(dilated_image, config=custom_config)

    return text.strip()


def correct_plate_text(text):
    text = text.upper()
    text = re.sub(r'[^A-Za-z0-9]', '', text)

    if text.startswith('F'):
        if len(text) > 3 and re.match(r'[A-Za-z]{3}', text[1:4]):
            text = text[1:]

    plate_match = re.findall(r'[A-Za-z0-9]', text)

    if len(plate_match) == 6:
        corrected_plate = []

        for i, char in enumerate(plate_match):
            if i < 3:
                if char == '0':
                    corrected_plate.append('D')
                elif char == '6':
                    corrected_plate.append('G')
                else:
                    corrected_plate.append(char)
            elif i < 5:
                if char == 'D':
                    corrected_plate.append('0')
                elif char == 'G':
                    corrected_plate.append('6')
                else:
                    corrected_plate.append(char)
            else:
                if char == '0':
                    corrected_plate.append('D')
                elif char == '6':
                    corrected_plate.append('G')
                else:
                    corrected_plate.append(char)

        return f"{''.join(corrected_plate[:3])}-{''.join(corrected_plate[3:5])}{corrected_plate[5]}"
    else:
        return f"Texto final no válido, longitud o formato incorrecto: {text}"
