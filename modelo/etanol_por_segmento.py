"""
Etanol por segmento: automoveis, comerciais leves nao-diesel e motocicletas.

Mesma frota, vendas e eletrificacao de projecao_2050.py, mas o estoque nao-diesel
e acompanhado separadamente para automoveis e comerciais leves:
  - legado: vendas Anfavea por segmento (fracao nao-diesel) x curva do segmento;
  - vendas futuras nao-diesel: fatias de 2025 (automoveis / comerciais leves).
Base de 2025 dividida pelas participacoes do Inventario Nacional de Emissoes
2025 (ano-base 2024, Apendice B): entre os leves, comerciais leves = 10,9% do
etanol (anidro + hidratado). Cada segmento evolui com o proprio indice de
consumo (estoque x intensidade da motorizacao), e o consumo por veiculo de cada
segmento fica constante.

Saida: resultados/etanol_segmentos_2050.csv
"""
import csv
import numpy as np
import modelo_frota_etanol_v3 as v3
import rodar_v3_sem_diesel as sd
import projecao_2050 as pl
import motos_projecao as mp

ANOS, T = pl.ANOS, pl.T
# Inventario 2025, etanol 2024 (mil m3): autos e comerciais leves (anidro + hidratado)
ETANOL_AUTOS_INV = 1966 + 8285 + 77 + 349 + 19897
ETANOL_CL_INV = 106 + 1087 + 0.48 + 13 + 2552
FRAC_CL = ETANOL_CL_INV / (ETANOL_AUTOS_INV + ETANOL_CL_INV)

ND_AU, ND_CL = sd.ND_AU, sd.ND_CL
W_AU, W_CL = ND_AU / (ND_AU + ND_CL), ND_CL / (ND_AU + ND_CL)


def legado_seg(t):
    """Frota legada nao-diesel por segmento no ano 2025 + t."""
    out = {}
    for seg, S, dd, pre in (("automoveis", sd.S_AUTO, sd.D_AU, sd.D_AU_PRE),
                            ("comerciais_leves", sd.S_CL, sd.D_CL, sd.D_CL_PRE)):
        tot = 0.0
        for c, v in sd.V[seg].items():
            x = 2025 + t - c
            if x < len(S):
                tot += v * (1 - dd.get(c, pre)) * S[x]
        out[seg] = tot
    return out


def projetar_seg(frota_alvo, traj):
    base = pl.projetar(frota_alvo, traj)          # vendas e totais do modelo principal
    vendas = base["vendas"]
    leg = [legado_seg(t) for t in range(T)]
    leg_tot = np.array([sum(sd.legado(t)) for t in range(T)])
    esc = frota_alvo[0] / leg_tot[0]
    mix = sd.mix_nd(traj)
    inten = sum(mix[k] * v3.INTENS[k] for k in v3.INTENS)
    eth = {"automoveis": np.array([l["automoveis"] for l in leg]) * esc,
           "comerciais_leves": np.array([l["comerciais_leves"] for l in leg]) * esc}
    for ti in range(T):
        for c in range(1, ti + 1):
            nd = vendas[c] * (1 - sd.D_FUT)
            eth["automoveis"][ti] += nd * W_AU * sd.S_AUTO[ti - c] * inten[c]
            eth["comerciais_leves"][ti] += nd * W_CL * sd.S_CL[ti - c] * inten[c]
    base_leves = np.array([(mp.HID_L + mp.GASC_L * pl.teor(int(a))) / 1e9 for a in ANOS])
    autos = base_leves * (1 - FRAC_CL) * eth["automoveis"] / eth["automoveis"][0]
    cl = base_leves * FRAC_CL * eth["comerciais_leves"] / eth["comerciais_leves"][0]
    return autos, cl


if __name__ == "__main__":
    print(f"comerciais leves = {100*FRAC_CL:.1f}% do etanol dos leves (Inventario 2024)")
    linhas = []
    for lim in ("inferior", "superior"):
        for pn, g in pl.PIB.items():
            mot = pl.motorizacao(g, lim)
            frota = mot / 1000 * np.array([pl.POP[a] for a in ANOS])
            m = mp.projetar(lim, g)
            for traj in ("rapida", "central", "lenta"):
                autos, cl = projetar_seg(frota, traj)
                motos = m["hid"] + m["anid"]
                for i, a in enumerate(ANOS):
                    linhas.append([int(a), lim, pn, traj, round(autos[i], 2), round(cl[i], 2),
                                   round(motos[i], 2), round(autos[i] + cl[i] + motos[i], 2)])
    with open("resultados/etanol_segmentos_2050.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ano", "motorizacao_limite", "cenario_pib", "trajetoria_eletrificacao",
                    "etanol_automoveis_bi_l", "etanol_comerciais_leves_bi_l", "etanol_motos_bi_l", "etanol_total_bi_l"])
        w.writerows(linhas)
    for t in ("rapida", "central", "lenta"):
        print(t)
        for a in (2025, 2030, 2035, 2040, 2045, 2050):
            r = [l for l in linhas if l[0] == a and l[3] == t]
            f = lambda k: f"{min(x[k] for x in r):.1f}-{max(x[k] for x in r):.1f}"
            print(f"  {a} autos {f(4)} | CL {f(5)} | motos {f(6)} | total {f(7)}")
