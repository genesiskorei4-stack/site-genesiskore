/*
 * Contagem de visitas do site, criada em 21/10/2026.
 *
 * Sem cookie e sem guardar IP: manda uma batida por página aberta para a plataforma
 * (app.genesiskore.com/api/visita), com o caminho, o domínio de onde a pessoa veio, as
 * etiquetas utm, um id de sessão que some quando a aba fecha e se é celular ou computador.
 * Nada disso identifica a pessoa.
 *
 * Também é aqui que mora a etiqueta de origem do lead (`gkOrigem`), porque a contagem precisa
 * dela em toda página e o formulário da página inicial também. O script.js lê daqui.
 *
 * Regra de ouro: a contagem nunca pode quebrar o site. Tudo fica dentro de try/catch, e quem
 * chama `gkContar` de fora também se protege.
 */
(() => {
    const ENDERECO = 'https://app.genesiskore.com/api/visita';
    const curto = (v, n = 100) => String(v || '').slice(0, n);

    /*
     * De onde o lead veio. O link da bio do Instagram é `genesiskore.com/?origem=instagram`, e a
     * etiqueta segue no formulário até o CRM. Sem etiqueta, o navegador interno do Instagram
     * costuma deixar `instagram.com` como página anterior, e o LinkedIn deixa `linkedin.com` ou
     * `lnkd.in`, que é como o post da empresa leva ao site sem `?origem` no texto. Guardada na
     * sessão porque a pessoa pode navegar pela página antes de preencher, e o endereço perde o `?`
     * quando ela clica num link de seção.
     */
    let origem = 'direto';
    try {
        const limpar = (v) => String(v || '').toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 40);
        const params = new URLSearchParams(location.search);
        let achada = limpar(params.get('origem') || params.get('utm_source'));
        if (!achada && /instagram\./i.test(document.referrer)) achada = 'instagram';
        if (!achada && /(linkedin\.|lnkd\.in)/i.test(document.referrer)) achada = 'linkedin';
        // Quem chega recomendado por um assistente de IA (ChatGPT, Perplexity, Claude, Gemini, Copilot) vira 'ia'.
        if (!achada && /(chatgpt\.com|openai\.com|perplexity\.ai|claude\.ai|gemini\.google|copilot\.microsoft)/i.test(document.referrer)) achada = 'ia';
        if (/^(chatgptcom|perplexity|claudeai|gemini|copilot)/.test(achada)) achada = 'ia';
        try {
            if (achada) sessionStorage.setItem('origem', achada);
            else achada = sessionStorage.getItem('origem') || '';
        } catch { /* navegação privada sem armazenamento: vale só o que veio no endereço */ }
        origem = achada || 'direto';
    } catch { /* fica 'direto' */ }
    window.gkOrigem = origem;

    // Id da aba. Vive no sessionStorage, então some quando a aba fecha e não segue a pessoa.
    function idDaSessao() {
        const novo = () => (window.crypto?.randomUUID?.() || `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`);
        try {
            let id = sessionStorage.getItem('gk_sessao');
            if (!id) {
                id = novo();
                sessionStorage.setItem('gk_sessao', id);
            }
            return id;
        } catch {
            return novo();
        }
    }

    // Só o domínio da página anterior: caminho e parâmetros podem carregar dado de alguém.
    function dominioAnterior() {
        try {
            return document.referrer ? new URL(document.referrer).hostname : '';
        } catch {
            return '';
        }
    }

    // Em teste local ou em navegador robotizado, nada sai.
    const desligada = (() => {
        try {
            const h = location.hostname;
            return location.protocol === 'file:' || !h || h === 'localhost' || h === '127.0.0.1' || h === '::1'
                || h.endsWith('.localhost') || navigator.webdriver === true;
        } catch {
            return true;
        }
    })();

    let base = null;
    function montarBase() {
        const params = new URLSearchParams(location.search);
        return {
            caminho: curto(location.pathname, 300),
            referencia: curto(dominioAnterior()),
            utm_source: curto(params.get('utm_source')),
            utm_medium: curto(params.get('utm_medium')),
            utm_campaign: curto(params.get('utm_campaign')),
            origem,
            sessao: idDaSessao(),
            dispositivo: window.innerWidth < 768 ? 'celular' : 'computador',
        };
    }

    function gkContar(evento) {
        try {
            if (desligada) return;
            if (!base) base = montarBase();
            const corpo = JSON.stringify({ ...base, evento: curto(evento, 40) });
            // text/plain não dispara a pergunta prévia de CORS; a plataforma lê o JSON do corpo.
            if (navigator.sendBeacon && navigator.sendBeacon(ENDERECO, new Blob([corpo], { type: 'text/plain' }))) return;
            if (window.fetch) {
                fetch(ENDERECO, {
                    method: 'POST',
                    body: corpo,
                    keepalive: true,
                    mode: 'no-cors',
                    headers: { 'Content-Type': 'text/plain' },
                }).catch(() => {});
            }
        } catch { /* a contagem nunca derruba o site */ }
    }

    window.gkContar = gkContar;
    gkContar('visita');
})();
