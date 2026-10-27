"""Acompanha o topo da cabeça (com cabelo) num vídeo 1080x1920; grava cabeca.json com (t, y_topo|None)."""
import cv2, json, sys
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
det = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path="face.tflite"), min_detection_confidence=0.4))
cap = cv2.VideoCapture(sys.argv[1]); n = 0; res = []
while True:
    ok, fr = cap.read()
    if not ok: break
    if n % 6 == 0:
        sm = cv2.cvtColor(cv2.resize(fr, (360, 640)), cv2.COLOR_BGR2RGB)
        r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=sm))
        top = None
        if r.detections:
            b = max(r.detections, key=lambda d: d.bounding_box.width).bounding_box
            top = int((b.origin_y - 0.5 * b.height) * 3)
        res.append((round(n / 30, 2), top))
    n += 1
json.dump(res, open(sys.argv[2], "w"))
