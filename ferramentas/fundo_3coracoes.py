"""Fundo 3 Corações desenhado por código (SVG -> PNG 2156x924), nas 3 cores da logo.
Conceito "o coração da 3 Corações": coração gigante marrom com contorno laranja (o coração da logo)
como palco dos pacotes, luz laranja dentro dele, grãos vetoriais com volume nas bordas e vapor quente.
Uso: python ferramentas/fundo_3coracoes.py saida.png [--debug]"""
import math, os, subprocess, sys
import numpy as np

W, H = 2156, 924
VERM_LOGO = "#E3262C"   # vermelho da logo
VERM_TEXTO = "#A51012"  # vermelho oficial das peças (zona do texto: branco 7,9:1, amarelo 5,4:1)
MARROM = "#452A1A"      # marrom do coração da logo
LARANJA = "#F9A12B"     # laranja dos corações da logo

# ---------- coração (paramétrico) ajustado a uma caixa ----------
CONTORNO = os.path.join(os.path.dirname(__file__), "..", "3coracoes", "3coracoes", "elementos", "coracao_logo_contorno.json")

def coracao_path(x0, y0, x1, y1):
    """Contorno do coração extraído da logo oficial (normalizado 0..1), encaixado na caixa."""
    import json
    pts = json.load(open(CONTORNO))
    return "M" + " L".join(f"{x0 + a * (x1 - x0):.1f},{y0 + b * (y1 - y0):.1f}" for a, b in pts) + " Z"

# ---------- grão de café (ilustração plana premium, nas cores da logo) ----------
def grao(cx, cy, w, ang, sombra=True):
    corpo = ('<ellipse rx="0.5" ry="0.33" fill="url(#gGrao)"/>'
             # fenda em S, marrom escuro, com fio laranja de luz
             '<path d="M-0.43,0.05 C-0.22,-0.13 0.04,0.17 0.43,-0.04" stroke="#22120A" stroke-width="0.075" '
             'fill="none" stroke-linecap="round"/>'
             f'<path d="M-0.40,-0.01 C-0.21,-0.17 0.04,0.11 0.40,-0.10" stroke="{LARANJA}" stroke-opacity="0.85" '
             'stroke-width="0.02" fill="none" stroke-linecap="round"/>'
             # borda de luz laranja no lado de cima (luz vindo do coração)
             f'<ellipse rx="0.5" ry="0.33" fill="none" stroke="{LARANJA}" stroke-opacity="0.35" stroke-width="0.025" '
             'clip-path="url(#cMeioCima)"/>')
    out = ""
    if sombra:
        out += (f'<g filter="url(#fSombra)" opacity="0.32"><g transform="translate({cx + 0.04 * w},{cy + 0.08 * w}) '
                f'rotate({ang}) scale({w})"><ellipse rx="0.5" ry="0.33" fill="#4A0406"/></g></g>')
    out += f'<g transform="translate({cx},{cy}) rotate({ang}) scale({w})">{corpo}</g>'
    return out

# ---------- vapor ----------
def vapor(d, larg, op):
    return (f'<path d="{d}" stroke="url(#gVapor)" stroke-width="{larg}" fill="none" stroke-linecap="round" '
            f'opacity="{op}" filter="url(#fB3)"/>')

