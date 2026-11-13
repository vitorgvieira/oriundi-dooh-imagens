import sys
from PIL import Image
from sombra_mesa import prep, sombra_mesa
W,H=830,924
L=int(sys.argv[1]); rot=float(sys.argv[2])
pos=[tuple(map(int,p.split(','))) for p in sys.argv[3:6]]
c=Image.new('RGBA',(W,H),(0,0,0,0))
for f,p in zip(['branco.png','meioamargo.png','aoleite.png'],pos):
  sombra_mesa(c,prep(f,L,rot),p)
a=c.split()[-1].point(lambda v:255 if v>128 else 0); print('visivel',a.getbbox())
c.save('prod3.png')
bg=Image.open('fundo_toalha2.png').convert('RGBA'); bg.alpha_composite(c,(0,0))
bg.convert('RGB').resize((1078,462)).save('mock3.jpg')
