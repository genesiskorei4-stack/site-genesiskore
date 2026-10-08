/*
 * GenesisKore, site institucional. Refeito em 07/10/2026 junto com o HTML e o CSS.
 * Sem biblioteca nenhuma. O que mora aqui: o topo de vidro que some ao descer e volta ao
 * subir, o menu do celular, a entrada suave das seções, os avisos que passam no hero, os
 * números que contam, a calculadora, as abas dos cases, a linha do tempo do processo e o
 * formulário de diagnóstico, que manda para o webhook do n8n.
 *
 * Quem pede menos movimento no sistema recebe tudo parado e já no lugar.
 */

const WEBHOOK_DIAGNOSTICO = 'https://n8n.srv1249694.hstgr.cloud/webhook/401bcc95-ad5d-4576-89f9-1ecb550fa667';

const menosMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const temMouse = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
const rolagem = menosMovimento ? 'auto' : 'smooth';

const reais = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(v);
const numero = (v) => new Intl.NumberFormat('pt-BR').format(v);
const fundoEscuro = (el) => !!el && el.matches('.escuro, .rodape');

/*
 * De onde o lead veio. O link da bio do Instagram é `genesiskore.com/?origem=instagram`, e a
 * etiqueta segue no formulário até o CRM. Sem etiqueta, o navegador interno do Instagram
 * costuma deixar `instagram.com` como página anterior, e o LinkedIn deixa `linkedin.com` ou
 * `lnkd.in`, que é como o post da empresa leva ao site sem `?origem` no texto. Guardada na sessão porque a pessoa
 * pode navegar pela página antes de preencher, e o endereço perde o `?` quando ela clica num
 * link de seção.
 */
const origemDoLead = (() => {
    const limpar = (v) => String(v || '').toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 40);
    const params = new URLSearchParams(location.search);
    let origem = limpar(params.get('origem') || params.get('utm_source'));
    if (!origem && /instagram\./i.test(document.referrer)) origem = 'instagram';
    if (!origem && /(linkedin\.|lnkd\.in)/i.test(document.referrer)) origem = 'linkedin';
    // Quem chega recomendado por um assistente de IA (ChatGPT, Perplexity, Claude, Gemini, Copilot) vira 'ia'.
    if (!origem && /(chatgpt\.com|openai\.com|perplexity\.ai|claude\.ai|gemini\.google|copilot\.microsoft)/i.test(document.referrer)) origem = 'ia';
    if (/^(chatgptcom|perplexity|claudeai|gemini|copilot)/.test(origem)) origem = 'ia';
    try {
        if (origem) sessionStorage.setItem('origem', origem);
        else origem = sessionStorage.getItem('origem') || '';
    } catch { /* navegação privada sem armazenamento: vale só o que veio no endereço */ }
    return origem || 'direto';
})();

/* ------------------------------------------------------------ elementos */

const topo = document.getElementById('topo');
const botaoMenu = document.getElementById('botaoMenu');
const menuCelular = document.getElementById('menuCelular');
const ctaFixo = document.getElementById('ctaFixo');
const abertura = document.getElementById('inicio');
const fechamento = document.getElementById('contato');
const janela = document.getElementById('leadModal');
const secoes = [...document.querySelectorAll('main > section, .rodape')];
const linksMenu = [...document.querySelectorAll('.menu-largo a[href^="#"]')];
const secoesMenu = linksMenu.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);

/* ------------------------------------------------------------ menu do celular */

const menuAberto = () => !!menuCelular && menuCelular.classList.contains('aberto');

function abrirMenu() {
    menuCelular.classList.add('aberto');
    botaoMenu.setAttribute('aria-expanded', 'true');
    botaoMenu.setAttribute('aria-label', 'Fechar menu');
    topo.classList.add('menu-aberto');
    topo.classList.remove('escondido');
    document.body.classList.add('travado');
}

