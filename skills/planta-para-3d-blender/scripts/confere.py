# -*- coding: utf-8 -*-
"""Sobrepoe o contorno extraido de volta na planta original.

Este passo nao e opcional. E a unica forma de afirmar "o modelo esta fiel" sem
que isso seja opiniao: se o contorno vermelho corre em cima da borda desenhada,
esta fiel; se corre por dentro ou por fora, nao esta. Olhe a imagem antes de
levar qualquer coisa para o Blender.

Gera confere_lajes.png com um painel por pavimento.
"""
import json
import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None

cfg = json.load(open("projeto.json", encoding="utf-8"))
lj = json.load(open("lajes.json"))
PXM = cfg["escala_px_por_m"]
ORIG = np.array(cfg["origem_px"], float)
ROT = np.deg2rad(cfg.get("rotacao_graus", 0.0))


def m2px(P):
    P = np.asarray(P)
    c, s = np.cos(-ROT), np.sin(-ROT)
    x = P[:, 0] * c - P[:, 1] * s
    y = P[:, 0] * s + P[:, 1] * c
    return np.stack([x * PXM + ORIG[0], -y * PXM + ORIG[1]], 1)


paineis = []
L = 1300
for cod, nv in cfg["niveis"].items():
    im = Image.open(nv["arquivo"]).convert("RGB")
    d = ImageDraw.Draw(im)
    for poly in lj["niveis"][cod]["laje"]:
        p = [tuple(v) for v in m2px(poly)]
        d.line(p + [p[0]], fill=(255, 0, 0), width=max(4, im.size[0] // 800))
    h = int(im.size[1] * L / im.size[0])
    im = im.resize((L, h))
    ImageDraw.Draw(im).text((10, 8), f"{cod}   {lj['niveis'][cod]['area_m2']} m2", fill=(255, 0, 0))
    paineis.append(im)

out = Image.new("RGB", (L, sum(p.size[1] for p in paineis)), (255, 255, 255))
y = 0
for p in paineis:
    out.paste(p, (0, y)); y += p.size[1]
out.save("confere_lajes.png")
print("-> confere_lajes.png   ABRA E OLHE antes de modelar")
