"""Desenha a planta de cada setor do site (lançamento de 05/01/2027).

Uso: python3 execution/plantas_de_setor.py
Grava em plantas/: <setor>-pc.svg e <setor>-cel.svg (o do celular tem só os números, a legenda é texto
da página) e setores.json com o chapéu, a frase e a legenda de cada setor. Regra em directives/paginas-de-setor.md.
"""
import json, math
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plantas_base import *   # noqa: F401,F403  (D, AZ, chamada, galpao, escritorio, caminhao, pessoa, arvore, furgao...)
import plantas_base

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, 'plantas')

CHAO = 590


class Marca:
    """Número no desenho. No computador a legenda vai numa faixa embaixo, sem linha cruzando nada."""
    def __init__(s, d, cel):
        s.d, s.cel = d, cel

    def __call__(s, px, py, n, lx, texto, lado=1):
        if s.cel:
            s.d.numero(px, py, n, 26)
            return
        s.d.numero(px, py, n, 15)



def moldura(d, cel, x0, x1, cota, carimbo_txt):
    if cel:
        return
    d.grade(1600, 760)
    d.ln(x0, 160, x1, 160, 1, .75)
    for x in (x0, x1):
        d.ln(x, 152, x, 168, 1, .75)
    for x in range(int(x0), int(x1) + 1, 37):
        d.ln(x, 157, x, 163, .8, .4)
    d.tx((x0 + x1) / 2, 144, cota, 'middle', 12, .85)
    d.carimbo(1290, 30, carimbo_txt)


def bloco3d(d, x, y, w, h, p=34, q=20, topo=True, lado=True):
    """Profundidade em projeção oblíqua: a face de cima e a face lateral do volume."""
    if topo:
        d.pl([(x, y), (x + p, y - q), (x + w + p, y - q), (x + w, y)], 1.2, 1, '#2A239A', True)
    if lado:
        d.pl([(x + w, y), (x + w + p, y - q), (x + w + p, y + h - q), (x + w, y + h)], 1.2, 1, '#1E1695', True)


def telhado3d(d, xe, xd, yb, alt, p=34, q=20):
    """Profundidade do telhado de duas águas: a água da direita, vista de lado."""
    xm = (xe + xd) / 2
    d.pl([(xm, yb - alt), (xm + p, yb - alt - q), (xd + p, yb - q), (xd, yb)], 1.2, 1, '#2A239A', True)
    for k in range(1, 4):
        t = k / 4
        d.ln(xm + (xd - xm) * t, yb - alt * (1 - t), xm + (xd - xm) * t + p, yb - alt * (1 - t) - q, .6, .35)


def janela(d, x, y, w, h, cols=2, rows=1, sw=1.3):
    d.rc(x, y, w, h, sw, 0, 1, 'rgba(255,255,255,.09)')
    for i in range(1, cols):
        d.ln(x + i * w / cols, y, x + i * w / cols, y + h, .9, .8)
    for j in range(1, rows):
        d.ln(x, y + j * h / rows, x + w, y + j * h / rows, .9, .8)


def mesa_trabalho(d, x, ytop, chao_local, pessoa_cabeca=True):
    d.rc(x, ytop, 110, 6, 1.3)
    d.ln(x + 8, ytop + 6, x + 8, chao_local, 1.2)
    d.ln(x + 102, ytop + 6, x + 102, chao_local, 1.2)
    d.rc(x + 30, ytop - 40, 56, 34, 1.3, 2, 1, AZ)
    for k in range(3):
        d.ln(x + 36, ytop - 32 + k * 9, x + 36 + (40 if k != 1 else 26), ytop - 32 + k * 9, .8, .5)
    d.ln(x + 58, ytop - 6, x + 58, ytop, 1.2)
    d.rc(x + 46, ytop - 2, 24, 2, .8)
    if pessoa_cabeca:
        d.ci(x + 58, ytop - 58 + 30, 9, 1.3, 1, AZ)       # cabeça na frente do monitor, de costas
        d.pl([(x + 42, ytop + 2), (x + 46, ytop - 12), (x + 70, ytop - 12), (x + 74, ytop + 2)], 1.2, 1, AZ, True)
    d.rc(x + 44, ytop + 10, 28, 4, 1)
    d.ln(x + 58, ytop + 14, x + 58, chao_local - 6, 1)
    d.ln(x + 46, chao_local - 2, x + 70, chao_local - 2, 1)


def bolsa(d, x, y, k=1):
    d.pl([(x - 22 * k, y), (x + 22 * k, y), (x + 17 * k, y - 32 * k), (x - 17 * k, y - 32 * k)], 1.4, 1, AZ, True)
    d.a(f'<path d="M {x - 9 * k:.1f} {y - 32 * k:.1f} C {x - 9 * k:.1f} {y - 50 * k:.1f}, {x + 9 * k:.1f} {y - 50 * k:.1f}, {x + 9 * k:.1f} {y - 32 * k:.1f}" fill="none" stroke="#fff" stroke-width="1.3"/>')


def celular_mao(d, x, y):
    d.rc(x, y, 9, 15, 1.1, 2, 1, '#fff')


# ------------------------------------------------------------ distribuidora
def cena_distribuidora(cel):
    d = D(); m = Marca(d, cel)
    moldura(d, cel, 150, 1170, 'A SUA DISTRIBUIDORA, DESENHADA', 'PLANTA 01 · DISTRIBUIDORA')
    chao_linha(d, 40, 1560, CHAO)
    arvore(d, 92, CHAO, 150)
    fim_esc = escritorio(d, 150, CHAO)
    fim_g, doca, placa = galpao(d, fim_esc, CHAO, 10, 4)
    cam = caminhao(d, 1196, CHAO)
    pessoa(d, 530, CHAO, 1)
    m(doca[0], doca[1], 1, 620, 'O PEDIDO DO WHATSAPP ENTRA SOZINHO')
    m(390, CHAO - 190, 2, 170, 'A NOTA SAI SOZINHA')
    m(cam[0] + 40, cam[1], 3, 1150, 'VOCÊ VÊ O LUCRO DE CADA ENTREGA')
    return d, '330 150 1010 480'


