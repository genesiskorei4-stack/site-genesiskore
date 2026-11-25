"""Base do desenho das plantas do site: traço branco sobre o azul, com peças reaproveitadas (celular,
notebook, galpão, caminhão). Usada por plantas_de_setor.py. Não roda sozinha."""
import os

AZ = '#120A8F'
DEFS = ('<defs><linearGradient id="parede" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".13"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity=".02"/></linearGradient>'
        '<radialGradient id="esm" cx=".5" cy=".5" r=".62"><stop offset=".55" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>'
        '<mask id="esmaece" maskContentUnits="objectBoundingBox"><rect x="0" y="0" width="1" height="1" fill="url(#esm)"/></mask></defs>')


class D:
    def __init__(s):
        s.L = []

    def a(s, t):
        s.L.append(t)

    def ln(s, x1, y1, x2, y2, w=1.6, op=1, extra=''):
        s.a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#fff" stroke-width="{w}" opacity="{op}" stroke-linecap="round"{extra}/>')

    def rc(s, x, y, w, h, sw=1.6, rx=0, op=1, fill='none'):
        if fill == 'none' and sw >= 1.8 and w * h > 20000:
            fill = 'url(#parede)'      # volume: parede grande ganha um sombreado leve
        s.a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="#fff" stroke-width="{sw}" opacity="{op}"/>')

    def ci(s, cx, cy, r, sw=1.6, op=1, fill='none'):
        s.a(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="#fff" stroke-width="{sw}" opacity="{op}"/>')

    def pl(s, pts, sw=1.6, op=1, fill='none', close=False):
        tag = 'polygon' if close else 'polyline'
        p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        s.a(f'<{tag} points="{p}" fill="{fill}" stroke="#fff" stroke-width="{sw}" opacity="{op}" stroke-linejoin="round"/>')

    def tx(s, x, y, t, anc='start', sz=12, op=.9, cls='rotulo', fam='JetBrains Mono,monospace', ls=2.2, peso=500):
        s.a(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anc}" font-family="{fam}" font-size="{sz}" font-weight="{peso}" letter-spacing="{ls}" fill="#fff" opacity="{op}">{t}</text>')

    def g(s, x, y, k=1):
        s.a(f'<g transform="translate({x},{y}) scale({k})">')

    def fg(s):
        s.a('</g>')

    def roda(s, cx, cy, r):
        s.ci(cx, cy, r, 1.8, 1, AZ)
        s.ci(cx, cy, r * .55, 1.2, .9)
        s.ci(cx, cy, r * .16, 1.2, .9, '#fff')
        for k in range(6):
            import math
            an = k * math.pi / 3
            s.ln(cx + math.cos(an) * r * .2, cy + math.sin(an) * r * .2, cx + math.cos(an) * r * .5, cy + math.sin(an) * r * .5, .8, .6)

    def seta(s, x1, y1, x2, y2, rot=''):
        s.ln(x1, y1, x2, y2, 1.4, .9, ' stroke-dasharray="6 6"')
        import math
        an = math.atan2(y2 - y1, x2 - x1)
        for d in (2.6, -2.6):
            s.ln(x2, y2, x2 - 12 * math.cos(an + d / 6), y2 - 12 * math.sin(an + d / 6), 1.4, .95)
        if rot:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            s.tx(mx, my - 10 if y1 == y2 else my, rot, 'middle', 11, .75)

    def numero(s, cx, cy, n, r=13):
        s.a(f'<g class="numero"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="#fff"/>'
            f'<text x="{cx:.1f}" y="{cy + r * .38:.1f}" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="{r * 1.05:.1f}" font-weight="700" fill="{AZ}">{n}</text></g>')

    def grade(s, w, h, passo=40):
        s.a('<g mask="url(#esmaece)">')
        s.a(f'<rect x="0" y="0" width="{w}" height="{h}" fill="none"/>')
        for x in range(passo, w, passo):
            s.ln(x, 0, x, h, .6, .08)
        for y in range(passo, h, passo):
            s.ln(0, y, w, y, .6, .08)
        s.a('</g>')

    def carimbo(s, x, y, titulo):
        s.a('<g class="rotulo">')
        s.rc(x, y, 270, 84, 1.2)
        s.ln(x, y + 26, x + 270, y + 26, 1, .7)
        s.ln(x, y + 54, x + 270, y + 54, 1, .7)
        s.ln(x + 196, y + 54, x + 196, y + 84, 1, .7)
        s.a('</g>')
        s.tx(x + 12, y + 18, 'GENESISKORE', sz=11)
        s.tx(x + 12, y + 45, titulo, sz=10, op=.8)
        s.tx(x + 12, y + 74, 'DESENHO ILUSTRATIVO', sz=9, op=.7, ls=1.6)
        s.tx(x + 233, y + 74, 'S/ESC', 'middle', 9, .7, ls=1.4)

    def svg(s, vb, rotulo):
        return (f'<svg viewBox="{vb}" role="img" aria-label="{rotulo}" style="width:100%;height:auto;display:block;overflow:visible">' + DEFS + ''.join(s.L) + '</svg>')


# ------------------------------------------------------------------ planta 01: a empresa
def arvore(d, x, chao, alt=150):
    d.ln(x, chao, x, chao - alt * .45, 1.6)
    d.ln(x, chao - alt * .32, x - 14, chao - alt * .5, 1.1, .8)
    d.ln(x, chao - alt * .38, x + 16, chao - alt * .55, 1.1, .8)
    for dx, dy, r in ((0, -.72, .26), (-.17, -.6, .2), (.18, -.62, .21), (-.08, -.86, .18), (.1, -.84, .17)):
        d.ci(x + dx * alt, chao + dy * alt, r * alt, 1.2, .85, AZ)


def pessoa(d, x, chao, k=1):
    h = 46 * k
    d.ci(x, chao - h + 5 * k, 4.6 * k, 1.3)
    d.ln(x, chao - h + 10 * k, x, chao - h * .42, 1.6)
    d.ln(x, chao - h * .42, x - 5 * k, chao, 1.4)
    d.ln(x, chao - h * .42, x + 5 * k, chao, 1.4)
    d.ln(x, chao - h * .78, x - 7 * k, chao - h * .48, 1.3)
    d.ln(x, chao - h * .78, x + 8 * k, chao - h * .5, 1.3)


def escritorio(d, x0, chao):
    w, topo = 280, chao - 230
    d.rc(x0 - 6, topo - 9, w + 12, 9, 1.4)                      # platibanda
    d.rc(x0, topo, w, 230, 2)
    meio = topo + 115
    d.ln(x0, meio, x0 + w, meio, 1.4)
    # andar de cima: pele de vidro
    d.rc(x0 + 16, topo + 16, w - 32, 86, 1.4)
    for i in range(1, 8):
        d.ln(x0 + 16 + i * (w - 32) / 8, topo + 16, x0 + 16 + i * (w - 32) / 8, topo + 102, 1, .8)
    d.ln(x0 + 16, topo + 44, x0 + w - 16, topo + 44, 1, .7)
    for i in (1, 4, 6):
        bx = x0 + 16 + i * (w - 32) / 8
        d.ln(bx + 6, topo + 92, bx + 22, topo + 56, .8, .35)
        d.ln(bx + 14, topo + 96, bx + 26, topo + 70, .8, .25)
    # térreo: vitrine, porta e marquise
    d.rc(x0 + 16, meio + 16, 104, 84, 1.4)
    for i in range(1, 3):
        d.ln(x0 + 16 + i * 104 / 3, meio + 16, x0 + 16 + i * 104 / 3, meio + 100, 1, .8)
    d.rc(x0 + 136, meio + 26, 62, chao - meio - 26, 1.6)
    d.ln(x0 + 167, meio + 26, x0 + 167, chao, 1.2, .9)
    d.ln(x0 + 160, meio + 70, x0 + 160, meio + 86, 1.8)
    d.ln(x0 + 174, meio + 70, x0 + 174, meio + 86, 1.8)
    d.rc(x0 + 126, meio + 14, 82, 6, 1.2)
    d.ln(x0 + 132, meio + 20, x0 + 140, meio + 30, 1, .7)
    d.ln(x0 + 202, meio + 20, x0 + 194, meio + 30, 1, .7)
    d.rc(x0 + 214, meio + 16, 50, 84, 1.4)
    d.ln(x0 + 239, meio + 16, x0 + 239, meio + 100, 1, .8)
    # ar condicionado no telhado
    d.rc(x0 + 30, topo - 34, 56, 25, 1.3)
    d.ci(x0 + 58, topo - 21.5, 8, 1, .8)
    d.rc(x0 + 190, topo - 26, 40, 17, 1.3)
    for i in range(4):
        d.ln(x0 + 196 + i * 9, topo - 22, x0 + 196 + i * 9, topo - 13, .8, .6)
    return x0 + w


def galpao(d, x0, chao, dentes=10, docas=4):
    passo = 74
    w = dentes * passo
    topo = chao - 260
    d.rc(x0, topo, w, 260, 2)
    # telhado em dente de serra, com as telhas e o vidro
    for i in range(dentes):
        x = x0 + i * passo
        d.pl([(x, topo), (x + passo, topo - 82), (x + passo, topo)], 1.8)
        for k in range(1, 5):
            t = k / 5
            d.ln(x + passo * t, topo - 82 * t, x + passo * t, topo, .7, .3)
        d.ln(x + passo - 3, topo - 72, x + passo - 3, topo - 4, .9, .6)
    d.ln(x0, topo + 28, x0 + w, topo + 28, 1.2, .8)
    # zona da esquerda: placa, janelas e porta de pessoas
    zona = 200
    for x in range(int(x0) + 8, int(x0 + zona), 7):
        d.ln(x, topo + 30, x, chao - 2, .6, .16)
    d.rc(x0 + 22, topo + 48, zona - 44, 54, 1.6, 0, 1, AZ)
    d.tx(x0 + zona / 2, topo + 74, 'SUA EMPRESA', 'middle', 15, 1, 'placa', ls=4, peso=600)
    d.tx(x0 + zona / 2, topo + 92, 'DISTRIBUIDORA', 'middle', 9, .75, 'placa', ls=3)
    for i in range(3):
        d.rc(x0 + 26 + i * 52, topo + 128, 38, 30, 1.3, 0, 1, AZ)
        d.ln(x0 + 45 + i * 52, topo + 128, x0 + 45 + i * 52, topo + 158, .8, .7)
    d.rc(x0 + 120, chao - 82, 44, 82, 1.6, 0, 1, AZ)
    d.ci(x0 + 156, chao - 40, 2, 1.2, 1, '#fff')
    d.rc(x0 + 114, chao - 90, 56, 6, 1.1)
    # zona das docas
    dx0 = x0 + zona + 10
    dw = w - zona - 20
    plat = chao - 58
    for x in range(int(dx0), int(x0 + w - 6), 7):
        d.ln(x, topo + 30, x, topo + 64, .6, .16)
    d.ln(dx0 - 6, topo + 70, x0 + w - 4, topo + 70, 1.6)                     # cobertura
    for i in range(docas + 1):
        bx = dx0 + i * dw / docas
        d.ln(bx, topo + 70, bx + (14 if i < docas else -14), topo + 92, .9, .7)
    d.rc(dx0 - 10, plat, dw + 16, 58, 1.8)                                   # plataforma
    for x in range(int(dx0 - 4), int(dx0 + dw), 11):
        d.ln(x, plat + 6, x + 6, plat + 14, .6, .25)
    # escada da plataforma
    for k in range(4):
        d.pl([(dx0 - 10 - k * 12, plat + k * 14.5), (dx0 - 22 - k * 12, plat + k * 14.5), (dx0 - 22 - k * 12, plat + (k + 1) * 14.5)], 1.2, .9)
    d.ln(dx0 - 10, plat - 30, dx0 - 58, plat + 28, 1, .7)
    porta_w = dw / docas - 26
    for i in range(docas):
        px = dx0 + 13 + i * dw / docas
        d.rc(px - 6, topo + 98, porta_w + 12, plat - topo - 98, 1.2, 0, .8)  # vedação
        d.rc(px, topo + 104, porta_w, plat - topo - 104, 1.6, 0, 1, AZ)
        aberta = i == 2
        fim = topo + 104 + ((plat - topo - 104) * .45 if aberta else plat - topo - 104)
        y = topo + 112
        while y < fim - 2:
            d.ln(px + 4, y, px + porta_w - 4, y, .8, .55)
            y += 9
        if aberta:
            # dentro da doca aberta: estante com caixas
            for lv in range(2):
                yy = fim + 12 + lv * 34
                d.ln(px + 6, yy + 26, px + porta_w - 6, yy + 26, 1, .8)
                for bx in range(3):
                    d.rc(px + 10 + bx * (porta_w - 20) / 3, yy + 6, (porta_w - 20) / 3 - 4, 20, 1, .8)
        d.rc(px - 4, plat - 20, 7, 18, 1.1, 1)                               # para choques
        d.rc(px + porta_w - 3, plat - 20, 7, 18, 1.1, 1)
        d.ln(px + 10, plat, px + porta_w - 10, plat, 2.2, .9)                # nivelador
    # palete com caixas e empilhadeira na plataforma
    pxp = dx0 + 3 * dw / docas - 30
    d.rc(pxp, plat - 8, 64, 8, 1.2)
    for c in range(2):
        for r in range(2):
            d.rc(pxp + 4 + c * 29, plat - 34 - r * 26, 27, 26, 1.2, 0, 1, AZ)
            d.ln(pxp + 4 + c * 29, plat - 21 - r * 26, pxp + 31 + c * 29, plat - 21 - r * 26, .7, .5)
    ex = dx0 + dw / docas + 8
    d.pl([(ex, plat - 10), (ex, plat - 40), (ex + 20, plat - 40), (ex + 30, plat - 26), (ex + 48, plat - 26), (ex + 48, plat - 10)], 1.4, 1, AZ, True)
    d.pl([(ex + 6, plat - 40), (ex + 6, plat - 70), (ex + 36, plat - 70), (ex + 40, plat - 40)], 1.2, .9)
    d.ln(ex + 52, plat - 4, ex + 52, plat - 82, 1.6)
    d.ln(ex + 58, plat - 4, ex + 58, plat - 82, 1, .7)
    d.ln(ex + 52, plat - 4, ex + 84, plat - 4, 1.6)
    d.ci(ex + 12, plat - 7, 7, 1.4, 1, AZ)
    d.ci(ex + 40, plat - 7, 7, 1.4, 1, AZ)
    pessoa(d, ex + 18, plat - 40, .55)
    pessoa(d, dx0 + 2.5 * dw / docas + 10, plat, .95)
    return x0 + w, (dx0 + 13 + 0.5 * dw / docas, topo + 160), (x0 + zona / 2, topo + 75)


def caminhao(d, x0, chao):
    bau = (x0, chao - 170, 250, 136)
    d.rc(*bau, 1.8)
    for x in range(int(x0) + 10, int(x0 + 250), 12):
        d.ln(x, chao - 164, x, chao - 40, .6, .3)
    d.ln(x0 + 6, chao - 160, x0 + 6, chao - 40, 1, .7)
    d.rc(x0 - 4, chao - 36, 258, 10, 1.4)                                     # chassi
    d.rc(x0 - 8, chao - 30, 6, 16, 1.2)
    d.ln(x0 + 250, chao - 30, x0 + 268, chao - 30, 1.4)
    # cabine
    cx = x0 + 262
    d.pl([(cx, chao - 26), (cx, chao - 138), (cx + 54, chao - 138), (cx + 84, chao - 96), (cx + 88, chao - 26)], 1.8, 1, AZ, True)
    d.pl([(cx + 50, chao - 130), (cx + 76, chao - 96), (cx + 50, chao - 96)], 1.3, .95, 'none', True)
    d.rc(cx + 8, chao - 130, 34, 30, 1.3)
    d.ln(cx + 8, chao - 92, cx + 44, chao - 92, 1, .7)
    d.rc(cx + 4, chao - 134, 44, 104, 1.1, 0, .7)
    d.ln(cx + 34, chao - 82, cx + 42, chao - 82, 1.6)
    for k in range(5):
        d.ln(cx + 82, chao - 86 + k * 9, cx + 88, chao - 86 + k * 9, .9, .7)
    d.rc(cx + 78, chao - 36, 16, 12, 1.2)
    d.ci(cx + 84, chao - 94, 3.5, 1, .8, '#fff')
    d.ln(cx + 52, chao - 134, cx + 58, chao - 150, 1.2)
    d.rc(cx + 56, chao - 156, 6, 16, 1)
    d.ln(cx - 6, chao - 138, cx - 6, chao - 172, 1.6)                       # escapamento
    d.rc(cx + 10, chao - 40, 30, 14, 1.1)                                    # tanque
    for wx in (x0 + 36, x0 + 80, x0 + 200, cx + 58):
        d.roda(wx, chao - 16, 16)
    return (x0 + 130, chao - 100)


def chamada(d, px, py, lx, ly, n, texto, lado=1):
    d.a('<g class="rotulo">')
    d.ln(px, py, lx, ly, 1.1, .85)
    d.ln(lx, ly, lx + 210 * lado, ly, 1.1, .85)
    d.a('</g>')
    d.numero(px, py, n)
    d.tx(lx + (34 if lado > 0 else -34), ly - 9, texto, 'start' if lado > 0 else 'end', 12, .95)
    d.a(f'<g class="rotulo"><circle cx="{lx + 14 * lado:.1f}" cy="{ly - 13:.1f}" r="9" fill="none" stroke="#fff" stroke-width="1.1"/>'
        f'<text x="{lx + 14 * lado:.1f}" y="{ly - 9:.1f}" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="10" font-weight="700" fill="#fff">{n}</text></g>')


def chao_linha(d, x1, x2, chao):
    d.ln(x1, chao, x2, chao, 2)
    for x in range(int(x1) + 8, int(x2), 22):
        d.ln(x, chao, x - 9, chao + 11, .8, .3)
    d.ln(x1, chao + 30, x2, chao + 30, .8, .35)
    x = x1
    while x < x2 - 30:
        d.ln(x, chao + 54, x + 30, chao + 54, 1, .3)
        x += 60


def planta01_pc():
    d = D()
    d.grade(1600, 760)
    chao = 590
    chao_linha(d, 40, 1560, chao)
    arvore(d, 92, chao, 150)
    arvore(d, 1574, chao, 110)
    fim_esc = escritorio(d, 150, chao)
    fim_g, doca, placa = galpao(d, fim_esc, chao, 10, 4)
    cam = caminhao(d, 1196, chao)
    pessoa(d, 530, chao, 1)
    # cota de cima e cota lateral
    d.ln(150, 190, fim_g, 190, 1, .75)
    for x in (150, fim_g):
        d.ln(x, 182, x, 198, 1, .75)
    for x in range(150, int(fim_g) + 1, 37):
        d.ln(x, 187, x, 193, .8, .4)
    d.tx((150 + fim_g) / 2, 174, 'A SUA OPERAÇÃO, DESENHADA', 'middle', 12, .85)
    d.ln(118, chao - 230, 118, chao, 1, .6)
    d.ln(110, chao - 230, 126, chao - 230, 1, .6)
    d.ln(110, chao, 126, chao, 1, .6)
    # chamadas
    chamada(d, doca[0], doca[1], 640, 680, 1, 'O PEDIDO ENTRA SOZINHO')
    chamada(d, 260, chao - 190, 190, 680, 2, 'A NOTA SAI SOZINHA')
    chamada(d, cam[0], cam[1], 1180, 680, 3, 'A ENTREGA NO PRAZO')
    # escala e norte
    d.a('<g class="rotulo">')
    for k in range(4):
        d.rc(40 + k * 30, 724, 30, 6, 1, 0, .8, '#fff' if k % 2 == 0 else 'none')
    d.a('</g>')
    d.tx(170, 731, 'SEM ESCALA', sz=9, op=.7, ls=1.6)
    d.a('<g class="rotulo">')
    d.ci(1265, 82, 20, 1.1, .8)
    d.pl([(1265, 58), (1259, 88), (1265, 82), (1271, 88)], 1.2, 1, '#fff', True)
    d.a('</g>')
    d.tx(1265, 120, 'N', 'middle', 10, .8)
    d.carimbo(1300, 40, 'PLANTA 01 · A OPERAÇÃO')
    return d.svg('0 0 1600 760', 'Desenho técnico ilustrativo de uma distribuidora: escritório, galpão com docas e caminhão, com o pedido, a nota e a entrega acontecendo sozinhos')


def planta01_cel():
    d = D()
    d.grade(1000, 520)
    chao = 450
    chao_linha(d, -40, 1040, chao)
    arvore(d, 18, chao, 120)
    fim_esc = escritorio(d, 40, chao)
    fim_g, doca, placa = galpao(d, fim_esc, chao, 7, 3)
    cam = caminhao(d, fim_g + 28, chao)
    d.numero(doca[0], doca[1], 1, 24)
    d.numero(150, chao - 190, 2, 24)
    d.numero(min(cam[0], 960), cam[1], 3, 24)
    return d.svg('0 88 1000 418', 'Desenho técnico ilustrativo de uma distribuidora').replace('overflow:visible','overflow:hidden')



CENA = dict(hora='07:02', sigla='SB', contato='Supermercado', sub='cliente desde 2024',
            b1=['Bom dia! Manda para amanhã:', '12 cx molho zero', '6 cx tempero de pipoca'], h1='07:01',
            b2=['Pedido 1873 registrado.', 'Entrega amanhã até 10h.'], b3=['Perfeito, obrigado!'], l3=120,
            tela='Pedidos de hoje', cards=[('Pedidos', '38'), ('Faturado', 'R$ 41.327'), ('Atrasados', '0')],
            grafico='Pedidos por hora',
            linhas=[('1873', 'Emitida'), ('1872', 'Separado'), ('1871', 'Entregue'), ('1870', 'Entregue'), ('1869', 'Pago')])

# ------------------------------------------------------------------ planta 02: o caminho do pedido
def celular(d, x, y, k=1):
    d.g(x, y, k)
    d.rc(0, 0, 236, 480, 2.2, 40)
    d.rc(9, 9, 218, 462, 1.2, 32, .8)
    d.rc(88, 20, 60, 18, 1.2, 9, 1, '#fff')
    d.ln(-2, 110, -2, 150, 3); d.ln(238, 130, 238, 190, 3); d.ln(-2, 165, -2, 205, 3)
    d.tx(32, 34, CENA['hora'], sz=11, op=.9, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=600)
    for i in range(4):
        d.rc(166 + i * 5, 30 - i * 2.5, 3, 4 + i * 2.5, .8, 0, .9, '#fff')
    d.rc(190, 24, 20, 10, 1, 2)
    d.rc(192, 26, 13, 6, 0, 1, .9, '#fff')
    # cabeçalho da conversa
    d.ln(9, 82, 227, 82, 1, .6)
    d.pl([(30, 56), (22, 64), (30, 72)], 1.4)
    d.ci(54, 64, 13, 1.3)
    d.tx(54, 68, CENA['sigla'], 'middle', 9, .9, 'tela', ls=0, peso=700)
    d.tx(74, 61, CENA['contato'], sz=12, op=1, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=600)
    d.tx(74, 75, CENA['sub'], sz=9, op=.7, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=400)
    # balões
    def balao(bx, by, bw, linhas, direita=False, fill='none'):
        h = 26 + len(linhas) * 15
        d.rc(bx, by, bw, h, 1.2, 10, 1, fill)
        for i, t in enumerate(linhas):
            d.tx(bx + 10, by + 19 + i * 15, t, sz=10.5, op=.95, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=400)
        return by + h
    yb = balao(20, 100, 168, CENA['b1'])
    d.tx(180, yb - 6, CENA['h1'], 'end', 8, .6, 'tela', ls=0)
    yb = balao(56, yb + 12, 160, CENA['b2'], fill='rgba(255,255,255,.14)')
    d.pl([(190, yb - 11), (194, yb - 7), (202, yb - 15)], 1.2)
    d.tx(184, yb - 6, CENA['hora'], 'end', 8, .6, 'tela', ls=0)
    yb = balao(20, yb + 12, CENA['l3'], CENA['b3'])
    # barra de digitar
    d.rc(18, 418, 160, 34, 1.2, 17)
    d.tx(34, 439, 'Mensagem', sz=10, op=.55, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=400)
    d.ci(200, 435, 17, 1.3)
    d.rc(196, 426, 8, 13, 1.1, 4)
    d.ln(200, 441, 200, 445, 1.1)
    d.fg()


def notebook(d, x, y, k=1):
    d.g(x, y, k)
    d.rc(0, 0, 560, 350, 2.2, 14)
    d.rc(14, 16, 532, 318, 1.2, 3, .8)
    d.ci(280, 8, 2.5, 1, .9, '#fff')
    # barra lateral
    d.ln(76, 16, 76, 334, 1, .5)
    d.rc(30, 30, 30, 30, 1.3, 7)
    d.tx(45, 50, 'SE', 'middle', 9, .9, 'tela', ls=0, peso=700)
    for i in range(5):
        d.rc(36, 84 + i * 40, 18, 16, 1.1, 3, .9 if i == 1 else .55)
    d.rc(28, 116, 36, 32, 1, 6, .35, 'rgba(255,255,255,.08)')
    # topo
    d.tx(96, 46, CENA['tela'], sz=15, op=1, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=600)
    d.tx(96, 62, 'terça, 24 de novembro', sz=10, op=.6, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=400)
    d.rc(440, 32, 90, 26, 1.2, 4)
    d.tx(485, 49, 'Exportar', 'middle', 10, .85, 'tela', 'Inter Tight,sans-serif', 0, 500)
    # cartões
    cards = CENA['cards']
    for i, (a, b) in enumerate(cards):
        cx = 96 + i * 148
        d.rc(cx, 76, 136, 62, 1.2, 6)
        d.tx(cx + 12, 96, a, sz=10, op=.65, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=400)
        d.tx(cx + 12, 124, b, sz=19, op=1, cls='tela', fam='Inter Tight,sans-serif', ls=-.4, peso=600)
    # gráfico
    d.rc(96, 150, 284, 168, 1.2, 6)
    d.tx(108, 170, CENA['grafico'], sz=10, op=.75, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=500)
    for i in range(4):
        d.ln(108, 200 + i * 28, 368, 200 + i * 28, .7, .25)
    vals = [10, 26, 18, 42, 36, 58, 48, 70, 62, 84]
    pts = [(116 + i * 27.5, 300 - v) for i, v in enumerate(vals)]
    d.pl(pts + [(pts[-1][0], 300), (pts[0][0], 300)], 0, 1, 'rgba(255,255,255,.10)', True)
    d.pl(pts, 1.8)
    for p_ in pts[::3]:
        d.ci(p_[0], p_[1], 3, 1, 1, '#fff')
    # tabela
    d.rc(392, 150, 138, 168, 1.2, 6)
    d.tx(404, 170, 'Últimos', sz=10, op=.75, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=500)
    linhas = CENA['linhas']
    for i, (a, b) in enumerate(linhas):
        yy = 194 + i * 25
        d.ln(404, yy + 8, 518, yy + 8, .6, .25)
        d.tx(404, yy, a, sz=9.5, op=.9, cls='tela', ls=.5)
        d.tx(518, yy, b, 'end', 9, .7, 'tela', 'Inter Tight,sans-serif', 0, 400)
    # base
    d.pl([(-34, 350), (594, 350), (606, 368), (-46, 368)], 2, 1, AZ, True)
    d.rc(232, 350, 96, 6, 1, 3)
    d.ln(-40, 362, 600, 362, .8, .4)
    d.fg()


def danfe(d, x, y, k=1):
    d.g(x, y, k)
    d.pl([(0, 0), (150, 0), (176, 26), (176, 230), (0, 230)], 1.8, 1, AZ, True)
    d.pl([(150, 0), (150, 26), (176, 26)], 1.3)
    d.rc(10, 10, 60, 38, 1.1)
    d.tx(40, 34, 'DANFE', 'middle', 10, 1, 'tela', ls=1, peso=700)
    d.tx(78, 24, 'NF-e 4.812', sz=8.5, op=.95, cls='tela', ls=.3)
    d.tx(80, 40, 'SÉRIE 1', sz=8, op=.7, cls='tela', ls=.6)
    xb = 12
    larg = [2, 1, 3, 1, 1, 2, 1, 3, 2, 1, 1, 2, 3, 1, 2, 1, 1, 3, 1, 2, 2, 1, 3, 1, 1, 2, 1, 2, 3, 1, 1, 2, 1, 3, 1, 2, 1, 1, 2, 3]
    for i, w_ in enumerate(larg):
        if i % 2 == 0:
            d.rc(xb, 58, w_, 30, 0, 0, .95, '#fff')
        xb += w_ + 1.2
        if xb > 164:
            break
    for i in range(5):
        yy = 104 + i * 18
        d.ln(10, yy, 166, yy, .7, .5)
        d.ln(18, yy + 9, 18 + (90 if i % 2 else 120), yy + 9, 1, .45)
    d.ln(110, 104, 110, 194, .7, .5)
    d.rc(10, 200, 156, 22, 1.1)
    d.tx(18, 215, 'TOTAL', sz=8, op=.75, cls='tela', ls=.8)
    d.tx(158, 215, 'R$ 1.286,40', 'end', 9, 1, 'tela', ls=.3, peso=700)
    d.fg()


def estante(d, x, y, k=1):
    d.g(x, y, k)
    for xx in (0, 220):
        d.rc(xx, 0, 10, 230, 1.6, 0, 1, AZ)
        for yy in range(10, 225, 14):
            d.ci(xx + 5, yy, 1.4, .8, .8)
    for yy in (70, 150, 230):
        d.rc(10, yy - 8, 210, 8, 1.4, 0, 1, AZ)
    caixas = [(16, 20, 56, 42), (76, 30, 64, 32), (146, 22, 66, 40),
              (16, 98, 90, 44), (112, 108, 48, 34), (166, 96, 46, 46),
              (16, 176, 60, 46), (82, 186, 70, 36), (158, 180, 54, 42)]
    for i, (cx, cy, cw, ch) in enumerate(caixas):
        destaque = i == 4
        d.rc(cx, cy, cw, ch, 1.8 if destaque else 1.2, 0, 1, 'rgba(255,255,255,.16)' if destaque else AZ)
        d.ln(cx + cw / 2, cy, cx + cw / 2, cy + 8, .8, .6)
        d.rc(cx + 6, cy + ch - 14, 20, 9, .8, 0, .8)
        if destaque:
            d.ci(cx + cw - 2, cy - 2, 9, 1.4, 1, AZ)
            d.pl([(cx + cw - 7, cy - 2), (cx + cw - 3, cy + 2), (cx + cw + 3, cy - 6)], 1.4)
    d.ln(-20, 238, 250, 238, 1.4)
    d.fg()


def furgao(d, x, y, k=1):
    d.g(x, y, k)
    d.pl([(0, 112), (0, 18), (6, 10), (178, 10), (200, 14), (236, 58), (258, 72), (262, 112)], 1.8, 1, AZ, True)
    d.pl([(186, 20), (224, 62), (186, 62)], 1.3, 1, 'none', True)
    d.ln(178, 12, 178, 112, 1.1, .8)
    d.ln(96, 12, 96, 112, 1.1, .7)
    d.rc(110, 20, 54, 34, 1.2)
    d.ln(200, 76, 210, 76, 1.6)
    d.rc(250, 84, 12, 10, 1, 2, .9, '#fff')
    d.tx(48, 64, 'ENTREGA', 'middle', 11, .95, 'tela', ls=2.5, peso=600)
    d.ln(18, 76, 80, 76, .8, .5)
    d.rc(254, 100, 14, 12, 1.2)
    for wx in (52, 206):
        d.roda(wx, 112, 19)
    d.ln(-20, 131, 290, 131, 1.4)
    d.fg()


def planta02_pc():
    d = D()
    d.grade(1600, 760)
    celular(d, 70, 150, .92)
    d.numero(70 + 236 * .92 + 6, 150 - 4, 1)
    d.seta(300, 372, 418, 372, '07:02')
    notebook(d, 470, 186, 1)
    d.numero(470 + 560 + 10, 186 - 6, 2)
    # ramificação para as três saídas
    d.ln(1060, 360, 1110, 360, 1.4, .9, ' stroke-dasharray="6 6"')
    d.ln(1110, 200, 1110, 590, 1.4, .9, ' stroke-dasharray="6 6"')
    d.seta(1110, 200, 1162, 200, '')
    d.seta(1110, 392, 1162, 392, '')
    d.seta(1110, 590, 1162, 590, '')
    d.tx(1136, 190, '07:03', 'middle', 10, .7)
    d.tx(1136, 382, '07:04', 'middle', 10, .7)
    d.tx(1136, 580, '07:40', 'middle', 10, .7)
    danfe(d, 1176, 128, .66)
    estante(d, 1176, 318, .66)
    furgao(d, 1176, 530, .7)
    d.numero(1176 + 176 * .66 + 8, 128, 3)
    d.numero(1176 + 230 * .66 + 14, 318, 4)
    d.numero(1176 + 262 * .7 + 8, 530, 5)
    d.tx(1376, 206, 'A NOTA SAI', sz=12)
    d.tx(1376, 398, 'O ESTOQUE SEPARA', sz=12)
    d.tx(1376, 596, 'A ENTREGA SAI', sz=12)
    d.tx(70 + 118 * .92, 620, 'O PEDIDO CHEGA', 'middle', 12)
    d.tx(750, 620, 'O SISTEMA DA SUA EMPRESA REGISTRA', 'middle', 12)
    # cota
    d.ln(70, 110, 1030, 110, 1, .75)
    for xx in (70, 1030):
        d.ln(xx, 102, xx, 118, 1, .75)
    for xx in range(70, 1031, 40):
        d.ln(xx, 107, xx, 113, .8, .4)
    d.tx(550, 94, 'UM PEDIDO, DO WHATSAPP À ENTREGA', 'middle', 12, .85)
    d.a('<g class="rotulo">')
    for k in range(4):
        d.rc(70 + k * 30, 724, 30, 6, 1, 0, .8, '#fff' if k % 2 == 0 else 'none')
    d.a('</g>')
    d.tx(200, 731, 'SEM ESCALA', sz=9, op=.7, ls=1.6)
    d.carimbo(1300, 24, 'PLANTA 02 · O CAMINHO')
    return d.svg('0 0 1600 760', 'Desenho técnico ilustrativo do caminho de um pedido: chega pelo WhatsApp, o sistema registra, e sai a nota, o estoque separado e a entrega')


def planta02_cel():
    d = D()
    d.grade(1000, 980)
    celular(d, 30, 40, .9)
    d.numero(30 + 236 * .9, 40, 1, 26)
    d.seta(254, 260, 312, 260)
    notebook(d, 340, 110, .108 * 6)
    d.numero(340 + 560 * .648, 110, 2, 26)
    base = 110 + 368 * .648
    d.ln(660, base + 30, 660, 560, 1.4, .9, ' stroke-dasharray="6 6"')
    d.ln(150, 560, 850, 560, 1.4, .9, ' stroke-dasharray="6 6"')
    for xx in (150, 500, 850):
        d.seta(xx, 560, xx, 612)
    danfe(d, 150 - 176 * .95 / 2, 630, .95)
    estante(d, 500 - 230 * .95 / 2, 630, .95)
    furgao(d, 820 - 262 * .95 / 2, 730, .95)
    d.numero(150 + 176 * .95 / 2 + 4, 630, 3, 26)
    d.numero(500 + 230 * .95 / 2 + 8, 630, 4, 26)
    d.numero(820 + 262 * .95 / 2 - 6, 722, 5, 26)
    return d.svg('0 0 1000 876', 'Desenho técnico ilustrativo do caminho de um pedido').replace('overflow:visible','overflow:hidden')


# ------------------------------------------------------------------ planta 03: qualquer empresa
CENA3 = dict(hora='09:12', sigla='NC', contato='Novo cliente', sub='chegou pelo site',
             b1=['Oi! Preciso de um orçamento', 'para começar no dia 2.', 'Vocês conseguem?'], h1='09:11',
             b2=['Recebido! A proposta chega', 'no seu email em minutos.'], b3=['Ótimo, obrigado!'], l3=112,
             tela='Solicitações de hoje', cards=[('Novas', '14'), ('A receber', 'R$ 41.327'), ('Atrasadas', '0')],
             grafico='Solicitações por dia',
             linhas=[('312', 'Proposta'), ('311', 'Assinada'), ('310', 'Andamento'), ('309', 'Paga'), ('308', 'Paga')])


def proposta(d, x, y, k=1):
    d.g(x, y, k)
    d.pl([(0, 0), (150, 0), (176, 26), (176, 230), (0, 230)], 1.8, 1, AZ, True)
    d.pl([(150, 0), (150, 26), (176, 26)], 1.3)
    d.tx(14, 30, 'PROPOSTA', sz=11, op=1, cls='tela', ls=1.4, peso=700)
    d.tx(14, 46, 'Nº 312', sz=9, op=.75, cls='tela', ls=.6)
    for i in range(6):
        yy = 66 + i * 15
        d.ln(14, yy, 14 + (148 if i % 3 else 120), yy, 1, .45)
    d.rc(14, 160, 148, 20, 1, 0, .8)
    d.tx(22, 174, 'TOTAL', sz=8, op=.75, cls='tela', ls=.8)
    d.tx(156, 174, 'R$ 4.800,00', 'end', 9, 1, 'tela', ls=.3, peso=700)
    # assinatura
    d.a('<path d="M 24 210 C 34 194, 44 222, 56 204 S 74 196, 84 210 S 100 214, 112 200" fill="none" stroke="#fff" stroke-width="1.5"/>')
    d.ln(18, 216, 120, 216, 1, .6)
    d.ci(150, 208, 12, 1.4, 1, AZ)
    d.pl([(144, 208), (148, 212), (156, 203)], 1.6)
    d.fg()


def quadro(d, x, y, k=1):
    d.g(x, y, k)
    d.rc(0, 0, 240, 200, 1.8, 10, 1, AZ)
    nomes = ['A FAZER', 'FAZENDO', 'FEITO']
    for c in range(3):
        cx = 10 + c * 76
        d.tx(cx + 33, 22, nomes[c], 'middle', 8, .8, 'tela', ls=1.2, peso=700)
        n = (3, 2, 3)[c]
        for r in range(n):
            cy = 34 + r * 52
            destaque = (c == 0 and r == 0)
            d.rc(cx, cy, 66, 44, 1.6 if destaque else 1.1, 4, 1, 'rgba(255,255,255,.16)' if destaque else AZ)
            d.ln(cx + 8, cy + 14, cx + 54, cy + 14, 1, .7)
            d.ln(cx + 8, cy + 24, cx + 40, cy + 24, .8, .45)
            d.ci(cx + 54, cy + 34, 5, 1, .9)
            if c == 2:
                d.pl([(cx + 8, cy + 34), (cx + 12, cy + 38), (cx + 19, cy + 30)], 1.2)
    d.fg()


def cobranca(d, x, y, k=1):
    d.g(x, y, k)
    d.rc(0, 0, 180, 230, 1.8, 12, 1, AZ)
    d.tx(14, 28, 'COBRANÇA', sz=10, op=1, cls='tela', ls=1.4, peso=700)
    d.tx(14, 44, 'vence dia 05', sz=9, op=.7, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=400)
    # código Pix ilustrativo
    import random
    random.seed(7)
    ox, oy, m = 46, 58, 6
    for i in range(14):
        for j in range(14):
            canto = (i < 4 and j < 4) or (i < 4 and j > 9) or (i > 9 and j < 4)
            if canto:
                continue
            if random.random() < .5:
                d.rc(ox + i * m, oy + j * m, m - .6, m - .6, 0, 0, .95, '#fff')
    for cx_, cy_ in ((0, 0), (10, 0), (0, 10)):
        d.rc(ox + cx_ * m, oy + cy_ * m, 4 * m - 1, 4 * m - 1, 1.4)
        d.rc(ox + cx_ * m + 6, oy + cy_ * m + 6, 2 * m - 1, 2 * m - 1, 0, 0, 1, '#fff')
    d.tx(90, 176, 'R$ 4.800,00', 'middle', 13, 1, 'tela', 'Inter Tight,sans-serif', 0, 600)
    d.rc(48, 190, 84, 26, 1.6, 13, 1, 'rgba(255,255,255,.16)')
    d.tx(90, 207, 'PAGO', 'middle', 10, 1, 'tela', ls=2.4, peso=700)
    d.fg()


def planta03_pc():
    global CENA
    guardada, CENA = CENA, CENA3
    d = D()
    d.grade(1600, 760)
    celular(d, 70, 150, .92)
    d.numero(70 + 236 * .92 + 6, 150 - 4, 1)
    d.seta(300, 372, 418, 372, '09:12')
    notebook(d, 470, 186, 1)
    d.numero(470 + 560 + 10, 186 - 6, 2)
    d.ln(1060, 360, 1110, 360, 1.4, .9, ' stroke-dasharray="6 6"')
    d.ln(1110, 200, 1110, 600, 1.4, .9, ' stroke-dasharray="6 6"')
    for yy, h in ((200, '09:14'), (400, '09:15'), (600, 'DIA 05')):
        d.seta(1110, yy, 1162, yy, '')
        d.tx(1136, yy - 10, h, 'middle', 10, .7)
    proposta(d, 1176, 128, .66)
    quadro(d, 1176, 336, .66)
    cobranca(d, 1176, 526, .66)
    d.numero(1176 + 176 * .66 + 8, 128, 3)
    d.numero(1176 + 240 * .66 + 8, 336, 4)
    d.numero(1176 + 180 * .66 + 8, 526, 5)
    d.tx(1376, 206, 'A PROPOSTA SAI', sz=12)
    d.tx(1376, 406, 'A EQUIPE RECEBE', sz=12)
    d.tx(1376, 606, 'O DINHEIRO ENTRA', sz=12)
    d.tx(70 + 118 * .92, 620, 'O CLIENTE PEDE', 'middle', 12)
    d.tx(750, 620, 'O SISTEMA DA SUA EMPRESA REGISTRA', 'middle', 12)
    d.ln(70, 110, 1030, 110, 1, .75)
    for xx in (70, 1030):
        d.ln(xx, 102, xx, 118, 1, .75)
    for xx in range(70, 1031, 40):
        d.ln(xx, 107, xx, 113, .8, .4)
    d.tx(550, 94, 'DA PRIMEIRA MENSAGEM AO DINHEIRO NA CONTA', 'middle', 12, .85)
    d.a('<g class="rotulo">')
    for k in range(4):
        d.rc(70 + k * 30, 724, 30, 6, 1, 0, .8, '#fff' if k % 2 == 0 else 'none')
    d.a('</g>')
    d.tx(200, 731, 'SEM ESCALA', sz=9, op=.7, ls=1.6)
    d.carimbo(1300, 24, 'PLANTA 03 · O CAMINHO')
    CENA = guardada
    return d.svg('0 0 1600 760', 'Desenho técnico ilustrativo do caminho de uma demanda: o cliente pede pelo WhatsApp, o sistema registra, sai a proposta, a equipe recebe a tarefa e o dinheiro entra')


def planta03_cel():
    global CENA
    guardada, CENA = CENA, CENA3
    d = D()
    d.grade(1000, 980)
    celular(d, 30, 40, .9)
    d.numero(30 + 236 * .9, 40, 1, 26)
    d.seta(254, 260, 312, 260)
    notebook(d, 340, 110, .648)
    d.numero(340 + 560 * .648, 110, 2, 26)
    base = 110 + 368 * .648
    d.ln(660, base + 30, 660, 560, 1.4, .9, ' stroke-dasharray="6 6"')
    d.ln(150, 560, 840, 560, 1.4, .9, ' stroke-dasharray="6 6"')
    for xx in (150, 490, 840):
        d.seta(xx, 560, xx, 612)
    proposta(d, 150 - 176 * .95 / 2, 630, .95)
    quadro(d, 490 - 240 * .95 / 2, 640, .95)
    cobranca(d, 840 - 180 * .95 / 2, 630, .95)
    d.numero(150 + 176 * .95 / 2 + 4, 630, 3, 26)
    d.numero(490 + 240 * .95 / 2 + 4, 640, 4, 26)
    d.numero(840 + 180 * .95 / 2 + 4, 630, 5, 26)
    CENA = guardada
    return d.svg('0 0 1000 876', 'Desenho técnico ilustrativo do caminho de uma demanda').replace('overflow:visible', 'overflow:hidden')



def gerar_base(pasta):
    """Grava as plantas do caminho do pedido (02 e 03), computador e celular."""
    saidas = {'caminho-distribuidora-pc.svg': planta02_pc(), 'caminho-distribuidora-cel.svg': planta02_cel(),
              'outro-pc.svg': planta03_pc(), 'outro-cel.svg': planta03_cel()}
    for nome, conteudo in saidas.items():
        open(os.path.join(pasta, nome), 'w', encoding='utf-8').write(conteudo)
    return saidas
