"""
MINERADOR DE OFERTAS BR v3 — @titio.digital
Queries combinadas + organização automática por nicho + upload Drive

SETUP:
  pip install requests google-auth google-api-python-client

  gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/drive.file

  export URLSCAN_API_KEY="sua_chave"
  python minerador_v3.py
"""

import requests, csv, json, os, time, re
from datetime import datetime
from urllib.parse import urlparse
from collections import defaultdict

try:
    from drive_upload import fazer_upload
    DRIVE_OK = True
except ImportError:
    DRIVE_OK = False

# ──────────────────────────────────────────────────────────────
API_KEY = os.environ.get("URLSCAN_API_KEY", "019d384b-2979-7447-86c9-a7af4dadb221")
DIAS_ATRAS    = 7    # busca dos últimos N dias na query urlscan
IDADE_MAX_DIAS = 7   # descarta se scan tiver mais de N dias
MAX_POR_QUERY = 100
DELAY         = 2.5   # segundos entre requests (respeita rate limit grátis: 30/min)
PASTA_SAIDA   = "mineracao_ofertas"

# ──────────────────────────────────────────────────────────────
# QUERIES COMBINADAS — dois sinais = muito menos ruído
# Formato: ("nome_legível", "query_urlscan")
# ──────────────────────────────────────────────────────────────

QUERIES = [
    # ── Trackers BR
    ("tracker_utmify",        "domain:utmify.com.br AND date:>now-{d}d"),
    ("tracker_rdstation",     "domain:rdstation.com.br AND date:>now-{d}d"),
    ("tracker_appmax",        "domain:appmax.com.br AND date:>now-{d}d"),

    # ── Gateways solo
    ("gateway_hotmart",       "domain:hotmart.com AND date:>now-{d}d"),
    ("gateway_kiwify",        "domain:kiwify.com.br AND date:>now-{d}d"),
    ("gateway_kirvano",       "domain:kirvano.com AND date:>now-{d}d"),
    ("gateway_cakto",         "domain:cakto.com.br AND date:>now-{d}d"),
    ("gateway_monetizze",     "domain:monetizze.com.br AND date:>now-{d}d"),
    ("gateway_eduzz",         "domain:eduzz.com AND date:>now-{d}d"),
    ("gateway_pepper",        "domain:pepper.com.br AND date:>now-{d}d"),

    # ── Construtores de página
    ("klickpages",            "domain:klickpages.com.br AND date:>now-{d}d"),
    ("leadlovers",            "domain:leadlovers.com.br AND date:>now-{d}d"),
]

# ──────────────────────────────────────────────────────────────
# CLASSIFICADOR DE NICHO
# Ordem importa: mais específico primeiro
# ──────────────────────────────────────────────────────────────

