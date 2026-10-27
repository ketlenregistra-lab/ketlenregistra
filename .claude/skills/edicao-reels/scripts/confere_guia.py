"""Confere a guia da Ketlen renderizando só os textos (legendas.ass) sobre fundo preto, a cada 0,1 s.
Área liberada em 1080x1920: x 88-994, y 263-1459; abaixo de y 1070 o limite direito é 927."""
import subprocess, sys, numpy as np
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 100
proc = subprocess.Popen(["ffmpeg","-v","error","-f","lavfi","-i",f"color=black:s=1080x1920:d={dur}:r=10",
                         "-vf","ass=legendas.ass:fontsdir=../fonts3","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
fora = np.zeros((1920,1080),bool); fora[:263]=1; fora[1460:]=1; fora[:,:88]=1; fora[:,995:]=1; fora[1070:,928:]=1
n=0; ruins=[]
while True:
    b=proc.stdout.read(1080*1920)
    if len(b)<1080*1920: break
    txt=np.frombuffer(b,np.uint8).reshape(1920,1080)>40
    k=int((txt&fora).sum())
    if k: 
        ys,xs=np.where(txt&fora); ruins.append((round(n/10,1),k,int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
    n+=1
print(f"{n} quadros conferidos; fora da guia: {len(ruins)}")
for r in ruins[:20]: print("  t=%s px=%s x %s-%s y %s-%s" % r)
