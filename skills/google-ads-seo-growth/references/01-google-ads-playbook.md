# Google Ads playbook

Estado verificado em 2026-08-15. Detalhes voláteis (interface, defaults, migrações) devem ser
reconferidos em `06-fontes-2026.md` antes de alterar conta ativa.

## Estratégia antes da interface

Escreva a frase-tarefa da conta:

> Para **[público]** que busca **[problema]**, gerar **[conversão valiosa]** por **[canal]**,
> com custo aceitável de **[limite]**, levando a **[oferta/página]** e medindo até **[venda]**.

Depois a economia:

- `CAC máximo ≈ margem bruta por venda × taxa de leads qualificados que viram venda`
- `CPL aceitável ≈ valor esperado do lead × margem de segurança`
- `vendas necessárias = custo fixo de mídia+serviço ÷ margem de contribuição por venda`

São ferramentas de planejamento, não prova. Confirme taxa de fechamento, margem, tempo de
resposta e capacidade **com o cliente**.

## Seleção de campanha

| Necessidade | Primeiro candidato | Porta de entrada antes de expandir |
|---|---|---|
| Capturar busca explícita por serviço/produto | Search | conversão real, página relevante, controle de consulta |
| Vender catálogo | Shopping ou PMax com Merchant Center | qualidade do feed, preço/disponibilidade, valor de compra |
| Escalar volume no inventário Google | Performance Max | conversões primárias reais, assets/feed completos, exclusões entendidas |
| Gerar demanda com criativo visual | Demand Gen / Vídeo | biblioteca criativa, hipótese de público, plano de conversão downstream |
| Reengajar visitantes/leads | Seus dados / remarketing | consentimento, tamanho do público, janelas, frequência, mensagem útil |
| Testar antes de gastar grande | Search pequena e controlada | regra de parada clara e medição |

**Não crie todos os tipos por padrão.** Uma Search bem feita com oferta real e medição limpa
vale mais que seis campanhas subfinanciadas.

## Estrutura de Search

1. Separe por objetivo ou oferta materialmente diferente: marca, serviço não-marca,
   especialidade de alto valor, emergência, localidade. Concorrente só com revisão legal.
2. Um grupo de anúncios = um tema coerente. Se um anúncio e uma página não conseguem responder
   o tema sem texto forçado, o grupo está errado.
3. Poucas campanhas fortes > dezenas de grupos minúsculos. Divida quando orçamento, geografia,
   margem, horário ou mensagem realmente diferirem.
4. **URL final alinhada ao serviço e à cidade.** Home genérica é fallback, não padrão.
   Quem busca "clareamento dental Belém" tem que cair na página de clareamento, não na home.
5. Desmarque **Parceiros de Pesquisa** e **Rede de Display** numa campanha de Search
   diagnóstica. Inventário extra esconde a intenção real.
6. Local = território que o negócio consegue atender.
7. **Presença × Presença e interesse**: presença apenas quando clique de fora custa caro
   (serviço local com atendimento físico). Presença e interesse quando faz sentido alguém
   pesquisar de outra cidade com interesse naquela (turismo, imóvel, mudança, cirurgia
   eletiva com deslocamento). Sempre confira o relatório de localização depois.
8. Públicos em **observação** primeiro; segmentação restrita só se o modelo exigir.
9. Agendamento de anúncios só se o negócio realmente perde venda fora do horário. Lembre que
   muita gente pesquisa à noite e decide no dia seguinte — restringir demais mata demanda.

## Palavras-chave e consultas

Fontes: linguagem do cliente, catálogo de serviços, Planejador de Palavras-Chave, Search
Console, CRM, gravações de ligação, busca interna do site, páginas de concorrentes.

Buckets:

- `core`: serviço + local / problema / urgência
- `comercial`: empresa, especialista, agência, orçamento, agendar, preço
- `informacional`: custo, comparação, como fazer, sintomas
- `ruído`: grátis, emprego, salário, curso, faça você mesmo, fornecedor, atacado
- `marca`: marca do cliente e variantes
- `concorrente`: teste separado, com revisão de política

### Método do Planejador (o que realmente extrai valor)

