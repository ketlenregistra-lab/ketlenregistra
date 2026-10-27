"""Mede o atraso entre boca e voz: correlaciona movimento da boca (detector de rosto) com a variação do áudio."""
import cv2, numpy as np, wave, subprocess, sys
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src = sys.argv[1]
det = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path="face.tflite"), min_detection_confidence=0.5))
proc = subprocess.Popen(["ffmpeg","-v","error","-i",src,"-vf","scale=540:960","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
fsz=540*960*3; mouth=[]; prev=None; box=None; n=0
while True:
    buf=proc.stdout.read(fsz)
    if len(buf)<fsz: break
    fr=np.frombuffer(buf,np.uint8).reshape(960,540,3)
    if n%3==0 or box is None:
        r=det.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(fr)))
        box=None
        if r.detections:
            d=max(r.detections,key=lambda d:d.bounding_box.width); kp=d.keypoints[3]
            box=(int(kp.x*540),int(kp.y*960),int(d.bounding_box.width*0.35))
    g=None
    if box:
        x,y,rr=box; c=fr[max(y-rr,0):y+rr, max(x-rr,0):x+rr]
        if c.size: g=cv2.resize(cv2.cvtColor(c,cv2.COLOR_RGB2GRAY),(32,32)).astype(float)
    mouth.append(np.nan if (g is None or prev is None) else np.mean(np.abs(g-prev)))
    prev=g; n+=1
m=np.array(mouth)
subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-vn","-ac","1","-ar","16000","_sync.wav"])
w=wave.open("_sync.wav"); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)
env=np.array([np.sqrt(np.mean(a[int(i*16000/30):int((i+1)*16000/30)]**2)+1e-9) for i in range(len(m))])
de=np.abs(np.diff(env,prepend=env[0]))
ok=~np.isnan(m)
def z(x):
    x=x.copy(); x[~ok]=0; x=(x-x[ok].mean())/x[ok].std(); x[~ok]=0; return x
mz, ez = z(m), z(de)
res=[]
for lag in range(-12,13):   # lag>0: áudio chega depois da boca
    c = np.dot(mz[:len(mz)-lag], ez[lag:]) if lag>=0 else np.dot(mz[-lag:], ez[:len(ez)+lag])
    res.append((lag,c))
with open("sync.txt","w") as f:
    for lag,c in res: f.write(f"{lag:+3d} quadros ({lag*1000/30:+6.0f} ms): {c:8.1f}\n")
    b=max(res,key=lambda x:x[1]); f.write(f"MELHOR {b[0]:+d} quadros = {b[0]*1000/30:+.0f} ms\n")
