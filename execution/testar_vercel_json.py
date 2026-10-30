"""Testa as regras do vercel.json: Markdown na raiz e 404 em Markdown para quem pede text/markdown.

Uso: python3 execution/testar_vercel_json.py
         Sobe um servidor local que lê o vercel.json e imita o roteamento da Vercel (routes, has,
         headers, continue, status, dest e handle filesystem) em cima dos arquivos do repositório.
     python3 execution/testar_vercel_json.py --url https://site-genesiskore.vercel.app
         Roda as mesmas checagens contra um endereço publicado (depois da troca, ou num endereço
         .vercel.app antes de mexer no DNS).
Sai com código 1 se alguma checagem falhar.

Por que imitar em vez de rodar `vercel dev`: a própria documentação da Vercel diz que o `has`
não funciona no `vercel dev`, só no deploy. E o `vercel dev` pede login. O imitador cobre só o
pedaço do roteamento que o vercel.json desta pasta usa; regra nova de outro tipo precisa entrar
aqui também, e o teste avisa se encontrar uma chave que não conhece.
"""
import json, mimetypes, os, re, sys, threading, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAVES_CONHECIDAS = {'src', 'dest', 'headers', 'continue', 'status', 'has', 'handle'}
mimetypes.add_type('text/markdown', '.md')


def casa_has(condicoes, cabecalhos):
    """Confere as condições `has` do tipo header. Valor: texto (regex inteira) ou {re, pre, suf, eq}."""
    for c in condicoes or []:
        if c.get('type') != 'header':
            raise ValueError(f'tipo de has não imitado: {c}')
        valor = cabecalhos.get(c['key'].lower())
        if valor is None:
            return False
        esperado = c.get('value')
        if esperado is None:
            continue
        if isinstance(esperado, str):
            if not re.fullmatch(esperado, valor):
                return False
            continue
        if 're' in esperado and not re.search(esperado['re'], valor):
            return False
        if 'pre' in esperado and not valor.startswith(esperado['pre']):
            return False
        if 'suf' in esperado and not valor.endswith(esperado['suf']):
            return False
        if 'eq' in esperado and valor != esperado['eq']:
            return False
    return True


def arquivo_de(caminho):
    """Como a Vercel acha o arquivo estático: /x/ vira /x/index.html, / vira /index.html."""
    relativo = caminho.lstrip('/')
    if relativo == '' or relativo.endswith('/'):
        relativo += 'index.html'
    completo = os.path.normpath(os.path.join(RAIZ, relativo))
    if not completo.startswith(RAIZ) or not os.path.isfile(completo):
        return None
    return completo


def rotear(caminho, cabecalhos, rotas):
    """Devolve (status, cabeçalhos, arquivo ou None)."""
    juntos = {}
    antes, depois = [], []
    lista = antes
    for r in rotas:
        if set(r) - CHAVES_CONHECIDAS:
            raise ValueError(f'chave de rota não imitada: {set(r) - CHAVES_CONHECIDAS}')
        if r.get('handle') == 'filesystem':
            lista = depois
            continue
        if 'handle' in r:
            raise ValueError(f'fase não imitada: {r["handle"]}')
        lista.append(r)

    destino = caminho
    for r in antes:
        m = re.fullmatch(r['src'].lstrip('^').rstrip('$'), caminho)
        if not m or not casa_has(r.get('has'), cabecalhos):
            continue
        for k, v in r.get('headers', {}).items():
            juntos[k] = m.expand(v.replace('$', '\\'))
        if 'status' in r and 'dest' not in r:
            return r['status'], juntos, None
        if 'dest' in r:
            # A Vercel troca $1, $2 do destino pelos grupos do src, como nos cabeçalhos.
            destino = m.expand(r['dest'].replace('$', '\\'))
        if not r.get('continue'):
            break

    arquivo = arquivo_de(destino)
    if arquivo:
        return 200, juntos, arquivo

    for r in depois:
        m = re.fullmatch(r['src'].lstrip('^').rstrip('$'), caminho)
        if not m or not casa_has(r.get('has'), cabecalhos):
            continue
        juntos.update(r.get('headers', {}))
        return r.get('status', 200), juntos, arquivo_de(r['dest']) if 'dest' in r else None
    return 404, juntos, None


