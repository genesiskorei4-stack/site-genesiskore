/*
 * GenesisKore, site institucional. Refeito em 07/10/2026 junto com o HTML e o CSS.
 * Sem biblioteca nenhuma. O que mora aqui: o topo de vidro que some ao descer e volta ao
 * subir, o menu do celular, a entrada suave das seções, os avisos que passam no hero, os
 * números que contam, a calculadora, as abas dos cases, a linha do tempo do processo, o
 * diagnóstico rápido (21/10/2026) e o formulário de diagnóstico, que manda para o webhook do n8n.
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
 * De onde o lead veio e a contagem de visitas moram no contagem.js, que carrega antes deste
 * arquivo em toda página. Se ele não carregar, o site segue normal e a origem vira 'direto'.
 */
const origemDoLead = window.gkOrigem || 'direto';
const registrarEvento = (evento) => {
    try { window.gkContar?.(evento); } catch { /* contagem nunca quebra o site */ }
};

/* ------------------------------------------------------------ elementos */

const topo = document.getElementById('topo');
const botaoMenu = document.getElementById('botaoMenu');
const menuCelular = document.getElementById('menuCelular');
const ctaFixo = document.getElementById('ctaFixo');
const abertura = document.getElementById('inicio');
const fechamento = document.getElementById('contato');
const janela = document.getElementById('leadModal');
const secaoDiagnostico = document.getElementById('diagnostico');
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
        // No diagnóstico rápido ele também sai: o resultado tem o próprio botão, e o fixo cobriria as respostas.
        const caixaQuiz = secaoDiagnostico?.getBoundingClientRect();
        const noDiagnostico = !!caixaQuiz && caixaQuiz.top < window.innerHeight * 0.9 && caixaQuiz.bottom > window.innerHeight * 0.1;
        ctaFixo.classList.toggle('visivel', passouAbertura && !chegouNoFim && !noDiagnostico && !janela?.open);
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

/* ------------------------------------------------------------ diagnóstico rápido */

/*
 * Seis perguntas, uma por vez, e um resultado montado por regra simples, sem IA. As perguntas
 * e as opções estão no HTML (seção #diagnostico); aqui ficam só as regras do resultado.
 * Nada é enviado ao terminar. As respostas só saem do navegador por um destes dois caminhos:
 * o formulário da conversa (vão como texto no campo `gargalo`, que o n8n já lê) ou o pedido do
 * Raio X em PDF (27/10/2026), que manda as respostas e o contato para a plataforma, e ela monta
 * o Raio X pelas mesmas regras (lib/diagnostico/raio-x-do-site.ts) e devolve o link.
 */

const quiz = document.getElementById('quiz');
const perguntasQuiz = quiz ? [...quiz.querySelectorAll('.quiz-pergunta')] : [];
const quizPasso = document.getElementById('quizPasso');
const quizBarra = document.getElementById('quizBarra');
const quizVoltar = document.getElementById('quizVoltar');
const quizResultado = document.getElementById('quizResultado');
const quizConversar = document.getElementById('quizConversar');

// chave da pergunta -> { valor, resumo }
let respostas = {};
let perguntaAtual = 0;
let quizComecou = false;
// Quando a primeira resposta foi dada. Vai junto no pedido do Raio X, que recusa resposta rápida demais.
let quizInicio = 0;
// O bloco de texto que vai junto no formulário. Vazio quando não há diagnóstico (ou a pessoa tirou).
let diagnosticoTexto = '';
let faturamentoDoQuiz = '';

// O formulário tem quatro faixas e o diagnóstico tem cinco: as duas de cima viram "Acima de R$ 500 mil".
const FAIXA_NO_FORMULARIO = {
    'ate-50k': 'ate-50k',
    '50k-150k': '50k-150k',
    '150k-500k': '150k-500k',
    '500k-2m': 'mais-500k',
    'mais-2m': 'mais-500k',
};

