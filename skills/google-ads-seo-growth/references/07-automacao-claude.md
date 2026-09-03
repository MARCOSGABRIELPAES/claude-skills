# Camada de automação: operar Google Ads e SEO com Claude

**Snapshot: 2026-08-16, America/Sao_Paulo.**
Este arquivo trata de **como executar** o que os outros arquivos mandam fazer. Ele não substitui
estratégia. Automatizar a execução de uma estratégia errada só faz você errar mais rápido e
mais barato — o que na prática significa errar mais caro.

Regra que atravessa o arquivo inteiro: **Claude opera a conta, não decide o negócio.**
A ficha do negócio (SKILL.md §1) e o plano de medição ([00-medicao.md](00-medicao.md))
continuam sendo trabalho humano antes de qualquer script rodar.

---

## 1. Os três níveis de conexão

Escolha o nível pelo risco que a tarefa carrega, não pela vontade de automatizar.

| Nível | O que é | Pode escrever na conta? | Quando usar |
|---|---|---|---|
| **N1 — Leitura oficial** | MCP oficial do Google Ads (`googleads/google-ads-mcp`) | Não | Auditoria, diagnóstico, relatório, mineração de termos, dashboard. **Padrão para conta de cliente.** |
| **N2 — Escrita via API própria** | Scripts Python/Node com a biblioteca do Google Ads API, rodados por Claude Code | Sim | Operações em massa (RSA, negativas, grupos SKAG/STAG) com revisão humana antes do envio |
| **N3 — MCP de terceiro com mutação** | Servidores comunitários que expõem `mutate` | Sim | Só em conta própria ou de teste. Em conta de cliente, exige contrato e aprovação explícita |

### N1 — MCP oficial (verificado em 2026-08-16 no repositório)

- Repositório: `github.com/googleads/google-ads-mcp`
- Instalação: `pipx run --spec git+https://github.com/googleads/google-ads-mcp.git google-ads-mcp`
- Ferramentas expostas: **três**, todas de leitura —
  `list_accessible_customers`, `search` (consulta GAQL), `get_resource_metadata`
- Variáveis: `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_PROJECT_ID`,
  `GOOGLE_APPLICATION_CREDENTIALS` (ou `GOOGLE_ADS_MCP_OAUTH_CLIENT_ID` +
  `GOOGLE_ADS_MCP_OAUTH_CLIENT_SECRET`), `GOOGLE_ADS_LOGIN_CUSTOMER_ID` (opcional, conta de
  administrador)
- Aviso do próprio repositório: **o servidor expõe seus dados ao modelo conectado**. Trate
  como decisão de privacidade, não como detalhe técnico.

*Fonte secundária, não confirmada na documentação:* lançamento em 28/04/2026. Irrelevante para
a operação — o que importa é o comportamento verificado acima.

**Consequência prática que muda o desenho do trabalho:** como o MCP oficial não escreve,
qualquer fluxo de "Claude cria a campanha sozinho" depende de N2 ou N3. Um tutorial que mostra
Claude criando campanhas está usando código próprio ou servidor de terceiro — não a integração
oficial. Diga isso ao cliente antes de prometer.

### Pré-requisitos que travam o projeto se ignorados

| Item | Detalhe | Risco se esquecer |
|---|---|---|
| Conta de administrador (MCC) | vincular a conta do cliente e aprovar o convite por e-mail | sem isso não há `login_customer_id` |
| Token de desenvolvedor | pedido no API Center da conta de administrador | níveis de acesso limitam volume e alcance |
| Nível de acesso do token | teste → limitado a contas de teste; níveis superiores exigem aprovação do Google | descobrir isso no dia da entrega |
| Projeto no Google Cloud | API do Google Ads habilitada + tela de consentimento OAuth + usuário de teste + credencial de aplicativo para computador | fluxo de login falha silenciosamente |
| Segredos | `.env` fora do versionamento, `credentials.json` fora do repositório | vazamento de acesso a conta com cartão vinculado |

O tutorial que originou esta seção cita "2.880 requisições por dia" no token inicial.
**Trate como número de tutorial**, não como limite contratual — confira no API Center da conta
antes de dimensionar qualquer rotina diária.