NICHOS = [
    ("saude_emagrecimento", [
        "emagrec", "emagrecimento", "barriga", "gordura", "dieta", "detox",
        "queima", "metabolismo", "jejum", "caloria", "peso", "obesi",
        "colesterol", "diabetes", "pressão", "tireoide", "hormônio",
    ]),
    ("saude_beleza", [
        "pele", "cabelo", "unha", "sobrancelha", "maquiagem", "skincare",
        "rejuvenesc", "antienvelhecimento", "manchas", "acne", "botox",
        "dermato", "colágeno", "beleza", "estética",
    ]),
    ("saude_bem_estar", [
        "sono", "ansiedade", "estresse", "depressão", "mental", "humor",
        "energia", "disposição", "cansaço", "imunidade", "dor",
        "articulação", "coluna", "postura", "meditação",
    ]),
    ("renda_extra", [
        "renda extra", "ganhar dinheiro", "lucrar", "faturar", "renda passiva",
        "trabalhar de casa", "home office", "liberdade financeira",
        "independência financeira", "dinheiro online", "renda online",
    ]),
    ("financas_investimento", [
        "investimento", "investir", "bolsa", "ações", "cripto", "bitcoin",
        "trader", "trading", "forex", "day trade", "renda fixa",
        "aposentadoria", "patrimônio", "carteira", "finançã",
    ]),
    ("relacionamento", [
        "relacionamento", "reconquistar", "sedução", "seducao", "atrair",
        "casamento", "divórcio", "ex ", "autoestima", "confiança",
        "paquera", "namoro", "amor", "parceiro",
    ]),
    ("desenvolvimento_pessoal", [
        "autoajuda", "mentalidade", "produtividade", "foco", "disciplina",
        "hábito", "habito", "motivação", "sucesso", "mindset",
        "liderança", "comunicação", "introvertido",
    ]),
    ("digital_afiliado", [
        "afiliado", "dropshipping", "automação", "tráfego", "trafico",
        "instagram", "youtube", "tiktok", "influencer", "digital",
        "marketing digital", "copy", "funil", "lançamento",
    ]),
    ("concurso_educacao", [
        "concurso", "enem", "oab", "aprovação", "aprovado", "vestibular",
        "prova", "edital", "gabarito", "questão", "estudo",
    ]),
    ("espiritualidade", [
        "espiritualidade", "ansiedad", "abundância", "prosperidade",
        "manifestação", "lei da atração", "gratidão", "meditação",
        "cura", "chakra",
    ]),
]

NICHO_PADRAO = "outros"

# ──────────────────────────────────────────────────────────────
# BLACKLISTS
# ──────────────────────────────────────────────────────────────

BLACKLIST_PALAVRAS = [
    # delivery / físico
    "delivery", "marmita", "marmitex", "gas", "gás", "distribuidora",
    "pizza", "burger", "lanche", "restaurante", "mercado", "farmácia",
    "pet shop", "borracharia", "oficina", "salão", "barbearia",
    # golpes / clones
    "banco ", "bradesco", "itaú", "santander", "caixa econômica",
    "nubank", "mercado pago", "pix liberado", "sua conta foi",
    "desbloqueio", "regularização", "benefício liberado", "auxílio",
    "bolsa família", "inss", "governo federal", "prefeitura",
    # esotérico suspeito
    "arcanjo", "feitiço", "macumba", "simpatia", "bruxaria",
]

BLACKLIST_DOMINIOS = [
    "blogspot", "wordpress.com", "wix.com", "weebly", "tumblr",
    "delivery", "marmita", "gas-agua", "pix-", "-pix",
    "bradesco", "itau-", "caixa-", "nubank-",
]

TLDS_ACEITOS = {
    ".com.br", ".com", ".online", ".site", ".app",
    ".net", ".io", ".digital", ".pro", ".info",
}

PLATAFORMAS = {
    "utmify.com.br", "hotmart.com", "kiwify.com.br", "kirvano.com",
    "cakto.com.br", "eduzz.com", "monetizze.com.br", "pepper.com.br",
    "klickpages.com.br", "leadlovers.com.br", "rdstation.com.br",
    "appmax.com.br", "jivochat.com", "crisp.chat", "tidio.com",
    "vturb.com.br", "videoask.com", "typebot.io", "notificamind.com", "pushnews.eu",
    "pagseguro.uol.com.br", "cieloecommerce.cielo.com.br", "sdk.mercadopago.com",
    "activecampaign.com", "mailchimp.com", "google.com", "google.com.br",
    "facebook.com", "instagram.com", "youtube.com", "googleapis.com",
    "framer.com", "lovable.app", "vercel.app", "netlify.app",
}

CONSTRUTORES_NOVOS = [
    "pages.dev", "vercel.app", "netlify.app", "lovable.app",
    "lovable.dev", "framer.app", "webflow.io", "bubble.io",
]

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def get_tld(url):
    try:
        host = urlparse(url).netloc.lower().split(":")[0]
        if host.endswith(".com.br"):
            return ".com.br"
        return "." + host.rsplit(".", 1)[-1]
    except:
        return ""

