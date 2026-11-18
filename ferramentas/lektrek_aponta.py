# Recorte do Lek Trek apontando (foto do pote de lasanha enviada pelo Vitor, 18/11/2026).
# 1) máscara dura: tudo que não é o amarelo do fundo; bico e faixa da máscara voltam pelo fill_holes.
# 2) refino da borda (faixa de ~3 px): alfa por projeção entre a cor do fundo local (B) e a cor
#    do mascote mais próxima (F); a cor da borda vira F, sem franja amarela.
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

def recorte(src, corte_y, mao_x=500, mao_y=368, banda=2):
    a = np.asarray(Image.open(src).convert('RGB')).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    amarelo = (r > 215) & (g > 175) & (b < 120) & (r - b > 120)
    fg = ~amarelo
    luva = (b > 150) & (np.abs(r - b) < 45)
    fg[corte_y:, :mao_x] = False; fg[mao_y:] = False
    fg[corte_y:, mao_x:] &= ndi.binary_dilation(luva, iterations=1)[corte_y:, mao_x:]   # abaixo da borda do pote, só a luva
    fg[:, :140] = False; fg[:, 650:] = False
    fg = ndi.binary_opening(fg, iterations=1)
    lab, n = ndi.label(fg); tam = ndi.sum(fg, lab, range(1, n + 1))
    fg = np.isin(lab, 1 + np.where(tam >= max(400, tam.max() * 0.01))[0])
    fg = ndi.binary_closing(fg, iterations=2); fg = ndi.binary_fill_holes(fg)
    certo = ndi.binary_erosion(fg, iterations=banda)
    fora = ~ndi.binary_dilation(fg, iterations=banda)
    # fundo local B (só do amarelo de verdade) e cor do mascote F (pixel firme mais próximo)
    _, (iy, ix) = ndi.distance_transform_edt(~(fora & amarelo), return_indices=True)
    B = ndi.gaussian_filter(a[iy, ix], (4, 4, 0))
    firme = ndi.binary_erosion(fg, iterations=1)   # cor F colada na borda (sem clarear o contorno)
    _, (jy, jx) = ndi.distance_transform_edt(~firme, return_indices=True)
    F = a[jy, jx]
    d = F - B; n2 = (d ** 2).sum(-1)
    proj = np.clip((((a - B) * d).sum(-1) / np.maximum(n2, 1) - 0.18) / 0.7, 0, 1)   # borda mais firme, sem halo
    al = np.where(certo, 1.0, np.where(fora, 0.0, np.where(n2 > 900, proj, fg.astype(float))))
    al[corte_y:, :mao_x] = np.minimum(al[corte_y:, :mao_x], 0)   # corte reto do corpo (fica atrás da base)
    al[mao_y:] = 0
    # borda do pote logo acima do corte (amarelo sem ser o fundo liso): fora
    pote = ((b < 130) & (r > 170) & (g > 130) & (r - b > 90)) | ((r > 230) & (g > 195) & (r - b > 45))   # inclui o brilho claro da borda
    al[corte_y - 10:corte_y][pote[corte_y - 10:corte_y]] = 0
    # dedos sobre o pote: alfa suave pela 'brancura' da luva (sem degraus na borda de baixo)
    luva_s = np.clip((b - 120) / 50, 0, 1) * np.clip((65 - np.abs(r - b)) / 30, 0, 1)
    luva_s = ndi.gaussian_filter(luva_s, 0.6)
    al[corte_y:, mao_x:] = np.minimum(al[corte_y:, mao_x:], luva_s[corte_y:, mao_x:])
    lab2, n2_ = ndi.label(al > 0.05); t2 = ndi.sum(al > 0.05, lab2, range(1, n2_ + 1))
    al[~np.isin(lab2, 1 + np.where(t2 >= 400)[0])] = 0          # tira restos soltos (brilho do pote)
    al = ndi.gaussian_filter(al, 0.35)
    cor = np.where(firme[..., None], a, F)            # borda com a cor do mascote, sem amarelo
    out = Image.fromarray(np.dstack([cor.clip(0, 255).astype(np.uint8), (al * 255).round().astype(np.uint8)]), 'RGBA')
    bb = out.getbbox(); return out.crop(bb), bb

if __name__ == '__main__':
    o, bb = recorte(sys.argv[1], int(sys.argv[3])); o.save(sys.argv[2]); print(o.size, bb)
