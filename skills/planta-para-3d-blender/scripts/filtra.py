# -*- coding: utf-8 -*-
"""Recorta os elementos de cada pavimento pela laje daquele pavimento.

Sem isto o modelo herda o desenho esmaecido dos niveis de baixo: piscinas
fantasma flutuando onde o projeto tem ceu aberto.
"""
import json
import numpy as np
from matplotlib.path import Path

g = json.load(open("geometria.json"))
lj = json.load(open("lajes.json"))
mant = drop = 0
for cod, dados in g["niveis"].items():
    paths = [Path(np.asarray(p)) for p in lj["niveis"][cod]["laje"]]
    for classe, lista in dados["elementos"].items():
        novo = []
        for el in lista:
            P = np.asarray(el["pts"])
            dentro = any(pa.contains_point(P.mean(axis=0)) for pa in paths) or \
                     any(pa.contains_points(P).mean() > 0.5 for pa in paths)
            if dentro:
                novo.append(el); mant += 1
            else:
                drop += 1
        dados["elementos"][classe] = novo
    print(f"  {cod}: " + "  ".join(f"{c}={len(p)}" for c, p in dados["elementos"].items()))
json.dump(g, open("geometria_filtrada.json", "w"))
print(f"descartados fora da laje: {drop}  -> geometria_filtrada.json")