# ------------------------------------------------------------ escritório
def cena_escritorio(cel):
    d = D(); m = Marca(d, cel)
    x0, x1, topo, meio = 380, 1220, 250, 420
    moldura(d, cel, x0, x1, 'O SEU ESCRITÓRIO, DESENHADO', 'PLANTA 04 · ESCRITÓRIO')
    chao_linha(d, 40, 1560, CHAO)
    arvore(d, 300, CHAO, 160)
    arvore(d, 1320, CHAO, 130)
    bloco3d(d, x0, topo, x1 - x0, CHAO - topo)
    d.rc(x0 - 8, topo - 12, x1 - x0 + 16, 12, 1.4)
    d.rc(x0, topo, x1 - x0, CHAO - topo, 2.2)
    d.rc(x0 + 300, topo - 40, 240, 28, 1.4, 0, 1, AZ)
    d.tx(x0 + 420, topo - 21, 'SEU ESCRITÓRIO', 'middle', 12, 1, 'placa', ls=3.5, peso=600)
    d.ln(x0, meio, x1, meio, 1.8)
    # andar de cima: três mesas, o quadro de prazos e a estante
    for i in range(3):
        mesa_trabalho(d, x0 + 24 + i * 122, meio - 32, meio, False)
    cx, cy, cw, ch = x0 + 410, topo + 24, 220, 110
    d.rc(cx, cy, cw, ch, 1.6, 0, 1, AZ)
    d.rc(cx, cy, cw, 18, 0, 0, .9, '#fff')
    d.a(f'<text x="{cx + 10}" y="{cy + 13}" font-family="JetBrains Mono,monospace" font-size="9" font-weight="700" letter-spacing="1.6" fill="{AZ}">PRAZOS · DEZEMBRO</text>')
    for r in range(4):
        for c in range(7):
            gx, gy = cx + 6 + c * 30, cy + 24 + r * 21
            d.rc(gx, gy, 26, 17, .7, 0, .55)
            if (r, c) in ((0, 2), (1, 4), (2, 1), (3, 5)):
                d.rc(gx + 2, gy + 2, 22, 13, 0, 0, .9, '#fff')
            if (r, c) in ((1, 1), (2, 5)):
                d.pl([(gx + 7, gy + 9), (gx + 11, gy + 13), (gx + 19, gy + 5)], 1.1)
    ex = x0 + 660
    d.rc(ex, topo + 20, 160, meio - topo - 20, 1.4, 0, 1, AZ)
    for k in range(3):
        yy = topo + 20 + (k + 1) * (meio - topo - 20) / 3
        d.ln(ex, yy, ex + 160, yy, 1.2)
        xx = ex + 8
        for b in range(9):
            w = 10 + (b * 7) % 8
            h = 34 + (b * 5) % 12
            d.rc(xx, yy - h, w, h, .9, 0, .85, AZ)
            xx += w + 4
            if xx > ex + 150:
                break
    # térreo: recepção, cliente, arquivo e sala de reunião
    d.rc(x0 + 24, CHAO - 66, 150, 66, 1.6, 0, 1, AZ)
    d.ln(x0 + 18, CHAO - 66, x0 + 180, CHAO - 66, 2)
    d.rc(x0 + 110, CHAO - 98, 44, 30, 1.2, 2, 1, AZ)
    d.ci(x0 + 70, CHAO - 92, 9, 1.3, 1, AZ)
    d.pl([(x0 + 52, CHAO - 66), (x0 + 56, CHAO - 80), (x0 + 84, CHAO - 80), (x0 + 88, CHAO - 66)], 1.2, 1, AZ, True)
    pessoa(d, x0 + 226, CHAO, 1.05)
    celular_mao(d, x0 + 233, CHAO - 34)
    ax = x0 + 290
    d.rc(ax, CHAO - 130, 96, 130, 1.8, 0, 1, AZ)
    for k in range(4):
        yy = CHAO - 130 + k * 32.5
        d.rc(ax + 6, yy + 5, 84, 24, 1.1)
        d.rc(ax + 38, yy + 14, 20, 5, .9)
    d.pl([(ax + 10, CHAO - 130), (ax + 18, CHAO - 152), (ax + 70, CHAO - 152), (ax + 78, CHAO - 130)], 1.2)
    for k in range(3):
        d.ln(ax + 24 + k * 3, CHAO - 148 + k * 3, ax + 66, CHAO - 148 + k * 3, .8, .7)
    sx = x0 + 430
    d.rc(sx, meio + 18, x1 - sx - 20, CHAO - meio - 18, 1.3, 0, .9)
    for k in range(1, 5):
        d.ln(sx + k * (x1 - sx - 20) / 5, meio + 18, sx + k * (x1 - sx - 20) / 5, CHAO, .8, .45)
    d.rc(sx + 120, meio + 32, 150, 64, 1.4, 2, 1, AZ)
    d.pl([(sx + 132, meio + 84), (sx + 160, meio + 66), (sx + 190, meio + 74), (sx + 222, meio + 50), (sx + 258, meio + 58)], 1.4)
    d.rc(sx + 60, CHAO - 50, 270, 7, 1.3, 0, 1, AZ)
    for k in range(2):
        d.ln(sx + 80 + k * 230, CHAO - 43, sx + 80 + k * 230, CHAO, 1.2)
    for k in range(4):
        cxh = sx + 90 + k * 70
        d.ci(cxh, CHAO - 68, 8, 1.2, 1, AZ)
    m(x0 + 237, CHAO - 27, 3, 150, 'O CLIENTE ACOMPANHA SEM LIGAR')
    m(ax + 48, CHAO - 166, 1, 610, 'O DOCUMENTO DO CLIENTE CHEGA ORGANIZADO')
    m(cx + cw - 10, cy - 6, 2, 1140, 'O PRAZO ENTRA NA AGENDA SOZINHO')
    return d, '330 160 940 470'


