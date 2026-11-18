# Fundos Sadia desenhados por codigo (2156x924, layout B). Uso: python fundo_sadia.py A|B saida.png
# A "Campo vermelho em S": produto sobre vermelho Sadia com luz radial; borda do campo em curva de S;
#   centro e direita em bordo #3A0B0F; terminal do S entrando pela borda direita (30-62% da altura).
# B "S gigante da embalagem": bordo #3A0B0F com luz radial vermelha atras do produto e o S oficial da
#   logo gigante, cortado pelas bordas, como no pote; fragmento do S no meio da borda direita.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

W, H, SS = 2156, 924, 2
VERM = (210, 35, 42)      # #D2232A, aprox. da logo
ESC = (58, 11, 15)        # #3A0B0F tom do texto
ESC2 = (74, 14, 18)       # #4A0E12
LOGO = 'brf/sadia/logo/sadia_vermelha.png'


def grad_radial(cx, cy, r, c0, c1, gamma=1.6):
    y, x = np.mgrid[0:H, 0:W].astype(float)
    t = np.clip(np.hypot(x - cx, y - cy) / r, 0, 1) ** gamma
    c0, c1 = np.array(c0, float), np.array(c1, float)
    return c0 + (c1 - c0) * t[..., None]


def base_escura():
    y, x = np.mgrid[0:H, 0:W].astype(float)
    # degrade linear muito suave: um pouco mais claro no topo-centro
    t = np.clip(np.hypot((x - 1300) / 1400, (y + 100) / 1100), 0, 1)
    c0, c1 = np.array(ESC2, float), np.array(ESC, float)
    return c0 + (c1 - c0) * t[..., None]


def bezier(pts, n=400):
    p = np.array(pts, float); t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3) * p[0] + 3 * ((1 - t) ** 2) * t * p[1] + 3 * (1 - t) * t * t * p[2] + t ** 3 * p[3]


