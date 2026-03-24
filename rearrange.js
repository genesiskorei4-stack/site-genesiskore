const fs = require('fs');

const file = 'c:\\Users\\lipec\\Desktop\\GenesisKore Clinicas\\index.html';
const content = fs.readFileSync(file, 'utf8');

// The marker strings that start each section (HTML comments are reliable here)
const markers = {
    roi: '    <!-- ROI Calculator -->',
    solucoes: '    <!-- Soluções -->',
    cases: '    <!-- Cases de Sucesso -->',
    sobre: '    <!-- Quem Somos -->',
    ecossistema: '    <!-- Ecossistema Tecnológico -->',
    processo: '    <!-- Timeline do Processo de Engenharia -->',
    comercial: '    <!-- Modelo Comercial & Segurança -->',
    footer: '    <!-- Footer -->'
};

const lines = content.split('\n');

function findLine(marker) {
    return lines.findIndex(l => l.startsWith(marker));
}

const bounds = {
    roi: [findLine(markers.roi), findLine(markers.solucoes)],
    solucoes: [findLine(markers.solucoes), findLine(markers.cases)],
    cases: [findLine(markers.cases), findLine(markers.sobre)],
    sobre: [findLine(markers.sobre), findLine(markers.ecossistema)],
    ecossistema: [findLine(markers.ecossistema), findLine(markers.processo)],
    processo: [findLine(markers.processo), findLine(markers.comercial)],
    comercial: [findLine(markers.comercial), findLine(markers.footer)],
    footer: [findLine(markers.footer), lines.length]
};

// Check if any didn't map correctly
let valid = true;
Object.entries(bounds).forEach(([key, [start, end]]) => {
    if (start === -1 || end === -1) {
        console.error(`Missing bound for ${key}: start=${start}, end=${end}`);
        valid = false;
    }
});

if (!valid) process.exit(1);

const blocks = {};
for (const [key, [start, end]] of Object.entries(bounds)) {
    blocks[key] = lines.slice(start, end).join('\n');
}

// Prefix lines before the first section
const prefix = lines.slice(0, bounds.roi[0]).join('\n');
// Suffix lines from footer onwards
const suffix = lines.slice(bounds.footer[0]).join('\n');

// Desired order:
// ROI, Quem Somos (sobre), Soluções, Cases, Processos, Stack (ecossistema), Modelo (comercial)
const newContent = [
    prefix,
    blocks.roi,
    blocks.sobre,
    blocks.solucoes,
    blocks.cases,
    blocks.processo,
    blocks.ecossistema,
    blocks.comercial,
    suffix
].join('\n');

fs.writeFileSync(file, newContent);
console.log('Successfully reordered sections!');
