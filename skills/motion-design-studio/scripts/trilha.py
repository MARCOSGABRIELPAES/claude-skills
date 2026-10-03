#!/usr/bin/env python3
"""trilha.py — trilha sintetizada NA MESMA LINHA DO TEMPO da imagem (só biblioteca padrão).

  python3 trilha.py --bpm 120 --dur 8 --hits 2.0,5.25,6.4 --whoosh 1.85,4.95 --silencio 4.6:5.1 --out out/trilha.wav

- batida: kick em cada tempo, chimbal no contratempo (a grade de batidas é a mesma do shotlist)
- --hits: impactos (grave + clique) nos quadros de contato — antecipados 0.03 s, como o olho espera
- --whoosh: sopros que TERMINAM no instante dado (coloque no corte da costura)
- --silencio a:b: vácuo antes do clímax (a batida some nesse trecho)
É um ponto de partida: troque por música licenciada quando o projeto pedir.
"""
import argparse, math, random, struct, wave

ap = argparse.ArgumentParser()
ap.add_argument('--bpm', type=float, default=120)
ap.add_argument('--dur', type=float, default=8)
ap.add_argument('--hits', default='')
ap.add_argument('--whoosh', default='')
ap.add_argument('--silencio', default='')
ap.add_argument('--out', default='out/trilha.wav')
a = ap.parse_args()

SR = 48000
N = int(a.dur * SR)
buf = [0.0] * N
rnd = random.Random(7)  # semente fixa: mesma trilha a cada render
lista = lambda s: [float(x) for x in s.split(',') if x.strip()]
vacuos = [tuple(map(float, p.split(':'))) for p in a.silencio.split(',') if p.strip()]
no_vacuo = lambda t: any(x <= t < y for x, y in vacuos)

def soma(t0, amostras, ganho=1.0):
    i0 = int(t0 * SR)
    for k, v in enumerate(amostras):
        if 0 <= i0 + k < N:
            buf[i0 + k] += v * ganho

def kick(dur=.35):
    out, fase = [], 0.0
    for k in range(int(dur * SR)):
        t = k / SR
        fase += 2 * math.pi * (45 + 75 * math.exp(-t * 30)) / SR
        out.append(math.sin(fase) * math.exp(-t * 9))
    return out

def chimbal(dur=.06):
    out, prev = [], 0.0
    for k in range(int(dur * SR)):
        n = rnd.uniform(-1, 1); out.append((n - prev) * .5 * math.exp(-k / SR * 70)); prev = n
    return out

def whoosh(dur=.5):  # ruído com envelope crescente, filtrado de leve: termina no corte
    out, lp = [], 0.0
    for k in range(int(dur * SR)):
        p = k / (dur * SR); lp += (rnd.uniform(-1, 1) - lp) * (.05 + .5 * p)
        out.append(lp * p ** 2.2)
    return out

def impacto(dur=1.2):
    out, fase = [], 0.0
    for k in range(int(dur * SR)):
        t = k / SR
        fase += 2 * math.pi * (38 + 60 * math.exp(-t * 18)) / SR
        clique = rnd.uniform(-1, 1) * math.exp(-t * 120) * .6
        out.append(math.sin(fase) * math.exp(-t * 3.2) + clique)
    return out

passo = 60 / a.bpm
K, C = kick(), chimbal()
b = 0
while b * passo < a.dur:
    t = b * passo
    if not no_vacuo(t):
        soma(t, K, .55)
        if not no_vacuo(t + passo / 2):
            soma(t + passo / 2, C, .18)
    b += 1

# pad: acorde grave sustentado (lá menor com nona), entra e sai em fade
for k in range(N):
    t = k / SR
    env = min(1, t / 1.5) * min(1, (a.dur - t) / 1.0) * (.25 if no_vacuo(t) else 1)
    v = sum(math.sin(2 * math.pi * f * t) for f in (110, 164.81, 220, 246.94)) / 4
    buf[k] += v * .09 * env * (1 + .15 * math.sin(2 * math.pi * .5 * t))

W = whoosh()
for t in lista(a.whoosh):
    soma(t - len(W) / SR, W, .5)
I = impacto()
for t in lista(a.hits):
    soma(t - .03, I, .8)

pico = max(1e-9, max(abs(v) for v in buf))
with wave.open(a.out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', int(v / pico * .89 * 32767)) for v in buf))
print(f'trilha -> {a.out}  ({a.dur:.2f} s, {a.bpm:g} BPM)')