# ------------------------------------------------------------ loja e varejo
def cena_varejo(cel):
    d = D(); m = Marca(d, cel)
    x0, x1, topo = 400, 1200, 250
    moldura(d, cel, x0, x1, 'A SUA LOJA, DESENHADA', 'PLANTA 05 · LOJA')
    chao_linha(d, 40, 1560, CHAO)
    bloco3d(d, x0, topo, x1 - x0, CHAO - topo)
    d.rc(x0 - 10, topo - 14, x1 - x0 + 20, 14, 1.4)
    d.rc(x0, topo, x1 - x0, CHAO - topo, 2.2)
    d.rc(x0 + 220, topo + 14, 360, 40, 1.6, 0, 1, AZ)
    d.tx((x0 + x1) / 2, topo + 41, 'SUA LOJA', 'middle', 20, 1, 'placa', ls=9, peso=600)
    # toldo
    yt = topo + 72
    d.ln(x0 - 6, yt, x1 + 6, yt, 1.6)
    pts = []
    for i in range(17):
        xa = x0 - 6 + i * (x1 - x0 + 12) / 16
        pts += [(xa, yt + 26)]
        if i < 16:
            pts += [(xa + (x1 - x0 + 12) / 32, yt + 34)]
    d.pl([(x0 - 6, yt)] + pts + [(x1 + 6, yt)], 1.4, 1, AZ)
    for i in range(17):
        xa = x0 - 6 + i * (x1 - x0 + 12) / 16
        d.ln(xa, yt, xa, yt + 26, .8, .5)
    # vitrine da esquerda: pedestais com bolsa e sapato, luz de cima
    vx, vy, vw, vh = x0 + 30, topo + 130, 250, CHAO - topo - 150
    d.rc(vx, vy, vw, vh, 1.8, 0, 1, AZ)
    for k, px in enumerate((vx + 60, vx + 180)):
        d.rc(px - 34, CHAO - 80, 68, 60, 1.3)
        d.a(f'<polygon points="{px - 10},{vy + 4} {px + 10},{vy + 4} {px + 46},{CHAO - 80} {px - 46},{CHAO - 80}" fill="rgba(255,255,255,.06)" stroke="#fff" stroke-width=".8" stroke-dasharray="4 5" opacity=".6"/>')
        if k == 0:
            bolsa(d, px, CHAO - 80, 1.2)
        else:
            d.pl([(px - 34, CHAO - 82), (px - 34, CHAO - 96), (px - 4, CHAO - 100), (px + 10, CHAO - 120), (px + 22, CHAO - 120), (px + 22, CHAO - 82)], 1.4, 1, AZ, True)
    for k in range(3):
        d.ln(vx + 20 + k * 12, vy + 18 + k * 10, vx + 40 + k * 12, vy + 12 + k * 10, .8, .35)
    # porta com o balcão lá dentro
    px0 = x0 + 320
    d.rc(px0, topo + 120, 160, CHAO - topo - 120, 1.8, 0, 1, AZ)
    d.ln(px0 + 80, topo + 120, px0 + 80, CHAO, 1.2)
    d.ln(px0 + 70, CHAO - 140, px0 + 70, CHAO - 100, 2)
    d.ln(px0 + 90, CHAO - 140, px0 + 90, CHAO - 100, 2)
    d.rc(px0 + 50, topo + 140, 60, 22, 1.1, 2)
    d.tx(px0 + 80, topo + 155, 'ABERTO', 'middle', 9, 1, 'placa', ls=1.8, peso=600)
    d.ln(px0 + 66, topo + 120, px0 + 72, topo + 140, .8); d.ln(px0 + 94, topo + 120, px0 + 88, topo + 140, .8)
    d.ln(px0 + 10, CHAO - 60, px0 + 150, CHAO - 60, 1, .6)
    d.rc(px0 + 104, CHAO - 82, 30, 20, 1.2, 2, 1, '#fff')
    # vitrine da direita: manequim
    wx = x0 + 520
    d.rc(wx, vy, vw, vh, 1.8, 0, 1, AZ)
    mx = wx + 125
    d.ci(mx, vy + 30, 11, 1.4, 1, AZ)
    d.pl([(mx - 28, vy + 50), (mx + 28, vy + 50), (mx + 20, vy + 105), (mx + 34, vy + 150), (mx - 34, vy + 150), (mx - 20, vy + 105)], 1.5, 1, AZ, True)
    d.ln(mx - 20, vy + 105, mx + 20, vy + 105, 1, .7)
    d.ln(mx, vy + 150, mx, CHAO - 28, 1.4)
    d.ln(mx - 26, CHAO - 26, mx + 26, CHAO - 26, 1.6)
    # cliente na calçada com o celular e a sacola
    pessoa(d, 340, CHAO, 1.15)
    celular_mao(d, 348, CHAO - 40)
    bolsa(d, 318, CHAO - 10, .7)
    # moto de entrega
    mo = 1290
    d.roda(mo, CHAO - 18, 18); d.roda(mo + 110, CHAO - 18, 18)
    d.pl([(mo, CHAO - 18), (mo + 30, CHAO - 56), (mo + 84, CHAO - 56), (mo + 110, CHAO - 18)], 1.5)
    d.ln(mo + 84, CHAO - 56, mo + 96, CHAO - 86, 1.5); d.ln(mo + 90, CHAO - 86, mo + 106, CHAO - 86, 1.6)
    d.rc(mo + 4, CHAO - 104, 52, 46, 1.5, 0, 1, AZ)
    d.tx(mo + 30, CHAO - 77, 'PRONTO', 'middle', 8, 1, 'placa', ls=1.2, peso=700)
    m(352, CHAO - 33, 1, 120, 'O CLIENTE VÊ O ANDAMENTO SOZINHO')
    m(px0 + 119, CHAO - 72, 2, 620, 'A FICHA DE CADA CLIENTE NA MÃO DA EQUIPE')
    m(mo + 30, CHAO - 112, 3, 1100, 'O AVISO DE PRONTO SAI SOZINHO')
    return d, '262 176 1170 454'


