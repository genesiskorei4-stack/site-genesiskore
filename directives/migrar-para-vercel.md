# Migrar genesiskore.com do GitHub Pages para a Vercel

Preparado em 28/10/2026. **Feito no mesmo dia**, a pedido do Felipe ("pode transferir para lá"). O site está na Vercel desde 28/10/2026.

## O que foi feito, e o que se aprendeu (28/10/2026)

| Item | Valor |
|---|---|
| Projeto | `site-genesiskore` (`prj_XCM18T4CXbexHIxFIj86LUm7ynlr`), equipe `genesis-kore`, sem framework, sem build, Output `.` |
| Primeiro deploy | `main` no commit `d93108f`, pronto em 2 segundos. Custou 1 vaga do balde (22 de 100 ocupadas antes) |
| Domínios | `genesiskore.com` e `www.genesiskore.com`, o `www` com 308 para o apex. Os dois entraram já verificados, porque a equipe já tinha o `app.genesiskore.com` |
| DNS novo | apex `A` `216.198.79.1` e `64.29.17.1`; `www` `CNAME` `67732ecfa8772377.vercel-dns-017.com`. TTL 300 nos três, para a volta ser rápida |
| Certificado | Saiu cerca de 80 segundos depois da troca do DNS |
| Teste | `testar_vercel_json.py` deu 21 de 21 no `.vercel.app` e depois no `genesiskore.com`. `CLAUDE.md`, `execution` e `directives` dão 404. O n8n e o `app.genesiskore.com/api/visita` aceitam a origem `https://genesiskore.com` (preflight 204) |
| Email | `MX`, SPF, DKIM, DMARC e as verificações do Google e do TikTok conferidos com `dig` depois da troca, iguais aos de antes |

**Três coisas que não estavam aqui e fazem diferença:**

1. **O conector da Vercel precisa de acesso à equipe.** A primeira chamada de criar projeto deu `403 You must re-authenticate to this scope`. Sai com `authorize_team_access` (teamId `team_pN1yARrPYaToprbLv9lAIhr3`): ele gera um link que vale 10 minutos, um sócio abre e aprova, e a chamada passa.
2. **A Vercel não recomenda mais o `76.76.21.21`.** O `get_domain_config` deu como primeira opção dois IPs (`216.198.79.1` e `64.29.17.1`) e um `CNAME` próprio do projeto. O `76.76.21.21` virou segunda opção. Use o que o `get_domain_config` devolver na hora.
3. **A sessão do Claude na nuvem não alcança o site.** O proxy dela recusa `genesiskore.com` e `*.vercel.app`. O teste rodou numa máquina de teste da Vercel (`create_sandboxes_v4` com o repositório clonado, e `run_session_command`). Chamada com espera longa estoura os 60 segundos do conector: dispare e leia o resultado com `get_session_command_logs`.

## Por que trocar

O relatório do Is Agentic de 28/10/2026 deu 81/100 ao site. Dois itens essenciais dependem de a resposta mudar pelo cabeçalho `Accept`, e o GitHub Pages não faz isso:

1. `Accept: text/markdown` na raiz tem de devolver Markdown, com `Content-Type: text/markdown` e `Vary: Accept`. Quem pede HTML continua recebendo o HTML.
2. Um endereço que não existe, pedido com `Accept: text/markdown`, tem de devolver 404 com corpo em Markdown que aponte para o `llms.txt` ou o sitemap.

O repositório já tem tudo pronto para isso: `vercel.json`, `404.md`, `.vercelignore` e o teste `execution/testar_vercel_json.py`.

## Como as regras funcionam, e a pegadinha que obrigou a usar `routes`

A documentação da Vercel diz, sobre `rewrites`: "The source property should not target a file due to filesystem precedence". O `rewrites` só roda **depois** de procurar o arquivo, e `/` sempre acha o `index.html`. Uma regra de `rewrites` para a raiz nunca dispararia.

