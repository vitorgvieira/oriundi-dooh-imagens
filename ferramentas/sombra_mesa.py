from PIL import Image, ImageFilter
import numpy as np
W,H=830,924
def prep(p,L,rot):
  im=Image.open(p).convert('RGBA'); im=im.crop(im.getbbox())
  s=L/im.width; im=im.resize((L,round(im.height*s)),Image.LANCZOS)
  return im.rotate(rot,expand=True,resample=Image.BICUBIC)
def layer_shadow(alpha, off, blur, col, a, size, pos):
  pad=120; c=Image.new('RGBA',(size[0]+2*pad,size[1]+2*pad),(0,0,0,0))
  al=alpha.point(lambda v:int(v*a)); lay=Image.new('RGBA',alpha.size,col+(255,)); lay.putalpha(al)
  c.paste(lay,(pad+pos[0]+off[0],pad+pos[1]+off[1]),lay)
  c=c.filter(ImageFilter.GaussianBlur(blur)); return c.crop((pad,pad,pad+size[0],pad+size[1]))
def sombra_mesa(canvas, im, pos):
  al=im.split()[-1]
  # sombra projetada larga (luz do canto superior esquerdo)
  canvas.alpha_composite(layer_shadow(al,(22,30),26,(45,18,4),0.42,canvas.size,pos))
  # sombra de contato curta e escura
  canvas.alpha_composite(layer_shadow(al,(5,7),6,(30,10,2),0.6,canvas.size,pos))
  canvas.alpha_composite(im,pos)
if __name__=='__main__':
  c=Image.new('RGBA',(W,H),(0,0,0,0))
  sombra_mesa(c,prep('branco.png',735,30),(18,70))
  sombra_mesa(c,prep('aoleite.png',735,22),(22,355))
  c.save('prod_mesa.png')
  # biscoito mordido apoiado na mesa
  b=Image.open('cut_mordido.png').convert('RGBA'); s=330/b.width; b=b.resize((330,round(b.height*s)),Image.LANCZOS).rotate(-8,expand=True,resample=Image.BICUBIC)
  cb=Image.new('RGBA',(b.width+80,b.height+80),(0,0,0,0)); sombra_mesa(cb,b,(20,20)); cb=cb.crop(cb.getbbox()); cb.save('biscoito_mesa.png'); print(cb.size)
