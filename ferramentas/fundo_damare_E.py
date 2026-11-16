"""Fundo Damare E (refinado): luz radial atrás do produto, onda oficial da logo como supergráfico
abraçando o topo do pacote (lockup "onda + produto"), rabiscos oficiais grandes sangrando pelas bordas.
Uso: python ferramentas/fundo_damare_E.py saida.png"""
import base64, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from fundo_damare import pincel, ponto, argola, g, W, H, VERDE, CIANO, LARANJA, AMARELO
from fundo_damare_oficial import icone, EL

AZUL = "#013E86"
BRANCO = "#FFFFFF"


def onda(x, y, w):
    from PIL import Image
    p = os.path.join(EL, "onda_logo.png")
    iw, ih = Image.open(p).size
    h = w * ih / iw
    b64 = base64.b64encode(open(p, "rb").read()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h:.1f}" href="data:image/png;base64,{b64}"/>'


def fundo():
    e = [
        '<defs><radialGradient id="luz" cx="445" cy="470" r="560" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#0E63BF"/><stop offset="0.45" stop-color="#0750A3"/>'
        f'<stop offset="0.74" stop-color="{AZUL}"/><stop offset="1" stop-color="{AZUL}"/></radialGradient></defs>',
        f'<rect width="{W}" height="{H}" fill="url(#luz)"/>',
    ]
    # supergráfico: a onda oficial da logo sobre o pacote, como o arco sobre a palavra Damare
    e.append(onda(140, 110, 640))
    # apoio amarelo sob o queijo
    e.append(pincel((285, 748), (380, 728), (510, 728), (610, 742), 36, AMARELO, 0.3))
    # cantos esquerdos: poucos, grandes, sangrando
    e.append(icone("coracao", -62, -58, 250, -16, LARANJA))
    e.append(icone("brigadeiro", -58, 400, 170, 14, CIANO))        # passa por trás do pacote
    e.append(icone("chapeu", -40, 708, 250, -10, VERDE))
    e.append(icone("copo", 360, 800, 170, 14, CIANO))              # sangra pela base
    e.append(icone("coracao", 640, 812, 120, 16, LARANJA))
    e.append(icone("caracol", 520, 8, 105, -8, CIANO))
    e.append(icone("circulo", 700, 40, 46, 0, VERDE))
    # acento da direita: um grande sangrando + um pequeno, com respiro
    e.append(icone("coracao", 2040, 285, 250, 18, CIANO))
    e.append(icone("gota", 1800, 320, 140, -24, LARANJA))
    e.append(icone("circulo", 1880, 505, 48, 0, VERDE))
    return e


if __name__ == "__main__":
    saida = sys.argv[1]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           + "".join(fundo()) + "</svg>")
    tmp = saida[:-4] + ".svg"
    open(tmp, "w", encoding="utf-8").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), tmp, "-o", saida], check=True)
    os.remove(tmp)
