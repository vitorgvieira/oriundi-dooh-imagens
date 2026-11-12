#!/usr/bin/env python3
"""Mede uma peca do layout B (miniatura do edit-design) e/ou o fundo sozinho.

Uso:
  python medir.py peca.png --caso 2_de [--fundo fundo.png] [--elementos el.json] [--leitura leitura.png]

- peca.png: miniatura da peca montada (qualquer largura, proporcao 2156x924).
- --fundo: imagem do fundo ja no enquadramento 2156x924. Da o contraste exato e confere os cantos das logos.
- --elementos: JSON [{"nome":"produto_visivel","x":..,"y":..,"w":..,"h":..}, ...] em px de 2156x924.
- --leitura: salva a peca com 300 px de largura (teste de leitura em 3 s para o revisor).
Saida: JSON com ok, falhas, avisos e medidas. Todas as medidas em px de 2156x924.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

AQUI = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(AQUI, "layout_b.json"), encoding="utf-8"))
W, H = L["tela"]["w"], L["tela"]["h"]

# zonas de texto (px 2156x924): x0, y0, x1, y1
ZONAS_TEXTO = {"nome": (870, 150, 1720, 400), "preco": (870, 380, 1720, 760), "validade": (1190, 815, 1650, 880)}
# zonas das logos no fundo (px), a partir das porcentagens do prompt
ZONAS_LOGO = {"logo_marca": (int(.81 * W), int(.04 * H), int(.97 * W), int(.20 * H)),
              "logo_oriundi": (int(.81 * W), int(.70 * H), int(.97 * W), int(.96 * H))}


def carregar(caminho):
    im = Image.open(caminho).convert("RGB")
    if abs(im.width / im.height - W / H) > 0.03:
        print(json.dumps({"ok": False, "falhas": [f"proporcao {im.width}x{im.height} nao e 2156x924"]}))
        sys.exit(1)
    return np.asarray(im).astype(np.float32) / 255.0, W / im.width


def luminancia(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def razao(lum):
    return round(float(1.05 / (lum + 0.05)), 2)


def recorte(arr, esc, caixa):
    x0, y0, x1, y1 = [int(round(v / esc)) for v in caixa]
    return arr[y0:y1, x0:x1]


def mascara_branco(arr, esc):
    m = arr.min(axis=2) >= 0.78
    return ndimage.binary_dilation(m, iterations=max(1, int(round(3 / esc))))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("peca")
    p.add_argument("--caso", required=True, help="chave de preco no layout_b.json (ex.: 2_de)")
    p.add_argument("--fundo")
    p.add_argument("--elementos")
    p.add_argument("--leitura")
    a = p.parse_args()

    falhas, avisos, med = [], [], {}
    arr, esc = carregar(a.peca)
    branco = mascara_branco(arr, esc)
    meta = L["contraste"]

    # 1. contraste atras do texto
    fonte_bg, esc_bg = (carregar(a.fundo) if a.fundo else (arr, esc))
    for nome, caixa in ZONAS_TEXTO.items():
        z = recorte(fonte_bg, esc_bg, caixa)
        lum = luminancia(z)
        if not a.fundo:
            lum = lum[~recorte(branco[..., None], esc, caixa)[..., 0]]
        lum = lum.ravel()
        if lum.size < 50:
            avisos.append(f"{nome}: poucos pixels de fundo para medir")
            continue
        r_med, r_claro = razao(np.median(lum)), razao(np.percentile(lum, 90))
        med[f"contraste_{nome}"] = {"mediana": r_med, "claros10": r_claro}
        if r_med < meta["mediana_min"]:
            falhas.append(f"contraste {nome}: mediana {r_med}:1 < {meta['mediana_min']}:1")
        if r_claro < meta["claros10_min"]:
            falhas.append(f"contraste {nome}: 10% mais claros {r_claro}:1 < {meta['claros10_min']}:1")
    if not a.fundo:
        avisos.append("contraste medido na peca (sem --fundo): brilhos brancos do fundo ficam de fora")

    # 2. cantos das logos limpos (so com o fundo sozinho)
    if a.fundo:
        for nome, caixa in ZONAS_LOGO.items():
            lum = luminancia(recorte(fonte_bg, esc_bg, caixa))
            desvio = float(lum.std())
            fora = float((np.abs(lum - np.median(lum)) > 0.08).mean())
            med[f"canto_{nome}"] = {"desvio": round(desvio, 4), "pixels_fora_pct": round(100 * fora, 1)}
            if desvio > 0.04 or fora > 0.05:
                falhas.append(f"canto {nome} com elementos ou brilho (desvio {desvio:.3f}, {100*fora:.1f}% fora)")
    else:
        avisos.append("cantos das logos nao conferidos (precisa de --fundo)")

    # 3. texto x coluna de marca: ponta direita do nome e do preco
    lim = L["zonas"]["limite_direito_texto"]
    col0 = L["zonas"]["coluna_marca"]["x0"]
    base_m = branco if a.fundo is None else (arr.min(axis=2) >= 0.78)
    for nome, (y0, y1) in {"nome": (185, 400), "preco": (380, 760)}.items():
        faixa = recorte(base_m[..., None], esc, (880, y0, col0, y1))[..., 0]
        cols = np.where(faixa.any(axis=0))[0]
        if cols.size:
            fim = int(round(880 + (cols.max() + 1) * esc))
            med[f"{nome}_fim_x"] = fim
            if fim > lim:
                falhas.append(f"{nome} termina em x {fim} (> {lim}): colado na coluna de marca")
            elif nome == "nome" and fim > L["zonas"]["aviso_nome_longo_x"]:
                avisos.append(f"nome termina em x {fim}: propor cortar palavra de categoria")

    # 4. respiro da virgula
    caso = L["preco"].get(a.caso, {})
    if "centavos" in caso:
        inteiro, cent = caso["inteiro"], caso["centavos"]
        vis = caso.get("visivel", {})
        y0 = vis.get("y0", inteiro["topo"] + 0.12 * inteiro["corpo"])
        y1 = vis.get("y1", inteiro["topo"] + 0.85 * inteiro["corpo"])
        faixa = recorte((arr.min(axis=2) >= 0.78)[..., None], esc, (880, y0, col0, y1))[..., 0]
        altura = faixa.sum(axis=0)
        altos = np.where(altura > 0.6 * faixa.shape[0])[0]
        minimo = L["virgula"]["respiro_min_pct_corpo_inteiro"] * inteiro["corpo"]
        if altos.size:
            fim_int = altos.max()
            depois = np.where(altura[fim_int + 1:] > 0)[0]
            if depois.size:
                gap = depois.min() * esc
                med["virgula_respiro_px"] = int(round(gap))
                if gap < minimo * 0.85:
                    falhas.append(f"virgula com respiro de {gap:.0f} px (minimo ~{minimo:.0f})")
        else:
            avisos.append("inteiro do preco nao encontrado na faixa: respiro da virgula nao conferido")
    else:
        avisos.append(f"caso {a.caso} sem medida de preco: respiro da virgula nao conferido")

    # 5. margens e folga do produto (com --elementos)
    if a.elementos:
        t = L["tela"]
        for e in json.load(open(a.elementos, encoding="utf-8")):
            x1, y1 = e["x"] + e["w"], e["y"] + e["h"]
            if e["nome"].startswith("fundo"):
                continue
            if e["x"] < t["margem_lateral"] - 2 or x1 > W - t["margem_lateral"] + 2 \
               or e["y"] < t["margem_vertical"] - 2 or y1 > H - t["margem_vertical"] + 2:
                if not e["nome"].startswith("produto"):
                    falhas.append(f"{e['nome']} fora da margem de seguranca")
            if e["nome"] == "produto_visivel":
                med["produto_fim_x"] = int(round(x1))
                if x1 > L["zonas"]["produto"]["fim_visivel_max"]:
                    falhas.append(f"produto termina em x {x1:.0f}: folga ate o R$ < 110 px")
    else:
        avisos.append("margens e folga do produto nao conferidas (precisa de --elementos)")

    if a.leitura:
        Image.open(a.peca).convert("RGB").resize((300, round(300 * H / W)), Image.LANCZOS).save(a.leitura)
        med["leitura"] = a.leitura

    print(json.dumps({"ok": not falhas, "falhas": falhas, "avisos": avisos, "medidas": med},
                     ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
