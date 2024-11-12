import os
from flask import Flask, request, jsonify, render_template, send_file
from PIL import Image, ImageDraw
from ultralytics import YOLO
from process_plate import process_plate_image
from characters_module import detect_plate_characters, correct_plate_text

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'output/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Modelo Yolov5 preentrenado para detectar objetos como carros o motocicletas (con o sin tripulante)
model = YOLO('yolov5s.pt')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No se proporcionó ninguna imagen.'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No se seleccionó ninguna imagen.'}), 400

    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    try:
        with Image.open(image_path) as img:
            format_ = img.format

        results = model(image_path)

        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        detections = []
        motorcycles = []
        persons = []
        cropped_image_path = None
        plate_text = ''

        for result in results:
            for box in result.boxes:
                label = result.names[int(box.cls)]
                bbox = box.xyxy.tolist()[0]
                confidence = float(box.conf)

                if label == 'person':
                    persons.append(bbox)
                elif label == 'motorcycle':
                    motorcycles.append(bbox)

                if label in ['car', 'motorcycle', 'person']:
                    draw.rectangle(bbox, outline="red", width=3)
                    detections.append({
                        'label': label,
                        'confidence': confidence,
                        'bbox': bbox
                    })
                    cropped_image_path = crop_and_save_image(img, bbox, label, image.filename)

        for motorcycle_bbox in motorcycles:
            for person_bbox in persons:
                if is_person_on_motorcycle(person_bbox, motorcycle_bbox):
                    draw.rectangle(motorcycle_bbox, outline="blue", width=3)
                    detections.append({
                        'label': 'person_on_motorcycle',
                        'confidence': confidence,
                        'bbox': motorcycle_bbox
                    })

        plate_image_path = process_plate_image(cropped_image_path)

        if plate_image_path is not None:
            text = detect_plate_characters(plate_image_path)
            if text is not None:
                plate_text = correct_plate_text(text)

        return jsonify({
            'filename': image.filename,
            'format': format_,
            'detections': detections,
            'plate_text': plate_text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/processed_image/<filename>', methods=['GET'])
def download_image(filename):
    image_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        return jsonify({'error': 'Imagen no encontrada.'}), 404


def is_person_on_motorcycle(person_bbox, motorcycle_bbox):
    px1, py1, px2, py2 = person_bbox
    mx1, my1, mx2, my2 = motorcycle_bbox

    if px1 < mx2 and px2 > mx1 and py2 > my1:
        return True
    return False


def crop_and_save_image(img, bbox, label, original_filename):
    x1, y1, x2, y2 = map(int, bbox)
    cropped_img = img.crop((x1, y1, x2, y2))
    cropped_image_path = os.path.join(OUTPUT_FOLDER, f"crop_{label}_{x1}_{y1}_{x2}_{y2}_{original_filename}")
    cropped_img.save(cropped_image_path)
    return cropped_image_path


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
