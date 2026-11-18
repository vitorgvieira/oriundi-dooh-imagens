import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
VERM=(210,35,42,255); X1,Y1=2156,924
BASE_TOP,BASE_X,RAIO=620,1700,50
def recorte_novo():
    im=Image.open('/mnt/user-data/uploads/996423c4-image.png').convert('RGB')
    a=np.asarray(im).astype(float); d=255-a.min(axis=2)
    lab,_=ndi.label(d<=2)
    edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    fg=~np.isin(lab,list(edge))
    al=np.clip((ndi.gaussian_filter(fg.astype(float),0.7)-0.15)/0.7,0,1)*fg
    out=Image.fromarray(np.dstack([a.astype(np.uint8),(al*255).astype(np.uint8)]),'RGBA')
    return out
def elemento(masc, w, x, afunda, X0, Y0, saida):
    W,H=X1-X0,Y1-Y0
    c=Image.new('RGBA',(W,H),(0,0,0,0))
    m=masc.resize((w,round(masc.height*w/masc.width)),Image.LANCZOS)
    top=BASE_TOP+afunda-m.height
    c.alpha_composite(m,(x-X0,top-Y0))
    base=Image.new('L',(W*2,H*2),0)
    ImageDraw.Draw(base).rounded_rectangle(((BASE_X-X0)*2,(BASE_TOP-Y0)*2,W*2+400,H*2+400),RAIO*2,fill=255)
    base=base.resize((W,H),Image.LANCZOS)
    cam=Image.new('RGBA',(W,H),VERM); cam.putalpha(base); c.alpha_composite(cam)
    c.save(saida); print(saida,(X0,Y0,W,H),'topo mascote',top,'x',x,'-',x+w)
    return c
def mock(el,X0,Y0,saida):
    p=Image.open('/tmp/dooh/peca_F3.png').convert('RGBA')
    f=Image.open('brf/sadia/fundos/fundo_sadia_F.png').convert('RGBA')
    p.paste(f.crop((1690,250,2156,924)),(1690,250))
    p.alpha_composite(el,(X0,Y0))
    s=Image.open('oriundi/meu-oriundi/assinatura_canto_meu_oriundi_branca.png').convert('RGBA').resize((260,206))
    p.alpha_composite(s,(1798,669))
    p.convert('RGB').save(saida)
if __name__=='__main__':
    atual=Image.open('brf/sadia/elementos/lektrek_recorte.png').convert('RGBA')
    A=elemento(atual,456,1700,6,1690,310,'/tmp/dooh/el_A.png'); mock(A,1690,310,'/tmp/dooh/mock_A2.png')
    n=recorte_novo(); n.save('/tmp/dooh/lek2_full.png')
    n=n.crop((592,80,1293,712)); n.save('/tmp/dooh/lek2_bust.png')
    B=elemento(n,400,1723,8,1690,250,'/tmp/dooh/el_B.png'); mock(B,1690,250,'/tmp/dooh/mock_B2.png')
