/*
 * Página do formulário, criada em 27/10/2026 (pedido do Felipe): o formulário saiu da janela da
 * página inicial e virou página própria, em cinco etapas, com a linha de progresso no alto.
 * O mais reservado (faturamento) fica por último, e cada etapa diz qual é a próxima.
 *
 * O envio é o mesmo de antes, para o workflow do n8n (Pipeline de Leads), com os mesmos campos:
 * nome, empresa, whatsapp, email, faturamento, gargalo, consent, website e origem. As respostas
 * das etapas 1 e 2 vão como texto dentro do gargalo, que é o campo livre que o workflow já lê.
 *
 * Cada etapa ganha um endereço (#etapa-2), então o botão de voltar do celular volta uma etapa
 * em vez de sair da página.
 */

const WEBHOOK_DIAGNOSTICO = 'https://n8n.srv1249694.hstgr.cloud/webhook/401bcc95-ad5d-4576-89f9-1ecb550fa667';
const TOTAL = 5;
const menosMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// A origem do lead e a contagem moram no contagem.js. Se ele não carregar, a origem vira 'direto'.
const origemDoLead = window.gkOrigem || 'direto';
const registrarEvento = (evento) => {
    try { window.gkContar?.(evento); } catch { /* contagem nunca quebra o site */ }
};

const form = document.getElementById('leadForm');
const etapas = [...document.querySelectorAll('.etapa')];
const sucesso = document.getElementById('formSuccessMessage');
const erroGeral = document.getElementById('formErrorMessage');
const botaoEnviar = document.getElementById('submitBtn');
const progresso = document.getElementById('progresso');

// pergunta -> { valor, rotulo }
const escolhas = {};
let atual = 1;
let liberada = 1;

/* ------------------------------------------------------------ progresso e navegação */

function mostrarProgresso(feitas) {
    [...progresso.children].forEach((traco, i) => traco.classList.toggle('feita', i < feitas));
    const porcento = Math.round((feitas / TOTAL) * 100);
    progresso.setAttribute('aria-valuenow', String(porcento));
    document.getElementById('progressoEtapa').textContent = feitas >= TOTAL ? 'Pronto' : `Etapa ${atual} de ${TOTAL}`;
    document.getElementById('progressoFeito').textContent = `${porcento}% respondido`;
}

function irPara(n, { historico = true } = {}) {
    atual = Math.min(Math.max(1, n), liberada);
    etapas.forEach((etapa) => { etapa.hidden = Number(etapa.dataset.etapa) !== atual; });
    if (atual === 3) montarConta();
    mostrarProgresso(atual - 1);
    if (historico) history.pushState({ etapa: atual }, '', `${location.search}#etapa-${atual}`);
    window.scrollTo({ top: 0, behavior: menosMovimento ? 'auto' : 'smooth' });
    document.getElementById(`t${atual}`)?.focus({ preventScroll: true });
}

function avancar() {
    liberada = Math.max(liberada, atual + 1);
    irPara(atual + 1);
}

window.addEventListener('popstate', (e) => {
    const n = e.state?.etapa || Number((location.hash.match(/etapa-(\d)/) || [])[1]) || 1;
    if (!sucesso.hidden) return;
    irPara(n, { historico: false });
});

document.querySelectorAll('[data-voltar]').forEach((b) => b.addEventListener('click', () => history.back()));

/* ------------------------------------------------------------ escolhas de um toque */

document.querySelectorAll('.opcoes').forEach((grupo) => {
    const pergunta = grupo.dataset.pergunta;
    grupo.addEventListener('click', (e) => {
        const botao = e.target.closest('.opcao');
        if (!botao) return;
        grupo.querySelectorAll('.opcao').forEach((b) => b.setAttribute('aria-pressed', String(b === botao)));
        escolhas[pergunta] = { valor: botao.dataset.valor, rotulo: botao.textContent.trim() };
        const erro = document.getElementById(`${pergunta}Error`);
        if (erro) erro.textContent = '';
        // Nas duas primeiras, o toque já leva para a próxima. No faturamento só marca, porque ainda tem a autorização.
        if (pergunta !== 'faturamento') setTimeout(avancar, menosMovimento ? 0 : 280);
    });
});