const PONTOS = {
    pedido: {
        whatsapp: 'O pedido chega pelo WhatsApp e alguém precisa ler, copiar e digitar de novo em outro lugar. Cada cópia gasta tempo e abre espaço para item errado ou pedido esquecido no meio da conversa.',
        telefone: 'O pedido chega por telefone e depende de quem atendeu anotar certo. Se a anotação se perde, o pedido some junto, e ninguém fica sabendo até o cliente reclamar.',
        'sistema-manual': 'O pedido já entra num sistema, mas alguém ainda confere à mão. Essa conferência é boa candidata a sair da mão da equipe: o sistema confere sozinho e só chama alguém quando algo não bate.',
    },
    status: {
        '2-5': 'De 2 a 5 horas por semana respondendo como está o pedido dão de 8 a 20 horas por mês de alguém parado. A resposta podia chegar ao cliente sozinha, por e-mail ou WhatsApp, a cada etapa do pedido.',
        'mais-5': 'Mais de 5 horas por semana respondendo como está o pedido passam de 20 horas por mês. É hora de equipe paga para repetir uma informação que já está anotada em algum lugar.',
        'nao-sei': 'Ninguém mediu quanto tempo vai em responder como está o pedido. Vale anotar por uma semana quantas vezes alguém para o que está fazendo para isso. É o primeiro número que a gente pediria na conversa.',
    },
    lucro: {
        cabeca: 'O lucro por produto está na cabeça, não numa conta. Dá para vender mais num mês e ganhar menos sem perceber, porque o produto que mais sai nem sempre é o que mais deixa dinheiro.',
        nao: 'Você sabe quanto entra, mas não quanto sobra em cada produto ou cliente. Os dados para essa conta já passam pela empresa, na nota fiscal, na planilha e no extrato. Falta juntar.',
    },
    pessoa: {
        para: 'Quando a pessoa-chave falta, a operação para. O processo mora na cabeça dela e sai junto nas férias, numa doença ou num pedido de demissão.',
        dono: 'A pessoa-chave é você. Enquanto a empresa precisar de você para conferir, lembrar e responder, é para isso que vai o seu tempo.',
    },
};

const PONTO_ATRASA = 'Quando a pessoa-chave falta, a operação atrasa. Com o passo a passo dentro de um sistema, quem cobre a falta sabe o que fazer sem ligar para ninguém.';
const PONTO_EM_ORDEM = 'Pelas suas respostas, pedido, atendimento, lucro e equipe já estão bem resolvidos. Pode ser que você não precise de sistema novo agora.';
const PONTO_SOBRA = 'Se ainda sobra trabalho repetido, procure nas tarefas pequenas que ninguém mede: relatório montado à mão, documento refeito, dado copiado de uma planilha para outra.';

// Regra da casa: abaixo de R$ 150 mil por mês, dizer com franqueza o que ele não precisa comprar.
const FRANQUEZA = {
    'ate-50k': 'Uma coisa com franqueza: com faturamento de até R$ 50 mil por mês, um sistema sob medida provavelmente custaria mais do que o problema. Uma ferramenta pronta, como o Bling ou o Omie, resolve pedido, estoque e financeiro por uma mensalidade. Se quiser, a gente conversa assim mesmo e indica qual serve para o seu caso, sem proposta nenhuma.',
    '50k-150k': 'Uma coisa com franqueza: com faturamento entre R$ 50 mil e R$ 150 mil por mês, talvez ainda não seja hora de sistema sob medida, e uma ferramenta pronta, como o Bling ou o Omie, pode bastar. Se uma tarefa específica come horas da equipe toda semana, vale a conversa para ver se um projeto pequeno se paga. Se não se pagar, a gente diz.',
};

