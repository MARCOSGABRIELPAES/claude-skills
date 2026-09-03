# Medição: conversões, GA4, GTM e qualidade de lead

Abrir depois do fluxo geral do `SKILL.md`. Validar detalhes voláteis na documentação oficial
listada em `06-fontes-2026.md` antes de mexer em conta ativa.

## Princípio

O sinal de conversão é o combustível de todo o resto — Smart Bidding, PMax, AI Max e até a
leitura de SEO. Sinal ruim não gera "resultado ruim": gera **escala do erro**. Por isso a
medição vem antes da campanha, sempre.

## Ordem de implantação

1. **Conta e faturamento** — fuso America/Sao_Paulo, moeda BRL, verificação do anunciante
   (o Google dá prazo; quando pedir documento com foto, enviar com os quatro cantos visíveis).
   Cartão com pagamento automático evita campanha parando por saldo.
2. **Google Tag / GTM no site** — instalar container no `<head>` e `<body>`. Em WordPress,
   plugin de header/footer resolve. Depois disso, nunca mais editar código do site para
   marketing: tudo pelo GTM.
3. **Variáveis do GTM** — ativar todas as variáveis embutidas de clique, formulário, vídeo e
   scroll antes de criar acionadores.
4. **Acionadores** — DOM pronto, cliques em link, envio de formulário. Parametrizar por
   `Page Path` + texto do botão para não contar formulário errado.
5. **Tags mínimas (3)**:
   - remarketing do Google Ads → todas as páginas (constrói públicos para depois);
   - vinculador de conversões (*conversion linker*) → todas as páginas (sem ele a conversão
     não persiste);
   - conversão de lead → acionador específico do formulário.
6. **Ações de conversão no Google Ads** — criar manualmente, desativar conversões otimizadas
   até entender o fluxo, contagem "uma" para lead, janela de clique 30–90 dias, atribuição
   definida conscientemente.
7. **GA4** — vincular. Decidir explicitamente quem é dono de cada evento: importar do GA4
   **ou** medir nativo no Ads. Importar os dois = contagem dupla.
8. **Teste real** — preencher o formulário, ligar para o número, clicar no WhatsApp, ver o
   lead no CRM, conferir GCLID/UTM, e confirmar que uma ação gera **uma** conversão.

## Taxonomia de conversões

| Nível | Exemplos | Uso |
|---|---|---|
| **Primária** | formulário qualificado, ligação atendida > 60–90s, agendamento confirmado, conversa de WhatsApp qualificada, venda/receita offline | otimização de lance |
| **Secundária** | pageview de obrigado genérico, clique em botão, início de formulário, sessão engajada, download | diagnóstico apenas |

Regra: **conversão primária deve ser escassa e valiosa.** Se qualquer clique vira "conversão",
o Smart Bidding vai comprar cliques.

Hierarquia de valor típica em serviço local: venda registrada > agendamento confirmado >
ligação longa > formulário > clique em WhatsApp > clique em telefone.

## Ligações

- **Chamadas dos anúncios** são criadas automaticamente quando há asset de chamada — conte
  ligação a partir de 60s (padrão) ou ajuste ao seu ciclo.
- **Ligações do site** exigem encaminhamento de chamada do Google ou ferramenta de call
  tracking (CallRail, WhatConverts). Não é obrigatório usar terceiro: GTM + número
  encaminhado resolve a maioria dos casos locais.
- Rastreie separadamente: ligação do anúncio, ligação do site, clique no botão de telefone.
  São três comportamentos e três taxas diferentes.

## WhatsApp (contexto Brasil)

O clique em WhatsApp é a conversão mais fácil de medir e a mais fácil de superestimar.
Recomendação:

- clique no botão = conversão **secundária**;
- conversa qualificada (respondeu, informou serviço, entrou no CRM) = **primária**, importada
  offline;
- use UTM no link `wa.me` e um identificador por página para saber de onde veio;
- se o cliente não registra as conversas, isso é um bloqueador de negócio, não de tecnologia —
  trate na proposta.

## Conversões offline e enhanced conversions

Para ciclo longo (implante, imóvel, jurídico, B2B), o painel do Ads sozinho mente por omissão.

1. Capture o **GCLID** no formulário (campo oculto) e leve para o CRM.
2. Marque no CRM o estágio real: lead → qualificado → oportunidade → venda → valor.
3. Importe de volta como conversão offline, com valor.
4. Só depois disso faça sentido otimizar por valor / tROAS.

*Enhanced conversions for leads* usa dado primário com hash. Antes de implementar, verificar
o estado atual da migração para Data Manager/API na documentação — este ponto mudou mais de
uma vez.

## Checagens que quase todo mundo pula

- [ ] A mesma ação gera **uma** conversão (não 2 pelo GA4 + nativo)?
- [ ] A janela de conversão cobre o ciclo real de decisão do negócio?
- [ ] Página de obrigado tem URL única e não é alcançável por outro caminho?
- [ ] Consentimento (Consent Mode) configurado antes de remarketing?
- [ ] Moeda, fuso e valor por conversão coerentes?
- [ ] Atraso de conversão medido? (não julgue campanha antes de 1–2 ciclos)
- [ ] Formulário anti-spam? Lead falso vira sinal falso.
- [ ] Existe uma lista de conversões primárias **por campanha**, e não só na conta?

## Relatório mínimo por período

Por campanha / serviço / geografia / dispositivo / termo:

`gasto · impressões · cliques · CTR · CPC · leads · leads qualificados · CVR · CPL ·
custo por lead qualificado · agendamentos · vendas · CAC · receita · margem · atraso médio`

E sempre: **o que foi alterado, por qual mecanismo esperado, qual foi o resultado observado,
qual a próxima decisão.** Relatório sem essa coluna é enfeite.

## Quando a medição está quebrada

Não otimize. Sequência:

1. Congele mudanças de lance/orçamento.
2. Corrija o rastreamento.
3. Rode 1–2 ciclos de conversão para gerar baseline limpo.
4. Só então retome otimização.

Comunicar isso ao cliente como decisão técnica consciente — e não como atraso — é parte do
trabalho.
