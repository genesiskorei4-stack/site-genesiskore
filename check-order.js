const fs = require('fs');

const content = fs.readFileSync('index.html', 'utf8');
const regex = /<!-- (.*?) -->/g;

let match;
const order = [];
while ((match = regex.exec(content)) !== null) {
  const name = match[1].trim();
  // Filter out any minor comments
  if (['ROI Calculator', 'Soluções', 'Cases de Sucesso', 'Quem Somos', 'Ecossistema Tecnológico', 'Timeline do Processo de Engenharia', 'Modelo Comercial & Segurança'].includes(name)) {
      order.push(name);
  }
}

console.log("Found Section Order:");
order.forEach((name, i) => console.log(`${i + 1}. ${name}`));

const expected = [
    'ROI Calculator',
    'Quem Somos',
    'Soluções',
    'Cases de Sucesso',
    'Timeline do Processo de Engenharia',
    'Ecossistema Tecnológico',
    'Modelo Comercial & Segurança'
];

let ok = true;
for (let i = 0; i < expected.length; i++) {
    if (order[i] !== expected[i]) {
        console.log(`\nMISMATCH at position ${i+1}: expected '${expected[i]}', found '${order[i]}'`);
        ok = false;
        break;
    }
}

if(ok) {
    console.log("\n✅ Order is exactly as requested.");
}