# ------------------------------------------------------------ indústria
def cena_industria(cel):
    d = D(); m = Marca(d, cel)
    x0, x1, topo = 440, 1180, 330
    moldura(d, cel, 250, x1, 'A SUA FÁBRICA, DESENHADA', 'PLANTA 06 · INDÚSTRIA')
    chao_linha(d, 40, 1560, CHAO)
    # silos
    for sx in (260, 340):
        d.rc(sx, 300, 64, CHAO - 340, 1.8, 0, 1, AZ)
        d.a(f'<path d="M {sx} 300 Q {sx + 32} 262 {sx + 64} 300" fill="{AZ}" stroke="#fff" stroke-width="1.8"/>')
        for yy in range(320, CHAO - 50, 26):
            d.ln(sx, yy, sx + 64, yy, .7, .4)
        d.pl([(sx + 8, CHAO - 40), (sx + 32, CHAO - 14), (sx + 56, CHAO - 40)], 1.4)
        d.ln(sx + 6, CHAO - 40, sx + 6, CHAO, 1.4); d.ln(sx + 58, CHAO - 40, sx + 58, CHAO, 1.4)
        d.rc(sx + 18, 390, 28, 60, 1, 0, .7)
        nivel = 430 if sx == 260 else 410
        d.rc(sx + 20, nivel, 24, 450 - nivel - 2, 0, 0, .9, '#fff')
    d.ln(324, 280, 440, 280, 1.4); d.ln(404, 280, 404, 300, 1.4)
    # galpão com telhado de duas águas e chaminé
    bloco3d(d, x0, topo, x1 - x0, CHAO - topo, topo=False)
    telhado3d(d, x0, x1, topo, 70)
    d.pl([(x0, topo), ((x0 + x1) / 2, topo - 70), (x1, topo)], 2, 1, AZ, True)
    for k in range(1, 12):
        t = k / 12
        xa = x0 + (x1 - x0) * t
        ya = topo - 70 * (1 - abs(2 * t - 1))
        d.ln(xa, ya, xa, topo, .6, .25)
    d.rc(x0, topo, x1 - x0, CHAO - topo, 2.2)
    d.rc(1080, 140, 36, 176, 1.8, 0, 1, AZ)
    for yy in range(160, topo - 50, 22):
        d.ln(1080, yy, 1116, yy, .6, .4)
    for k, (cx_, cy_, r) in enumerate(((1098, 118, 14), (1118, 94, 18), (1146, 72, 22))):
        d.ci(cx_, cy_, r, 1.1, .55 - k * .12)
    # recorte: linha de produção
    d.rc(x0 + 20, topo + 30, x1 - x0 - 40, CHAO - topo - 40, 1, 0, .5)
    # prensa
    pr = x0 + 60
    d.rc(pr, CHAO - 150, 110, 150, 1.8, 0, 1, AZ)
    d.rc(pr + 20, CHAO - 130, 70, 20, 1.3)
    d.ln(pr + 55, CHAO - 110, pr + 55, CHAO - 80, 2.4)
    d.rc(pr + 30, CHAO - 80, 50, 10, 1.3, 0, 1, '#fff')
    d.rc(pr + 10, CHAO - 56, 90, 12, 1.2)
    d.ci(pr + 94, CHAO - 136, 7, 1.1)
    # esteira
    ey = CHAO - 52
    d.ln(pr + 110, ey, x1 - 150, ey, 1.6)
    d.ln(pr + 110, ey + 16, x1 - 150, ey + 16, 1.6)
    for xx in range(int(pr + 120), int(x1 - 150), 34):
        d.ci(xx, ey + 8, 6, 1, .8)
    for xx in range(int(pr + 140), int(x1 - 180), 96):
        d.rc(xx, ey - 30, 40, 30, 1.3, 0, 1, AZ)
        d.ln(xx + 20, ey - 30, xx + 20, ey - 20, .8, .6)
    for k in range(3):
        d.ln(pr + 130 + k * 160, ey + 16, pr + 130 + k * 160, CHAO, 1)
    # braço robótico
    rb = x0 + 470
    d.rc(rb - 24, ey - 10, 48, 10, 1.4)
    d.pl([(rb, ey - 10), (rb - 20, ey - 110), (rb + 50, ey - 150), (rb + 70, ey - 110)], 2.2)
    for (px_, py_) in ((rb, ey - 10), (rb - 20, ey - 110), (rb + 50, ey - 150)):
        d.ci(px_, py_, 7, 1.4, 1, AZ)
    d.ln(rb + 62, ey - 110, rb + 62, ey - 96, 1.4); d.ln(rb + 78, ey - 110, rb + 78, ey - 96, 1.4)
    # palete pronto
    pp = x1 - 140
    d.rc(pp, CHAO - 10, 110, 10, 1.3)
    for c in range(3):
        for r in range(2):
            d.rc(pp + 4 + c * 35, CHAO - 44 - r * 34, 33, 34, 1.2, 0, 1, AZ)
    d.rc(pp + 70, CHAO - 104, 36, 26, 1.1, 0, 1, '#fff')
    d.a(f'<text x="{pp + 88}" y="{CHAO - 87}" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="9" font-weight="700" fill="{AZ}">R$</text>')
    # janelas altas
    for i in range(8):
        d.rc(x0 + 60 + i * 80, topo + 40, 48, 26, 1, 0, .7)
    m(pr + 55, CHAO - 160, 1, 560, 'A ORDEM DE PRODUÇÃO SAI DO PEDIDO')
    m(292, 340, 2, 100, 'A MATÉRIA PRIMA É COMPRADA ANTES DE FALTAR')
    m(pp + 88, CHAO - 118, 3, 1100, 'O CUSTO DE CADA PRODUTO, DE VERDADE')
    return d, '230 16 1000 614'