- Comece com 2 sementes amplas ("encanador", "encanamento"); o resto vem sozinho.
- Rode também com **a URL do site** — o Google devolve o que ele considera relevante para
  aquele domínio. Costuma bater com o Search Console.
- Filtre por volume mínimo (20–50/mês em mercado local; ajuste conforme a lista).
- Filtre por **texto contendo**: `serviço`, `perto de mim`, `empresa`, `contratar`,
  `orçamento`, `24 horas`, nome da cidade. Isso separa intenção de compra de curiosidade.
- **Leia a faixa de lance de topo de página.** Lance alto = anunciantes estão obtendo retorno.
  Lance baixo em termo popular = provavelmente converte mal. É o sinal mais subestimado da
  ferramenta.
- Termos com volume, faixa de lance e concorrência **idênticos** são o mesmo termo para o
  Google. Não some volumes; trate como um público só.
- Previsão (forecast) serve para cenário, não promessa. Use CVR conservadora (5% pessimista,
  10% base, 15–20% serviço local bem feito) e mostre a faixa.

### Tipos de correspondência

Correspondência é **controle**, não estratégia.

- Campanha nova de lead com pouco dado: exata (e frase) como hipótese controlada.
  Sintaxe importa — `[termo]` para exata, `"termo"` para frase.
- Ampla só com conversão confiável, negativas maduras, orçamento e Smart Bidding.
- **Exata não é literal.** O Google serve variantes próximas e mesma intenção — inclusive troca
  de verbo/sinônimo, não só flexão de palavra. Caso real: `[criação de sites]` e
  `[criação de site profissional]` casaram com buscas como "criar site", "criar um site", "site
  criar" — sem nenhum gatilho óbvio tipo "grátis" ou "como" envolvido — e trouxeram contato
  querendo aprender a fazer sozinho, não contratar. Sempre leia o relatório de termos de
  pesquisa **nos primeiros dias de toda campanha nova**, comparando cada termo real contra o
  público ideal definido na ficha do negócio, não só contra a lista de negativas existente.
- Palavras marcadas "baixo volume de pesquisa" podem ser removidas; não gastam, mas poluem.

### Negativas

Construa a partir da **fronteira do negócio**, não de lista genérica copiada. Níveis: conta,
campanha, grupo. Antes de negativar, verifique se a consulta está mesmo fora da oferta —
negativar palavra sem contexto bloqueia variações boas. **Antes de salvar, confira se a palavra
negativa não é substring de nenhuma palavra-chave positiva ativa** — negativa sempre vence
correspondência positiva, então negativar um termo genérico (ex.: "criar") pode matar de vez
uma keyword de intenção boa que contém esse termo (ex.: `[criar site para empresa belém]`).
Nesse caso, use negativa de frase mais específica em vez da palavra solta.

Rotina semanal de termos: `manter → promover → reescrever → negativar → investigar`.
Promova consulta convertedora para o tema certo **só se melhorar controle ou leitura** —
não crie duplicata só para engordar a lista.

Listas iniciais em PT-BR estão em `05-operacao-templates.md`.

## Lances e orçamento

| Situação | Estratégia razoável |
|---|---|
| Sem histórico confiável de conversão | Maximizar cliques **com CPC máximo definido**, ou CPC manual |
| Conversões reais acumulando | Maximizar conversões |
| Volume estável e economia conhecida | CPA desejado |
| E-commerce com receita real rastreada | Maximizar valor / ROAS desejado |
| Visibilidade de marca | Parcela de impressão — nunca como substituto de meta de venda |

Notas de campo:

- Ao usar Maximizar cliques, **sempre** defina limite de CPC. Sem limite, o Google acha
  cliques caros para gastar o orçamento.
- Um jeito prático de calibrar o limite: pegue a faixa de topo de página do Planejador,
  faça a média e coloque um pouco acima. Depois do lançamento, o próprio Ads informa o lance
  estimado de primeira página e de topo — mire no **topo**, não na primeira página: clique de
  topo costuma ter melhor qualidade.
- Não fique em manual para sempre porque um tutorial antigo mandou; e não force automação
  antes do evento significar algo.
