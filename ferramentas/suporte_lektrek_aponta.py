# Lek Trek apontando para o preço, apoiado na base vermelha (18/11/2026).
# Corpo atrás da base; a mão direita dele passa por cima da borda da base, como no pote da foto original.
import sys
sys.path.insert(0, 'ferramentas')
from PIL import Image, ImageDraw
from lektrek_aponta import recorte
X0, Y0, X1, Y1 = 1690, 300, 2156, 924
BASE_TOP, BASE_X, RAIO = 620, 1700, 50
VERM = (210, 35, 42, 255)
LEK_W, LEK_X, AFUNDA = 440, 1706, 2
CORTE, MAO_X = 336, 500   # linha do pote e início da mão, na foto original
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
    cam = Image.new('RGBA', (W, H), VERM); cam.putalpha(base.resize((W, H), Image.LANCZOS)); c.alpha_composite(cam)
    mx = round((MAO_X - bb[0]) * s); my = round((CORTE - 30 - bb[1]) * s)
    mao = m.crop((mx, my, m.width, m.height))
    c.alpha_composite(mao, (LEK_X - X0 + mx, top - Y0 + my))
    c.save(saida); print('elemento', (X0, Y0, W, H), 'mascote topo', top, 'x', LEK_X, LEK_X + LEK_W)
if __name__ == '__main__':
    montar(sys.argv[1], sys.argv[2])