def svg():
    hx0, hy0, hx1, hy1 = -20, 12, 800, 762           # coração da logo: lobos acima dos pacotes, ponta atrás deles
    hcx = (hx0 + hx1) / 2
    heart = coracao_path(hx0, hy0, hx1, hy1)
    defs = f'''<defs>
<radialGradient id="gBase" cx="400" cy="400" r="580" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{VERM_LOGO}"/><stop offset="0.5" stop-color="#D0201F"/>
  <stop offset="0.8" stop-color="{VERM_TEXTO}"/><stop offset="1" stop-color="{VERM_TEXTO}"/></radialGradient>
<radialGradient id="gCor" cx="{hcx}" cy="380" r="520" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#6A3A21"/><stop offset="0.6" stop-color="#4E2F1D"/><stop offset="1" stop-color="{MARROM}"/></radialGradient>
<radialGradient id="gLuz" cx="{hcx + 10}" cy="430" r="400" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{LARANJA}" stop-opacity="0.9"/><stop offset="0.55" stop-color="{LARANJA}" stop-opacity="0.5"/>
  <stop offset="1" stop-color="{LARANJA}" stop-opacity="0"/></radialGradient>
<linearGradient id="gGrao" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#7A4529"/><stop offset="0.47" stop-color="#5C3420"/>
  <stop offset="0.53" stop-color="#3E2214"/><stop offset="1" stop-color="#2B170D"/></linearGradient>
<linearGradient id="gVapor" x1="0" y1="1" x2="0" y2="0">
  <stop offset="0" stop-color="#FFEFD6" stop-opacity="0"/><stop offset="0.3" stop-color="#FFEFD6" stop-opacity="0.85"/>
  <stop offset="0.75" stop-color="#FFEFD6" stop-opacity="0.35"/><stop offset="1" stop-color="#FFEFD6" stop-opacity="0"/></linearGradient>
<radialGradient id="gMaskR" cx="{hcx}" cy="330" r="620" gradientUnits="userSpaceOnUse">
  <stop offset="0.45" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="mRaios" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#gMaskR)"/></mask>
<clipPath id="cEsq"><rect x="0" y="0" width="850" height="{H}"/></clipPath>
<clipPath id="cCor"><path d="{heart}"/></clipPath>
<clipPath id="cMeioCima"><rect x="-1" y="-1" width="2" height="0.95"/></clipPath>
<filter id="fSombra" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="fB3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="fB6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="fGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="26"/></filter>
</defs>'''
    e = [defs, f'<rect width="{W}" height="{H}" fill="url(#gBase)"/>']
    import math as _m
    cx, cy = hcx, 330
    raios = ""
    n = 22
    for i in range(n):
        a0 = 2 * _m.pi * i / n + 0.05
        a1 = a0 + _m.pi / n
        raios += (f'<path d="M{cx},{cy} L{cx + 1400 * _m.cos(a0):.1f},{cy + 1400 * _m.sin(a0):.1f} '
                  f'L{cx + 1400 * _m.cos(a1):.1f},{cy + 1400 * _m.sin(a1):.1f} Z"/>')
    e.append(f'<g mask="url(#mRaios)" clip-path="url(#cEsq)"><g fill="{LARANJA}" fill-opacity="0.16">{raios}</g></g>')
    e.append(f'<path d="{heart}" fill="none" stroke="{LARANJA}" stroke-width="70" stroke-opacity="0.22" filter="url(#fGlow)"/>')
    e.append(f'<path d="{heart}" fill="{MARROM}"/>')
    e.append(f'<g clip-path="url(#cCor)"><rect width="{W}" height="{H}" fill="url(#gLuz)"/></g>')
    e.append(f'<path d="{heart}" fill="none" stroke="{LARANJA}" stroke-width="14" stroke-linejoin="round"/>')
    # grãos: cantos esquerdos, grandes, sangrando pelas bordas
    e.append(grao(96, 22, 240, -28))
    e.append(grao(-14, 735, 210, 35))
    e.append(grao(800, 18, 110, 20))
    # meio da borda direita (entre as logos, y 303–588)
    e.append(grao(2120, 400, 280, 32))
    e.append(grao(1985, 548, 120, -18))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(e) + "</svg>"

if __name__ == "__main__":
    saida = sys.argv[1]
    tmp = saida[:-4] + ".svg"
    open(tmp, "w", encoding="utf-8").write(svg())
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), tmp, "-o", saida], check=True)
    if "--debug" not in sys.argv:
        os.remove(tmp)
    print(saida)
