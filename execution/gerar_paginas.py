"""Gera as páginas de conteúdo do site a partir de um Markdown, e refaz o sitemap.

Uso: python3 execution/gerar_paginas.py            gera e grava
     python3 execution/gerar_paginas.py --conferir  só diz se algo gerado está desatualizado (sai 1)

De onde sai cada coisa:
- `<pasta>/index.md` com `gerar: sim` no cabeçalho é a fonte. Ele mesmo é publicado e é a versão
  em Markdown que os agentes de IA leem (o vercel.json entrega quando pedem `text/markdown`).
- `<pasta>/index.html` é montado daqui: o visual vem do <style> de consultoria/index.html, para
  todas as páginas secundárias ficarem iguais. Não edite o HTML gerado à mão; edite o .md e rode.
- O topo e o rodapé (identidade do lançamento de 05/01/2027) saem de `topo()` e `rodape()`, e valem
  também para os cases (gerar_paginas_de_case.py) e para as páginas escritas à mão de MOLDE_A_MAO: nelas
  este script troca só o <style>, o topo e o rodapé, e nunca o texto do <main>.
- As perguntas da seção "## Perguntas" viram o FAQPage dos dados estruturados, com o mesmo texto
  que está na tela (o Google pede que seja igual).
- `sitemap.xml` é refeito com toda página que é canônica dela mesma, e só ela.

O Markdown aceito é o pedaço que as páginas usam: #, ##, ###, parágrafo, lista com - ou 1.,
**negrito**, [link](endereço) e > citação.
"""
import html, json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://genesiskore.com/'
ORGANIZACAO = {
    '@type': ['Organization', 'ProfessionalService'],
    '@id': BASE + '#organizacao',
    'name': 'GenesisKore',
    'alternateName': 'Genesis Kore',
    'url': BASE,
    'logo': BASE + 'logo.png',
    'foundingDate': '2025-08',
    'email': 'contato@genesiskore.com',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'São Paulo', 'addressRegion': 'SP', 'addressCountry': 'BR'},
    'areaServed': {'@type': 'Country', 'name': 'Brasil'},
    'sameAs': ['https://www.instagram.com/genesiskore/', 'https://www.tiktok.com/@genesiskore', 'https://www.linkedin.com/company/genesiskore'],
}


# Identidade do lançamento de 05/01/2027 (25/11/2026): o topo azul das páginas de setor e o rodapé da página
# inicial. Um molde só para as páginas geradas, os cases e as escritas à mão, para nenhuma ficar para trás.
PRELOAD = ('    <link rel="preload" href="/fontes/inter-tight-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
           '    <link rel="preload" href="/fontes/jetbrains-mono-latin.woff2" as="font" type="font/woff2" crossorigin>\n')
TOPO = {
    'pt': ('Pular para o conteúdo', 'GenesisKore, página inicial', 'Páginas', 'Conversar',
           [('/#sistemas', 'Sistemas'), ('/consultoria/', 'Consultoria'), ('/#cases', 'Resultados'),
            ('/#como-funciona', 'Como funciona'), ('/#perguntas', 'Perguntas')]),
    'en': ('Skip to content', 'GenesisKore, home page', 'Pages', 'Talk to us',
           [('/management-consulting/', 'Consulting'), ('/about/', 'About'), ('/contact/', 'Contact')]),
}
REDES = [('mailto:contato@genesiskore.com', 'contato@genesiskore.com'),
         ('https://www.instagram.com/genesiskore/', 'Instagram @genesiskore'),
         ('https://www.tiktok.com/@genesiskore', 'TikTok @genesiskore'),
         ('https://www.linkedin.com/company/genesiskore', 'LinkedIn GenesisKore')]