# ------------------------------------------------------------ imobiliária
def cena_imobiliaria(cel):
    d = D(); m = Marca(d, cel)
    moldura(d, cel, 300, 1300, 'A SUA IMOBILIÁRIA, DESENHADA', 'PLANTA 07 · IMOBILIÁRIA')
    chao_linha(d, 40, 1560, CHAO)
    # prédio
    px0, pw, ptopo = 300, 300, 200
    bloco3d(d, px0, ptopo, pw, CHAO - ptopo)
    d.rc(px0, ptopo, pw, CHAO - ptopo, 2.2)
    d.rc(px0 - 8, ptopo - 10, pw + 16, 10, 1.4)
    andares = 6
    ha = (CHAO - 60 - ptopo) / andares
    for a in range(andares):
        y = ptopo + 14 + a * ha
        for c in range(3):
            janela(d, px0 + 24 + c * 92, y, 70, ha - 28, 2)
        d.rc(px0 + 14, y + ha - 18, pw - 28, 6, 1)
        for k in range(12):
            d.ln(px0 + 22 + k * 22, y + ha - 12, px0 + 22 + k * 22, y + ha - 2, .7, .5)
    d.rc(px0 + 120, CHAO - 56, 60, 56, 1.6, 0, 1, AZ)
    d.ln(px0 + 150, CHAO - 56, px0 + 150, CHAO, 1)
    # casa 1, com a placa
    def casa(x, w, altura, andares2=False):
        tp = CHAO - altura
        bloco3d(d, x, tp, w, altura, topo=False)
        telhado3d(d, x - 12, x + w + 12, tp, 80)
        d.pl([(x - 12, tp), (x + w / 2, tp - 80), (x + w + 12, tp)], 2, 1, AZ, True)
        for k in range(1, 7):
            t = k / 7
            d.ln(x + w * t, tp - 80 * (1 - abs(2 * t - 1)), x + w * t, tp, .6, .3)
        d.rc(x, tp, w, altura, 2)
        d.rc(x + w * .62, CHAO - 90, 46, 90, 1.6, 0, 1, AZ)
        d.ci(x + w * .62 + 38, CHAO - 44, 2, 1, 1, '#fff')
        janela(d, x + 22, CHAO - 104, 80, 60, 2, 2)
        if andares2:
            janela(d, x + 22, tp + 20, 80, 50, 2, 2)
            janela(d, x + w - 102, tp + 20, 80, 50, 2, 2)
            d.ln(x, CHAO - 120, x + w, CHAO - 120, 1.2, .8)
    casa(690, 240, 150)
    casa(1010, 250, 230, True)
    # cerca e placa
    for xx in range(670, 950, 14):
        d.ln(xx, CHAO, xx, CHAO - 34, 1, .8)
    d.ln(664, CHAO - 28, 950, CHAO - 28, 1, .8)
    d.ln(626, CHAO, 626, CHAO - 120, 2)
    d.rc(580, CHAO - 168, 92, 50, 1.8, 0, 1, '#fff')
    d.a(f'<text x="626" y="{CHAO - 137}" text-anchor="middle" font-family="Inter Tight,sans-serif" font-size="17" font-weight="700" letter-spacing="2" fill="{AZ}">ALUGA</text>')
    # corretor e interessado
    pessoa(d, 790, CHAO, 1.05)
    d.rc(798, CHAO - 34, 12, 16, 1.1, 1, 1, AZ)
    pessoa(d, 840, CHAO, 1.1)
    celular_mao(d, 847, CHAO - 38)
    # carro
    cx = 1310
    d.pl([(cx, CHAO - 18), (cx, CHAO - 46), (cx + 40, CHAO - 50), (cx + 66, CHAO - 76), (cx + 140, CHAO - 76), (cx + 168, CHAO - 50), (cx + 200, CHAO - 44), (cx + 200, CHAO - 18)], 1.8, 1, AZ, True)
    d.pl([(cx + 72, CHAO - 70), (cx + 100, CHAO - 70), (cx + 100, CHAO - 50), (cx + 54, CHAO - 50)], 1.2)
    d.pl([(cx + 108, CHAO - 70), (cx + 136, CHAO - 70), (cx + 158, CHAO - 50), (cx + 108, CHAO - 50)], 1.2)
    d.roda(cx + 44, CHAO - 16, 16); d.roda(cx + 160, CHAO - 16, 16)
    m(626, CHAO - 176, 1, 640, 'O INTERESSADO DO PORTAL VIRA VISITA MARCADA')
    m(450, 280, 2, 130, 'O ALUGUEL É COBRADO SOZINHO')
    m(1135, CHAO - 310, 3, 1120, 'O REPASSE AO PROPRIETÁRIO SAI CERTO')
    return d, '262 100 1056 530'


