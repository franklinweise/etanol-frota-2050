#!/usr/bin/env bash
# Reproduz todos os resultados do artigo a partir da pasta raiz do repositorio.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p resultados
python3 modelo/calibrar_por_safra.py      # curva de sucateamento de leves (resultados/calibracao_por_safra.json)
python3 modelo/projecao_2050.py           # frota, vendas e etanol de leves (Tabela 2; Figuras 1, 4, 5)
python3 modelo/motos_projecao.py          # motocicletas (Tabela 3; Figura 2)
python3 modelo/etanol_por_segmento.py     # etanol por segmento (Tabela 4; Figura 7)
python3 modelo/frota_segmentos.py         # frota por segmento 2010-2050 (Figura 3)
python3 modelo/balanco_2050.py            # balanco, sensibilidades e hibrido-flex (Tabelas 5 e 6; Figura 8; secao 2.4)
python3 modelo/teste_2026.py              # teste com a projecao da Anfavea para 2026 (nota da Tabela 2)
echo "Concluido. Resultados em resultados/."
