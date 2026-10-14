# Do excedente à produção de moléculas: modelo de frota e demanda de etanol, 2025–2050

Código, dados e resultados do artigo *Do excedente à produção de moléculas* (FATEC Shunji Nishimura, Pompeia, 2026).
O modelo projeta a frota de automóveis, comerciais leves e motocicletas do Brasil até 2050, a eletrificação das vendas
e a demanda de etanol resultante, e a confronta com a oferta de cana e milho.

**Autores:** Antonio Cesar, Alberto Honda, Carlos Otoboni, Marcela Campista B. Carvalho, Igor Polikarpov,
Franklin Weise e Hannes Fischer.

## Como rodar

Requer Python 3.10 ou superior.

```bash
pip install -r requirements.txt
./rodar_tudo.sh
```

Os scripts devem ser executados a partir da pasta raiz do repositório (o `rodar_tudo.sh` já faz isso), porque leem
`dados/` e gravam em `resultados/` por caminho relativo. A execução completa leva poucos segundos.
Os arquivos em `resultados/` deste repositório são exatamente os que geraram as tabelas e figuras do artigo.

## Estrutura do modelo

O modelo é dirigido pelo estoque: a frota de cada ano é definida pela taxa de motorização, e as vendas são o que
falta para atingi-la depois do sucateamento.

1. **Motorização e renda** (`motorizacao.py`). Veículos leves por mil habitantes com 18 anos ou mais, em função do
   PIB per capita, entre dois limites: Gompertz com ajuste parcial (Dargay, Gately e Sommer, 2007), calibrada em
   2000–2025 (limite superior), e elasticidade de 2015–2025, de 0,08 (limite inferior). PIB per capita real cresce
   1,0%, 1,5% ou 2,0% ao ano, o que resulta em seis cenários de frota.
2. **Sucateamento** (`calibrar_por_safra.py`, `rodar_v3_recalibrado.py`). Curva de sobrevivência por ano de venda,
   calibrada nas vendas da Anfavea desde 1957 e na estrutura etária da frota do Sindipeças.
3. **Vendas** (`projecao_2050.py`). Vendas = frota-alvo − sobreviventes das safras anteriores.
4. **Eletrificação** (`modelo_frota_etanol_v3.py`, `rodar_v3_sem_diesel.py`). Três trajetórias logísticas
   declaradas (rápida, central e lenta), ancoradas na participação observada dos elétricos em julho de 2026, com
   híbridos plugáveis e híbridos-flex modelados explicitamente. Comerciais leves a diesel ficam fora da demanda.
5. **Consumo de etanol**. Intensidade por quilômetro: flex 1,0; híbrido-flex 0,5; plugável 0,3; elétrico 0. Base de
   2025 de 34,4 bilhões de litros, mistura E32.
6. **Motocicletas** (`motos_calibrar.py`, `motos_projecao.py`). Mesmo método, sem eletrificação.
7. **Balanço** (`balanco_2050.py`). Oferta de cana estável em 27,3 bilhões de litros e milho de 10 para 20 bilhões
   até 2032; demais usos de 3,0 para 4,5 bilhões; sensibilidades a mix, milho, E35 e exportação.

`modelo_frota_etanol_v3.py` é usado como biblioteca (trajetórias, intensidades e funções de frota). Seu bloco
principal, se executado diretamente, reproduz uma versão anterior do modelo, com frota exógena, e não é usado
no artigo.

## Correspondência com o artigo

| Artigo | Script | Arquivo de resultado |
|---|---|---|
| Figura 1 – Motorização de leves e renda | `motorizacao.py` | `resultados/historico_2000_2025.csv` |
| Figura 2 – Motorização de motocicletas | `motos_calibrar.py`, `motos_projecao.py` | `resultados/motos_2050.csv` |
| Figura 3 – Frota por segmento, 2010–2050 | `frota_segmentos.py` | `resultados/frota_segmentos_2010_2050.csv` |
| Tabela 2, Figuras 4 e 5 – Frota, motorização e vendas de leves | `projecao_2050.py` | `resultados/projecao_2050.csv` |
| Nota da Tabela 2 – Teste com a projeção da Anfavea para 2026 | `teste_2026.py` | (saída no terminal) |
| Estimativa central de frota e vendas (PIB 1,5% a.a., média dos limites) | `cenario_central.py` | `resultados/cenario_central.csv` |
| Tabela 3 – Motocicletas | `motos_projecao.py` | `resultados/motos_2050.csv` |
| Figura 6 – Trajetórias de eletrificação | `modelo_frota_etanol_v3.py` (`TRAJETORIAS`) | — |
| Mix de vendas e participação dos BEV na frota, por trajetória | `eletrificacao_series.py` | `resultados/eletrificacao_mix_vendas.csv`, `resultados/eletrificacao_frota_bev.csv` |
| Tabela 4 – Etanol por segmento | `etanol_por_segmento.py` | `resultados/etanol_segmentos_2050.csv` |
| Figura 7 – Índice de demanda | `motos_projecao.py` | `resultados/etanol_leves_motos_2050.csv` |
| Seção 2.4 – Efeito do híbrido-flex | `balanco_2050.py` | (saída no terminal) |
| Tabela 5, Figura 8 – Balanço | `balanco_2050.py` | `resultados/balanco_2050.csv` |
| Tabela 6 – Sensibilidades | `balanco_2050.py` | (saída no terminal) |
| Figura 9 – Hierarquia de valor da sacarose | — | `dados/figura9_hierarquia_valor.csv` |

## Dados

| Arquivo | Conteúdo | Fonte |
|---|---|---|
| `anfavea_autos_cl_1957_2025.csv` | Emplacamentos anuais de automóveis e comerciais leves | Anfavea |
| `anfavea_leves_combustivel.csv` | Emplacamentos de leves por combustível, 2017–2025 | Anfavea |
| `frota_sindipecas_2010_2025.csv` | Frota circulante e idade média por segmento | Abipeças/Sindipeças, Relatório da Frota Circulante (ed. 2023 e 2026) |
| `motos_vendas_abraciclo.csv` | Vendas anuais de motocicletas desde 1975 | Abraciclo (anos iniciais estimados a partir da produção, conforme coluna `fonte`) |
| `pop18_ibge_2024.csv` | População com 18 anos ou mais, projeção 2000–2070 | IBGE, Projeções da População (2024) |
| `pib_per_capita_ibge.csv` | Variação real anual do PIB per capita, 2000–2025 | IBGE |
| `figura9_hierarquia_valor.csv` | Faixas indicativas de valor por tonelada de sacarose, 2024–2026 | Elaboração dos autores (valores aproximados) |

`resultados/historico_2000_2025.csv` é derivado dos dados acima; antes de 2010, a frota é reconstruída a partir
das vendas e da curva de sucateamento.

## Licença

Código sob licença MIT (ver `LICENSE`). Resultados e dados derivados sob CC BY 4.0. As séries originais pertencem às
respectivas fontes, citadas acima.

## Como citar

Cesar, A.; Honda, A.; Otoboni, C.; Carvalho, M. C. B.; Polikarpov, I.; Weise, F.; Fischer, H. *Do excedente à
produção de moléculas*. FATEC Shunji Nishimura, 2026. Código e dados: https://github.com/franklinweise/etanol-frota-2050