- **AI Max e correspondência ampla completa não funcionam bem com CPC manual** — a
  documentação diz que CPC manual limita as capacidades, incluindo a correspondência de
  termos do AI Max. Escolha uma tese: ou lançamento manual controlado, ou pilha de IA. Não
  misture e depois culpe a ferramenta.

Orçamento:

1. Defina o teto mensal de risco primeiro.
2. Converta em orçamento diário médio. **O orçamento diário oscila para cima em dias de
   demanda e compensa ao longo do período** — não entre em pânico com um dia acima.
3. Financie cliques suficientes para aprender. Heurística útil para lead de serviço:
   orçamento diário ≥ 5 a 10 × CPC esperado. Abaixo disso a campanha não gera dado, só ruído.
4. Priorize a oferta com melhor economia marginal. Não espalhe verba pequena em todas as redes.
5. Registre mudanças de orçamento e espere o atraso de conversão antes de declarar vitória.

Sempre explique orçamento como cenário:

`orçamento → cliques ao CPC previsto → leads à CVR prevista → qualificados → vendas → margem`

Rotule cada número: observado / benchmark / previsão / premissa.

## Anúncios, assets e extensões

Por grupo, pelo menos **2 RSAs** relevantes quando a conta comportar.

| Asset | Função |
|---|---|
| Título 1/2 | consulta/serviço + promessa clara; fixe só por exigência legal ou de marca |
| Demais títulos | benefício, prova, mecanismo, diferencial, local, urgência, objeção |
| Descrições | oferta, qualificação, processo, confiança, CTA |
| Sitelinks | rotas reais: serviço, preço, prova, sobre, contato |
| Frases de destaque | diferenciais curtos, não repetição dos títulos |
| Snippets estruturados | listas factuais de serviços/categorias |
| Chamada, local, imagem, nome da empresa | quando elegível e relevante |

Notas de campo:

- A IA do Ads pontua "Eficácia do anúncio" pesando **quantidade**. Quantidade não é qualidade.
  4 a 6 títulos únicos e 2+ descrições já entregam bom resultado; não encha linguiça nem
  repita a mesma ideia em cinco variações.
- A palavra-chave (ou algo muito próximo) precisa aparecer no título.
- Para escrever bom anúncio sem inspiração: (a) liste as 2 maiores dores e as 2 maiores
  objeções do cliente; (b) pesquise o termo no Google e leia os anúncios dos concorrentes;
  (c) use IA para gerar 5 variações a partir da palavra-chave e edite — nunca cole cru.
- **Sitelinks só se houver link real que complementa** a promessa. Landing page única sem
  navegação? Não force. 2 a 4 sitelinks muito bons > 6 medíocres. O Google decide quando
  mostrar.
- Nome da empresa verificado deixa o anúncio visivelmente melhor. Complete a verificação.
- **Anúncios somente chamada** estão em descontinuação: criação removida em fev/2026, veiculação
  encerra em fev/2027. Substitua por RSA + asset de chamada.

## Índice de Qualidade e Ad Rank

QS é diagnóstico 1–10, não KPI. Três componentes:

- **CTR esperada** — a mensagem merece o clique nessa consulta?
- **Relevância do anúncio** — o anúncio responde ao tema da palavra?
- **Experiência na página de destino** — o destino corresponde, carrega, explica e converte?

Melhore o caminho do usuário primeiro. Anúncio mais restrito e de intenção alta pode ter CTR
menor e converter melhor. Ad Rank é calculado no leilão e inclui lance, qualidade e contexto —
não prometa que subir QS sozinho derruba CPC.

## AI Max para Search

Camada de otimização **dentro** de campanhas Search. Verificado em 2026-08-15.

**O que faz:** correspondência de termos (ampla + sem palavra-chave), personalização de texto
(gera cópia a partir do site, landing pages, anúncios e assets) e expansão de URL final.

**Controles:** locais de interesse (nível de grupo), configurações de marca (campanha e grupo),
inclusões/exclusões de URL, e desativação da correspondência por grupo.

**Requisitos e limites documentados:**

