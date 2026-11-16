"""Fundo Damare D: rabiscos oficiais da marca (SVG em damare/damare/elementos/) sobre azul royal.
Uso: python ferramentas/fundo_damare_oficial.py saida.png"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from fundo_damare import pincel, ponto, g, argola, W, H, VERDE, CIANO, LARANJA, AMARELO

AZUL = "#013E86"
EL = os.path.join(os.path.dirname(__file__), "..", "damare", "damare", "elementos")


def icone(nome, x, y, h, rot, cor):
    s = open(os.path.join(EL, nome + ".svg"), encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    paths = "".join(f'<path d="{d}"/>' for d in re.findall(r'<path[^>]* d="([^"]+)"', s))
    esc = h / vb[3]
    w = vb[2] * esc
    cx, cy = x + w / 2, y + h / 2
    return (f'<g transform="rotate({rot} {cx:.1f} {cy:.1f}) translate({x} {y}) scale({esc:.4f}) '
            f'translate({-vb[0]} {-vb[1]})" fill="{cor}">{paths}</g>')


def fundo():
    e = [f'<rect width="{W}" height="{H}" fill="{AZUL}"/>']
    # onda dupla da logo atrás do produto (termina antes do texto)
    e.append(pincel((-40, 640), (160, 330), (420, 210), (650, 235), 40, VERDE))
    e.append(pincel((-40, 760), (200, 430), (460, 320), (700, 345), 62, CIANO))
    # pincelada amarela de apoio sob o queijo
    e.append(pincel((215, 752), (360, 726), (540, 726), (690, 746), 40, AMARELO, 0.3))
    # topo esquerdo
    e.append(icone("coracao", 28, 22, 150, -14, LARANJA))
    e.append(icone("espatula", 230, 8, 150, 8, VERDE))
    e.append(icone("bolo", 450, 36, 105, -6, CIANO))
    e.append(icone("gota", 700, 14, 130, 28, LARANJA))
    e.append(ponto(395, 60, 9, AMARELO)); e.append(ponto(650, 150, 8, VERDE))
    # borda esquerda
    e.append(icone("brigadeiro", -40, 360, 140, 12, CIANO))
    # base esquerda
    e.append(icone("chapeu", 14, 732, 165, -8, VERDE))
    e.append(icone("copo", 290, 778, 130, 12, CIANO))
    e.append(icone("gota", 505, 790, 110, -32, AMARELO))
    e.append(icone("coracao", 690, 790, 100, 14, LARANJA))
    e.append(g(argola(16), 445, 900, 1, 0, VERDE))
    # meio da borda direita (y 265-567, x > 1760)
    e.append(icone("coracao", 2050, 290, 170, 16, LARANJA))
    e.append(icone("brigadeiro", 1790, 300, 115, -10, VERDE))
    e.append(icone("copo", 1860, 440, 110, -14, CIANO))
    e.append(ponto(2000, 520, 9, VERDE)); e.append(g(argola(14), 1985, 285, 1, 0, CIANO))
    return e


if __name__ == "__main__":
    saida = sys.argv[1]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           + "".join(fundo()) + "</svg>")
    tmp = saida[:-4] + ".svg"
    open(tmp, "w", encoding="utf-8").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), tmp, "-o", saida], check=True)
    os.remove(tmp)
