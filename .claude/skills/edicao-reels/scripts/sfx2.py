import numpy as np, wave, os
SR=44100; OUT=os.path.join(os.environ.get('EDIT_ROOT', os.getcwd()),'sfx'); os.makedirs(OUT, exist_ok=True); rng=np.random.default_rng(11)
def save(name,x,peak=0.9):
    x=x/(np.max(np.abs(x))+1e-9)*peak; st=np.stack([x,x],1)
    with wave.open(os.path.join(OUT,name+'.wav'),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())
def t(d): return np.arange(int(SR*d))/SR
def hp(x):  # simples passa-altas
    return np.concatenate([[0],np.diff(x)])
# click de interface: estalo curto e nítido (mouse/toque)
tt=t(0.05)
c=hp(rng.standard_normal(len(tt)))*np.exp(-tt*300)*0.6+np.sin(2*np.pi*3200*tt)*np.exp(-tt*220)+0.5*np.sin(2*np.pi*1800*tt)*np.exp(-tt*260)
save('click',c)
# tecla de teclado (mecânico suave), uma variação
def key(seed):
    r=np.random.default_rng(seed); tt=t(0.07)
    body=np.sin(2*np.pi*r.uniform(380,520)*tt)*np.exp(-tt*90)
    tick=hp(r.standard_normal(len(tt)))*np.exp(-tt*500)
    return body*0.6+tick*0.9
save('key',key(3))
# contagem: ticks rápidos acelerando ~0.9s, terminando num tique mais agudo
x=np.zeros(int(SR*1.0)); times=np.cumsum(np.linspace(0.085,0.035,16)); times=times/times[-1]*0.85
for i,s in enumerate(times):
    tt=t(0.03); f=1500+i*60
    k=np.sin(2*np.pi*f*tt)*np.exp(-tt*200); p=int(s*SR); x[p:p+len(k)]+=k[:len(x)-p]
tt=t(0.12); k=np.sin(2*np.pi*2600*tt)*np.exp(-tt*35); p=int(0.88*SR); x[p:p+len(k)]+=k[:len(x)-p]
save('count',x,0.8)
print('ok')