def get_dominio_raiz(url):
    try:
        host = urlparse(url).netloc.lower().split(":")[0]
        if host.endswith(".com.br"):
            partes = host.rsplit(".", 3)
            return ".".join(partes[-3:]) if len(partes) >= 3 else host
        partes = host.rsplit(".", 2)
        return ".".join(partes[-2:]) if len(partes) >= 2 else host
    except:
        return ""

def calcular_idade_dias(data_scan_str):
    """Retorna quantos dias faz desde o scan. None se não parsear."""
    if not data_scan_str:
        return None
    try:
        data = datetime.strptime(data_scan_str[:10], "%Y-%m-%d")
        return (datetime.utcnow() - data).days
    except Exception:
        return None

def detectar_nicho(texto):
    t = texto.lower()
    for nome, palavras in NICHOS:
        for p in palavras:
            if p in t:
                return nome
    return NICHO_PADRAO

def calcular_score(url, titulo, dominio, query_nome):
    texto = (titulo + " " + url + " " + dominio).lower()
    score = 0
    motivos = []

    # Blacklist imediata
    for p in BLACKLIST_PALAVRAS:
        if p in texto:
            return -99, [f"blacklist:{p}"]
    for bl in BLACKLIST_DOMINIOS:
        if bl in dominio:
            return -99, [f"dominio_bl:{bl}"]

    # TLD
    tld = get_tld(url)
    if tld not in TLDS_ACEITOS:
        score -= 5
        motivos.append(f"tld:{tld}")

    # Sem título
    if not titulo or len(titulo.strip()) < 5:
        score -= 3
        motivos.append("sem_titulo")

    # Bônus: query combinada = sinal duplo confirmado
    if "_" in query_nome and not query_nome.startswith("tracker"):
        score += 4
        motivos.append("sinal_duplo")

    # Bônus: construtor novo/quente
    for c in CONSTRUTORES_NOVOS:
        if c in url:
            score += 2
            motivos.append(f"construtor:{c}")
            break

    # Bônus: nicho detectado no título/url
    nicho = detectar_nicho(texto)
    if nicho != NICHO_PADRAO:
        score += 3
        motivos.append(f"nicho:{nicho}")

    # Bônus: indicadores de oferta rápida no título
    oferta_rapida = [
        "método", "metodo", "protocolo", "sistema", "fórmula", "formula",
        "segredo", "técnica", "desafio", "acesso", "revelado", "kit",
        "guia", "ebook", "e-book", "masterclass", "workshop",
        "r$", "grátis", "gratuito", "oferta", "promoção", "desconto",
    ]
    for o in oferta_rapida:
        if o in texto:
            score += 2
            motivos.append(f"oferta:{o}")
            break

    # Bônus: VSL / copy longa
    vsl = ["assista", "vídeo", "video", "descubra", "revelação", "antes que",
           "urgente", "atenção", "resultado", "transformação", "comprovado"]
    for v in vsl:
        if v in texto:
            score += 2
            motivos.append(f"vsl:{v}")
            break

    # Penalidade: curso / mentoria
    for p in ["curso online", "mentoria", "mastermind", "formação", "certificado"]:
        if p in texto:
            score -= 2
            motivos.append(f"penalidade:{p}")

    return score, motivos[:6]

def label_prioridade(score):
    if score >= 9:  return "S — Elite"
    if score >= 6:  return "A — Top"
    if score >= 3:  return "B — Alta"
    if score >= 0:  return "C — Média"
    return           "D — Baixa"

# ──────────────────────────────────────────────────────────────
# API
# ──────────────────────────────────────────────────────────────

def buscar(query_raw):
    query = query_raw.format(d=DIAS_ATRAS)
    headers = {"API-Key": API_KEY}
    params = {"q": query, "size": MAX_POR_QUERY}
    try:
        resp = requests.get(
            "https://urlscan.io/api/v1/search/",
            headers=headers, params=params, timeout=15
        )
        if resp.status_code == 429:
            print("  ⚠️  Rate limit. Aguardando 65s...")
            time.sleep(65)
            return buscar(query_raw)
        if resp.status_code == 401:
            print("  ❌ API key inválida")
            return []
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return []

