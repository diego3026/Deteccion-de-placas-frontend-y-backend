import cv2
import numpy as np
import os


def process_plate_image(image_path):
    image = cv2.imread(image_path)
    resized_image = cv2.resize(image, (500, 600))

    hsv_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])

    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
    kernel = np.ones((5, 5), np.uint8)
    dilated_mask = cv2.dilate(yellow_mask, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        plate_region = resized_image[y:y + h, x:x + w]
        extended_detected_high_res = cv2.resize(plate_region, (1000, 400), interpolation=cv2.INTER_CUBIC)
        kernel_sharpening = np.array([[-1, -1, -1],
                                      [-1, 9, -1],
                                      [-1, -1, -1]])
        sharpened_image = cv2.filter2D(extended_detected_high_res, -1, kernel_sharpening)

        output_folder = "plate_detected"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, "Plate_Enhanced.jpg")
        cv2.imwrite(output_path, sharpened_image)
        return output_path

    return None