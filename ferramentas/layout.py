#!/usr/bin/env python3
"""Devolve as posicoes do layout B para um caso de oferta.

Uso: python layout.py --digitos 2 [--de] [--meu-oriundi] [--produtos 2_frascos_leque]
Saida: JSON compacto. Codigo 2 = caso sem medida (parar e avisar o Vitor).
"""
import argparse, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--digitos", type=int, required=True, help="digitos antes da virgula")
    p.add_argument("--de", action="store_true", help="oferta com preco DE")
    p.add_argument("--meu-oriundi", action="store_true")
    p.add_argument("--produtos", help="chave de 'produtos' no JSON (ex.: 2_frascos_leque)")
    a = p.parse_args()

    L = json.load(open(os.path.join(AQUI, "layout_b.json"), encoding="utf-8"))
    chave = f"{a.digitos}_{'de' if a.de else 'sem_de'}"
    preco = L["preco"].get(chave)
    faltas = []
    if not preco or preco["status"] == "calibrar":
        faltas.append(f"preco {chave}")
    prod = None
    if a.produtos:
        prod = L["produtos"].get(a.produtos)
        if not prod or prod["status"] == "calibrar":
            faltas.append(f"produtos {a.produtos} (opcoes: {', '.join(L['produtos'])})")

    if faltas:
        print(json.dumps({"ok": False, "caso_sem_medida": faltas,
                          "acao": "parar, avisar o Vitor e propor calibrar; nao improvisar"}, ensure_ascii=False))
        sys.exit(2)

    nome = dict(L["nome"])
    nome["topo"] = nome.pop("topo_1_digito") if a.digitos == 1 else nome["topo"]
    nome.pop("topo_1_digito", None)
    out = {
        "ok": True, "caso": chave, "status_preco": preco["status"],
        "nome": {k: nome[k] for k in ("corpo", "caixa_w", "x", "topo")},
        "preco": {k: v for k, v in preco.items() if k not in ("status", "origem")},
        "validade": {k: L["validade"][k] for k in ("corpo", "caixa_w", "x", "topo")},
        "logo_marca": L["logos"]["marca"] | {"exemplos": None},
        "canto_inferior": (L["logos"]["assinatura_meu_oriundi"] if a.meu_oriundi else L["logos"]["oriundi"]),
        "fundo_crop": L["fundo"]["crop_media"],
    }
    out["logo_marca"].pop("exemplos")
    if a.de:
        out["risco_shape"] = L["risco_shape"]
    if a.meu_oriundi:
        out["validade_meu_oriundi"] = L["validade"]["meu_oriundi"]
    if prod:
        out["produtos"] = {k: v for k, v in prod.items() if k != "status"}
    print(json.dumps(out, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
