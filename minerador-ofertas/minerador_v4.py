"""
MINERADOR DE OFERTAS BR v4 — Focado em ofertas REAIS para modelar
Analisa conteudo da pagina, detecta funil, valida se e pagina de vendas.

SETUP:
  pip install requests python-dotenv supabase
  python minerador_v4.py
"""

import requests, csv, json, os, time, re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

# --------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------
API_KEY        = os.environ.get("URLSCAN_API_KEY", "")  # Opcional — funciona sem key
DIAS_ATRAS     = 14
IDADE_MAX_DIAS = 14
MAX_POR_QUERY  = 100
DELAY          = 2.5
PASTA_SAIDA    = "mineracao_ofertas"
SCORE_MINIMO   = 5   # So mostra ofertas com score >= 5

# --------------------------------------------------------------
# QUERIES v4 — Sinais DUPLOS de oferta real
# Combina plataforma + sinal de checkout/venda
# --------------------------------------------------------------

QUERIES = [
    # -- Checkout direto (sinal mais forte) --
    ("hotmart_checkout",    'page.url:"pay.hotmart.com" AND date:>now-{d}d'),
    ("kiwify_checkout",     'page.url:"kiwify.com.br/pay" AND date:>now-{d}d'),
    ("kirvano_checkout",    'page.url:"kirvano.com" AND page.url:"checkout" AND date:>now-{d}d'),
    ("monetizze_checkout",  'page.url:"monetizze.com.br" AND page.url:"checkout" AND date:>now-{d}d'),
    ("eduzz_checkout",      'page.url:"eduzz.com" AND page.url:"checkout" AND date:>now-{d}d'),
    ("pepper_checkout",     'page.url:"pepper.com.br" AND page.url:"checkout" AND date:>now-{d}d'),
    ("cakto_checkout",      'page.url:"cakto.com.br" AND page.url:"checkout" AND date:>now-{d}d'),

    # -- Tracker + Gateway (sinal duplo forte) --
    ("utmify_hotmart",      "domain:utmify.com.br AND domain:hotmart.com AND date:>now-{d}d"),
    ("utmify_kiwify",       "domain:utmify.com.br AND domain:kiwify.com.br AND date:>now-{d}d"),
    ("utmify_monetizze",    "domain:utmify.com.br AND domain:monetizze.com.br AND date:>now-{d}d"),

    # -- VSL players (sinal de funil rodando) --
    ("vturb_hotmart",       "domain:vturb.com.br AND domain:hotmart.com AND date:>now-{d}d"),
    ("vturb_kiwify",        "domain:vturb.com.br AND domain:kiwify.com.br AND date:>now-{d}d"),
    ("vturb_solo",          "domain:vturb.com.br AND date:>now-{d}d"),

    # -- Paginas com titulo de oferta (titulo = sinal forte de VSL) --
    ("titulo_metodo",       'page.title:"método" AND domain:hotmart.com AND date:>now-{d}d'),
    ("titulo_protocolo",    'page.title:"protocolo" AND domain:hotmart.com AND date:>now-{d}d'),
    ("titulo_segredo",      'page.title:"segredo" AND domain:kiwify.com.br AND date:>now-{d}d'),
    ("titulo_formula",      'page.title:"fórmula" AND domain:hotmart.com AND date:>now-{d}d'),
    ("titulo_ebook",        'page.title:"ebook" AND domain:hotmart.com AND date:>now-{d}d'),
    ("titulo_guia",         'page.title:"guia" AND domain:kiwify.com.br AND date:>now-{d}d'),

    # -- Construtores novos + gateway (oferta recem-lancada) --
    ("lovable_hotmart",     "domain:lovable.app AND domain:hotmart.com AND date:>now-{d}d"),
    ("vercel_hotmart",      "domain:vercel.app AND domain:hotmart.com AND date:>now-{d}d"),
    ("vercel_kiwify",       "domain:vercel.app AND domain:kiwify.com.br AND date:>now-{d}d"),
    ("pages_hotmart",       "domain:pages.dev AND domain:hotmart.com AND date:>now-{d}d"),

    # -- Klickpages/Leadlovers (page builders de oferta) --
    ("klick_hotmart",       "domain:klickpages.com.br AND domain:hotmart.com AND date:>now-{d}d"),
    ("klick_kiwify",        "domain:klickpages.com.br AND domain:kiwify.com.br AND date:>now-{d}d"),
    ("leadlovers_hotmart",  "domain:leadlovers.com.br AND domain:hotmart.com AND date:>now-{d}d"),

    # -- Gateways solo (fallback, menos preciso) --
    ("gateway_hotmart",     "domain:hotmart.com AND date:>now-{d}d"),
    ("gateway_kiwify",      "domain:kiwify.com.br AND date:>now-{d}d"),
    ("gateway_kirvano",     "domain:kirvano.com AND date:>now-{d}d"),
    ("gateway_monetizze",   "domain:monetizze.com.br AND date:>now-{d}d"),
]

