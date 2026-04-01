# MineradorOfertas — Sistema de Infoprodutos Low Ticket BR

Sistema completo para minerar, modelar e produzir infoprodutos low ticket no mercado brasileiro.

## Arquitetura

```
Minerar ofertas -> Escolher produto -> Briefing -> Paginas HTML -> Copy -> Entregaveis
```

## Estrutura

```
MineradorOfertas/
  agentes/              # Agentes especializados (pagina, copy, entregas)
  skills/               # Skills compartilhadas (frontend, backend, copywriting)
  minerador-ofertas/    # Minerador de ofertas BR via urlscan.io
  produtos-entrada/     # Produtos brutos para modelar
  produtos-modelados/   # Output: HTML, copy, entregaveis
  .claude/commands/     # Slash commands para Claude Code
  briefing-ativo.md     # Briefing atual (gerado automaticamente)
```

## Slash Commands

| Comando | Funcao |
|---------|--------|
| `/briefing` | Gera briefing a partir de produto |
| `/AGENTE-PAGINA` | Gera paginas HTML completas |
| `/AGENTE-COPY` | Gera copy de alta conversao |
| `/AGENTE-ENTREGAS` | Produz entregaveis reais |
| `/minerar` | Executa mineracao de ofertas |
| `/status` | Status do projeto e ultimas mineracoes |

## Setup

1. `pip install requests`
2. Configurar `.env` com URLSCAN_API_KEY e credenciais Supabase
3. Abrir pasta no Claude Code / Antigravity

## Stack

- Python 3 + requests (minerador)
- Supabase (banco de dados)
- HTML/CSS puro (paginas de venda)
- Claude Code (agentes e automacao)

## @titio.digital — Movimento High Level
