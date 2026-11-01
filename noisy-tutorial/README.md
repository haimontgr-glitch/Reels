# Noisy.la referral-code tutorial (faceless, 1080×1920, 45 s)

Files
- `index.html` – the whole animated video (HTML/CSS/JS, deterministic timeline; open it in Chrome to preview with Play/scrub).
- `make_audio.py` – synthesizes an original royalty-free music bed + sound effects → `assets/music_sfx.wav`.
- `render.js` – renders every frame with headless Chromium and encodes `../videos/noisy_tutorial.mp4` with ffmpeg.
- `script_en.txt`, `subtitles_ne.srt`, `storyboard.md` – voiceover script, Nepali subtitles, scene-by-scene storyboard.

## Add the English voiceover
1. Record the 6 lines in `script_en.txt` (phone voice-recorder or Audacity; quiet room, calm tone).
   Or generate it on a machine with internet: `pip install edge-tts` then
   `edge-tts --voice en-US-GuyNeural --text "<line>" --write-media line1.mp3` (repeat per line).
2. Place each line at the time shown in `script_en.txt` (e.g. line 2 starts at 5.3 s) and export ONE file,
   45 s long or shorter: `assets/voiceover.mp3` (wav/m4a also accepted).
3. Re-run the render (below). If `assets/voiceover.*` exists it is mixed in automatically and the music is lowered.
   The browser preview (`index.html`) also plays `assets/voiceover.mp3` and `assets/music_sfx.wav` if present.

## Music and sound effects
`assets/music_sfx.wav` is synthesized by `make_audio.py` (no samples, so no licensing). To use a different track:
replace the wav with your own royalty-free file (YouTube Audio Library / Pixabay – check its licence), keep the name
`music_sfx.wav` and keep it ≥45 s; sound effects are baked into the same file, so mute them by editing `make_audio.py`.
TikTok's own trending sounds can also be added in the TikTok app after upload; render without VO music if you do.

## Export the MP4
```bash
cd noisy-tutorial
python3 make_audio.py                      # only if you changed the audio
node render.js ../videos/noisy_tutorial.mp4   # needs node, playwright (chromium) and ffmpeg; ~2-3 min
node render.js --frames 5,12,22,31,36      # optional: dump check frames to /tmp/frames
```
No-code alternative: open `index.html`, press Play and screen-record the page at 1080×1920, or use any
HTML-to-video recorder; the render script is more accurate (exact 30 fps, exact sync).

Devanagari font: Noto Sans Devanagari (`apt-get install fonts-noto-core`).

## Accuracy notes
Screens are mockups rebuilt from your screenshots. The sign-up form, Referrals page, "Enter Referral Code" sheet and
confirmation banner all exist on the real site per your screenshots. Personal data (email, username, own code) is
replaced with placeholders. The video never promises earnings; the end card says rewards may change and are not guaranteed.
