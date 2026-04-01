# SKILL — FRONTEND & UI/UX

> **OBRIGATÓRIO:** Leia o arquivo `briefing-ativo.md` antes de executar qualquer tarefa. Use os dados de nicho, público e identidade visual sugerida do briefing para definir o estilo da página.

## QUANDO USAR
Use esta skill sempre que precisar gerar ou melhorar páginas HTML. Antes de escrever qualquer código, execute o PROCESSO DE ANÁLISE VISUAL abaixo.

---

## PROCESSO DE ANÁLISE VISUAL

### PASSO 1 — IDENTIFICA O NICHO E A PROMESSA
Leia o briefing-ativo.md e classifique:
- Qual é o nicho? (finanças, emagrecimento, renda extra, relacionamento, produtividade, saúde, concursos)
- Qual é a emoção dominante da promessa? (alívio, conquista, pertencimento, urgência, transformação)
- Quem é o público? (iniciante ansioso / intermediário cético / avançado que quer resultado rápido)

### PASSO 2 — ESCOLHE O ESTILO VISUAL
Com base no nicho e emoção, escolhe um dos estilos abaixo e declara qual escolheu antes de gerar o código.

---

## ESTILOS VISUAIS POR NICHO

### ESTILO 1 — CLAREZA FINANCEIRA
**Usar para:** finanças pessoais, organização, planilhas, controle de gastos
**Emoção:** alívio, controle, segurança
**Paleta:**
```css
--bg: #f8fafc;
--surface: #ffffff;
--border: #e2e8f0;
--text: #0f172a;
--muted: #64748b;
--accent: #0ea5e9;      /* azul confiança */
--cta: #16a34a;         /* verde conversão */
--danger: #dc2626;      /* urgência */
```
**Tipografia:** Plus Jakarta Sans (headlines) + Inter (corpo)
**Características:** Muito espaço em branco, números em destaque, ícones de gráfico/dinheiro, depoimentos com foto real, selos de segurança visíveis

---

### ESTILO 2 — TRANSFORMAÇÃO BOLD
**Usar para:** emagrecimento, fitness, mudança de hábitos, saúde
**Emoção:** conquista, energia, motivação
**Paleta:**
```css
--bg: #0a0a0a;
--surface: #111111;
--border: #222222;
--text: #f5f5f5;
--muted: #888888;
--accent: #f97316;      /* laranja energia */
--cta: #f97316;
--highlight: #fbbf24;   /* amarelo destaque */
```
**Tipografia:** Bebas Neue ou Syne (headlines bold) + Roboto (corpo)
**Características:** Contraste extremo, before/after visual, números grandes (kg perdidos, dias), CTA enorme, urgência visual

---

### ESTILO 3 — RENDA & OPORTUNIDADE
**Usar para:** renda extra, infoprodutos, tráfego pago, marketing digital
**Emoção:** oportunidade, urgência, prova social
**Paleta:**
```css
--bg: #0f0f0f;
--surface: #1a1a1a;
--border: #2a2a2a;
--text: #e8e8e8;
--muted: #666666;
--accent: #a3e635;      /* verde limão resultado */
--cta: #22c55e;
--gold: #f59e0b;        /* dourado prova social */
```
**Tipografia:** Syne (headlines) + JetBrains Mono (números/stats)
**Características:** Screenshots de resultados, contador de alunos, depoimentos em vídeo placeholder, senso de escassez, tabela de comparação

---

### ESTILO 4 — CONEXÃO & CONFIANÇA
**Usar para:** relacionamento, desenvolvimento pessoal, coaching, espiritualidade
**Emoção:** pertencimento, esperança, conexão
**Paleta:**
```css
--bg: #fdfcfb;
--surface: #ffffff;
--border: #e8e0d8;
--text: #2d1b0e;
--muted: #8b7355;
--accent: #d97706;      /* âmbar acolhimento */
--cta: #b45309;
--soft: #fef3c7;        /* amarelo suave */
```
**Tipografia:** Playfair Display (headlines) + Lora (corpo)
**Características:** Foto do autor/produto em destaque, tom empático, depoimentos emocionais, garantia proeminente, sem pressão excessiva

