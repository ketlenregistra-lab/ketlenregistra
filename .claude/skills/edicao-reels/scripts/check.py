import sys,subprocess; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import SAFE
from PIL import Image, ImageDraw
f=sys.argv[1]; ts=[float(x) for x in sys.argv[3:]]; out=sys.argv[2]
import os; tmpf=f'/tmp/claude-0/_c{os.getpid()}.png'
ims=[]
for t in ts:
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',f,'-frames:v','1',tmpf])
    im=Image.open(tmpf).convert('RGB'); d=ImageDraw.Draw(im); S=SAFE
    d.line([(S['x0'],S['y0']),(S['x1'],S['y0']),(S['x1'],S['y_low']),(S['x1_low'],S['y_low']),(S['x1_low'],S['y1']),(S['x0'],S['y1']),(S['x0'],S['y0'])],fill=(0,255,0),width=4)
    d.text((10,10),f'{t:.1f}s',fill=(255,255,0),font_size=60)
    ims.append(im.resize((300,533)))
cols=min(len(ims),7); rows=(len(ims)+cols-1)//cols
sh=Image.new('RGB',(cols*300,rows*533))
for k,im in enumerate(ims): sh.paste(im,((k%cols)*300,(k//cols)*533))
sh.save(out)