# --------------------------------------------------------------
# NICHOS — Ampliado e mais preciso
# --------------------------------------------------------------

NICHOS = [
    ("emagrecimento", [
        "emagrec", "emagrecimento", "barriga", "gordura", "dieta", "detox",
        "queima", "metabolismo", "jejum", "caloria", "peso", "obesi",
        "seca barriga", "perder peso", "secar", "magr", "slim", "fit",
    ]),
    ("saude", [
        "colesterol", "diabetes", "pressão", "tireoide", "hormônio",
        "próstata", "visão", "enxergar", "audição", "ouvir", "dor nas costas",
        "articulação", "coluna", "postura", "imunidade", "dor", "remédio",
        "natural", "receita caseira", "chá",
    ]),
    ("beleza", [
        "pele", "cabelo", "unha", "sobrancelha", "maquiagem", "skincare",
        "rejuvenesc", "manchas", "acne", "colágeno", "beleza", "estética",
        "rugas", "olheira", "celulite",
    ]),
    ("renda_extra", [
        "renda extra", "ganhar dinheiro", "lucrar", "faturar", "renda passiva",
        "trabalhar de casa", "home office", "liberdade financeira",
        "dinheiro online", "renda online", "primeira venda", "vender online",
    ]),
    ("relacionamento", [
        "relacionamento", "reconquistar", "sedução", "seducao", "atrair",
        "casamento", "divórcio", "ex ", "autoestima", "confiança",
        "paquera", "namoro", "amor", "parceiro", "marido", "esposa",
        "homem", "mulher dos sonhos",
    ]),
    ("sexualidade", [
        "libido", "impotência", "ereção", "desempenho sexual", "prazer",
        "próstata", "testosterona", "vigor", "ejaculação", "orgasmo",
    ]),
    ("desenvolvimento_pessoal", [
        "mentalidade", "produtividade", "foco", "disciplina",
        "hábito", "habito", "motivação", "sucesso", "mindset",
        "liderança", "comunicação", "introvertido", "ansiedade",
    ]),
    ("digital_marketing", [
        "afiliado", "dropshipping", "tráfego", "trafico pago",
        "instagram", "tiktok", "marketing digital", "copy", "funil",
        "lançamento", "infoproduto",
    ]),
    ("financas", [
        "investimento", "investir", "cripto", "bitcoin", "trader", "trading",
        "forex", "day trade", "renda fixa", "patrimônio",
    ]),
    ("concurso", [
        "concurso", "enem", "oab", "aprovação", "vestibular",
        "prova", "edital", "questão", "estudo",
    ]),
    ("espiritualidade", [
        "abundância", "prosperidade", "manifestação", "lei da atração",
        "gratidão", "meditação", "oração", "fé", "deus",
    ]),
    ("pet", [
        "cachorro", "gato", "pet", "adestrar", "adestramento",
        "latir", "filhote",
    ]),
]

NICHO_PADRAO = "outros"

# --------------------------------------------------------------
# BLACKLISTS — Agressiva contra nao-ofertas
# --------------------------------------------------------------

