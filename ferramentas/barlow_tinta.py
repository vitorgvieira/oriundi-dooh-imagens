# Tinta dos glifos da Barlow Condensed (fontsource woff em /tmp/fonts). Uso: ink(texto, x_caixa, corpo, letter_spacing_em, peso)
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
F={}
def font(w):
    if w not in F:
        f=TTFont('/tmp/fonts/pkg/package/files/barlow-condensed-latin-%s-normal.woff'%w)
        F[w]=(f,f.getGlyphSet(),f.getBestCmap())
    return F[w]
def ink(text,left,size,ls=-0.02,w='700'):
    """ink x0,x1 relativos e por glifo; ls em em"""
    f,gs,cm=font(w); x=0; xs=[]
    for i,ch in enumerate(text):
        g=gs[cm[ord(ch)]]; bp=BoundsPen(gs); g.draw(bp)
        b=bp.bounds
        if b is None: x+=g.width+ls*1000; continue
        xs.append((left+(x+b[0])*size/1000, left+(x+b[2])*size/1000, ch))
        x+=g.width+ls*1000
    return xs
if __name__=='__main__':
    for ls in (-0.02,0):
        print(ls, [(round(a),round(b),c) for a,b,c in ink('16',1009,440,ls)], [(round(a),round(b),c) for a,b,c in ink(',79',1345.3,242,ls)], [(round(a),round(b),c) for a,b,c in ink('R$',880,112,ls)])