- não funciona bem em campanha **limitada por orçamento**;
- personalização de texto precisa estar ativa para a expansão de URL final funcionar;
- template de rastreamento precisa usar padrão compatível (`{lpurl}?`, `{lpurl}&`) ou gera 404;
- assets fixados são ignorados quando uma URL mais relevante é escolhida;
- expansão de URL só envia tráfego para URLs relevantes ao tema do grupo;
- CPC manual limita as capacidades, incluindo a correspondência de termos.

**Relatórios:** termos correspondidos via AI Max com atribuição de origem, coluna "AI Max" no
relatório de palavras-chave, coluna "Selecionado por" no relatório de páginas de destino,
desempenho de assets.

**Antes de ligar:**

1. Conversões primárias reais, deduplicadas e ligadas a resultado qualificado.
2. Folga de orçamento.
3. Site e landing pages auditados (o AI Max lê o seu conteúdo — conteúdo ruim vira anúncio ruim).
4. Locais permitidos, inclusões/exclusões de marca e de URL, restrições de texto definidas.
5. Baseline salvo: gasto, consultas, qualidade de conversão, CPA/valor, URLs de destino,
   parcela de impressão, atraso de conversão.
6. Piloto em campanha madura ou experimento isolado. Nunca em conta frágil.

**Quando segurar:** sem dado confiável de conversão, orçamento pequeno, ciclo longo sem
feedback offline, muitas páginas fracas, ou necessidade de controle estrito de consulta.

**Deriva de intenção é real.** Caso documentado: adestrador de cães ligou AI Max e passou a
receber consultas de banho e tosa e limpeza. Se ligar, leia os termos toda semana.

**Migração DSA → AI Max (verificado 2026-08-15):**

- criação de novas campanhas DSA encerra em **setembro/2026**;
- upgrade automático geral adiado para **fevereiro/2027**;
- exceção: campanhas com **assets criados automaticamente (ACA)** e **correspondência ampla
  em nível de campanha** sobem automaticamente já em **setembro/2026**;
- o Google divulga média de ~7% mais conversões/valor a CPA-ROAS similar com o pacote
  completo — número do próprio fornecedor, trate como referência, não como garantia.

Plano prático: agora → travar baseline e finalizar lista de negativas; próximos 60 dias →
2 a 3 pilotos isolados; depois → migrar antes do prazo, não em cima dele. AI Max leva ~4 a 6
semanas para estabilizar.

**AI Max não é campanha, é configuração.** Em conta nova, deixe **desligado** (inclusive no
nível do grupo) até entender. Ligar cedo traz público sujo e queima a confiança do cliente.

## Performance Max

Use quando o objetivo comporta automação multicanal **e** a conta consegue alimentar bons
inputs. Para geração de lead, a conversão primária precisa representar lead de verdade —
senão o sistema escala lixo com eficiência. Para e-commerce, arrume o feed antes de culpar o
lance.

**Portas de entrada:** conversão/valor primário correto e consentido · texto, imagem e vídeo
suficientes · sinais de público como orientação (não garantia de segmentação) · exclusões de
marca, controles de URL e exclusão de clientes revisados · sobreposição com Search entendida ·
baseline ou experimento planejado para qualquer migração.

**Controles disponíveis (verificado 2026-08-15 na documentação oficial):**
palavras-chave negativas em **nível de conta e de campanha** — aplicáveis apenas ao inventário
de Pesquisa e Shopping do PMax, com limite ampliado (na casa dos milhares por campanha);
exclusões de marca; insights de termos de pesquisa.

**Controles relatados por fontes secundárias, ainda não confirmados na documentação oficial**
(confirme na conta antes de prometer ao cliente): negativas em nível de grupo de recursos,
sitelinks em nível de campanha, rótulos de desempenho de assets, Customer Match ampliado,
relatório de distribuição por canal.

Revise: insights, termos, canais/posicionamentos, grupos de recursos, atraso de conversão.
PMax **não** é "configurar e esquecer" e não prova venda incremental só porque reporta conversão.

Em conta de serviço local pequena, PMax costuma canibalizar marca. Se for usar, exclua marca e
compare com período anterior.

## Shopping, Display, Vídeo/Demand Gen e remarketing