# ──────────────────────────────────────────────────────────────
# PROCESSAMENTO
# ──────────────────────────────────────────────────────────────

def processar(resultados_brutos, query_nome):
    processados = []
    descartados = 0

    for item in resultados_brutos:
        page = item.get("page", {})
        task = item.get("task", {})

        url    = page.get("url") or task.get("url", "")
        titulo = page.get("title", "")
        pais   = page.get("country", "")
        if not url:
            continue

        dominio = get_dominio_raiz(url)
        if any(p in dominio for p in PLATAFORMAS):
            continue

        # Filtro de idade — descarta ofertas mais velhas que IDADE_MAX_DIAS
        data_scan_str = task.get("time", "")[:10]
        idade = calcular_idade_dias(data_scan_str)
        if idade is not None and idade > IDADE_MAX_DIAS:
            descartados += 1
            continue

        score, motivos = calcular_score(url, titulo, dominio, query_nome)
        if score <= -2:
            descartados += 1
            continue

        texto  = (titulo + " " + url).lower()
        nicho  = detectar_nicho(texto)
        novo   = any(c in url for c in CONSTRUTORES_NOVOS)

        processados.append({
            "prioridade":      label_prioridade(score),
            "score":           score,
            "nicho":           nicho,
            "url":             url,
            "dominio":         dominio,
            "titulo":          titulo[:120],
            "pais":            pais,
            "data_scan":       task.get("time", "")[:10],
            "idade_dias":       idade if idade is not None else "",
            "construtor_novo": "sim" if novo else "",
            "query":           query_nome,
            "motivos":         " | ".join(motivos),
            "screenshot":      f"https://urlscan.io/screenshots/{item.get('_id','')}.png",
            "detalhe":         f"https://urlscan.io/result/{item.get('_id','')}/",
        })

    return processados, descartados

def deduplicar(todos):
    vistos = {}
    for item in todos:
        chave = item["url"].rstrip("/").lower()
        if chave not in vistos or item["score"] > vistos[chave]["score"]:
            vistos[chave] = item
    return list(vistos.values())

# ──────────────────────────────────────────────────────────────
# EXPORTAÇÃO ORGANIZADA POR NICHO
# ──────────────────────────────────────────────────────────────

CAMPOS_CSV = [
    "prioridade", "score", "url", "oferta", "dominio", "titulo",
    "pais", "data_scan", "idade_dias", "construtor_novo", "query", "motivos",
    "screenshot", "preview"
]

def formatar_hyperlinks(item):
    """Converte campos de URL em fórmulas HYPERLINK do Google Sheets."""
    row = dict(item)
    url     = row.get("url", "")
    shot    = row.get("screenshot", "")
    detalhe = row.get("detalhe", "")
    titulo  = (row.get("titulo") or row.get("dominio") or "abrir")[:50].replace('"', "'")

    row["url"]        = url
    row["oferta"]     = f'=HYPERLINK("{url}","{titulo}")' if url else ""
    row["screenshot"] = f'=HYPERLINK("{shot}","📸 ver")' if shot else ""
    row["preview"]    = f'=HYPERLINK("{detalhe}","🔍 urlscan")' if detalhe else ""
    return row

def salvar_csv(resultados, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV, extrasaction="ignore")
        writer.writeheader()
        for item in resultados:
            writer.writerow(formatar_hyperlinks(item))

def organizar_e_exportar(todos, timestamp):
    # Pasta raiz com timestamp
    pasta_raiz = os.path.join(PASTA_SAIDA, timestamp)
    os.makedirs(pasta_raiz, exist_ok=True)

    # Agrupa por nicho (apenas pra relatório — sem subpastas na versão free)
    por_nicho = defaultdict(list)
    for item in todos:
        por_nicho[item["nicho"]].append(item)

    # CSV único com tudo
    todos_sorted = sorted(todos, key=lambda x: x["score"], reverse=True)
    caminho_geral = os.path.join(pasta_raiz, "_TODAS_OFERTAS.csv")
    salvar_csv(todos_sorted, caminho_geral)

    return pasta_raiz, por_nicho, [caminho_geral]

