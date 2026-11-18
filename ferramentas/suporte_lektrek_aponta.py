# Lek Trek apontando para o preço, apoiado na base vermelha (18/11/2026).
# Corpo atrás da base; a mão direita passa por cima da borda da base, como no pote da foto,
# com a sombra de contato da mão sobre a base (pedido do Vitor), em vermelho escuro, só na base.
import sys
sys.path.insert(0, 'ferramentas')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lektrek_aponta import recorte
X0, Y0, X1, Y1 = 1690, 300, 2156, 924
BASE_TOP, BASE_X, RAIO = 620, 1700, 50
VERM = (210, 35, 42, 255)
SOMBRA = (110, 12, 18)              # vermelho bem fechado (multiplica a base, não é preto)
LEK_W, LEK_X, AFUNDA = 440, 1706, 0
CORTE, MAO_X = 341, 500             # borda do pote (vira a borda da base) e início da mão, na foto original

def montar(src, saida):
    m, bb = recorte(src, CORTE, MAO_X)
    s = LEK_W / m.width
    m = m.resize((LEK_W, round(m.height * s)), Image.LANCZOS)
    top = BASE_TOP + AFUNDA - round((CORTE - bb[1]) * s)
    W, H = X1 - X0, Y1 - Y0
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    c.alpha_composite(m, (LEK_X - X0, top - Y0))
    base = Image.new('L', (W * 2, H * 2), 0)
    ImageDraw.Draw(base).rounded_rectangle(((BASE_X - X0) * 2, (BASE_TOP - Y0) * 2, W * 2 + 400, H * 2 + 400), RAIO * 2, fill=255)
    base = base.resize((W, H), Image.LANCZOS)
    cam = Image.new('RGBA', (W, H), VERM); cam.putalpha(base); c.alpha_composite(cam)
    # mão por cima da borda
    mx = round((MAO_X - bb[0]) * s); my = round((CORTE - 30 - bb[1]) * s)
    mao = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    mao.alpha_composite(m.crop((mx, my, m.width, m.height)), (LEK_X - X0 + mx, top - Y0 + my))
    am = np.asarray(mao.getchannel('A')).astype(float) / 255
    # sombra: projetada (desce e vai um pouco à direita, como na foto) + contato colado nos dedos
    def desloca(x, dx, dy):
        return np.roll(np.roll(x, dy, 0), dx, 1)
    proj = np.asarray(Image.fromarray((desloca(am, 7, 12) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))).astype(float) / 255
    cont = np.asarray(Image.fromarray((desloca(am, 2, 3) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5))).astype(float) / 255
    k = np.clip(proj * 0.65 + cont * 0.5, 0, 0.8) * (np.asarray(base).astype(float) / 255) * (1 - am)
    som = Image.new('RGBA', (W, H), SOMBRA + (255,)); som.putalpha(Image.fromarray((k * 255).astype(np.uint8)))
    c.alpha_composite(som)
    c.alpha_composite(mao)
    c.save(saida); print('elemento', (X0, Y0, W, H), 'mascote topo', top, 'x', LEK_X, LEK_X + LEK_W)

if __name__ == '__main__':
    montar(sys.argv[1], sys.argv[2])
