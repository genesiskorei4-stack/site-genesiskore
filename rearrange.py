import re

def process_html():
    with open('c:\\Users\\lipec\\Desktop\\GenesisKore Clinicas\\index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Define regexes to extract each block (everything between its marker and the next section's marker)
    # Using specific markers found in the HTML
    
    markers = {
        'roi': r'(<!-- ROI Calculator -->.*?)(?=<!-- Soluções -->)',
        'solucoes': r'(<!-- Soluções -->.*?)(?=<!-- Cases de Sucesso -->)',
        'cases': r'(<!-- Cases de Sucesso -->.*?)(?=<!-- Quem Somos -->)',
        'sobre': r'(<!-- Quem Somos -->.*?)(?=<!-- Ecossistema Tecnológico -->)',
        'ecossistema': r'(<!-- Ecossistema Tecnológico -->.*?)(?=<!-- Timeline do Processo de Engenharia -->)',
        'processo': r'(<!-- Timeline do Processo de Engenharia -->.*?)(?=<!-- Modelo Comercial & Segurança -->)',
        'comercial': r'(<!-- Modelo Comercial & Segurança -->.*?)(?=<!-- Footer -->)'
    }

    blocks = {}
    for key, pattern in markers.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            blocks[key] = match.group(1)
            # Remove the captured block from content to isolated prefix/suffix later? 
            # Actually easier to just piece it together.
        else:
            print(f"Error: Could not find block {key}")
            return
            
    # Extract prefix (everything before ROI)
    prefix_match = re.search(r'(.*?)(?=<!-- ROI Calculator -->)', content, re.DOTALL)
    prefix = prefix_match.group(1) if prefix_match else ""
    
    # Extract suffix (everything from footer onwards)
    suffix_match = re.search(r'(<!-- Footer -->.*)', content, re.DOTALL)
    suffix = suffix_match.group(1) if suffix_match else ""

    # Reorder desired: ROI -> Quem Somos(sobre) -> Solucoes -> Cases -> Processo -> Stack(ecossistema) -> Modelo(comercial)
    new_content = (
        prefix +
        blocks['roi'] +
        blocks['sobre'] +
        blocks['solucoes'] +
        blocks['cases'] +
        blocks['processo'] +
        blocks['ecossistema'] +
        blocks['comercial'] +
        suffix
    )

    with open('c:\\Users\\lipec\\Desktop\\GenesisKore Clinicas\\index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Success")

if __name__ == '__main__':
    process_html()
