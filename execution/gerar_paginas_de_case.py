"""Gera cases/<nome>/index.html a partir do texto de cada case na página inicial (index.html).
Uso: python3 execution/gerar_paginas_de_case.py   (rodar de novo sempre que o texto do case mudar)
"""
import re, json, os, html
t=open('index.html',encoding='utf-8').read()
estilo=re.search(r'<style>.*?</style>',open('consultoria/index.html',encoding='utf-8').read(),re.S).group(0)
limpa=lambda s: re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s)).strip()
CASES={'auth':('auth','AUTH','Sistema sob medida para autenticação de peças de luxo'),
       'cca':('fazenda-cca','Fazenda CCA','Aplicativo de gestão de fazenda de gado feito sob medida'),
       'rastro':('rastro','Rastro','Aplicativo sob medida para controle de frota e de pneus')}
# A descrição que aparece no resultado de busca: o que era, o que virou, sem número que não esteja na página.
DESCRICAO={'auth':'Como a AUTH, que autentica peças de luxo, ganhou 500% de capacidade de avaliação sem contratar: certificado automático e uma plataforma para equipe, loja e cliente.',
           'cca':'Como a Fazenda CCA trocou o bloquinho por um aplicativo só: pastos, lotes, entradas, saídas e o caixa, preenchidos pelo celular, direto do pasto.',
           'rastro':'Como a Rastro passou a controlar frota e pneus pelo celular: cada pneu com história, desgaste calculado na medição e relatório do que trocar todo mês.'}
feitos=[]
for cid,(slug,nome,tit) in CASES.items():
    art=re.search(r'<(?:article|section) class="case" id="case-%s".*?</(?:article|section)>'%cid,t,re.S).group(0)
    setor=limpa(re.search(r'<p class="etiqueta">(.*?)</p>',art,re.S).group(1))
    h3=limpa(re.search(r'<h3>(.*?)</h3>',art,re.S).group(1))
    res=re.search(r'<div class="case-resultado">(.*?)</div>',art,re.S).group(1)
    num=limpa(re.search(r'<p class="resultado-numero">(.*?)</p>',res,re.S).group(1))
    resto=limpa(re.sub(r'<p class="resultado-numero">.*?</p>','',res,flags=re.S))
    hist=re.findall(r'<p class="mini">(.*?)</p>\s*<p>(.*?)</p>',art,re.S)
    antes,fez=limpa(hist[0][1]),limpa(hist[1][1])
    itens=[(limpa(a),limpa(b)) for a,b in re.findall(r'<li><strong>(.*?)</strong>(.*?)</li>',art,re.S)]
    U=f'https://genesiskore.com/cases/{slug}/'
    desc=DESCRICAO[cid]
    ld={"@context":"https://schema.org","@graph":[
      {"@type":["Organization","ProfessionalService"],"@id":"https://genesiskore.com/#organizacao","name":"GenesisKore","url":"https://genesiskore.com/","logo":"https://genesiskore.com/logo.png"},
      {"@type":"Article","@id":U+"#case","headline":h3,"description":f"{antes} {fez}","inLanguage":"pt-BR","url":U,"mainEntityOfPage":U,"articleSection":setor,
       "image":"https://genesiskore.com/previa-link.png","datePublished":"2026-11-10","dateModified":"2026-11-10",
       "author":{"@id":"https://genesiskore.com/#organizacao"},"publisher":{"@id":"https://genesiskore.com/#organizacao"},
       "about":[{"@type":"Thing","name":"sistema sob medida"},{"@type":"Thing","name":setor}]},
      {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"GenesisKore","item":"https://genesiskore.com/"},
        {"@type":"ListItem","position":2,"name":"Sistemas sob medida","item":"https://genesiskore.com/sistemas-sob-medida/"},
        {"@type":"ListItem","position":3,"name":nome,"item":U}]}]}
    outros=' · '.join(f'<a href="../{s}/">{n}</a>' for k,(s,n,_) in CASES.items() if k!=cid)
    lis='\n'.join(f'        <section class="produto">\n            <h3>{a}</h3>\n            <p>{b}</p>\n        </section>' for a,b in itens)
    insta='\n        <p class="suave"><a href="https://www.instagram.com/auth.br/" target="_blank" rel="noopener noreferrer">Ver a AUTH no Instagram</a></p>' if cid=='auth' else ''
    # 13/11/2026: a página da AUTH leva as telas reais (dados de exemplo) e o depoimento do fundador,
    # recomendação pública no LinkedIn em 29/10/2026. Texto dele, sem correção.
    extra='''
        <p><video muted loop playsinline controls preload="none" poster="/tela-auth-fila.webp" width="1006" height="948" style="max-width:100%;height:auto;background:#000" aria-label="Vídeo sem som da plataforma da AUTH: a fila de autenticação, o checklist da peça, o certificado emitido e a conferência pelo celular"><source src="/tela-auth.mp4" type="video/mp4"><source src="/tela-auth.webm" type="video/webm"></video></p>
        <p class="suave">A plataforma da AUTH em uso: fila, checklist, certificado e conferência pelo celular. Dados de exemplo.</p>
        <h2>O que o fundador da AUTH diz</h2>
        <blockquote>&ldquo;A Genesis Kore tornou nossos processos na AUTH muito mais rápidos, completos e seguros.&rdquo;</blockquote>
        <p>&ldquo;Iniciamos com o processo de automatização da emissão dos Certificados AUTH, onde isso tornou-se possível com o trabalho executado com total excelência e compreensão do Felipe Concílio, após o Emissor de Certificados AUTH, os contatamos novamente para o desenvolvimento do sistema interno operacional da equipe de autenticação e sistema de administração geral, onde o resultado seguiu a mesma lógica, excelência do total.&rdquo;</p>
        <p>&ldquo;E no momento, estão trabalhando no desenvolvimento da plataforma geral de autenticações da AUTH, após mostrarem responsabilidade, comprometimento e expertise técnica nos projetos propostos.&rdquo;</p>
        <p class="suave">Theodoro Janz, fundador da AUTH. Recomendação publicada no LinkedIn em 29/10/2026.</p>''' if cid=='auth' else ''
    pg=f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nome}: {tit[0].lower()+tit[1:]} | GenesisKore</title>
    <meta name="description" content="{html.escape(desc,quote=True)}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
    <meta name="theme-color" content="#000000">
    <link rel="canonical" href="{U}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{U}">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:title" content="{h3} | GenesisKore">
    <meta property="og:description" content="{num} {resto}">
    <meta property="og:image" content="https://genesiskore.com/previa-link.png">
    <link rel="icon" type="image/png" href="/icone-tema-claro.png?v=1" media="(prefers-color-scheme: light)">
    <link rel="icon" type="image/png" href="/icone-tema-escuro.png?v=1" media="(prefers-color-scheme: dark)">
    <link rel="help" type="text/plain" href="https://genesiskore.com/llms.txt">
    <!-- Gerada do texto do case na página inicial (10/11/2026). Mudou lá, mude aqui. -->
    <script type="application/ld+json">
{json.dumps(ld,ensure_ascii=False,indent=2)}
    </script>
    {estilo}
