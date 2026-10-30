"""Nota de SEO e GEO do site, lida dos arquivos do repositório.

Uso: python3 execution/auditar_seo_geo.py                  (a pasta atual, que é o repositório)
     python3 execution/auditar_seo_geo.py --raiz <pasta>    (outra cópia do site, por exemplo a main antiga)
     python3 execution/auditar_seo_geo.py --json            (resultado em JSON, para comparar antes e depois)

O que ele confere, em quatro blocos que somam 100 pontos:
  1. Rastreio e indexação (25): robots.txt sem bloquear robô de busca nem de IA, sitemap só com
     página canônica e com todas elas, chave do IndexNow publicada.
  2. Entidade (20): os dados que dizem ao Google e às IAs quem é a empresa (Organization com
     nome alternativo, endereço, área atendida, redes, contato, sócios).
  3. Página por página (25): título e descrição no tamanho, um h1 só, canonical dela mesma,
     prévia de link, dados estruturados, trilha (BreadcrumbList) nas internas, sem travessão.
  4. Cobertura de intenção (30): para cada busca de execution/intencoes.json, existe uma página
     com os termos no título ou no h1. É o bloco que mais pesa porque, sem a página certa, nem o
     Google nem a IA têm o que citar.

Não acessa a internet. A indexação de verdade (quantas páginas o Google e o Bing têm) e a
resposta das IAs são medidas pela diretiva directives/medir-seo-geo.md.
"""
import argparse, html as htmllib, json, os, re, sys, unicodedata
import xml.dom.minidom

ROBOS_DE_BUSCA = ('Googlebot', 'Bingbot', 'OAI-SearchBot', 'ChatGPT-User', 'GPTBot', 'PerplexityBot',
                  'Perplexity-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'Google-Extended',
                  'Applebot', 'Applebot-Extended', 'DuckDuckBot')
NAO_INDEXAVEIS = {'404.html'}


def normalizar(texto):
    texto = unicodedata.normalize('NFKD', htmllib.unescape(texto)).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', texto.lower()).strip()


def sem_tags(trecho):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', trecho)).strip()


def json_ld(pagina):
    nos = []
    for bloco in re.findall(r'application/ld\+json">(.*?)</script>', pagina, re.S):
        dado = json.loads(bloco)
        nos.extend(dado.get('@graph', [dado]) if isinstance(dado, dict) else dado)
    return nos


def tipos(no):
    t = no.get('@type', [])
    return set(t if isinstance(t, list) else [t])


