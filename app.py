import base64
from flask import Flask, request, jsonify
import cv2
import numpy as np
import mediapipe as mp

app = Flask(__name__)

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='hand_gesture.task'),
    running_mode=VisionRunningMode.IMAGE)
recognizer = GestureRecognizer.create_from_options(options)

@app.route('/process_image', methods=['POST'])
def process_image_route():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'error': 'No image found'}), 400
    
    image_bytes = base64.b64decode(data['image'])
    
    npimg = np.frombuffer(image_bytes, np.uint8)
    
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    gesture_recognition_result = recognizer.recognize(mp_image)

    if gesture_recognition_result.gestures:
        top_gesture = gesture_recognition_result.gestures[0][0]
        label = top_gesture.category_name
        accuracy = top_gesture.score * 100
        accuracy = "{:.2f}".format(accuracy)
        print("Detected Gesture Label:", label, " with Accuracy:", accuracy, "%")
        return jsonify({'gesture': label}), 200
    else:
        print("No gesture detected.")
        return jsonify({'error': 'No gesture detected'}), 400

# flask run -h 192.168.1.102

if __name__ == '__main__':
    app.run()