function montarResultado(r) {
    const principais = ['pedido', 'status', 'lucro', 'pessoa']
        .map((chave) => PONTOS[chave][r[chave]?.valor])
        .filter(Boolean);
    const pontos = [...principais];
    if (pontos.length < 2 && r.pessoa?.valor === 'atrasa') pontos.push(PONTO_ATRASA);
    if (!principais.length) pontos.unshift(PONTO_EM_ORDEM);
    if (pontos.length < 2) pontos.push(PONTO_SOBRA);
    return {
        titulo: principais.length ? 'Onde provavelmente você perde' : 'Sua operação parece em ordem',
        pontos: pontos.slice(0, 4),
        franqueza: FRANQUEZA[r.faturamento?.valor] || '',
    };
}

function textoDoDiagnostico(r) {
    const linhas = perguntasQuiz
        .filter((p) => r[p.dataset.chave])
        .map((p) => `${p.dataset.rotulo}: ${r[p.dataset.chave].resumo}`);
    return ['Diagnóstico rápido do site', ...linhas].join('\n');
}

function atualizarBarra(feitas) {
    if (quizBarra) quizBarra.style.transform = `scaleX(${feitas / perguntasQuiz.length})`;
}

function mostrarPergunta(i, focar = true) {
    perguntaAtual = i;
    perguntasQuiz.forEach((p, k) => { p.hidden = k !== i; });
    quizResultado.hidden = true;
    quizVoltar.hidden = i === 0;
    quizPasso.textContent = `Pergunta ${i + 1} de ${perguntasQuiz.length}`;
    atualizarBarra(i);
    if (focar) perguntasQuiz[i].querySelector('h3')?.focus({ preventScroll: true });
}

function mostrarResultadoQuiz() {
    const { titulo, pontos, franqueza } = montarResultado(respostas);
    perguntasQuiz.forEach((p) => { p.hidden = true; });
    quizVoltar.hidden = true;
    quizPasso.textContent = 'Resultado';
    atualizarBarra(perguntasQuiz.length);

    document.getElementById('quizResultadoTitulo').textContent = titulo;
    const lista = document.getElementById('quizPontos');
    lista.replaceChildren(...pontos.map((texto) => {
        const item = document.createElement('li');
        item.textContent = texto;
        return item;
    }));
    const franco = document.getElementById('quizFranco');
    franco.textContent = franqueza;
    franco.hidden = !franqueza;
    quizConversar.textContent = franqueza ? 'Quero conversar assim mesmo' : 'Prefiro só conversar';
    prepararRaio();

    diagnosticoTexto = textoDoDiagnostico(respostas);
    faturamentoDoQuiz = FAIXA_NO_FORMULARIO[respostas.faturamento?.valor] || '';
    quizResultado.hidden = false;
    document.getElementById('quizResultadoTitulo').focus({ preventScroll: true });
    quiz.scrollIntoView({ behavior: rolagem, block: 'start' });
    registrarEvento('diagnostico_concluido');
}

function responder(botao) {
    const pergunta = botao.closest('.quiz-pergunta');
    pergunta.querySelectorAll('.quiz-opcao').forEach((b) => b.setAttribute('aria-pressed', String(b === botao)));
    respostas[pergunta.dataset.chave] = { valor: botao.dataset.valor, resumo: botao.dataset.resumo };
    if (!quizComecou) {
        quizComecou = true;
        quizInicio = Date.now();
        registrarEvento('diagnostico_iniciado');
    }
    // Um respiro curto para a escolha aparecer marcada antes de trocar de pergunta.
    setTimeout(() => {
        if (perguntaAtual < perguntasQuiz.length - 1) mostrarPergunta(perguntaAtual + 1);
        else mostrarResultadoQuiz();
    }, menosMovimento ? 0 : 220);
}

function refazerQuiz() {
    respostas = {};
    quizComecou = false;
    quizInicio = 0;
    diagnosticoTexto = '';
    faturamentoDoQuiz = '';
    quiz.querySelectorAll('.quiz-opcao').forEach((b) => b.setAttribute('aria-pressed', 'false'));
    mostrarPergunta(0);
}

/* ------------------------------------------------------------ Raio X em PDF */

