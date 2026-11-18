# Lek Trek apoiado numa base vermelha Sadia na coluna direita (pedido do Vitor, 18/11/2026):
# o corte do peito fica escondido atras da base; o selo Meu Oriundi branco vai em cima da base (no Canva).
# Saida: PNG transparente do tamanho da caixa, para inserir em (X0, Y0) na peca 2156x924.
import sys
from PIL import Image, ImageDraw
sys.path.insert(0, 'ferramentas')
from asset import sombra

X0, Y0, X1, Y1 = 1690, 310, 2156, 924     # caixa do elemento na peca
BASE_TOP, BASE_X, RAIO = 620, 1740, 70    # base vermelha: topo, borda esquerda, canto arredondado
VERM = (210, 35, 42, 255)
LEK_W, LEK_X, LEK_AFUNDA = 430, 1712, 34  # largura do mascote, x na peca, quanto o peito entra atras da base

def montar(saida):
    W, H = X1 - X0, Y1 - Y0
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lek = Image.open('brf/sadia/elementos/lektrek_recorte.png').convert('RGBA')
    lek = lek.resize((LEK_W, round(lek.height * LEK_W / lek.width)), Image.LANCZOS)
    ls = sombra(lek, '#5A2A00')                   # folga de 70 px em volta
    y_lek = BASE_TOP + LEK_AFUNDA - lek.height     # topo do mascote na peca
    c.alpha_composite(ls, (LEK_X - X0 - 70, y_lek - Y0 - 70))
    base = Image.new('L', (W * 2, H * 2), 0)
    ImageDraw.Draw(base).rounded_rectangle(((BASE_X - X0) * 2, (BASE_TOP - Y0) * 2, W * 2 + 400, H * 2 + 400), RAIO * 2, fill=255)
    base = base.resize((W, H), Image.LANCZOS)
    camada = Image.new('RGBA', (W, H), VERM); camada.putalpha(base)
    c.alpha_composite(camada)
    c.save(saida)
    print('elemento', (X0, Y0, W, H), 'mascote topo', y_lek)

if __name__ == '__main__':
    montar(sys.argv[1])
