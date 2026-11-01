"""Cuts the ElevenLabs Nepali recording (assets/nepali_voice_source.mp3) at its natural pauses and places every
phrase at its scene/subtitle start time -> assets/voiceover.wav (45 s, mono, cleaned + levelled).
(src_start, src_end, video_time, tempo)  -- source times were measured with silence detection."""
import subprocess
SRC="assets/nepali_voice_source.mp3"; PAD_A,PAD_B=0.03,0.05
SEGS=[
 (0.15, 2.41, 0.30,1.00),  # 1  नोइजी डट एलए हेर्न चाहनुहुन्छ?
 (2.90, 4.78, 2.75,1.00),  # 1  सुरु गर्ने सजिलो गाइड यहाँ छ।
 (5.19, 9.10, 5.30,1.00),  # 2  ...खोल्नुहोस्। माथि लगइन र साइन अप देखिन्छ।
 (9.46,10.44,10.30,1.00),  # 3  साइन अप थिच्नुहोस्।
 (10.83,15.38,12.30,1.00), # 3  इमेल र पासवर्ड ... जारी राख्नुहोस्।
 (15.87,18.51,17.30,1.00), # 4  लगइनपछि मेनु खोलेर रेफरल्स थिच्नुहोस्।
 (18.84,21.26,20.15,1.00), # 4  त्यसपछि "एड रेफरल कोड" थिच्नुहोस्।
 (21.64,25.04,25.30,1.05), # 5  कोड एम एस एच आर जे यु टाइप गर्नुहोस्,
 (25.35,27.14,28.62,1.05), # 5  अनि "एड रेफरर" थिच्नुहोस्।
 (27.48,28.25,30.40,1.05), # 5  स्वीकार भए,
 (28.54,30.29,31.21,1.05), # 5  नोइजीले पुष्टि सन्देश देखाउँछ।
 (30.69,33.98,34.00,1.00), # 6  नोइजी डट एलए मा जानुहोस् र चरणहरू पालना गर्नुहोस्।
 (34.34,37.96,38.45,1.00), # 6  सहभागी हुनुअघि, अभियानका नियम अवश्य जाँच्नुहोस्।
]
fc=[];outs=[]
for i,(s,e,d,t) in enumerate(SEGS):
    s0=s-PAD_A; e0=e+PAD_B; dur=(e0-s0)/t; dly=int(round((d-PAD_A)*1000))
    fc.append(f"[0:a]atrim={s0:.3f}:{e0:.3f},asetpts=PTS-STARTPTS,"+(f"atempo={t}," if t!=1 else "")+
              f"afade=t=in:d=0.025,afade=t=out:st={max(dur-0.05,0):.3f}:d=0.05,adelay={dly}:all=1[s{i}]")
    outs.append(f"[s{i}]")
fc.append("".join(outs)+f"amix=inputs={len(SEGS)}:normalize=0:duration=longest,apad=whole_dur=45,"
          "highpass=f=80,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=3,"
          "asetpts=PTS-STARTPTS[v]")
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",SRC,"-filter_complex",";".join(fc),"-map","[v]","-ar","44100","-ac","1","assets/_vo_raw.wav"],check=True)
# loudness: measure integrated LUFS, apply one fixed gain to reach -15 LUFS (a fixed gain never shifts timing), then peak-limit
import re
m=subprocess.run(["ffmpeg","-hide_banner","-nostats","-i","assets/_vo_raw.wav","-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
lufs=float(re.findall(r"I:\s+(-?[\d.]+) LUFS",m)[-1]); gain=-15-lufs
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","assets/_vo_raw.wav","-af",f"volume={gain:.2f}dB,alimiter=limit=0.89:level=0","-t","45","assets/voiceover.wav"],check=True)
import os; os.remove("assets/_vo_raw.wav")
print(f"wrote assets/voiceover.wav (measured {lufs:.1f} LUFS, gain {gain:+.1f} dB)")
