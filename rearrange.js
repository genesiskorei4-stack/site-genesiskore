const fs = require('fs');

const extractBlock = (html, startMarker, endMarker) => {
    const start = html.indexOf(startMarker);
    const end = endMarker ? html.indexOf(endMarker, start) : html.length;
    if (start === -1 || (endMarker && end === -1)) {
        throw new Error(`Failed to extract block: ${startMarker}`);
    }
    return html.substring(start, end);
};

try {
    const html = fs.readFileSync('index.html', 'utf8');

    // Extract blocks
    const preHero = html.substring(0, html.indexOf('    <!-- Hero Section -->'));
    const hero = extractBlock(html, '    <!-- Hero Section -->', '    <!-- Quem Somos -->');
    const quemSomos = extractBlock(html, '    <!-- Quem Somos -->', '    <!-- Soluções -->');
    const solucoes = extractBlock(html, '    <!-- Soluções -->', '    <!-- Cases de Sucesso -->');
    const cases = extractBlock(html, '    <!-- Cases de Sucesso -->', '    <!-- Ecossistema Tecnológico -->');
    const ecossistema = extractBlock(html, '    <!-- Ecossistema Tecnológico -->', '    <!-- Timeline do Processo de Engenharia -->');
    const timeline = extractBlock(html, '    <!-- Timeline do Processo de Engenharia -->', '    <!-- Modelo Comercial & Segurança -->');
    const comercial = extractBlock(html, '    <!-- Modelo Comercial & Segurança -->', '    <!-- ROI Calculator -->');
    const roi = extractBlock(html, '    <!-- ROI Calculator -->', '    <!-- Footer -->');

    // There are some blank lines between ROI Calculator and Footer.
    // The previous comment for Footer is '    <!-- Footer -->'.
    // roi block captures up to Footer.

    const footer = html.substring(html.indexOf('    <!-- Footer -->'));

    // Reconstruct pre-hero to update navbar links
    let newPreHero = preHero.replace(
        /<div class="nav-links">[\s\S]*?<\/div>/,
        `<div class="nav-links">
                <a href="#roi-calculator">ROI</a>
                <a href="#solucoes">Soluções</a>
                <a href="#cases">Cases</a>
                <a href="#sobre">Quem Somos</a>
                <a href="#ecossistema">Stack</a>
                <a href="#processo">Processo</a>
                <a href="#comercial">Modelo</a>
            </div>`
    );

    // New order: Hero -> ROI -> Soluções -> Cases -> Quem Somos -> Ecossistema -> Timeline -> Comercial -> Footer
    const newHtml = newPreHero +
        hero +
        roi +
        solucoes +
        cases +
        quemSomos +
        ecossistema +
        timeline +
        comercial +
        footer;

    fs.writeFileSync('index.html', newHtml, 'utf8');
    console.log("SUCCESS");
} catch (e) {
    console.error(e.message);
    process.exit(1);
}