def mascara_poly(pts):
    m = Image.new('L', (W * SS, H * SS), 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    return np.asarray(m.resize((W, H), Image.LANCZOS)).astype(float) / 255


def traco(pts, larg):
    """Traco do S: espessura constante ao longo de uma bezier (terminais fora da tela)."""
    m = Image.new('L', (W * SS, H * SS), 0)
    d = ImageDraw.Draw(m); r = larg * SS / 2
    for x, y in bezier(pts, 1500):
        d.ellipse((x * SS - r, y * SS - r, x * SS + r, y * SS + r), fill=255)
    return np.asarray(m.resize((W, H), Image.LANCZOS)).astype(float) / 255


def compor(fundo, mask, cor):
    cor = np.broadcast_to(np.array(cor, float), fundo.shape) if np.ndim(cor) == 1 else cor
    return fundo * (1 - mask[..., None]) + cor * mask[..., None]


def s_oficial():
    """Recorta o S da logo oficial (maior componente mais a esquerda) e devolve a mascara L."""
    im = Image.open(LOGO).convert('RGBA')
    # o S encosta no "a" na logo: corta na coluna onde comeca o "a" (x 392 no arquivo de 1280 px)
    alfa = np.asarray(im)[..., 3].copy()
    alfa[:, int(392 * im.width / 1280):] = 0
    return Image.fromarray(alfa).crop(Image.fromarray(alfa).getbbox())


def conceito_a():
    f = base_escura()
    # campo vermelho: borda direita em curva de S (contracurva no topo e na base)
    borda = np.vstack([
        bezier([(560, -30), (700, 60), (850, 150), (850, 330)]),
        bezier([(850, 330), (850, 560), (830, 700), (700, 820)]),
        bezier([(700, 820), (620, 890), (520, 930), (430, 960)]),
    ])
    pts = [(-10, -30)] + [tuple(p) for p in borda] + [(-10, 960)]
    m = mascara_poly(pts)
    verm = grad_radial(430, 470, 820, (232, 52, 58), (170, 22, 28), 1.3)
    f = compor(f, m, verm)
    # terminal do S entrando pela borda direita, so no meio (30-62% da altura)
    f = compor(f, traco([(2230, 250), (2060, 330), (2050, 520), (2230, 620)], 74), VERM)
    return f


def conceito_b():
    f = grad_radial(420, 480, 900, (140, 20, 25), ESC, 1.5)
    # garante o centro e a direita no bordo liso
    y, x = np.mgrid[0:H, 0:W].astype(float)
    k = np.clip((x - 700) / 250, 0, 1)[..., None]
    f = f * (1 - k) + np.array(ESC, float) * k
    s = s_oficial()
    # S gigante atras dos potes, cortado no topo, na base e na esquerda
    hs = 1160; ws = round(s.width * hs / s.height)
    sg = s.resize((ws, hs), Image.LANCZOS)
    tela = Image.new('L', (W, H), 0)
    tela.paste(sg, (-60, -130))
    m = np.asarray(tela).astype(float) / 255
    f = compor(f, m, VERM)
    # fragmento do S (terminal) no meio da borda direita
    # S inteiro pequeno (280 px, dentro da faixa 30-62% da altura), metade para fora da borda
    hr = 280; sr = s.resize((round(s.width * hr / s.height), hr), Image.LANCZOS)
    tela2 = Image.new('L', (W, H), 0)
    tela2.paste(sr, (W - sr.width // 2, 292))
    m2 = np.asarray(tela2).astype(float) / 255
    f = compor(f, m2, VERM)
    return f




# --- Versao amarela (18/11/2026): o Vitor mostrou que a comunicacao atual ("Seu dia pede Sadia")
# usa fundo amarelo, com vermelho so na logo e no S. A e B (vermelhos) ficam como testados.
AM = (249, 206, 39)       # #F9CE27 aprox. das pecas oficiais enviadas
AM_CLARO = (255, 222, 80)
AM_QUENTE = (248, 184, 37)  # #F8B825 brilho quente do piso nas pecas oficiais


def base_amarela(cx=420, cy=470, r=1500):
    f = grad_radial(cx, cy, r, AM_CLARO, AM, 1.2)
    return f


def conceito_c():
    """C "S gigante da embalagem": amarelo com luz atras dos potes e o S oficial vermelho gigante,
    cortado pelas bordas, como no pote; S inteiro pequeno no meio da borda direita."""
    f = base_amarela()
    s = s_oficial()
    hs = 1160; ws = round(s.width * hs / s.height)
    tela = Image.new('L', (W, H), 0)
    tela.paste(s.resize((ws, hs), Image.LANCZOS), (-60, -130))
    f = compor(f, np.asarray(tela).astype(float) / 255, VERM)
    hr = 280; sr = s.resize((round(s.width * hr / s.height), hr), Image.LANCZOS)
    tela2 = Image.new('L', (W, H), 0)
    tela2.paste(sr, (W - sr.width // 2, 292))
    f = compor(f, np.asarray(tela2).astype(float) / 255, VERM)
    return f


def conceito_d():
    """D "Estudio Seu dia pede Sadia": parede amarela, piso amarelo-quente com horizonte suave
    (como nas pecas oficiais), luz atras dos potes; traco do S vermelho entrando pela borda direita."""
    # parede: halo claro atras dos potes, amarelo Sadia no resto
    f = grad_radial(430, 430, 950, (255, 232, 120), AM, 1.1)
    y, x = np.mgrid[0:H, 0:W].astype(float)
    # piso: horizonte em curva (palco), y ~690 sob os potes, descendo e saindo pela base antes da
    # coluna da logo Oriundi (canto inferior direito liso)
    hz = 690 + 300 * np.clip((x - 700) / 1000, 0, 1) ** 1.6
    k = np.clip((y - hz) / 70, 0, 1)
    piso = grad_radial(430, 800, 1400, (250, 196, 50), (236, 160, 28), 0.8)
    f = f * (1 - k[..., None]) + piso * k[..., None]
    # traco do S (espessura constante) entrando e saindo pela borda direita, 30-62% da altura
    f = compor(f, traco([(2240, 255), (2050, 330), (2040, 520), (2240, 610)], 70), VERM)
    return f


CONCEITOS = {'A': conceito_a, 'B': conceito_b, 'C': conceito_c, 'D': conceito_d}


if __name__ == '__main__':
    f = CONCEITOS[sys.argv[1]]()
    Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).save(sys.argv[2])
