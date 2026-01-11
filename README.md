# ✋ TaleCraft – Gesture Recognition Service

This repository contains the **gesture recognition backend service** used in the **TaleCraft** interactive storytelling platform.

It is a Python-based REST API that processes images and detects hand gestures using **MediaPipe**, enabling gesture-controlled interactions inside the TaleCraft mobile application.

---

## 🚀 Overview

The service exposes an HTTP endpoint that:

1. Accepts an image encoded in Base64
2. Decodes and processes the image
3. Detects hand gestures using a trained MediaPipe gesture recognition model
4. Returns the detected gesture as a JSON response

This enables **hands-free navigation** and **natural interaction** within the TaleCraft app.

---

## 🧠 Features

* **Hand Gesture Recognition**

  * Uses MediaPipe’s Gesture Recognizer task
  * Detects predefined hand gestures with confidence scoring

* **REST API Interface**

  * Simple POST endpoint for easy mobile integration
  * JSON-based request/response format

* **Real-Time Image Processing**

  * OpenCV-based image decoding and color conversion
  * Optimized for low-latency gesture detection

---

## 🛠️ Tech Stack

* **Language:** Python
* **Framework:** Flask
* **Computer Vision:** OpenCV
* **ML / Gesture Recognition:** MediaPipe
* **Model Format:** `.task` (MediaPipe gesture model)
* **Data Transfer:** Base64-encoded images over REST

---

## 📡 API Endpoint

### `POST /process_image`

**Request Body (JSON):**

```json
{
  "image": "<base64-encoded-image>"
}
```

**Success Response (200):**

```json
{
  "gesture": "Open_Palm"
}
```

**Error Responses:**

* `400` – No image provided
* `400` – No gesture detected

---

## ⚙️ How It Works

1. The client captures an image frame
2. Image is Base64-encoded and sent to the API
3. Server decodes the image and converts it to RGB
4. MediaPipe processes the image using the gesture model
5. The top detected gesture is returned to the client

---

## ▶️ Running the Project

### 1. Install Dependencies

```bash
pip install flask opencv-python mediapipe numpy
```

### 2. Add Gesture Model

Place the MediaPipe gesture model file in the project root:

```
hand_gesture.task
```

### 3. Start the Server

```bash
python app.py
```

Or using Flask:

```bash
flask run --host=0.0.0.0
```

---

## 🔗 Integration

This service is designed to be consumed by:

* **Flutter mobile applications**
* Any frontend capable of sending Base64 images via REST

Used directly by the **TaleCraft** mobile app for gesture-based story navigation.

---

## 📂 Project Purpose

This project was built to:

* Implement real-time computer vision in a production-style API
* Integrate ML-based gesture recognition with mobile apps
* Explore hands-free UI interactions
* Support advanced storytelling interaction in TaleCraft

---

## 👤 Author

**Senith Umesha**
Flutter Developer | Mobile & AI Integration

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge\&logo=linkedin\&logoColor=white)](https://www.linkedin.com/in/senith-umesha/)

---

## ⚠️ Disclaimer

This project is intended for educational and experimental use.
Gesture recognition accuracy depends on lighting conditions, camera quality, and model limitations.
