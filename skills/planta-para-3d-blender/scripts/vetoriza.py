# -*- coding: utf-8 -*-
"""Vetoriza cada pavimento em poligonos por classe de superficie.

Duas familias de deteccao, porque as plantas renderizadas misturam duas
linguagens graficas:

  - SUPERFICIES (agua, areia, vegetacao, madeira, vaga): manchas de cor. Regras
    em HSV. Laminas d'agua com textura fotografica de caustica sao classificadas
    numa copia borrada, senao a caustica quebra a mancha em milhares de pixels.

  - PAREDES: linha escura fina sobre fundo de qualquer tom. Limiar de brilho
    global nao serve (pega piso escuro de academia, perde parede clara). O
    bottom-hat -- grey_closing menos a imagem -- realca linha fina escura
    independente do fundo. A abertura por disco descarta rejunte de piso e
    contorno fino de mobiliario; o que sobra, alongado, e parede; o que sobra
    compacto e mobiliario.

Le projeto.json e escreve geometria.json.
"""
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure, color as skcolor, morphology as morph
Image.MAX_IMAGE_PIXELS = None


def px2m(pts, pxm, origem, rot_rad):
    p = (np.asarray(pts, float) - origem) / pxm
    x, y = p[:, 0], -p[:, 1]
    c, s = np.cos(rot_rad), np.sin(rot_rad)
    return np.stack([x * c - y * s, x * s + y * c], 1)


def classes(a, tem_agua=True, tem_vaga=True, parede_modo="linha", parede_limiar=0.22):
    hv = skcolor.rgb2hsv(a.astype(np.float32) / 255.0)
    Hd, S, V = hv[:, :, 0] * 360, hv[:, :, 1], hv[:, :, 2]
    R, G, B = (a[:, :, i].astype(int) for i in range(3))
    c = {}

    c["areia"]     = (Hd > 28) & (Hd < 56) & (S > 0.16) & (S < 0.45) & (V > 0.62)
    c["vegetacao"] = (Hd > 58) & (Hd < 160) & (S > 0.18) & (V < 0.75)
    c["madeira"]   = (Hd > 15) & (Hd < 42) & (S > 0.33) & (V > 0.30) & (V < 0.82)

    if tem_vaga:
        teal  = (Hd > 150) & (Hd < 205) & (S > 0.10) & (S < 0.30) & (V > 0.40) & (V < 0.72) & (B >= G)
        oliva = (Hd > 70) & (Hd < 130) & (S > 0.04) & (S < 0.30) & (V > 0.28) & (V < 0.60) & (G > R) & (G > B)
        c["vaga"] = teal | oliva
    else:
        c["vaga"] = np.zeros(a.shape[:2], bool)

    agua = (Hd > 178) & (Hd < 240) & (S >= 0.28) & ((B - G) >= 6) & (V > 0.30)
    if tem_agua:
        # laminas com caustica: classifica no borrado
        ab = ndi.uniform_filter(a.astype(np.float32), size=(15, 15, 1))
        hb = skcolor.rgb2hsv(ab / 255.0)
        Hb, Sb, Vb = hb[:, :, 0] * 360, hb[:, :, 1], hb[:, :, 2]
        Rb, Gb, Bb = ab[:, :, 0], ab[:, :, 1], ab[:, :, 2]
        agua |= (Hb > 145) & (Hb < 205) & (Sb > 0.12) & (Vb > 0.45) & ((Gb - Rb) > 12) & ((Bb - Rb) > 8)
        agua |= (Hb > 100) & (Hb < 142) & (Sb > 0.07) & (Sb < 0.22) & (Vb > 0.68)   # verde-agua claro
    c["agua"] = agua

    # paredes e mobiliario
    #
    # Plantas vem em duas linguagens graficas e cada uma pede um detector:
    #   "linha"  -> parede desenhada como contorno escuro fino (implantacoes).
    #   "poche"  -> parede preenchida de preto solido (planta de apartamento).
    # No modo poche a rede de paredes e um unico componente conectado, entao o
    # filtro de alongamento do modo linha a classificaria como mobiliario.
    # Para escolher: meca a fracao de pixel bem escuro dentro da laje. Acima de
    # ~3% e poche; linha fina raramente passa de 1%.
    g = a.mean(axis=2).astype(np.int16)
    m = ndi.binary_closing((ndi.grey_closing(g, size=21) - g) > 42, np.ones((3, 3)))
    m = ndi.binary_opening(m, morph.disk(3))
    veg = (Hd > 58) & (Hd < 160) & (S > 0.14)
    m &= ~ndi.binary_dilation(veg, np.ones((5, 5)))
    if parede_modo == "poche":
        par = V < parede_limiar
        par = ndi.binary_closing(par, np.ones((3, 3)))
        m &= ~ndi.binary_dilation(par, np.ones((5, 5)))     # mobiliario = o resto
        lab, _ = ndi.label(m)
        mob = np.zeros_like(m)
        for i, sl in enumerate(ndi.find_objects(lab)):
            sub = (lab[sl] == i + 1)
            if int(sub.sum()) >= 300: mob[sl] |= sub
        c["parede"] = par
        c["mobiliario"] = mob
        return c

    lab, _ = ndi.label(m)
    par = np.zeros_like(m); mob = np.zeros_like(m)
    for i, sl in enumerate(ndi.find_objects(lab)):
        sub = (lab[sl] == i + 1); area = int(sub.sum())
        if area < 150:
            continue
        d = max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start)
        if d >= 55 and area / float(d) <= 18:     # alongado e fino -> parede
            par[sl] |= sub
        elif area >= 400:                          # compacto -> mobiliario
            mob[sl] |= sub
    c["parede"] = par
    c["mobiliario"] = mob
    return c