BLACKLIST_PALAVRAS = [
    # Nao e oferta
    "login", "entrar", "cadastro", "dashboard", "painel", "admin",
    "recuperar senha", "esqueci", "minha conta",
    # Institucional
    "agência", "agencia", "consultoria", "empresa", "quem somos",
    "sobre nós", "nossos serviços", "contato", "fale conosco",
    # Delivery / fisico
    "delivery", "marmita", "pizza", "burger", "restaurante",
    "farmácia", "pet shop", "barbearia", "salão",
    # Golpes
    "banco ", "bradesco", "itaú", "santander", "nubank",
    "pix liberado", "benefício liberado", "auxílio", "inss",
    # SaaS / plataforma
    "plataforma de", "sistema de gestão", "erp", "crm",
    "saas", "api", "integração", "developer",
    # Educacao formal
    "faculdade", "universidade", "pós-graduação", "mba",
    "certificado iso", "graduação",
]

BLACKLIST_DOMINIOS = [
    "blogspot", "wordpress.com", "wix.com", "weebly", "tumblr",
    "bradesco", "itau-", "caixa-", "nubank-",
    "gov.br", "edu.br", "org.br",
    "linkedin.com", "facebook.com", "instagram.com", "twitter.com",
]

# Palavras no titulo que indicam que NAO e pagina de vendas
TITULO_BLACKLIST = [
    "login", "entrar", "sign in", "log in", "cadastr",
    "dashboard", "painel", "admin", "hub de",
    "404", "not found", "error", "forbidden",
    "academy", "plataforma", "app store", "google play",
]

TLDS_ACEITOS = {
    ".com.br", ".com", ".online", ".site", ".app",
    ".net", ".io", ".digital", ".pro", ".info",
}

PLATAFORMAS_IGNORAR = {
    "hotmart.com", "kiwify.com.br", "kirvano.com",
    "cakto.com.br", "eduzz.com", "monetizze.com.br", "pepper.com.br",
    "pay.hotmart.com", "pay.kiwify.com.br",
}

# --------------------------------------------------------------
# SINAIS DE OFERTA REAL (para scoring)
# --------------------------------------------------------------

SINAIS_TITULO_OFERTA = [
    # Formatos classicos de VSL/oferta
    ("método", 3), ("metodo", 3), ("protocolo", 3), ("sistema", 2),
    ("fórmula", 3), ("formula", 3), ("segredo", 3), ("revelado", 3),
    ("técnica", 2), ("desafio", 2),
    # Formato produto
    ("ebook", 2), ("e-book", 2), ("guia", 2), ("kit", 2),
    ("masterclass", 2), ("workshop", 2), ("treinamento", 2),
    # Preço / oferta
    ("r$", 4), ("reais", 2), ("grátis", 2), ("gratuito", 2),
    ("oferta", 3), ("promoção", 2), ("desconto", 2),
    ("por apenas", 4), ("de r$", 4), ("acesso imediato", 3),
    # Urgencia
    ("últimas vagas", 3), ("vagas limitadas", 3), ("só hoje", 3),
    ("antes que", 2), ("urgente", 2), ("atenção", 2),
    # VSL
    ("assista", 3), ("vídeo", 2), ("descubra", 2),
    ("resultado", 2), ("transformação", 2), ("comprovado", 2),
    ("depoimento", 3), ("garantia", 3),
    # Dor / promessa
    ("sem dieta", 3), ("sem exercício", 3), ("em 7 dias", 3),
    ("em 30 dias", 3), ("em 21 dias", 3), ("rápido", 2),
    ("simples", 2), ("natural", 2), ("caseiro", 2),
]

SINAIS_URL_OFERTA = [
    # Paginas de venda/captura
    ("checkout", 5), ("/pay/", 5), ("/comprar", 4),
    ("/oferta", 4), ("/vsl", 5), ("/video", 2),
    ("/lp/", 3), ("/landing", 3), ("/captura", 3),
    ("/obrigado", 3), ("/parabens", 3), ("/confirmado", 3),
    ("/upsell", 5), ("/orderbump", 5), ("/downsell", 5),
    ("/bonus", 3), ("/especial", 3),
    # Sinais de funil
    ("/step", 2), ("/etapa", 2), ("/fase", 2),
]

# --------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------

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
    if not data_scan_str:
        return None
    try:
        data = datetime.strptime(data_scan_str[:10], "%Y-%m-%d")
        return (datetime.utcnow() - data).days
    except:
        return None

def detectar_nicho(texto):
    t = texto.lower()
    for nome, palavras in NICHOS:
        for p in palavras:
            if p in t:
                return nome
    return NICHO_PADRAO

