import sys

file_path = r'c:\Users\lipec\Desktop\GenesisKore Clinicas\index.html'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

def extract_block(start_marker, end_marker):
    start = html.find(start_marker)
    if start == -1:
        print(f"Could not find start marker: {start_marker}")
        return ""
    if end_marker:
        end = html.find(end_marker, start)
        if end == -1:
            print(f"Could not find end marker: {end_marker}")
            return ""
    else:
        end = len(html)
    return html[start:end]

hero_block = extract_block('    <!-- Hero Section -->', '    <!-- Quem Somos -->')
quem_somos_block = extract_block('    <!-- Quem Somos -->', '    <!-- Soluções -->')
solucoes_block = extract_block('    <!-- Soluções -->', '    <!-- Cases de Sucesso -->')
cases_block = extract_block('    <!-- Cases de Sucesso -->', '    <!-- Ecossistema Tecnológico -->')
ecossistema_block = extract_block('    <!-- Ecossistema Tecnológico -->', '    <!-- Timeline do Processo de Engenharia -->')
timeline_block = extract_block('    <!-- Timeline do Processo de Engenharia -->', '    <!-- Modelo Comercial & Segurança -->')
comercial_block = extract_block('    <!-- Modelo Comercial & Segurança -->', '    <!-- ROI Calculator -->')
roi_block = extract_block('    <!-- ROI Calculator -->', '    <!-- Footer -->')

if not all([hero_block, quem_somos_block, solucoes_block, cases_block, ecossistema_block, timeline_block, comercial_block, roi_block]):
    print("Failed to extract all blocks. Check markers.")
    sys.exit(1)

pre_hero = html[:html.find('    <!-- Hero Section -->')]
footer_and_rest = html[html.find('    <!-- Footer -->'):]

new_order = [
    hero_block,
    roi_block,
    solucoes_block,
    cases_block,
    quem_somos_block,
    ecossistema_block,
    timeline_block,
    comercial_block
]

new_html = pre_hero + "".join(new_order) + footer_and_rest

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_html)
print("SUCCESS")