REL = ' rel="noopener"'
COLUNAS = {
    'pt': [('Sistemas sob medida', [('/sistemas-sob-medida/', 'Como funciona'), ('/sistema-para-distribuidora/', 'Para distribuidora e atacado'),
                                    ('/sistema-para-distribuidora-de-alimentos/', 'Para distribuidora de alimentos'), ('/sistema-de-pedidos-b2b/', 'Pedidos B2B'),
                                    ('/lucro-por-produto/', 'Lucro por produto'), ('/automacao-de-processos/', 'Automação de processos'),
                                    ('/automacao-para-escritorio/', 'Para escritório')]),
           ('Para decidir', [('/bling-omie-ou-sistema-sob-medida/', 'Bling, Omie ou sob medida'), ('/quanto-custa-um-sistema-sob-medida/', 'Quanto custa'),
                             ('/sistema-para-substituir-planilhas/', 'Substituir planilhas'), ('/consultoria-de-ia/', 'Consultoria de IA'),
                             ('/consultoria-financeira/', 'Consultoria financeira'), ('/dre-gerencial-para-distribuidora/', 'DRE gerencial (modelo)')]),
           ('Contato', REDES)],
    'en': [('Pages', [('/', 'Home'), ('/management-consulting/', 'Consulting'), ('/about/', 'About'), ('/contact/', 'Contact'), ('/privacy/', 'Privacy')]),
           ('Contact', REDES)],
}
RODAPE_FIM = {
    'pt': ('A empresa cresceu e ainda depende de você.',
           '© 2026 GenesisKore. Sistemas sob medida e consultoria de gestão. São Paulo, atendimento em todo o Brasil.',
           [('/consultoria/', 'Consultoria'), ('/sobre/', 'Sobre'), ('/contato/', 'Contato'), ('/privacidade/', 'Privacidade')]),
    'en': ('Custom systems and management consulting.',
           '© 2026 GenesisKore. Custom systems and management consulting.', []),
}


def topo(lingua='pt'):
    pular, rotulo, rotulo_nav, cta, menu = TOPO[lingua]
    links = ''.join(f'<a href="{h}">{t}</a>' for h, t in menu)
    return (f'    <a class="pular" href="#conteudo">{pular}</a>\n'
            f'    <header class="topo">\n'
            f'        <a href="/" class="marca" aria-label="{rotulo}"><img src="/logo.webp" alt="" width="36" height="40"><span>GenesisKore</span></a>\n'
            f'        <nav class="menu" aria-label="{rotulo_nav}">{links}</nav>\n'
            f'        <a class="topo-cta" href="/conversar/">{cta}</a>\n'
            f'    </header>')


def rodape(lingua='pt', outro_idioma=None):
    """outro_idioma: (endereço, hreflang) da mesma página no outro idioma, quando ela existe."""
    frase, direitos, fim = RODAPE_FIM[lingua]
    colunas = ''
    for titulo, links in COLUNAS[lingua]:
        itens = ''.join(f'                <li><a href="{h}"{REL if h.startswith("https") else ""}>{t}</a></li>\n' for h, t in links)
        colunas += (f'            <ul class="rodape-links" aria-label="{titulo}">\n'
                    f'                <li class="rodape-titulo">{titulo}</li>\n{itens}            </ul>\n')
    links = [f'<a href="{h}">{t}</a>' for h, t in fim]
    if outro_idioma:
        h, lang = outro_idioma
        links.append(f'<a href="{h}" hreflang="{lang}" lang="{lang}">{"English" if lang == "en" else "Português"}</a>')
    return (f'    <footer class="rodape">\n'
            f'        <div class="rodape-grade">\n'
            f'            <div>\n'
            f'                <a href="/" class="marca" aria-label="{TOPO[lingua][1]}"><img src="/logo.webp" alt="" width="32" height="36" loading="lazy"><span>GenesisKore</span></a>\n'
            f'                <p>{frase}</p>\n'
            f'            </div>\n{colunas}'
            f'        </div>\n'
            f'        <p class="rodape-fim">{direitos}{" " + " · ".join(links) if links else ""}</p>\n'
            f'    </footer>')


# Páginas escritas à mão: o texto é delas, mas o estilo, o topo e o rodapé vêm do molde acima.
MOLDE_A_MAO = ('consultoria', 'management-consulting', 'sobre', 'about', 'contato', 'contact', 'privacidade', 'privacy', '404.html')