---

## 2. Regras de segurança da automação

Não negociáveis. Uma conta de cliente tem cartão de crédito ligado nela.

1. **Leitura por padrão.** Escrita só depois que o diagnóstico foi lido e aprovado por humano.
2. **Humano no circuito (HITL).** Claude propõe o diff; a pessoa aprova; só então executa.
   Vale especialmente para: pausar campanha, mexer em orçamento, mudar estratégia de lance,
   aplicar negativa em massa, alterar URL final.
3. **Simulação antes do envio.** Toda operação em massa gera primeiro um CSV/relatório do que
   *seria* feito. Compare a contagem esperada com a real.
4. **Baseline salvo.** Antes de mexer em campanha madura, exporte o estado atual
   (`05-operacao-templates.md` §Log de mudanças). Sem baseline não existe reversão nem leitura
   de impacto.
5. **Uma variável relevante por vez.** Automação não revoga a regra 12 da SKILL.md — ela
   aumenta a tentação de quebrá-la.
6. **Escopo travado.** O script recebe `customer_id` e `campaign_id` explícitos. Nunca
   "aplique em todas as contas acessíveis".
7. **Limite de gasto como guarda-corpo.** Se a automação puder mexer em orçamento, defina teto
   diário e alerta de anomalia antes de ligar.
8. **Log de mudanças automático.** Data, o que mudou, por quê, quem aprovou, como reverter.
   Isso é o que salva a relação com o cliente quando o número cai.
9. **LGPD.** Dado de lead (nome, telefone, e-mail) só sai do CRM com base legal. Upload de
   conversão offline usa dado com consentimento e, quando aplicável, formato com hash.
10. **Nada de credencial em prompt.** Segredo vive em variável de ambiente, não no chat.

---

## 3. Pipeline: o que vale automatizar, em ordem

Ordem intencional — cada etapa depende da anterior. Pular medição para chegar mais rápido em
"gerar 200 anúncios" é o erro clássico.

| # | Etapa | Nível | O que Claude faz bem | O que continua humano |
|---|---|---|---|---|
| 1 | Ficha do negócio | — | estruturar o que foi coletado | coletar, validar ticket/margem/capacidade |
| 2 | Plano de medição | N1 | escrever o mapa de eventos, gerar o GTM, checar disparo | decidir o que é lead qualificado |
| 3 | Pesquisa de palavras | N1 | classificar intenção, agrupar temas, gerar matriz | rodar o Planejador (volume real é dado, não palpite) |
| 4 | Arquitetura de conta | N1 | propor estrutura, nomenclatura, negativas | aprovar separação por intenção/oferta/geografia |
| 5 | Criação de campanha/grupo | N2 | executar em massa a estrutura aprovada | aprovar antes do envio |
| 6 | RSA em volume | N2 | 15 títulos + 4 descrições + extensões por grupo | revisar promessa, conformidade e fixação |
| 7 | Landing pages | — | gerar página por tema, com correspondência de mensagem | julgar oferta, prova social, conformidade |
| 8 | Tag, conversão, público | N1+N2 | instalar, testar, diagnosticar o Tag Assistant | confirmar que o lead chegou no CRM |
| 9 | Painel e leitura | N1 | consulta GAQL, painel, relatório semanal | decidir pausar/escalar |
| 10 | Mineração de negativas | N1→N2 | achar termos que gastam sem converter, pesquisar o que o termo significa | aprovar a lista antes de aplicar |
| 11 | Conversões offline | N2 | montar o CSV a partir do CRM por GCLID | garantir base legal e integridade do dado |

### Onde está o ganho real

Não é "escrever anúncio mais rápido". É:

- **Etapa 10** — mineração de termos com pesquisa ativa do significado de cada termo. Um termo
  aparentemente comercial pode ser vaga de emprego, cidade fora da área ou curso. Achar isso à
  mão em conta grande é inviável; achar em minutos muda o CPA.
- **Etapa 11** — fechar o laço receita→plataforma. É o que transforma "conversões" em ROAS real
  e o que permite lance por valor. Ver [00-medicao.md](00-medicao.md).