---

### ESTILO 5 — AUTORIDADE TÉCNICA
**Usar para:** concursos, idiomas, estudos, tecnologia, certificações
**Emoção:** confiança, credibilidade, método
**Paleta:**
```css
--bg: #ffffff;
--surface: #f8f9fa;
--border: #dee2e6;
--text: #212529;
--muted: #6c757d;
--accent: #0d6efd;      /* azul institucional */
--cta: #198754;
--warning: #ffc107;
```
**Tipografia:** IBM Plex Sans (headlines) + Source Serif 4 (corpo)
**Características:** Estrutura clara de módulos, lista de conteúdo do produto, credenciais do autor, aprovação/reprovação como gatilho, depoimentos com resultado específico (aprovado em X)

---

## PASSO 3 — ESTRUTURA DA PÁGINA DE VENDAS

Independente do estilo, toda página de vendas segue esta estrutura:

```
1. HERO
   - Headline principal (acima da dobra)
   - Subheadline
   - CTA primário visível sem scroll
   - Imagem ou mockup do produto

2. PROBLEMA
   - 3 dores específicas do público
   - Linguagem espelho (fala como o público fala)

3. SOLUÇÃO
   - O que é o produto em 1 parágrafo
   - Como funciona (3 passos simples)

4. PROVA
   - 3 depoimentos com nome, foto e resultado específico
   - Número de alunos/usuários (se tiver)

5. OFERTA
   - O que inclui (lista com ✓)
   - Preço riscado + preço real
   - Economia destacada

6. GARANTIA
   - Prazo + condição clara
   - Ícone de cadeado ou escudo

7. CTA FINAL
   - Repete headline em versão curta
   - Botão CTA grande
   - Lembrete de garantia abaixo do botão

8. FOOTER MÍNIMO
   - Sem links de distração
   - Apenas termos e privacidade
```

---

## PASSO 4 — PADRÕES TÉCNICOS OBRIGATÓRIOS

### HTML
- `lang="pt-BR"` no html
- Meta tags completas: charset, viewport, og:title, og:description, og:image
- Google Fonts via `<link>` no head
- CSS antes do JS

### CSS
- Todas as cores como variáveis CSS no `:root`
- Mobile-first — escreve mobile primeiro
- CSS puro — sem Bootstrap ou Tailwind
- Transições: `transition: all 0.2s ease`
- CTA mínimo: `min-height: 56px; font-size: 18px`

### PERFORMANCE
- `loading="lazy"` em todas as imagens exceto hero
- `loading="eager"` no hero
- Sem JS desnecessário

### PLACEHOLDERS
- `<!-- SUBSTITUA: link do checkout -->`
- `<!-- SUBSTITUA: URL da imagem do produto -->`
- `<!-- SUBSTITUA: nome do depoimento -->`

---

## REGRAS DE UI/UX

- Nunca mais de 2 CTAs diferentes na mesma página
- Espaçamento generoso entre seções — mínimo 80px desktop, 48px mobile
- Nunca usar mais de 2 fontes
- Contraste mínimo texto/fundo: 4.5:1
- Formulários: máximo 3 campos visíveis de uma vez
- Mobile: botão CTA fixo no bottom em páginas longas
- Imagens: sempre com alt text descritivo

---

## CHECKLIST ANTES DE ENTREGAR

Antes de entregar o HTML, confirme:
- [ ] Estilo escolhido declarado explicitamente
- [ ] Paleta do estilo aplicada como variáveis CSS
- [ ] Hero com CTA acima da dobra no mobile
- [ ] Todos os placeholders marcados com comentário
- [ ] Mobile-first implementado
- [ ] Página abre sem erro no navegador