# ──────────────────────────────────────────────────────────────
# RELATÓRIO MARKDOWN
# ──────────────────────────────────────────────────────────────

def gerar_relatorio(todos, por_nicho, pasta_raiz, timestamp):
    elite = [r for r in todos if r["score"] >= 9]
    top   = [r for r in todos if 6 <= r["score"] < 9]
    alta  = [r for r in todos if 3 <= r["score"] < 6]
    novos = [r for r in todos if r["construtor_novo"] == "sim"]

    linhas = []
    linhas.append(f"# Mineração de Ofertas BR — {timestamp}")
    linhas.append(f"\n**Total único:** {len(todos)} URLs  |  "
                  f"**S Elite:** {len(elite)}  |  "
                  f"**A Top:** {len(top)}  |  "
                  f"**B Alta:** {len(alta)}  |  "
                  f"**Construtores novos:** {len(novos)}\n")

    # Top 20 geral
    linhas.append("## Top 20 geral\n")
    linhas.append("| # | Prioridade | Nicho | URL | Título |")
    linhas.append("|---|-----------|-------|-----|--------|")
    for i, r in enumerate(todos[:20], 1):
        titulo_curto = (r["titulo"] or "—")[:50]
        url_curta    = r["url"][:60]
        linhas.append(f"| {i} | {r['prioridade']} | {r['nicho']} | {url_curta} | {titulo_curto} |")

    # Por nicho
    linhas.append("\n## Por nicho\n")
    for nicho, itens in sorted(por_nicho.items(), key=lambda x: -len(x[1])):
        top_nicho = [r for r in itens if r["score"] >= 6]
        linhas.append(f"### {nicho} ({len(itens)} ofertas | {len(top_nicho)} top)\n")
        for r in itens[:5]:
            linhas.append(f"- [{r['prioridade']} score={r['score']}] {r['url']}")
            if r["titulo"]:
                linhas.append(f"  > {r['titulo'][:80]}")
        if len(itens) > 5:
            linhas.append(f"  _(+ {len(itens)-5} mais no CSV)_")
        linhas.append("")

    # Construtores novos
    if novos:
        linhas.append("## Construtores novos / quentes\n")
        linhas.append("_Lovable, Vercel, Framer — ofertas antes de tracionar_\n")
        for r in novos[:10]:
            linhas.append(f"- {r['url']}")
            if r["titulo"]:
                linhas.append(f"  > {r['titulo'][:80]}")
        linhas.append("")

    relatorio = "\n".join(linhas)
    caminho   = os.path.join(pasta_raiz, "RELATORIO.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(relatorio)
    return caminho

# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

def main():
    if API_KEY == "COLE_SUA_API_KEY_AQUI":
        print("❌ Configure sua API key!")
        print("   export URLSCAN_API_KEY='sua_chave'")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    print("\n╔══════════════════════════════════════════════╗")
    print("║   MINERADOR v3 — OFERTAS LOW TICKET BR       ║")
    print("║   @titio.digital / Movimento High Level      ║")
    print("╚══════════════════════════════════════════════╝\n")
    print(f"   Queries: {len(QUERIES)} | Dias: {DIAS_ATRAS} | Saída: {PASTA_SAIDA}/{timestamp}/\n")

    todos           = []
    total_brutos    = 0
    total_descart   = 0

    for i, (nome, query_raw) in enumerate(QUERIES, 1):
        print(f"[{i:>2}/{len(QUERIES)}] {nome}")
        brutos = buscar(query_raw)
        total_brutos += len(brutos)

        filtrados, desc = processar(brutos, nome)
        total_descart  += desc
        todos.extend(filtrados)

        status = f"  → {len(brutos)} brutos | {len(filtrados)} passaram | {desc} descartados"
        print(status)

        if i < len(QUERIES):
            time.sleep(DELAY)

    print(f"\n{'─'*50}")
    print(f"Total brutos:     {total_brutos}")
    print(f"Total descartados:{total_descart}")

    # Deduplicar
    todos = deduplicar(todos)
    todos.sort(key=lambda x: x["score"], reverse=True)
    print(f"URLs únicas:      {len(todos)}")

    # Organizar e exportar
    pasta_raiz, por_nicho, arquivos = organizar_e_exportar(todos, timestamp)
    relatorio   = gerar_relatorio(todos, por_nicho, pasta_raiz, timestamp)

    # ── Resumo final ──
    elite = [r for r in todos if r["score"] >= 9]
    top   = [r for r in todos if 6 <= r["score"] < 9]
    novos = [r for r in todos if r["construtor_novo"] == "sim"]

    print(f"\n{'═'*50}")
    print(f"✅ CONCLUÍDO — {pasta_raiz}/")
    print(f"{'═'*50}")
    print(f"   S Elite:           {len(elite)}")
    print(f"   A Top:             {len(top)}")
    print(f"   Construtores novos:{len(novos)}")
    print(f"   Nichos detectados: {len(por_nicho)}")
    print(f"\n   Pastas criadas:")
    for nicho, itens in sorted(por_nicho.items(), key=lambda x: -len(x[1])):
        top_n = len([r for r in itens if r["score"] >= 6])
        print(f"   📁 {nicho:<30} {len(itens):>3} ofertas  ({top_n} top)")

    print(f"\n   📋 Relatório: {relatorio}")
    print(f"   📄 CSV geral: {pasta_raiz}/_TODAS_OFERTAS.csv")

    # ── Upload Google Drive ──
    if DRIVE_OK:
        links = fazer_upload(pasta_raiz)
        if links.get("_pasta"):
            print(f"   🔗 Drive: {links['_pasta']}")
    else:
        print("\n  ℹ️  Drive desativado.")
        print("     Instale: pip install google-auth google-api-python-client")
        print("     Depois:  gcloud auth application-default login \\")
        print("              --scopes=https://www.googleapis.com/auth/drive.file")

    print(f"\n{'─'*50}")
    print("🔥 TOP 10:")
    for j, r in enumerate(todos[:10], 1):
        print(f"\n  {j:>2}. [{r['prioridade']}] {r['url']}")
        if r["titulo"]:
            print(f"      📝 {r['titulo'][:70]}")
        print(f"      🏷️  {r['nicho']} | score={r['score']} | {r['motivos'][:55]}")

    print(f"\n{'═'*50}\n")

def loop_comando():
    """Fica escutando no terminal. Digite /minerar pra disparar."""
    print("\n╔══════════════════════════════════════════════╗")
    print("║   AGENTE MINERADOR — @titio.digital          ║")
    print("║   Digite /minerar para iniciar               ║")
    print("║   Digite /sair    para encerrar              ║")
    print("╚══════════════════════════════════════════════╝\n")

    while True:
        try:
            cmd = input("aguardando comando > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Encerrando agente.")
            break

        if cmd == "/minerar":
            print(f"\n🚀 Iniciando mineração — limite {IDADE_MAX_DIAS} dias\n")
            main()
            print("\n✅ Mineração concluída. Aguardando próximo comando...\n")
            print("─" * 50)
            print("⚡ Versão gratuita — 12 queries | 7 dias | sem organização por nicho")
            print("   A versão Pro roda 37 queries | 60 dias | pastas por nicho + sinais duplos")
            print("─" * 50)

        elif cmd == "/sair":
            print("\n👋 Encerrando agente.")
            break

        elif cmd == "":
            pass  # enter em branco, ignora

        else:
            print(f"  Comando não reconhecido: '{cmd}'")
            print("  Comandos disponíveis: /minerar  /sair")


if __name__ == "__main__":
    loop_comando()