def extrair_dominio_pagina(url):
    """Retorna o dominio da pagina escaneada (nao do gateway)."""
    try:
        host = urlparse(url).netloc.lower().split(":")[0]
        # Se for URL do gateway, tentar extrair o referrer
        for gw in PLATAFORMAS_IGNORAR:
            if gw in host:
                return None
        return host
    except:
        return None

# --------------------------------------------------------------
# SCORING v4 — Calibrado para encontrar ofertas modelaveis
# --------------------------------------------------------------

def calcular_score_v4(url, titulo, dominio, query_nome, page_data=None):
    texto_titulo = (titulo or "").lower()
    texto_url = url.lower()
    texto = f"{texto_titulo} {texto_url} {dominio}".lower()
    score = 0
    motivos = []

    # -- BLACKLIST IMEDIATA --
    for p in BLACKLIST_PALAVRAS:
        if p in texto:
            return -99, [f"BL:{p}"], "descartado"

    for bl in BLACKLIST_DOMINIOS:
        if bl in dominio:
            return -99, [f"BL_DOM:{bl}"], "descartado"

    for bt in TITULO_BLACKLIST:
        if bt in texto_titulo:
            return -99, [f"BL_TIT:{bt}"], "descartado"

    # -- TLD --
    tld = get_tld(url)
    if tld not in TLDS_ACEITOS:
        score -= 5
        motivos.append(f"tld:{tld}")

    # -- TITULO VAZIO --
    if not titulo or len(titulo.strip()) < 8:
        score -= 4
        motivos.append("sem_titulo")

    # -- SINAIS DE OFERTA NO TITULO (+3 a +4 cada) --
    titulo_hits = 0
    for sinal, pts in SINAIS_TITULO_OFERTA:
        if sinal in texto_titulo:
            score += pts
            if titulo_hits < 3:
                motivos.append(f"TIT:{sinal}")
            titulo_hits += 1

    # -- SINAIS DE OFERTA NA URL (+2 a +5 cada) --
    url_hits = 0
    for sinal, pts in SINAIS_URL_OFERTA:
        if sinal in texto_url:
            score += pts
            if url_hits < 2:
                motivos.append(f"URL:{sinal}")
            url_hits += 1

    # -- QUERY TYPE BONUS --
    if "checkout" in query_nome:
        score += 5
        motivos.append("Q:checkout")
    elif "vturb" in query_nome:
        score += 4
        motivos.append("Q:vsl_player")
    elif "titulo_" in query_nome:
        score += 3
        motivos.append("Q:titulo_match")
    elif "_" in query_nome and "gateway" not in query_nome:
        score += 3
        motivos.append("Q:sinal_duplo")

    # -- NICHO DETECTADO --
    nicho = detectar_nicho(texto)
    if nicho != NICHO_PADRAO:
        score += 2
        motivos.append(f"N:{nicho}")
    else:
        score -= 2
        motivos.append("sem_nicho")

    # -- CONSTRUTOR NOVO --
    construtores = ["pages.dev", "vercel.app", "netlify.app", "lovable.app",
                    "lovable.dev", "framer.app"]
    for c in construtores:
        if c in texto_url:
            score += 2
            motivos.append(f"NOVO:{c}")
            break

    # -- PENALIDADES --
    for p in ["curso online", "mentoria", "mastermind", "formação completa",
              "certificado", "graduação"]:
        if p in texto:
            score -= 3
            motivos.append(f"PEN:{p}")

    # Dominio muito generico / curto
    if dominio and len(dominio.split(".")[0]) <= 3:
        score -= 2
        motivos.append("dom_generico")

    # -- CLASSIFICACAO --
    if score >= 12:
        tier = "S"
    elif score >= 8:
        tier = "A"
    elif score >= 5:
        tier = "B"
    elif score >= 2:
        tier = "C"
    else:
        tier = "D"

    return score, motivos[:8], tier

def label_tier(tier, score):
    labels = {
        "S": "S - MODELAR JA",
        "A": "A - Top (revisar)",
        "B": "B - Potencial",
        "C": "C - Talvez",
        "D": "D - Ignorar",
    }
    return labels.get(tier, "D - Ignorar")

