# Ler o conjunto antes de modelar

Estes são os erros que aparecem quando se começa a modelar cedo demais. Cada um
já custou uma reconstrução inteira.

## 1. A ordem dos pavimentos não é a que você supõe
Garagem não significa subsolo. Um empreendimento pode ter térreo no nível da rua e
os **pilotis de estacionamento acima dele**, com o lazer no topo do embasamento.

Como decidir, em ordem de confiabilidade:
1. **Corte**, se existir — resolve tudo, inclusive as cotas.
2. **Numeração das pranchas** — normalmente sobe junto com o pavimento.
3. **Conteúdo do desenho** — o pavimento no nível da rua é o único com meio-fio,
   faixa de pedestre, calçada e carros chegando da via. Os de cima têm o entorno
   em branco.

## 2. Pavimento inferior esmaecido não é laje
As implantações desenham os níveis de baixo por transparência, para dar contexto.
Modelar isso cria laje onde o projeto tem céu aberto. `scripts/lajes.py` resolve
com o teste da fração de pixel escuro — mas entenda o que ele faz antes de confiar.

## 3. Conte núcleos para contar torres
Um núcleo de circulação (escada + bateria de elevadores) atende uma torre. Se a
planta do último pavimento do embasamento tem dois núcleos, são duas torres.
Isso é mais confiável do que contar volumes numa perspectiva, onde um volume
recuado se esconde atrás do da frente.

## 4. Verifique se as pranchas compartilham o enquadramento
Se todas têm a mesma dimensão em pixels e a mesma moldura, estão registradas entre
si: um único sistema de coordenadas serve para todas, e qualquer elemento medido
numa vale nas outras. Confirme comparando um ponto fixo (esquina do lote, seta do
norte) em duas pranchas.

## 5. O desenho pode estar levemente girado
Meça a borda superior da laje em dois pontos distantes. Uma inclinação de meio grau
é comum e some no modelo se você não compensar — mas gera erro de meio metro nas
pontas de um lote de 150 m. Registre em `rotacao_graus`.

## 6. Escala: ancore no que é normativo
Ordem de preferência para o elemento de referência:
1. **Cota escrita ou barra de escala** na prancha — se existir, acabou.
2. **Vaga de garagem** — dimensão exigida por código, desenhada dezenas de vezes,
   e o passo repetido permite medir por FFT com precisão sub-pixel. No Brasil,
   2,50 × 5,00 m é o mais comum; 2,40 × 4,80 também aparece.
3. **Degrau** (piso 0,28–0,30 m), **porta** (0,80 / 0,90 m), **corredor de garagem**
   (6,0–7,0 m).

Nunca ancore em quadra esportiva ou piscina de condomínio: raramente são
regulamentares. Servem como **conferência**, não como âncora — se a quadra der
15,4 × 7,6 m contra 16 × 8 oficial, tudo bem; se der 12 × 9, a escala está errada.

**Sempre feche com duas referências independentes.** Uma medida sozinha não tem
como estar errada de forma detectável.

## 7. Paredes vem em duas linguagens graficas

**Linha fina**: parede desenhada como contorno escuro sobre fundo qualquer -
tipico de implantacao. Detecta-se por *bottom-hat*, e o que sobra alongado e
parede, o compacto e mobiliario.

**Poche solido**: parede preenchida de preto - tipico de planta de apartamento.
Aqui a rede inteira de paredes e **um unico componente conectado**, entao o
filtro de alongamento a classificaria como mobiliario. Use limiar de escuro
direto (`parede_modo: "poche"` no `projeto.json`).

Para escolher sem adivinhar: meca a fracao de pixel bem escuro (V<0.22) dentro
da laje. Acima de ~3% e poche; linha fina raramente passa de 1%. De quebra, as
espessuras que sairem servem de conferencia da escala - devem cair em valores
construtivos (0,10-0,15 m de alvenaria interna, 0,20-0,30 m de estrutural).

## 8. Contar pavimentos: procure a elevacao ortografica

Renders de fachada costumam ser perspectiva, onde os pavimentos comprimem para
cima e a contagem por FFT falha. Mas alguns sao **elevacao ortografica**, e
nesses a contagem e exata.

Como saber qual e qual sem confiar no olho: meca o periodo das lajes de varanda
no terco superior, medio e inferior. Se os tres baterem dentro de ~1%, e
ortografica. Se crescerem para baixo, e perspectiva - nesse caso nao conte por
FFT.

Numa elevacao ortografica, o **perfil do topo da silhueta** (menor y ocupado por
coluna) entrega de graca o desnivel entre volumes, em pavimentos. Segmente o ceu
por variancia local, nao por cor: ceu de por do sol muda de azul para laranja e
quebra qualquer regra de matiz.

**O que a elevacao NAO entrega** e a altura de pavimento em metros. Para isso e
preciso uma dimensao conhecida na mesma projecao, e a largura da silhueta nao
serve quando os volumes se sobrepoem na vista. Sem corte, declare a premissa e
siga - nao invente uma conta que parece medicao.

## 9. Peca os arquivos originais
Imagem colada no chat não dá para medir. Quando o pedido é fidelidade, peça o
arquivo em disco antes de começar — é mais rápido pedir e esperar do que modelar
por estimativa e refazer. Vale para planta de implantação, pavimento tipo, corte
e fachada.
