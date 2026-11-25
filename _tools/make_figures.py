"""Research-style thumbnail figures computed from real signal processing / real data.
Usage: python3 _tools/make_figures.py assets/img/blog assets/img/projects <sklearn-data-dir> [thumb]
"""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects
from scipy import signal

OUT_BLOG, OUT_PROJ, SKDATA = sys.argv[1], sys.argv[2], sys.argv[3]
THUMB = len(sys.argv) > 4 and sys.argv[4] == "thumb"
K = .6 if THUMB else 1.0          # thumbnails: same pixels, ~1.7x larger text
FS = (12.8 * K, 7.2 * K)
SUFFIX = "-thumb" if THUMB else ""
SR = 16000
BG, FG, MUTED, GRID = "#0f1115", "#ecebe8", "#9aa0ab", "#2a2e36"
plt.rcParams.update({
    "font.family": ["Lato", "DejaVu Sans"], "font.size": 13,
    "axes.facecolor": BG, "figure.facecolor": BG, "savefig.facecolor": BG,
    "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.titlecolor": FG, "axes.titleweight": "bold", "axes.titlesize": 15, "axes.titlepad": 8,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "axes.labelsize": 11,
})
rng = np.random.default_rng(7)

# ---------- signal synthesis ----------
VOWELS = {"a": (730, 1090, 2440), "i": (270, 2290, 3010), "u": (300, 870, 2240),
          "e": (530, 1840, 2480), "o": (570, 840, 2410)}

def speech(dur, f0_base, seed, sr=SR):
    """Source-filter speech-like signal: harmonic glottal source + time-varying formants + fricatives."""
    r = np.random.default_rng(seed)
    n = int(dur * sr); t = np.arange(n) / sr
    # syllable plan
    env = np.zeros(n); F = np.zeros((3, n)); pos = int(.12 * sr)
    while pos < n - int(.15 * sr):
        L = int(r.uniform(.14, .30) * sr)
        v = VOWELS[r.choice(list(VOWELS))]
        seg = slice(pos, min(n, pos + L))
        m = seg.stop - seg.start; u = np.linspace(0, 1, m)
        w = (u ** .25) * np.exp(-2.2 * u) * (1 - u) ** .3          # fast attack, slow decay
        w = w / w.max() * r.uniform(.45, 1.0)                      # uneven loudness
        w *= 1 + .12 * np.sin(2 * np.pi * r.uniform(3, 6) * u * m / sr)
        env[seg] = np.maximum(env[seg], w)
        v2 = VOWELS[r.choice(list(VOWELS))]                        # diphthong glide
        g = np.clip((u - .35) / .5, 0, 1)
        for k in range(3): F[k, seg] = v[k] * (1 - .5 * g) + v2[k] * .5 * g
        pos += L + int(r.uniform(.02, .16) * sr)
    for k in range(3):  # smooth formant tracks; fill gaps with neighbours
        idx = np.nonzero(F[k])[0]
        F[k] = np.interp(np.arange(n), idx, F[k, idx])
        F[k] = np.convolve(F[k], np.ones(600) / 600, mode="same")
    f0 = f0_base * (1 + .12 * np.sin(2 * np.pi * .8 * t + r.uniform(0, 6)) - .08 * t / dur) * (1 + .01 * r.standard_normal(n).cumsum() / np.sqrt(n))
    phase = 2 * np.pi * np.cumsum(f0) / sr
    x = np.zeros(n)
    for h in range(1, 60):
        fh = h * f0
        a = sum(1 / (1 + ((fh - F[k]) / (60 + 40 * k)) ** 2) * (1, .6, .35)[k] for k in range(3)) / h ** .4
        a[fh > sr / 2 - 200] = 0
        x += a * np.sin(h * phase)
    x *= env
    # fricatives between some syllables
    noise = r.standard_normal(n)
    b, a_ = signal.butter(4, [3500, 7500], btype="band", fs=sr)
    fric = signal.lfilter(b, a_, noise)
    fe = np.zeros(n)
    for c in r.choice(np.arange(int(.2 * sr), n - int(.2 * sr)), 4):
        L = int(.07 * sr); fe[c:c + L] = np.hanning(L)
    x += .35 * fric * fe * (env < .3)
    x = x / np.max(np.abs(x))
    floor = signal.lfilter([1], [1, -.97], r.standard_normal(n)); floor *= .002 / np.std(floor)
    return x + floor

