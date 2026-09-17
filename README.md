<p align="center">
  <strong>TaleCraft Gesture Recognition</strong>
</p>

<h1 align="center">✋ story choices, but with your hand</h1>

<p align="center">
  A tiny Flask + MediaPipe service that turns a camera frame into a TaleCraft story-choice number.
</p>

<p align="center">
  <a href="https://github.com/SenithUmesha/talecraft">TaleCraft app</a> ·
  <a href="docs/integration.md">Integration notes</a> ·
  <a href="#api">API</a>
</p>

<p align="center">
  <code>Python</code> · <code>Flask</code> · <code>OpenCV</code> · <code>MediaPipe</code>
</p>

---

## why this exists

TaleCraft has branching stories.

Normally you tap a choice. I wanted to see if the same branch could be selected with a hand gesture instead.

So this repo does one small job:

```text
camera image
   ↓
HTTP request
   ↓
image decode
   ↓
MediaPipe gesture recognition
   ↓
gesture label
   ↓
choice number in TaleCraft
```

The service stays separate from the Flutter app so the computer-vision experiment can be run, changed and tested without turning the mobile project into a Python/MediaPipe build problem.

## how TaleCraft uses it

The Flutter app reaches a decision point with, say, three choices.

It captures a camera image and sends it here as Base64. The custom gesture model returns a category label such as `"1"`, `"2"`, or `"3"`. TaleCraft converts that label to an integer, checks that the choice exists, asks the reader for confirmation, then continues down that branch.

```text
┌──────────────┐
│ TaleCraft UI │
└──────┬───────┘
       │ camera frame
       ▼
┌──────────────┐
│ Flask API    │
└──────┬───────┘
       │ decoded RGB image
       ▼
┌──────────────┐
│ MediaPipe    │
│ Recognizer   │
└──────┬───────┘
       │ label + confidence
       ▼
┌──────────────┐
│ choice index │
└──────────────┘
```

The mobile side lives in **[SenithUmesha/talecraft](https://github.com/SenithUmesha/talecraft)**.

## what the service does

The recognizer is created once when the Flask process starts, using `hand_gesture.task`.

For every image request, the service:

1. validates the JSON payload,
2. accepts raw Base64 or a `data:image/...;base64,...` string,
3. decodes the image bytes,
4. creates a NumPy buffer,
5. decodes the image through OpenCV,
6. converts BGR → RGB,
7. wraps the frame as a MediaPipe image,
8. runs `GestureRecognizer`,
9. returns the top label and confidence score.

If no gesture is recognised, the API returns a non-200 response so TaleCraft can retry or ask for another frame.

## api

### `GET /health`

A lightweight process/model check.

```json
{
  "status": "ok",
  "model": "hand_gesture.task"
}
```

### `POST /process_image`

Request:

```json
{
  "image": "<base64 encoded image>"
}
```

Success:

```json
{
  "gesture": "2",
  "confidence": 0.9734
}
```

The exact label set comes from the model. The TaleCraft integration expects numeric labels because those map naturally to `choice 1`, `choice 2`, etc.

Common errors:

```json
{ "error": "No image provided" }
```

```json
{ "error": "Image is not valid Base64" }
```

```json
{ "error": "Image could not be decoded" }
```

```json
{ "error": "No gesture detected" }
```

## run it locally

Create a virtual environment outside version control:

```bash
python -m venv .venv
```

Activate it, then install dependencies:

```bash
pip install -r requirements.txt
```

Make sure the model file exists at the repository root:

```text
hand_gesture.task
```

Then start the service:

```bash
python app.py
```

By default it listens on:

```text
0.0.0.0:5000
```

Optional environment variables:

```text
MODEL_PATH   custom .task model path
HOST         bind address
PORT         HTTP port
FLASK_DEBUG  set to 1 for Flask debug mode
```

Example:

```bash
MODEL_PATH=hand_gesture.task PORT=5000 python app.py
```

## quick API test

Health check:

```bash
curl http://127.0.0.1:5000/health
```

Image request:

```bash
curl -X POST http://127.0.0.1:5000/process_image \
  -H "Content-Type: application/json" \
  -d '{"image":"<base64>"}'
```

For an actual TaleCraft device, `127.0.0.1` means the phone/emulator itself — not your laptop. Use an address reachable by the device, or tunnel/deploy the service.

## project layout

```text
.
├── app.py               # Flask API + MediaPipe pipeline
├── hand_gesture.task    # gesture recognizer model
├── requirements.txt     # Python dependencies
├── .gitignore
├── docs/
│   └── integration.md   # mobile/service architecture notes
└── README.md
```

## engineering choices

### Why Flask?

This was a small integration service, not a platform. Flask kept the HTTP layer tiny and easy to inspect.

### Why Base64 JSON?

It made the first mobile integration straightforward because the Flutter side could read image bytes, Base64-encode them and send one JSON object.

The downside is overhead: Base64 increases payload size and JSON is not ideal for high-frequency image streaming.

### Why one image at a time?

TaleCraft only needs a gesture when a story reaches a choice. This is intentionally not a continuous video pipeline.

That keeps CPU usage, network traffic and implementation complexity much lower than streaming every camera frame.

### Why a separate service instead of on-device ML?

For the original experiment, Python + MediaPipe was faster to iterate on than building native/on-device inference into Flutter.

For a production rebuild, on-device recognition would be worth considering for lower latency, better privacy and offline use.

## limitations

This is a prototype computer-vision service, not a hardened public API.

Recognition quality depends on the model, camera framing, lighting and how clearly the gesture appears. There is no auth, rate limiting, request-size cap or production server configuration in this repo.

The mobile prototype also treats the top recognised label as a choice number, so a model with non-numeric labels requires an explicit mapping layer.

More integration detail is in **[docs/integration.md](docs/integration.md)**.

---

built as the slightly unnecessary computer-vision side quest of **[TaleCraft](https://github.com/SenithUmesha/talecraft)** by [Senith Umesha](https://github.com/SenithUmesha)
