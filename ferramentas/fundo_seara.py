# Fundo Seara desenhado por codigo (2156x924, layout B). Uso: python fundo_seara.py A saida.png [args]
# A "Sol da Seara": vermelho fechado da marca; oval oficial da logo nascendo da base atras dos pacotes
#   e os 5 raios oficiais da logo, gigantes, abrindo em leque para o canto superior esquerdo;
#   zona do texto em vermelho profundo uniforme; arco do oval sangrando no meio da borda direita.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

W, H = 2156, 924
LOGO = 'seara/seara/logo/seara_oficial.png'
VERM = (227, 6, 19)      # #E30613 oval da logo (medido no PNG oficial)
AMAR = (255, 230, 0)     # #FFE600 raios da logo (medido)
ESC = (104, 6, 14)       # #68060E vermelho profundo (zona do texto)
FOCO_LOGO = (325, 260)   # centro do oval no PNG recortado (650x438)


def grad_radial(cx, cy, r, c0, c1, gamma=1.5):
    y, x = np.mgrid[0:H, 0:W].astype(float)
    t = np.clip(np.hypot(x - cx, y - cy) / r, 0, 1) ** gamma
    return np.array(c0, float) + (np.array(c1, float) - np.array(c0, float)) * t[..., None]


def compor(f, m, cor):
    cor = np.broadcast_to(np.array(cor, float), f.shape) if np.ndim(cor) == 1 else cor
    return f * (1 - m[..., None]) + cor * m[..., None]


def mascaras_logo():
    a = np.asarray(Image.open(LOGO).convert('RGBA')).astype(int)
    al = a[..., 3] / 255
    yel = (a[..., 0] > 200) & (a[..., 1] > 170) & (a[..., 2] < 120)
    yel = ndimage.binary_dilation(yel, iterations=1)
    raios = np.where(yel, al, 0)
    oval = np.where(~yel, al, 0)  # oval com o wordmark (preenchido abaixo)
    oval = ndimage.binary_fill_holes(oval > 0.5).astype(float)
    oval = np.maximum(oval, np.where(~yel, al, 0))
    return oval, raios


def elipse(cx, cy, rx, ry, ss=3):
    m = Image.new('L', (W * ss, H * ss), 0)
    ImageDraw.Draw(m).ellipse(((cx - rx) * ss, (cy - ry) * ss, (cx + rx) * ss, (cy + ry) * ss), fill=255)
    return np.asarray(m.resize((W, H), Image.LANCZOS)).astype(float) / 255


def transformar(m, escala, rot, foco_dst):
    """Escala e gira a mascara do PNG da logo em torno do foco do oval e coloca o foco em foco_dst."""
    im = Image.fromarray((m * 255).astype(np.uint8))
    w, h = round(im.width * escala), round(im.height * escala)
    im = im.resize((w, h), Image.BICUBIC).point(lambda v: 255 if v > 127 else 0)
    im = im.filter(ImageFilter.GaussianBlur(1.1))  # borda lisa: limiar + antisserrilhado
    fx, fy = FOCO_LOGO[0] * escala, FOCO_LOGO[1] * escala
    pad = int(max(w, h))
    big = Image.new('L', (w + 2 * pad, h + 2 * pad), 0)
    big.paste(im, (pad, pad))
    big = big.rotate(rot, resample=Image.BICUBIC, center=(fx + pad, fy + pad))
    tela = Image.new('L', (W, H), 0)
    tela.paste(big, (round(foco_dst[0] - fx - pad), round(foco_dst[1] - fy - pad)))
    return np.asarray(tela).astype(float) / 255


def conceito_a(fx=420, fy=640, esc_oval=1.26, esc_raio=2.6, rot=22):
    f = grad_radial(420, 520, 900, (196, 12, 24), ESC, 1.3)
    y, x = np.mgrid[0:H, 0:W].astype(float)
    k = np.clip((x - 760) / 220, 0, 1)[..., None]
    f = f * (1 - k) + np.array(ESC, float) * k
    oval, raios = mascaras_logo()
    # oval da logo (elipse 650x354 no PNG oficial) como palco atras dos pacotes
    m_oval = elipse(fx, fy, 325 * esc_oval, 177 * esc_oval)
    m_raio = transformar(raios, esc_raio, rot, (fx, fy))
    luz = grad_radial(fx, fy - 120, 620, (238, 30, 38), VERM, 1.2)
    f = compor(f, m_oval, luz)
    f = compor(f, m_raio, AMAR)
    # arco do oval sangrando no meio da borda direita (30-62% da altura), vermelho pouco acima do fundo
    f = compor(f, elipse(W + 40, 425, 210, 115), (140, 10, 20))
    return f


LAR = (255, 83, 1)       # #FF5301 laranja da peca oficial Seara (medido na arte enviada pelo Vitor)
LAR_LUZ = (255, 150, 20) # luz amarelo-alaranjada atras dos pacotes, como na peca oficial
LAR_TXT = (255, 122, 16) # #FF7A10 luz suave atras do texto (sobe o contraste do texto escuro)


def raios_sol(f, fx, fy, esc, rot, cor=AMAR):
    _, raios = mascaras_logo()
    return compor(f, transformar(raios, esc, rot, (fx, fy)), cor)


def conceito_b(fx=420, fy=640, esc_raio=2.6, rot=22):
    """B "Laranja Seara": laranja da peca oficial na tela toda, luz amarelo-alaranjada atras dos pacotes,
    raios oficiais gigantes; luz suave atras do texto para o texto escuro (nome, preco) ganhar contraste."""
    # versao escolhida pelo Vitor (18/11/2026): laranja inteiro, preco no amarelo padrao, luz amarela forte
    # atras das embalagens como na peca oficial Seara, raios oficiais da logo; sem luz atras do texto
    f = grad_radial(430, 430, 700, (255, 214, 10), LAR, 0.85)
    f = raios_sol(f, fx, fy, esc_raio, rot)
    return f


def conceito_c(fx=420, fy=640, esc_raio=2.6, rot=22):
    """C "Laranja com campo vermelho": laranja da peca oficial na zona do produto e nas bordas, com luz e
    raios oficiais; campo vermelho profundo Seara atras do texto e da coluna da marca, com a borda esquerda
    no arco do oval da logo; mantem preco amarelo Oriundi e texto branco."""
    f = grad_radial(420, 470, 760, LAR_LUZ, LAR, 1.1)
    f = raios_sol(f, fx, fy, esc_raio, rot)
    verm = grad_radial(1500, 470, 1100, (150, 10, 18), ESC, 1.2)
    campo = elipse(1720, 462, 920, 700)  # arco do oval: borda esquerda curva entre x ~800 e 860
    f = compor(f, campo, verm)
    return f


if __name__ == '__main__':
    args = [float(v) for v in sys.argv[3:]]
    f = {'A': conceito_a, 'B': conceito_b, 'C': conceito_c}[sys.argv[1]](*args)
    Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).save(sys.argv[2])
