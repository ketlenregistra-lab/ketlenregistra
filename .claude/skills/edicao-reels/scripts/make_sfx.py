import numpy as np, wave
SR=48000
def save(name,x):
    x=x/np.max(np.abs(x))*0.9
    st=np.stack([x,x],1)
    w=wave.open(f"sfx/{name}.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
rng=np.random.default_rng(1)
# whoosh: ruído com filtro passa-baixa que abre e fecha
d=0.55; n=int(SR*d); t=np.arange(n)/SR
noise=rng.standard_normal(n)
cut=300+5000*np.sin(np.pi*t/d)**2
y=np.zeros(n); a=0
for i in range(n):
    k=1-np.exp(-2*np.pi*cut[i]/SR); a+=k*(noise[i]-a); y[i]=a
env=np.sin(np.pi*np.clip(t/d,0,1))**1.5
save("whoosh",y*env)
# pop: bolha curta com queda de frequência
d=0.12; n=int(SR*d); t=np.arange(n)/SR
f=1400*np.exp(-t*25)+350
ph=2*np.pi*np.cumsum(f)/SR
save("pop",np.sin(ph)*np.exp(-t*38))
# impacto: grave + ataque de ruído (para zoom repentino)
d=0.6; n=int(SR*d); t=np.arange(n)/SR
f=110*np.exp(-t*6)+45
low=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7)
hit=rng.standard_normal(n)*np.exp(-t*60)*0.5
save("impacto",low+hit)
