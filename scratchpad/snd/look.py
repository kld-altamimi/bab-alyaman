# look.py - spectrogram sheets, since the sound has to be judged by eye here.
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal
from core import SR


def sheet(items, path, fmax=8000, cols=3, nfft=1024, hop=128, w=5.0, h=2.6, dbrange=70):
    rows = (len(items) + cols - 1) // cols
    fig, axes = plt.subplots(rows * 2, cols, figsize=(w * cols, (h + 0.9) * rows),
                             gridspec_kw={'height_ratios': [3, 1] * rows}, squeeze=False)
    for i, (name, y) in enumerate(items):
        r, c = divmod(i, cols)
        y = np.asarray(y)
        if y.ndim == 2:
            y = y.mean(axis=1)
        f, t, S = signal.spectrogram(y, SR, nperseg=nfft, noverlap=nfft - hop, window='hann', mode='magnitude')
        S = 20 * np.log10(S + 1e-9)
        top = S.max()
        ax = axes[r * 2][c]
        ax.pcolormesh(t, f, S, vmin=top - dbrange, vmax=top, cmap='magma', shading='auto')
        ax.set_ylim(0, fmax)
        ax.set_title(name, fontsize=9)
        ax.tick_params(labelsize=7)
        ax2 = axes[r * 2 + 1][c]
        ax2.plot(np.arange(len(y)) / SR, y, lw=0.4, color='#254a78')
        ax2.set_xlim(0, len(y) / SR)
        ax2.set_ylim(-1.05 * np.abs(y).max() - 1e-6, 1.05 * np.abs(y).max() + 1e-6)
        ax2.tick_params(labelsize=6)
    for j in range(len(items), rows * cols):
        r, c = divmod(j, cols)
        axes[r * 2][c].axis('off')
        axes[r * 2 + 1][c].axis('off')
    plt.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)