</head>
<body>
    <header>
        <a href="/" class="marca" aria-label="GenesisKore, página inicial"><img src="/logo.webp" alt="" width="40" height="44"><span>GENESISKORE</span></a>
        <nav aria-label="Páginas"><a href="/sistemas-sob-medida/">Sistemas</a><a href="/consultoria/">Consultoria</a><a href="/contato/">Contato</a></nav>
    </header>
    <main>
        <p class="etiqueta">Case · {setor}</p>
        <h1>{h3}</h1>
        <blockquote>{num} {resto}</blockquote>{extra}

        <h2>Antes</h2>
        <p>{antes}</p>

        <h2>O que a GenesisKore fez</h2>
        <p>{fez}</p>

        <h2>O que o sistema faz</h2>
{lis}{insta}

        <h2>Como um projeto assim começa</h2>
        <p>Com uma conversa de diagnóstico, que não custa nada. Você conta como o trabalho acontece hoje, e a gente diz o que vale automatizar e o que não vale. A proposta vem com preço fechado, em três opções, e a primeira parte entra em uso em até 2 semanas. O passo a passo está na página dos <a href="/sistemas-sob-medida/">Sistemas sob medida</a>.</p>
        <a class="botao" href="/conversar/">Quero conversar</a>

        <h2>Outros projetos</h2>
        <p>{outros}</p>
    </main>
    <footer>
        <a href="/">Início</a><a href="/sistemas-sob-medida/">Sistemas</a><a href="/consultoria/">Consultoria</a><a href="/sobre/">Sobre</a><a href="/privacidade/">Privacidade</a>
        <p>© 2026 GenesisKore. Sistemas sob medida e consultoria de gestão.</p>
    </footer>
    <script src="/contagem.js" defer></script>
</body>
</html>
'''
    os.makedirs(f'cases/{slug}',exist_ok=True)
    open(f'cases/{slug}/index.html','w',encoding='utf-8').write(pg)
    feitos.append((slug,nome,len(itens),desc))
for f in feitos: print(f)
