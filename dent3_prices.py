import subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
D="/tmp/claude-0/-home-user-Mjod/375c75bc-52d4-57d0-947b-16fcea146510/scratchpad/dent3/"
U="/root/.claude/uploads/375c75bc-52d4-57d0-947b-16fcea146510/"
OUT=sys.argv[1]; PREV=[float(x) for x in sys.argv[2:]]
T0,T1=13.10,21.55; FPS=30; W,H=1080,1920
CL=[(U+"d97d212d-IMG_0670.mov",0.3,1.80),(U+"fda1d1f8-IMG_0677.mov",0.8,2.30),
    (U+"c6f0981b-IMG_0675.mov",0.8,2.20),(U+"ba21060c-IMG_0681.mov",0.3,2.15)]
poster=Image.open(D+"pfull.png").convert("RGB")
def box(x0,y0,x1,y1):
    im=poster.crop((x0,y0,x1,y1)).convert("RGBA")
    m=Image.new("L",im.size,0); ImageDraw.Draw(m).rounded_rectangle((2,2,im.size[0]-3,im.size[1]-3),radius=30,fill=255)
    im.putalpha(m); return im
# (sprite, pos, spoken time)
B=[(box(578,380,964,567),(578,380),13.90),(box(142,380,528,567),(142,380),15.80),
   (box(578,598,964,784),(578,598),18.26),(box(142,598,528,784),(142,598),19.76)]
def shadow(sp):
    a=sp.split()[3]; s=Image.new("RGBA",(sp.size[0]+60,sp.size[1]+60),(0,0,0,0))
    s.paste(Image.new("RGBA",sp.size,(0,0,0,150)),(30,40),a); return s.filter(ImageFilter.GaussianBlur(14))
SH=[shadow(b[0]) for b in B]
def ease(p):
    if p>=1: return 1.0
    return 1+0.12*np.sin(p*np.pi)*(1-p)*2 if p>0.45 else 0.55+0.45*(p/0.45)*1.12
def comp(fr,t):
    for (sp,(x,y),ts),sh in zip(B,SH):
        if t<ts-0.05: continue
        p=(t-ts+0.05)/0.28; s=ease(min(p,1)); al=min(1,p*2.5)
        w,h=sp.size; cx,cy=x+w/2,y+h/2
        sw,shh=int(w*s),int(h*s)
        s1=sp.resize((sw,shh),Image.BILINEAR); h1=sh.resize((int(sh.size[0]*s),int(sh.size[1]*s)),Image.BILINEAR)
        if al<1:
            s1.putalpha(s1.split()[3].point(lambda v:int(v*al))); h1.putalpha(h1.split()[3].point(lambda v:int(v*al)))
        fr.alpha_composite(h1,(int(cx-h1.size[0]/2),int(cy-h1.size[1]/2)))
        fr.alpha_composite(s1,(int(cx-sw/2),int(cy-shh/2)))
    return fr
# decode broll concat as raw
args=["ffmpeg","-v","error"]; fc=[]
for i,(f,ss,d) in enumerate(CL):
    args+=["-ss",str(ss),"-t",str(d+0.1),"-i",f]
    fc.append(f"[{i}:v]scale=-2:1920,crop=1080:1920,setsar=1,fps=30,trim=duration={d},setpts=PTS-STARTPTS[v{i}]")
fc.append("".join(f"[v{i}]" for i in range(len(CL)))+f"concat=n={len(CL)}:v=1:a=0,format=rgb24[v]")
args+=["-filter_complex",";".join(fc),"-map","[v]","-f","rawvideo","-"]
dec=subprocess.Popen(args,stdout=subprocess.PIPE)
N=int(round((T1-T0)*FPS))
if PREV:
    frames={int(round((t-T0)*FPS)):t for t in PREV}
    for i in range(N):
        b=dec.stdout.read(W*H*3)
        if not b: break
        if i in frames:
            fr=Image.frombytes("RGB",(W,H),b).convert("RGBA")
            comp(fr,frames[i]).convert("RGB").save(D+f"out/p_{frames[i]}.png")
    dec.kill(); sys.exit()
SRC=D+"src.mov"
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-i",SRC,"-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r","30","-i","-",
   "-filter_complex",f"[1:v]setpts=PTS-STARTPTS+{T0}/TB[o];[0:v][o]overlay=eof_action=pass:enable='between(t,{T0},{T1-0.001})'[v]",
   "-map","[v]","-map","0:a","-c:v","libx264","-preset","medium","-crf","20","-maxrate","6000k","-bufsize","12000k","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",OUT],stdin=subprocess.PIPE)
last=None
for i in range(N):
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: b=last
    last=b
    fr=Image.frombytes("RGB",(W,H),b).convert("RGBA")
    enc.stdin.write(comp(fr,T0+i/FPS).convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); dec.kill()