Por isso o `vercel.json` usa `routes`, que roda **antes** do sistema de arquivos até a linha `{ "handle": "filesystem" }`, e depois dela só quando o arquivo não existe:

| Ordem | Regra | O que faz |
|---|---|---|
| 1 | `/consultoria`, `/sobre` etc. sem barra | 308 para a versão com barra. O GitHub Pages fazia isso sozinho, e sem a barra os links relativos das páginas quebram (o `conversar.js`, por exemplo) |
| 2 | `/` | Põe `Vary: Accept` em toda resposta da raiz |
| 3 | `/` com `accept` contendo `text/markdown` | Serve o `index.md` com `Content-Type: text/markdown; charset=utf-8` |
| 4 | `*.md` e `llms.txt` | Fixa o `Content-Type` com `charset=utf-8` |
| 5 | `handle: filesystem` | Daqui para baixo, só quando o arquivo não existe |
| 6 | Qualquer caminho, com `text/markdown` | 404 com o corpo do `404.md` |
| 7 | Qualquer caminho | 404 com o `404.html` de sempre |

Detalhes que valem saber:

- `routes` não convive com `rewrites`, `redirects`, `headers`, `cleanUrls` nem `trailingSlash` no mesmo arquivo. Regra nova entra em `routes`.
- Pasta nova com página (`nova-pagina/index.html`) precisa entrar na lista da regra 1. O teste avisa se faltar.
- Um navegador nunca manda `text/markdown` no `Accept`, então quem visita não vê diferença.
- O `git.deploymentEnabled` com `claude/*` desligado é o mesmo do `ai-os`: push em ramo de trabalho do Claude não gera deploy.
- A Vercel diz que o `has` não funciona no `vercel dev`. O teste local é um imitador do roteamento (`execution/testar_vercel_json.py`), e por isso o passo 3 abaixo testa no deploy de verdade antes de mexer no DNS.

## O que isso custa

- **Cota de deploy.** O site passa a ser o oitavo projeto no balde de 100 deploys por dia da conta `genesis-kore`. Cada push na `main` do `site-genesiskore` custa 1 deploy. Push em ramo `claude/*` não custa nada. Hoje, no GitHub Pages, o site não gasta nada desse balde.
- **Sem função.** É tudo estático e regra de roteamento, sem função nem middleware. Não entra em cobrança de execução.
- **Plano gratuito.** A conta está no plano gratuito, que a Vercel descreve como uso pessoal e não comercial. Os outros sete projetos da casa já estão nessa situação. O site seria mais um. Decisão do Felipe.

## Antes de começar

1. Rode os dois testes locais e confira tudo `ok`:

   ```
   python3 execution/verificar_agentes.py
   python3 execution/testar_vercel_json.py
   ```

2. Anote o estado atual do DNS e guarde a saída (é o plano de volta):

   ```
   dig +short genesiskore.com A
   dig +short www.genesiskore.com CNAME
   dig +short genesiskore.com MX
   dig +short genesiskore.com TXT
   dig +short genesiskore.com CAA
   dig +short app.genesiskore.com CNAME
   ```

   E a lista inteira pelo conector da WordPress.com (`domains.dns_records`). O apex deve ter 4 registros `A` do GitHub Pages (os endereços que o GitHub publica são `185.199.108.153`, `185.199.109.153`, `185.199.110.153` e `185.199.111.153`; vale o que o `dig` mostrar) e o `www` um `CNAME` para `genesiskorei4-stack.github.io`.

3. Grave a resposta de hoje, para comparar depois:

   ```
   curl -sI https://genesiskore.com/ -H 'Accept: text/markdown' | grep -iE '^(HTTP|content-type|vary|server)'
   curl -s -o /dev/null -w '%{http_code} %{content_type}\n' -H 'Accept: text/markdown' https://genesiskore.com/esta-pagina-nao-existe-7f3a
   curl -s -o /dev/null -w '%{http_code} %{content_type}\n' -H 'Accept: text/html' https://genesiskore.com/
   ```

   No GitHub Pages a primeira volta `text/html` e `server: GitHub.com`, e a segunda `404 text/html`.

