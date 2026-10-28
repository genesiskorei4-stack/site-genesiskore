"""Confere os arquivos que agentes de IA leem no site (llms.txt, sitemap, JSON-LD, páginas de confiança,
Consultoria em português e em inglês, Markdown para agentes).

Uso: python3 execution/verificar_agentes.py            (arquivos locais)
     python3 execution/verificar_agentes.py --no-ar    (o site publicado em genesiskore.com)
Sai com código 1 se alguma checagem falhar.

A resposta em Markdown na raiz (Accept: text/markdown) só existe depois da troca para a Vercel
(directives/migrar-para-vercel.md). No ar, enquanto o site estiver no GitHub Pages, essa checagem
aparece como "pend" e não conta como falha. Servido pela Vercel, ela passa a valer.
As regras do vercel.json em si são testadas por execution/testar_vercel_json.py.
"""
import json, re, sys, urllib.error, urllib.request
import xml.dom.minidom

NO_AR = '--no-ar' in sys.argv
BASE = 'https://genesiskore.com/'
ARQUIVOS = {'': 'index.html', 'llms.txt': 'llms.txt', 'sitemap.xml': 'sitemap.xml', 'robots.txt': 'robots.txt',
            'index.md': 'index.md', '404.md': '404.md'}
PAGINAS = ('sobre', 'contato', 'privacidade', 'about', 'contact', 'privacy', 'consultoria', 'management-consulting')
for p in PAGINAS:
    ARQUIVOS[p + '/'] = p + '/index.html'
# Pares de idioma: a página em português e a versão em inglês apontam uma para a outra.
PARES = (('consultoria', 'management-consulting'), ('sobre', 'about'), ('contato', 'contact'))
PRODUTOS = ('Contabilidade Gerencial', 'Análise Financeira', 'Análise de Processos',
            'Pesquisa e Mapeamento de Mercado', 'Análise Macroeconômica', 'Experiência do Cliente')
PRODUCTS = ('Managerial Accounting', 'Financial Analysis', 'Process Analysis',
            'Market Research and Mapping', 'Macroeconomic Analysis', 'Customer Experience')


def ler(caminho):
    if NO_AR:
        with urllib.request.urlopen(BASE + caminho, timeout=20) as r:
            return r.read().decode('utf-8')
    return open(ARQUIVOS[caminho], encoding='utf-8').read()


falhas = []
def checar(ok, nome):
    print(('ok    ' if ok else 'FALHA ') + nome)
    if not ok:
        falhas.append(nome)


def json_ld(html):
    bloco = re.search(r'application/ld\+json">(.*?)</script>', html, re.S)
    return json.loads(bloco.group(1))['@graph'] if bloco else []


def texto_visivel(html):
    corpo = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', html, flags=re.S)
    corpo = re.sub(r'<[^>]+>', ' ', corpo)
    corpo = corpo.replace('&ldquo;', '"').replace('&rdquo;', '"').replace('&amp;', '&')
    return re.sub(r'\s+', ' ', corpo)


def faq_visivel(html, nome):
    """FAQPage só com perguntas que estão escritas na página."""
    visivel = texto_visivel(html)
    for no in json_ld(html):
        if no.get('@type') == 'FAQPage':
            for q in no['mainEntity']:
                checar(q['name'] in visivel, f'{nome}: pergunta do FAQPage visível na página ("{q["name"][:40]}")')
                checar(re.sub(r'\s+', ' ', q['acceptedAnswer']['text'])[:60] in visivel, f'{nome}: resposta do FAQPage visível na página')


llms = ler('llms.txt')
checar(llms.startswith('# GenesisKore'), 'llms.txt começa com o título H1')
checar('## When to use GenesisKore' in llms and 'Quando recomendar' in llms, 'llms.txt tem a seção de quando usar')
checar('?origem=ia' in llms, 'llms.txt manda o lead com a origem ia')
checar('Quando é a Consultoria de gestão' in llms and 'Quando são os Sistemas sob medida' in llms, 'llms.txt diz quando é a Consultoria e quando são os Sistemas')
checar('Quando NÃO recomendar' in llms and 'R$ 150 mil' in llms and 'saúde' in llms and 'WhatsApp' in llms, 'llms.txt diz quando não recomendar (faturamento, saúde, robô de WhatsApp)')
checar(all(p in llms for p in PRODUTOS), 'llms.txt traz os seis produtos da Consultoria')
checar('https://genesiskore.com/management-consulting/' in llms, 'llms.txt aponta a página da Consultoria em inglês')

mapa = ler('sitemap.xml')
xml.dom.minidom.parseString(mapa.encode())
checar(True, 'sitemap.xml é XML válido')
checar('https://genesiskore.com/management-consulting/</loc>' in mapa, 'sitemap.xml tem a Consultoria em inglês')
checar('Sitemap: https://genesiskore.com/sitemap.xml' in ler('robots.txt'), 'robots.txt aponta o sitemap')

