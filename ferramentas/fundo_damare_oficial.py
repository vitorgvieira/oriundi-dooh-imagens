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
    # onda dupla da logo, faixa contínua por trás do topo do pacote (termina antes do texto)
    e.append(pincel((-60, 600), (180, 300), (450, 190), (720, 200), 54, VERDE))
    e.append(pincel((-60, 730), (220, 400), (460, 300), (690, 320), 84, CIANO))
    # pincelada amarela de apoio sob o queijo
    e.append(pincel((260, 752), (400, 726), (560, 726), (700, 746), 40, AMARELO, 0.3))
    # topo esquerdo: um grande + dois médios
    e.append(icone("coracao", 18, 6, 215, -14, LARANJA))
    e.append(icone("espatula", 300, 4, 165, 8, VERDE))
    e.append(icone("gota", 640, 6, 150, 28, LARANJA))
    # borda esquerda
    e.append(icone("brigadeiro", -50, 380, 155, 12, CIANO))
    # base esquerda: chapéu grande + copo + coração pequeno
    e.append(icone("chapeu", 4, 690, 225, -8, VERDE))
    e.append(icone("copo", 330, 772, 145, 12, CIANO))
    e.append(icone("coracao", 650, 790, 115, 14, LARANJA))
    # meio da borda direita (y 265-567, x > 1760)
    e.append(icone("coracao", 2020, 300, 210, 16, LARANJA))
    e.append(icone("brigadeiro", 1785, 300, 130, -10, VERDE))
    e.append(icone("copo", 1860, 430, 125, -14, CIANO))
    return e


if __name__ == "__main__":
    saida = sys.argv[1]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           + "".join(fundo()) + "</svg>")
    tmp = saida[:-4] + ".svg"
    open(tmp, "w", encoding="utf-8").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), tmp, "-o", saida], check=True)
    os.remove(tmp)
