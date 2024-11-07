import os
from flask import Flask, request, jsonify, render_template, send_file
from PIL import Image, ImageDraw
from ultralytics import YOLO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'output/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
            width, height = img.size
            format_ = img.format

        results = model(image_path)

        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        detections = []
        for result in results:
            for box in result.boxes:
                label = result.names[int(box.cls)]
                if label in ['car', 'motorcycle']:
                    bbox = box.xyxy.tolist()[0]
                    draw.rectangle(bbox, outline="red", width=3)
                    detections.append({
                        'label': label,
                        'confidence': float(box.conf),
                        'bbox': bbox
                    })

        output_image_path = os.path.join(OUTPUT_FOLDER, f"detected_{image.filename}")
        img.save(output_image_path)

        return jsonify({
            'filename': image.filename,
            'width': width,
            'height': height,
            'format': format_,
            'detections': detections,
            'processed_image': output_image_path
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')