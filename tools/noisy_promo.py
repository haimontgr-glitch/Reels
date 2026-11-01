import subprocess, os
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,D,X=1080,1920,30,3.0,0.5
F="/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
slides=[  # (lines, highlight line index, bg, fg, hl)
 (["Editors:","stop editing","for free."],1,(10,10,12),(255,255,255),(255,214,0)),
 (["Get paid","per 1,000 views","on TikTok."],1,(255,255,255),(10,10,12),(0,150,90)),
 (["Easy access","for new users."],0,(10,10,12),(255,255,255),(255,214,0)),
 (["Post an edit.","Submit the link."],1,(255,255,255),(10,10,12),(0,150,90)),
 (["Search","noisy.la"],1,(10,10,12),(255,255,255),(255,214,0)),
]
os.makedirs("/tmp/ns",exist_ok=True)
clips=[]
for i,(lines,hl,bg,fg,hc) in enumerate(slides):
    im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(F,120); y=H//2-len(lines)*85
    for j,t in enumerate(lines):
        w=d.textlength(t,font=f)
        while w>W-120: f=ImageFont.truetype(F,f.size-6); w=d.textlength(t,font=f)
        d.text(((W-w)/2,y),t,font=f,fill=hc if j==hl else fg); y+=170
    p=f"/tmp/ns/s{i}.png"; im.save(p)
    out=f"/tmp/ns/c{i}.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",p,"-vf",
      f"zoompan=z='1+0.0008*on':d={int(D*FPS)}:s={W}x{H}:fps={FPS},format=yuv420p",
      "-t",str(D),out],check=True); clips.append(out)
ins=sum([["-i",c] for c in clips],[])
fc="";last="0:v";off=D-X
for k in range(1,len(clips)):
    fc+=f"[{last}][{k}:v]xfade=transition=slideleft:duration={X}:offset={off}[v{k}];";last=f"v{k}";off+=D-X
subprocess.run(["ffmpeg","-y","-loglevel","error",*ins,"-filter_complex",fc.rstrip(";"),"-map",f"[{last}]",
  "-r",str(FPS),"-c:v","libx264","-pix_fmt","yuv420p","videos/noisy_promo.mp4"],check=True)
