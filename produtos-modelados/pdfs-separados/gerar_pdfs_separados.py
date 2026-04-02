"""
Gerador de PDFs estilizados para os 3 produtos separados.
Gera HTMLs estilizados + PDFs via fpdf2.

Uso: python gerar_pdfs_separados.py
Saida: produtos-modelados/pdfs-separados/
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# CSS PROFISSIONAL - Dark Blue Theme
# ============================================================

CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');

:root {
    --primary: #1a1a2e;
    --accent: #e94560;
    --accent-light: #ff6b6b;
    --bg: #ffffff;
    --bg-alt: #f8f9fa;
    --text: #2d3436;
    --text-light: #636e72;
    --border: #e9ecef;
    --gold: #f39c12;
    --success: #00b894;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: var(--text);
    background: var(--bg);
    -webkit-font-smoothing: antialiased;
}

.container {
    max-width: 750px;
    margin: 0 auto;
    padding: 40px 50px;
}

/* CAPA */
.cover {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 60px 40px;
    page-break-after: always;
}

.cover h1 {
    font-family: 'Playfair Display', serif;
    font-size: 3em;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #fff 0%, #e2e2e2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.cover .subtitle {
    font-size: 1.3em;
    font-weight: 300;
    color: #b2bec3;
    margin-bottom: 40px;
    max-width: 500px;
}

.cover .badge {
    display: inline-block;
    background: var(--accent);
    color: white;
    padding: 10px 30px;
    border-radius: 50px;
    font-weight: 600;
    font-size: 1.1em;
    letter-spacing: 1px;
}

.cover .price {
    margin-top: 30px;
    font-size: 1.5em;
    font-weight: 700;
    color: var(--gold);
}

.cover .author {
    margin-top: 60px;
    font-size: 0.9em;
    color: #636e72;
}

/* HEADINGS */
h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2em;
    font-weight: 700;
    color: var(--primary);
    margin: 50px 0 20px 0;
    line-height: 1.3;
}

h2 {
    font-size: 1.6em;
    font-weight: 700;
    color: var(--primary);
    margin: 40px 0 15px 0;
    padding-bottom: 10px;
    border-bottom: 3px solid var(--accent);
    display: inline-block;
}

h3 {
    font-size: 1.25em;
    font-weight: 600;
    color: var(--primary);
    margin: 30px 0 12px 0;
}

h4 {
    font-size: 1.1em;
    font-weight: 600;
    color: var(--text-light);
    margin: 20px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* PARAGRAPHS */
p {
    margin-bottom: 16px;
    text-align: justify;
    hyphens: auto;
}

/* LISTS */
ul, ol {
    margin: 15px 0 15px 25px;
}

li {
    margin-bottom: 8px;
    padding-left: 5px;
}

li::marker {
    color: var(--accent);
    font-weight: 700;
}

strong {
    font-weight: 700;
    color: var(--primary);
}

em {
    font-style: italic;
    color: var(--text-light);
}

blockquote {
    border-left: 4px solid var(--accent);
    background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
    padding: 20px 25px;
    margin: 25px 0;
    border-radius: 0 12px 12px 0;
    font-style: italic;
}

blockquote p {
    margin-bottom: 0;
    color: var(--primary);
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 0.95em;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

thead {
    background: var(--primary);
    color: white;
}

th {
    padding: 14px 18px;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 12px 18px;
    border-bottom: 1px solid var(--border);
}

tbody tr:nth-child(even) {
    background: var(--bg-alt);
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), var(--accent), var(--border), transparent);
    margin: 40px 0;
}

/* CHECKBOX styling */
.checkbox {
    background: var(--bg-alt);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    padding: 8px 15px;
    margin: 4px 0;
    border-radius: 0 6px 6px 0;
    font-size: 0.95em;
}

/* TEMPLATE BOX */
.template-box {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid var(--border);
    border-left: 5px solid var(--accent);
    padding: 25px;
    border-radius: 0 10px 10px 0;
    margin: 25px 0;
}

/* PRINT STYLES */
@media print {
    body { font-size: 11pt; line-height: 1.6; }
    .container { max-width: 100%; padding: 0; margin: 0; }
    .cover {
        min-height: auto;
        padding: 120px 40px;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    h1 { page-break-after: avoid; }
    h2, h3 { page-break-after: avoid; }
    table, blockquote, pre { page-break-inside: avoid; }
    thead { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    a { color: var(--accent); text-decoration: none; }
    @page { size: A4; margin: 2cm 2.5cm; }
}
"""