- **Etapa 9** — leitura semanal consistente. A maioria das contas não morre de configuração
  ruim, morre de ninguém olhar toda semana.

---

## 4. Empacotar como skill (o que vira comando)

Depois que o fluxo funcionou duas vezes à mão, vire skill. Candidatos, em ordem de retorno:

| Comando | Entrada | Saída | Nível |
|---|---|---|---|
| `/auditar-conta` | `customer_id`, janela | diagnóstico por camada + top 10 ações priorizadas por impacto financeiro | N1 |
| `/minerar-negativas` | `customer_id`, janela, gasto mínimo | tabela termo · gasto · conversões · motivo · veredito, para aprovação | N1 |
| `/relatorio-semanal` | `customer_id` | SOP semanal de `05-operacao-templates.md` preenchido com dado real | N1 |
| `/gerar-rsa` | tema, oferta, URL, restrições | 15 títulos + 4 descrições + extensões, com títulos fixados | N2 |
| `/estrutura-campanha` | matriz intenção→tema aprovada | campanhas/grupos/palavras/negativas em CSV para revisão | N2 |
| `/checar-medicao` | domínio | disparo de eventos, duplicação, conversão primária, destino quebrado | N1 |
| `/seo-oportunidades` | domínio | páginas com impressão alta e CTR baixo, canibalização, lacunas | N1 |

Cada skill precisa carregar o **contexto do cliente** (oferta, área atendida, tom, proibições
do setor) em arquivo próprio, senão você recria o problema do anúncio genérico.

---

## 5. Avaliação crítica do material de referência

Base: masterclass de Jono Catliff, *Claude Code Google Ads: Automate Everything ($730K Earned)*
(YouTube, jun/2026, ~1h08). O criador relata US$730 mil gerados e ~20% de conversão em negócio
próprio de serviço local (DJ/foto/vídeo, Canadá) que ele vendeu. **Números do criador, sobre a
conta dele, sem auditoria** — não são benchmark, não são promessa, e o modelo de negócio dele
não é o do seu cliente. O vídeo também vende comunidade paga e consultoria, e usa links
afiliados: separe método de oferta comercial.

