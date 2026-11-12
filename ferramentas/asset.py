#!/usr/bin/env python3
"""Tratamento de imagens do telao (produtos e logos).

  recorte  ENTRADA SAIDA --fundo preto|branco   recorta foto de fundo liso
  sombra   ENTRADA SAIDA --cor #06122E          apara e embute a sombra padrao (folga 70 px)
  branca   ENTRADA SAIDA                        logo com transparencia -> toda branca
  alfacor  ENTRADA SAIDA --cor-fundo #C8643C [--tol 60] [--escuro-para-branco]
                                                logo sobre fundo liso colorido -> transparente
  ampliar  ENTRADA SAIDA [--fator 3]            LANCZOS
Na moldura do Canva: w,h = PNG x escala; o canto sobe e recua 70 x escala.
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

FOLGA = 70


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def aparar(im):
    bbox = im.getchannel("A").getbbox()
    return im.crop(bbox) if bbox else im


def recorte(im, fundo):
    rgb = np.asarray(im.convert("RGB")).astype(int)
    perto = rgb.max(axis=2) < 28 if fundo == "preto" else rgb.min(axis=2) > 238
    rot, _ = ndimage.label(perto)
    borda = set(np.unique(np.concatenate([rot[0], rot[-1], rot[:, 0], rot[:, -1]]))) - {0}
    fundo_m = np.isin(rot, list(borda))
    obj = ~fundo_m
    rot2, n = ndimage.label(obj)
    if n:
        tam = ndimage.sum(obj, rot2, range(1, n + 1))
        obj = rot2 == (int(np.argmax(tam)) + 1)
    obj = ndimage.binary_fill_holes(obj)
    obj = ndimage.binary_erosion(obj, iterations=2)
    alfa = Image.fromarray((obj * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGB").convert("RGBA")
    out.putalpha(alfa)
    return aparar(out)


def sombra(im, cor):
    im = aparar(im.convert("RGBA"))
    w, h = im.width + 2 * FOLGA, im.height + 2 * FOLGA
    alfa = Image.new("L", (w, h), 0)
    alfa.paste(im.getchannel("A"), (FOLGA, FOLGA))
    tela = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for dx, dy, raio, op in ((6, 26, 26, 0.55), (2, 8, 7, 0.35)):
        m = Image.new("L", (w, h), 0)
        m.paste(alfa, (dx, dy))
        m = m.filter(ImageFilter.GaussianBlur(raio)).point(lambda v: int(v * op))
        camada = Image.new("RGBA", (w, h), hex_rgb(cor) + (0,))
        camada.putalpha(m)
        tela = Image.alpha_composite(tela, camada)
    tela.alpha_composite(im, (FOLGA, FOLGA))
    return tela


def branca(im):
    im = im.convert("RGBA")
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(im.getchannel("A"))
    return aparar(out)


def alfacor(im, cor_fundo, tol, escuro_para_branco):
    rgb = np.asarray(im.convert("RGB")).astype(float)
    d = np.sqrt(((rgb - np.array(hex_rgb(cor_fundo))) ** 2).sum(axis=2))
    alfa = np.clip((d - tol * 0.5) / (tol * 0.5), 0, 1)
    if escuro_para_branco:
        escuro = rgb.max(axis=2) < 90
        rgb[escuro] = 255
    out = np.dstack([rgb, alfa * 255]).astype(np.uint8)
    return aparar(Image.fromarray(out, "RGBA"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("modo", choices=["recorte", "sombra", "branca", "alfacor", "ampliar"])
    p.add_argument("entrada")
    p.add_argument("saida")
    p.add_argument("--fundo", default="branco", choices=["preto", "branco"])
    p.add_argument("--cor", default="#06122E")
    p.add_argument("--cor-fundo")
    p.add_argument("--tol", type=float, default=60)
    p.add_argument("--escuro-para-branco", action="store_true")
    p.add_argument("--fator", type=float, default=3)
    a = p.parse_args()
    im = Image.open(a.entrada)
    if a.modo == "recorte":
        out = recorte(im, a.fundo)
    elif a.modo == "sombra":
        out = sombra(im, a.cor)
    elif a.modo == "branca":
        out = branca(im)
    elif a.modo == "alfacor":
        out = alfacor(im, a.cor_fundo, a.tol, a.escuro_para_branco)
    else:
        out = im.resize((round(im.width * a.fator), round(im.height * a.fator)), Image.LANCZOS)
    out.save(a.saida)
    print(f"{a.saida} {out.width}x{out.height}")


if __name__ == "__main__":
    main()