const RAIO_ENDERECO = 'https://app.genesiskore.com/api/diagnostico';
const raioForm = document.getElementById('raioForm');
const raioPronto = document.getElementById('raioPronto');
const raioErro = document.getElementById('raioErro');
const raioEnviar = document.getElementById('raioEnviar');
const RAIO_FALHOU = 'Não deu para montar o Raio X agora. Tente de novo em instantes, ou escreva para contato@genesiskore.com.';
const EMAIL_DO_RAIO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

// Cada campo e a regra dele. Devolve a mensagem de erro, ou vazio quando está certo.
const RAIO_CAMPOS = {
    raioNome: (v) => (v.trim().length >= 2 ? '' : 'Escreva seu nome. Pode ser só o primeiro.'),
    raioEmpresa: (v) => (v.trim().length >= 2 ? '' : 'Escreva o nome da empresa.'),
    raioEmail: (v) => (EMAIL_DO_RAIO.test(v.trim()) ? '' : 'O Raio X vai para um e-mail. Confira o @ e o final, como voce@empresa.com.br.'),
    raioWhatsapp: (v) => {
        const n = v.replace(/\D/g, '');
        return !n || (n.length >= 10 && n.length <= 11) ? '' : 'Coloque o DDD e o número, como (11) 98765-4321.';
    },
};

function conferirCampoDoRaio(id) {
    const campo = document.getElementById(id);
    const erro = id === 'raioConsent' ? (campo.checked ? '' : 'Marque a caixa para autorizar. Sem ela a gente não pode montar o Raio X.') : RAIO_CAMPOS[id](campo.value);
    document.getElementById(`${id}Erro`).textContent = erro;
    campo.classList.toggle('field-invalid', Boolean(erro));
    campo.setAttribute('aria-invalid', String(Boolean(erro)));
    return !erro;
}

// Cada resultado novo começa com o pedido limpo, mas sem apagar o que a pessoa já digitou.
function prepararRaio() {
    if (!raioForm) return;
    raioForm.hidden = false;
    raioPronto.hidden = true;
    raioErro.textContent = '';
}

function respostasDoQuiz() {
    const saida = {};
    for (const [chave, r] of Object.entries(respostas)) saida[chave] = r.valor;
    return saida;
}