/* ------------------------------------------------------------ a conta do ano (etapa 3) */

// Horas por semana: o piso da faixa escolhida, para o número nunca passar do que a pessoa disse.
const PISO_POR_SEMANA = { '5-15': 5, '15-40': 15, 'mais-40': 40 };
const SEMANAS = 52;
const HORAS_POR_MES = 160; // a mesma jornada da calculadora da página inicial
const um = (v) => new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(v);

function mesesDeTrabalho(horas) {
    const meses = horas / HORAS_POR_MES;
    return `${um(meses)} ${meses < 2 ? 'mês' : 'meses'}`;
}

function montarConta() {
    const tempo = escolhas.tempo;
    const caixa = document.getElementById('contaDoAno');
    const forte = document.getElementById('contaHoras');
    const texto = document.getElementById('contaTexto');
    if (!tempo) {
        caixa.hidden = true;
        return;
    }
    caixa.hidden = false;
    if (tempo.valor === 'nao-sei') {
        forte.textContent = 'Ainda sem número';
        texto.textContent = 'Quase ninguém mede. Na conversa a gente mede junto com você, e esse é o primeiro número que vale ter.';
    } else if (tempo.valor === 'ate-5') {
        const horas = 5 * SEMANAS;
        forte.textContent = `Até ${um(horas)} horas`;
        texto.textContent = `Menos de 5 horas por semana, vezes ${SEMANAS} semanas. Pode chegar a ${mesesDeTrabalho(horas)} de uma pessoa trabalhando só nisso, contando ${HORAS_POR_MES} horas por mês.`;
    } else {
        const piso = PISO_POR_SEMANA[tempo.valor];
        const horas = piso * SEMANAS;
        forte.textContent = `Pelo menos ${um(horas)} horas`;
        texto.textContent = `${tempo.rotulo} por semana, vezes ${SEMANAS} semanas, contando pelo menor número da faixa. É o mesmo que ${mesesDeTrabalho(horas)} de uma pessoa trabalhando só nisso, a ${HORAS_POR_MES} horas por mês.`;
    }
}

/* ------------------------------------------------------------ campos e regras */

const EMAIL_VALIDO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const digitos = (v) => String(v || '').replace(/\D/g, '');