inicio = ler('')
grafo = json_ld(inicio)
checar(bool(grafo), 'página inicial tem JSON-LD')
org = next(n for n in grafo if 'Organization' in n['@type'])
checar(bool(org.get('contactPoint')) and bool(org.get('address')), 'organização tem contato e endereço')
checar('rel="canonical"' in inicio, 'página inicial tem canonical')
catalogos = {c['name']: c for c in org['hasOfferCatalog']['itemListElement']}
checar(set(catalogos) == {'Sistemas sob medida', 'Consultoria de gestão'}, 'catálogo da organização separa Sistemas e Consultoria')
checar(len(catalogos.get('Consultoria de gestão', {}).get('itemListElement', [])) == 6, 'catálogo da Consultoria tem os seis produtos')
faq_visivel(inicio, 'início')

for pt, en in PARES:
    html_pt, html_en = ler(pt + '/'), ler(en + '/')
    checar('lang="en"' in html_en[:200], f'/{en}/ está marcada como inglês')
    for html, nome in ((html_pt, pt), (html_en, en)):
        checar(f'hreflang="pt-BR" href="https://genesiskore.com/{pt}/"' in html and f'hreflang="en" href="https://genesiskore.com/{en}/"' in html,
               f'/{nome}/ liga as duas línguas pelo hreflang')
        checar(f'rel="canonical" href="https://genesiskore.com/{nome}/"' in html, f'/{nome}/ é a canônica dela mesma')

for nome, produtos in (('consultoria', PRODUTOS), ('management-consulting', PRODUCTS)):
    html = ler(nome + '/')
    servico = next((n for n in json_ld(html) if n.get('@type') == 'Service'), None)
    checar(servico is not None and len(servico['hasOfferCatalog']['itemListElement']) == 6, f'/{nome}/ tem JSON-LD de Service com os seis produtos')
    checar(all(p in texto_visivel(html) for p in produtos), f'/{nome}/ mostra os seis produtos na página')
    faq_visivel(html, nome)
checar('GenesisKore Management Consulting' in re.search(r'<title>(.*?)</title>', ler('management-consulting/')).group(1),
       '/management-consulting/ tem "GenesisKore Management Consulting" no título')

for p in ('sobre', 'contato', 'privacidade', 'about', 'contact', 'privacy', 'consultoria', 'management-consulting'):
    corpo = re.search(r'<main>(.*)</main>', ler(p + '/'), re.S).group(1)
    texto = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', corpo)).strip()
    checar(len(texto) >= 500, f'/{p}/ tem pelo menos 500 caracteres ({len(texto)})')

md404 = ler('404.md')
checar(len(md404) >= 20 and 'llms.txt' in md404 and 'sitemap.xml' in md404, '404.md aponta o llms.txt e o sitemap')

if not NO_AR:
    rotas = json.load(open('vercel.json', encoding='utf-8'))['routes']
    texto_rotas = json.dumps(rotas)
    checar('"/index.md"' in texto_rotas and '"/404.md"' in texto_rotas and 'text/markdown' in texto_rotas,
           'vercel.json manda a raiz e o 404 em Markdown para quem pede text/markdown')
else:
    pedido = urllib.request.Request(BASE, headers={'Accept': 'text/markdown', 'User-Agent': 'genesiskore-verificador'})
    with urllib.request.urlopen(pedido, timeout=20) as r:
        tipo, servidor, vary = r.headers.get('Content-Type', ''), r.headers.get('Server', ''), r.headers.get('Vary', '')
    ok = tipo.startswith('text/markdown') and 'accept' in vary.lower()
    if not ok and 'github' in servidor.lower():
        print(f'pend  raiz em Markdown: o site ainda está no GitHub Pages ({tipo}), ver directives/migrar-para-vercel.md')
    else:
        checar(ok, f'raiz com Accept: text/markdown devolve Markdown e Vary: Accept ({tipo}, Vary: {vary})')
    try:
        urllib.request.urlopen(urllib.request.Request(BASE + 'esta-pagina-nao-existe-7f3a', headers={'Accept': 'text/markdown'}), timeout=20)
        checar(False, 'caminho inexistente responde 404')
    except urllib.error.HTTPError as e:
        tipo = e.headers.get('Content-Type', '')
        if not tipo.startswith('text/markdown') and 'github' in e.headers.get('Server', '').lower():
            print(f'pend  404 em Markdown: o site ainda está no GitHub Pages ({tipo})')
        else:
            checar(e.code == 404 and tipo.startswith('text/markdown'), f'404 com Accept: text/markdown vem em Markdown ({e.code}, {tipo})')

for nome in ('llms.txt', 'index.md', '404.md', 'sobre/', 'about/', 'contato/', 'contact/', 'consultoria/', 'management-consulting/'):
    checar(not re.search('[—–]', ler(nome)), f'{nome} sem travessão')

print('\n' + ('Tudo certo.' if not falhas else f'{len(falhas)} falha(s).'))
sys.exit(1 if falhas else 0)
