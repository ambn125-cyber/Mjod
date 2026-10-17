import subprocess, sys
SRC="/tmp/claude-0/-home-user-Mjod/375c75bc-52d4-57d0-947b-16fcea146510/scratchpad/v10x/src.mov"; VO="/root/.claude/uploads/375c75bc-52d4-57d0-947b-16fcea146510/cc674b42-copy_99CD3373-D661-411C-A683-5E7EF73CC2AC.mov"
C1="/root/.claude/uploads/375c75bc-52d4-57d0-947b-16fcea146510/d97d212d-IMG_0670.mov"; C6="/root/.claude/uploads/375c75bc-52d4-57d0-947b-16fcea146510/fda1d1f8-IMG_0677.mov"; C4="/root/.claude/uploads/375c75bc-52d4-57d0-947b-16fcea146510/c6f0981b-IMG_0675.mov"; C7="/root/.claude/uploads/375c75bc-52d4-57d0-947b-16fcea146510/26dd5f5d-IMG_0678.mov"; C2="/root/.claude/uploads/375c75bc-52d4-57d0-947b-16fcea146510/12e08d52-IMG_0671.mov"; C14="/root/.claude/uploads/375c75bc-52d4-57d0-947b-16fcea146510/0ed81367-_____________________4.mp4"
OUT=sys.argv[1]
V=[(SRC,0.00,2.90,'v'),(SRC,32.08,4.20,'v'),(SRC,10.06,2.84,'v'),
   (C1,0.3,2.28,'h'),(C6,1.0,2.30,'h'),(C4,1.0,2.30,'h'),(C7,0.0,2.32,'h'),(C2,0.0,2.10,'h'),
   (SRC,37.52,5.12,'v'),(SRC,44.76,3.82,'v'),(SRC,48.60,4.94,'v'),(SRC,54.38,3.46,'v'),(SRC,57.86,10.22,'v'),(SRC,68.10,2.16,'v'),
   (C14,26.0,3.0,'k')]
A=[(SRC,0.00,2.90,1),(SRC,32.08,4.20,1),(SRC,10.06,2.84,1),(VO,0.0,11.30,1.4),
   (SRC,37.52,5.12,1),(SRC,44.76,3.82,1),(SRC,48.60,4.94,1),(SRC,54.38,3.46,1),(SRC,57.86,10.22,1),(SRC,68.10,2.16,1),(C14,26.0,3.0,0.5)]
args=["ffmpeg","-v","error","-y"]; fc=[]
n=0
for f,ss,d,k in V:
    args+=["-ss",str(ss),"-t",str(d),"-i",f]
    if k=='h': flt="scale=-2:1920,crop=1080:1920"
    else: flt="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    fc.append(f"[{n}:v]{flt},setsar=1,fps=30,format=yuv420p,trim=duration={d},setpts=PTS-STARTPTS[v{n}]"); n+=1
vn=n
for f,ss,d,vol in A:
    args+=["-ss",str(ss),"-t",str(d),"-i",f]
    fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},atrim=duration={d},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.03}:d=0.03[a{n}]"); n+=1
fc.append("".join(f"[v{i}]" for i in range(vn))+f"concat=n={vn}:v=1:a=0[v]")
fc.append("".join(f"[a{i}]" for i in range(vn,n))+f"concat=n={n-vn}:v=0:a=1[a]")
args+=["-filter_complex",";".join(fc),"-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","16","-c:a","aac","-b:a","192k",OUT]
subprocess.run(args,check=True)