4. Confira o saldo do balde antes de criar o projeto (`list_deployments` das últimas 24 horas, sem filtro de projeto: o `pagination.count` é quanto está ocupado).

## A troca, passo a passo

### 1. Levar as mudanças para a `main` do site

O `vercel.json` e o resto precisam estar na `main`. O GitHub Pages ignora o `vercel.json` (está no `exclude` do `_config.yml`), então esse push não muda nada no ar.

### 2. Criar o projeto na Vercel

No time `genesis-kore`: Add New, Project, importar `genesiskorei4-stack/site-genesiskore`.

| Campo | Valor |
|---|---|
| Nome do projeto | `site-genesiskore` |
| Framework Preset | Other |
| Root Directory | a raiz do repositório (deixe em branco) |
| Build Command | nenhum (deixe desligado) |
| Output Directory | `.` |
| Install Command | nenhum |
| Production Branch | `main` |

Sem `package.json`, a Vercel publica os arquivos como estão. O `.vercelignore` tira do deploy o `CLAUDE.md`, o `AGENTS.md`, o `GEMINI.md`, a pasta `execution` e a pasta `directives`. O primeiro deploy gasta 1 vaga do balde.

### 3. Testar no endereço `.vercel.app`, antes de mexer no DNS

```
python3 execution/testar_vercel_json.py --url https://site-genesiskore.vercel.app
```

Tem de dar tudo `ok`. Se o endereço responder 401, é a proteção de deploy da Vercel: use o link de compartilhamento do painel ou desligue a proteção só desse projeto (o site é público de qualquer jeito).

Se a raiz em Markdown passar e só o 404 em Markdown falhar, vá para "Se o 404 em Markdown não funcionar", no fim. Não troque o DNS antes de resolver.

### 4. Pôr o domínio no projeto

Em Settings, Domains do `site-genesiskore`: adicione `genesiskore.com` e `www.genesiskore.com`, com o `www` redirecionando para o apex (o site sempre usou o apex como canônico). A Vercel mostra os valores exatos que o DNS precisa ter. Hoje a documentação dá como exemplo `A 76.76.21.21` para o apex e um `CNAME` em `cname.vercel-dns-0.com` (ou parecido) para o `www`. Use o que o painel mostrar, não o exemplo.

Se a Vercel pedir uma verificação por `TXT` em `_vercel.genesiskore.com`, isso é um registro **novo**, num nome que ainda não existe. Pode criar. Nunca edite nem apague um `TXT` que já existe.

### 5. Trocar o DNS na WordPress.com

Entre pela conta da WordPress.com, no domínio `genesiskore.com`, DNS. Mexa **só** nestes registros:

| Registro | De | Para |
|---|---|---|
| `A` do apex (os 4) | IPs do GitHub Pages | o `A` que a Vercel mostrou (normalmente um só; apague os 4 do GitHub e crie o da Vercel) |
| `CNAME` do `www` | `genesiskorei4-stack.github.io` | o alvo que a Vercel mostrou |

**Não toque em mais nada.** O e-mail do Google Workspace mora nesse DNS:

- `MX` em `smtp.google.com`: não mexa.
- Todos os `TXT` do apex (SPF, `google-site-verification`, `tiktok-developers-site-verification`): não mexa.
- `_dmarc`, `google._domainkey`, o `CNAME` `yco23fze2k4d`: não mexa.
- `app.genesiskore.com` (a plataforma, `CNAME` para `cname.vercel-dns.com`): não mexa.

Se houver registro `CAA` no apex, ele precisa permitir `letsencrypt.org`, que é quem emite o certificado da Vercel (e também era o do GitHub Pages).

### 6. Esperar o certificado e conferir

