# Interface 1.1

A interface foi reorganizada como portal editorial de pesquisa, mantendo Streamlit.
Não houve alteração de seeds, schemas, fórmulas, regras de validação ou fontes.
O diagnóstico inicial encontrou cards densos, avisos com aparência de erro e gráficos
sem uma sequência de leitura. A versão 1.1 introduz apresentação, evidências por tema,
interpretações curtas e transparência próxima dos números.

## Componentes

- `src/visualization/theme.py`: cores, famílias, rótulos de qualidade e rotas.
- `styles.py`: somente classes próprias `oh-*` e a classe pública de um container
  com `key="page_heading"`. Não usa seletores internos `data-testid` para estilizar.
- `layout.py`: marca editorial, títulos, seções, notas, gráficos contextualizados,
  caminhos temáticos e rodapé.
- `components.py`: cards com proveniência, formatação brasileira e tabelas com CSV integral.
  O acesso ao snapshot continua com cache e consultas somente leitura.
- `charts.py`: visualizações Plotly interativas e estilo compartilhado.

O cabeçalho e a navegação são comuns às seis páginas. `app.py` usa somente
`st.navigation` e `st.Page`; não há navegação paralela por sidebar.
A página inicial passou a `pages/0_visao_geral.py`.
Em telas estreitas, a navegação nativa apresenta seu controle de abertura.

## Identidade

Fundo #F3F0E9, superfícies brancas, texto #171717, secundário #626262,
destaques #8B342F e #47635C e bordas #DDD8D0.
Source Serif 4 serve aos títulos editoriais; Inter serve à interface e aos valores.
As duas famílias são distribuídas localmente em `static/fonts/`, com licenças OFL
e proveniência/SHA-256. A aplicação não consulta serviços de fontes em execução.

Fontes consultadas:
[Inter](https://rsms.me/inter/),
[Source Serif](https://github.com/adobe-fonts/source-serif),
[fontes locais no Streamlit](https://docs.streamlit.io/develop/api-reference/configuration/config.toml).

A escala de títulos usa rem/clamp; cards usam três colunas em desktop, duas abaixo
de 1000 px e uma abaixo de 600 px. As alturas são iguais por linha, com altura
automática no celular para respeitar o conteúdo. Valores não dependem de cores para
serem compreendidos. Anos são apresentados como 2025, sem separador de milhar.

## Leitura estatística

Cada card conserva unidade, ano, fonte, situação do indicador e situação da fonte.
Não há índice combinado de acessibilidade. Notas informativas não usam aparência de erro.
Os gráficos têm fontes, períodos, interpretação textual, unidades e hover em português.
Faixas salariais permanecem acumuladas, apresentadas como pontos com referência em 0–100%;
não viram categorias exclusivas ou barras empilhadas.

O histograma usa classes regulares de R$ 500, limites inferiores inclusivos e superiores
exclusivos. A linha tracejada representa a mediana da seleção. O gráfico de faixas mantém
os cortes originais de 1500/2500/3500, explicitando seus limites e a amplitude desigual.
Valores censitários desconhecidos não são desenhados como zero.
O catálogo de política urbana usa agrupamentos editoriais; não acrescenta descrição jurídica.

Tabelas apresentam nomes legíveis e formatação brasileira. O download conserva colunas,
valores e nomes originais, incluindo as colunas não mostradas na visualização resumida.
Células vazias no CSV continuam significando ausência de informação.

## Verificações realizadas em 20/11/2026

Ambiente: Python 3.12.16, Streamlit 1.67.0 e Chrome headless local.

- 49 testes do MVP executados antes das alterações.
- 67 testes após o redesign, incluindo indicadores, banco, interface, exportação pública,
  formatação, preservação de qualidade, escape de HTML e contraste dos tokens de texto.
- Ruff: lint e formatação.
- Seis rotas abertas no navegador em 1440, 1024, 768, 390 e 320 px: 30 combinações.
- Capturas da apresentação e dos gráficos em desktop/celular.
- Ausência de exceções Streamlit e de erros JavaScript, sem overflow horizontal
  da página, dos cards ou dos containers dos gráficos nas larguras verificadas.
- Comparação final das nove tabelas com o registro anterior ao redesign e hashes dos
  22 arquivos preservados da camada de dados.
- Download CSV/JSON, filtros e navegação possuem verificações de interface/dados;
  o script de navegador verifica as rotas e a geometria das páginas.

O teste geométrico não certifica sozinho toda a acessibilidade.
Revisão com leitor de tela (NVDA/VoiceOver), dispositivos físicos, Safari/iOS e uma
auditoria integral de teclado/WCAG continuam recomendadas. A referência é
[WCAG 2.2](https://www.w3.org/WAI/WCAG22/quickref/), sem alegação de certificação AA.

## Reproduzir a verificação visual

Dependência opcional de desenvolvimento, fora dos requisitos da aplicação:

```bash
python -m pip install playwright==1.65.2
python -m playwright install chromium
streamlit run app.py
```

Em outro terminal com o mesmo ambiente ativado:

```bash
python scripts/check_visual_layout.py
```

Para um Chrome local no Windows:

```powershell
python scripts/check_visual_layout.py --browser-executable "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

O script grava capturas e `report.json` em `artifacts/visual/`, ignorada pelo Git.
Também aceita `--base-url` e `--output`.

Se aparecer importação antiga após atualização de vários arquivos, reinicie o Streamlit
(Ctrl+C no terminal, seguido de `streamlit run app.py`) e atualize a aba.
O projeto usa `server.fileWatcherType="poll"`, para maior previsibilidade nesse ambiente
Windows. Mudanças de configuração de servidor exigem reinicialização.
