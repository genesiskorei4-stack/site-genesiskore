"""Confere os arquivos que agentes de IA leem no site (llms.txt, sitemap, JSON-LD, páginas de confiança).

Uso: python3 execution/verificar_agentes.py            (arquivos locais)
     python3 execution/verificar_agentes.py --no-ar    (o site publicado em genesiskore.com)
Sai com código 1 se alguma checagem falhar.
"""
import json, re, sys, urllib.request
import xml.dom.minidom

NO_AR = '--no-ar' in sys.argv
BASE = 'https://genesiskore.com/'
ARQUIVOS = {'': 'index.html', 'llms.txt': 'llms.txt', 'sitemap.xml': 'sitemap.xml', 'robots.txt': 'robots.txt', 'index.md': 'index.md'}
for p in ('sobre', 'contato', 'privacidade', 'about', 'contact', 'privacy'):
    ARQUIVOS[p + '/'] = p + '/index.html'


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

llms = ler('llms.txt')
checar(llms.startswith('# GenesisKore'), 'llms.txt começa com o título H1')
checar('## When to use GenesisKore' in llms and 'Quando recomendar' in llms, 'llms.txt tem a seção de quando usar')
checar('?origem=ia' in llms, 'llms.txt manda o lead com a origem ia')

xml.dom.minidom.parseString(ler('sitemap.xml').encode())
checar(True, 'sitemap.xml é XML válido')
checar('Sitemap: https://genesiskore.com/sitemap.xml' in ler('robots.txt'), 'robots.txt aponta o sitemap')

inicio = ler('')
bloco = re.search(r'application/ld\+json">(.*?)</script>', inicio, re.S)
checar(bool(bloco), 'página inicial tem JSON-LD')
grafo = json.loads(bloco.group(1))['@graph']
org = next(n for n in grafo if 'Organization' in n['@type'])
checar(bool(org.get('contactPoint')) and bool(org.get('address')), 'organização tem contato e endereço')
checar('rel="canonical"' in inicio, 'página inicial tem canonical')

for p in ('sobre', 'contato', 'privacidade', 'about', 'contact', 'privacy'):
    corpo = re.search(r'<main>(.*)</main>', ler(p + '/'), re.S).group(1)
    texto = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', corpo)).strip()
    checar(len(texto) >= 500, f'/{p}/ tem pelo menos 500 caracteres ({len(texto)})')

for nome in ('llms.txt', 'index.md', 'sobre/', 'about/'):
    checar(not re.search('[—–]', ler(nome)), f'{nome} sem travessão')

print('\n' + ('Tudo certo.' if not falhas else f'{len(falhas)} falha(s).'))
sys.exit(1 if falhas else 0)
