"""Recorte da pessoa (MODNet) para colocar elementos ATRÁS dela."""
import numpy as np, onnxruntime as ort
from PIL import Image
from huggingface_hub import hf_hub_download
_s = None


def session():
    global _s
    if _s is None:
        so = ort.SessionOptions(); so.intra_op_num_threads = 2
        _s = ort.InferenceSession(hf_hub_download('Xenova/modnet', 'onnx/model.onnx'), so)
    return _s


def matte(img, w=384, h=672):
    """img PIL RGB 1080x1920 -> máscara L 1080x1920 (255 = pessoa)."""
    x = np.asarray(img.resize((w, h), Image.BILINEAR), dtype=np.float32)
    x = (x / 255.0 - 0.5) / 0.5
    x = x.transpose(2, 0, 1)[None]
    m = session().run(None, {'input': x})[0][0, 0]
    m = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).resize(img.size, Image.BILINEAR)
    return m