**Shopping.** Estrutura do feed segue a economia do produto. Separe só quando margem,
disponibilidade, sazonalidade ou orçamento justificarem. Cheque reprovações, identificadores,
títulos, atributos, imagens, preço e consistência com a página. Meça valor de compra.

**Display.** Alcance, consideração ou remarketing, com público e hipótese criativa claros.
Exclua posicionamentos ruins, defina expectativa de frequência, e não julgue Display com
benchmark de CTR de Search. Campanhas de Display vêm sendo migradas para Demand Gen — confirme
o estado atual antes de recomendar.

**Vídeo / Demand Gen.** Primeiros segundos fortes, uma mensagem, um CTA, prova, destino que
funciona no celular. Defina se o objetivo é atenção, tráfego qualificado ou conversão. Campanhas
de ação em vídeo migraram para Demand Gen — tutoriais antigos estão desatualizados. Novidades
de 2026: parcerias com criadores do YouTube, inventário do Google Maps, distribuição dinâmica
de vídeo de produto e configuração assistida por IA.

**Remarketing / "seus dados".** Só com consentimento adequado. Janelas por comportamento:
todos os visitantes, visitantes de página de serviço, quem iniciou formulário, carrinho
abandonado, clientes atuais, e **exclusão de convertidos**. Adeque a mensagem ao estágio.
Saúde é categoria sensível — verifique a política de publicidade personalizada antes de usar
remarketing ou lista de clientes em nicho clínico.

## Busca conversacional e anúncios em superfícies de IA

Contexto verificado em 2026: anúncios são elegíveis a aparecer acima, abaixo e **dentro** de
AI Overviews (Search, Shopping e PMax), sem opção de segmentar apenas essa posição nem de
optar por sair. O AI Mode já opera no Brasil e o volume de busca conversacional cresce.

Consequências práticas:

- Volume de palavra-chave individual tende a cair sem que a demanda caia — a busca se espalha
  em frases longas e conversas. Não conclua "o mercado morreu" a partir do Planejador.
- Correspondência ampla bem controlada e AI Max ganham peso relativo, mas **exigem** sinal de
  conversão confiável. Isso torna a medição ainda mais decisiva, não menos.
- O conteúdo do site vira insumo direto do anúncio (personalização de texto e expansão de URL).
  Site pobre = anúncio pobre. SEO e Ads deixaram de ser departamentos separados.

Anúncios em formatos conversacionais (Conversational Discovery, Highlighted Answers, Business
Agent for Leads) e ferramentas como Ask Advisor e Asset Studio foram anunciados no Google
Marketing Live 2026 (20/05/2026). Confirme disponibilidade no Brasil antes de prometer ao
cliente.

## Erros comuns

- lançar antes de testar conversão;
- tratar CPC baixo ou CTR alto como receita;
- misturar serviços não relacionados no mesmo grupo;
- mandar toda intenção para uma página genérica;
- deixar "presença e interesse" ligado em serviço local sem conferir;
- ampla / expansão por IA sem feedback de conversão qualificada;
- ligar AI Max ou PMax em dado fraco e culpar a IA;
- importar o mesmo evento GA4/Ads duas vezes;
- contar pageview ou início de formulário como lead primário;
- mudar orçamento, lance, local, palavras e página ao mesmo tempo;
- aceitar recomendação automática do Google sem checagem de negócio (elas otimizam o gasto,
  não a sua margem);
- prometer resultado com CPC ou case de tutorial;
- ignorar tempo de resposta comercial do cliente;
- esquecer de excluir clientes atuais, funcionários e candidatos a emprego.

## Contas grandes

Nomenclatura, rótulos, histórico de alterações, taxonomia de conversões, listas negativas
compartilhadas, scripts/regras com salvaguardas, donos de orçamento, experimentos e notas de
rollback. Visão de portfólio preservando a economia por serviço. Segmente por margem e
resultado qualificado, não só por canal. Audite acesso, faturamento, política e frescor dos
dados. Escale em incrementos medidos e avalie 1–2 ciclos de conversão após mudança grande,
salvo problema de segurança. Google Ads Editor para construções em massa.