def vestir(pagina, estilo, trocar_estilo=True):
    """Põe o estilo, o topo e o rodapé do molde numa página pronta, sem tocar no <main>."""
    lingua = 'en' if '<html lang="en">' in pagina else 'pt'
    rod = re.search(r'\n    <footer\b.*?\n    </footer>', pagina, re.S)
    outro = re.search(r'href="([^"]+)" hreflang="(en|pt-BR)"', rod.group(0)) if rod else None
    outro = ('/' + re.sub(r'^(\.\./|/)', '', outro.group(1)), outro.group(2)) if outro else None
    if trocar_estilo:
        pagina = re.sub(r'<style>.*?</style>', lambda m: f'<style>{estilo}</style>', pagina, count=1, flags=re.S)
    pagina = pagina.replace('<meta name="theme-color" content="#000000">', '<meta name="theme-color" content="#120A8F">')
    if 'inter-tight-latin.woff2" as="font"' not in pagina:
        pagina = pagina.replace('    <style>', PRELOAD + '    <style>', 1)
    pagina = re.sub(r'\n    (?:<a class="pular"[^\n]*\n    )?<header\b.*?\n    </header>', lambda m: '\n' + topo(lingua), pagina, count=1, flags=re.S)
    if rod:
        pagina = pagina.replace(rod.group(0), '\n' + rodape(lingua, outro), 1)
    return pagina.replace('<main>', '<main id="conteudo">', 1)


def ler(rel):
    return open(os.path.join(RAIZ, rel), encoding='utf-8').read()


def gravar(rel, texto, conferir, mudados):
    caminho = os.path.join(RAIZ, rel)
    antigo = open(caminho, encoding='utf-8').read() if os.path.isfile(caminho) else None
    if antigo != texto:
        mudados.append(rel)
        if not conferir:
            open(caminho, 'w', encoding='utf-8').write(texto)


def cabecalho(md):
    m = re.match(r'---\n(.*?)\n---\n', md, re.S)
    if not m:
        return {}, md
    dados = {}
    for linha in m.group(1).splitlines():
        if ':' in linha:
            k, v = linha.split(':', 1)
            dados[k.strip()] = v.strip()
    return dados, md[m.end():]