def music(dur, seed, sr=SR):
    r = np.random.default_rng(seed)
    n = int(dur * sr); t = np.arange(n) / sr; x = np.zeros(n)
    notes = [196, 247, 294, 392, 330, 262, 294, 220]
    step = dur / len(notes)
    for i, f in enumerate(notes):
        s = int(i * step * sr); L = n - s; tt = t[:L]
        dec = np.exp(-tt * 2.2) * np.minimum(1, tt / .012)
        tone = sum(np.sin(2 * np.pi * f * h * tt) / h ** 1.2 for h in range(1, 14) if f * h < 7800)
        x[s:] += .6 * tone * dec
    return x / np.max(np.abs(x))

def spec_db(x, sr=SR, nper=512):
    f, t, Z = signal.stft(x, fs=sr, nperseg=nper, noverlap=nper * 3 // 4)
    S = 20 * np.log10(np.abs(Z) + 1e-6)
    return f, t, S - S.max()

def show_spec(ax, x, title=None, cmap="magma", ylab=True, xlab=True, fmax=8000):
    f, t, S = spec_db(x)
    ax.pcolormesh(t, f, S, shading="gouraud", cmap=cmap, vmin=-75, vmax=0, rasterized=True)
    ax.set_ylim(0, fmax)
    ax.set_yticks([0, 2000, 4000, 6000, 8000][: 1 + fmax // 2000]); ax.set_yticklabels([f"{v//1000}k" for v in ax.get_yticks()])
    if ylab: ax.set_ylabel("Frequency (Hz)")
    if xlab: ax.set_xlabel("Time (s)")
    else: ax.set_xticklabels([])
    if title: ax.set_title(title, loc="left")
    for s in ax.spines.values(): s.set_visible(False)

def save(fig, path):
    path = path.replace(".png", SUFFIX + ".png")
    fig.savefig(path, dpi=100 / K)
    plt.close(fig)
    from PIL import Image
    im = Image.open(path).convert("RGB"); im.save(path.replace(".png", ".jpg"), quality=86, optimize=True, progressive=True)
    import os; os.remove(path)

def tag(ax, text, color):
    ax.text(.985, .94, text, transform=ax.transAxes, ha="right", va="top", fontsize=11, fontweight="bold", color=BG,
            bbox=dict(boxstyle="round,pad=.35,rounding_size=.6", fc=color, ec="none"))

DUR = 3.0
sp = speech(DUR, 165, 1)
mu = music(DUR, 2)
spB = speech(DUR, 105, 5)

# ===== BLOG 1: source separation (mixture -> speech + music) =====
fig = plt.figure(figsize=FS)
gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], left=.07, right=.98, top=.9, bottom=.11, wspace=.12, hspace=.32)
mix = .6 * sp + .5 * mu
a0 = fig.add_subplot(gs[:, 0]); show_spec(a0, mix, "Mixture"); tag(a0, "INPUT", "#f2b84b")
a1 = fig.add_subplot(gs[0, 1]); show_spec(a1, sp, "Separated: speech", xlab=False, ylab=False); tag(a1, "SOURCE 1", "#ff9db0")
a2 = fig.add_subplot(gs[1, 1]); show_spec(a2, mu, "Separated: music", ylab=False); tag(a2, "SOURCE 2", "#b8a6ff")
save(fig, f"{OUT_BLOG}/source-separation.png")

# ===== BLOG 2: audio metrics (reference vs degraded, measured SNR) =====
clean = sp
noise = rng.standard_normal(clean.size)
b, a_ = signal.butter(2, 3000, fs=SR); noise = signal.lfilter(b, a_, noise)
target_snr = 10.0
noise *= np.sqrt(np.mean(clean ** 2) / (np.mean(noise ** 2) * 10 ** (target_snr / 10)))
deg = clean + noise
snr = 10 * np.log10(np.mean(clean ** 2) / np.mean((deg - clean) ** 2))
fig = plt.figure(figsize=FS)
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], left=.07, right=.98, top=.9, bottom=.1, hspace=.38, wspace=.1)
aw = fig.add_subplot(gs[0, :])
tt = np.arange(clean.size) / SR
aw.plot(tt, deg, color="#ff9db0", lw=.6, alpha=.85, label="Degraded")
aw.plot(tt, clean, color="#ecebe8", lw=.7, label="Reference")
aw.set_xlim(0, DUR); aw.set_ylim(-1.3, 1.3); aw.set_yticks([-1, 0, 1]); aw.set_ylabel("Amplitude")
aw.set_title("Reference vs. degraded waveform", loc="left")
aw.legend(loc="upper left", bbox_to_anchor=(.0, 1.0), frameon=False, labelcolor=FG, fontsize=11, ncol=2, borderaxespad=.2)
for s in aw.spines.values(): s.set_visible(False)
tag(aw, f"SNR = {snr:.1f} dB", "#a6f0c0")
s1 = fig.add_subplot(gs[1, 0]); show_spec(s1, clean, "Reference")
s2 = fig.add_subplot(gs[1, 1]); show_spec(s2, deg, "Degraded", ylab=False)
save(fig, f"{OUT_BLOG}/audio-metrics.png")

