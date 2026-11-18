# Recorte do Lek Trek apontando (foto do pote de lasanha enviada pelo Vitor, 18/11/2026).
# Fundo amarelo liso: fora = amarelo (B baixo, R e G altos); bico e faixa da mascara voltam pelo fill_holes.
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
def recorte(src, corte_y, mao_x=500, mao_y=368):
    a=np.asarray(Image.open(src).convert('RGB')).astype(float)
    r,g,b=a[...,0],a[...,1],a[...,2]
    amarelo=(r>215)&(g>175)&(b<120)&(r-b>120)
    fg=~amarelo
    fg[corte_y:, :mao_x]=False; fg[mao_y:]=False; luva=(b>150)&(np.abs(r-b)<45); fg[corte_y-4:, mao_x:]&=luva[corte_y-4:, mao_x:];  # abaixo do pote só a luva branca
    fg[:, :140]=False; fg[:, 650:]=False
    fg=ndi.binary_opening(fg,iterations=1)
    lab,n=ndi.label(fg); tam=ndi.sum(fg,lab,range(1,n+1))
    fg=np.isin(lab, 1+np.where(tam>=max(400, tam.max()*0.01))[0])
    fg=ndi.binary_closing(fg,iterations=2); fg=ndi.binary_fill_holes(fg)
    # alfa suave e descontaminação do amarelo na borda
    al=np.clip(ndi.gaussian_filter(fg.astype(float),0.8)*1.6-0.3,0,1)
    borda=(al>0)&(al<1)
    bg=np.array([252,218,45.])
    rgb=a.copy()
    m=borda[...,None]
    rgb=np.where(m,np.clip((a-bg*(1-al[...,None]))/np.maximum(al[...,None],0.25),0,255),a)
    out=Image.fromarray(np.dstack([rgb.astype(np.uint8),(al*255).astype(np.uint8)]),'RGBA')
    bb=out.getbbox(); return out.crop(bb), bb
if __name__=='__main__':
    o,bb=recorte(sys.argv[1], int(sys.argv[3])); o.save(sys.argv[2]); print(o.size, bb)
