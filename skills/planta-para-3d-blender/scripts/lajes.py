# -*- coding: utf-8 -*-
"""Contorno da LAJE CONSTRUIDA de cada pavimento.

O problema que isto resolve: plantas de implantacao desenham os pavimentos
inferiores esmaecidos, por transparencia, para dar contexto. Quem modela sem
perceber isso constroi laje onde o projeto tem ceu aberto.

Criterio: so e construido onde existe traco escuro de verdade. Num trecho
esmaecido a fracao de pixels com V<0.5 cai praticamente a zero (medido: 0.00%
contra 7-60% em tudo que e construido), entao o teste separa os dois casos com
folga enorme.

Le projeto.json e escreve lajes.json.
"""
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
Image.MAX_IMAGE_PIXELS = None

CEL = 32          # celula da grade de "tem desenho real aqui?"
LIMIAR = 0.004    # fracao minima de pixel escuro por celula


def px2m(pts, pxm, origem, rot_rad):
    p = (np.asarray(pts, float) - origem) / pxm
    x, y = p[:, 0], -p[:, 1]                      # Y da planta cresce para baixo
    c, s = np.cos(rot_rad), np.sin(rot_rad)
    return np.stack([x * c - y * s, x * s + y * c], 1)


def blocos(m, cel):
    h, w = m.shape
    H, W = h // cel * cel, w // cel * cel
    return m[:H, :W].reshape(H // cel, cel, W // cel, cel).mean(axis=(1, 3))


def laje(caminho, ds, pxm, origem, rot_rad, area_min=60.0):
    im = Image.open(caminho).convert("RGB")
    a = np.asarray(im.resize((im.size[0] // ds, im.size[1] // ds), Image.LANCZOS)).astype(np.int16)
    R, B = a[:, :, 0], a[:, :, 2]
    V = a.max(axis=2) / 255.0

    # 1) area desenhada: exclui o branco do papel e o cinza neutro do entorno
    desenho = ((R - B) >= 6) | ((B - R) >= 8) | (V < 0.40)
    # 2) so onde ha traco escuro real -> descarta o pavimento esmaecido
    real = blocos(V < 0.50, CEL) > LIMIAR
    real = ndi.binary_fill_holes(ndi.binary_closing(real, np.ones((5, 5))))
    real = np.kron(real, np.ones((CEL, CEL), bool))

    m = np.zeros_like(desenho)
    h, w = real.shape
    m[:h, :w] = desenho[:h, :w] & real
    m = ndi.binary_fill_holes(ndi.binary_closing(m, np.ones((15, 15))))
    m = ndi.binary_opening(m, np.ones((9, 9)))

    lab, n = ndi.label(m)
    sz = ndi.sum(m, lab, range(1, n + 1))
    out, area = [], 0.0
    for i in range(n):
        if sz[i] / pxm ** 2 <= area_min:
            continue
        sub = (lab == i + 1)
        area += sub.sum() / pxm ** 2
        c = max(measure.find_contours(np.pad(sub.astype(float), 1), 0.5), key=len)
        s = measure.approximate_polygon(c, tolerance=6)
        out.append(np.round(px2m(np.stack([s[:, 1] - 1, s[:, 0] - 1], 1), pxm, origem, rot_rad), 3).tolist())
    return out, area


def main():
    cfg = json.load(open("projeto.json", encoding="utf-8"))
    ds = cfg.get("downsample", 2)
    pxm = cfg["escala_px_por_m"] / ds
    origem = np.array(cfg["origem_px"], float) / ds
    rot = np.deg2rad(cfg.get("rotacao_graus", 0.0))

    res = {"escala_px_por_m": cfg["escala_px_por_m"], "niveis": {}}
    for cod, nv in cfg["niveis"].items():
        p, a = laje(nv["arquivo"], ds, pxm, origem, rot)
        res["niveis"][cod] = {"laje": p, "area_m2": round(a, 1)}
        print(f"  {cod:4s} {len(p)} poligono(s)  area construida = {a:8.1f} m2")
    json.dump(res, open("lajes.json", "w"))
    print("-> lajes.json")


if __name__ == "__main__":
    main()
