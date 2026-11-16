"""Fundos Damare desenhados por código (estilo rabiscos da marca). Uso: python fundo_damare.py A|B saida.png"""
import math, subprocess, sys

W, H = 2156, 924
AZUL = "#024A9A"
VERDE, CIANO, LARANJA, AMARELO = "#A6C23A", "#3FA9E0", "#F39A2E", "#F6C21C"
SW = 12  # traço base


def g(el, x, y, s=1.0, r=0, cor=CIANO, sw=SW):
    return (f'<g transform="translate({x} {y}) rotate({r}) scale({s})" fill="none" stroke="{cor}" '
            f'stroke-width="{sw / s:.1f}" stroke-linecap="round" stroke-linejoin="round">{el}</g>')


# ícones em coordenadas locais centradas em 0,0 (~100 px)
CORACAO = '<path d="M0 40 C-30 18 -46 0 -40 -18 C-34 -36 -10 -38 0 -18 C10 -38 34 -36 40 -18 C46 0 30 18 4 38"/>'
CHAPEU = ('<path d="M-26 22 C-44 18 -46 -8 -28 -12 C-30 -36 -2 -44 6 -26 C18 -42 46 -32 36 -10 C50 -6 48 18 28 22"/>'
          '<path d="M-24 24 L-22 44 L26 44 L28 24"/>')
COPO = '<path d="M-26 -42 L-18 42 L18 42 L26 -42"/><path d="M-22 -8 L22 -8"/>'
ESPATULA = ('<path d="M0 48 L0 6"/><path d="M-16 6 L16 6 L18 -40 C18 -48 -18 -48 -18 -40 Z"/>'
            '<path d="M-6 -30 L-6 -6"/><path d="M6 -30 L6 -6"/>')
BATEDOR = ('<path d="M0 50 L0 14"/><path d="M0 14 C-26 -10 -20 -50 0 -50 C20 -50 26 -10 0 14"/>'
           '<path d="M0 14 C-8 -10 -8 -46 0 -50 C8 -46 8 -10 0 14"/>')


def espiral(voltas=1.8, r=50):
    pts = []
    n = 120
    for i in range(n + 1):
        t = i / n
        a = t * voltas * 2 * math.pi
        rr = 14 + (r - 14) * t
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return '<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + '"/>'


def argola(r=22):
    return f'<circle cx="0" cy="0" r="{r}"/>'


def ponto(x, y, r, cor):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{cor}"/>'


def pincel(p0, p1, p2, p3, larg, cor, ponta=0.15):
    """traço afinado (estilo onda da logo): cúbica com largura variando de ponta*larg a larg e afinando"""
    def bez(t):
        u = 1 - t
        return [u**3 * p0[k] + 3 * u * u * t * p1[k] + 3 * u * t * t * p2[k] + t**3 * p3[k] for k in (0, 1)]
    n = 80
    esq, dir_ = [], []
    for i in range(n + 1):
        t = i / n
        x, y = bez(t)
        x2, y2 = bez(min(t + 1e-3, 1)) if t < 1 else bez(t)
        x1, y1 = bez(max(t - 1e-3, 0))
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = larg * (ponta + (1 - ponta) * t ** 0.8) / 2
        esq.append((x + nx * w, y + ny * w))
        dir_.append((x - nx * w, y - ny * w))
    pts = esq + dir_[::-1]
    return (f'<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + f' Z" fill="{cor}"/>'
            f'<circle cx="{p3[0]}" cy="{p3[1]}" r="{larg / 2:.1f}" fill="{cor}"/>')


def borda_comum():
    """rabiscos nas bordas permitidas: topo e base 0-37%, borda esquerda, meio da borda direita"""
    e = []
    # topo esquerdo
    e.append(g(CORACAO, 72, 72, 1.15, -14, LARANJA))
    e.append(g(argola(20), 250, 48, 1, 0, VERDE))
    e.append(g(ESPATULA, 470, 66, 1.3, 35, CIANO))
    e.append(g(espiral(), 700, 64, 0.9, 0, VERDE))
    e.append(ponto(345, 92, 9, AMARELO)); e.append(ponto(590, 34, 8, CIANO)); e.append(ponto(790, 104, 8, LARANJA))
    # borda esquerda (cortada)
    e.append(g(espiral(1.8, 66), 4, 470, 1, 0, CIANO))
    # base esquerda
    e.append(g(CHAPEU, 120, 850, 1.25, -10, VERDE))
    e.append(g(COPO, 400, 862, 1.05, 12, LARANJA))
    e.append(g(BATEDOR, 620, 862, 1.25, -28, CIANO))
    e.append(g(argola(18), 790, 880, 1, 0, VERDE))
    e.append(ponto(250, 900, 9, CIANO)); e.append(ponto(505, 818, 8, VERDE))
    # meio da borda direita (y 277-567, x > 1760)
    e.append(g(CORACAO, 2128, 420, 1.35, 18, LARANJA, 17))
    e.append(g(argola(24), 1860, 330, 1, 0, VERDE))
    e.append(g(espiral(1.8, 46), 1960, 515, 1, 0, CIANO))
    e.append(ponto(1800, 450, 9, AMARELO)); e.append(ponto(2010, 300, 8, CIANO)); e.append(ponto(1880, 545, 7, VERDE))
    return e


def opcao_a():
    e = [f'<rect width="{W}" height="{H}" fill="{AZUL}"/>']
    # onda dupla grande atrás do produto (verde em cima, ciano embaixo), termina antes do texto
    e.append(pincel((-60, 700), (180, 300), (500, 170), (770, 205), 46, VERDE))
    e.append(pincel((-60, 820), (220, 420), (540, 300), (790, 335), 70, CIANO))
    # pincelada amarela de apoio sob o queijo
    e.append(pincel((70, 770), (260, 735), (520, 735), (720, 760), 46, AMARELO, 0.3))
    e += borda_comum()
    return e


def opcao_b():
    e = [f'<rect width="{W}" height="{H}" fill="{AZUL}"/>']
    # "prato" azul-claro atrás do produto, com aro verde
    e.append(f'<circle cx="445" cy="470" r="345" fill="{CIANO}"/>')
    e.append(f'<circle cx="445" cy="470" r="300" fill="#5DBBEA"/>')
    e.append(f'<path d="M150 260 A360 360 0 0 1 700 190" fill="none" stroke="{VERDE}" stroke-width="16" stroke-linecap="round"/>')
    e.append(f'<path d="M790 560 A372 372 0 0 1 560 812" fill="none" stroke="{LARANJA}" stroke-width="14" stroke-linecap="round"/>')
    e += borda_comum()
    return e


if __name__ == "__main__":
    op, saida = sys.argv[1], sys.argv[2]
    corpo = opcao_a() if op == "A" else opcao_b()
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(corpo) + "</svg>"
    open(saida.replace(".png", ".svg"), "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), saida.replace(".png", ".svg"), "-o", saida], check=True)
