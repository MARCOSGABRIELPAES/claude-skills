# -*- coding: utf-8 -*-
"""Afere a escala px/m de uma planta medindo o passo de um elemento repetido
e normatizado (vaga de garagem, degrau, modulo estrutural).

Por que assim: o passo e medido por FFT sobre uma faixa longa do desenho, entao
o erro de leitura de uma linha isolada nao contamina o resultado. Tres faixas
independentes dando o mesmo passo e o sinal de que a medida esta certa.

Uso:
  python afere_escala.py planta.jpg --faixa y0 y1 x0 x1 [--faixa ...] --medida 2.50

A banda de busca (--pmin/--pmax) precisa cercar o periodo esperado. Vaga de
garagem cai perto de 200 px numa prancha grande; degrau de escada, perto de 25.
Se a dispersao entre faixas passar de ~2%, a banda ou a regiao esta errada.
"""
import argparse
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


def passo_por_fft(cinza, y0, y1, x0, x1, pmin=80, pmax=400):
    """Periodo dominante (px) do padrao vertical dentro da faixa."""
    s = cinza[y0:y1, x0:x1].mean(axis=0)
    s = s - s.mean()
    p = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2
    f = np.arange(len(p)) / len(s)
    banda = (f > 1.0 / pmax) & (f < 1.0 / pmin)
    k = int(np.argmax(p * banda))
    y1_, y2_, y3_ = p[k - 1], p[k], p[k + 1]       # refino parabolico do pico
    dk = 0.5 * (y1_ - y3_) / (y1_ - 2 * y2_ + y3_)
    return len(s) / (k + dk)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("planta")
    ap.add_argument("--faixa", nargs=4, type=int, action="append", metavar=("Y0", "Y1", "X0", "X1"),
                    required=True, help="regiao com o elemento repetido; repita a flag")
    ap.add_argument("--medida", type=float, default=2.50,
                    help="dimensao real do passo em metros (vaga padrao BR = 2.50)")
    ap.add_argument("--pmin", type=float, default=80.0,
                    help="menor periodo plausivel em px (baixe para degraus, suba para vagas)")
    ap.add_argument("--pmax", type=float, default=400.0, help="maior periodo plausivel em px")
    a = ap.parse_args()

    cinza = np.asarray(Image.open(a.planta).convert("L"), dtype=np.float32)
    passos = []
    for (y0, y1, x0, x1) in a.faixa:
        p = passo_por_fft(cinza, y0, y1, x0, x1, a.pmin, a.pmax)
        passos.append(p)
        print(f"  faixa y[{y0}:{y1}] x[{x0}:{x1}]  passo = {p:7.2f} px  ->  {p / a.medida:6.2f} px/m")

    passos = np.array(passos)
    disp = passos.std() / passos.mean() * 100 if len(passos) > 1 else 0.0
    print(f"\n  passo mediano = {np.median(passos):.2f} px   dispersao entre faixas = {disp:.2f}%")
    print(f"  ESCALA = {np.median(passos) / a.medida:.2f} px/m")
    if disp > 2:
        print("  AVISO: dispersao alta. As faixas provavelmente nao cortam o mesmo elemento.")
    print("\n  Confira agora com 2 referencias independentes (profundidade de vaga ~5.0 m,")
    print("  corredor 6.0-7.0 m, quadra de areia 16x8 m). Se nao fecharem, a medida esta errada.")


if __name__ == "__main__":
    main()