class Auditoria:
    def __init__(self, raiz):
        self.raiz = raiz
        self.itens = []  # (bloco, nome, ok, peso)

    def checar(self, bloco, nome, ok, peso=1):
        self.itens.append((bloco, nome, bool(ok), peso))

    def ler(self, relativo):
        caminho = os.path.join(self.raiz, relativo)
        return open(caminho, encoding='utf-8').read() if os.path.isfile(caminho) else None

    def paginas(self):
        """Páginas HTML que o site publica, com a URL que cada uma tem."""
        achadas = {}
        if os.path.isfile(os.path.join(self.raiz, 'index.html')):
            achadas['https://genesiskore.com/'] = 'index.html'
        for nome in sorted(os.listdir(self.raiz)):
            arquivo = os.path.join(nome, 'index.html')
            if nome.startswith('.') or nome in ('execution', 'directives'):
                continue
            if os.path.isfile(os.path.join(self.raiz, arquivo)):
                achadas[f'https://genesiskore.com/{nome}/'] = arquivo
        return achadas

    def rodar(self):
        paginas = self.paginas()
        conteudo = {url: self.ler(arq) for url, arq in paginas.items()}
        canonica = {}
        for url, pagina in conteudo.items():
            m = re.search(r'rel="canonical" href="([^"]+)"', pagina)
            canonica[url] = m.group(1) if m else None
        noindex = {url for url, p in conteudo.items() if re.search(r'name="robots"[^>]*noindex', p)}
        indexaveis = [u for u in conteudo if canonica[u] == u and u not in noindex]

        # 1. Rastreio e indexação
        robots = self.ler('robots.txt') or ''
        self.checar('rastreio', 'robots.txt existe e aponta o sitemap', 'Sitemap: https://genesiskore.com/sitemap.xml' in robots, 2)
        bloqueados = []
        agente_atual = []
        for linha in robots.splitlines():
            linha = linha.split('#', 1)[0].strip()
            if linha.lower().startswith('user-agent:'):
                agente_atual.append(linha.split(':', 1)[1].strip())
            elif linha.lower().startswith('disallow:'):
                if linha.split(':', 1)[1].strip() == '/':
                    bloqueados += agente_atual
            elif linha:
                agente_atual = [] if not linha.lower().startswith('allow') else agente_atual
        self.checar('rastreio', 'nenhum robô de busca ou de IA bloqueado no robots.txt',
                    not any(b == '*' or b in ROBOS_DE_BUSCA for b in bloqueados), 3)
        mapa = self.ler('sitemap.xml') or ''
        try:
            xml.dom.minidom.parseString(mapa.encode())
            mapa_ok = True
        except Exception:
            mapa_ok = False
        locs = set(re.findall(r'<loc>(.*?)</loc>', mapa))
        self.checar('rastreio', 'sitemap.xml válido', mapa_ok, 2)
        faltando = [u for u in indexaveis if u not in locs]
        self.checar('rastreio', f'sitemap tem todas as páginas indexáveis (faltam {len(faltando)}: {", ".join(faltando)[:120]})', not faltando, 4)
        nao_canonicas = [u for u in locs if u in canonica and canonica[u] != u]
        self.checar('rastreio', f'sitemap sem página que aponta canonical para outra ({", ".join(nao_canonicas)})', not nao_canonicas, 2)
        self.checar('rastreio', 'toda URL do sitemap tem data (lastmod)', mapa.count('<loc>') == mapa.count('<lastmod>'), 1)
        chave = None
        for nome in os.listdir(self.raiz):
            m = re.fullmatch(r'([0-9a-f]{32})\.txt', nome)
            if m and (self.ler(nome) or '').strip() == m.group(1):
                chave = m.group(1)
        self.checar('rastreio', 'chave do IndexNow publicada na raiz (avisa Bing e Yandex na hora)', chave, 4)
        llms = self.ler('llms.txt') or ''
        fora_do_llms = [u for u in indexaveis if u not in llms]
        self.checar('rastreio', f'llms.txt aponta todas as páginas indexáveis (faltam {len(fora_do_llms)})', not fora_do_llms, 3)
        md = [u for u in indexaveis if self.ler(u.replace('https://genesiskore.com/', '') + 'index.md') or u == 'https://genesiskore.com/' and self.ler('index.md')]
        self.checar('rastreio', f'versão em Markdown para agentes em pelo menos metade das páginas ({len(md)} de {len(indexaveis)})', len(md) * 2 >= len(indexaveis), 2)

        # 2. Entidade
        inicio = conteudo.get('https://genesiskore.com/', '')
        grafo = json_ld(inicio)
        org = next((n for n in grafo if 'Organization' in tipos(n)), {})
        self.checar('entidade', 'Organization na página inicial', org, 3)
        self.checar('entidade', 'nome alternativo para não confundir com homônimos (alternateName)', org.get('alternateName'), 3)
        self.checar('entidade', 'descrição da empresa (description)', len(org.get('description', '')) > 80, 2)
        self.checar('entidade', 'endereço e área atendida', org.get('address') and org.get('areaServed'), 2)
        self.checar('entidade', 'três redes ou mais em sameAs', len(org.get('sameAs', [])) >= 3, 2)
        self.checar('entidade', 'contato comercial (contactPoint)', org.get('contactPoint'), 2)
        self.checar('entidade', 'sócios ligados à empresa (founder ou member)', org.get('founder') or org.get('member'), 2)
        self.checar('entidade', 'data de fundação', org.get('foundingDate'), 1)
        self.checar('entidade', 'o que a empresa sabe fazer (knowsAbout)', len(org.get('knowsAbout', [])) >= 5, 1)
        self.checar('entidade', 'serviços descritos (hasOfferCatalog ou Service)', org.get('hasOfferCatalog') or any('Service' in tipos(n) for n in grafo), 2)

        # 3. Página por página
        titulos, descricoes = {}, {}
        por_pagina = []
        for url in indexaveis:
            p = conteudo[url]
            t = re.search(r'<title>(.*?)</title>', p, re.S)
            d = re.search(r'name="description"\s+content="(.*?)"', p, re.S)
            t = htmllib.unescape(t.group(1).strip()) if t else ''
            d = htmllib.unescape(d.group(1).strip()) if d else ''
            titulos.setdefault(t, []).append(url)
            descricoes.setdefault(d, []).append(url)
            h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', p, re.S)
            nos = json_ld(p)
            visivel = sem_tags(re.sub(r'<script.*?</script>|<style.*?</style>', ' ', p, flags=re.S))
            ok = {
                'título de 30 a 65 caracteres': 30 <= len(t) <= 65,
                'descrição de 70 a 165 caracteres': 70 <= len(d) <= 165,
                'um h1 só': len(h1s) == 1,
                'prévia de link (og:title e og:image)': 'og:title' in p and 'og:image' in p,
                'dados estruturados': bool(nos),
                'trilha (BreadcrumbList) nas internas': url == 'https://genesiskore.com/' or any('BreadcrumbList' in tipos(n) for n in nos),
                'sem travessão no texto': not re.search('[—–]', visivel),
                'pelo menos 300 palavras': len(visivel.split()) >= 300,
            }
            por_pagina.append((url, ok))
        total = sum(len(ok) for _, ok in por_pagina) or 1
        passaram = sum(sum(ok.values()) for _, ok in por_pagina)
        self.itens.append(('pagina', f'checagens por página ({passaram} de {total})', passaram / total, 20))
        repetidos = [t for t, us in titulos.items() if len(us) > 1] + [d for d, us in descricoes.items() if len(us) > 1]
        self.checar('pagina', 'nenhum título ou descrição repetido entre páginas', not repetidos, 5)

        # 4. Cobertura de intenção
        mapa_int = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'intencoes.json'), encoding='utf-8'))['intencoes']
        alvos = {}
        for url in indexaveis:
            p = conteudo[url]
            t = re.search(r'<title>(.*?)</title>', p, re.S)
            h1 = re.search(r'<h1[^>]*>(.*?)</h1>', p, re.S)
            alvos[url] = normalizar((t.group(1) if t else '') + ' | ' + sem_tags(h1.group(1) if h1 else ''))
        cobertura = []
        for it in mapa_int:
            candidatas = [u for u in alvos if not it.get('pagina_propria') or u != 'https://genesiskore.com/']
            def bate(texto):
                if 'todos' in it:
                    return all(normalizar(x) in texto for x in it['todos'])
                return any(normalizar(x) in texto for x in it['algum'])
            achou = [u for u in candidatas if bate(alvos[u])]
            cobertura.append((it['id'], it['busca'], achou))
        cobertas = sum(1 for _, _, a in cobertura if a)
        self.itens.append(('intencao', f'buscas com página própria ({cobertas} de {len(cobertura)})', cobertas / len(cobertura), 30))

        return {'indexaveis': indexaveis, 'por_pagina': por_pagina, 'cobertura': cobertura}

    def nota(self):
        pesos = {'rastreio': 25, 'entidade': 20, 'pagina': 25, 'intencao': 30}
        resultado = {}
        for bloco, teto in pesos.items():
            itens = [i for i in self.itens if i[0] == bloco]
            soma = sum(p for *_, p in itens) or 1
            feito = sum((ok if isinstance(ok, float) else (1 if ok else 0)) * p for _, _, ok, p in itens)
            resultado[bloco] = round(teto * feito / soma, 1)
        resultado['total'] = round(sum(resultado.values()), 1)
        return resultado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raiz', default='.')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    aud = Auditoria(os.path.abspath(a.raiz))
    detalhe = aud.rodar()
    nota = aud.nota()
    if a.json:
        print(json.dumps({'nota': nota, 'itens': [(b, n, ok if isinstance(ok, float) else bool(ok)) for b, n, ok, _ in aud.itens],
                          'cobertura': detalhe['cobertura'], 'paginas': detalhe['indexaveis']}, ensure_ascii=False, indent=1))
        return
    nomes = {'rastreio': 'Rastreio e indexação', 'entidade': 'Entidade', 'pagina': 'Página por página', 'intencao': 'Cobertura de intenção'}
    for bloco in nomes:
        print(f'\n{nomes[bloco]}: {nota[bloco]}')
        for b, n, ok, _ in aud.itens:
            if b == bloco:
                marca = f'{ok:.0%}' if isinstance(ok, float) else ('ok  ' if ok else 'FALTA')
                print(f'  {marca:5} {n}')
    print('\nPáginas e o que falta em cada uma:')
    for url, ok in detalhe['por_pagina']:
        faltas = [k for k, v in ok.items() if not v]
        print(f'  {url}: {"tudo certo" if not faltas else "; ".join(faltas)}')
    print('\nBuscas e a página que responde:')
    for _, busca, achou in detalhe['cobertura']:
        print(f'  {"ok   " if achou else "FALTA"} {busca}: {", ".join(achou) if achou else "nenhuma página"}')
    print(f'\nNota: {nota["total"]} de 100')


if __name__ == '__main__':
    sys.exit(main())
