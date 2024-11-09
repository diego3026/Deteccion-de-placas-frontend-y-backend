import cv2
import numpy as np

# Ruta de la imagen cargada (actualízala si es necesario)
image_path = "output/img.png"

# Cargar la imagen
image = cv2.imread(image_path)

# Redimensionar la imagen a 500x600 píxeles
resized_image = cv2.resize(image, (500, 600))

# Convertir la imagen redimensionada al espacio de color HSV
hsv_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)

# Definir los rangos de color amarillo en el espacio HSV
lower_yellow = np.array([20, 100, 100])  # Límite inferior del amarillo
upper_yellow = np.array([40, 255, 255])  # Límite superior del amarillo

# Crear una máscara que detecte los píxeles amarillos
yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

# Aplicar la máscara sobre la imagen original para obtener solo los píxeles amarillos
yellow_detected = cv2.bitwise_and(resized_image, resized_image, mask=yellow_mask)

# Redimensionar la imagen con los píxeles amarillos detectados a 500x200
yellow_detected_resized = cv2.resize(yellow_detected, (500, 200))

# Expandir la máscara para incluir más área alrededor del amarillo
kernel = np.ones((5, 5), np.uint8)  # Crear un kernel de 5x5 píxeles
dilated_mask = cv2.dilate(yellow_mask, kernel, iterations=1)  # Dilatar la máscara

# Aplicar la máscara dilatada sobre la imagen original para obtener los píxeles en el rango extendido
extended_detected = cv2.bitwise_and(resized_image, resized_image, mask=dilated_mask)

# Redimensionar la imagen con los píxeles detectados a 500x200
extended_detected_resized = cv2.resize(extended_detected, (500, 200))

# Mostrar la imagen original
cv2.imshow("Original image", resized_image)

# Mostrar la imagen en espacio HSV
cv2.imshow("Processing", hsv_image)

# Mostrar la imagen con el rango extendido alrededor del amarillo
cv2.imshow("Plate", extended_detected_resized)

# Esperar hasta que se presione una tecla para cerrar las ventanas
cv2.waitKey(0)
cv2.destroyAllWindows()
