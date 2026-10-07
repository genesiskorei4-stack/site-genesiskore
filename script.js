/*
 * GenesisKore, site institucional. Reescrito em 07/10/2026 junto com o HTML.
 * Sem biblioteca nenhuma: menu do celular, entrada suave das seções, botão fixo,
 * calculadora e o formulário de diagnóstico, que manda para o webhook do n8n.
 */

const WEBHOOK_DIAGNOSTICO = 'https://n8n.srv1249694.hstgr.cloud/webhook/401bcc95-ad5d-4576-89f9-1ecb550fa667';

/* ------------------------------------------------------------ menu do celular */

const botaoMenu = document.getElementById('botaoMenu');
const menuCelular = document.getElementById('menuCelular');

function fecharMenu() {
    if (!menuCelular || menuCelular.hidden) return;
    menuCelular.hidden = true;
    botaoMenu.setAttribute('aria-expanded', 'false');
    botaoMenu.setAttribute('aria-label', 'Abrir menu');
}

if (botaoMenu && menuCelular) {
    botaoMenu.addEventListener('click', () => {
        const abrir = menuCelular.hidden;
        menuCelular.hidden = !abrir;
        botaoMenu.setAttribute('aria-expanded', String(abrir));
        botaoMenu.setAttribute('aria-label', abrir ? 'Fechar menu' : 'Abrir menu');
    });
    menuCelular.querySelectorAll('a').forEach((link) => link.addEventListener('click', fecharMenu));
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') fecharMenu();
    });
}

/* ------------------------------------------------------------ entrada suave e botão fixo */

if ('IntersectionObserver' in window) {
    const revelar = new IntersectionObserver((entradas) => {
        entradas.forEach((entrada) => {
            if (entrada.isIntersecting) {
                entrada.target.classList.add('visivel');
                revelar.unobserve(entrada.target);
            }
        });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    document.querySelectorAll('.revelar').forEach((el) => revelar.observe(el));

    // O botão fixo do celular só aparece depois da primeira tela e some no fechamento,
    // onde já existe o botão grande.
    const ctaFixo = document.getElementById('ctaFixo');
    const abertura = document.getElementById('inicio');
    const fechamento = document.getElementById('contato');
    if (ctaFixo && abertura) {
        let passouAbertura = false;
        let noFechamento = false;
        const atualizar = () => ctaFixo.classList.toggle('visivel', passouAbertura && !noFechamento);
        new IntersectionObserver(([e]) => {
            passouAbertura = !e.isIntersecting;
            atualizar();
        }).observe(abertura);
        if (fechamento) {
            new IntersectionObserver(([e]) => {
                noFechamento = e.isIntersecting;
                atualizar();
            }).observe(fechamento);
        }
    }
} else {
    document.querySelectorAll('.revelar').forEach((el) => el.classList.add('visivel'));
}

/* ------------------------------------------------------------ calculadora */

const horas = document.getElementById('hoursSlider');
const salario = document.getElementById('salarySlider');
const horasRotulo = document.getElementById('hoursVal');
const salarioRotulo = document.getElementById('salaryVal');
const custoAno = document.getElementById('costResult');
const horasAno = document.getElementById('timeResult');

const reais = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(v);
const numero = (v) => new Intl.NumberFormat('pt-BR').format(v);

// A conta que a página explica embaixo do resultado: horas por dia × 22 dias × 12 meses,
// custo CLT de 1,85 vez o salário, jornada de 160 horas por mês.
function calcular() {
    const h = Number(horas.value);
    const s = Number(salario.value);
    const horasPorAno = h * 22 * 12;
    const custoPorHora = (s * 1.85) / 160;
    horasRotulo.textContent = `${h}h`;
    salarioRotulo.textContent = reais(s);
    custoAno.textContent = reais(Math.round(custoPorHora * horasPorAno));
    horasAno.textContent = `${numero(horasPorAno)}h`;
}

if (horas && salario) {
    horas.addEventListener('input', calcular);
    salario.addEventListener('input', calcular);
    calcular();
}

/* ------------------------------------------------------------ janela do diagnóstico */

const janela = document.getElementById('leadModal');
const form = document.getElementById('leadForm');
const sucesso = document.getElementById('formSuccessMessage');
const erroGeral = document.getElementById('formErrorMessage');
const botaoEnviar = document.getElementById('submitBtn');

function abrirDiagnostico() {
    if (!janela) return;
    fecharMenu();
    if (typeof janela.showModal === 'function') {
        janela.showModal();
    } else {
        janela.setAttribute('open', '');
    }
    document.body.style.overflow = 'hidden';
    const primeiro = document.getElementById('nome');
    // No celular o teclado abrindo sozinho cobre metade da janela; só foca no computador.
    if (primeiro && window.matchMedia('(min-width: 720px)').matches) primeiro.focus();
}

function fecharDiagnostico() {
    if (!janela) return;
    if (typeof janela.close === 'function') {
        janela.close();
    } else {
        janela.removeAttribute('open');
    }
}

if (janela) {
    janela.addEventListener('close', () => {
        document.body.style.overflow = '';
        // Depois de um envio, a próxima abertura começa do formulário limpo.
        if (!sucesso.hidden) {
            sucesso.hidden = true;
            form.hidden = false;
            form.reset();
        }
    });
    // Clique fora da caixa (no fundo escurecido) fecha.
    janela.addEventListener('click', (e) => {
        if (e.target === janela) fecharDiagnostico();
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
