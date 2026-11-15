"""Fable 5.2 independent re-run of experiment 003 (fade-triggered unit closing a wave loop).

This is a standalone numpy re-implementation of the WaveFieldNode update rule and the
FadingHistorySpikeNode rule, written from the node sources. It does NOT import the
upstream PerceptionLab classes (Sol's runners in PerceptionLabAI do that).
Thresholds are held FROZEN at the 003 calibration (arm 0.72201012, release 0.320893387)
while one parameter at a time is changed. Sol's 003 table recalibrates thresholds per
geometry, so the two sets of numbers answer different questions.

Run:  python receipts/fable_rerun_003.py
Output of the run on 15 Nov 2026 is saved in receipts/fable_rerun_003_output.txt
"""
import numpy as np, math
class Field:
    def __init__(s,size=96,speed=.5,damp=.006,sub=4,gain=.6,clip=4.0):
        s.n=size;s.c2=speed**2;s.damp=damp;s.sub=sub;s.gain=gain;s.clip=clip
        s.f=np.zeros((size,size),np.float32);s.v=np.zeros_like(s.f)
        y=int(.5*size);xs=np.linspace(.2*size,.92*size,8);s.xy=[(int(round(x)),y) for x in xs]
        band=max(2,int(.06*size));r=np.ones(size,np.float32);q=np.linspace(.9,1,band,dtype=np.float32)
        r[:band]=q;r[-band:]=q[::-1];s.ab=np.outer(r,r)
        rad=12;yy,xx=np.mgrid[-rad:rad+1,-rad:rad+1];s.g=np.exp(-(xx*xx+yy*yy)/32.).astype(np.float32);s.rad=rad
        s.maxabs=0
    def inject(s,i,a):
        x,y=s.xy[i];r=s.rad
        y0,y1,x0,x1=max(0,y-r),min(s.n,y+r+1),max(0,x-r),min(s.n,x+r+1)
        s.v[y0:y1,x0:x1]+=s.gain*a*s.g[y0-(y-r):y1-(y-r),x0-(x-r):x1-(x-r)]
    def step(s):
        for _ in range(s.sub):
            p=np.pad(s.f,1,mode='edge')
            s.v+=s.c2*(p[1:-1,2:]+p[1:-1,:-2]+p[2:,1:-1]+p[:-2,1:-1]-4*s.f)
            s.v*=(1-s.damp);s.f+=s.v;s.f*=s.ab;s.v*=s.ab
        s.maxabs=max(s.maxabs,float(np.abs(s.f).max()))
        if s.clip: np.clip(s.f,-s.clip,s.clip,out=s.f);np.clip(s.v,-s.clip,s.clip,out=s.v)
    def read(s,i):
        x,y=s.xy[i];return float(s.f[y-3:y+4,x-3:x+4].mean())
def run(T=1500,reader=1,decay=.9,arm=.72201012,rel=.320893387,amp=2.0,damp=.006,clip=4.0,kick=None,size=96):
    F=Field(size=size,damp=damp,clip=clip);tr=0;armed=False;cd=0;pulse=0;fires=[];peaks=[]
    for t in range(1,T+1):
        w=pulse+(1.0 if t in(19,20) else 0)
        if w: F.inject(0,w)
        if kick and t==kick[0]: F.inject(kick[1],kick[2])
        F.step()
        a=abs(F.read(reader));tr=decay*tr+(1-decay)*a;pulse=0
        if cd>0:cd-=1
        if not armed and tr>=arm:armed=True
        if armed and tr<=rel and cd==0:
            pulse=amp;fires.append(t);cd=3;armed=False
    return fires,F.maxabs
def per(f): 
    d=np.diff(f[-8:]) if len(f)>8 else np.diff(f); return (round(float(d.mean()),2),round(float(d.std()),2)) if len(d) else None
f,m=run();print("base fires",f[:14],"period",per(f),"n",len(f),"max|f|",round(m,2))
f2,m2=run(clip=None);print("noclip period",per(f2),"n",len(f2),"max",round(m2,2))
for r in (1,2,3,4,5): f,_=run(reader=r);print("reader",r,"n",len(f),"period",per(f))
for d in (.8,.85,.9,.93,.95): f,_=run(decay=d);print("decay",d,"n",len(f),"period",per(f))
for dm in (.003,.006,.012,.02): f,_=run(damp=dm);print("damp",dm,"n",len(f),"period",per(f))
for a in (1.0,1.5,2.0,3.0): f,_=run(amp=a);print("amp",a,"n",len(f),"period",per(f))
# phase response: kick at aperture 4 at phase after the 15th spike
base,_=run(T=900);k=15;t0=base[k];P=base[k+1]-base[k]
print("PRC base period",P)
for ph in range(2,P,4):
    for sgn in (1.0,):
        f,_=run(T=900,kick=(t0+ph,4,sgn));nx=[x for x in f if x>t0][:3]
        print(" kick at phase",ph,"next spike shift",nx[0]-base[k+1],"then",nx[1]-base[k+2] if len(nx)>1 else None)