# ------------------------------------------------------------ agência e eventos
def cena_agencia(cel):
    d = D(); m = Marca(d, cel)
    moldura(d, cel, 380, 1240, 'O SEU EVENTO, DESENHADO', 'PLANTA 08 · EVENTOS')
    chao_linha(d, 40, 1560, CHAO)
    # palco
    s0, s1, sy = 560, 1120, CHAO - 60
    bloco3d(d, s0, sy, s1 - s0, 60, 26, 14)
    d.rc(s0, sy, s1 - s0, 60, 2, 0, 1, AZ)
    for xx in range(s0 + 10, s1, 16):
        d.ln(xx, sy + 8, xx, CHAO - 4, .6, .35)
    # treliça
    def torre(x):
        d.rc(x, 230, 24, sy - 230, 1.4)
        y = 230
        while y < sy - 20:
            d.ln(x, y, x + 24, y + 20, .8, .7); d.ln(x + 24, y + 20, x, y + 40, .8, .7)
            y += 40
    torre(s0 + 10); torre(s1 - 34)
    d.rc(s0 + 10, 220, s1 - s0 - 20, 24, 1.4)
    x = s0 + 10
    while x < s1 - 30:
        d.ln(x, 244, x + 20, 220, .8, .7); d.ln(x + 20, 220, x + 40, 244, .8, .7)
        x += 40
    # luzes com o facho
    for lx in (s0 + 90, s0 + 210, s1 - 210, s1 - 90):
        d.rc(lx - 10, 244, 20, 22, 1.3, 2, 1, AZ)
        d.a(f'<polygon points="{lx - 8},{266} {lx + 8},{266} {lx + 46},{sy} {lx - 46},{sy}" fill="rgba(255,255,255,.05)" stroke="#fff" stroke-width=".8" stroke-dasharray="4 6" opacity=".55"/>')
    # telão com o cronograma
    tx0, ty0, tw, th = 700, 290, 280, 150
    d.rc(tx0, ty0, tw, th, 2, 0, 1, AZ)
    d.tx(tx0 + 14, ty0 + 22, 'CRONOGRAMA', sz=10, op=1, cls='tela', ls=1.6, peso=700)
    for i, (h, w_) in enumerate((('18:00', 120), ('19:30', 80), ('20:15', 150), ('22:00', 60))):
        yy = ty0 + 44 + i * 25
        d.tx(tx0 + 14, yy + 9, h, sz=9, op=.85, cls='tela', ls=.5)
        d.rc(tx0 + 66, yy, w_, 12, 0, 0, .9 if i == 2 else .55, '#fff')
    # caixas de som
    for bx in (s0 + 44, s1 - 104):
        d.rc(bx, sy - 110, 60, 110, 1.6, 0, 1, AZ)
        d.ci(bx + 30, sy - 78, 16, 1.2); d.ci(bx + 30, sy - 30, 11, 1.2)
    # mesas redondas
    def mesa(x):
        d.pl([(x - 50, CHAO - 54), (x + 50, CHAO - 54), (x + 58, CHAO - 4), (x - 58, CHAO - 4)], 1.5, 1, AZ, True)
        d.ln(x - 52, CHAO - 54, x + 52, CHAO - 54, 2)
        d.ln(x, CHAO - 54, x, CHAO - 76, 1.2); d.ci(x, CHAO - 82, 7, 1.1)
        for c in (-74, 74):
            d.pl([(x + c, CHAO), (x + c, CHAO - 36), (x + c + (10 if c < 0 else -10), CHAO - 36)], 1.2)
            d.ln(x + c, CHAO - 36, x + c, CHAO - 72, 1.2)
    mesa(450); mesa(1230)
    # van do fornecedor
    furgao(d, 90, CHAO - 131, .95)
    d.rc(150, CHAO - 104, 70, 20, 0, 0, 1, AZ)
    d.tx(186, CHAO - 89, 'FORNECEDOR', 'middle', 9, 1, 'placa', ls=1.4, peso=700)
    pessoa(d, 360, CHAO, 1)
    d.rc(366, CHAO - 34, 14, 18, 1.1, 1, 1, AZ)
    m(200, CHAO - 140, 1, 110, 'CADA FORNECEDOR NO ORÇAMENTO CERTO')
    m(tx0 + tw - 6, ty0 - 4, 2, 620, 'O CRONOGRAMA DO EVENTO PARA TODO MUNDO')
    m(1230, CHAO - 94, 3, 1100, 'O CONTRATO E O PAGAMENTO SEM CORRER ATRÁS')
    return d, '70 160 1290 470'


