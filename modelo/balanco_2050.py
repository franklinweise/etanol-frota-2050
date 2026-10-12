"""
Balanco de oferta e demanda de etanol (secao 3 do artigo), com a demanda nova
(automoveis + comerciais leves nao-diesel + motocicletas, E32) de etanol_por_segmento.py.
Oferta e outros usos: premissas do artigo (cana 27,3 bi L estavel; milho 10 -> 20 bi L
linear 2025-2032; outros usos 3,0 -> 4,5 bi L linear 2025-2040).
Tambem: sensibilidade aos mitigadores (Tabela 4) e contrafactual do hibrido-flex (2.3).
Saida: resultados/balanco_2050.csv
"""
import csv
import numpy as np
import modelo_frota_etanol_v3 as v3
import projecao_2050 as pl
import motos_projecao as mp
import etanol_por_segmento as es

ANOS = pl.ANOS
CANA = 27.3
def milho(a): return 10 + 10 * min(max(a - 2025, 0), 7) / 7
def oferta(a, milho_teto=20, cana=CANA): return cana + min(milho(a), milho_teto)
def outros(a): return 3.0 + 1.5 * min(max(a - 2025, 0), 15) / 15
FR_ANID_L = lambda a: mp.GASC_L * pl.teor(a) / (mp.HID_L + mp.GASC_L * pl.teor(a))

def rodar(intens=None):
    orig = dict(v3.INTENS)
    if intens: v3.INTENS.update(intens)
    out = {}
    for lim in ("inferior", "superior"):
        for pn, g in pl.PIB.items():
            mot = pl.motorizacao(g, lim)
            frota = mot / 1000 * np.array([pl.POP[a] for a in ANOS])
            m = mp.projetar(lim, g)
            for traj in ("rapida", "central", "lenta"):
                au, cl = es.projetar_seg(frota, traj)
                motos = m["hid"] + m["anid"]
                anid = np.array([(au[i] + cl[i]) * FR_ANID_L(int(a)) for i, a in enumerate(ANOS)]) + m["anid"]
                out[(lim, pn, traj)] = {"dem": au + cl + motos, "anid": anid}
    v3.INTENS.clear(); v3.INTENS.update(orig)
    return out

if __name__ == "__main__":
    R = rodar()
    rows = []
    for (lim, pn, traj), r in R.items():
        for i, a in enumerate(ANOS):
            a = int(a)
            rows.append([a, lim, pn, traj, round(oferta(a), 2), round(r["dem"][i], 2), round(outros(a), 2),
                         round(oferta(a) - r["dem"][i] - outros(a), 2), round(r["anid"][i], 2)])
    with open("resultados/balanco_2050.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ano", "motorizacao_limite", "cenario_pib", "trajetoria_eletrificacao", "oferta_bi_l",
                    "demanda_veiculos_bi_l", "outros_usos_bi_l", "excedente_bi_l", "anidro_bi_l"])
        w.writerows(rows)
    rng = lambda v: f"{min(v):.1f}-{max(v):.1f}"
    print("TABELA 5 do artigo - balanco de oferta e demanda (bi L/ano)")
    for a in (2025, 2030, 2035, 2040, 2045, 2050):
        i = a - 2025
        d = {t: [r["dem"][i] for k, r in R.items() if k[2] == t] for t in ("rapida", "central", "lenta")}
        ex = [oferta(a) - x - outros(a) for t in d for x in d[t]]
        exc = [oferta(a) - x - outros(a) for x in d["central"]]
        print(a, f"oferta {oferta(a):.1f}", " ".join(f"{t} {rng(d[t])}" for t in d), f"outros {outros(a):.1f}",
              f"exc {rng(ex)} | central {rng(exc)}")
    print("\nTABELA 6 do artigo - sensibilidade do excedente central (faixa dos 6 cenarios)")
    for nome, f in [("base", lambda a, r, i: 0),
                    ("milho 15", lambda a, r, i: -5),
                    ("mix 60 (cana 22)", lambda a, r, i: -5.3),
                    ("E35", lambda a, r, i: -r["anid"][i] * 3 / 32),
                    ("export +8", lambda a, r, i: -8),
                    ("tres juntos", lambda a, r, i: -10.3 - r["anid"][i] * 3 / 32)]:
        s = []
        for a in (2035, 2040):
            i = a - 2025
            v = [oferta(a) - r["dem"][i] - outros(a) + f(a, r, i) for k, r in R.items() if k[2] == "central"]
            s.append(rng(v))
        print(f"  {nome:<18}", " | ".join(s))
    for a in (2035, 2040):
        i = a - 2025
        v = [oferta(a) - r["dem"][i] - outros(a) - 10.3 for k, r in R.items() if k[2] == "lenta"]
        print("  lenta+milho15+mix60", a, rng(v))
    v = [r["anid"][i] * 3 / 32 for k, r in R.items() for i in (10, 15)]
    print("  E35 incremento", rng(v))
    # hibrido-flex: contrafactual em que HEV e PHEV fossem BEV
    C = rodar({"HEV": 0.0, "PHEV": 0.0})
    print("\nHIBRIDO-FLEX: pontos de indice (2025=100) preservados em 2040")
    for t in ("rapida", "central", "lenta"):
        p = [100 * (R[k]["dem"][15] - C[k]["dem"][15]) / R[k]["dem"][0] for k in R if k[2] == t]
        print(f"  {t}: {rng(p)}")
    # SAF 1 bi L como fracao do excedente 2040
    ex40 = [oferta(2040) - r["dem"][15] - outros(2040) for r in R.values()]
    print("\nSAF 1 bi L / excedente 2040:", f"{100/max(ex40):.1f}% a {100/min(ex40):.1f}%")
