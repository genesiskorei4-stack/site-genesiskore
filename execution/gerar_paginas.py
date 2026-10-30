"""Gera as páginas de conteúdo do site a partir de um Markdown, e refaz o sitemap.

Uso: python3 execution/gerar_paginas.py            gera e grava
     python3 execution/gerar_paginas.py --conferir  só diz se algo gerado está desatualizado (sai 1)

De onde sai cada coisa:
- `<pasta>/index.md` com `gerar: sim` no cabeçalho é a fonte. Ele mesmo é publicado e é a versão
  em Markdown que os agentes de IA leem (o vercel.json entrega quando pedem `text/markdown`).
- `<pasta>/index.html` é montado daqui: o visual vem do <style> de consultoria/index.html, para
  todas as páginas secundárias ficarem iguais. Não edite o HTML gerado à mão; edite o .md e rode.
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
    'url': BASE,
    'logo': BASE + 'logo.png',
    'email': 'contato@genesiskore.com',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'São Paulo', 'addressRegion': 'SP', 'addressCountry': 'BR'},
}


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
        if lista:
            lista[-1] += ' ' + s
        else:
            paragrafo.append(s)
    fechar()
    return saida


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
        else:
            itens = '\n'.join(f'            <li>{em_linha(i)}</li>' for i in c)
            corpo_html.append(f'        <{t}>\n{itens}\n        </{t}>')
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
    nav = '<a href="/sistemas-sob-medida/">Sistemas</a><a href="/consultoria/">Consultoria</a><a href="/sobre/">Sobre</a><a href="/contato/">Contato</a>'
    rodape = ('<a href="/">Início</a><a href="/sistemas-sob-medida/">Sistemas sob medida</a><a href="/consultoria/">Consultoria de gestão</a>'
              '<a href="/sobre/">Sobre</a><a href="/contato/">Contato</a><a href="/privacidade/">Privacidade</a>')
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Página gerada por execution/gerar_paginas.py a partir de {pasta}/index.md. Edite o .md e rode o script. -->
    <title>{titulo}</title>
    <meta name="description" content="{descricao}">
    <meta name="theme-color" content="#000000">
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
    <script type="application/ld+json">
{ld}
    </script>
    <style>{estilo}</style>
</head>
<body>
    <header>
        <a href="/" class="marca" aria-label="GenesisKore, página inicial"><img src="/logo.png" alt="" width="40" height="44"><span>GENESISKORE</span></a>
        <nav aria-label="Páginas">{nav}</nav>
    </header>
    <main>
{chr(10).join(corpo_html)}
    </main>
    <footer>
        {rodape}
        <p>© 2026 GenesisKore. Sistemas sob medida e consultoria de gestão. São Paulo, atendimento remoto em todo o Brasil.</p>
    </footer>
    <!-- Contagem de visitas sem cookie e sem IP. -->
    <script src="/contagem.js" defer></script>
</body>
</html>
'''


def sitemap(lastmods):
    """Toda página canônica dela mesma entra, com os pares de idioma que ela declara."""
    entradas = []
    pastas = [''] + sorted(p for p in os.listdir(RAIZ) if os.path.isfile(os.path.join(RAIZ, p, 'index.html')))
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
    gravar('sitemap.xml', sitemap(lastmods), conferir, mudados)
    if conferir:
        print('Desatualizado: ' + ', '.join(mudados) if mudados else 'Tudo gerado está em dia.')
        return 1 if mudados else 0
    print('Gravado: ' + (', '.join(mudados) if mudados else 'nada mudou'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
