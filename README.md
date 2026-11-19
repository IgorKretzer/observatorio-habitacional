# Observatório Habitacional de Pato Branco

**Renda, moradia e desenvolvimento urbano**

Pesquisa independente baseada em dados públicos e metodologia documentada. Sem vínculo
institucional com Prefeitura, IBGE, IPARDES ou outros órgãos públicos.

MVP funcional em Python 3.12, Streamlit, DuckDB, Pandas, PyArrow/Parquet, Plotly e OpenPyXL,
com testes Pytest e lint/formatação Ruff. Inicia offline depois da instalação das dependências.

## Instalação e execução

Entre nesta pasta (`observatorio-habitacional`). É necessário Python 3.12+ instalado.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/initialize_database.py
streamlit run app.py
```

Se a política local impedir ativação, use o executável diretamente, sem mudar a política:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/initialize_database.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/initialize_database.py
streamlit run app.py
```

Abra http://localhost:8501. A barra lateral dá acesso à visão geral e às cinco páginas.
Na primeira execução o banco também é reconstruído automaticamente se estiver ausente
ou se a assinatura dos seeds mudou. Não é necessário acesso à internet para ler os dados locais.
Pare com Ctrl+C.

`requirements.txt` estabelece faixas compatíveis; `requirements-lock.txt` registra as
versões exatas usadas na validação deste MVP. Para reproduzi-las, substitua a instalação por
`python -m pip install -r requirements-lock.txt`.

Neste workspace de desenvolvimento foi preparado um Python 3.12 isolado em `../.runtime`
porque não havia Python no PATH. A `.venv` local depende desse runtime; ele não deve ser
versionado nem é necessário em outra máquina com Python instalado.

## Conteúdo

- `app.py`: visão geral, seis cards, quatro gráficos e exportação dos indicadores.
- `pages/`: renda e trabalho, mercado de aluguéis, estoque habitacional, política urbana,
  metodologia e fontes.
- `src/config.py`, `schemas.py`, `database.py`: caminhos, schemas e acesso analítico.
- `src/ingestion/`: leitura de CSV padronizado e Excel de salários; ausência não vira zero.
- `src/indicators/`: salários, faixas acumuladas, estoque, estatísticas de anúncios e simulação.
- `src/validation/`: chaves, domínios, fontes, anos, contagens, coerência e duplicados.
- `src/visualization/`: gráficos e componentes nativos; sem seletores CSS internos.
- `data/seeds/`: nove CSVs versionados, incluindo solicitações inicialmente vazias.
- `data/raw/`: reservado aos documentos originais públicos; pipeline nunca escreve aqui.
- `data/processed/`: DuckDB, nove Parquets e relatório JSON reconstruíveis; fora do Git.
- `data/metadata/`: proveniência e modelo CSV de anúncios.
- `scripts/`: inicialização e validação independente.
- `tests/`: testes de dados, cálculos, persistência e interface Streamlit.

## Modelo e processamento

As nove tabelas são `sources`, `indicators`, `formal_wages`, `wage_distribution`,
`housing_stock`, `occupancy_status`, `rental_listings`, `urban_policy_documents` e
`information_requests`. Campos desconhecidos ficam NULL; não há ORM.

`python scripts/initialize_database.py`:

1. Lê todos os seeds, exige o schema e valida tipos, chaves, contagens e valores.
2. Confere integridade de fontes, correspondência de anos, ordem de faixas acumuladas
   e fechamento aritmético do estoque informado.
3. Calcula um catálogo rastreável de indicadores, sem preencher mediana salarial inexistente.
4. Monta um banco temporário em transação e substitui o snapshot somente após sucesso.
5. Gera Parquets via PyArrow e um relatório `data/processed/observatorio.report.json`.

Executar novamente não acrescenta cópias. O snapshot é reconstruído **a partir dos seeds**;
alterações manuais no banco não são um método de atualização. Execute reprocessamentos
administrativos com a aplicação parada para evitar bloqueios de arquivo no Windows.
Os Parquets e o relatório são artefatos reconstruíveis; o DuckDB é o snapshot usado pela interface.

Views `rental_costs`, `export_*` e `indicator_catalog` permitem consultas SQL.
A API `query(sql, parameters)` abre conexão somente leitura e aceita parâmetros.
A interface usa `st.cache_data` para consultas e `st.cache_resource` para preparar o snapshot;
não compartilha uma conexão DuckDB mutável entre sessões.
Arquivos grandes devem ser transformados em scripts externos; não carregar microdados da
PNAD na interface.

Os CSVs exportados preservam os campos da base, fonte, período, município e status sempre
disponíveis. O catálogo acrescenta unidade, metodologia, limitações e status da fonte original.
Células vazias nos CSVs representam informação desconhecida, não zero.

## Dados iniciais e ressalva aritmética

Os valores originais da especificação foram preservados integralmente.
Os **13 aluguéis somam R$ 33.440,00**, com **média R$ 2.572,31** e **mediana R$ 2.300,00**.
A média esperada de R$ 2.587,69 na solicitação não corresponde à lista fornecida;
não se alteraram os anúncios para forçar esse resultado. Os testes verificam a conta correta.

Há 37.323 vínculos formais em 2025; remuneração média nominal de R$ 4.075,06.
Os subtotais nas três categorias de domicílios são 22.290 próprios, 10.656 alugados e
1.184 cedidos, sem afirmar que sejam totais municipais definitivos.