def em_linha(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    def link(m):
        alvo = m.group(2)
        if alvo.startswith(BASE):
            alvo = '/' + alvo[len(BASE):]
        return f'<a href="{html.escape(alvo)}">{m.group(1)}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, t)


def texto_puro(t):
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', t)


def blocos(corpo):
    """Quebra o Markdown em blocos: (tipo, conteúdo)."""
    saida, paragrafo, lista, tipo_lista = [], [], [], None
    def fechar():
        nonlocal paragrafo, lista, tipo_lista
        if paragrafo:
            saida.append(('p', ' '.join(paragrafo)))
            paragrafo = []
        if lista:
            saida.append((tipo_lista, lista))
            lista, tipo_lista = [], None
    for linha in corpo.splitlines():
        s = linha.strip()
        if not s:
            fechar()
            continue
        m = re.match(r'(#{1,3}) (.*)', s)
        if m:
            fechar()
            saida.append((f'h{len(m.group(1))}', m.group(2)))
            continue
        m = re.match(r'(-|\d+\.) (.*)', s)
        if m:
            if paragrafo:
                fechar()
            novo = 'ul' if m.group(1) == '-' else 'ol'
            if tipo_lista and tipo_lista != novo:
                fechar()
            tipo_lista = novo
            lista.append(m.group(2))
            continue
        if s.startswith('> '):
            fechar()
            saida.append(('blockquote', s[2:]))
            continue
        if s.startswith('|') and s.endswith('|'):
            celulas = [c.strip() for c in s.strip('|').split('|')]
            if all(re.fullmatch(r':?-{3,}:?', c) for c in celulas):
                continue
            if not saida or saida[-1][0] != 'table' or paragrafo or lista:
                fechar()
                saida.append(('table', []))
            saida[-1][1].append(celulas)
            continue
        if lista:
            lista[-1] += ' ' + s
        else:
            paragrafo.append(s)
    fechar()
    return saida


# "Leia também" no fim de cada página gerada (13/11/2026, auditoria de SEO): duas ou três vizinhas do
# mesmo assunto, para nenhuma página depender de um link só. O nome vem do campo `trilha` de cada uma.
RELACIONADAS = {
    'automacao-de-processos': ['cobranca-automatica', 'documento-automatico', 'sistemas-sob-medida'],
    'automacao-para-escritorio': ['documento-automatico', 'cobranca-automatica', 'automacao-de-processos'],
    'bling-omie-ou-sistema-sob-medida': ['erp-sob-medida-para-distribuidora', 'quanto-custa-um-sistema-sob-medida', 'sistema-para-substituir-planilhas'],
    'cobranca-automatica': ['automacao-de-processos', 'documento-automatico', 'lucro-por-produto'],
    'como-escolher-empresa-de-software-sob-medida': ['quanto-custa-um-sistema-sob-medida', 'bling-omie-ou-sistema-sob-medida', 'sistemas-sob-medida'],
    'consultoria-de-ia': ['consultoria-financeira', 'automacao-de-processos'],
    'consultoria-financeira': ['dre-gerencial-para-distribuidora', 'lucro-por-produto', 'consultoria-de-ia'],
    'documento-automatico': ['automacao-para-escritorio', 'cobranca-automatica', 'automacao-de-processos'],
    'dre-gerencial-para-distribuidora': ['lucro-por-produto', 'consultoria-financeira', 'sistema-para-distribuidora'],
    'erp-sob-medida-para-distribuidora': ['sistema-para-distribuidora', 'bling-omie-ou-sistema-sob-medida', 'sistema-de-pedidos-b2b'],
    'ficha-de-cliente-para-joalheria': ['sistemas-sob-medida', 'documento-automatico', 'automacao-de-processos'],
    'lucro-por-produto': ['dre-gerencial-para-distribuidora', 'sistema-para-distribuidora', 'consultoria-financeira'],
    'quanto-custa-um-sistema-sob-medida': ['como-escolher-empresa-de-software-sob-medida', 'bling-omie-ou-sistema-sob-medida', 'sistemas-sob-medida'],
    'sistema-de-pedidos-b2b': ['sistema-para-distribuidora', 'erp-sob-medida-para-distribuidora', 'cobranca-automatica'],
    'sistema-para-distribuidora': ['erp-sob-medida-para-distribuidora', 'sistema-para-distribuidora-de-alimentos', 'sistema-de-pedidos-b2b'],
    'sistema-para-distribuidora-de-alimentos': ['sistema-para-distribuidora', 'lucro-por-produto', 'dre-gerencial-para-distribuidora'],
    'sistema-para-substituir-planilhas': ['bling-omie-ou-sistema-sob-medida', 'como-escolher-empresa-de-software-sob-medida', 'automacao-de-processos'],
    'sistemas-sob-medida': ['como-escolher-empresa-de-software-sob-medida', 'quanto-custa-um-sistema-sob-medida', 'erp-sob-medida-para-distribuidora'],
}


def leia_tambem(pasta):
    itens = []
    for vizinha in RELACIONADAS.get(pasta, []):
        dados, _ = cabecalho(ler(os.path.join(vizinha, 'index.md')))
        itens.append(f'            <li><a href="/{vizinha}/">{html.escape(dados.get("trilha", vizinha))}</a></li>')
    if not itens:
        return ''
    return '\n        <h2>Leia também</h2>\n        <ul class="leia-tambem">\n' + '\n'.join(itens) + '\n        </ul>'


def montar(pasta, md, estilo):
    dados, corpo = cabecalho(md)
    url = BASE + pasta + '/'
    partes = blocos(corpo)
    h1 = next(c for t, c in partes if t == 'h1')

    # Perguntas: cada ### depois de "## Perguntas" com o parágrafo que vem logo abaixo.
    perguntas, dentro, pergunta = [], False, None
    for t, c in partes:
        if t == 'h2':
            dentro = c.lower().startswith('perguntas')
        elif dentro and t == 'h3':
            pergunta = c
        elif dentro and pergunta and t == 'p':
            perguntas.append((pergunta, texto_puro(c)))
            pergunta = None

    corpo_html = []
    for t, c in partes:
        if t in ('h1', 'h2', 'h3'):
            if t == 'h1':
                if dados.get('etiqueta'):
                    corpo_html.append(f'        <p class="etiqueta">{html.escape(dados["etiqueta"])}</p>')
                corpo_html.append(f'        <h1>{em_linha(c)}</h1>')
            else:
                corpo_html.append(f'\n        <{t}>{em_linha(c)}</{t}>')
        elif t == 'p':
            botao = re.fullmatch(r'\[([^\]]+)\]\((/conversar/[^)]*)\)', c)
            if botao:
                corpo_html.append(f'        <a class="botao" href="{html.escape(botao.group(2))}">{html.escape(botao.group(1))}</a>')
            else:
                corpo_html.append(f'        <p>{em_linha(c)}</p>')
        elif t == 'blockquote':
            corpo_html.append(f'        <blockquote>{em_linha(c)}</blockquote>')
        elif t == 'table':
            cab = ''.join(f'<th scope="col">{em_linha(x)}</th>' for x in c[0])
            # data-rotulo: no celular a tabela vira cartão, e cada célula mostra o nome da coluna antes.
            linhas = '\n'.join('            <tr><th scope="row">' + em_linha(r[0]) + '</th>' + ''.join(f'<td data-rotulo="{html.escape(texto_puro(c[0][i + 1]))}">{em_linha(x)}</td>' for i, x in enumerate(r[1:])) + '</tr>' for r in c[1:])
            corpo_html.append(f'        <div class="tabela"><table>\n            <thead><tr>{cab}</tr></thead>\n            <tbody>\n{linhas}\n            </tbody>\n        </table></div>')
        else:
            itens = '\n'.join(f'            <li>{em_linha(i)}</li>' for i in c)
            corpo_html.append(f'        <{t}>\n{itens}\n        </{t}>')
    corpo_html.append(leia_tambem(pasta))
    atualizado = dados.get('atualizado', '')
    if atualizado:
        a, m_, d = atualizado.split('-')
        corpo_html.insert(2, f'        <p class="suave">Atualizado em {d}/{m_}/{a}.</p>')

    grafo = [ORGANIZACAO, {
        '@type': dados.get('tipo_pagina', 'WebPage'),
        '@id': url + '#pagina',
        'url': url,
        'name': dados['titulo'],
        'description': dados['descricao'],
        'inLanguage': 'pt-BR',
        'isPartOf': {'@id': BASE + '#site'},
        'publisher': {'@id': BASE + '#organizacao'},
        'dateModified': atualizado,
        'breadcrumb': {'@id': url + '#trilha'},
    }, {
        '@type': 'BreadcrumbList',
        '@id': url + '#trilha',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Início', 'item': BASE},
            {'@type': 'ListItem', 'position': 2, 'name': dados.get('trilha', texto_puro(h1)), 'item': url},
        ],
    }]
    if dados.get('servico'):
        servico = {
            '@type': 'Service',
            '@id': url + '#servico',
            'name': dados['servico'],
            'serviceType': dados.get('tipo_servico', dados['servico']),
            'url': url,
            'provider': {'@id': BASE + '#organizacao'},
            'areaServed': {'@type': 'Country', 'name': 'Brasil'},
            'description': dados['descricao'],
        }
        if dados.get('publico'):
            servico['audience'] = {'@type': 'BusinessAudience', 'name': dados['publico']}
        grafo[1]['about'] = {'@id': url + '#servico'}
        grafo.append(servico)
    if perguntas:
        grafo.append({
            '@type': 'FAQPage',
            '@id': url + '#perguntas',
            'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in perguntas],
        })
    ld = json.dumps({'@context': 'https://schema.org', '@graph': grafo}, ensure_ascii=False, indent=2)
    titulo = html.escape(dados['titulo'])
    descricao = html.escape(dados['descricao'])
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Página gerada por execution/gerar_paginas.py a partir de {pasta}/index.md. Edite o .md e rode o script. -->
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
{PRELOAD}    <script type="application/ld+json">
{ld}
    </script>
    <style>{estilo}</style>