# ------------------------------------------------------------ escola e curso
def cena_escola(cel):
    d = D(); m = Marca(d, cel)
    moldura(d, cel, 380, 1240, 'A SUA ESCOLA, DESENHADA', 'PLANTA 09 · ESCOLA')
    chao_linha(d, 40, 1560, CHAO)
    # alas
    for (ax0, ax1) in ((380, 690), (930, 1240)):
        bloco3d(d, ax0, 320, ax1 - ax0, CHAO - 320, lado=(ax0 > 800))
        d.rc(ax0, 320, ax1 - ax0, CHAO - 320, 2)
        d.rc(ax0 - 6, 310, ax1 - ax0 + 12, 10, 1.3)
        for r in range(2):
            for c in range(4):
                wx = ax0 + 20 + c * ((ax1 - ax0 - 40) / 4)
                wy = 344 + r * 120
                janela(d, wx, wy, 56, 72, 2, 2)
        d.ln(ax0, 455, ax1, 455, 1.2, .8)
    # bloco central com relógio
    d.rc(690, 260, 240, CHAO - 260, 2.2)
    telhado3d(d, 680, 940, 260, 70)
    d.pl([(680, 260), (810, 190), (940, 260)], 2, 1, AZ, True)
    d.ci(810, 230, 22, 1.6, 1, AZ)
    d.ln(810, 230, 810, 216, 1.6); d.ln(810, 230, 820, 236, 1.6)
    d.rc(720, 280, 180, 34, 1.5, 0, 1, AZ)
    d.tx(810, 302, 'SUA ESCOLA', 'middle', 14, 1, 'placa', ls=4, peso=600)
    janela(d, 720, 336, 180, 70, 4)
    # entrada com escada e marquise
    d.rc(750, CHAO - 130, 120, 110, 1.8, 0, 1, AZ)
    d.ln(810, CHAO - 130, 810, CHAO - 20, 1.2)
    for k in range(3):
        d.rc(730 - k * 12, CHAO - 20 + k * 6.6, 160 + k * 24, 6.6, 1.1)
    d.rc(730, CHAO - 146, 160, 10, 1.4)
    # secretaria
    d.rc(1000, CHAO - 118, 140, 22, 1.3, 0, 1, '#fff')
    d.a(f'<text x="1070" y="{CHAO - 102}" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="10" font-weight="700" letter-spacing="1.6" fill="{AZ}">SECRETARIA</text>')
    # mastro
    d.ln(1320, CHAO, 1320, 250, 1.8)
    d.a('<path d="M 1320 254 C 1350 244, 1370 268, 1400 258 L 1400 296 C 1370 306, 1350 282, 1320 292 Z" fill="none" stroke="#fff" stroke-width="1.4"/>')
    # ônibus escolar
    bx = 70
    d.rc(bx, CHAO - 120, 250, 96, 1.8, 10, 1, AZ)
    for k in range(5):
        d.rc(bx + 16 + k * 44, CHAO - 106, 34, 30, 1.2)
    d.ln(bx, CHAO - 62, bx + 250, CHAO - 62, 1.2, .8)
    d.tx(bx + 125, CHAO - 44, 'ESCOLAR', 'middle', 11, 1, 'placa', ls=3, peso=700)
    d.roda(bx + 56, CHAO - 18, 18); d.roda(bx + 200, CHAO - 18, 18)
    # responsável e aluno
    pessoa(d, 560, CHAO, 1.1)
    celular_mao(d, 567, CHAO - 38)
    pessoa(d, 596, CHAO, .66)
    d.rc(588, CHAO - 26, 14, 14, 1, 2, 1, AZ)
    m(810, CHAO - 150, 1, 640, 'A MATRÍCULA ENTRA PELO SITE')
    m(1162, CHAO - 107, 2, 1100, 'A MENSALIDADE É COBRADA SOZINHA')
    m(571, CHAO - 31, 3, 130, 'O RESPONSÁVEL RECEBE O AVISO')
    return d, '340 140 1080 480'


# ------------------------------------------------------------ startup
def cena_startup(cel):
    d = D(); m = Marca(d, cel)
    x0, x1, topo = 400, 1240, 230
    moldura(d, cel, x0, x1, 'A SUA STARTUP, DESENHADA', 'PLANTA 10 · STARTUP')
    chao_linha(d, 40, 1560, CHAO)
    bloco3d(d, x0, topo, x1 - x0, CHAO - topo)
    d.rc(x0, topo, x1 - x0, CHAO - topo, 2.2)
    # janelão industrial ao fundo
    for c in range(14):
        d.ln(x0 + c * 60, topo, x0 + c * 60, topo + 140, .7, .3)
    for r in range(1, 4):
        d.ln(x0, topo + r * 35, x1, topo + r * 35, .7, .3)
    d.ln(x0, topo + 140, x1, topo + 140, 1.2, .7)
    # quadro branco com notas
    d.rc(x0 + 40, topo + 30, 230, 120, 1.6, 0, 1, AZ)
    for i in range(3):
        for j in range(4):
            if (i + j) % 3 == 2:
                continue
            d.rc(x0 + 54 + j * 52, topo + 44 + i * 34, 40, 26, 1, 0, .9, 'rgba(255,255,255,.14)' if (i * j) % 2 else AZ)
    # telão do painel de números
    sx, sy, sw, sh = x0 + 470, topo + 28, 330, 190
    d.rc(sx, sy, sw, sh, 2, 4, 1, AZ)
    d.tx(sx + 16, sy + 26, 'Receita recorrente', sz=12, op=1, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=600)
    d.tx(sx + 16, sy + 56, 'R$ 84.300', sz=24, op=1, cls='tela', fam='Inter Tight,sans-serif', ls=-.5, peso=600)
    d.tx(sx + 160, sy + 56, '+12% no mês', sz=11, op=.8, cls='tela', fam='Inter Tight,sans-serif', ls=0, peso=400)
    vals = [20, 28, 26, 38, 44, 52, 60, 74, 82, 96]
    pts = [(sx + 20 + i * 32, sy + sh - 16 - v) for i, v in enumerate(vals)]
    d.pl(pts + [(pts[-1][0], sy + sh - 16), (pts[0][0], sy + sh - 16)], 0, 1, 'rgba(255,255,255,.1)', True)
    d.pl(pts, 2)
    # mesa comprida com notebooks e pessoas
    ty = CHAO - 70
    d.rc(x0 + 40, ty, 560, 8, 1.6, 0, 1, AZ)
    for xx in (x0 + 60, x0 + 580):
        d.ln(xx, ty + 8, xx, CHAO, 1.4)
    for k, nx in enumerate((x0 + 90, x0 + 260, x0 + 430)):
        d.pl([(nx, ty), (nx + 70, ty), (nx + 64, ty - 44), (nx + 6, ty - 44)], 1.4, 1, AZ, True)
        d.ln(nx + 12, ty - 30, nx + 58, ty - 30, .8, .6); d.ln(nx + 12, ty - 20, nx + 46, ty - 20, .8, .6)
        d.ci(nx + 35, ty - 64, 10, 1.3, 1, AZ)
        d.pl([(nx + 16, ty - 44), (nx + 20, ty - 52), (nx + 50, ty - 52), (nx + 54, ty - 44)], 1.1)
    # plantas
    for px in (x0 + 660, x1 - 60):
        d.pl([(px - 18, CHAO), (px - 22, CHAO - 40), (px + 22, CHAO - 40), (px + 18, CHAO)], 1.4, 1, AZ, True)
        for ang in (-60, -30, 0, 30, 60):
            r = math.radians(ang - 90)
            d.ln(px, CHAO - 40, px + math.cos(r) * 44, CHAO - 40 + math.sin(r) * 50, 1.2, .85)
    # as ferramentas ligadas ao painel
    nos = [('PAGAMENTO', 300), ('CRM', 380), ('EMAIL', 460)]
    for nome, ny in nos:
        d.rc(200, ny - 18, 140, 36, 1.4, 18, 1, AZ)
        d.tx(270, ny + 4, nome, 'middle', 10, 1, 'placa', ls=1.6, peso=700)
        k = (ny - 300) / 80
        xr = 360 - 10 * k
        d.a(f'<polyline points="340,{ny} {xr},{ny} {xr},{200 - 12 * k} {sx + 60 + 40 * k},{200 - 12 * k} {sx + 60 + 40 * k},{sy}" fill="none" stroke="#fff" stroke-width="1.1" opacity=".7" stroke-dasharray="5 6"/>')
    m(x0 + 125, ty - 50, 1, 560, 'O CLIENTE NOVO ENTRA SOZINHO')
    m(sx + sw - 6, sy - 4, 2, 1110, 'OS NÚMEROS DO MÊS NUM PAINEL SÓ')
    m(196, 300, 3, 130, 'A COBRANÇA RECORRENTE RODA SOZINHA')
    return d, '150 130 1140 490'


