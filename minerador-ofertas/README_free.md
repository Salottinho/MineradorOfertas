# Agente Minerador de Ofertas BR — Versão Gratuita
### @titio.digital — Movimento High Level ⭕️

Esse agente vasculha a internet em busca de páginas de venda de infoprodutos brasileiros — usando as ferramentas que os próprios produtores usam (gateways, trackers, construtores de página) como sinal de detecção. O resultado sai num CSV pronto pra abrir no Google Sheets com links clicáveis e score de qualidade.

> **Versão gratuita:** 12 queries | últimos 7 dias | CSV único
> **Versão Pro:** 37 queries | 60 dias | organização automática por nicho + sinais duplos

---

## O que você vai precisar

- **Python 3** instalado na máquina
- **API Key gratuita** do urlscan.io
- **Terminal** (nativo do Mac/Linux, PowerShell no Windows, ou integrado no VSCode/Antigravity)

---

## Passo 1 — Verificar se Python está instalado

Abre o terminal e digita:

```bash
python3 --version
```

Se aparecer algo como `Python 3.9.x` ou superior, tá bom. Se não aparecer, baixa em **python.org/downloads** e instala.

---

## Passo 2 — Pegar sua API Key gratuita

1. Acessa **urlscan.io/user/signup** e cria uma conta grátis
2. Vai em **urlscan.io/user/profile/**
3. Na seção **API Key**, copia a chave

---

## Passo 3 — Configurar a API Key no agente

Abre o arquivo `minerador_v3_free.py` em qualquer editor de texto (VSCode, Antigravity, Bloco de Notas, TextEdit).

Procura essa linha perto do topo:

```python
API_KEY = os.environ.get("URLSCAN_API_KEY", "COLE_SUA_API_KEY_AQUI")
```

Substitui `COLE_SUA_API_KEY_AQUI` pela sua chave:

```python
API_KEY = os.environ.get("URLSCAN_API_KEY", "sua-chave-aqui")
```

Salva o arquivo.

---

## Passo 4 — Configurar a pasta de saída (opcional)

Por padrão os resultados ficam numa pasta `mineracao_ofertas` dentro do mesmo diretório do arquivo. Se quiser salvar direto no Google Drive, instala o **Google Drive Desktop** e aponta o caminho.

Procura essa linha:

```python
PASTA_SAIDA = "mineracao_ofertas"
```

Exemplo com Google Drive Desktop no Mac:

```python
PASTA_SAIDA = "/Users/SEU_USUARIO/Library/CloudStorage/GoogleDrive-SEU_EMAIL/Meu Drive/Mineracoes"
```

Se não quiser mexer, deixa como está.

---

## Passo 5 — Instalar a dependência

No terminal, navega até a pasta onde está o arquivo:

```bash
cd /caminho/para/a/pasta
```

Instala o pacote necessário:

**Mac / Linux:**
```bash
pip3 install requests
```

**Windows:**
```bash
pip install requests
```

---

## Passo 6 — Rodar o agente

**Mac / Linux:**
```bash
python3 minerador_v3_free.py
```

**Windows:**
```bash
python minerador_v3_free.py
```

Vai aparecer:

```
╔══════════════════════════════════════════════╗
║   AGENTE MINERADOR — @titio.digital          ║
║   Digite /minerar para iniciar               ║
║   Digite /sair    para encerrar              ║
╚══════════════════════════════════════════════╝

aguardando comando >
```

---

## Passo 7 — Minerar

Digita e aperta Enter:

```
/minerar
```

O agente roda as 12 queries e mostra o progresso em tempo real. Leva em média 2 a 3 minutos.

Para encerrar:
```
/sair
```

---

## O que é gerado

```
mineracao_ofertas/
  20260329_0350/
    _TODAS_OFERTAS.csv    ← todas as ofertas ordenadas por score
    RELATORIO.md          ← resumo com top 20
```

---

## Como abrir no Google Sheets

1. Vai até a pasta no Google Drive
2. Clica no arquivo `.csv` com botão direito
3. **Abrir com → Planilhas Google**

As colunas de link (`oferta`, `screenshot`, `preview`) já aparecem clicáveis automaticamente.

**Colunas principais:**

| Coluna | O que é |
|--------|---------|
| `prioridade` | S Elite / A Top / B Alta / C Média |
| `score` | Pontuação do agente (maior = melhor) |
| `url` | Link direto da página de venda |
| `oferta` | Link clicável com título da página |
| `titulo` | Título da página capturado |
| `nicho` | Nicho detectado automaticamente |
| `idade_dias` | Quantos dias a oferta está no ar |
| `screenshot` | Foto da página capturada pelo urlscan |
| `preview` | Análise completa no urlscan |

---

## Dúvidas frequentes

**O agente pede API key toda vez?**
Não, se você editou o arquivo e colou a key diretamente no Passo 3. O problema só acontece se usar o comando `export` no terminal — que some ao fechar. Editar o arquivo resolve de vez.

**Quantas ofertas encontra?**
Com 12 queries e 7 dias, espera entre 80 e 200 URLs únicas por mineração, já filtradas e pontuadas.

**Posso rodar toda semana?**
Sim. Cada execução cria uma pasta nova com o timestamp — os resultados anteriores ficam intactos.

**O agente acessa as páginas?**
Não. Consulta apenas o banco histórico do urlscan.io, que já escaneou e fotografou as páginas automaticamente.

**Limite da API gratuita?**
30 requests por minuto. O agente respeita esse limite com delay automático.

**Por que a versão Pro tem mais resultado?**
37 queries vs 12, 60 dias vs 7, sinais duplos (páginas que carregam duas ferramentas BR ao mesmo tempo = mais preciso), e organização automática por nicho em pastas separadas.

---

## Suporte

**@titio.digital** no Instagram
