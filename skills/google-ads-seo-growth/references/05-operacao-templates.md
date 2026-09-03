# Operação: checklists, nomenclatura, negativas e SOPs

Artefatos prontos para copiar. Adapte ao cliente antes de usar.

## Nomenclatura

Padrão sugerido (facilita filtro, relatório e automação):

```
Campanha:  [Tipo]_[Marca|NaoMarca]_[Serviço]_[Geo]_[Objetivo]
           SRCH_NaoMarca_Implante_Belem_Leads
           PMAX_Ecom_Geral_BR_Vendas
           DGEN_Topo_Clinica_Belem_Alcance

Grupo:     [Tema]_[Correspondência]
           implante-dentario_EXA
           implante-dentario_FRA

Anúncio:   RSA_[Tema]_[Variante]      → RSA_implante_v1
Asset:     [Tipo]_[Tema]              → SITELINK_precos
Conversão: [Nível]_[Ação]             → P_form-agendamento / S_clique-whatsapp
```

Regras: sem acento e sem espaço em nomes de campanha; `P_` = primária, `S_` = secundária;
data no formato `AAAA-MM` quando houver versão sazonal.

## Checklist de lançamento — campanha de Search (lead local)

### Antes de criar

- [ ] Ficha do negócio preenchida (oferta, ticket, margem, capacidade, tempo de resposta)
- [ ] Conta com fuso America/Sao_Paulo, moeda BRL, pagamento automático
- [ ] Verificação do anunciante iniciada
- [ ] GTM instalado e publicado; variáveis de clique/formulário ativadas
- [ ] Tags: remarketing (todas as páginas) + vinculador de conversões (todas) + conversão de lead
- [ ] Conversão primária definida e **testada com envio real**
- [ ] GA4 vinculado, com dono de cada evento decidido (sem contagem dupla)
- [ ] Landing page do serviço existe, abre rápido no celular, tem CTA e telefone/WhatsApp visíveis
- [ ] Pesquisa de palavras feita no Planejador com filtro de intenção e leitura da faixa de lance
- [ ] Lista de negativas iniciais montada
- [ ] Cenário de orçamento apresentado e aprovado

### Na criação

- [ ] Objetivo: Leads · Tipo: Pesquisa · sem meta pré-selecionada indevida
- [ ] Nome seguindo a nomenclatura
- [ ] **Desmarcar Parceiros de Pesquisa**
- [ ] **Desmarcar Rede de Display**
- [ ] Local: raio ou cidades reais de atendimento (confira o raio no mapa — 5 km em capital é
      muito mais do que parece)
- [ ] Presença × Presença e interesse decidido conscientemente
- [ ] Idioma: português
- [ ] Programação de anúncios só se o negócio realmente perde venda fora do horário
- [ ] Públicos em **observação**, incluindo seus dados/segmentos
- [ ] **AI Max DESLIGADO** (campanha e grupo) em conta nova
- [ ] Lance: Maximizar cliques **com limite de CPC** ou CPC manual
- [ ] Palavras em exata `[ ]` (e frase `" "` se necessário), sintaxe conferida
- [ ] URL final = página do serviço, não a home
- [ ] 4–6 títulos únicos com a palavra-chave no título 1 ou 2; 2+ descrições
- [ ] Asset de chamada com DDD + número
- [ ] 2–4 sitelinks reais com descrição preenchida
- [ ] Frases de destaque e snippets estruturados
- [ ] Imagens e logo quando fizer sentido
- [ ] Nome da empresa verificado
- [ ] Negativas aplicadas
- [ ] Orçamento diário ≥ 5–10 × CPC esperado

### Nas primeiras 72 horas

- [ ] Anúncios aprovados? Alguma reprovação por política?
- [ ] Está recebendo impressão? Se não: lance abaixo do estimado de primeira página?
- [ ] Ler o relatório de termos de pesquisa **todo dia**
- [ ] Verificar se a primeira conversão registrada é real (ligar para o lead)
- [ ] Conferir relatório de localização — o clique veio de onde deveria?
- [ ] Ajustar lance para o **lance estimado de topo de página**, não o de primeira página
- [ ] Remover palavras "baixo volume de pesquisa"
- [ ] Desativar recomendações automáticas de aplicação automática

## SOP semanal de otimização (ordem fixa, ~45–60 min por conta)

1. **Segurança** — reprovações, gasto anômalo, conversão zerada de repente, página fora do ar.
2. **Termos de pesquisa** — classificar cada termo relevante:
   `manter · promover · reescrever anúncio · negativar · investigar`.
3. **Negativas** — aplicar no nível certo (conta / campanha / grupo).
4. **Qualidade do lead** — perguntar ao cliente quais leads prestaram. Sem esse input, você
   está otimizando no escuro.
5. **Localização** — cliques fora da área? Ajustar raio ou presença.
6. **Dispositivo e horário** — desvio grande de CPL justifica ajuste.
7. **Anúncios e assets** — pausar variação claramente pior, adicionar nova hipótese. Uma por vez.
8. **Páginas de destino** — taxa de conversão por página; a pior recebe a próxima melhoria.
9. **Lances** — só se houver dado suficiente. Não mexa em campanha em aprendizado.
10. **Orçamento** — realocar para o que tem melhor custo por lead **qualificado**.
11. **Anotar** no log: o que mudou, por quê, o que espero, quando revisar.

