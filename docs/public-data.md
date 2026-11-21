# Contrato público de dados — versão 1.0

A versão 1.1 prepara uma futura interface Next.js/Vercel através de arquivos estáticos.
Não implementa Next.js, API ou serviço adicional.

## Geração

Depois de preparar e validar o snapshot:

```bash
python scripts/initialize_database.py
python scripts/export_public_data.py
```

O exportador abre o DuckDB somente para leitura. Não reconstrói nem modifica o banco.
Se o banco não existir, informa a necessidade de inicialização.
Aceita `--database caminho.duckdb` e `--output diretório`.
Pode ser executado na etapa de build; o frontend futuro recebe apenas os arquivos estáticos
e não precisa acessar DuckDB ou ter um banco gravável.

Saídas versionáveis em `public/data/`:

| Arquivo | Conteúdo |
| --- | --- |
| indicators.json | Lista ordenada por indicator_id, com indicadores e proveniência |
| sources.json | Lista ordenada por source_id, com fontes declaradas |
| manifest.json | Versões, município, contagens, categorias de qualidade e hashes SHA-256 |

As duas listas têm chaves em ordem estável. Não há timestamp de execução.
Reexportar o mesmo snapshot produz os mesmos bytes. JSON usa UTF-8, números JSON e
`null` para valores desconhecidos; nunca NaN/Infinity.

## Indicadores

Campos de cada registro:

`indicator_id`, `indicator_name`, `category`, `municipality_code`,
`reference_year`, `value`, `unit`, `source_id`, `methodology`,
`quality_status`, `limitations`, `upstream_status`, `source_name`,
`source_url` e `source_notes`.

O ano é inteiro ou null. Valor é número ou null. Os identificadores e códigos de município
são strings. Textos desconhecidos também podem ser null.
`source_id` referencia um registro de `sources.json`.
As cinco categorias de qualidade são verified, pending_source_verification, exploratory,
derived e unavailable. O exportador rejeita classificações desconhecidas.

Uma interface futura deve mostrar `quality_status` **e** `upstream_status`, ano,
unidade, fonte e ressalvas. `derived` não implica `verified`.
Os anúncios são exploratórios conforme a metodologia e as limitações preservadas.
Coleta desconhecida continua com ano null; não usar o ano de exportação como referência.
Valor null não deve ser substituído por zero.

## Fontes

Campos: `source_id`, `institution`, `dataset_name`, `source_url`,
`reference_year`, `retrieved_at`, `methodology_url`, `notes` e `status`.
Datas conhecidas usam YYYY-MM-DD. Data desconhecida é null.

O manifesto contém os hashes dos bytes de indicators.json e sources.json e notas metodológicas.
Não inclui credenciais, configuração do GitHub, protocolos presumidos, nomes de proprietários,
inquilinos ou registros individuais de anúncios.

## Consumo futuro

Em um futuro projeto Next.js, os arquivos poderão ser copiados para `public/data/`
e lidos em build ou com fetch. Essa etapa não faz parte da versão 1.1.
Não há dependência de uma base mutável em execução ou de serviço pago.

Na hospedagem Streamlit com diretório somente leitura, gere banco e relatório no build,
preservando os seeds correspondentes. Com o snapshot e assinatura preparados, a aplicação
consulta o banco somente para leitura. Se os seeds mudarem, prepare novamente os artefatos
antes de publicar.

A página Metodologia e Fontes oferece download dos JSONs preparados.
Atualize os arquivos estáticos quando o snapshot de dados mudar.
