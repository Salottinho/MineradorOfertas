# SKILL — BACKEND

> **OBRIGATÓRIO:** Leia o arquivo `briefing-ativo.md` antes de executar qualquer tarefa. Use os dados de plataforma, planos e funil do briefing para definir a estrutura de backend necessária.

## QUANDO USAR
Use esta skill sempre que precisar conectar banco de dados, autenticação, armazenamento de dados ou integrações com serviços externos.

## STACK PADRÃO
- **Banco de dados:** Supabase (PostgreSQL)
- **Autenticação:** Supabase Auth
- **Hospedagem:** Vercel
- **Pagamentos:** Stripe ou integração via webhook Hotmart/Kirvano

## SUPABASE — PADRÕES

### ESTRUTURA DE TABELAS
Sempre incluir em toda tabela:
```sql
id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
created_at timestamptz DEFAULT now(),
updated_at timestamptz DEFAULT now()
```

### RLS (Row Level Security)
- Sempre ativar RLS em todas as tabelas
- Nunca deixar tabela exposta sem política
- Padrão mínimo: usuário só acessa seus próprios dados

### NOMENCLATURA
- Tabelas: snake_case plural (`user_profiles`, `product_orders`)
- Colunas: snake_case (`created_at`, `user_id`)
- Funções: snake_case com verbo (`get_user_profile`, `update_order_status`)

### VARIÁVEIS DE AMBIENTE
Nunca expor no código:
```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
STRIPE_SECRET_KEY=
```
Sempre usar `.env` e adicionar ao `.gitignore`

## AUTENTICAÇÃO — FLUXO PADRÃO
1. Login com email/senha ou magic link
2. Sessão gerenciada pelo Supabase Auth
3. Token JWT verificado no lado do servidor
4. Refresh automático de sessão

## WEBHOOKS — INTEGRAÇÃO COM PLATAFORMAS BR
### Hotmart
- Endpoint: `/api/webhooks/hotmart`
- Verificar `hottok` no header
- Eventos: `PURCHASE_COMPLETE`, `PURCHASE_CANCELED`, `SUBSCRIPTION_CANCELLATION`

### Kirvano / Cakto
- Endpoint: `/api/webhooks/kirvano`
- Verificar assinatura no header
- Liberar acesso após `payment.approved`

## ESTRUTURA DE PROJETO VERCEL
```
/
├── api/
│   └── webhooks/
│       └── hotmart.js
├── public/
│   └── index.html
├── .env
├── .gitignore
└── vercel.json
```

## SEGURANÇA
- Nunca usar service_key no frontend
- Sempre validar dados no servidor antes de salvar
- Rate limiting em endpoints de pagamento
- Logs de erro sem expor dados sensíveis
