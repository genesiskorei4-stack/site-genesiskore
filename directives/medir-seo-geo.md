# Medir o SEO e o GEO da GenesisKore

Criada em 30/10/2026, junto com o primeiro diagnóstico de SEO e GEO (síntese na wiki do AI OS:
`sinteses/2026-10-30-seo-e-geo-da-genesiskore.md`). Serve para repetir a mesma medição todo mês e
comparar com o ponto de partida. **Rodar no primeiro dia útil de cada mês**, e também duas e quatro
semanas depois de qualquer mudança grande no site.

## Por que medir assim

Não temos Search Console nem ferramenta paga de palavra-chave ligada a esta sessão. O que dá para
medir sem gastar nada, e que mostra se a empresa está sendo achada:

1. **Indexação**: quantas páginas o Google e o Bing têm. O Bing alimenta o ChatGPT e o Copilot, o
   Brave alimenta o Claude, o Google alimenta o Gemini, a Visão Geral e o Modo IA.
2. **Resposta das IAs**: as mesmas 21 perguntas de comprador feitas ao Modo IA do Google e ao Copilot,
   lidas pela página pública de cada um.
3. **Nota técnica do site**: `execution/auditar_seo_geo.py`, que não depende de rede.
4. **Visitas por origem**: tabela `visitas_site` da plataforma (Supabase `AI-OS`), campo `referencia` e
   `origem` (a origem `ia` marca quem veio do ChatGPT, Perplexity, Claude, Gemini ou Copilot).

## Ferramentas

| Medida | Como | Custo |
|---|---|---|
| Indexação no Google | `firecrawl_scrape` em `https://www.google.com/search?q=site%3Agenesiskore.com&hl=pt-BR&gl=br`, `location` BR | 1 crédito Firecrawl |
| Indexação no Bing | `firecrawl_scrape` em `https://www.bing.com/search?q=site%3Agenesiskore.com&setlang=pt-BR&cc=BR` | 1 crédito |
| Marca no Google | `firecrawl_scrape` em `https://www.google.com/search?q=GenesisKore&hl=pt-BR&gl=br` | 1 crédito |
| Modo IA do Google | `firecrawl_scrape` em `https://www.google.com/search?q=<pergunta>&udm=50&hl=pt-BR&gl=br`, `waitFor` 8000 | 1 crédito por pergunta |
| Copilot | `firecrawl_scrape` em `https://www.bing.com/copilotsearch?q=<pergunta>&setlang=pt-BR&cc=BR`, `waitFor` 10000 | 1 crédito por pergunta |
| Nota do site | `python3 execution/auditar_seo_geo.py --json` | Nada |
| Visitas | SQL na tabela `visitas_site`, agrupando por `referencia` e `origem` | Nada |

As perguntas ficam em `directives/perguntas-de-comprador.json`. **Não mude as perguntas** sem guardar
a lista antiga: comparação só vale com a mesma pergunta.

**O que não funcionou em 30/10/2026:** o Perplexity pede cadastro para responder, e o ChatGPT
(`chatgpt.com/?q=`) estoura o tempo do Firecrawl. O proxy da sessão na nuvem recusa
`genesiskore.com`, o Google e o Bing pelo terminal; tudo passa pelo Firecrawl. Para testar o site no
ar com cabeçalho (Markdown, 404), use a máquina de teste da Vercel, como em `migrar-para-vercel.md`.

## Como registrar

Para cada pergunta, anote: se a IA nomeou empresas, quais, de que tipo eram as fontes (ficha local
do Google ou do Bing, página do fornecedor com setor e cidade no título, lista de "melhores", diretório,
blog, vídeo, rede social) e se a GenesisKore apareceu. Some no fim:

| Indicador | 30/10/2026 (antes) |
|---|---|
| Páginas no Google (`site:`) | 4 |
| Páginas no Bing (`site:`) | 0 |
| Site na primeira página do Google para "GenesisKore" | Não (o Google sugere "Genesis Korea") |
| Perguntas de comprador em que o Modo IA citou a GenesisKore | ver a síntese |
| Perguntas de comprador em que o Copilot citou a GenesisKore | ver a síntese |
| Nota técnica do site | 56,6 de 100 |
| Sessões vindas do Google, de 21 a 30/10/2026 | 7 de 35 |
| Sessões vindas de IA, de 21 a 30/10/2026 | 0 |

Guarde o resultado de cada mês numa linha nova desta tabela e o detalhe na wiki.

## O teste de geração (para mudança de texto, antes de publicar)

Mudança de texto leva semanas para aparecer nas IAs, porque depende de o robô voltar e reindexar.
Para saber antes se o texto novo é mais citável, simule a etapa final da IA:

1. Para cada pergunta, junte as fontes que o Modo IA e o Copilot citaram de verdade (o conteúdo da
   página, raspado com `firecrawl_scrape`).
2. Some a página da GenesisKore que responderia a pergunta: a versão de antes e a de depois.
   **Troque o nome GenesisKore por um nome inventado nas duas** (por exemplo "Kestrel Sistemas"),
   para o modelo que julga não puxar o que sabe dos arquivos do projeto.
3. Peça a um modelo, sem acesso à internet, que responda à pergunta usando só as fontes, citando
   cada uma pelo número, como faria um buscador com IA. Embaralhe a ordem das fontes.
4. Conte em quantas respostas a empresa foi recomendada, em que posição e se os fatos dela (prazo,
   preço fechado, para quem é) foram levados para a resposta.
5. Rode com pelo menos dois modelos diferentes e compare antes com depois.

O resultado de 30/10/2026 está na síntese da wiki.

## O que aprendi e não está escrito em outro lugar

- **O Modo IA do Google e o Copilot puxam a ficha local** (Perfil da Empresa no Google, Bing Places)
  para perguntas do tipo "quem faz X em São Paulo". Nas duas primeiras leituras de 30/10/2026, duas
  das quatro empresas do Modo IA e as duas do Copilot vieram de ficha com endereço e telefone.
- **A busca pela marca no Bing devolve lixo** (pornografia e AliExpress em 30/10/2026), porque o Bing
  não conhece nenhuma página do site. Isso some quando o site entra no índice.
- **O Google corrige "GenesisKore" para "Genesis Korea"** enquanto a marca não tem sinal suficiente.
  Nome escrito sempre igual, em todo lugar, com o K, é o que resolve.