# --------------------------------------------------------------
# ANALISE DE CONTEUDO (urlscan result API)
# --------------------------------------------------------------

def analisar_resultado_urlscan(scan_id):
    """Busca detalhes do scan para detectar sinais de oferta no conteudo."""
    if not scan_id:
        return {}

    try:
        resp = requests.get(
            f"https://urlscan.io/api/v1/result/{scan_id}/",
            timeout=10
        )
        if resp.status_code != 200:
            return {}

        data = resp.json()
        sinais = {}

        # Verificar requests feitas pela pagina (gateways, trackers)
        requests_list = data.get("lists", {}).get("urls", [])
        domains = data.get("lists", {}).get("domains", [])

        gateways_detectados = []
        trackers_detectados = []
        vsl_detectados = []

        gateway_domains = ["hotmart.com", "kiwify.com.br", "kirvano.com",
                          "monetizze.com.br", "eduzz.com", "pepper.com.br",
                          "cakto.com.br", "pay.hotmart.com"]
        tracker_domains = ["utmify.com.br", "rdstation.com.br", "appmax.com.br",
                          "activecampaign.com", "mailchimp.com"]
        vsl_domains = ["vturb.com.br", "youtube.com", "vimeo.com",
                      "wistia.com", "videoask.com"]

        for d in domains:
            d_lower = d.lower()
            for gw in gateway_domains:
                if gw in d_lower:
                    gateways_detectados.append(gw)
            for tr in tracker_domains:
                if tr in d_lower:
                    trackers_detectados.append(tr)
            for vs in vsl_domains:
                if vs in d_lower:
                    vsl_detectados.append(vs)

        sinais["gateways"] = list(set(gateways_detectados))
        sinais["trackers"] = list(set(trackers_detectados))
        sinais["vsl"] = list(set(vsl_detectados))
        sinais["total_requests"] = len(requests_list)
        sinais["total_domains"] = len(domains)

        return sinais

    except:
        return {}

def bonus_conteudo(sinais):
    """Calcula bonus baseado na analise de conteudo."""
    bonus = 0
    motivos = []

    if sinais.get("gateways"):
        bonus += 4
        motivos.append(f"GW:{','.join(sinais['gateways'][:2])}")

    if sinais.get("trackers"):
        bonus += 3
        motivos.append(f"TRK:{','.join(sinais['trackers'][:2])}")

    if sinais.get("vsl"):
        bonus += 3
        motivos.append(f"VSL:{','.join(sinais['vsl'][:1])}")

    # Muitos requests = pagina complexa (oferta real tem muitos scripts)
    total_req = sinais.get("total_requests", 0)
    if total_req > 30:
        bonus += 1
        motivos.append(f"REQ:{total_req}")

    return bonus, motivos

# --------------------------------------------------------------
# API
# --------------------------------------------------------------

def buscar(query_raw):
    query = query_raw.format(d=DIAS_ATRAS)
    headers = {}
    if API_KEY:
        headers["API-Key"] = API_KEY
    params = {"q": query, "size": MAX_POR_QUERY}
    try:
        resp = requests.get(
            "https://urlscan.io/api/v1/search/",
            headers=headers, params=params, timeout=15
        )
        if resp.status_code == 429:
            print("  !! Rate limit. Aguardando 65s...")
            time.sleep(65)
            return buscar(query_raw)
        if resp.status_code == 401:
            print("  !! API key invalida/desabilitada, tentando sem key...")
            headers.pop("API-Key", None)
            resp = requests.get(
                "https://urlscan.io/api/v1/search/",
                headers=headers, params=params, timeout=15
            )
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        print(f"  !! Erro: {e}")
        return []