function fecharMenu() {
    if (!menuAberto()) return;
    menuCelular.classList.remove('aberto');
    botaoMenu.setAttribute('aria-expanded', 'false');
    botaoMenu.setAttribute('aria-label', 'Abrir menu');
    topo.classList.remove('menu-aberto');
    document.body.classList.remove('travado');
}

if (botaoMenu && menuCelular) {
    botaoMenu.addEventListener('click', () => (menuAberto() ? fecharMenu() : abrirMenu()));
    menuCelular.querySelectorAll('a').forEach((link) => link.addEventListener('click', fecharMenu));
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && menuAberto()) {
            fecharMenu();
            botaoMenu.focus();
        }
    });
}

/* ------------------------------------------------------------ rolagem: topo, botão fixo, linha do tempo */

const passos = document.getElementById('passos');
const itensPasso = passos ? [...passos.querySelectorAll('.passo')] : [];

// A linha do tempo vai do primeiro marco até o último, não até o fim do texto.
function medirTrilho() {
    if (!passos || itensPasso.length < 2) return;
    const altura = itensPasso[itensPasso.length - 1].offsetTop - itensPasso[0].offsetTop;
    passos.style.setProperty('--trilho', `${altura}px`);
}

function linhaDoTempo() {
    if (!passos) return;
    const alvo = window.innerHeight * 0.62;
    const caixa = passos.getBoundingClientRect();
    const trilho = parseFloat(passos.style.getPropertyValue('--trilho')) || caixa.height;
    const feito = Math.min(1, Math.max(0, (alvo - caixa.top - 12) / trilho));
    passos.style.setProperty('--progresso', feito.toFixed(4));
    itensPasso.forEach((passo) => {
        passo.classList.toggle('ativo', passo.getBoundingClientRect().top + 12 <= alvo);
    });
}

function secaoNaAltura(y) {
    for (const secao of secoes) {
        const caixa = secao.getBoundingClientRect();
        if (caixa.height && caixa.top <= y && caixa.bottom > y) return secao;
    }
    return null;
}

let ultimoY = window.scrollY;
let rolagemAgendada = false;

function aoRolar() {
    rolagemAgendada = false;
    const y = window.scrollY;

    // O topo copia a cor da seção que está embaixo dele.
    const debaixoDoTopo = secaoNaAltura(topo.offsetHeight / 2);
    const claro = !!debaixoDoTopo && !fundoEscuro(debaixoDoTopo);
    topo.classList.toggle('claro', claro);
    topo.classList.toggle('solido', y > 10 && !claro);

    // Descendo, o topo sai do caminho. Subindo, volta.
    if (!menuAberto()) {
        const diferenca = y - ultimoY;
        if (y < 160) topo.classList.remove('escondido');
        else if (diferenca > 6) topo.classList.add('escondido');
        else if (diferenca < -6) topo.classList.remove('escondido');
    }
    if (Math.abs(y - ultimoY) > 6 || y < 160) ultimoY = y;

    const maximo = document.documentElement.scrollHeight - window.innerHeight;
    topo.style.setProperty('--lido', maximo > 0 ? (y / maximo).toFixed(4) : '0');

    // O botão fixo aparece depois da primeira tela e some no fechamento, onde já tem o grande.
    if (ctaFixo && abertura) {
        const passouAbertura = abertura.getBoundingClientRect().bottom < window.innerHeight * 0.4;
        const chegouNoFim = !!fechamento && fechamento.getBoundingClientRect().top < window.innerHeight * 0.85;
        ctaFixo.classList.toggle('visivel', passouAbertura && !chegouNoFim && !janela?.open);
        const debaixoDoBotao = secaoNaAltura(window.innerHeight - 44);
        ctaFixo.classList.toggle('sobre-claro', !!debaixoDoBotao && !fundoEscuro(debaixoDoBotao));
    }

    // No computador, o menu marca a seção que está sendo lida.
    let idAtual = null;
    secoesMenu.forEach((secao) => {
        if (secao.getBoundingClientRect().top <= window.innerHeight * 0.35) idAtual = secao.id;
    });
    linksMenu.forEach((a) => a.classList.toggle('ativo', a.getAttribute('href') === `#${idAtual}`));

    linhaDoTempo();
}

