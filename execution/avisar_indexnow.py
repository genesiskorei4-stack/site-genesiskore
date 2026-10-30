"""Avisa o IndexNow (Bing, Yandex, Seznam, Naver e Yep) das páginas do site que mudaram.

O Bing é o índice do ChatGPT e do Copilot, então quanto antes ele souber de uma página nova,
antes ela pode aparecer numa resposta de IA. Roda sozinho no GitHub depois de cada push na main
(.github/workflows/indexnow.yml), com o Felipe de acordo desde 30/10/2026.

Uso:
  python3 execution/avisar_indexnow.py --antes <sha> --depois <sha>   só as páginas que o push mexeu
  python3 execution/avisar_indexnow.py --todas                        todas as do sitemap
  acrescente --so-mostrar para ver a lista sem enviar nada

A chave é pública por desenho: ela fica na raiz do site (7f7a9820d89718fb34d248743a09623f.txt)
para o IndexNow conferir que o aviso veio do dono do domínio.
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HOST = 'genesiskore.com'
BASE = f'https://{HOST}/'
CHAVE = '7f7a9820d89718fb34d248743a09623f'
ENDERECO = 'https://api.indexnow.org/indexnow'


def urls_do_sitemap():
    texto = (RAIZ / 'sitemap.xml').read_text(encoding='utf-8')
    return re.findall(r'<loc>([^<]+)</loc>', texto)


def url_do_arquivo(caminho):
    """De um arquivo do repositório para o endereço público, ou None se não for página."""
    if caminho in ('index.html', 'index.md'):
        return BASE
    m = re.match(r'^([a-z0-9-]+)/index\.(html|md)$', caminho)
    if m:
        return f'{BASE}{m.group(1)}/'
    if caminho == 'llms.txt':
        return f'{BASE}llms.txt'
    return None


def urls_mudadas(antes, depois):
    if not antes or set(antes) == {'0'}:
        return urls_do_sitemap()
    saida = subprocess.run(['git', 'diff', '--name-only', antes, depois], cwd=RAIZ,
                           capture_output=True, text=True, check=True).stdout
    no_sitemap = set(urls_do_sitemap())
    urls = []
    for caminho in saida.split():
        url = url_do_arquivo(caminho)
        if url and url in no_sitemap and url not in urls:
            urls.append(url)
    return urls


def enviar(urls):
    corpo = json.dumps({
        'host': HOST,
        'key': CHAVE,
        'keyLocation': f'{BASE}{CHAVE}.txt',
        'urlList': urls,
    }).encode('utf-8')
    pedido = urllib.request.Request(ENDERECO, data=corpo, method='POST',
                                    headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(pedido, timeout=30) as resposta:
            return resposta.status, resposta.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as erro:
        return erro.code, erro.read().decode('utf-8', 'replace')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--antes')
    p.add_argument('--depois', default='HEAD')
    p.add_argument('--todas', action='store_true')
    p.add_argument('--so-mostrar', action='store_true')
    a = p.parse_args()

    urls = urls_do_sitemap() if a.todas else urls_mudadas(a.antes, a.depois)
    if not urls:
        print('Nenhuma página mudou: nada para avisar.')
        return 0
    print(f'{len(urls)} endereço(s):')
    for u in urls:
        print('  ', u)
    if a.so_mostrar:
        return 0

    status, texto = enviar(urls)
    # 200 e 202 são aceitos. 422 quer dizer que algum endereço não é do host ou a chave não confere.
    print('IndexNow respondeu', status, texto[:300])
    return 0 if status in (200, 202) else 1


if __name__ == '__main__':
    sys.exit(main())