| Afirmação do vídeo | Avaliação | Como aplicar aqui |
|---|---|---|
| Ignorar pontuação de otimização e recomendações automáticas | **Concordo em parte.** A crítica é legítima e já está na SKILL.md, mas "ignorar tudo" é preguiça: algumas recomendações apontam medição quebrada e destino inválido | Ler, filtrar, aplicar só o que passa pelo critério de negócio. Desligar aplicação automática |
| Lucro é a única métrica que importa | **Concordo.** É exatamente a espinha da skill | Sem mudança. Reforça `00-medicao.md` |
| Correspondência de **frase** é a vencedora; evitar ampla | **Datado / contexto-dependente.** Vale como ponto de partida em conta nova e orçamento curto. Em 2026 a documentação já trata ampla + lance inteligente + AI Max como caminho para volume, e variantes próximas borraram as fronteiras | Frase como partida controlada; testar ampla só com conversão confiável e negativas fortes. Ver `01-google-ads-playbook.md` |
| **SKAG** (um termo por grupo) como "estratégia dos US$700 mil" | **Parcialmente superado.** Com RSA obrigatório e variantes próximas, SKAG fragmenta dado e atrasa aprendizado. O que sobrevive — e é o valor real da ideia — é a **correspondência de mensagem**: busca → anúncio → página → e-mail → atendimento | Adotar **STAG** (grupo por tema apertado) como padrão; SKAG só para termo de alto valor e volume suficiente. Ver debate em §7 |
| Matriz cidade × serviço, uma página por município | **Concordo com trava.** Só quando o serviço é realmente prestado naquela cidade e a página tem conteúdo próprio | Sem isso vira página de porta de entrada — violação de política e risco de SEO. Ver `02-seo-e-local.md` |
| Presença, não interesse, na segmentação por local | **Concordo. Um dos pontos mais valiosos do vídeo.** O padrão do Google desperdiça verba com quem só tem interesse na região | Já está no checklist de lançamento. Reforçar |
| Excluir o resto do mundo nas localizações | **Aceito como higiene.** O relato de cliques via VPN/robô é plausível e o custo de excluir é baixo | Aplicar como padrão em serviço local no Brasil |
| Fugir de PMax, Display, Demand Gen e Vídeo ("é lixo") | **Discordo da generalização.** É a experiência dele em serviço local; virou regra universal indevidamente. A skill decide canal por papel no funil, não por moda nem por trauma | Search primeiro para captar demanda existente; PMax exige sinal de conversão confiável; remarketing tem papel próprio. Regra 6 da SKILL.md |
| Fixar o termo-raiz no primeiro título do RSA | **Concordo.** Impede combinação que não responde à busca | Incorporar ao `/gerar-rsa`: título 1 fixado com o tema, restante rotativo |
| Maximizar extensões para ocupar espaço na página | **Concordo, com ressalva.** Ganho de área é real; extensão irrelevante gera clique ruim | Sitelink só se complementar a oferta — já é regra em `01-google-ads-playbook.md` |
| Lista universal de negativas + mineração contínua de termos | **Concordo integralmente. Melhor parte do vídeo.** | Lista PT-BR já existe em `05-operacao-templates.md`. Automatizar via `/minerar-negativas` |
| Ligar para o lead em até 60 segundos (média de mercado citada: 48h) | **Concordo com a direção.** O múltiplo citado é referência de mercado, não medição dele | Entra no diagnóstico "lead qualificado sem venda". É frequentemente a maior alavanca — e não custa mídia |
| Testes A/B de página e depoimento em vídeo como maior alavanca | **Concordo** | `04-precificacao-propostas.md` (escopo) e `02-seo-e-local.md` (prova social) |
| Gerar centenas de anúncios porque é barato | **Cuidado.** Volume de variante sem volume de busca não gera aprendizado; gera ruído e diluição | Dimensionar número de variantes ao tráfego disponível. O próprio vídeo reconhece isso de passagem — mantenha a ressalva em primeiro plano |
| Pipeline de ROAS real: parâmetro de URL → campo oculto no formulário → CRM → painel → upload para o Google | **Concordo. Tecnicamente o trecho mais importante.** | Já coberto em `00-medicao.md`; usar o vídeo como confirmação de sequência, não como fonte |
| Publicar site em Next.js via GitHub + Vercel | **Neutro.** Escolha de pilha, não de marketing | Válido. Em cliente com site existente, integrar em vez de recriar — trocar de pilha por conta da campanha é escopo escondido |
| Empacotar o fluxo como skill de comando | **Concordo.** É o ganho composto real | §4 acima |

### O que o vídeo não cobre e você precisa cobrir

- Conformidade setorial (saúde, jurídico, financeiro) — no Brasil isso pausa conta.
- LGPD e consentimento para remarketing e upload de dado de cliente.
- Qualidade de lead versus quantidade: o vídeo mede conversão de formulário, não venda fechada,
  na maior parte do fluxo.
- Contexto brasileiro: WhatsApp como destino dominante de lead local, CPCs e sazonalidade
  locais, comportamento de busca em português.
- O que fazer quando a automação erra: reversão, comunicação com cliente, responsabilidade.

---

## 6. A mesma camada aplicada a SEO

O padrão se repete: conectar fonte de verdade por leitura, deixar a decisão com humano,
automatizar a parte repetitiva.

| Fonte | Estado em 2026-08-16 | Uso |
|---|---|---|
| **GA4** | servidor MCP oficial do Google existe (`google-analytics/google-analytics-mcp`) | comportamento, funil, receita por origem |
| **Search Console** | **sem servidor oficial**; opções da comunidade (ex.: `AminForou/mcp-gsc`) | consulta, página, impressão, CTR, indexação, inspeção de URL |
| **Ferramenta de SEO paga** | conectores próprios quando o cliente já paga | backlink, lacuna de conteúdo, concorrente |
| **Navegador** | automação de navegador | renderizar como o buscador vê, checar Core Web Vitals na prática |

*Servidor da comunidade não é servidor oficial:* audite o código, prefira leitura, e não
conecte conta de cliente a servidor não auditado.