def preprocess_md(text):
    """Converte o formato texto puro em markdown valido."""
    lines = text.split('\n')
    result = []

    for line in lines:
        stripped = line.strip()

        # Skip linhas de ====
        if re.match(r'^={5,}$', stripped):
            continue

        # === SEMANA X === -> h2
        m = re.match(r'^=== (.+?) ===$', stripped)
        if m:
            result.append(f'## {m.group(1)}')
            continue

        # --- TEMPLATE ... --- -> h3
        m = re.match(r'^--- (.+?) ---$', stripped)
        if m:
            result.append(f'### {m.group(1)}')
            continue

        # CAPITULO X -> h2
        if re.match(r'^CAPITULO \d+', stripped):
            result.append(f'## {stripped}')
            continue

        # SUMARIO, INTRODUCAO, CONCLUSAO -> h2
        if stripped in ['SUMARIO', 'INTRODUCAO', 'CONCLUSAO + PROXIMOS PASSOS',
                        'CHECKLIST 30 DIAS DO AFILIADO', 'PACK DE TEMPLATES PRONTOS',
                        'COMO USAR ESTE CHECKLIST', 'COMO USAR ESTES TEMPLATES']:
            result.append(f'## {stripped}')
            continue

        # X.Y headers -> h3
        if re.match(r'^\d+\.\d+ [A-Z]', stripped):
            result.append(f'### {stripped}')
            continue

        # DIA X headers -> h3
        if re.match(r'^DIA \d+', stripped):
            result.append(f'### {stripped}')
            continue

        # RESULTADO ESPERADO -> bold
        if stripped.startswith('RESULTADO ESPERADO'):
            result.append(f'**{stripped}**')
            result.append('')
            continue

        # METAS PROGRESSIVAS -> h3
        if stripped == 'METAS PROGRESSIVAS:':
            result.append(f'### {stripped}')
            continue

        # ALL CAPS short lines -> bold
        if (stripped and
            stripped == stripped.upper() and
            len(stripped) > 5 and
            len(stripped) < 80 and
            not stripped.startswith('-') and
            not stripped.startswith('*') and
            not stripped.startswith('[') and
            not re.match(r'^\d', stripped) and
            stripped not in ['---']):
            result.append(f'**{stripped}**')
            result.append('')
            continue

        # --- -> hr
        if stripped == '---':
            result.append('\n---\n')
            continue

        result.append(line)

    return '\n'.join(result)


def md_to_styled_html(md_text, title, subtitle, price=""):
    """Converte markdown em HTML estilizado com capa."""
    import markdown
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
    )

    price_html = f'<p class="price">{price}</p>' if price else ''

    cover_html = f"""
    <div class="cover">
        <div class="badge">METODO RENDA SILENCIOSA</div>
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
        {price_html}
        <p class="author">2026 &mdash; Todos os direitos reservados</p>
    </div>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{CSS_STYLE}</style>
</head>
<body>
    {cover_html}
    <div class="container">
        {html_body}
    </div>
</body>
</html>"""

    return full_html