function lerFormulario() {
    return {
        nome: document.getElementById('nome').value.trim(),
        empresa: document.getElementById('empresa').value.trim(),
        whatsapp: document.getElementById('whatsapp').value.trim(),
        email: document.getElementById('email').value.trim(),
        faturamento: escolhas.faturamento?.valor || '',
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

const DA_ETAPA = { 4: ['nome', 'empresa', 'whatsapp', 'email'], 5: ['consent'] };

function mostrarErro(id, mensagem) {
    const campo = document.getElementById(id);
    const erro = document.getElementById(`${id}Error`);
    campo?.classList.toggle('field-invalid', !!mensagem);
    if (mensagem) campo?.setAttribute('aria-invalid', 'true');
    else campo?.removeAttribute('aria-invalid');
    if (erro) erro.textContent = mensagem;
}

function conferirCampo(id) {
    const mensagem = REGRAS[id](lerFormulario());
    mostrarErro(id, mensagem);
    return !mensagem;
}

function validarEtapa(n) {
    const invalidos = (DA_ETAPA[n] || []).filter((id) => !conferirCampo(id));
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

document.getElementById('whatsapp').addEventListener('input', (e) => {
    e.target.value = mascaraTelefone(e.target.value);
});

Object.keys(REGRAS).forEach((id) => {
    const campo = document.getElementById(id);
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

/* ------------------------------------------------------------ envio */

// O texto do campo gargalo: o que a pessoa escreveu e, embaixo, as escolhas das etapas 1 e 2.
function gargaloComEscolhas(gargalo) {
    const linhas = [
        escolhas.onde && `Onde mais perde tempo: ${escolhas.onde.rotulo}`,
        escolhas.tempo && `Tempo por semana: ${escolhas.tempo.rotulo}`,
    ].filter(Boolean);
    const bloco = linhas.length ? ['Respostas do formulário do site', ...linhas].join('\n') : '';
    return [gargalo, bloco].filter(Boolean).join('\n\n');
}

// Se o envio falhar, o botão de e-mail leva tudo pronto, para nada se perder.
function montarEmailReserva(d) {
    const linhas = [
        `Nome: ${d.nome}`,
        `Empresa: ${d.empresa}`,
        d.whatsapp && `WhatsApp: ${d.whatsapp}`,
        d.email && `E-mail: ${d.email}`,
        escolhas.faturamento?.valor && `Faturamento: ${escolhas.faturamento.rotulo}`,
        d.gargalo && `\n${d.gargalo}`,
    ].filter(Boolean);
    const assunto = `Conversa de diagnóstico: ${d.empresa}`;
    document.getElementById('formErroEmail').href = `mailto:contato@genesiskore.com?subject=${encodeURIComponent(assunto)}&body=${encodeURIComponent(linhas.join('\n'))}`;
}

// Regra da casa: abaixo de R$ 150 mil por mês, dizer com franqueza o que ele não precisa comprar.
const FRANQUEZA = {
    'ate-50k': 'Uma coisa com franqueza: com faturamento de até R$ 50 mil por mês, um sistema sob medida provavelmente custaria mais do que o problema. Uma ferramenta pronta, como o Bling ou o Omie, resolve pedido, estoque e financeiro por uma mensalidade. Na conversa a gente indica qual serve para o seu caso, sem proposta nenhuma.',
    '50k-150k': 'Uma coisa com franqueza: com faturamento entre R$ 50 mil e R$ 150 mil por mês, talvez ainda não seja hora de sistema sob medida, e uma ferramenta pronta, como o Bling ou o Omie, pode bastar. Se uma tarefa específica come horas da equipe toda semana, a conversa serve para ver se um projeto pequeno se paga. Se não se pagar, a gente diz.',
};

function mostrarSucesso(d) {
    const primeiroNome = d.nome.split(/\s+/)[0];
    document.getElementById('formSucessoTitulo').textContent = `Recebido, ${primeiroNome}.`;
    let texto = d.whatsapp
        ? 'Uma pessoa da nossa equipe lê o que você mandou e chama você no WhatsApp para marcar a conversa de diagnóstico.'
        : 'Uma pessoa da nossa equipe lê o que você mandou e responde por e-mail para marcar a conversa de diagnóstico.';
    if (d.email) texto += ' Você também recebe um e-mail confirmando que o pedido chegou.';
    document.getElementById('formSucessoTexto').textContent = texto;
    const franqueza = document.getElementById('formFranqueza');
    franqueza.textContent = FRANQUEZA[d.faturamento] || '';
    franqueza.hidden = !franqueza.textContent;
    form.hidden = true;
    sucesso.hidden = false;
    mostrarProgresso(TOTAL);
    history.replaceState({ etapa: 'fim' }, '', `${location.search}#recebido`);
    window.scrollTo({ top: 0 });
    document.getElementById('formSucessoTitulo').focus({ preventScroll: true });
}

async function enviar() {
    if (botaoEnviar.disabled) return;
    erroGeral.hidden = true;
    const lido = lerFormulario();
    const dados = {
        ...lido,
        gargalo: gargaloComEscolhas(lido.gargalo),
        website: document.getElementById('website').value || '',
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
        mostrarSucesso(dados);
    } catch (erro) {
        console.error('Erro ao enviar o pedido de diagnóstico:', erro);
        montarEmailReserva(dados);
        erroGeral.hidden = false;
        erroGeral.scrollIntoView({ behavior: menosMovimento ? 'auto' : 'smooth', block: 'nearest' });
    } finally {
        clearTimeout(prazo);
        botaoEnviar.disabled = false;
        botaoEnviar.removeAttribute('aria-busy');
        botaoEnviar.textContent = 'Enviar';
    }
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!validarEtapa(atual)) return;
    if (atual < TOTAL) avancar();
    else enviar();
});

/* ------------------------------------------------------------ começo */

// Quem recarrega no meio, ou chega por um link com #etapa-3, começa da primeira: as respostas
// de antes não ficam guardadas em lugar nenhum.
history.replaceState({ etapa: 1 }, '', `${location.pathname}${location.search}`);
irPara(1, { historico: false });
registrarEvento('formulario_aberto');