# --------------------------------------------------------------
# PROCESSAMENTO v4
# --------------------------------------------------------------

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

        # Ignorar URLs que sao da propria plataforma
        dominio_pagina = extrair_dominio_pagina(url)
        if dominio_pagina is None:
            continue

        # Filtro de idade
        data_scan_str = task.get("time", "")[:10]
        idade = calcular_idade_dias(data_scan_str)
        if idade is not None and idade > IDADE_MAX_DIAS:
            descartados += 1
            continue

        score, motivos, tier = calcular_score_v4(url, titulo, dominio, query_nome)
        if score <= -2:
            descartados += 1
            continue

        texto  = (titulo + " " + url).lower()
        nicho  = detectar_nicho(texto)

        novo = any(c in url for c in ["pages.dev", "vercel.app", "netlify.app",
                                       "lovable.app", "framer.app"])

        scan_id = item.get("_id", "")

        processados.append({
            "tier":            tier,
            "prioridade":      label_tier(tier, score),
            "score":           score,
            "nicho":           nicho,
            "url":             url,
            "dominio":         dominio,
            "titulo":          titulo[:120],
            "pais":            pais,
            "data_scan":       data_scan_str,
            "idade_dias":      idade if idade is not None else "",
            "construtor_novo": "sim" if novo else "",
            "query":           query_nome,
            "motivos":         " | ".join(motivos),
            "scan_id":         scan_id,
            "screenshot":      f"https://urlscan.io/screenshots/{scan_id}.png",
            "detalhe":         f"https://urlscan.io/result/{scan_id}/",
        })

    return processados, descartados

def deduplicar(todos):
    vistos = {}
    for item in todos:
        # Normalizar URL
        chave = item["url"].rstrip("/").lower()
        # Remover query params para dedup
        parsed = urlparse(chave)
        chave_limpa = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

        if chave_limpa not in vistos or item["score"] > vistos[chave_limpa]["score"]:
            vistos[chave_limpa] = item
    return list(vistos.values())

# --------------------------------------------------------------
# DEEP ANALYSIS — Analisa top ofertas via urlscan result
# --------------------------------------------------------------

def deep_analyze_top(todos, top_n=30):
    """Analisa as top N ofertas buscando sinais de conteudo."""
    print(f"\n  Analisando conteudo das top {top_n} ofertas...")
    candidates = todos[:top_n]

    for i, item in enumerate(candidates):
        scan_id = item.get("scan_id", "")
        if not scan_id:
            continue

        sinais = analisar_resultado_urlscan(scan_id)
        if sinais:
            bonus, bonus_motivos = bonus_conteudo(sinais)
            item["score"] += bonus
            if bonus_motivos:
                item["motivos"] += " | " + " | ".join(bonus_motivos)
            item["gateways"] = ", ".join(sinais.get("gateways", []))
            item["trackers"] = ", ".join(sinais.get("trackers", []))
            item["vsl_player"] = ", ".join(sinais.get("vsl", []))

            # Recalcular tier
            s = item["score"]
            if s >= 12:   item["tier"] = "S"
            elif s >= 8:  item["tier"] = "A"
            elif s >= 5:  item["tier"] = "B"
            elif s >= 2:  item["tier"] = "C"
            else:         item["tier"] = "D"
            item["prioridade"] = label_tier(item["tier"], s)

        if i < len(candidates) - 1:
            time.sleep(1)  # Rate limit

    # Re-sort
    todos.sort(key=lambda x: x["score"], reverse=True)
    return todos

# --------------------------------------------------------------
# EXPORTACAO
# --------------------------------------------------------------

CAMPOS_CSV = [
    "prioridade", "score", "nicho", "url", "oferta", "dominio", "titulo",
    "gateways", "trackers", "vsl_player",
    "pais", "data_scan", "idade_dias", "construtor_novo", "query", "motivos",
    "screenshot", "preview"
]

def formatar_hyperlinks(item):
    row = dict(item)
    url     = row.get("url", "")
    shot    = row.get("screenshot", "")
    detalhe = row.get("detalhe", "")
    titulo  = (row.get("titulo") or row.get("dominio") or "abrir")[:50].replace('"', "'")

    row["oferta"]     = f'=HYPERLINK("{url}","{titulo}")' if url else ""
    row["screenshot"] = f'=HYPERLINK("{shot}","ver")' if shot else ""
    row["preview"]    = f'=HYPERLINK("{detalhe}","urlscan")' if detalhe else ""
    return row

def salvar_csv(resultados, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV, extrasaction="ignore")
        writer.writeheader()
        for item in resultados:
            writer.writerow(formatar_hyperlinks(item))