# ===== BLOG 3: nomenclature (annotated waveform + spectrogram) =====
fig = plt.figure(figsize=FS)
gs = fig.add_gridspec(2, 1, height_ratios=[1, 2.2], left=.08, right=.97, top=.92, bottom=.1, hspace=.12)
aw = fig.add_subplot(gs[0]); seg = sp[: int(1.6 * SR)]; tt = np.arange(seg.size) / SR
aw.plot(tt, seg, color="#c8b6ff", lw=.7); aw.set_xlim(0, 1.6); aw.set_ylim(-1.1, 1.1); aw.set_xticklabels([])
aw.set_ylabel("Amplitude"); aw.set_title("Waveform  ·  Spectrogram  ·  Harmonics  ·  Formants", loc="left")
for s in aw.spines.values(): s.set_visible(False)
asp = fig.add_subplot(gs[1]); show_spec(asp, seg, cmap="magma", fmax=6000)
f, t, S = spec_db(seg)
# annotate a harmonic and a formant region at a voiced frame
fr = np.argmax(np.abs(seg[int(.3 * SR):int(1.2 * SR)])) / SR + .3
kw = dict(color=FG, fontsize=12, fontweight="bold", arrowprops=dict(arrowstyle="-|>", color=FG, lw=1.5),
          path_effects=[patheffects.withStroke(linewidth=3, foreground=BG)])
asp.annotate("harmonics", xy=(fr, 165 * 4), xytext=(fr + .25, 2400), **kw)
asp.annotate("formant", xy=(fr, 2300), xytext=(fr + .3, 4300), **kw)
asp.annotate("silence", xy=(.05, 3000), xytext=(.1, 5200), **kw)
save(fig, f"{OUT_BLOG}/audio-nomenclature.png")

