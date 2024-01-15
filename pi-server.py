from flask import Flask, request, jsonify
import cv2
import numpy as np
import pytesseract
import re
import requests
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Function to detect license plate
def detect_license_plate(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use a Gaussian blur to reduce noise and improve edge detection
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection
    edged = cv2.Canny(gray, 30, 200)

    # Find contours based on edges
    contours, new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours based on their area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

    # Initialize license Plate contour and coordinates
    license_plate = None
    x = None
    y = None
    w = None
    h = None

    # Find the best contour for the license plate
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4:  # Contour with 4 corners
            license_plate = approx
            x, y, w, h = cv2.boundingRect(contour)
            break

    # Crop the image to the detected license plate
    cropped_image = gray[y:y + h, x:x + w]

    # Use Tesseract OCR to read the license plate number
    text = pytesseract.image_to_string(cropped_image, lang='eng')

    # Process the text
    modified_text = re.sub('[^A-Za-z0-9]+', '', text.strip().lower().replace('o', '0'))

    return modified_text

def check_plate_authorization(plate):
    url = f"http://192.168.1.30:1880/api/is-authorized?plate={plate}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('authorized', False), plate
    else:
        return False, plate

# Endpoint for uploading an image
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('/tmp', filename)
        file.save(filepath)

        image = cv2.imread(filepath)
        detected_plate_text = detect_license_plate(image)
        is_authorized, plate = check_plate_authorization(detected_plate_text)

        print(f"License Plate: {plate}, Authorized: {is_authorized}")
        return jsonify({'License Plate': plate, 'Authorized': is_authorized})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)