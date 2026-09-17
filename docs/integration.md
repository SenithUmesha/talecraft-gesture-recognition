# TaleCraft gesture integration

This document covers the boundary between the Flutter app and the Python gesture-recognition service.

## 1. The goal

The service does not try to understand story semantics.

It only answers one question:

> “Which trained gesture is visible in this image?”

TaleCraft then interprets the returned category as a choice number.

That separation keeps the vision model independent from story logic.

## 2. End-to-end flow

```text
TaleCraft reaches a choice block
        ↓
Flutter asks for camera permission
        ↓
camera captures one image
        ↓
image bytes → Base64
        ↓
POST /process_image
        ↓
Flask validates payload
        ↓
OpenCV decodes image
        ↓
BGR image → RGB
        ↓
MediaPipe GestureRecognizer
        ↓
top gesture category + confidence
        ↓
Flutter parses category as integer
        ↓
validate number <= available choices
        ↓
show confirmation dialog
        ↓
resume selected story branch
```

The important design decision is at the bottom: recognition does not directly mutate story state. The app validates and confirms the result first.

## 3. Request contract

Endpoint:

```text
POST /process_image
```

Content type:

```text
application/json
```

Payload:

```json
{
  "image": "<base64>"
}
```

The service accepts either plain Base64 or a data URL such as:

```text
data:image/jpeg;base64,/9j/4AAQSk...
```

## 4. Response contract

Successful recognition:

```json
{
  "gesture": "2",
  "confidence": 0.9734
}
```

TaleCraft's original client code expects `gesture` to be parseable as an integer.

That means the model used with the app should expose categories like:

```text
1
2
3
4
...
```

If you use a generic MediaPipe model with labels such as `Open_Palm` or `Thumb_Up`, add a mapping layer before passing the result into TaleCraft.

## 5. Why confidence is returned

The original service only returned the category name.

The current API also exposes MediaPipe's score so a client can choose to introduce a threshold, for example:

```text
confidence < 0.70 → ask for another gesture
confidence >= 0.70 → show confirmation
```

The Flutter prototype does not currently depend on the confidence field, so adding it is backward-compatible with the existing `gesture` property.

## 6. Error behavior

### Missing image

HTTP `400`

```json
{
  "error": "No image provided"
}
```

### Invalid Base64

HTTP `400`

```json
{
  "error": "Image is not valid Base64"
}
```

### Invalid image bytes

HTTP `400`

```json
{
  "error": "Image could not be decoded"
}
```

### No recognisable gesture

HTTP `422`

```json
{
  "error": "No gesture detected"
}
```

The original TaleCraft client simply treats any non-200 response as a failed recognition and retries after a delay.

## 7. Network configuration

The original Flutter prototype points to a private LAN address because the Flask service was running on a development machine.

That works for a quick experiment, but the address must be reachable from the device running TaleCraft.

Common local setups:

### Physical phone + laptop

Put both devices on the same Wi-Fi network and use the laptop's LAN address:

```text
http://192.168.x.x:5000/process_image
```

### Android emulator

For a service running on the host machine, Android emulators commonly use:

```text
http://10.0.2.2:5000/process_image
```

### iOS simulator

A host service is commonly reachable through localhost:

```text
http://127.0.0.1:5000/process_image
```

Exact networking depends on the development environment.

## 8. Performance characteristics

This is request/response recognition, not streaming inference.

One user choice generally means:

- one camera capture,
- one Base64 conversion,
- one HTTP request,
- one MediaPipe image inference.

That is a reasonable prototype shape for occasional story decisions, but not for continuous gesture tracking.

Main overheads are:

1. JPEG/PNG encoding on the mobile side,
2. Base64 size expansion,
3. network latency,
4. OpenCV image decode,
5. MediaPipe inference.

## 9. Why not send every camera frame?

Because TaleCraft does not need to.

The user reaches a branch, performs a gesture, gets a result, then goes back to reading/listening.

Continuous inference would add battery, CPU, bandwidth and synchronization complexity without much value for this interaction.

## 10. Model lifecycle

The MediaPipe model is loaded once when `app.py` starts:

```text
process start
    ↓
load hand_gesture.task
    ↓
create GestureRecognizer
    ↓
serve many HTTP requests
```

It is not recreated for every request.

That keeps repeated inference much cheaper than repeatedly loading the model from disk.

## 11. Production concerns

This service intentionally stays small, but a public deployment should add more around it:

- request authentication,
- rate limiting,
- maximum request/payload size,
- HTTPS,
- a production WSGI server,
- structured request metrics,
- timeouts,
- concurrency testing,
- explicit confidence thresholds,
- model/version reporting,
- privacy rules for uploaded camera images.

A stronger production architecture could also remove the network hop entirely and run gesture inference on-device.

## 12. Relationship to TaleCraft

The Flutter-side gesture flow lives in the main project:

**https://github.com/SenithUmesha/talecraft**

Look at the gesture story controller to see how TaleCraft:

- captures the image,
- Base64-encodes it,
- calls `/process_image`,
- converts the returned label to a choice index,
- confirms the result,
- resumes the story graph.