window.addEventListener('scroll', () => {
    if (!rolagemAgendada) {
        rolagemAgendada = true;
        requestAnimationFrame(aoRolar);
    }
}, { passive: true });

/* ------------------------------------------------------------ números que contam */

function contar(el, deNovo = false) {
    if (el.dataset.contado && !deNovo) return;
    el.dataset.contado = '1';
    const alvo = Number(el.dataset.contar);
    if (menosMovimento || !alvo) {
        el.textContent = numero(alvo);
        return;
    }
    const duracao = 1600;
    const inicio = performance.now();
    const passo = (agora) => {
        const p = Math.min(1, (agora - inicio) / duracao);
        el.textContent = numero(Math.round(alvo * (1 - Math.pow(1 - p, 4))));
        if (p < 1) requestAnimationFrame(passo);
    };
    el.textContent = '0';
    requestAnimationFrame(passo);
}

/* ------------------------------------------------------------ entrada suave, contadores e pausa */

const revelaveis = [...document.querySelectorAll('.revelar')];
const contadores = [...document.querySelectorAll('[data-contar]')];

// Irmãos entram um depois do outro, com uma diferença pequena.
revelaveis.forEach((el) => {
    const irmaos = [...el.parentElement.children].filter((c) => c.classList.contains('revelar'));
    const posicao = irmaos.indexOf(el);
    if (posicao > 0) el.style.setProperty('--atraso', `${Math.min(posicao, 5) * 0.08}s`);
});