</head>
<body>
{topo()}
    <main id="conteudo">
{chr(10).join(corpo_html)}
    </main>
{rodape()}
    <!-- Contagem de visitas sem cookie e sem IP. -->
    <script src="/contagem.js" defer></script>
    <a class="conversa-fixa" href="/conversar/">Quero meu diagnóstico</a>
</body>
</html>
'''


def sitemap(lastmods):
    """Toda página canônica dela mesma entra, com os pares de idioma que ela declara."""
    entradas = []
    pastas = [''] + sorted(p for p in os.listdir(RAIZ) if os.path.isfile(os.path.join(RAIZ, p, 'index.html')))
    # As páginas de case moram um nível abaixo (cases/<nome>/), geradas por gerar_paginas_de_case.py.
    casos = os.path.join(RAIZ, 'cases')
    if os.path.isdir(casos):
        pastas += sorted('cases/' + p for p in os.listdir(casos) if os.path.isfile(os.path.join(casos, p, 'index.html')))
    for pasta in pastas:
        rel = (pasta + '/' if pasta else '') + 'index.html'
        pagina = ler(rel)
        url = BASE + (pasta + '/' if pasta else '')
        canonica = re.search(r'rel="canonical" href="([^"]+)"', pagina)
        if not canonica or canonica.group(1) != url or 'noindex' in pagina[:3000]:
            continue
        pares = re.findall(r'rel="alternate" hreflang="(pt-BR|en)" href="([^"]+)"', pagina)
        data = lastmods.get(url, '2026-10-30')
        if pares:
            linhas = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{u}"/>' for h, u in pares)
            entradas.append(f'  <url>\n    <loc>{url}</loc><lastmod>{data}</lastmod>{linhas}\n  </url>')
        else:
            entradas.append(f'  <url><loc>{url}</loc><lastmod>{data}</lastmod></url>')
    for extra in ('llms.txt', 'index.md'):
        entradas.append(f'  <url><loc>{BASE}{extra}</loc><lastmod>{lastmods.get(BASE + extra, "2026-10-30")}</lastmod></url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(entradas) + '\n</urlset>\n')


def main():
    conferir = '--conferir' in sys.argv
    estilo = re.search(r'<style>(.*?)</style>', ler('consultoria/index.html'), re.S).group(1)
    mudados = []
    lastmods = dict(re.findall(r'<loc>(.*?)</loc><lastmod>(.*?)</lastmod>', ler('sitemap.xml')))
    for pasta in sorted(os.listdir(RAIZ)):
        fonte = os.path.join(pasta, 'index.md')
        if not os.path.isfile(os.path.join(RAIZ, fonte)):
            continue
        md = ler(fonte)
        dados, _ = cabecalho(md)
        if dados.get('gerar') != 'sim':
            continue
        gravar(os.path.join(pasta, 'index.html'), montar(pasta, md, estilo), conferir, mudados)
        lastmods[BASE + pasta + '/'] = dados.get('atualizado', '2026-10-30')
    for pagina in MOLDE_A_MAO:
        rel = pagina if pagina.endswith('.html') else os.path.join(pagina, 'index.html')
        gravar(rel, vestir(ler(rel), estilo, trocar_estilo=pagina != 'consultoria'), conferir, mudados)
    gravar('sitemap.xml', sitemap(lastmods), conferir, mudados)
    if conferir:
        print('Desatualizado: ' + ', '.join(mudados) if mudados else 'Tudo gerado está em dia.')
        return 1 if mudados else 0
    print('Gravado: ' + (', '.join(mudados) if mudados else 'nada mudou'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
