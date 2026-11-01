// Usage: node render.js [out.mp4] [--frames 1,8,12.5]   (needs: node + playwright + ffmpeg)
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const args = process.argv.slice(2);
const fi = args.indexOf('--frames');
const out = args[0] && !args[0].startsWith('--') ? args[0] : 'noisy_tutorial.mp4';
const FPS = 30, DUR = 45;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(__dirname, 'index.html') + '?render=1');
  await p.evaluate(() => document.fonts.ready);
  if (fi > -1) {
    fs.mkdirSync('/tmp/frames', { recursive: true });
    for (const s of args[fi + 1].split(',')) {
      await p.evaluate(t => window.__render(t), parseFloat(s));
      await p.screenshot({ path: `/tmp/frames/f_${s}.png` });
    }
    return b.close();
  }
  // audio: music + sfx stems; if a voiceover exists the MUSIC is automatically ducked (sidechain) while the voice speaks
  const a = path.resolve(__dirname, 'assets');
  const vo = ['voiceover.wav', 'voiceover.mp3', 'voiceover.m4a'].map(f => path.join(a, f)).find(fs.existsSync);
  const ff = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(a, 'music_only.wav'), '-i', path.join(a, 'sfx_only.wav')];
  let fc;
  if (vo) { ff.push('-i', vo);
    fc = '[3:a]apad,asplit=2[vo][key];' +
         '[1:a]volume=0.8[mus];[mus][key]sidechaincompress=threshold=0.02:ratio=3.5:attack=40:release=900:makeup=1[duck];' +
         '[2:a]volume=0.8[sfx];[vo]volume=1.0[v];' +
         '[duck][sfx][v]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95[a]'; }
  else fc = '[1:a][2:a]amix=inputs=2:duration=first:normalize=0[a]';
  ff.push('-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-t', String(DUR), '-r', String(FPS),
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out);
  const f = spawn('ffmpeg', ff, { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = DUR * FPS;
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.__render(t), i / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
    if (!f.stdin.write(buf)) await new Promise(r => f.stdin.once('drain', r));
  }
  f.stdin.end(); await new Promise(r => f.on('close', r)); await b.close();
  console.log('done', out, vo ? '(with voiceover)' : '(no voiceover file found)');
})();