O DNS pode levar de minutos a algumas horas. Quando o painel da Vercel mostrar o domínio como válido e com certificado:

```
python3 execution/testar_vercel_json.py --url https://genesiskore.com
python3 execution/verificar_agentes.py --no-ar
curl -sI https://genesiskore.com/ -H 'Accept: text/markdown' | grep -iE '^(HTTP|content-type|vary|server)'
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' -H 'Accept: text/markdown' https://genesiskore.com/esta-pagina-nao-existe-7f3a
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' -H 'Accept: text/html' https://genesiskore.com/
curl -sI https://www.genesiskore.com/ | grep -iE '^(HTTP|location)'
```

Esperado: `200`, `text/markdown`, `Vary: Accept`, `server: Vercel` na primeira; `404 text/markdown` na segunda; `200 text/html` na terceira; o `www` redirecionando para `https://genesiskore.com/`.

E confira que o e-mail não foi tocado: `dig +short genesiskore.com MX` e `dig +short genesiskore.com TXT` iguais ao que você anotou antes. Mande um e-mail de teste para `contato@genesiskore.com`.

Abra no celular a página inicial, `/consultoria/`, `/management-consulting/` e o formulário em `/conversar/`, e mande um formulário de teste. O envio vai para o n8n e a contagem de visitas para `app.genesiskore.com`, e os dois continuam vendo a mesma origem (`https://genesiskore.com`), então nada muda ali.

Depois, rode o Is Agentic de novo.

### 7. Desligar o GitHub Pages, só depois de uns dias

Deixe o GitHub Pages ligado por uma semana (até 04/11/2026), com o arquivo `CNAME` no repositório. Ele é o plano de volta. Passado o prazo sem problema, desligue em Settings, Pages do repositório.

## Plano de volta

Se algo der errado depois da troca de DNS:

1. Na WordPress.com, apague os dois `A` da Vercel (`216.198.79.1` e `64.29.17.1`) e ponha de volta os 4 do GitHub Pages (`185.199.108.153`, `185.199.109.153`, `185.199.110.153` e `185.199.111.153`). Troque o `CNAME` do `www` de `67732ecfa8772377.vercel-dns-017.com` para `genesiskorei4-stack.github.io`. Nada mais muda.
2. Confira com `dig +short genesiskore.com A` e com o primeiro `curl` (tem de voltar `server: GitHub.com`).
3. Se o navegador disser "Não seguro", é o certificado do GitHub Pages sendo emitido de novo: Settings, Pages, caixa Enforce HTTPS. Pode levar alguns minutos.
4. O projeto na Vercel pode ficar parado sem custo. Para ele não gastar deploy enquanto isso, desligue o Git do projeto ou pause o projeto.

O site no ar nunca fica sem resposta durante a volta, porque o GitHub Pages continuou publicando a `main` o tempo todo.

## Se o 404 em Markdown não funcionar

As regras com `status` e `dest` depois do `handle: filesystem` são o caminho documentado, mas só o deploy de verdade prova. Se o passo 3 mostrar a raiz certa e o 404 errado, a saída é um Routing Middleware: um `middleware.js` na raiz do repositório que, só quando o `Accept` pede Markdown e o caminho não é uma das páginas do site, devolve o `404.md` com status 404.

O custo: o middleware roda a cada pedido que casar com o `matcher` dele, e conta como execução na Vercel (o plano gratuito tem uma franquia mensal, e o tráfego do site é pequeno). Ele também precisa de uma lista das páginas que existem, mantida junto com o site. Por isso ficou como plano B, e não como primeira opção.

## Depois da troca, registrar

- No `CLAUDE.md` da raiz do `ai-os`, a tabela de projetos da seção de deploy passa de sete para oito, com o `site-genesiskore`, e a tabela de endereços muda o `genesiskore.com` de GitHub Pages para Vercel.
- Na wiki, o fato com data, o resultado do Is Agentic antes e depois, e o que foi medido.
