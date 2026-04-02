"""
Gerador de PDFs estilizados a partir dos ebooks Markdown.
Gera HTMLs estilizados com @media print + tenta gerar PDFs via fpdf2.

Uso: python gerar_pdfs.py
Saida: produtos-modelados/pdfs/
"""

import os
import re
import markdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# CSS PROFISSIONAL - Clean White Theme com fontes modernas
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

/* STRONG / EM */
strong {
    font-weight: 700;
    color: var(--primary);
}

em {
    font-style: italic;
    color: var(--text-light);
}

/* BLOCKQUOTES - dicas / destaques */
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

/* TABLES */
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
    letter-spacing: 0.3px;
}

td {
    padding: 12px 18px;
    border-bottom: 1px solid var(--border);
}

tbody tr:nth-child(even) {
    background: var(--bg-alt);
}

tbody tr:hover {
    background: #eef2ff;
}

/* CODE / PRE */
code {
    background: var(--bg-alt);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
    color: var(--accent);
}

pre {
    background: var(--primary);
    color: #dfe6e9;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 20px 0;
    font-size: 0.9em;
    line-height: 1.6;
}

pre code {
    background: none;
    color: inherit;
    padding: 0;
}

/* HR - section breaks */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), var(--accent), var(--border), transparent);
    margin: 40px 0;
}

/* HIGHLIGHT BOXES */
.highlight-box {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid var(--border);
    border-left: 5px solid var(--accent);
    padding: 25px;
    border-radius: 0 10px 10px 0;
    margin: 25px 0;
}

/* SUMARIO styling */
.sumario {
    background: var(--bg-alt);
    padding: 30px 40px;
    border-radius: 12px;
    border: 1px solid var(--border);
    margin: 30px 0;
}

.sumario p {
    font-family: 'Inter', monospace;
    margin-bottom: 8px;
    font-size: 0.95em;
}

