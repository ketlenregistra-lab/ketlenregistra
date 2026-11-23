"""Pontos do rosto (olhos, nariz, boca, orelhas) em px de 1080x1920 num intervalo de tempo do vídeo."""
import cv2, json, sys, subprocess, numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
det = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path="face.tflite"), min_detection_confidence=0.4))
p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", src,
                      "-vf", "fps=10,scale=540:960", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
res = []
n = 0
while True:
    b = p.stdout.read(540 * 960 * 3)
    if len(b) < 540 * 960 * 3: break
    fr = np.frombuffer(b, np.uint8).reshape(960, 540, 3)
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr)))
    if r.detections:
        d = max(r.detections, key=lambda d: d.bounding_box.width)
        bb = d.bounding_box
        res.append({"t": round(t0 + n / 10, 2), "box": [bb.origin_x * 2, bb.origin_y * 2, bb.width * 2, bb.height * 2],
                    "kp": [[k.x * 1080, k.y * 1920] for k in d.keypoints]})
    n += 1
json.dump(res, open(out, "w"))
