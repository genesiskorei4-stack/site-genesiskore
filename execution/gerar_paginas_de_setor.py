"""Gera as nove páginas de setor e os pedaços da página inicial que dependem delas (lançamento de 05/01/2027).

Uso: python3 execution/gerar_paginas_de_setor.py            gera e grava
     python3 execution/gerar_paginas_de_setor.py --conferir  só diz se algo gerado está desatualizado (sai 1)

De onde sai cada coisa (regra em directives/paginas-de-setor.md):
- `plantas/setores.json`: o chapéu, a frase e a legenda de cada setor. A frase é o h1 da página.
- `plantas/<setor>-pc.svg` e `-cel.svg`: o desenho, que entra dentro do próprio HTML. No desenho vai só
  o número; a legenda é texto da página.
- `<pasta>/index.md` com `gerar: setor` e `setor: <chave>`: o texto da página. Ele mesmo é publicado e é a
  versão em Markdown que os agentes de IA leem (o vercel.json entrega quando pedem `text/markdown`).
  O `# ` dele tem de ser igual à frase do setores.json, senão o gerador para e avisa.

O que mais ele grava, para nada ficar fora de sincronia:
- `sitemap.xml`, refeito pela mesma função do gerar_paginas.py, com a data de cada página de setor.
- `llms.txt`, só a seção "## Uma página por setor".
- `index.html`, só o que está entre os marcadores `gerado:boas-vindas` (a primeira tela com a planta 03) e
  `gerado:pergunta` (a pergunta "Qual é o setor da sua empresa?", com as nove opções como links de verdade).

O Markdown aceito é o mesmo do gerar_paginas.py. Seções reconhecidas pelo começo do título (##):
"Onde dói", "O que construímos" (seis itens), "O que você não precisa comprar", "Perguntas" e a última,
que tem o botão para /conversar/?setor=<chave>. As outras saem como texto corrido.
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_paginas as gp  # noqa: E402  (cabeçalho, blocos, em_linha, sitemap, ORGANIZACAO)

RAIZ = gp.RAIZ
BASE = gp.BASE
LEMA = ('Construído para você', 'Rodando sem você')

# A ordem é a da pergunta na página inicial. (chave, nome na pergunta, o que cobre, pasta)
SETORES = [
    ('distribuidora', 'Distribuidora e atacado', 'pedido, nota e margem', 'sistema-para-distribuidora'),
    ('escritorio', 'Escritório', 'advocacia, contabilidade, engenharia', 'automacao-para-escritorio'),
    ('varejo', 'Loja e varejo', 'pedido, cliente e pós-venda', 'sistema-para-varejo'),
    ('industria', 'Indústria', 'produção, compra e custo', 'sistema-para-industria'),
    ('imobiliaria', 'Imobiliária', 'visita, contrato e aluguel', 'sistema-para-imobiliaria'),
    ('agencia', 'Agência e eventos', 'orçamento, fornecedor e prazo', 'sistema-para-agencia'),
    ('escola', 'Escola e curso', 'matrícula e mensalidade', 'sistema-para-escola'),
    ('startup', 'Startup', 'a operação que cresce rápido', 'para-startups'),
    ('outro', 'Outro setor', 'o caminho que serve para todos', 'sistemas-sob-medida'),
]
PASTA_DO = {chave: pasta for chave, _, _, pasta in SETORES}
NOME_DO = {chave: nome for chave, nome, _, _ in SETORES}

# "Leia também" das seis páginas novas. As três que já existiam continuam com a lista do gerar_paginas.py.
RELACIONADAS = {
    'sistema-para-varejo': ['ficha-de-cliente-para-joalheria', 'documento-automatico', 'cobranca-automatica'],
    'sistema-para-industria': ['lucro-por-produto', 'sistema-de-pedidos-b2b', 'bling-omie-ou-sistema-sob-medida'],
    'sistema-para-imobiliaria': ['cobranca-automatica', 'documento-automatico', 'automacao-de-processos'],
    'sistema-para-agencia': ['documento-automatico', 'cobranca-automatica', 'automacao-de-processos'],
    'sistema-para-escola': ['cobranca-automatica', 'documento-automatico', 'sistema-para-substituir-planilhas'],
    'para-startups': ['consultoria-de-ia', 'cobranca-automatica', 'quanto-custa-um-sistema-sob-medida'],
}

# A legenda da planta 03 na página inicial (o caminho de uma demanda). É a mesma do setor "outro".
PLANTA_INICIO = 'outro'


def ler(rel):
    return open(os.path.join(RAIZ, rel), encoding='utf-8').read()


def sem_ponto(t):
    return t.strip().rstrip('.').strip()


def prefixar_ids(svg, prefixo):
    """O desenho do computador e o do celular moram na mesma página e usam os mesmos ids (gradiente,
    máscara). Id repetido faz o do celular apontar para o do computador, que está escondido, e o
    navegador não pinta o que mora em elemento escondido. Cada um ganha o seu prefixo."""
    for ident in sorted(set(re.findall(r'\bid="([^"]+)"', svg)), key=len, reverse=True):
        novo = f'{prefixo}-{ident}'
        svg = svg.replace(f'id="{ident}"', f'id="{novo}"')
        svg = svg.replace(f'url(#{ident})', f'url(#{novo})')
        svg = svg.replace(f'href="#{ident}"', f'href="#{novo}"')
    return svg


def desenho(chave, formato, descricao):
    svg = ler(f'plantas/{chave}-{formato}.svg').strip()
    svg = prefixar_ids(svg, f'{chave}-{formato}')
    svg = re.sub(r'aria-label="[^"]*"', f'aria-label="{html.escape(descricao)}"', svg, count=1)
    return svg


def proporcao(svg):
    m = re.search(r'viewBox="([-\d. ]+)"', svg)
    _, _, w, h = (float(x) for x in m.group(1).split())
    return round(w / h, 3)


def legenda_no_desenho(svg, legenda):
    """A planta 03 do computador já traz cada passo escrito ao lado do número. Nela a legenda da página
    fica só no celular, para o texto não aparecer duas vezes."""
    escritos = {t.upper() for t in re.findall(r'<text[^>]*>([^<]+)</text>', svg)}
    return all(sem_ponto(t).upper() in escritos for t in legenda[2:])


def descricao_do_desenho(texto, legenda):
    itens = '; '.join(f'{i}, {sem_ponto(t).lower()}' for i, t in enumerate(legenda, 1))
    return f'{sem_ponto(texto)}. Os números marcam: {itens}.'


# ------------------------------------------------------------------ estilo das páginas de setor

ESTILO = r"""
@font-face{font-family:'Inter Tight';font-style:normal;font-weight:300 700;font-display:swap;src:url('/fontes/inter-tight-latin.woff2') format('woff2')}
@font-face{font-family:'Inter Tight Reserva';src:local('Arial'),local('ArialMT'),local('Liberation Sans'),local('Roboto');size-adjust:95.4%;ascent-override:101.5%;descent-override:25.4%;line-gap-override:0%}
@font-face{font-family:'JetBrains Mono';font-style:normal;font-weight:500;font-display:swap;src:url('/fontes/jetbrains-mono-latin.woff2') format('woff2')}
@font-face{font-family:'Playfair Display';font-style:italic;font-weight:400;font-display:swap;src:url('/fontes/playfair-italic-latin.woff2') format('woff2')}
@view-transition{navigation:auto}
:root{--azul:#120A8F;--tinta:#121212;--suave:#4a4a4a;--linha:#dcdcdc;--papel:#ffffff;--mono:'JetBrains Mono',ui-monospace,monospace;--letra:'Inter Tight','Inter Tight Reserva',system-ui,sans-serif}
*,*::before,*::after{box-sizing:border-box}
*{margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{background:var(--papel);color:var(--tinta);font:400 17px/1.6 var(--letra);-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit}
img,svg{max-width:100%}
.pular{position:absolute;left:-9999px;top:0;background:#fff;color:var(--azul);padding:12px 16px;z-index:10}
.pular:focus{left:12px;top:12px}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}

.topo{background:var(--azul);color:#fff;display:flex;align-items:center;gap:24px;padding:10px max(20px,calc((100% - 1200px)/2))}
.marca{display:flex;align-items:center;gap:10px;text-decoration:none;margin-right:auto;font:600 25px/1 var(--letra);letter-spacing:-.03em}
.marca img{height:34px;width:auto;display:block}
.menu{display:none;gap:30px}
.menu a{font:500 12px var(--letra);letter-spacing:.12em;text-transform:uppercase;text-decoration:none;opacity:.9;padding:12px 0}
.menu a:hover{opacity:1;text-decoration:underline;text-underline-offset:6px}
.topo-cta{background:#fff;color:var(--azul);font:500 12px var(--letra);letter-spacing:.12em;text-transform:uppercase;text-decoration:none;padding:15px 21px;min-height:44px;display:inline-flex;align-items:center}

.heroi{background:var(--azul);color:#fff;text-align:center;padding:4px 20px 44px}
.volta{display:inline-flex;align-items:center;min-height:44px;font:500 11px var(--mono);letter-spacing:.14em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(255,255,255,.35);padding:0 12px;opacity:.85}
.volta:hover{opacity:1;border-color:#fff}
.chapeu{font:500 12px/1.6 var(--mono);letter-spacing:.2em;text-transform:uppercase;opacity:.8;margin:12px auto 0;max-width:760px}
.lema{font:600 clamp(32px,9.3vw,84px)/.98 var(--letra);letter-spacing:-.05em;margin-top:12px}
.lema span{display:block;white-space:nowrap}
.lema span+span{opacity:.6}
.heroi h1{font:500 clamp(16px,2vw,20px)/1.35 var(--letra);letter-spacing:-.01em;margin:14px auto 0;max-width:760px;opacity:.95}
.planta{margin:8px auto 0;width:min(1180px,calc((100vh - 430px) * var(--proporcao,2.42)));min-width:min(100%,640px)}
.planta .so-cel{display:none}
.legenda.so-celular{display:none}
.legenda{display:flex;flex-wrap:wrap;justify-content:center;gap:10px 44px;list-style:none;margin:10px auto 0;text-align:left}
.legenda li{display:flex;gap:10px;align-items:center;font:500 12px/1.35 var(--mono);letter-spacing:.12em;text-transform:uppercase}
.legenda b{flex:none;width:22px;height:22px;border-radius:50%;background:#fff;color:var(--azul);display:flex;align-items:center;justify-content:center;font-size:11px}

.corpo{max-width:1040px;margin:0 auto;padding:0 20px}
.secao{padding:72px 0 0}
.secao h2{font:600 clamp(28px,4.2vw,44px)/1.05 var(--letra);letter-spacing:-.035em;max-width:820px;margin-bottom:22px}
.secao h2 em{font:italic 400 1.08em/1 'Playfair Display',Georgia,serif;letter-spacing:0;color:var(--azul)}
.secao h3{font:600 20px/1.25 var(--letra);letter-spacing:-.015em;margin:28px 0 8px}
.secao p,.secao li{max-width:760px}
.secao p+p{margin-top:14px}
.secao a{color:var(--azul);text-underline-offset:3px}
.secao ul,.secao ol{margin:18px 0 0 20px}
.secao li+li{margin-top:8px}
.secao ul+p,.secao ol+p{margin-top:18px}
.secao strong{font-weight:600}
.secao blockquote{border-left:3px solid var(--azul);padding:4px 0 4px 18px;margin-top:20px;max-width:720px;font-size:19px;line-height:1.5}
.suave{color:var(--suave);font-size:15px}
.intro h2{font-size:clamp(22px,2.8vw,30px);letter-spacing:-.02em;color:var(--suave)}
.intro p:first-of-type{font-size:19px;line-height:1.55}

.dores ul{list-style:none;margin-left:0;border-top:1px solid var(--linha);max-width:820px}
.dores li{max-width:none;padding:16px 0 16px 40px;border-bottom:1px solid var(--linha);position:relative;margin:0}
.dores li::before{content:counter(dor,decimal-leading-zero);counter-increment:dor;position:absolute;left:0;top:19px;font:500 12px var(--mono);color:var(--azul);letter-spacing:.08em}
.dores ul{counter-reset:dor}

.modulos ul{list-style:none;margin:0;display:grid;grid-template-columns:1fr;gap:12px}
.modulos li{max-width:none;margin:0;border:1px solid var(--linha);padding:20px 22px;background:#fff}
.modulos li strong{display:block;font-size:18px;letter-spacing:-.01em;margin-bottom:4px}

.nao-comprar{background:#0a0a0a;color:#fff;margin:72px -20px 0;padding:64px 20px}
.nao-comprar .dentro{max-width:1040px;margin:0 auto}
.nao-comprar h2{color:#fff}
.nao-comprar a{color:#fff}
.nao-comprar p{color:rgba(255,255,255,.86)}

.secao table{border-collapse:collapse;width:100%;min-width:560px;font-size:15px}
.tabela{overflow-x:auto;margin-top:18px;border:1px solid var(--linha)}
.secao th,.secao td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--linha);vertical-align:top}
.secao thead th{font:500 11px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--suave)}

.passos ol{list-style:none;margin-left:0;counter-reset:passo}
.passos li{position:relative;padding:14px 0 14px 48px;border-top:1px solid var(--linha);margin:0}
.passos li::before{content:counter(passo,decimal-leading-zero);counter-increment:passo;position:absolute;left:0;top:17px;font:500 12px var(--mono);color:var(--azul);letter-spacing:.08em}

.perguntas h3{border-top:1px solid var(--linha);padding-top:22px}

.leia{padding-top:72px}
.leia h2{font:500 12px var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--suave);margin-bottom:12px}
.leia ul{list-style:none;display:flex;flex-wrap:wrap;gap:8px}
.leia a{display:inline-flex;align-items:center;min-height:44px;border:1px solid var(--linha);padding:0 14px;text-decoration:none;color:var(--tinta);font-size:15px}
.leia a:hover{border-color:var(--azul);color:var(--azul)}

.chamada{background:var(--azul);color:#fff;text-align:center;margin-top:88px;padding:80px 20px}
.chamada h2{font:600 clamp(30px,5vw,52px)/1.05 var(--letra);letter-spacing:-.04em;max-width:820px;margin:0 auto}
.chamada p{max-width:620px;margin:16px auto 0;color:rgba(255,255,255,.86)}
.botao{display:inline-flex;align-items:center;gap:10px;min-height:48px;margin-top:28px;background:#fff;color:var(--azul);font:500 13px var(--letra);letter-spacing:.14em;text-transform:uppercase;text-decoration:none;padding:0 26px}
.botao:hover{background:#0a0a0a;color:#fff}

.rodape{background:#fafafa;border-top:4px solid var(--azul);padding:36px 20px calc(36px + env(safe-area-inset-bottom));font-size:14px;color:var(--suave)}
.rodape .dentro{max-width:1040px;margin:0 auto;display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center}
.rodape a{color:var(--tinta);text-decoration:none;min-height:44px;display:inline-flex;align-items:center}
.rodape a:hover{text-decoration:underline}
.rodape p{width:100%}

@media (min-width:720px){
 .modulos ul{grid-template-columns:1fr 1fr}
 .nao-comprar{margin-left:calc((100vw - 100%) / -2);margin-right:calc((100vw - 100%) / -2);padding-left:calc((100vw - 100%) / 2 + 20px);padding-right:calc((100vw - 100%) / 2 + 20px)}
}
@media (min-width:1024px){
 .menu{display:flex}
 .modulos ul{grid-template-columns:repeat(3,1fr)}
}
@media (max-width:767px){
 body{font-size:16px}
 .topo{padding:12px 20px}
 .marca span{display:none}
 .marca img{height:40px}
 .topo-cta{font-size:13px;padding:0 20px}
 .heroi{padding:22px 20px 32px}
 .volta{font-size:10px}
 .chapeu{font-size:10px;letter-spacing:.08em;max-width:320px}
 .lema{font-size:9.3vw}
 .heroi h1{max-width:330px}
 .planta{width:calc(100% + 40px);min-width:0;margin:22px -20px 0}
 .planta .so-pc{display:none}
 .planta .so-cel{display:block}
 .legenda,.legenda.so-celular{display:grid;grid-template-columns:1fr;gap:9px;max-width:330px;margin-top:18px}
 .legenda li{font-size:10.5px;letter-spacing:.06em}
 .intro p:first-of-type{font-size:17px}
 .secao{padding-top:52px}
 .nao-comprar{margin-top:52px;padding:48px 20px}
 .chamada{margin-top:64px;padding:60px 20px}
}
@media (prefers-reduced-motion:reduce){@view-transition{navigation:none}}
"""
# O menu do celular é o mesmo das páginas internas (gerar_paginas.MENU_CSS e gerar_paginas.topo).
ESTILO += gp.MENU_CSS + '\n'


# ------------------------------------------------------------------ uma página

def secoes(partes):
    """Agrupa os blocos do Markdown por ## (h2). O h1 fica de fora."""
    grupos, atual = [], None
    for t, c in partes:
        if t == 'h1':
            continue
        if t == 'h2':
            atual = {'titulo': c, 'blocos': []}
            grupos.append(atual)
        elif atual is not None:
            atual['blocos'].append((t, c))
    return grupos


def tipo_da_secao(titulo, i, total):
    t = titulo.lower()
    if i == 0:
        return 'intro'
    if t.startswith('onde dói'):
        return 'dores'
    if t.startswith('o que construímos'):
        return 'modulos'
    if t.startswith('o que você não precisa comprar'):
        return 'nao-comprar'
    if t.startswith('como funciona'):
        return 'passos'
    if t.startswith('perguntas'):
        return 'perguntas'
    if i == total - 1:
        return 'chamada'
    return ''


def blocos_html(blocos, recuo='        '):
    saida = []
    for t, c in blocos:
        if t == 'h3':
            saida.append(f'{recuo}<h3>{gp.em_linha(c)}</h3>')
        elif t == 'p':
            botao = re.fullmatch(r'\[([^\]]+)\]\((/conversar/[^)]*)\)', c)
            if botao:
                saida.append(f'{recuo}<a class="botao" href="{html.escape(botao.group(2))}">{html.escape(botao.group(1))}'
                             '<svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>')
            else:
                saida.append(f'{recuo}<p>{gp.em_linha(c)}</p>')
        elif t == 'blockquote':
            saida.append(f'{recuo}<blockquote>{gp.em_linha(c)}</blockquote>')
        elif t == 'table':
            cab = ''.join(f'<th scope="col">{gp.em_linha(x)}</th>' for x in c[0])
            linhas = ''.join('<tr><th scope="row">' + gp.em_linha(r[0]) + '</th>' + ''.join(f'<td>{gp.em_linha(x)}</td>' for x in r[1:]) + '</tr>' for r in c[1:])
            saida.append(f'{recuo}<div class="tabela"><table><thead><tr>{cab}</tr></thead><tbody>{linhas}</tbody></table></div>')
        else:
            itens = ''.join(f'<li>{gp.em_linha(i)}</li>' for i in c)
            saida.append(f'{recuo}<{t}>{itens}</{t}>')
    return '\n'.join(saida)


def titulo_h2(titulo, tipo):
    texto = gp.em_linha(titulo)
    # A única palavra em Playfair da página, em azul sobre branco (identidade de 24/11/2026).
    if tipo == 'dores':
        texto = re.sub(r'\bdói\b', '<em>dói</em>', texto, count=1)
    return texto


def leia_tambem(pasta):
    vizinhas = gp.RELACIONADAS.get(pasta) or RELACIONADAS.get(pasta, [])
    itens = []
    for vizinha in vizinhas:
        dados, _ = gp.cabecalho(ler(os.path.join(vizinha, 'index.md')))
        itens.append(f'<li><a href="/{vizinha}/">{html.escape(dados.get("trilha", vizinha))}</a></li>')
    return ''.join(itens)


def outros_setores(chave):
    return ''.join(f'<li><a href="/{pasta}/">{html.escape(nome)}</a></li>' for c, nome, _, pasta in SETORES if c != chave)


def conferir_texto(pasta, chave, meta, dados, partes, grupos):
    """O que a diretiva exige de toda página de setor. Falha para, com o motivo."""
    erros = []
    h1 = next((c for t, c in partes if t == 'h1'), '')
    if sem_ponto(h1) != sem_ponto(meta['frase']):
        erros.append(f'o "# " do index.md ("{h1}") tem de ser a frase do setores.json ("{meta["frase"]}")')
    tipos = [tipo_da_secao(g['titulo'], i, len(grupos)) for i, g in enumerate(grupos)]
    for exigido, nome in (('dores', 'Onde dói'), ('modulos', 'O que construímos'), ('nao-comprar', 'O que você não precisa comprar'), ('perguntas', 'Perguntas')):
        if exigido not in tipos:
            erros.append(f'falta a seção "## {nome}"')
    modulos = next((g for g, t in zip(grupos, tipos) if t == 'modulos'), None)
    if modulos:
        n = sum(len(c) for t, c in modulos['blocos'] if t == 'ul')
        if n != 6:
            erros.append(f'"O que construímos" tem {n} módulos, e o molde pede seis')
    if f'(/conversar/?setor={chave})' not in ''.join(c for g in grupos[-1:] for t, c in g['blocos'] if t == 'p'):
        erros.append(f'a última seção precisa do botão [..](/conversar/?setor={chave})')
    for campo in ('titulo', 'descricao', 'trilha', 'servico', 'publico', 'desenho', 'atualizado'):
        if not dados.get(campo):
            erros.append(f'falta o campo "{campo}" no cabeçalho')
    if re.search('[—–]', ler(os.path.join(pasta, 'index.md'))):
        erros.append('tem travessão ou meia-risca no texto')
    if erros:
        raise SystemExit(f'{pasta}/index.md: ' + '; '.join(erros))


def montar(chave, pasta, meta, md):
    dados, corpo = gp.cabecalho(md)
    partes = gp.blocos(corpo)
    grupos = secoes(partes)
    conferir_texto(pasta, chave, meta, dados, partes, grupos)
    url = BASE + pasta + '/'
    frase = sem_ponto(meta['frase'])

    descricao_planta = descricao_do_desenho(dados['desenho'], meta['legenda'])
    pc, cel = desenho(chave, 'pc', descricao_planta), desenho(chave, 'cel', descricao_planta)
    legenda = ''.join(f'<li><b>{i}</b>{html.escape(t)}</li>' for i, t in enumerate(meta['legenda'], 1))

    # Perguntas: cada ### da seção "Perguntas" com o parágrafo logo abaixo, igual ao gerar_paginas.py.
    perguntas = []
    for g in grupos:
        if tipo_da_secao(g['titulo'], 1, 2) != 'perguntas':
            continue
        pergunta = None
        for t, c in g['blocos']:
            if t == 'h3':
                pergunta = c
            elif t == 'p' and pergunta:
                perguntas.append((pergunta, gp.texto_puro(c)))
                pergunta = None

    corpo_html = []
    for i, g in enumerate(grupos):
        tipo = tipo_da_secao(g['titulo'], i, len(grupos))
        ident = re.sub(r'[^a-z0-9]+', '-', gp.texto_puro(g['titulo']).lower().translate(str.maketrans('áàâãéêíóôõúç', 'aaaaeeiooouc'))).strip('-')
        h2 = titulo_h2(g['titulo'], tipo)
        miolo = blocos_html(g['blocos'])
        if tipo == 'chamada':
            vizinhas = leia_tambem(pasta)
            corpo_html.append(f'''    <div class="corpo">
    <nav class="leia" aria-label="Outros setores">
        <h2>Outros setores</h2>
        <ul>{outros_setores(chave)}</ul>
    </nav>
    <nav class="leia" aria-label="Leia também">
        <h2>Leia também</h2>
        <ul>{vizinhas}</ul>
    </nav>
    </div>
    <section class="chamada" id="{ident}" aria-labelledby="t-{ident}">
        <h2 id="t-{ident}">{h2}</h2>
{miolo}
    </section>''')
        elif tipo == 'nao-comprar':
            corpo_html.append(f'''    <div class="corpo"><section class="secao nao-comprar" id="{ident}" aria-labelledby="t-{ident}"><div class="dentro">
        <h2 id="t-{ident}">{h2}</h2>
{miolo}
    </div></section></div>''')
        else:
            classe = f'secao {tipo}'.strip()
            corpo_html.append(f'''    <div class="corpo"><section class="{classe}" id="{ident}" aria-labelledby="t-{ident}">
        <h2 id="t-{ident}">{h2}</h2>
{miolo}
    </section></div>''')

    atualizado = dados['atualizado']
    a, m_, d = atualizado.split('-')
    grafo = [gp.ORGANIZACAO, {
        '@type': 'WebPage',
        '@id': url + '#pagina',
        'url': url,
        'name': dados['titulo'],
        'headline': frase,
        'description': dados['descricao'],
        'inLanguage': 'pt-BR',
        'isPartOf': {'@id': BASE + '#site'},
        'publisher': {'@id': BASE + '#organizacao'},
        'dateModified': atualizado,
        'breadcrumb': {'@id': url + '#trilha'},
        'about': {'@id': url + '#servico'},
    }, {
        '@type': 'BreadcrumbList',
        '@id': url + '#trilha',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Início', 'item': BASE},
            {'@type': 'ListItem', 'position': 2, 'name': dados['trilha'], 'item': url},
        ],
    }, {
        '@type': 'Service',
        '@id': url + '#servico',
        'name': dados['servico'],
        'serviceType': dados.get('tipo_servico', dados['servico']),
        'url': url,
        'provider': {'@id': BASE + '#organizacao'},
        'areaServed': {'@type': 'Country', 'name': 'Brasil'},
        'description': dados['descricao'],
        'audience': {'@type': 'BusinessAudience', 'name': dados['publico']},
        'slogan': ' / '.join(LEMA),
    }]
    if perguntas:
        grafo.append({
            '@type': 'FAQPage',
            '@id': url + '#perguntas',
            'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in perguntas],
        })
    ld = json.dumps({'@context': 'https://schema.org', '@graph': grafo}, ensure_ascii=False, indent=2)
    titulo = html.escape(dados['titulo'])
    descricao = html.escape(dados['descricao'])
    conversar = f'/conversar/?setor={chave}'
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <!-- Página de setor gerada por execution/gerar_paginas_de_setor.py a partir de {pasta}/index.md, de
         plantas/setores.json e de plantas/{chave}-pc.svg e -cel.svg. Edite a fonte e rode o script. -->
    <title>{titulo}</title>
    <meta name="description" content="{descricao}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
    <meta name="theme-color" content="#120A8F">
    <link rel="canonical" href="{url}">
    <link rel="alternate" type="text/markdown" href="{url}index.md" title="Versão em Markdown para agentes de IA">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{url}">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:site_name" content="GenesisKore">
    <meta property="og:title" content="{html.escape(dados.get('titulo_curto', dados['titulo']))}">
    <meta property="og:description" content="{descricao}">
    <meta property="og:image" content="https://genesiskore.com/previa-link.png">
    <link rel="icon" type="image/png" href="/icone-tema-claro.png?v=1" media="(prefers-color-scheme: light)">
    <link rel="icon" type="image/png" href="/icone-tema-escuro.png?v=1" media="(prefers-color-scheme: dark)">
    <link rel="help" type="text/plain" href="https://genesiskore.com/llms.txt">
    <link rel="preload" href="/fontes/inter-tight-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="/fontes/jetbrains-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
    <script type="application/ld+json">
{ld}
    </script>
    <style>{ESTILO}</style>
</head>
<body>
{gp.topo('pt', conversar)}
    <main id="conteudo">
    <section class="heroi" aria-labelledby="titulo-setor">
        <a class="volta" href="/"><span aria-hidden="true">&larr;&nbsp;</span>Escolher outro setor</a>
        <p class="chapeu">{html.escape(meta['chapeu'])}</p>
        <p class="lema"><span>{LEMA[0]}</span> <span>{LEMA[1]}</span></p>
        <h1 id="titulo-setor">{html.escape(frase)}.</h1>
        <figure class="planta" style="--proporcao:{proporcao(pc)}">
            <div class="so-pc">{pc}</div>
            <div class="so-cel">{cel}</div>
            <figcaption><ol class="legenda{' so-celular' if legenda_no_desenho(pc, meta['legenda']) else ''}">{legenda}</ol></figcaption>
        </figure>
    </section>
{chr(10).join(corpo_html)}
    </main>
    <footer class="rodape">
        <div class="dentro">
            <a href="/">Início</a><a href="/sistemas-sob-medida/">Sistemas sob medida</a><a href="/consultoria/">Consultoria de gestão</a><a href="/sobre/">Sobre</a><a href="/contato/">Contato</a><a href="/privacidade/">Privacidade</a>
            <p>© 2026 GenesisKore. Sistemas sob medida e consultoria de gestão. São Paulo, atendimento em todo o Brasil. Atualizado em {d}/{m_}/{a}.</p>
        </div>
    </footer>
    <!-- Contagem de visitas sem cookie e sem IP. -->
    <script src="/contagem.js" defer></script>
</body>
</html>
'''


# ------------------------------------------------------------------ a página inicial

def boas_vindas(meta):
    """A primeira tela da página inicial: o lema e a planta 03 (o caminho de uma demanda)."""
    m = meta[PLANTA_INICIO]
    dados, _ = gp.cabecalho(ler(os.path.join(PASTA_DO[PLANTA_INICIO], 'index.md')))
    descricao = descricao_do_desenho(dados['desenho'], m['legenda'])
    pc = desenho(PLANTA_INICIO, 'pc', descricao).replace(f'id="{PLANTA_INICIO}-pc-', 'id="inicio-pc-').replace(f'#{PLANTA_INICIO}-pc-', '#inicio-pc-')
    cel = desenho(PLANTA_INICIO, 'cel', descricao).replace(f'id="{PLANTA_INICIO}-cel-', 'id="inicio-cel-').replace(f'#{PLANTA_INICIO}-cel-', '#inicio-cel-')
    legenda = ''.join(f'<li><b>{i}</b>{html.escape(t)}</li>' for i, t in enumerate(m['legenda'], 1))
    return f'''        <section class="boas-vindas" id="inicio" aria-labelledby="titulo-inicio">
            <h1 class="bv-titulo" id="titulo-inicio"><span class="linha">{LEMA[0]}</span> <span class="linha">{LEMA[1]}</span></h1>
            <p class="bv-dor">A empresa cresceu e ainda depende de você.</p>
            <figure class="bv-planta" style="--proporcao:{proporcao(pc)}">
                <div class="so-pc">{pc}</div>
                <div class="so-cel">{cel}</div>
                <figcaption><ol class="bv-legenda">{legenda}</ol></figcaption>
            </figure>
            <p class="bv-sub"><span class="linha">Sistema para o que se repete.</span> <span class="linha">Número para o que se decide.</span></p>
            <a class="bv-botao" href="/conversar/">Quero conversar</a>
        </section>'''


def pergunta():
    """A pergunta do setor: um dialog com nove links de verdade. Quem abre é o script.js."""
    opcoes = '\n'.join(
        f'                <li><a class="pp-op" href="/{pasta}/" data-setor="{chave}"><b>{html.escape(nome)}</b>'
        f'<small>{html.escape(cobre)}</small><span class="pp-seta" aria-hidden="true">&rarr;</span></a></li>'
        for chave, nome, cobre, pasta in SETORES)
    return f'''    <dialog class="pergunta" id="pergunta" aria-labelledby="pergunta-titulo" aria-describedby="pergunta-texto">
        <form method="dialog" class="pp-topo"><button class="pp-x" value="fechar" aria-label="Fechar e ver a página inteira"><span aria-hidden="true">&times;</span></button></form>
        <p class="pp-chapeu">Antes de começar</p>
        <h2 id="pergunta-titulo" tabindex="-1" autofocus>Qual é o setor da sua empresa?</h2>
        <p id="pergunta-texto" class="pp-texto">A gente mostra o que faz para empresas como a sua.</p>
        <nav aria-label="Setores">
            <ul class="pp-grade">
{opcoes}
            </ul>
        </nav>
        <form method="dialog"><button class="pp-pular" value="pular">Pular, quero ver tudo</button></form>
    </dialog>'''


def trocar_bloco(texto, nome, novo, arquivo):
    inicio, fim = f'<!-- gerado:{nome} -->', f'<!-- /gerado:{nome} -->'
    if inicio not in texto or fim not in texto:
        raise SystemExit(f'{arquivo}: faltam os marcadores {inicio} e {fim}')
    a = texto.index(inicio) + len(inicio)
    b = texto.index(fim)
    return texto[:a] + '\n' + novo + '\n        ' + texto[b:] if nome == 'boas-vindas' else texto[:a] + '\n' + novo + '\n    ' + texto[b:]


def llms(texto, meta):
    """Só a seção "## Uma página por setor" do llms.txt."""
    linhas = ['## Uma página por setor', '',
              'A página inicial pergunta "Qual é o setor da sua empresa?" e leva a uma destas nove páginas, '
              'cada uma com as dores do setor, o que a GenesisKore constrói, o que o dono não precisa comprar e as perguntas frequentes.', '']
    for chave, nome, _, pasta in SETORES:
        dados, _ = gp.cabecalho(ler(os.path.join(pasta, 'index.md')))
        linhas.append(f'- [{nome}]({BASE}{pasta}/) ([Markdown]({BASE}{pasta}/index.md)): {sem_ponto(meta[chave]["frase"])}. {dados["descricao"]}')
    novo = '\n'.join(linhas) + '\n\n'
    m = re.search(r'## Uma página por setor\n.*?(?=\n## )', texto, re.S)
    if not m:
        raise SystemExit('llms.txt: falta a seção "## Uma página por setor" (ela tem de vir antes de outra seção ##)')
    return texto[:m.start()] + novo.rstrip('\n') + '\n' + texto[m.end():]


def main():
    conferir = '--conferir' in sys.argv
    meta = json.load(open(os.path.join(RAIZ, 'plantas', 'setores.json'), encoding='utf-8'))
    faltam = [c for c, *_ in SETORES if c not in meta]
    if faltam or len(meta) != len(SETORES):
        raise SystemExit(f'plantas/setores.json e a lista SETORES não batem (faltam: {faltam})')
    mudados, rascunhos = [], []
    lastmods = dict(re.findall(r'<loc>(.*?)</loc><lastmod>(.*?)</lastmod>', ler('sitemap.xml')))
    for chave, _, _, pasta in SETORES:
        fonte = os.path.join(pasta, 'index.md')
        if not os.path.isfile(os.path.join(RAIZ, fonte)):
            raise SystemExit(f'falta {fonte}, o texto do setor {chave}')
        md = ler(fonte)
        dados, _ = gp.cabecalho(md)
        if dados.get('gerar') != 'setor' or dados.get('setor') != chave:
            raise SystemExit(f'{fonte}: o cabeçalho precisa de "gerar: setor" e "setor: {chave}"')
        if dados.get('rascunho'):
            rascunhos.append(pasta)
        gp.gravar(os.path.join(pasta, 'index.html'), montar(chave, pasta, meta[chave], md), conferir, mudados)
        lastmods[BASE + pasta + '/'] = dados['atualizado']
    gp.gravar('sitemap.xml', gp.sitemap(lastmods), conferir, mudados)
    gp.gravar('llms.txt', llms(ler('llms.txt'), meta), conferir, mudados)
    inicio = ler('index.html')
    inicio = trocar_bloco(inicio, 'boas-vindas', boas_vindas(meta), 'index.html')
    inicio = trocar_bloco(inicio, 'pergunta', pergunta(), 'index.html')
    gp.gravar('index.html', inicio, conferir, mudados)
    if rascunhos:
        print(f'Aviso: {len(rascunhos)} página(s) ainda marcadas como rascunho, esperando a aprovação dos sócios: ' + ', '.join(rascunhos))
    if conferir:
        print('Desatualizado: ' + ', '.join(mudados) if mudados else 'Páginas de setor em dia.')
        return 1 if mudados else 0
    print('Gravado: ' + (', '.join(mudados) if mudados else 'nada mudou'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
