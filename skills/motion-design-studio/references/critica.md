# Loop de crítica

Aja como um diretor de motion exigente, não como um autor orgulhoso. Rode nos stills antes do render
completo e de novo no final. Abra cada imagem e olhe de verdade.

## Ferramentas de olhar (ffmpeg puro)
```bash
# folha de contato dos stills
ffmpeg -y -pattern_type glob -i 'out/stills/still-*.png' -vf "scale=270:480,tile=5x2" out/contato.png
# filme inteiro, 1,25 quadro/s
ffmpeg -y -i out/video.mp4 -vf "fps=1.25,scale=216:384,tile=5x2" -frames:v 1 out/folha.png
# tira de 12 quadros em volta de um corte (ex.: corte em 2,0 s, rascunho a 30 fps)
ffmpeg -y -ss 1.8 -t 0.4 -i out/rascunho.mp4 -vf "scale=180:320,tile=12x1" -frames:v 1 out/corte.png
# tamanho celular: dá pra ler a 360 px de largura?
ffmpeg -y -ss 3 -i out/video.mp4 -vf scale=360:-2 -frames:v 1 out/celular.png
# loudness e pico do arquivo entregue
ffmpeg -i out/final.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
```

## Notas de 1 a 10
1. **Gancho** nos primeiros 2 s, sem som
2. **Legibilidade** no tamanho do celular
3. **Qualidade do movimento:** molas, nada deslizando linear, nenhum quadro morto
4. **Costuras:** portadores, vetores casados, sem pulo nem quadro vazio no corte
5. **Variedade:** algo novo a cada 2–4 s, um movimento-assinatura
6. **Composição e área segura:** centrado em 540, nada nas zonas de perigo
7. **Precisão de marca/produto:** UI real em tamanho real, números honestos
8. **Sincronia do som:** efeitos nos quadros de contato, estrutura audível
9. **Visual:** todo quadro pertence ao `style_guide.md`, nada parece padrão
10. **Acabamento:** ao lado da referência, parece tão pronto quanto? Profundidade, luz, tipografia

8+ significa: você colocaria ao lado da referência sem pedir desculpas. Se não sabe dizer por que é 8
com a folha aberta na frente, não é 8.

## Caçar especificamente
- Quadro vazio ou quase vazio logo depois de um corte (portador chegou tarde)
- Resto da cena anterior vazando na seguinte
- Camada com `clip-path` que sumiu inteira (camada sem tamanho)
- Texto sobreposto durante troca, ou dois títulos ao mesmo tempo
- Algo deslizando linear em vez de mola
- Bordas duplicadas/escalonadas em movimento rápido (subquadros separados demais)
- Texto sobre fundo movimentado sem contraste
- Texto borrado por escala (`will-change`, bitmap escalado)
- Beat em que nada acontece e que não é um vácuo intencional

## Depois
Escreva as notas e os 3 piores problemas com timestamp em `out/review_log.md`, corrija, re-renderize só
os stills/segundos afetados e dê nota de novo. Pare quando tudo for 8+; aí render completo e repita.