As fontes numéricas permanecem `pending_source_verification`. Os anúncios têm ainda
`validation_status=exploratory`; IDs `seed-001` etc. são internos. Não foram inventados
bairros, tipos, URLs, nome da imobiliária, protocolos ou datas de coleta. Ano desconhecido
continua nulo, inclusive no catálogo de indicadores.

Os nove documentos legislativos foram identificados no
[índice municipal](https://patobranco.pr.gov.br/legislacao-planejamento-urbano/) em
19/11/2026. Isso não constitui análise jurídica de artigos, vigência ou efeitos.
A tabela [SIDRA 9928](https://sidra.ibge.gov.br/tabela/9928) é referência declarada da
pesquisa; a consulta automatizada retornou 403 e não validou seus valores.
Veja `data/metadata/provenance.md`.

## Testes e qualidade

Com o ambiente ativado:

```bash
pytest
ruff check .
ruff format --check .
python scripts/validate_data.py
```

Ou no Windows sem ativação, prefixe com `.\.venv\Scripts\python.exe -m` para pytest e Ruff.

Os testes cobrem os subtotais, média/mediana dos anúncios, percentuais acumulados,
variação nominal anual, ausência de divisão por zero, nulos, preservação de anos e fontes,
não duplicação, rejeição de dados negativos e inconsistentes, Parquet, coerência dos cards,
filtros e renderização das seis telas com `streamlit.testing.v1.AppTest`.
A validação independente usa um banco temporário sem alterar o banco da aplicação.

## Atualização dos dados

1. Guarde documentos originais públicos em `data/raw/`, sem editar os arquivos originais.
2. Documente instituição, URL específica, ano, metodologia e data real de acesso em
   `sources.csv`. Só marque `verified` após conferir documento e valores.
3. Atualize os CSVs padronizados de seed, mantendo chaves técnicas estáveis e fontes válidas.
   Campos vazios são desconhecidos. Datas usam YYYY-MM-DD; números usam ponto decimal.
4. Execute validação, testes e inicialização. Revise o relatório e as telas.
5. Versione código, seeds e metadados com Git; não versione banco, ambiente nem credenciais.

Para anúncios use `data/metadata/rental_listings_template.csv`. A página de aluguéis aceita
upload para validar e visualizar **sem persistir** dados na aplicação pública.
Para incorporar de fato, cadastre a fonte e substitua/mescle o seed local com revisão das chaves.
`src.ingestion.listings.read_listings` valida o CSV; leia antes de unir dados.
A leitura de Excel disponível é de um layout padronizado de salários, não um extrator universal
dos arquivos originais da RAIS.

URLs repetidas são apenas possíveis duplicados; o sistema não os remove. Sem URL,
não tenta identificar o imóvel a partir do preço. A imobiliária inicial é desconhecida:
filtros de imobiliária, tipo, bairro e período ficam desabilitados/ocultos até haver informação.
Filtros por período excluem registros sem data e mostram essa ressalva.
Nenhuma requisição à Prefeitura ou ao IBGE aparece sem data de envio confirmada.

## Limitações metodológicas

- Vínculos da RAIS não são pessoas distintas, renda familiar ou todos os trabalhadores.
- Salários são nominais; não há mediana exata nem correção inflacionária.
- Faixas até 2 e até 3 salários mínimos são acumuladas, não somáveis.
- Anúncios são preços pedidos, não aluguéis efetivamente pagos. A amostra de uma imobiliária
  não é representativa e não estima o preço médio municipal.
- Custo total exige aluguel, condomínio e IPTU conhecidos. Não imputar zero a ausências.
- Subtotais censitários abrangem categorias selecionadas. Traços não são zero.
- O fechamento 34.318 + 3.053 + 1.484 = 38.855 não valida a equivalência conceitual entre
  o diagnóstico municipal e o Censo. Vacância não equivale a oferta para locação.
- Não se calcula déficit a partir de imóveis vagos menos alugados. Déficit e inadequação
  aguardam dados e metodologia específica.
- Não se assume representatividade municipal da PNAD Contínua. Renda domiciliar,
  CadÚnico, registros administrativos e Fundação João Pinheiro são integrações futuras.
- Não há indicador oficial que cruze RAIS e anúncios de outro período.
  A função de simulação em `affordability.py` preserva fontes/anos e avisos;
  não é apresentada como estimativa populacional no painel.
- `derived` não significa `verified`: o catálogo preserva `upstream_status`,
  origem, ano e limitações de cada valor.

## Publicação no Streamlit Community Cloud

Projeto preparado, sem publicação automática nem conta paga necessária.
Versione **esta pasta como raiz do repositório**, incluindo `.streamlit/config.toml`,
seeds, código, requisitos e metadados. No Community Cloud selecione repositório/branch,
arquivo `app.py` e Python 3.12 nas configurações avançadas.
Consulte as [instruções oficiais de publicação](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).

O banco é reconstruído dos CSVs versionados no primeiro uso; o sistema de arquivos pode
ser efêmero. A aplicação não depende de gravações persistentes feitas por visitantes.
Não adicionar autenticação, credenciais, dados pessoais ou arquivos restritos.
Não é necessário Docker, serviço de banco externo ou infraestrutura adicional.
Para ambientes com diretório de aplicação sem escrita, prepare os artefatos no processo
de implantação ou adapte o caminho de processamento para um diretório temporário gravável.

## Próximas funcionalidades

Conferência documental e anexos; novas rodadas de anúncios com datas verificáveis;
preços corrigidos pela inflação; deduplicação revisada; intervalos de incerteza;
renda domiciliar e desenho amostral; dados municipais e metodologia de déficit/inadequação.
São etapas futuras, sem resultados presumidos neste MVP.