Mensal: atraso de conversão, receita/margem, capacidade do cliente, incrementalidade,
próximos testes, revisão de negativas acumuladas.

## Listas de negativas iniciais (PT-BR)

Aplicar como **lista compartilhada de conta**, revisando o que faz sentido para o nicho.

**Gratuidade e baixa intenção**
```
gratis, grátis, gratuito, gratuita, de graca, de graça, barato, mais barato,
preco baixo, promocao gratis, amostra gratis, teste gratis, free
```

**Emprego e carreira**
```
emprego, vaga, vagas, salario, salário, quanto ganha, piso salarial, concurso,
estagio, estágio, trainee, curriculo, currículo, contratacao clt, trabalhe conosco
```

**Educação e DIY**
```
curso, cursos, aula, aulas, apostila, pdf, download, como fazer, passo a passo,
tutorial, faca voce mesmo, faça você mesmo, caseiro, receita, diy, artigo, wikipedia
```

**Fornecedor e revenda**
```
atacado, fornecedor, distribuidor, revenda, franquia, comprar equipamento,
maquina, máquina, insumo, peca, peça, loja de material
```

**Institucional e ruído**
```
significado, o que e, o que é, definicao, definição, historia, história,
imagens, fotos, memes, youtube, reclame aqui, telefone da, cnpj, horario de funcionamento
```

**Público-alvo errado (ajustar por nicho)**
```
sus, publico, público, convenio popular, plano de saude gratuito, prefeitura,
ongs, projeto social, doacao, doação
```

**Concorrentes** — liste os nomes dos concorrentes locais como negativas na campanha
não-marca, para não pagar caro por tráfego que já tem destino.

**Não negativar cegamente:** "preço", "quanto custa", "valor" costumam ter intenção comercial
real em serviço de ticket alto. Antes de bloquear, veja se converteram.

## Estrutura de conta padrão (serviço local)

```
CONTA
├── SRCH_Marca_[Negocio]_[Geo]_Leads          ← protege a marca, CPC baixo
├── SRCH_NaoMarca_[ServicoPrincipal]_[Geo]    ← núcleo do investimento
│   ├── servico-principal_EXA
│   └── servico-principal-perto-de-mim_EXA
├── SRCH_NaoMarca_[ServicoPremium]_[Geo]      ← separado por CPC/margem diferentes
├── SRCH_Emergencia_[Geo]                     ← se houver urgência (24h, hoje, agora)
├── PMAX_[Geo]                                ← só depois de conversão consolidada
└── RMKT_Display_[Geo]                        ← só com consentimento e volume
```

Regra: **serviço com CPC muito diferente merece campanha própria**, senão o caro come o
orçamento do barato. Ex.: "dentista perto de mim" a R$ 8 e "implante dentário" a R$ 25 não
convivem bem no mesmo orçamento.

## Plano de 90 dias (novo cliente)

**Dias 1–7 — fundação**
Acessos, ficha do negócio, GTM/GA4/conversões testadas, GBP auditado e corrigido, uma landing
page do serviço principal, pesquisa de palavras, negativas iniciais.

**Dias 8–14 — lançamento controlado**
1 campanha Search não-marca + 1 de marca. Exata, CPC limitado, orçamento suficiente para
5–10 cliques/dia. Leitura diária de termos.

**Dias 15–30 — calibragem**
Negativas maduras, lances no topo de página, 2ª variação de anúncio, segunda landing page,
primeiro relatório com funil real. Começar coleta de avaliações no GBP.

**Dias 31–60 — expansão controlada**
Adicionar frase onde a exata está limitando volume. Segundo serviço em campanha própria.
Trocar para Maximizar conversões se houver sinal confiável. Publicar as primeiras páginas de
serviço/localidade e 4–8 conteúdos.

**Dias 61–90 — consolidação e decisão**
Avaliar CPA por serviço, importar conversões offline se o ciclo for longo, testar PMax ou
AI Max **em piloto isolado** se as portas de entrada estiverem cumpridas. Relatório de
decisão: escalar, ajustar ou encerrar, contra o critério definido no dia 1.

Nada de PMax, AI Max, Display, Vídeo e remarketing no primeiro mês. Conta jovem precisa de
sinal limpo, não de sofisticação.

## Log de mudanças (formato mínimo)

```
Data | Conta | Onde | O que mudei | Mecanismo esperado | Revisar em | Resultado observado | Decisão
```

Sem log, três meses depois ninguém sabe por que a conta melhorou — e você não consegue repetir.

## Auditoria rápida de conta herdada (30 min)

1. Conversões: quantas primárias? Alguma é pageview? Alguma duplicada? Alguma zerada há 30 dias?
2. Termos de pesquisa dos últimos 30 dias: que % é claramente fora da oferta?
3. Negativas: existem? Em que nível?
4. Redes: Parceiros e Display ligados numa campanha de Search?
5. Local: presença × interesse; relatório de localização mostra cliques de fora?
6. Lance: estratégia compatível com o volume de conversão real?
7. Orçamento: campanhas limitadas por orçamento enquanto outras desperdiçam?
8. Anúncios: URL final é a home em todos os grupos?
9. Assets: chamada, sitelinks, nome verificado presentes?
10. AI Max / PMax ligados sem sinal de conversão?
11. Recomendações com aplicação automática ativadas?
12. Marca e não-marca misturadas (inflando o resultado aparente)?

Cada "sim" problemático vira um item do diagnóstico com estimativa de impacto e um conserto.