def organizar_e_exportar(todos, timestamp):
    pasta_raiz = os.path.join(PASTA_SAIDA, timestamp)
    os.makedirs(pasta_raiz, exist_ok=True)

    por_nicho = defaultdict(list)
    for item in todos:
        por_nicho[item["nicho"]].append(item)

    # CSV com TUDO (score >= SCORE_MINIMO)
    bons = [t for t in todos if t["score"] >= SCORE_MINIMO]
    caminho_geral = os.path.join(pasta_raiz, "_MELHORES_OFERTAS.csv")
    salvar_csv(bons, caminho_geral)

    # CSV com TODAS (inclui score baixo, para referencia)
    caminho_todas = os.path.join(pasta_raiz, "_TODAS_OFERTAS.csv")
    salvar_csv(todos, caminho_todas)

    # CSV por nicho (top nichos)
    for nicho, itens in por_nicho.items():
        if nicho == NICHO_PADRAO:
            continue
        bons_nicho = [i for i in itens if i["score"] >= SCORE_MINIMO]
        if bons_nicho:
            caminho = os.path.join(pasta_raiz, f"nicho_{nicho}.csv")
            salvar_csv(bons_nicho, caminho)

    return pasta_raiz, por_nicho, caminho_geral

# --------------------------------------------------------------
# RELATORIO v4
# --------------------------------------------------------------

