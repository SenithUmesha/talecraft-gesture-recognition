import base64
import binascii
import os

import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "hand_gesture.task")

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
)
recognizer = GestureRecognizer.create_from_options(options)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "model": os.path.basename(MODEL_PATH)}), 200


@app.post("/process_image")
def process_image_route():
    data = request.get_json(silent=True) or {}
    encoded_image = data.get("image")

    if not isinstance(encoded_image, str) or not encoded_image.strip():
        return jsonify({"error": "No image provided"}), 400

    # Accept both raw Base64 and data-URL formatted image strings.
    if encoded_image.startswith("data:") and "," in encoded_image:
        encoded_image = encoded_image.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(encoded_image, validate=True)
    except (binascii.Error, ValueError):
        return jsonify({"error": "Image is not valid Base64"}), 400

    np_image = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Image could not be decoded"}), 400

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    result = recognizer.recognize(mp_image)

    if not result.gestures:
        return jsonify({"error": "No gesture detected"}), 422

    top_gesture = result.gestures[0][0]
    label = top_gesture.category_name
    confidence = round(float(top_gesture.score), 4)

    app.logger.info(
        "Detected gesture %s with confidence %.2f%%",
        label,
        confidence * 100,
    )

    return jsonify({"gesture": label, "confidence": confidence}), 200


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
