#!/usr/bin/env bash
# mux.sh — junta vídeo + trilha e masteriza para redes sociais: -15 LUFS integrado, pico abaixo de -1.5 dB.
#   bash mux.sh out/video.mp4 out/trilha.wav out/final.mp4 [alvo_lufs]
# 1) mede a loudness da trilha  2) aplica o ganho que falta  3) limita os picos com oversampling 4x
# 4) mede de novo o arquivo ENTREGUE (depois do AAC) e falha se errou o alvo por mais de 1 LU.
set -euo pipefail
VID="$1"; AUD="$2"; OUT="$3"; ALVO="${4:--15}"
mede() { ffmpeg -hide_banner -nostats -i "$1" -af ebur128=peak=true -f null - 2>&1; }
I=$(mede "$AUD" | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
GANHO=$(awk -v a="$ALVO" -v i="$I" 'BEGIN{printf "%.2f", a - i + 1.5}')   # +1.5: compensa o que o limitador come
AF="aresample=192000,volume=${GANHO}dB,alimiter=limit=0.79:level=false:attack=2:release=60,aresample=48000"
ffmpeg -y -loglevel error -i "$VID" -i "$AUD" -map 0:v -map 1:a -c:v copy -af "$AF" -c:a aac -b:a 256k -shortest -movflags +faststart "$OUT"
R=$(mede "$OUT"); FI=$(echo "$R" | grep -E '^\s+I:' | tail -1 | awk '{print $2}'); FP=$(echo "$R" | grep -E '^\s+Peak:' | tail -1 | awk '{print $2}')
echo "trilha: ${I} LUFS -> ganho ${GANHO} dB | entregue: ${FI} LUFS, pico real ${FP} dBFS"
awk -v f="$FI" -v a="$ALVO" -v p="$FP" 'BEGIN{ if (f-a>1 || a-f>1 || p>-1.5) { print "FORA DO ALVO"; exit 1 } }'
echo "final -> $OUT"
