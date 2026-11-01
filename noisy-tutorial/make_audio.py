"""Synthesizes an ORIGINAL royalty-free ambient track + UI sound effects (no samples, no downloads).
Output: assets/music_sfx.wav (45 s, 44.1 kHz stereo). Event times must match index.html (TAPS etc.)."""
import numpy as np, wave
SR=44100; DUR=45; N=SR*DUR
rng=np.random.default_rng(7)
t=np.arange(N)/SR
L=np.zeros(N); R=np.zeros(N)

def add(sig,at,pan=0.0,gain=1.0):
    i=int(at*SR); n=min(len(sig),N-i)
    if n<=0: return
    L[i:i+n]+=sig[:n]*gain*(1-max(pan,0)); R[i:i+n]+=sig[:n]*gain*(1+min(pan,0))

def env(n,a,r):
    e=np.ones(n); na=int(a*SR); nr=int(r*SR)
    e[:na]=np.linspace(0,1,na); e[-nr:]=np.linspace(1,0,nr); return e

# ---- music: 4-chord loop, 96 BPM, soft pad + pluck arpeggio + sub ----
bpm=96; beat=60/bpm; bar=4*beat
chords=[(57,60,64),(53,57,60),(48,52,55),(55,59,62)]       # Am F C G
mf=lambda m:440*2**((m-69)/12)
for b in range(int(DUR/bar)+1):
    ch=chords[b%4]; st=b*bar
    n=int(bar*SR*1.05); tt=np.arange(n)/SR
    pad=sum(np.sin(2*np.pi*mf(m)*tt)+.5*np.sin(2*np.pi*mf(m)*1.004*tt+1) for m in ch)/6
    add(pad*env(n,.5,.9)*.22,st,0,1)
    sub=np.sin(2*np.pi*mf(ch[0]-24)*tt)*env(n,.05,.4)
    add(sub*.22,st,0,1)
    for k in range(8):                                        # 8th-note plucks
        m=ch[[0,1,2,1,2,1,0,1][k]]+12
        nn=int(.5*SR); tp=np.arange(nn)/SR
        pl=(np.sin(2*np.pi*mf(m)*tp)+.3*np.sin(4*np.pi*mf(m)*tp))*np.exp(-tp*7)
        add(pl*.11,st+k*beat/2,(-.4 if k%2 else .4),1)
    for k in range(4):                                        # soft tick/hat
        nn=int(.05*SR); h=rng.standard_normal(nn)*np.exp(-np.arange(nn)/SR*90)
        h=np.diff(h,prepend=0); add(h*.05,st+k*beat+beat/2,0,1)
# gentle fade in/out
fade=np.minimum(1,np.minimum(t/1.5,(DUR-t)/2.0)); L*=fade; R*=fade
mus=.9

# ---- sfx ----
def whoosh(dur=.7):
    n=int(dur*SR); x=rng.standard_normal(n); e=np.sin(np.linspace(0,np.pi,n))**2
    # moving band-pass via cumulative one-pole sweep
    out=np.zeros(n); lp=0; bp=0
    for i in range(n):
        f=.02+.35*(i/n)**1.5
        lp+=f*(x[i]-lp); bp+=f*(lp-bp); out[i]=lp-bp
    return out/np.max(np.abs(out))*e*.5
def tap():
    n=int(.12*SR); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*(900-3000*tt)*tt)*np.exp(-tt*45)+.3*np.sin(2*np.pi*180*tt)*np.exp(-tt*30))*.7
def tick():
    n=int(.04*SR); tt=np.arange(n)/SR
    return np.sin(2*np.pi*2200*tt)*np.exp(-tt*140)*.35
def chime():
    out=np.zeros(int(1.6*SR)); tt=np.arange(len(out))/SR
    for f,d in((880,0),(1318.5,.12),(1760,.24)):
        i=int(d*SR); s=np.sin(2*np.pi*f*tt[:len(out)-i])*np.exp(-tt[:len(out)-i]*3.2)
        out[i:]+=s*.35
    return out
for at in (4.4,10.6,16.9,18.55,20.4,25.85,29.95,32.9): add(whoosh(.55 if at not in (4.4,32.9) else .8),at,0,.55)
for at in (5.6,10.5,18.5,20.2,25.8,29.4): add(tap(),at,0,.9)
for i in range(6): add(tick(),26.8+.27*i,0,1)
add(chime(),30.2,0,.9)
add(chime()[:int(1.2*SR)],35.9,0,.35)      # soft chime when the end-card code appears
# normalise
peak=max(np.max(np.abs(L)),np.max(np.abs(R)));L/=peak/.85;R/=peak/.85
pcm=(np.stack([L,R],1)*32767).astype('<i2')
with wave.open('assets/music_sfx.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes())
print('wrote assets/music_sfx.wav')