def servidor_local():
    rotas = json.load(open(os.path.join(RAIZ, 'vercel.json'), encoding='utf-8'))['routes']

    class Atendente(BaseHTTPRequestHandler):
        def do_GET(self):
            caminho = self.path.split('?', 1)[0]
            cabecalhos = {k.lower(): v for k, v in self.headers.items()}
            status, extras, arquivo = rotear(caminho, cabecalhos, rotas)
            corpo = open(arquivo, 'rb').read() if arquivo else b''
            self.send_response(status)
            tipo = mimetypes.guess_type(arquivo)[0] if arquivo else 'text/plain'
            if tipo and tipo.startswith('text/'):
                tipo += '; charset=utf-8'
            if not any(k.lower() == 'content-type' for k in extras):
                self.send_header('Content-Type', tipo or 'application/octet-stream')
            for k, v in extras.items():
                self.send_header(k, v)
            self.send_header('Content-Length', str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def log_message(self, *args):
            pass

    srv = ThreadingHTTPServer(('127.0.0.1', 0), Atendente)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f'http://127.0.0.1:{srv.server_address[1]}'


class SemSeguirRedirecionamento(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


abrir = urllib.request.build_opener(SemSeguirRedirecionamento).open


def pedir(base, caminho, accept):
    req = urllib.request.Request(base + caminho, headers={'Accept': accept, 'User-Agent': 'genesiskore-teste-vercel-json'})
    try:
        with abrir(req, timeout=20) as r:
            return r.status, r.headers, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode('utf-8', 'replace')


falhas = []
def checar(ok, nome):
    print(('ok    ' if ok else 'FALHA ') + nome)
    if not ok:
        falhas.append(nome)


def main():
    if '--url' in sys.argv:
        base = sys.argv[sys.argv.index('--url') + 1].rstrip('/')
        srv = None
    else:
        srv, base = servidor_local()
    print(f'Testando {base}\n')

    MD = 'text/markdown'
    HTML = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    INEXISTENTE = '/esta-pagina-nao-existe-7f3a'

    s, h, corpo = pedir(base, '/', MD)
    checar(s == 200, f'raiz com Accept: text/markdown responde 200 ({s})')
    checar(h.get('Content-Type', '').startswith('text/markdown'), f'raiz em Markdown vem com Content-Type text/markdown ({h.get("Content-Type")})')
    checar('accept' in h.get('Vary', '').lower(), f'raiz em Markdown vem com Vary: Accept ({h.get("Vary")})')
    checar(corpo.startswith('# GenesisKore') and len(corpo) > 500, 'raiz em Markdown traz o index.md de verdade')

    s, h, corpo = pedir(base, '/', HTML)
    checar(s == 200, f'raiz com Accept de navegador responde 200 ({s})')
    checar(h.get('Content-Type', '').startswith('text/html'), f'raiz para navegador continua HTML ({h.get("Content-Type")})')
    checar('accept' in h.get('Vary', '').lower(), f'raiz em HTML também vem com Vary: Accept ({h.get("Vary")})')
    checar('<!DOCTYPE html>' in corpo[:200], 'raiz para navegador é a página inicial')

    s, h, corpo = pedir(base, INEXISTENTE, MD)
    checar(s == 404, f'caminho inexistente com text/markdown responde 404 ({s})')
    checar(h.get('Content-Type', '').startswith('text/markdown'), f'404 para agente vem em Markdown ({h.get("Content-Type")})')
    checar(len(corpo) >= 20 and 'llms.txt' in corpo and 'sitemap.xml' in corpo, '404 em Markdown aponta para o llms.txt e o sitemap')

    s, h, corpo = pedir(base, INEXISTENTE, HTML)
    checar(s == 404, f'caminho inexistente para navegador responde 404 ({s})')
    checar(h.get('Content-Type', '').startswith('text/html') and 'Página não encontrada' in corpo, '404 para navegador é a página 404.html')

    s, h, _ = pedir(base, '/index.md', HTML)
    checar(s == 200 and h.get('Content-Type', '').startswith('text/markdown'), f'/index.md direto vem como text/markdown ({h.get("Content-Type")})')

    s, h, _ = pedir(base, '/consultoria', HTML)
    checar(s in (301, 308) and h.get('Location', '').endswith('/consultoria/'), f'/consultoria sem barra redireciona para /consultoria/ ({s} {h.get("Location")})')

    # Páginas geradas de um index.md (30/10/2026): agente que pede Markdown recebe o .md, navegador recebe o HTML.
    s, h, corpo = pedir(base, '/sistemas-sob-medida/', MD)
    checar(s == 200 and h.get('Content-Type', '').startswith('text/markdown') and '# Sistemas sob medida' in corpo,
           f'/sistemas-sob-medida/ com Accept: text/markdown devolve o index.md ({s}, {h.get("Content-Type")})')
    s, h, corpo = pedir(base, '/sistemas-sob-medida/', HTML)
    checar(s == 200 and h.get('Content-Type', '').startswith('text/html') and 'accept' in h.get('Vary', '').lower(),
           f'/sistemas-sob-medida/ para navegador é HTML com Vary: Accept ({s}, {h.get("Content-Type")}, {h.get("Vary")})')

    for pagina in ('/consultoria/', '/management-consulting/', '/conversar/', '/llms.txt', '/sitemap.xml', '/styles.css',
                   '/7f7a9820d89718fb34d248743a09623f.txt'):
        s, _, _ = pedir(base, pagina, HTML)
        checar(s == 200, f'{pagina} continua respondendo 200 ({s})')

    if srv:
        # Pasta com página nova e fora da lista de redirecionamento quebra os links relativos dela.
        regra = json.load(open(os.path.join(RAIZ, 'vercel.json'), encoding='utf-8'))['routes'][0]['src']
        for nome in sorted(os.listdir(RAIZ)):
            if os.path.isfile(os.path.join(RAIZ, nome, 'index.html')):
                checar(re.fullmatch(regra.lstrip('^').rstrip('$'), '/' + nome) is not None, f'/{nome} está na regra que põe a barra no fim')
        srv.shutdown()

    print('\n' + ('Tudo certo.' if not falhas else f'{len(falhas)} falha(s).'))
    sys.exit(1 if falhas else 0)


if __name__ == '__main__':
    main()
