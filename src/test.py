import cv2
import numpy as np
import pytesseract
from PIL import Image
import os

from flask import jsonify

# ---------------------------------------------
# Cargar la imagen
image_path = "imgreferences/3.jpeg"
frame = cv2.imread(image_path)

frame = cv2.resize(frame, (1024, 576))

Ctexto = ''

# ----------------------------------------------
al, an, c = frame.shape

x1 = int(an / 3)
x2 = int(x1 * 2)

y1 = int(al / 3)
y2 = int(y1 * 2)

# Recortar el área de la imagen donde podría estar la placa
recorte = frame[y1:y2, x1:x2]

# Separar los canales de color
mB = np.matrix(recorte[:, :, 0])
mG = np.matrix(recorte[:, :, 1])
mR = np.matrix(recorte[:, :, 2])

# Identificar diferencias de color entre el verde y el azul para encontrar el amarillo
Color = cv2.absdiff(mG, mB)

# Aplicar un umbral para binarizar la imagen
_, umbral = cv2.threshold(Color, 40, 255, cv2.THRESH_BINARY)

# Encontrar contornos en la imagen
contornos, _ = cv2.findContours(umbral, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Ordenar los contornos por área
contornos = sorted(contornos, key=lambda x: cv2.contourArea(x), reverse=True)

for contorno in contornos:
    area = cv2.contourArea(contorno)
    if area > 500 and area < 5000:
        x, y, ancho, alto = cv2.boundingRect(contorno)

        xpi = x + x1
        ypi = y + y1

        xpf = x + ancho + x1
        ypf = y + alto + y1

        # Recortar la placa
        placa = frame[ypi:ypf, xpi:xpf]

        alp, anp, cp = placa.shape

        Mva = np.zeros((alp, anp))

        mBp = np.matrix(placa[:, :, 0])
        mGp = np.matrix(placa[:, :, 1])
        mRp = np.matrix(placa[:, :, 2])

        # Invertir los colores para mejorar el reconocimiento
        for col in range(0, alp):
            for fil in range(0, anp):
                Max = max(mRp[col, fil], mGp[col, fil], mBp[col, fil])
                Mva[col, fil] = 255 - Max

        # Binarizar la placa
        _, bin = cv2.threshold(Mva, 150, 255, cv2.THRESH_BINARY)

        bin = bin.reshape(alp, anp)
        bin = Image.fromarray(bin)
        bin = bin.convert("L")

        if alp >= 36 and anp >= 82:
            # Configurar Tesseract
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            config = "--psm 1"
            texto = pytesseract.image_to_string(bin, config=config)

            if len(texto) >= 7:
                Ctexto = texto

        # Guardar la imagen recortada de la placa
        # Crear la carpeta si no existe
        output_folder = 'placa_img'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Guardar la imagen de la placa recortada
        placa_image_path = os.path.join(output_folder, 'placa_recortada.jpg')
        cv2.imwrite(placa_image_path, placa)

        break

def plate_result():
    # Imprimir el texto detectado en la placa en la consola
    plate = 'Texto detectado en la placa: ' + Ctexto
    return plate