def gerar_relatorio(todos, por_nicho, pasta_raiz, timestamp):
    s_tier = [r for r in todos if r["tier"] == "S"]
    a_tier = [r for r in todos if r["tier"] == "A"]
    b_tier = [r for r in todos if r["tier"] == "B"]
    bons   = [r for r in todos if r["score"] >= SCORE_MINIMO]

    linhas = []
    linhas.append(f"# Mineracao v4 — Ofertas para MODELAR — {timestamp}")
    linhas.append(f"\n**Total unico:** {len(todos)} | "
                  f"**Modelaveis (score>={SCORE_MINIMO}):** {len(bons)} | "
                  f"**S MODELAR JA:** {len(s_tier)} | "
                  f"**A Top:** {len(a_tier)} | "
                  f"**B Potencial:** {len(b_tier)}\n")

    # SECAO: MODELAR JA
    if s_tier:
        linhas.append("## S — MODELAR JA (score >= 12)\n")
        linhas.append("Estas ofertas tem sinais fortes de funil ativo. Prioridade maxima.\n")
        for i, r in enumerate(s_tier, 1):
            linhas.append(f"### {i}. {r['titulo'] or r['dominio']}")
            linhas.append(f"- **URL:** {r['url']}")
            linhas.append(f"- **Nicho:** {r['nicho']} | **Score:** {r['score']}")
            linhas.append(f"- **Motivos:** {r['motivos']}")
            if r.get("gateways"):
                linhas.append(f"- **Gateways:** {r['gateways']}")
            if r.get("trackers"):
                linhas.append(f"- **Trackers:** {r['trackers']}")
            if r.get("vsl_player"):
                linhas.append(f"- **VSL Player:** {r['vsl_player']}")
            linhas.append(f"- **Screenshot:** {r['screenshot']}")
            linhas.append("")

    # SECAO: TOP
    if a_tier:
        linhas.append("## A — Top para revisar (score 8-11)\n")
        for i, r in enumerate(a_tier[:15], 1):
            titulo_curto = (r["titulo"] or "—")[:60]
            linhas.append(f"{i}. [{r['nicho']}] **{titulo_curto}**")
            linhas.append(f"   {r['url']}")
            linhas.append(f"   Score: {r['score']} | {r['motivos'][:80]}")
            linhas.append("")

    # SECAO: Por nicho (so nichos com ofertas boas)
    linhas.append("\n## Distribuicao por nicho\n")
    linhas.append("| Nicho | Total | Modelaveis | Melhor Score |")
    linhas.append("|-------|-------|-----------|-------------|")
    for nicho, itens in sorted(por_nicho.items(), key=lambda x: -max(i["score"] for i in x[1])):
        bons_n = [r for r in itens if r["score"] >= SCORE_MINIMO]
        melhor = max(i["score"] for i in itens)
        linhas.append(f"| {nicho} | {len(itens)} | {len(bons_n)} | {melhor} |")

    # SECAO: Resumo executivo
    linhas.append("\n## Como usar este relatorio\n")
    linhas.append("1. **S — MODELAR JA**: Abra cada URL, analise o funil, modele a oferta")
    linhas.append("2. **A — Top**: Revise manualmente, podem ser ofertas boas para modelar")
    linhas.append("3. **B — Potencial**: So se nao tiver S ou A suficientes")
    linhas.append("4. Use `/briefing` no Claude Code para gerar o briefing de cada oferta")

    relatorio = "\n".join(linhas)
    caminho   = os.path.join(pasta_raiz, "RELATORIO.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(relatorio)
    return caminho

# --------------------------------------------------------------
# MAIN
# --------------------------------------------------------------

def main():
    # API key e opcional - funciona sem ela (rate limit menor)
    if API_KEY:
        print(f"  API Key: {API_KEY[:8]}...")
    else:
        print("  Sem API key - usando modo anonimo (rate limit 2/min)")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    print("\n" + "=" * 55)
    print("  MINERADOR v4 - OFERTAS PARA MODELAR")
    print("  Foco: paginas de vendas reais com funil ativo")
    print("=" * 55)
    print(f"\n  Queries: {len(QUERIES)} | Dias: {DIAS_ATRAS} | Score min: {SCORE_MINIMO}")
    print(f"  Saida: {PASTA_SAIDA}/{timestamp}/\n")

    todos         = []
    total_brutos  = 0
    total_descart = 0

    for i, (nome, query_raw) in enumerate(QUERIES, 1):
        print(f"[{i:>2}/{len(QUERIES)}] {nome}")
        brutos = buscar(query_raw)
        total_brutos += len(brutos)

        filtrados, desc = processar(brutos, nome)
        total_descart  += desc
        todos.extend(filtrados)

        print(f"  -> {len(brutos)} brutos | {len(filtrados)} passaram | {desc} descartados")

        if i < len(QUERIES):
            time.sleep(DELAY)

    print(f"\n{'-'*55}")
    print(f"Total brutos:      {total_brutos}")
    print(f"Total descartados: {total_descart}")

    # Deduplicar e ordenar
    todos = deduplicar(todos)
    todos.sort(key=lambda x: x["score"], reverse=True)
    print(f"URLs unicas:       {len(todos)}")

    # Deep analysis das top ofertas
    if todos:
        todos = deep_analyze_top(todos, top_n=min(30, len(todos)))

    # Filtrar para relatorio
    bons = [t for t in todos if t["score"] >= SCORE_MINIMO]
    print(f"Ofertas modelaveis (score>={SCORE_MINIMO}): {len(bons)}")

    # Exportar
    pasta_raiz, por_nicho, csv_path = organizar_e_exportar(todos, timestamp)
    relatorio = gerar_relatorio(todos, por_nicho, pasta_raiz, timestamp)

    # Resumo
    s_tier = [r for r in todos if r["tier"] == "S"]
    a_tier = [r for r in todos if r["tier"] == "A"]
    b_tier = [r for r in todos if r["tier"] == "B"]

    print(f"\n{'='*55}")
    print(f"  RESULTADO - {pasta_raiz}/")
    print(f"{'='*55}")
    print(f"  S MODELAR JA:    {len(s_tier)}")
    print(f"  A Top:           {len(a_tier)}")
    print(f"  B Potencial:     {len(b_tier)}")
    print(f"  Nichos:          {len(por_nicho)}")

    if s_tier:
        print(f"\n  === MODELAR JA ===")
        for j, r in enumerate(s_tier[:10], 1):
            print(f"\n  {j}. {r['url']}")
            print(f"     {r['titulo'][:70]}")
            print(f"     Nicho: {r['nicho']} | Score: {r['score']}")
            print(f"     {r['motivos'][:70]}")

    if a_tier:
        print(f"\n  === TOP (revisar) ===")
        for j, r in enumerate(a_tier[:10], 1):
            print(f"\n  {j}. {r['url']}")
            print(f"     {r['titulo'][:70]}")
            print(f"     Nicho: {r['nicho']} | Score: {r['score']}")

    print(f"\n  Relatorio: {relatorio}")
    print(f"  CSV melhores: {csv_path}")
    print(f"{'='*55}\n")

    return todos


if __name__ == "__main__":
    todos = main()
