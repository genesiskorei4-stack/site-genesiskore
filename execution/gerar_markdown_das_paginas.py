"""Gera o index.md das páginas escritas à mão e dos cases, a partir do <main> do index.html.

Uso: python3 execution/gerar_markdown_das_paginas.py            gera e grava
     python3 execution/gerar_markdown_das_paginas.py --conferir  só diz se algum .md está desatualizado (sai 1)

Por quê (13/11/2026, auditoria de GEO): 17 páginas tinham versão em Markdown para agentes de IA e 7
não tinham, entre elas o case da AUTH, que é a prova mais forte da casa. Nestas páginas a fonte é o
HTML (escrito à mão, ou gerado por gerar_paginas_de_case.py), então o Markdown sai dele e não o
contrário. Rodar depois de mexer em qualquer uma delas. O vercel.json entrega o .md a quem pede
`text/markdown`, igual às páginas geradas.
"""
import html, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://genesiskore.com/'
PAGINAS = ('sobre', 'contato', 'consultoria', 'management-consulting', 'about', 'contact', 'privacidade', 'privacy',
           'cases/auth', 'cases/fazenda-cca', 'cases/rastro')


def em_linha(t, pasta):
    """Links viram [texto](endereço absoluto); o resto das marcações sai."""
    def link(m):
        href, texto = m.group(1), limpar(m.group(2), pasta)
        if not texto:
            return ''
        if href.startswith(('http', 'mailto:')):
            alvo = href
        else:
            alvo = BASE + os.path.normpath(os.path.join(pasta, href)).lstrip('./').replace('\\', '/')
            if href.endswith('/') and not alvo.endswith('/'):
                alvo += '/'
            if alvo.endswith('/./') or alvo == BASE + '.':
                alvo = BASE
        return f'[{texto}]({alvo})'
    t = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', link, t, flags=re.S)
    t = re.sub(r'<(strong|b)>(.*?)</\1>', r'**\2**', t, flags=re.S)
    return limpar(t, pasta)


def limpar(t, pasta):
    t = re.sub(r'<br\s*/?>', ' ', t)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def markdown(pasta):
    pagina = open(os.path.join(RAIZ, pasta, 'index.html'), encoding='utf-8').read()
    titulo = limpar(re.search(r'<title>(.*?)</title>', pagina, re.S).group(1), pasta)
    descricao = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', pagina).group(1))
    main = re.search(r'<main[^>]*>(.*?)</main>', pagina, re.S).group(1)
    main = re.sub(r'<(script|style|video|figure|svg)\b.*?</\1>', '', main, flags=re.S)
    saida = [f'<!-- Gerado por execution/gerar_markdown_das_paginas.py a partir de {pasta}/index.html. -->',
             f'<!-- {titulo}. Página: {BASE}{pasta}/ -->', '']
    for m in re.finditer(r'<(h[1-3]|p|li|blockquote|tr)\b[^>]*>(.*?)</\1>', main, re.S):
        tag, corpo = m.group(1), m.group(2)
        if tag == 'tr':
            celulas = [em_linha(c, pasta) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', corpo, re.S)]
            primeira = not saida or not saida[-1].startswith('|')
            if primeira and saida and saida[-1] != '':
                saida.append('')
            saida.append('| ' + ' | '.join(celulas) + ' |')
            if primeira:  # a linha do cabeçalho pede a linha de traços embaixo
                saida.append('|' + '---|' * len(celulas))
            continue
        texto = em_linha(corpo, pasta)
        if not texto:
            continue
        if tag.startswith('h'):
            saida += ['', '#' * int(tag[1]) + ' ' + texto, '']
        elif tag == 'li':
            saida.append('- ' + texto)
        elif tag == 'blockquote':
            saida += ['', '> ' + texto, '']
        else:
            saida += [texto, '']
    if not any(l.startswith('# ') for l in saida):
        saida.insert(3, '# ' + titulo.split(' | ')[0])
    saida += ['', f'Resumo: {descricao}', '']
    texto = '\n'.join(saida)
    return re.sub(r'\n{3,}', '\n\n', texto).strip() + '\n'


def main():
    conferir = '--conferir' in sys.argv
    mudados = []
    for pasta in PAGINAS:
        novo = markdown(pasta)
        caminho = os.path.join(RAIZ, pasta, 'index.md')
        velho = open(caminho, encoding='utf-8').read() if os.path.exists(caminho) else ''
        if novo != velho:
            mudados.append(pasta + '/index.md')
            if not conferir:
                open(caminho, 'w', encoding='utf-8').write(novo)
    if conferir:
        print('Desatualizado: ' + ', '.join(mudados) if mudados else 'Markdown das páginas em dia.')
        return 1 if mudados else 0
    print('Gravado: ' + (', '.join(mudados) if mudados else 'nada mudou'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