def generate_pdf_fpdf2(text, output_path, title, subtitle):
    """Gera PDF a partir de texto markdown usando fpdf2."""
    from fpdf import FPDF

    text = re.sub(r'^={5,}$', '', text, flags=re.MULTILINE)

    pdf = FPDF(format='A4')
    pdf.set_auto_page_break(auto=True, margin=25)

    # Fontes
    fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
    pdf.add_font('DejaVu', '', os.path.join(fonts_dir, 'arial.ttf'))
    pdf.add_font('DejaVu', 'B', os.path.join(fonts_dir, 'arialbd.ttf'))
    pdf.add_font('DejaVu', 'I', os.path.join(fonts_dir, 'ariali.ttf'))
    pdf.add_font('DejaVu', 'BI', os.path.join(fonts_dir, 'arialbi.ttf'))

    # CAPA
    pdf.add_page()
    pdf.set_fill_color(26, 26, 46)
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_y(80)
    pdf.set_font('DejaVu', 'B', 10)
    pdf.set_text_color(233, 69, 96)
    pdf.cell(0, 10, 'METODO RENDA SILENCIOSA', align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.set_y(100)
    pdf.set_font('DejaVu', 'B', 26)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(0, 13, title, align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.ln(10)
    pdf.set_font('DejaVu', '', 13)
    pdf.set_text_color(178, 190, 195)
    pdf.multi_cell(0, 8, subtitle, align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.set_y(250)
    pdf.set_font('DejaVu', '', 9)
    pdf.set_text_color(99, 110, 114)
    pdf.cell(0, 6, '2026 - Todos os direitos reservados', align='C', new_x='LMARGIN', new_y='NEXT')

    # CONTEUDO
    pdf.add_page()
    pdf.set_text_color(45, 52, 54)

    lines = text.split('\n')

    for line in lines:
        stripped = line.strip()

        if not stripped:
            pdf.ln(3)
            continue

        if stripped == '---':
            pdf.ln(5)
            pdf.set_draw_color(233, 69, 96)
            pdf.set_line_width(0.3)
            y = pdf.get_y()
            pdf.line(30, y, 180, y)
            pdf.ln(5)
            continue

        # H1
        if stripped.startswith('# '):
            text_content = stripped[2:]
            pdf.ln(10)
            pdf.set_fill_color(26, 26, 46)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('DejaVu', 'B', 20)
            y = pdf.get_y()
            pdf.rect(10, y, 190, 18, 'F')
            pdf.set_xy(15, y + 2)
            pdf.multi_cell(180, 7, text_content, align='L', new_x='LMARGIN', new_y='NEXT')
            pdf.set_text_color(45, 52, 54)
            pdf.ln(8)
            continue

        # H2
        if stripped.startswith('## '):
            text_content = stripped[3:]
            pdf.ln(8)
            pdf.set_font('DejaVu', 'B', 16)
            pdf.set_text_color(26, 26, 46)
            pdf.multi_cell(0, 8, text_content, new_x='LMARGIN', new_y='NEXT')
            y = pdf.get_y()
            pdf.set_draw_color(233, 69, 96)
            pdf.set_line_width(0.8)
            pdf.line(10, y + 1, 80, y + 1)
            pdf.ln(6)
            pdf.set_text_color(45, 52, 54)
            continue

        # H3
        if stripped.startswith('### '):
            text_content = stripped[4:]
            pdf.ln(6)
            pdf.set_font('DejaVu', 'B', 13)
            pdf.set_text_color(26, 26, 46)
            pdf.multi_cell(0, 7, text_content, new_x='LMARGIN', new_y='NEXT')
            pdf.ln(4)
            pdf.set_text_color(45, 52, 54)
            continue

        # Bold line **text**
        if stripped.startswith('**') and stripped.endswith('**'):
            text_content = stripped[2:-2]
            pdf.set_font('DejaVu', 'B', 11)
            pdf.multi_cell(0, 6, text_content, new_x='LMARGIN', new_y='NEXT')
            pdf.ln(2)
            pdf.set_font('DejaVu', '', 11)
            continue

        # Checkbox [ ]
        if stripped.startswith('[ ]'):
            text_content = stripped[3:].strip()
            text_content = re.sub(r'\*\*(.+?)\*\*', r'\1', text_content)
            pdf.set_font('DejaVu', '', 10)
            pdf.set_x(15)
            # Draw checkbox
            y = pdf.get_y()
            pdf.set_draw_color(233, 69, 96)
            pdf.set_line_width(0.4)
            pdf.rect(15, y, 4, 4)
            pdf.set_x(22)
            pdf.set_text_color(45, 52, 54)
            pdf.multi_cell(165, 5, text_content, new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            continue

        # Table
        if '|' in stripped and stripped.startswith('|'):
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if all(re.match(r'^[-:]+$', c) for c in cells):
                continue
            col_width = 170 / max(len(cells), 1)
            pdf.set_font('DejaVu', '', 9)
            for cell in cells:
                pdf.cell(col_width, 7, cell, border=1, align='C')
            pdf.ln()
            continue

        # Bullet points
        if stripped.startswith('- ') or stripped.startswith('* '):
            text_content = stripped[2:]
            text_content = re.sub(r'\*\*(.+?)\*\*', r'\1', text_content)
            text_content = re.sub(r'\*(.+?)\*', r'\1', text_content)
            pdf.set_font('DejaVu', '', 11)
            pdf.set_x(15)
            pdf.set_text_color(233, 69, 96)
            pdf.cell(5, 6, chr(8226), new_x='END')
            pdf.set_text_color(45, 52, 54)
            pdf.multi_cell(165, 6, f' {text_content}', new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            continue

        # Numbered items
        m = re.match(r'^(\d+)\. (.+)', stripped)
        if m:
            num = m.group(1)
            text_content = m.group(2)
            text_content = re.sub(r'\*\*(.+?)\*\*', r'\1', text_content)
            pdf.set_font('DejaVu', 'B', 11)
            pdf.set_x(15)
            pdf.set_text_color(233, 69, 96)
            pdf.cell(8, 6, f'{num}.', new_x='END')
            pdf.set_text_color(45, 52, 54)
            pdf.set_font('DejaVu', '', 11)
            pdf.multi_cell(162, 6, f' {text_content}', new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            continue

        # Regular paragraph
        text_content = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)
        text_content = re.sub(r'\*(.+?)\*', r'\1', text_content)
        pdf.set_font('DejaVu', '', 11)
        pdf.multi_cell(0, 6, text_content, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

    pdf.output(output_path)
    print(f"  PDF gerado: {output_path}")


# ============================================================
# PRODUTOS
# ============================================================

PRODUTOS = [
    {
        "md_file": "ebook-principal.md",
        "html_file": "Ebook-Metodo-Renda-Silenciosa.html",
        "pdf_file": "Ebook-Metodo-Renda-Silenciosa.pdf",
        "title": "Metodo Renda Silenciosa",
        "subtitle": "O Guia Completo para Gerar Renda como Afiliado de Produtos Fisicos sem Aparecer",
        "price": "R$ 37,00",
    },
    {
        "md_file": "checklist-30-dias.md",
        "html_file": "Checklist-30-Dias-do-Afiliado.html",
        "pdf_file": "Checklist-30-Dias-do-Afiliado.pdf",
        "title": "Checklist 30 Dias do Afiliado",
        "subtitle": "Metodo Renda Silenciosa",
        "price": "R$ 9,90",
    },
    {
        "md_file": "pack-templates.md",
        "html_file": "Pack-de-Templates-Prontos.html",
        "pdf_file": "Pack-de-Templates-Prontos.pdf",
        "title": "Pack de Templates Prontos",
        "subtitle": "Metodo Renda Silenciosa",
        "price": "R$ 14,90",
    },
]


def generate_all():
    """Gera todos os HTMLs e PDFs."""

    for produto in PRODUTOS:
        print("=" * 60)
        print(f"Processando: {produto['md_file']}")
        print("=" * 60)

        md_path = os.path.join(BASE_DIR, produto["md_file"])
        with open(md_path, "r", encoding="utf-8") as f:
            raw = f.read()

        # Pre-processar markdown
        md_text = preprocess_md(raw)

        # Gerar HTML
        html = md_to_styled_html(
            md_text,
            title=produto["title"],
            subtitle=produto["subtitle"],
            price=produto["price"]
        )

        html_path = os.path.join(BASE_DIR, produto["html_file"])
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  HTML gerado: {html_path}")

        # Gerar PDF
        try:
            pdf_path = os.path.join(BASE_DIR, produto["pdf_file"])
            generate_pdf_fpdf2(
                md_text,
                pdf_path,
                produto["title"],
                produto["subtitle"]
            )
        except Exception as e:
            print(f"  ERRO no PDF: {e}")

    # INSTRUCOES FINAIS
    print("\n" + "=" * 60)
    print("CONCLUIDO!")
    print("=" * 60)
    print(f"\nArquivos gerados em: {BASE_DIR}")
    print("\nSe os PDFs ficaram sem formatacao ideal, use os HTMLs:")
    print("  1. Abra o arquivo .html no Chrome")
    print("  2. Ctrl+P (Imprimir)")
    print("  3. Destino: 'Salvar como PDF'")
    print("  4. Margens: Padrao")
    print("  5. Marque 'Graficos de fundo' para manter cores")
    print("  6. Clique 'Salvar'")


if __name__ == "__main__":
    generate_all()