/* CHAPTER HEADER */
.chapter-header {
    background: linear-gradient(135deg, var(--primary) 0%, #16213e 100%);
    color: white;
    padding: 40px;
    border-radius: 12px;
    margin: 40px 0 30px 0;
    page-break-before: always;
}

.chapter-header h2 {
    color: white;
    border: none;
    display: block;
    font-family: 'Playfair Display', serif;
    font-size: 1.8em;
}

/* PAGE NUMBERS */
.page-footer {
    text-align: center;
    color: var(--text-light);
    font-size: 0.8em;
    padding: 20px 0;
    border-top: 1px solid var(--border);
    margin-top: 60px;
}

/* PRINT STYLES */
@media print {
    body {
        font-size: 11pt;
        line-height: 1.6;
    }

    .container {
        max-width: 100%;
        padding: 0;
        margin: 0;
    }

    .cover {
        min-height: auto;
        padding: 120px 40px;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    h1 { page-break-after: avoid; }
    h2, h3 { page-break-after: avoid; }

    table, blockquote, pre {
        page-break-inside: avoid;
    }

    .chapter-header {
        page-break-before: always;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    thead {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    tbody tr:nth-child(even) {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    a { color: var(--accent); text-decoration: none; }

    @page {
        size: A4;
        margin: 2cm 2.5cm;
    }
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .container { padding: 20px; }
    .cover h1 { font-size: 2em; }
    h1 { font-size: 1.8em; }
    h2 { font-size: 1.4em; }
}
"""


def preprocess_entregavel(text):
    """Converte o formato texto puro do entregavel em markdown valido."""
    lines = text.split('\n')
    result = []
    i = 0
    in_sumario = False

    while i < len(lines):
        line = lines[i]

        # Skip linhas de ====
        if re.match(r'^={5,}$', line.strip()):
            i += 1
            continue

        # PARTE X -> h1
        if re.match(r'^PARTE \d+', line.strip()):
            result.append(f'# {line.strip()}')
            i += 1
            continue

        # ENTREGAVEL COMPLETO header
        if line.strip().startswith('ENTREGAVEL COMPLETO'):
            result.append(f'# {line.strip()}')
            i += 1
            continue

        # "Produto:" and "Data:" lines as italic
        if re.match(r'^(Produto|Data):', line.strip()):
            result.append(f'*{line.strip()}*')
            result.append('')
            i += 1
            continue

        # CAPITULO X -> h2
        if re.match(r'^CAPITULO \d+', line.strip()):
            result.append(f'## {line.strip()}')
            i += 1
            continue

        # SUMARIO, INTRODUCAO, CONCLUSAO -> h2
        if line.strip() in ['SUMARIO', 'INTRODUCAO', 'CONCLUSAO + PROXIMOS PASSOS']:
            result.append(f'## {line.strip()}')
            in_sumario = line.strip() == 'SUMARIO'
            i += 1
            continue

        # === SEMANA X === -> h3
        m = re.match(r'^=== (.+?) ===$', line.strip())
        if m:
            result.append(f'### {m.group(1)}')
            i += 1
            continue

        # --- TEMPLATE DE ANUNCIO #X --- -> h3
        m = re.match(r'^--- (.+?) ---$', line.strip())
        if m:
            result.append(f'### {m.group(1)}')
            i += 1
            continue

        # X.Y headers (like 1.1, 2.3 etc) - all caps -> h3
        if re.match(r'^\d+\.\d+ [A-Z]', line.strip()):
            result.append(f'### {line.strip()}')
            i += 1
            continue

        # ALL CAPS lines that are short (section headers) -> h3
        if (line.strip() and
            line.strip() == line.strip().upper() and
            len(line.strip()) > 5 and
            len(line.strip()) < 80 and
            not line.strip().startswith('-') and
            not line.strip().startswith('*') and
            not re.match(r'^\d', line.strip()) and
            line.strip() not in ['---']):
            # Likely a subheader
            result.append(f'**{line.strip()}**')
            result.append('')
            i += 1
            continue

        # --- -> hr
        if line.strip() == '---':
            result.append('\n---\n')
            i += 1
            continue

        # Numbered items starting with number. text
        if re.match(r'^\d+\. ', line.strip()):
            result.append(line)
            i += 1
            continue

        # Bullet points
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            result.append(line)
            i += 1
            continue

        result.append(line)
        i += 1

    return '\n'.join(result)


def split_ebooks_completos(text):
    """Separa o arquivo ebooks-completos em 2 ebooks."""
    # Find the second ebook marker
    marker = "# EBOOK 2:"
    idx = text.find(marker)
    if idx == -1:
        return [("Renda Silenciosa PRO", text)]

    # Find start of second book (backtrack to ==== line)
    # Look for the ==== block before EBOOK 2
    search_area = text[:idx]
    last_eq = search_area.rfind('\n====')
    if last_eq == -1:
        last_eq = idx

    ebook1 = text[:last_eq].strip()
    ebook2 = text[last_eq:].strip()

    return [
        ("Renda Silenciosa PRO - Trafego Pago Avancado", ebook1),
        ("Quiz que Vende - Funis Interativos", ebook2),
    ]


def md_to_styled_html(md_text, title, subtitle=""):
    """Converte markdown em HTML estilizado com capa."""
    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
    )

    # Build cover
    cover_html = f"""
    <div class="cover">
        <div class="badge">METODO RENDA SILENCIOSA</div>
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
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


def generate_all():
    """Gera todos os PDFs/HTMLs."""

    # ========================================
    # 1. ENTREGAVEL (ebook principal + checklist + templates)
    # ========================================
    print("=" * 60)
    print("Processando: entregavel-renda-silenciosa.md")
    print("=" * 60)

    with open(os.path.join(BASE_DIR, "entregavel-renda-silenciosa.md"), "r", encoding="utf-8") as f:
        raw = f.read()

    md_text = preprocess_entregavel(raw)
    html = md_to_styled_html(
        md_text,
        title="Metodo Renda Silenciosa",
        subtitle="O Guia Completo para Gerar Renda como Afiliado de Produtos Fisicos sem Aparecer"
    )

    outpath = os.path.join(OUTPUT_DIR, "Metodo-Renda-Silenciosa-Guia-Completo.html")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  HTML gerado: {outpath}")

    # ========================================
    # 2. EBOOKS COMPLETOS (2 ebooks separados)
    # ========================================
    print("\n" + "=" * 60)
    print("Processando: ebooks-completos-renda-silenciosa.md")
    print("=" * 60)

    with open(os.path.join(BASE_DIR, "ebooks-completos-renda-silenciosa.md"), "r", encoding="utf-8") as f:
        raw = f.read()

    ebooks = split_ebooks_completos(raw)

    filenames = [
        "Renda-Silenciosa-PRO-Trafego-Pago.html",
        "Quiz-que-Vende-Funis-Interativos.html",
    ]

    subtitles = [
        "Trafego Pago Avancado para Afiliados de Produtos Fisicos",
        "Como Criar Funis Interativos que Convertem 3x Mais",
    ]

    for idx, (title, content) in enumerate(ebooks):
        # Clean ==== lines from content
        content_clean = re.sub(r'^={5,}$', '', content, flags=re.MULTILINE)

        html = md_to_styled_html(
            content_clean,
            title=title,
            subtitle=subtitles[idx]
        )

        outpath = os.path.join(OUTPUT_DIR, filenames[idx])
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  HTML gerado: {outpath}")

    # ========================================
    # 3. Tentar gerar PDFs via fpdf2
    # ========================================
    print("\n" + "=" * 60)
    print("Tentando gerar PDFs com fpdf2...")
    print("=" * 60)

    try:
        generate_pdf_fpdf2(
            os.path.join(BASE_DIR, "entregavel-renda-silenciosa.md"),
            os.path.join(OUTPUT_DIR, "Metodo-Renda-Silenciosa-Guia-Completo.pdf"),
            "Metodo Renda Silenciosa",
            "O Guia Completo",
            preprocess=True
        )
    except Exception as e:
        print(f"  ERRO no PDF do entregavel: {e}")

    for idx, (title, content) in enumerate(ebooks):
        pdf_name = filenames[idx].replace('.html', '.pdf')
        try:
            generate_pdf_fpdf2_from_text(
                content,
                os.path.join(OUTPUT_DIR, pdf_name),
                title,
                subtitles[idx]
            )
        except Exception as e:
            print(f"  ERRO no PDF {pdf_name}: {e}")

    # ========================================
    # INSTRUCOES FINAIS
    # ========================================
    print("\n" + "=" * 60)
    print("CONCLUIDO!")
    print("=" * 60)
    print(f"\nArquivos gerados em: {OUTPUT_DIR}")
    print("\nSe os PDFs ficaram sem formatacao ideal, use os HTMLs:")
    print("  1. Abra o arquivo .html no Chrome")
    print("  2. Ctrl+P (Imprimir)")
    print("  3. Destino: 'Salvar como PDF'")
    print("  4. Margens: Padrao")
    print("  5. Marque 'Graficos de fundo' para manter cores")
    print("  6. Clique 'Salvar'")
    print("\nOs HTMLs geram PDFs de alta qualidade pelo Chrome.")


def generate_pdf_fpdf2(filepath, output_path, title, subtitle, preprocess=False):
    """Gera PDF estilizado usando fpdf2."""
    from fpdf import FPDF

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    if preprocess:
        raw = preprocess_entregavel(raw)

    generate_pdf_fpdf2_from_text(raw, output_path, title, subtitle)


def generate_pdf_fpdf2_from_text(text, output_path, title, subtitle):
    """Gera PDF a partir de texto markdown usando fpdf2."""
    from fpdf import FPDF

    # Clean ==== lines
    text = re.sub(r'^={5,}$', '', text, flags=re.MULTILINE)

    pdf = FPDF(format='A4')
    pdf.set_auto_page_break(auto=True, margin=25)

    # Fontes
    pdf.add_font('DejaVu', '', os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arial.ttf'))
    pdf.add_font('DejaVu', 'B', os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arialbd.ttf'))
    pdf.add_font('DejaVu', 'I', os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'ariali.ttf'))
    pdf.add_font('DejaVu', 'BI', os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arialbi.ttf'))

    # CAPA
    pdf.add_page()
    pdf.set_fill_color(26, 26, 46)  # dark blue
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_y(80)
    pdf.set_font('DejaVu', 'B', 10)
    pdf.set_text_color(233, 69, 96)  # accent red
    pdf.cell(0, 10, 'METODO RENDA SILENCIOSA', align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.set_y(100)
    pdf.set_font('DejaVu', 'B', 28)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(0, 14, title, align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.ln(10)
    pdf.set_font('DejaVu', '', 14)
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

        # Skip --- lines
        if stripped == '---':
            pdf.ln(5)
            pdf.set_draw_color(233, 69, 96)
            pdf.set_line_width(0.3)
            y = pdf.get_y()
            pdf.line(30, y, 180, y)
            pdf.ln(5)
            continue

        # H1 - # headers
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

        # H2 - ## headers
        if stripped.startswith('## '):
            text_content = stripped[3:]
            pdf.ln(8)
            pdf.set_font('DejaVu', 'B', 16)
            pdf.set_text_color(26, 26, 46)
            pdf.multi_cell(0, 8, text_content, new_x='LMARGIN', new_y='NEXT')
            # Underline accent
            y = pdf.get_y()
            pdf.set_draw_color(233, 69, 96)
            pdf.set_line_width(0.8)
            pdf.line(10, y + 1, 80, y + 1)
            pdf.ln(6)
            pdf.set_text_color(45, 52, 54)
            continue

        # H3 - ### headers
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

        # Table header line
        if '|' in stripped and stripped.startswith('|'):
            # Simple table rendering
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if all(re.match(r'^[-:]+$', c) for c in cells):
                # Separator line, skip
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
            # Clean markdown bold/italic
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
        # Clean markdown formatting
        text_content = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)
        text_content = re.sub(r'\*(.+?)\*', r'\1', text_content)
        pdf.set_font('DejaVu', '', 11)
        pdf.multi_cell(0, 6, text_content, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

    pdf.output(output_path)
    print(f"  PDF gerado: {output_path}")


if __name__ == "__main__":
    generate_all()