if ('IntersectionObserver' in window) {
    const revelar = new IntersectionObserver((entradas) => {
        entradas.forEach((entrada) => {
            if (entrada.isIntersecting) {
                entrada.target.classList.add('visivel');
                revelar.unobserve(entrada.target);
            }
        });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revelaveis.forEach((el) => revelar.observe(el));

    if (!menosMovimento) contadores.forEach((el) => { el.textContent = '0'; });
    const observarContador = new IntersectionObserver((entradas) => {
        entradas.forEach((entrada) => {
            if (entrada.isIntersecting) {
                // Espera a seção terminar de subir antes de contar.
                setTimeout(() => contar(entrada.target), 250);
                observarContador.unobserve(entrada.target);
            }
        });
    }, { threshold: 0.6 });
    contadores.forEach((el) => observarContador.observe(el));

    // Hero, faixa de logos e fechamento só animam enquanto estão na tela.
    const pausar = new IntersectionObserver((entradas) => {
        entradas.forEach((entrada) => entrada.target.classList.toggle('parado', !entrada.isIntersecting));
    });
    document.querySelectorAll('[data-anima]').forEach((el) => pausar.observe(el));
} else {
    revelaveis.forEach((el) => el.classList.add('visivel'));
}

/* ------------------------------------------------------------ avisos ao vivo no hero */

const listaAvisos = document.getElementById('avisosLista');
const MENSAGENS = [
    'Cliente avisado da entrega',
    'Pedido conferido com o estoque',
    'Relatório do mês no seu e-mail',
    'Orçamento enviado em PDF',
    'Pagamento conferido no extrato',
    'Ficha do pneu atualizada',
    'Recibo enviado ao cliente',
    'Pedido lançado na planilha',
    'Certificado emitido com QR code',
];
const HORAS = ['agora', 'há 1 min', 'há 3 min', 'há 6 min'];
let proximaMensagem = 0;

function novoAviso() {
    if (document.hidden || abertura?.classList.contains('parado')) return;
    const item = document.createElement('li');
    item.className = 'aviso aviso-novo';
    item.innerHTML = '<span class="aviso-ponto"></span><span class="aviso-texto"></span><span class="aviso-hora"></span>';
    item.querySelector('.aviso-texto').textContent = MENSAGENS[proximaMensagem % MENSAGENS.length];
    proximaMensagem += 1;
    listaAvisos.prepend(item);

    // A lista inteira desce um degrau de uma vez, e o novo aviso entra por cima.
    const degrau = item.offsetHeight;
    listaAvisos.style.transition = 'none';
    listaAvisos.style.transform = `translateY(-${degrau}px)`;
    void listaAvisos.offsetHeight;
    listaAvisos.style.transition = '';
    listaAvisos.style.transform = '';

    [...listaAvisos.children].forEach((aviso, i) => {
        const hora = aviso.querySelector('.aviso-hora');
        if (hora) hora.textContent = HORAS[i] || '';
    });
    while (listaAvisos.children.length > 4) listaAvisos.lastElementChild.remove();
}

if (listaAvisos && !menosMovimento) setInterval(novoAviso, 2800);

/* ------------------------------------------------------------ calculadora */

const horas = document.getElementById('hoursSlider');
const salario = document.getElementById('salarySlider');
const horasRotulo = document.getElementById('hoursVal');
const salarioRotulo = document.getElementById('salaryVal');
const custoAno = document.getElementById('costResult');
const horasAno = document.getElementById('timeResult');

let custoMostrado = 76313;
let horasMostradas = 2640;
let quadroCalculadora = 0;

function preencherTrilho(input) {
    const pct = ((input.value - input.min) / (input.max - input.min)) * 100;
    input.style.setProperty('--pct', `${pct}%`);
}

function mostrarResultado() {
    custoAno.textContent = reais(Math.round(custoMostrado));
    horasAno.textContent = `${numero(Math.round(horasMostradas))}h`;
}

// A conta que a página explica embaixo do resultado: horas por dia × 22 dias × 12 meses,
// custo CLT de 1,85 vez o salário, jornada de 160 horas por mês.
function calcular(suave = true) {
    const h = Number(horas.value);
    const s = Number(salario.value);
    const horasPorAno = h * 22 * 12;
    const custo = Math.round(((s * 1.85) / 160) * horasPorAno);
    horasRotulo.textContent = `${h}h`;
    salarioRotulo.textContent = reais(s);
    preencherTrilho(horas);
    preencherTrilho(salario);

    cancelAnimationFrame(quadroCalculadora);
    if (!suave || menosMovimento) {
        custoMostrado = custo;
        horasMostradas = horasPorAno;
        mostrarResultado();
        return;
    }
    const custoDe = custoMostrado;
    const horasDe = horasMostradas;
    const inicio = performance.now();
    const passo = (agora) => {
        const p = Math.min(1, (agora - inicio) / 450);
        const e = 1 - Math.pow(1 - p, 3);
        custoMostrado = custoDe + (custo - custoDe) * e;
        horasMostradas = horasDe + (horasPorAno - horasDe) * e;
        mostrarResultado();
        if (p < 1) quadroCalculadora = requestAnimationFrame(passo);
    };
    quadroCalculadora = requestAnimationFrame(passo);
}

// A dica do site antigo: a barra das horas balança sozinha quando aparece, para mostrar que
// dá para arrastar. Para no primeiro toque.
function dicaDaBarra(input) {
    const original = Number(input.value);
    const amplitude = (input.max - input.min) * 0.08;
    const duracao = 3600;
    let quadro = 0;
    let inicio = null;
    let acabou = false;

    const parar = (voltar) => {
        if (acabou) return;
        acabou = true;
        cancelAnimationFrame(quadro);
        input.classList.remove('mexendo');
        if (voltar) {
            input.value = original;
            calcular(false);
        }
    };
    const passo = (agora) => {
        if (acabou) return;
        if (inicio === null) inicio = agora;
        const passou = agora - inicio;
        if (passou >= duracao) {
            parar(true);
            return;
        }
        input.value = Math.round(original + amplitude * Math.sin((2 * Math.PI * passou) / 1800));
        calcular(false);
        quadro = requestAnimationFrame(passo);
    };

    ['pointerdown', 'touchstart', 'keydown', 'focus'].forEach((evento) => {
        input.addEventListener(evento, () => parar(true), { once: true, passive: true });
    });

    const observar = new IntersectionObserver(([entrada]) => {
        if (!entrada.isIntersecting) return;
        observar.disconnect();
        setTimeout(() => {
            if (acabou) return;
            input.classList.add('mexendo');
            quadro = requestAnimationFrame(passo);
        }, 500);
    }, { threshold: 1 });
    observar.observe(input);
}

if (horas && salario) {
    horas.addEventListener('input', () => calcular(true));
    salario.addEventListener('input', () => calcular(true));
    calcular(false);
    if (!menosMovimento && 'IntersectionObserver' in window) dicaDaBarra(horas);
}

/* ------------------------------------------------------------ cases em abas */

const abasCases = document.getElementById('caseAbas');
const abas = abasCases ? [...abasCases.querySelectorAll('.case-aba')] : [];
const paineis = abas.map((aba) => document.getElementById(aba.getAttribute('aria-controls')));
const indicador = abasCases?.querySelector('.case-indicador');
const areaPaineis = document.getElementById('casePaineis');
let caseAtual = 0;

function posicionarIndicador() {
    const aba = abas[caseAtual];
    if (!aba || !indicador) return;
    indicador.style.setProperty('--largura-aba', `${aba.offsetWidth}px`);
    indicador.style.setProperty('--posicao-aba', `${aba.offsetLeft}px`);
}

function ativarCase(indice, { animar = true, rolar = false, focar = false } = {}) {
    if (!abas.length) return;
    const i = (indice + abas.length) % abas.length;
    const direcao = i >= caseAtual ? 1 : -1;

    abas.forEach((aba, k) => {
        const ativa = k === i;
        aba.setAttribute('aria-selected', String(ativa));
        aba.tabIndex = ativa ? 0 : -1;
        paineis[k].hidden = !ativa;
    });

    const painel = paineis[i];
    painel.classList.remove('entrando');
    if (animar && !menosMovimento) {
        painel.style.setProperty('--direcao', direcao);
        void painel.offsetWidth;
        painel.classList.add('entrando');
        painel.querySelectorAll('[data-contar]').forEach((el) => contar(el, true));
    }

    caseAtual = i;
    posicionarIndicador();

    // A aba escolhida aparece inteira na faixa, mesmo no celular.
    const aba = abas[i];
    const folga = parseFloat(getComputedStyle(abasCases).paddingLeft) || 0;
    abasCases.scrollTo({ left: Math.max(0, aba.offsetLeft - folga), behavior: rolagem });

    if (focar) aba.focus();
    if (rolar) {
        const topoDasAbas = abasCases.getBoundingClientRect().top;
        if (topoDasAbas < 0 || topoDasAbas > window.innerHeight * 0.5) {
            abasCases.scrollIntoView({ behavior: rolagem, block: 'start' });
        }
    }
}

if (abas.length) {
    abas.forEach((aba, i) => aba.addEventListener('click', () => ativarCase(i)));

    abasCases.addEventListener('keydown', (e) => {
        const teclas = { ArrowRight: caseAtual + 1, ArrowLeft: caseAtual - 1, Home: 0, End: abas.length - 1 };
        if (!(e.key in teclas)) return;
        e.preventDefault();
        ativarCase(teclas[e.key], { focar: true });
    });

    document.querySelectorAll('[data-proximo]').forEach((botao) => {
        botao.addEventListener('click', () => ativarCase(caseAtual + 1, { rolar: true }));
    });

    // No celular, deslizar o dedo para o lado troca de case.
    let toqueX = null;
    let toqueY = null;
    areaPaineis.addEventListener('touchstart', (e) => {
        toqueX = e.touches[0].clientX;
        toqueY = e.touches[0].clientY;
    }, { passive: true });
    areaPaineis.addEventListener('touchend', (e) => {
        if (toqueX === null) return;
        const dx = e.changedTouches[0].clientX - toqueX;
        const dy = e.changedTouches[0].clientY - toqueY;
        toqueX = null;
        if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) ativarCase(caseAtual + (dx < 0 ? 1 : -1));
    }, { passive: true });

    // Link direto para um case (genesiskore.com/#case-rastro) abre a aba certa.
    const abrirCaseDoEndereco = () => {
        const i = paineis.findIndex((p) => `#${p.id}` === window.location.hash);
        if (i < 0) return;
        ativarCase(i, { animar: false });
        document.getElementById('cases').scrollIntoView({ block: 'start' });
    };

    ativarCase(0, { animar: false });
    abrirCaseDoEndereco();
    window.addEventListener('hashchange', abrirCaseDoEndereco);
}

/* ------------------------------------------------------------ luz que segue o mouse */

if (temMouse) {
    document.querySelectorAll('.brilho').forEach((el) => {
        el.addEventListener('pointermove', (e) => {
            const caixa = el.getBoundingClientRect();
            el.style.setProperty('--mx', `${e.clientX - caixa.left}px`);
            el.style.setProperty('--my', `${e.clientY - caixa.top}px`);
        });
    });
}

/* ------------------------------------------------------------ medidas que dependem da fonte */

function remedir() {
    medirTrilho();
    posicionarIndicador();
    aoRolar();
}

window.addEventListener('resize', remedir);
document.fonts?.ready.then(remedir);
remedir();

/* ------------------------------------------------------------ janela do diagnóstico */

const form = document.getElementById('leadForm');
const sucesso = document.getElementById('formSuccessMessage');
const erroGeral = document.getElementById('formErrorMessage');
const botaoEnviar = document.getElementById('submitBtn');

function abrirDiagnostico() {
    if (!janela) return;
    fecharMenu();
    janela.classList.remove('fechando');
    if (typeof janela.showModal === 'function') {
        if (!janela.open) janela.showModal();
    } else {
        janela.setAttribute('open', '');
    }
    document.body.classList.add('travado');
    ctaFixo?.classList.remove('visivel');
    const primeiro = document.getElementById('nome');
    // No celular o teclado abrindo sozinho cobre metade da janela; só foca no computador.
    if (primeiro && window.matchMedia('(min-width: 720px)').matches) primeiro.focus();
}

function fecharDeVez() {
    janela.classList.remove('fechando');
    if (typeof janela.close === 'function') {
        if (janela.open) janela.close();
    } else {
        janela.removeAttribute('open');
        janela.dispatchEvent(new Event('close'));
    }
}

// A janela desce antes de sumir, em vez de desaparecer de uma vez.
function fecharDiagnostico() {
    if (!janela || !janela.open || janela.classList.contains('fechando')) return;
    if (menosMovimento) {
        fecharDeVez();
        return;
    }
    janela.classList.add('fechando');
    const reserva = setTimeout(fecharDeVez, 450);
    janela.addEventListener('animationend', () => {
        clearTimeout(reserva);
        fecharDeVez();
    }, { once: true });
}

if (janela) {
    janela.addEventListener('cancel', (e) => {
        e.preventDefault();
        fecharDiagnostico();
    });
    janela.addEventListener('close', () => {
        document.body.classList.remove('travado');
        // Depois de um envio, a próxima abertura começa do formulário limpo.
        if (!sucesso.hidden) {
            sucesso.hidden = true;
            form.hidden = false;
            form.reset();
        }
        aoRolar();
    });
    // Toque fora da caixa (no fundo escurecido) fecha.
    janela.addEventListener('click', (e) => {
        if (e.target !== janela) return;
        const caixa = janela.getBoundingClientRect();
        const fora = e.clientX < caixa.left || e.clientX > caixa.right || e.clientY < caixa.top || e.clientY > caixa.bottom;
        if (fora) fecharDiagnostico();
    });
}

document.querySelectorAll('[data-abrir-diagnostico]').forEach((b) => b.addEventListener('click', abrirDiagnostico));
document.querySelectorAll('[data-fechar-diagnostico]').forEach((b) => b.addEventListener('click', fecharDiagnostico));
document.getElementById('fecharDiagnostico')?.addEventListener('click', fecharDiagnostico);

/* ------------------------------------------------------------ formulário */

const CAMPOS = ['nome', 'empresa', 'whatsapp', 'email', 'faturamento', 'gargalo', 'consent'];

function limparErros() {
    CAMPOS.forEach((id) => {
        document.getElementById(id)?.classList.remove('field-invalid');
        const erro = document.getElementById(`${id}Error`);
        if (erro) erro.textContent = '';
    });
}

function marcarErro(id, mensagem) {
    document.getElementById(id)?.classList.add('field-invalid');
    const erro = document.getElementById(`${id}Error`);
    if (erro) erro.textContent = mensagem;
}

function validar(d) {
    limparErros();
    const erros = [];
    if (!d.nome || d.nome.length < 2) erros.push(['nome', 'Escreva seu nome.']);
    if (!d.empresa || d.empresa.length < 2) erros.push(['empresa', 'Escreva o nome da empresa.']);
    if (!d.whatsapp || d.whatsapp.replace(/\D/g, '').length < 10) erros.push(['whatsapp', 'Coloque o WhatsApp com DDD.']);
    if (!d.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) erros.push(['email', 'Confira o e-mail.']);
    if (!d.faturamento) erros.push(['faturamento', 'Escolha uma faixa de faturamento.']);
    if (!d.gargalo || d.gargalo.length < 10) erros.push(['gargalo', 'Conte um pouco mais sobre a tarefa.']);
    if (!d.consent) erros.push(['consent', 'Marque a autorização para a gente poder entrar em contato.']);
    erros.forEach(([id, msg]) => marcarErro(id, msg));
    if (erros.length) document.getElementById(erros[0][0])?.focus();
    return erros.length === 0;
}

function mascaraTelefone(bruto) {
    const d = bruto.replace(/\D/g, '').slice(0, 11);
    if (d.length <= 2) return d;
    if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
    if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
    return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}

document.getElementById('whatsapp')?.addEventListener('input', (e) => {
    e.target.value = mascaraTelefone(e.target.value);
});

CAMPOS.forEach((id) => {
    const campo = document.getElementById(id);
    if (!campo) return;
    const evento = id === 'consent' || campo.tagName === 'SELECT' ? 'change' : 'input';
    campo.addEventListener(evento, () => {
        campo.classList.remove('field-invalid');
        const erro = document.getElementById(`${id}Error`);
        if (erro) erro.textContent = '';
    });
});

function mostrarSucesso() {
    form.hidden = true;
    sucesso.hidden = false;
    sucesso.querySelector('button')?.focus();
}

form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (botaoEnviar.disabled) return;
    erroGeral.hidden = true;

    const dados = {
        nome: document.getElementById('nome').value.trim(),
        empresa: document.getElementById('empresa').value.trim(),
        whatsapp: document.getElementById('whatsapp').value.trim(),
        email: document.getElementById('email').value.trim(),
        faturamento: document.getElementById('faturamento').value,
        gargalo: document.getElementById('gargalo').value.trim(),
        consent: document.getElementById('consent').checked,
        website: document.getElementById('website')?.value || '',
        origem: origemDoLead,
    };

    if (!validar(dados)) return;

    // Campo escondido preenchido é robô: finge que enviou e não dispara o workflow, que
    // chamaria a IA e mandaria e-mail para um endereço inventado.
    if (dados.website) {
        mostrarSucesso();
        return;
    }

    botaoEnviar.disabled = true;
    botaoEnviar.textContent = 'Enviando…';
    try {
        const resposta = await fetch(WEBHOOK_DIAGNOSTICO, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados),
        });
        if (!resposta.ok) throw new Error(`Falha ao enviar (${resposta.status})`);
        mostrarSucesso();
    } catch (erro) {
        console.error('Erro ao enviar o diagnóstico:', erro);
        erroGeral.hidden = false;
    } finally {
        botaoEnviar.disabled = false;
        botaoEnviar.textContent = 'Enviar';
    }
});