# ===== BLOG 4: peak normalization (measured dBFS) =====
quiet = sp * np.concatenate([np.linspace(.08, .16, sp.size // 2), np.linspace(.16, .12, sp.size - sp.size // 2)])
peak_before = 20 * np.log10(np.max(np.abs(quiet)))
norm = quiet / np.max(np.abs(quiet))
peak_after = 20 * np.log10(np.max(np.abs(norm)))
fig, axs = plt.subplots(2, 1, figsize=FS, sharex=True, gridspec_kw=dict(left=.08, right=.97, top=.9, bottom=.1, hspace=.35))
for ax, x, title, col, pk in [(axs[0], quiet, "Before normalization", "#9aa0ab", peak_before), (axs[1], norm, "After peak normalization", "#5eead4", peak_after)]:
    ax.fill_between(np.arange(x.size) / SR, x, -x * 0 + x, color=col)
    ax.plot(np.arange(x.size) / SR, x, color=col, lw=.6)
    for y in (1, -1): ax.axhline(y, color="#f2b84b", lw=1.4, ls=(0, (6, 5)))
    ax.set_ylim(-1.25, 1.25); ax.set_yticks([-1, 0, 1]); ax.set_ylabel("Amplitude"); ax.set_title(title, loc="left")
    for s in ax.spines.values(): s.set_visible(False)
    tag(ax, f"peak {pk:+.1f} dBFS", "#f2b84b" if ax is axs[0] else "#5eead4")
axs[1].set_xlabel("Time (s)"); axs[1].set_xlim(0, DUR)
for ax in axs: ax.text(.01, 1.06, "0 dBFS", color="#f2b84b", ha="left", va="bottom", fontsize=10, fontweight="bold", transform=ax.get_yaxis_transform())
save(fig, f"{OUT_BLOG}/audio-normalization.png")

# ===== PROJECT: speech separation (two talkers) =====
fig = plt.figure(figsize=FS)
gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], left=.07, right=.98, top=.9, bottom=.11, wspace=.12, hspace=.32)
two = .6 * sp + .6 * spB
a0 = fig.add_subplot(gs[:, 0]); show_spec(a0, two, "Two-talker mixture", cmap="inferno"); tag(a0, "INPUT", "#f2b84b")
a1 = fig.add_subplot(gs[0, 1]); show_spec(a1, sp, "Speaker A", cmap="inferno", xlab=False, ylab=False); tag(a1, "SPEAKER A", "#ff9db0")
a2 = fig.add_subplot(gs[1, 1]); show_spec(a2, spB, "Speaker B", cmap="inferno", ylab=False); tag(a2, "SPEAKER B", "#7dd3fc")
save(fig, f"{OUT_PROJ}/speech-separation.png")

# ===== PROJECT: text classification (real 20 Newsgroups, TF-IDF -> SVD -> t-SNE) =====
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
cats = ["comp.graphics", "rec.sport.hockey", "sci.med", "sci.space"]
d = fetch_20newsgroups(data_home=SKDATA, subset="train", categories=cats, remove=("headers", "footers", "quotes"))
keep = [i for i, s in enumerate(d.data) if len(s.split()) > 25]
X = TfidfVectorizer(max_features=20000, stop_words="english", sublinear_tf=True, min_df=2).fit_transform([d.data[i] for i in keep])
y = d.target[keep]
Z = TruncatedSVD(60, random_state=0).fit_transform(X)
E = TSNE(2, perplexity=35, init="pca", random_state=0).fit_transform(Z)
fig, ax = plt.subplots(figsize=FS, gridspec_kw=dict(left=.03, right=.97, top=.9, bottom=.04))
cols = ["#7dd3fc", "#f2b84b", "#ff9db0", "#a6f0c0"]
names = ["Graphics", "Hockey", "Medicine", "Space"]
for k in range(4):
    m = y == k
    ax.scatter(E[m, 0], E[m, 1], s=9, c=cols[k], alpha=.8, linewidths=0, label=names[k])
    cx, cy = np.median(E[m], axis=0)
    ax.text(cx, cy, names[k], color=BG, fontsize=14, fontweight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=.35,rounding_size=.6", fc=cols[k], ec="none", alpha=.95))
ax.set_xticks([]); ax.set_yticks([]); [s.set_visible(False) for s in ax.spines.values()]
ax.set_title(("TF-IDF embeddings (t-SNE) · 20 Newsgroups" if THUMB else f"TF-IDF document embeddings (t-SNE), 20 Newsgroups · {len(y):,} documents"), loc="left")
save(fig, f"{OUT_PROJ}/text-classification.png")

# ===== PROJECT: VQA (public-domain photo + spectral-residual saliency + Q/A) =====
import matplotlib.cbook as cbook
from PIL import Image
img = np.asarray(Image.open(cbook.get_sample_data("grace_hopper.jpg")).convert("RGB")).astype(float) / 255
gray = img.mean(2)
small = np.asarray(Image.fromarray((gray * 255).astype(np.uint8)).resize((64, 64))).astype(float)
Fq = np.fft.fft2(small); logA = np.log(np.abs(Fq) + 1e-8); ph = np.angle(Fq)
resid = logA - signal.convolve2d(logA, np.ones((3, 3)) / 9, mode="same", boundary="wrap")
sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * ph))) ** 2
from scipy.ndimage import gaussian_filter
sal = gaussian_filter(sal, 2.5); sal = (sal - sal.min()) / (sal.max() - sal.min())
sal = np.asarray(Image.fromarray((sal * 255).astype(np.uint8)).resize((img.shape[1], img.shape[0]), Image.BICUBIC)) / 255
fig = plt.figure(figsize=FS)
ai = fig.add_axes([.06, .08, .42, .84]); ai.imshow(img); ai.imshow(sal, cmap="inferno", alpha=.45); ai.axis("off")
ai.set_title("Image + saliency map", loc="left")
at = fig.add_axes([.54, .08, .42, .84]); at.axis("off")
def card(y, label, text, fc, tc):
    at.text(0, y, label, fontsize=12, fontweight="bold", color=MUTED, transform=at.transAxes)
    at.text(0, y - .07, text, fontsize=21, fontweight="bold", color=tc, va="top", transform=at.transAxes, wrap=True,
            bbox=dict(boxstyle="round,pad=.7,rounding_size=.8", fc=fc, ec="none"))