def polys(mask, pxm, origem, rot_rad, min_m2, tol, close, keep, preencher=True):
    m = ndi.binary_opening(ndi.binary_closing(mask, np.ones((close, close))), np.ones((3, 3)))
    if preencher:
        m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m)
    if n == 0:
        return []
    sz = ndi.sum(m, lab, range(1, n + 1)) / pxm ** 2
    out = []
    for i in [i for i in np.argsort(sz)[::-1][:keep] if sz[i] >= min_m2]:
        sub = (lab == i + 1)
        sl = ndi.find_objects(sub.astype(np.uint8))[0]
        y0, x0 = max(sl[0].start - 3, 0), max(sl[1].start - 3, 0)
        crop = np.pad(sub[y0:sl[0].stop + 3, x0:sl[1].stop + 3].astype(float), 1)
        cs = measure.find_contours(crop, 0.5)
        if not cs:
            continue
        s = measure.approximate_polygon(max(cs, key=len), tolerance=tol)
        if len(s) < 4:
            continue
        pts = np.stack([s[:, 1] + x0 - 1, s[:, 0] + y0 - 1], 1)
        out.append({"area_m2": round(float(sz[i]), 2),
                    "pts": np.round(px2m(pts, pxm, origem, rot_rad), 3).tolist()})
    return out


CFG = {"parede":     dict(min_m2=0.25, tol=3, close=3, keep=2500, preencher=False),
       "mobiliario": dict(min_m2=0.30, tol=4, close=3, keep=1500),
       "agua":       dict(min_m2=3.0,  tol=5, close=7, keep=60),
       "areia":      dict(min_m2=5.0,  tol=6, close=9, keep=30),
       "vegetacao":  dict(min_m2=4.0,  tol=7, close=7, keep=120),
       "madeira":    dict(min_m2=3.0,  tol=6, close=7, keep=80),
       "vaga":       dict(min_m2=6.0,  tol=4, close=5, keep=400)}


def main():
    cfg = json.load(open("projeto.json", encoding="utf-8"))
    ds = cfg.get("downsample", 2)
    pxm = cfg["escala_px_por_m"] / ds
    origem = np.array(cfg["origem_px"], float) / ds
    rot = np.deg2rad(cfg.get("rotacao_graus", 0.0))

    res = {"escala_px_por_m": cfg["escala_px_por_m"], "niveis": {}}
    for cod, nv in cfg["niveis"].items():
        im = Image.open(nv["arquivo"]).convert("RGB")
        a = np.asarray(im.resize((im.size[0] // ds, im.size[1] // ds), Image.LANCZOS))
        cs = classes(a, nv.get("tem_agua", True), nv.get("tem_vaga", True),
                     nv.get("parede_modo", "linha"), nv.get("parede_limiar", 0.22))
        d = {"z": nv["z"], "elementos": {}}
        for k, m in cs.items():
            p = polys(m, pxm, origem, rot, **CFG[k])
            d["elementos"][k] = p
            print(f"  {cod} {k:11s} {len(p):4d} pol {sum(x['area_m2'] for x in p):8.1f} m2")
        res["niveis"][cod] = d
    json.dump(res, open("geometria.json", "w"))
    print("-> geometria.json")


if __name__ == "__main__":
    main()
