import numpy as np, wave, os
SR=44100
OUT=os.path.join(os.environ.get('EDIT_ROOT', os.getcwd()),'sfx'); os.makedirs(OUT, exist_ok=True)
rng=np.random.default_rng(7)
def save(name,x):
    x=np.asarray(x,dtype=np.float64); x=x/ (np.max(np.abs(x))+1e-9)*0.9
    st=np.stack([x,x],1)
    with wave.open(os.path.join(OUT,name+'.wav'),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st*32767).astype(np.int16).tobytes())
def t(d): return np.arange(int(SR*d))/SR
def lp(x,a):  # one-pole lowpass, a in (0,1) per-sample array or scalar
    y=np.zeros_like(x); s=0.0; a=np.broadcast_to(a,x.shape)
    for i in range(len(x)): s+=a[i]*(x[i]-s); y[i]=s
    return y
def bp_sweep(x,f0,f1):
    n=len(x); f=np.geomspace(f0,f1,n); a=1-np.exp(-2*np.pi*f/SR)
    return lp(x,a)-lp(lp(x,a),a*0.5)
# whoosh: noise swept band, bell envelope
d=0.55; tt=t(d); n=rng.standard_normal(len(tt))
env=np.sin(np.pi*np.clip(tt/d,0,1))**2.2
w=bp_sweep(n,300,4500)*env
save('whoosh',w)
# reverse-ish whoosh down (zoom out)
save('whoosh_down',bp_sweep(n,4000,250)*env)
# soft whoosh short (for subtitle slides / cards)
d=0.32; tt=t(d); n=rng.standard_normal(len(tt)); env=np.sin(np.pi*tt/d)**2
save('swish',bp_sweep(n,800,6000)*env*0.7)
# pop: short sine blip with pitch drop
tt=t(0.12); f=900*np.exp(-tt*25)+250; ph=2*np.pi*np.cumsum(f)/SR
save('pop',np.sin(ph)*np.exp(-tt*38))
# click / tick
tt=t(0.04); save('click',(rng.standard_normal(len(tt))*0.5+np.sin(2*np.pi*2500*tt))*np.exp(-tt*160))
# check ding (two partials)
tt=t(0.7); x=np.sin(2*np.pi*1318*tt)+0.5*np.sin(2*np.pi*1976*tt)+0.2*np.sin(2*np.pi*2637*tt)
save('ding',x*np.exp(-tt*7)*(1-np.exp(-tt*400)))
# impact boom: low sine drop + noise thump
tt=t(0.9); f=110*np.exp(-tt*6)+38; ph=2*np.pi*np.cumsum(f)/SR
x=np.sin(ph)*np.exp(-tt*4.5)+lp(rng.standard_normal(len(tt)),0.05)*np.exp(-tt*18)*2
save('impact',x)
# riser
d=1.2; tt=t(d); n=rng.standard_normal(len(tt)); f=np.geomspace(200,2500,len(tt))
x=bp_sweep(n,200,6000)*(tt/d)**2 + 0.3*np.sin(2*np.pi*np.cumsum(f)/SR)*(tt/d)**2
save('riser',x)
# typewriter-ish keys (for question box)
out=np.zeros(int(SR*0.9))
for k in range(9):
    s=int(SR*(k*0.09+rng.uniform(0,0.02))); tt=t(0.03)
    c=(rng.standard_normal(len(tt))*0.7+np.sin(2*np.pi*rng.uniform(1800,3000)*tt))*np.exp(-tt*220)
    out[s:s+len(c)]+=c[:len(out)-s]
save('typing',out)
# notification (message bubble) two-tone
tt=t(0.35); a=np.sin(2*np.pi*1046*tt)*np.exp(-tt*14); b=np.sin(2*np.pi*1568*tt)*np.exp(-tt*14)
x=np.zeros(int(SR*0.5)); x[:len(a)]+=a; o=int(SR*0.11); x[o:o+len(b)]+=b[:len(x)-o]
save('notify',x)
# cash register / calculator beeps
x=np.zeros(int(SR*0.6))
for k,fq in enumerate([2093,2349,2093]):
    tt=t(0.07); s=int(SR*k*0.13); x[s:s+len(tt)]+=np.sin(2*np.pi*fq*tt)*np.where(tt<0.06,1,0)
save('beeps',x)
# camera shutter / snap
tt=t(0.15); x=rng.standard_normal(len(tt))*(np.exp(-tt*80)+0.6*np.exp(-np.maximum(tt-0.06,0)*90)*(tt>0.06))
save('snap',x)
# chart grow (rising blips)
x=np.zeros(int(SR*0.8))
for k in range(5):
    tt=t(0.08); s=int(SR*k*0.13); fq=600*(1.26**k); x[s:s+len(tt)]+=np.sin(2*np.pi*fq*tt)*np.exp(-tt*30)
save('chart',x)
print(sorted(os.listdir(OUT)))