### Consultas que rendem

- Páginas com **impressão alta e CTR baixo** → problema de título/descrição, não de conteúdo.
- Páginas com **CTR bom e conversão zero** → problema de oferta ou de correspondência de intenção.
- **Canibalização**: duas URLs disputando a mesma consulta.
- **Queda por consulta** após update, separando o que caiu do que só mudou de sazonalidade.
- Cruzamento GSC × GA4: da consulta até a receita.

### SEO programático — a linha que não se atravessa

Gerar centenas de páginas por template é tecnicamente trivial com Claude e é exatamente por
isso que é perigoso. A pergunta não é "consigo gerar?", é **"esta página existiria se não
fosse pela ferramenta?"**. Página de serviço × cidade só se presta o serviço lá, com prova
local, endereço de atuação e conteúdo que não seja o mesmo texto com a cidade trocada. Caso
contrário é porta de entrada — e a política do Google trata como spam.

Ver [02-seo-e-local.md](02-seo-e-local.md). A orientação oficial permanece: **não existe
arquivo especial nem schema exclusivo para busca com IA**; fundamentos decidem.

---

## 7. O que não automatizar

- **Decidir se o cliente deve anunciar.** Às vezes a resposta é "arruma o atendimento primeiro".
- **Escrever a promessa da oferta.** Claude ajuda a redigir; quem responde por ela é você.
- **Aprovar gasto.** Nenhuma automação sobe orçamento sozinha.
- **Julgar qualidade de lead.** Precisa de quem atende o telefone.
- **Falar com o cliente sobre resultado ruim.** Relatório automático não substitui conversa.
- **Conformidade.** Regra de setor muda e o modelo não sabe que mudou.

---

## 8. Checklist de implantação (uma vez por conta)

**Conexão**
- [ ] Conta de administrador criada e vinculada; convite aprovado
- [ ] Token de desenvolvedor obtido; nível de acesso confirmado e anotado
- [ ] Projeto no Cloud com a API habilitada, consentimento OAuth e usuário de teste
- [ ] Credencial de aplicativo para computador baixada e guardada fora do repositório
- [ ] `.env` no `.gitignore`; nenhum segredo em prompt ou em arquivo versionado
- [ ] MCP de leitura respondendo `list_accessible_customers` com a conta certa

**Governança**
- [ ] Escopo escrito: o que a automação pode e não pode tocar
- [ ] Aprovação humana definida para pausar, orçamento, lance, negativa em massa, URL final
- [ ] Baseline exportado
- [ ] Log de mudanças criado
- [ ] Teto de gasto e alerta de anomalia configurados
- [ ] Autorização do cliente registrada — inclusive para expor dados da conta ao modelo

**Contexto**
- [ ] Ficha do negócio no repositório do projeto
- [ ] Plano de medição validado com evento disparando e lead chegando no CRM
- [ ] Lista de negativas PT-BR aplicada
- [ ] Proibições do setor documentadas

**Só então**
- [ ] Primeira operação de escrita, pequena, reversível, com resultado conferido na interface

---

## 9. Fontes desta seção

| Fonte | Tipo | Verificado |
|---|---|---|
| `github.com/googleads/google-ads-mcp` — ferramentas, instalação, variáveis, aviso de exposição de dados | oficial (repositório) | 2026-08-16 |
| Jono Catliff, *Claude Code Google Ads: Automate Everything ($730K Earned)*, YouTube, jun/2026 | tutorial · resultado autorrelatado · com oferta comercial | 2026-08-16 |
| Servidor MCP oficial de GA4; ausência de servidor oficial de Search Console | secundária | 2026-08-16 — **reverificar** |
| Debate SKAG × STAG em 2026 | secundária, múltiplas fontes convergentes | 2026-08-16 |
| Data de lançamento do MCP oficial (28/04/2026); limite de 2.880 requisições/dia | secundária / tutorial | **não confirmado** |

**Reverificar antes de prometer a cliente:** níveis de acesso do token e limites de requisição,
existência de servidor oficial de Search Console, e se o MCP oficial do Google Ads passou a
permitir escrita.
