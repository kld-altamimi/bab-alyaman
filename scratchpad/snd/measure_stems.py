import sys
import numpy as np
from scipy.io import wavfile
from core import lufs, db
S='/home/claude/bab_out/m1_src/shots/'
tag = sys.argv[1] if len(sys.argv) > 1 else 'hold'
def load(n):
    sr,x=wavfile.read(S+n); x=x.astype(float)/32768.0
    return x if x.ndim==2 else np.stack([x,x],1)
mix=load('run_%s.wav'%tag); mu=load('run_%s_music.wav'%tag); fx=load('run_%s_sfx.wav'%tag); vo=load('run_%s_voice.wav'%tag)
print('%s: mix %.1f LUFS, peak %.1f dB, %d samples near full scale; music bus %.1f LUFS, effects bus %.1f LUFS, voice bus %.1f LUFS' % (tag, lufs(mix), db(np.abs(mix).max()), (np.abs(mix)>0.985).sum(), lufs(mu), lufs(fx), lufs(vo)))
env=np.sqrt(np.convolve((vo**2).mean(1), np.ones(4410)/4410, 'same'))
talk=env>10**(-40/20)
n=min(len(mix),len(mu),len(fx),len(vo)); talk=talk[:n]
r=lambda x: db(np.sqrt((x[:n][talk]**2).mean())+1e-12)
print('  while someone is speaking (%.1f s): voice %.1f dB, effects %.1f dB, music %.1f dB' % (talk.sum()/44100, r(vo), r(fx), r(mu)))
quiet=~talk
r2=lambda x: db(np.sqrt((x[:n][quiet]**2).mean())+1e-12)
print('  the rest of the time: effects %.1f dB, music %.1f dB' % (r2(fx), r2(mu)))
