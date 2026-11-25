# Páginas de setor e a pergunta da entrada

Criada em 24/11/2026, para o lançamento de 05/01/2027. O plano completo está no AI OS, em
`Obsidian/GenesisKore/wiki/sinteses/2026-11-24-lancamento-da-marca-em-05-01-2027.md`.

## O objetivo

Quem abre a página inicial responde "Qual é o setor da sua empresa?" e cai, sem tela de carregamento,
numa página feita para o setor dele. São nove páginas no mesmo molde, cada uma com o desenho da
operação daquele setor.

## O que já existe

| Peça | Onde | Estado |
|---|---|---|
| Desenhos dos nove setores | `execution/plantas_de_setor.py` (usa `execution/plantas_base.py`), grava em `plantas/` | Pronto em 24/11/2026 |
| Chapéu, frase e legenda de cada setor | `plantas/setores.json`, gerado pelo mesmo script | Pronto |
| Gerador das páginas | `execution/gerar_paginas_de_setor.py`, com `--conferir` | Pronto em 25/11/2026 |
| Texto de cada setor (dores, módulos, o que não comprar, perguntas) | `<pasta do setor>/index.md` | Rascunho em 25/11/2026, marcado `rascunho: aguardando aprovação dos sócios` |
| A pergunta e a primeira tela nova da página inicial | `index.html`, `styles.css`, `script.js` | Pronto em 25/11/2026 |

## Regras que não mudam

- O lema "Construído para você / Rodando sem você" é o texto grande das nove páginas e nunca quebra de
  linha no meio. O `h1` de cada página é a frase do setor, para as nove não disputarem a mesma busca.
- Nenhum texto sobre linha do desenho. No desenho vai só o número, e a legenda é texto da página.
- A pergunta aparece só na página inicial. Tem "Pular, quero ver tudo" e o X. Cada opção é um link de
  verdade, e não um botão com script.
- As três páginas que já existiam guardam o endereço: `/sistema-para-distribuidora/`,
  `/automacao-para-escritorio/` e `/sistemas-sob-medida/`.
- Caso de cliente só com contrato fechado. Número só com fonte.
- Nenhum travessão em texto que o visitante lê.

## Como o gerador funciona

`python3 execution/gerar_paginas_de_setor.py` lê `plantas/setores.json` (chapéu, frase e legenda), os desenhos
e o `index.md` de cada setor (`gerar: setor` e `setor: <chave>` no cabeçalho), e grava:

- o `index.html` das nove páginas, com o desenho dentro do HTML, o JSON-LD (WebPage, Service, trilha e
  FAQPage igual ao texto da tela) e o Markdown publicado para os agentes;
- o `sitemap.xml`, a seção "## Uma página por setor" do `llms.txt`;
- na página inicial, só o que está entre os marcadores `gerado:boas-vindas` e `gerado:pergunta`.

Ele para com o motivo se o `# ` do texto não for a frase do `setores.json`, se faltar "Onde dói",
"O que construímos" (seis itens), "O que você não precisa comprar" ou "Perguntas", se o botão final não levar
`/conversar/?setor=<chave>`, ou se houver traço. Página com `rascunho:` no cabeçalho gera um aviso: tirar a
linha é o sinal de que os sócios aprovaram. Endereço novo de setor precisa entrar também nas três listas do
`vercel.json`.

## Como mexer num desenho

1. Editar a cena em `execution/plantas_de_setor.py`.
2. Rodar `python3 execution/plantas_de_setor.py`.
3. Olhar o resultado no celular e no computador antes de enviar.

## Antes de publicar

`python3 execution/gerar_paginas.py --conferir`, `python3 execution/testar_vercel_json.py`,
`python3 execution/auditar_seo_geo.py` e `python3 execution/verificar_agentes.py`, mais a foto de cada
página no celular. O trabalho fica no ramo de lançamento e só entra na `main` em 05/01/2027.