async function pedirRaio(e) {
    e.preventDefault();
    const ids = [...Object.keys(RAIO_CAMPOS), 'raioConsent'];
    const certos = ids.map(conferirCampoDoRaio);
    if (certos.includes(false)) {
        document.getElementById(ids[certos.indexOf(false)]).focus();
        return;
    }
    raioErro.textContent = '';
    raioEnviar.disabled = true;
    raioEnviar.textContent = 'Montando o Raio X…';
    const pedido = {
        nome: document.getElementById('raioNome').value.trim(),
        empresa: document.getElementById('raioEmpresa').value.trim(),
        email: document.getElementById('raioEmail').value.trim(),
        whatsapp: document.getElementById('raioWhatsapp').value.trim(),
        consentimento: true,
        respostas: respostasDoQuiz(),
        origem: origemDoLead,
        site: document.getElementById('raioSite').value,
        ms: quizInicio ? Date.now() - quizInicio : undefined,
    };
    try {
        // text/plain, como a contagem: sem preflight de CORS. A plataforma lê o JSON do corpo.
        const resposta = await fetch(RAIO_ENDERECO, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=UTF-8' }, body: JSON.stringify(pedido) });
        const corpo = await resposta.json().catch(() => ({}));
        if (!resposta.ok || !corpo.ok || !corpo.url) {
            // A frase da plataforma é escrita para quem lê (limite, campo errado). Sem ela, a frase padrão.
            raioErro.textContent = corpo.erro || RAIO_FALHOU;
            return;
        }
        document.getElementById('raioProntoEmpresa').textContent = pedido.empresa;
        document.getElementById('raioAbrir').href = corpo.url;
        document.getElementById('raioPdf').href = corpo.pdf;
        raioForm.hidden = true;
        raioPronto.hidden = false;
        raioPronto.focus({ preventScroll: true });
        raioPronto.scrollIntoView({ behavior: rolagem, block: 'center' });
        // Quem pede o Raio X deixou o contato: no funil conta como formulário enviado.
        registrarEvento('formulario_enviado');
    } catch {
        // Sem rede, ou a plataforma fora do ar. A mensagem do navegador ("Failed to fetch") não serve a ninguém.
        raioErro.textContent = RAIO_FALHOU;
    } finally {
        raioEnviar.disabled = false;
        raioEnviar.textContent = 'Gerar meu Raio X';
    }
}

if (raioForm) {
    raioForm.addEventListener('submit', pedirRaio);
    for (const id of [...Object.keys(RAIO_CAMPOS), 'raioConsent']) {
        const campo = document.getElementById(id);
        // Confere ao sair do campo, e de novo a cada mudança enquanto ele estiver marcado com erro.
        campo.addEventListener('blur', () => { if (campo.value || id === 'raioConsent') conferirCampoDoRaio(id); });
        campo.addEventListener(id === 'raioConsent' ? 'change' : 'input', () => { if (campo.classList.contains('field-invalid')) conferirCampoDoRaio(id); });
    }
}

if (quiz && perguntasQuiz.length && quizResultado) {
    quiz.addEventListener('click', (e) => {
        const opcao = e.target.closest('.quiz-opcao');
        if (opcao) responder(opcao);
    });
    quizVoltar.addEventListener('click', () => {
        if (perguntaAtual > 0) mostrarPergunta(perguntaAtual - 1);
    });
    document.getElementById('quizRefazer')?.addEventListener('click', refazerQuiz);
    quizConversar.addEventListener('click', () => abrirDiagnostico());
    mostrarPergunta(0, false);
}

/* ------------------------------------------------------------ janela do formulário */

const form = document.getElementById('leadForm');
const sucesso = document.getElementById('formSuccessMessage');
const erroGeral = document.getElementById('formErrorMessage');
const botaoEnviar = document.getElementById('submitBtn');
const caixaDiagnostico = document.getElementById('formDiagnostico');

// Mostra no formulário as respostas do diagnóstico que vão junto, e já escolhe a faixa de faturamento.
function prepararFormulario() {
    if (!caixaDiagnostico) return;
    caixaDiagnostico.hidden = !diagnosticoTexto;
    document.getElementById('formDiagnosticoTexto').textContent = diagnosticoTexto.split('\n').slice(1).join('\n');
    const faixa = document.getElementById('faturamento');
    if (faixa && faturamentoDoQuiz && !faixa.value) faixa.value = faturamentoDoQuiz;
}

function abrirDiagnostico() {
    if (!janela) return;
    fecharMenu();
    prepararFormulario();
    janela.classList.remove('fechando');
    const jaAberta = janela.open;
    if (typeof janela.showModal === 'function') {
        if (!janela.open) janela.showModal();
    } else {
        janela.setAttribute('open', '');
    }
    if (!jaAberta) registrarEvento('formulario_aberto');
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
            limparErros();
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

document.querySelectorAll('[data-abrir-diagnostico]').forEach((b) => b.addEventListener('click', () => abrirDiagnostico()));
// Link de outra página que já abre o formulário (../#conversar), desde 27/10/2026. Antes caía em #contato e faltava um clique.
if (location.hash === '#conversar') abrirDiagnostico();
document.querySelectorAll('[data-fechar-diagnostico]').forEach((b) => b.addEventListener('click', fecharDiagnostico));
document.getElementById('fecharDiagnostico')?.addEventListener('click', fecharDiagnostico);

document.getElementById('formDiagnosticoTirar')?.addEventListener('click', () => {
    diagnosticoTexto = '';
    caixaDiagnostico.hidden = true;
    document.getElementById('nome')?.focus();
});

/* ------------------------------------------------------------ formulário */

/*
 * Obrigatório só o essencial: nome, empresa, WhatsApp ou e-mail (um dos dois) e a autorização
 * da LGPD, que é a base legal escrita na página de privacidade. Faixa de faturamento e tarefa
 * são opcionais. Cada campo é conferido ao sair dele, e de novo enquanto a pessoa corrige.
 */

const CAMPOS = ['nome', 'empresa', 'whatsapp', 'email', 'faturamento', 'gargalo', 'consent'];
const EMAIL_VALIDO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const digitos = (v) => String(v || '').replace(/\D/g, '');

function lerFormulario() {
    return {
        nome: document.getElementById('nome').value.trim(),
        empresa: document.getElementById('empresa').value.trim(),
        whatsapp: document.getElementById('whatsapp').value.trim(),
        email: document.getElementById('email').value.trim(),
        faturamento: document.getElementById('faturamento').value,
        gargalo: document.getElementById('gargalo').value.trim(),
        consent: document.getElementById('consent').checked,
    };
}

// Cada regra devolve a mensagem de erro, ou vazio quando o campo está certo.
const REGRAS = {
    nome: (d) => (d.nome.length >= 2 ? '' : 'Escreva seu nome. Pode ser só o primeiro.'),
    empresa: (d) => (d.empresa.length >= 2 ? '' : 'Escreva o nome da empresa. Se ainda não tiver, vale o ramo, como "distribuidora de bebidas".'),
    whatsapp: (d) => {
        const n = digitos(d.whatsapp);
        if (!n && !d.email) return 'Deixe um WhatsApp ou um e-mail para a gente conseguir responder.';
        if (n && (n.length < 10 || n.length > 11)) return 'Falta número. Coloque o DDD e o número, como (11) 98765-4321.';
        return '';
    },
    email: (d) => (d.email && !EMAIL_VALIDO.test(d.email) ? 'Esse e-mail parece incompleto. Confira o @ e o final, como voce@empresa.com.br.' : ''),
    consent: (d) => (d.consent ? '' : 'Marque a caixa acima para autorizar o contato. Sem ela a gente não pode responder.'),
};

function mostrarErro(id, mensagem) {
    const campo = document.getElementById(id);
    const erro = document.getElementById(`${id}Error`);
    campo?.classList.toggle('field-invalid', !!mensagem);
    if (mensagem) campo?.setAttribute('aria-invalid', 'true');
    else campo?.removeAttribute('aria-invalid');
    if (erro) erro.textContent = mensagem;
}

function conferirCampo(id) {
    const regra = REGRAS[id];
    if (!regra) return true;
    const mensagem = regra(lerFormulario());
    mostrarErro(id, mensagem);
    return !mensagem;
}

function limparErros() {
    CAMPOS.forEach((id) => mostrarErro(id, ''));
}

function validar() {
    const invalidos = Object.keys(REGRAS).filter((id) => !conferirCampo(id));
    if (invalidos.length) document.getElementById(invalidos[0])?.focus();
    return invalidos.length === 0;
}

// Aceita colar com +55 na frente: o país sai, fica DDD e número.
function mascaraTelefone(bruto) {
    let d = digitos(bruto);
    if (d.length > 11 && d.startsWith('55')) d = d.slice(2);
    d = d.slice(0, 11);
    if (d.length <= 2) return d;
    if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
    if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
    return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}

document.getElementById('whatsapp')?.addEventListener('input', (e) => {
    e.target.value = mascaraTelefone(e.target.value);
});

Object.keys(REGRAS).forEach((id) => {
    const campo = document.getElementById(id);
    if (!campo) return;
    // Ao sair do campo, confere, mas só se a pessoa escreveu algo (não acusa erro em campo que ela nem tocou).
    campo.addEventListener('blur', () => {
        if (id !== 'consent' && campo.value.trim()) conferirCampo(id);
    });
    // Enquanto corrige, o erro some assim que o campo fica certo.
    campo.addEventListener(id === 'consent' ? 'change' : 'input', () => {
        if (campo.classList.contains('field-invalid')) conferirCampo(id);
        // WhatsApp e e-mail andam juntos: escrever num resolve o "falta um dos dois" do outro.
        if (id === 'email' && document.getElementById('whatsapp').classList.contains('field-invalid')) conferirCampo('whatsapp');
    });
});

// O texto que segue no campo `gargalo`: o que a pessoa escreveu e, embaixo, o diagnóstico rápido.
function gargaloComDiagnostico(gargalo) {
    return [gargalo, diagnosticoTexto].filter(Boolean).join('\n\n');
}

// Se o envio falhar, o botão de e-mail leva tudo pronto, para nada se perder.
function montarEmailReserva(d) {
    const linhas = [
        `Nome: ${d.nome}`,
        `Empresa: ${d.empresa}`,
        d.whatsapp && `WhatsApp: ${d.whatsapp}`,
        d.email && `E-mail: ${d.email}`,
        d.faturamento && `Faturamento: ${document.getElementById('faturamento').selectedOptions[0]?.textContent || d.faturamento}`,
        d.gargalo && `\n${d.gargalo}`,
    ].filter(Boolean);
    const assunto = `Conversa de diagnóstico: ${d.empresa}`;
    document.getElementById('formErroEmail').href = `mailto:contato@genesiskore.com?subject=${encodeURIComponent(assunto)}&body=${encodeURIComponent(linhas.join('\n'))}`;
}

function mostrarSucesso(d) {
    const primeiroNome = d.nome.split(/\s+/)[0];
    document.getElementById('formSucessoTitulo').textContent = `Recebido, ${primeiroNome}.`;
    let texto = d.whatsapp
        ? 'Uma pessoa da nossa equipe lê o que você mandou e chama você no WhatsApp para marcar a conversa de diagnóstico.'
        : 'Uma pessoa da nossa equipe lê o que você mandou e responde por e-mail para marcar a conversa de diagnóstico.';
    if (d.email) texto += ' Você também recebe um e-mail confirmando que o pedido chegou.';
    document.getElementById('formSucessoTexto').textContent = texto;
    form.hidden = true;
    sucesso.hidden = false;
    sucesso.focus();
}

form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (botaoEnviar.disabled) return;
    erroGeral.hidden = true;

    if (!validar()) return;
    const lido = lerFormulario();
    const dados = {
        ...lido,
        gargalo: gargaloComDiagnostico(lido.gargalo),
        website: document.getElementById('website')?.value || '',
        origem: origemDoLead,
    };

    // Campo escondido preenchido é robô: finge que enviou e não dispara o workflow, que
    // chamaria a IA e mandaria e-mail para um endereço inventado.
    if (dados.website) {
        mostrarSucesso(dados);
        return;
    }

    botaoEnviar.disabled = true;
    botaoEnviar.setAttribute('aria-busy', 'true');
    botaoEnviar.textContent = 'Enviando…';
    // Internet ruim no navegador do Instagram não pode deixar o botão girando para sempre.
    const controle = new AbortController();
    const prazo = setTimeout(() => controle.abort(), 20000);
    try {
        const resposta = await fetch(WEBHOOK_DIAGNOSTICO, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados),
            signal: controle.signal,
        });
        if (!resposta.ok) throw new Error(`Falha ao enviar (${resposta.status})`);
        registrarEvento('formulario_enviado');
        // Já foi junto: a próxima abertura não repete o diagnóstico.
        diagnosticoTexto = '';
        mostrarSucesso(dados);
    } catch (erro) {
        console.error('Erro ao enviar o pedido de diagnóstico:', erro);
        montarEmailReserva(dados);
        erroGeral.hidden = false;
        erroGeral.scrollIntoView({ behavior: rolagem, block: 'nearest' });
    } finally {
        clearTimeout(prazo);
        botaoEnviar.disabled = false;
        botaoEnviar.removeAttribute('aria-busy');
        botaoEnviar.textContent = 'Enviar';
    }
});