CENAS = {
    'distribuidora': (cena_distribuidora, 'Para distribuidoras e atacado', 'Cada pedido vira nota', 'e você vê quanto sobrou',
                      ['O pedido do WhatsApp entra sozinho', 'A nota sai sozinha', 'Você vê o lucro de cada entrega']),
    'escritorio': (cena_escritorio, 'Para escritórios de advocacia, contabilidade e engenharia', 'O escritório anda', 'sem você conferir cada prazo',
                   ['O documento do cliente chega organizado', 'O prazo entra na agenda sozinho', 'O cliente acompanha sem ligar']),
    'varejo': (cena_varejo, 'Para lojas e varejo', 'O cliente para de perguntar', 'cadê o meu pedido',
               ['O cliente vê o andamento sozinho', 'A ficha de cada cliente na mão da equipe', 'O aviso de pronto sai sozinho']),
    'industria': (cena_industria, 'Para indústrias', 'A fábrica produz o que vendeu', 'e você sabe quanto custou',
                  ['A ordem de produção sai do pedido', 'A matéria prima é comprada antes de faltar', 'O custo de cada produto, de verdade']),
    'imobiliaria': (cena_imobiliaria, 'Para imobiliárias', 'Do anúncio ao repasse', 'sem planilha no meio',
                    ['O interessado do portal vira visita marcada', 'O aluguel é cobrado sozinho', 'O repasse ao proprietário sai certo']),
    'agencia': (cena_agencia, 'Para agências e eventos', 'Cada evento no prazo', 'e cada fornecedor no lugar',
                ['Cada fornecedor no orçamento certo', 'O cronograma do evento para todo mundo', 'O contrato e o pagamento sem correr atrás']),
    'escola': (cena_escola, 'Para escolas e cursos', 'A matrícula entra sozinha', 'e a mensalidade também',
               ['A matrícula entra pelo site', 'A mensalidade é cobrada sozinha', 'O responsável recebe o aviso']),
    'startup': (cena_startup, 'Para startups', 'Mais clientes todo mês', 'sem crescer a planilha',
                ['O cliente novo entra sozinho', 'Os números do mês num painel só', 'A cobrança recorrente roda sozinha']),
}

def main():
    os.makedirs(PASTA, exist_ok=True)
    meta = {}
    for slug, (fn, chapeu, t1, t2, leg) in CENAS.items():
        d, _ = fn(False)
        open(os.path.join(PASTA, f'{slug}-pc.svg'), 'w', encoding='utf-8').write(d.svg('0 0 1600 660', f'Desenho técnico ilustrativo: {chapeu.lower()}'))
        d, vb = fn(True)
        open(os.path.join(PASTA, f'{slug}-cel.svg'), 'w', encoding='utf-8').write(d.svg(vb, f'Desenho técnico ilustrativo: {chapeu.lower()}').replace('overflow:visible', 'overflow:hidden'))
        meta[slug] = dict(chapeu=chapeu, frase=f'{t1} {t2}', legenda=leg)
    plantas_base.gerar_base(PASTA)
    meta['outro'] = dict(chapeu='Para qualquer empresa', frase='Do primeiro pedido ao dinheiro na conta, sem depender de alguém lembrar',
                         legenda=['O cliente pede', 'O sistema registra', 'A proposta sai', 'A equipe recebe', 'O dinheiro entra'])
    json.dump(meta, open(os.path.join(PASTA, 'setores.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('plantas gravadas em', PASTA, '·', len(meta), 'setores')


if __name__ == '__main__':
    main()