card(.86, "QUESTION", "How many\npeople?" if THUMB else "How many people are\nin the image?", "#1c2029", FG)
card(.42, "ANSWER", "1 person", "#5eead4", BG)
at.text(0, .10, "image + question → answer", fontsize=14, color=MUTED, transform=at.transAxes)
save(fig, f"{OUT_PROJ}/vqa.png")

# ===== PROJECT: chatbot (intent + entity extraction, displaCy-style) =====
fig = plt.figure(figsize=FS); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1280); ax.set_ylim(720, 0)
ENT = {"JOB_TITLE": "#ff9db0", "LOCATION": "#7dd3fc", "SKILL": "#a6f0c0", "EXPERIENCE": "#f2b84b", "JOB": "#ff9db0", "LOC": "#7dd3fc"}
rend = fig.canvas.get_renderer()
def width(t):
    bb = t.get_window_extent(renderer=rend)
    return bb.width * 1280 / fig.bbox.width   # display px -> data units (axes span 0..1280)
def utter(y, who, tokens, intent):
    ax.text(70, y - 46, who, fontsize=13, fontweight="bold", color=MUTED)
    x = 70; space = 12
    for tok, ent in tokens:
        if ent:
            t1 = ax.text(x + 12, y, tok, fontsize=22, fontweight="bold", color=BG, va="center", zorder=3)
            w1 = width(t1)
            t2 = ax.text(x + 12 + w1 + 10, y + 1, ent, fontsize=10, fontweight="bold", color=BG, va="center", alpha=.7, zorder=3)
            w2 = width(t2)
            ax.add_patch(matplotlib.patches.FancyBboxPatch((x, y - 27), w1 + w2 + 34, 54, boxstyle="round,pad=0,rounding_size=12", fc=ENT[ent], ec="none", zorder=2))
            x += w1 + w2 + 34 + space
        else:
            t = ax.text(x, y, tok, fontsize=22, color=FG, va="center"); x += width(t) + space
    ti = ax.text(70, y + 52, "intent:", fontsize=13, color=MUTED)
    ax.text(70 + width(ti) + 8, y + 52, intent, fontsize=13, fontweight="bold", color="#c8b6ff")
ax.text(70, 70, "Intent classification + named-entity recognition", fontsize=17, fontweight="bold", color=FG)
if THUMB:
    utter(200, "USER", [("Find", None), ("Data Scientist", "JOB"), ("jobs", None), ("in", None), ("Kathmandu", "LOC")], "search_jobs")
    utter(400, "USER", [("I", None), ("know", None), ("Python", "SKILL"), ("and", None), ("PyTorch", "SKILL")], "update_profile")
else:
    utter(190, "USER", [("Looking", None), ("for", None), ("a", None), ("Data Scientist", "JOB_TITLE"), ("role", None), ("in", None), ("Kathmandu", "LOCATION")], "search_jobs")
    utter(380, "USER", [("I", None), ("have", None), ("3 years", "EXPERIENCE"), ("with", None), ("Python", "SKILL"), ("and", None), ("PyTorch", "SKILL")], "update_profile")
ax.text(70, 610, "BERT NER + intent  ·  RASA dialogue" if THUMB else "BERT fine-tuned for NER + intent  ·  RASA dialogue management", fontsize=13, color=MUTED)
save(fig, f"{OUT_PROJ}/chatbot.png")
print("done")
