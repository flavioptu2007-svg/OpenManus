#!/usr/bin/env bash
# ============================================================================
#  📊 Histórico do Diagnóstico de Rede
#  Mostra os registros automáticos salvos pelo cron.
#
#  Uso:
#    ./rede_historico.sh            # lista os últimos registros (resumo)
#    ./rede_historico.sh --ultimo   # mostra o registro mais recente completo
#    ./rede_historico.sh 2026-08-01 # mostra o registro de uma data (YYYY-MM-DD)
# ============================================================================
set -u

DIR_LOG="$HOME/rede_historico"
if [ ! -d "$DIR_LOG" ]; then
  echo "Nenhum histórico ainda (o cron roda em ~/rede_historico)."
  exit 1
fi

case "${1:-}" in
  --ultimo|-u)
    ULT=$(ls -1t "$DIR_LOG"/rede_*.log 2>/dev/null | head -1)
    [ -z "$ULT" ] && { echo "Nenhum registro ainda."; exit 1; }
    echo "📄 Registro mais recente: $(basename "$ULT")"
    echo "============================================================"
    cat "$ULT"
    ;;
  --resumo|-r|"")
    echo "📊 ÚLTIMOS REGISTROS DE REDE (em $DIR_LOG)"
    echo "============================================================"
    for f in $(ls -1t "$DIR_LOG"/rede_*.log 2>/dev/null | head -${2:-10}); do
      DATA=$(basename "$f" | sed 's/rede_//; s/\.log//')
      SIG=$(grep -oE 'Sinal: -?[0-9]+ dBm' "$f" | head -1)
      PERDA=$(grep -oE 'perda: [0-9]+%' "$f" | head -1 | sed 's/perda: //')
      DOWN=$(grep -oE 'Download: [0-9.]+ Mbit/s' "$f" | head -1 | sed 's/Download: //; s/ Mbit.s//')
      UP=$(grep -oE 'Upload: [0-9.]+ Mbit/s' "$f" | head -1 | sed 's/Upload: //; s/ Mbit.s//')
      AVISO=""
      grep -q 'Possível degradação' "$f" && AVISO=" ⚠️"
      printf "  %-16s | %-18s | perda %-3s | ↓ %-8s | ↑ %-8s%s\n" \
        "$DATA" "${SIG:-sinal: n/a}" "${PERDA:-n/a}" "${DOWN:-n/a}" "${UP:-n/a}" "$AVISO"
    done
    echo
    echo "Total de registros: $(ls -1 "$DIR_LOG"/rede_*.log 2>/dev/null | wc -l)"
    echo "Dica: use --ultimo para ver o registro completo, ou passe uma data (YYYY-MM-DD)."
    ;;
  *)
    PAT="*$1*.log"
    MATCH=$(ls -1 "$DIR_LOG"/rede_$PAT 2>/dev/null)
    if [ -n "$MATCH" ]; then
      echo "📄 Registros de $1:"
      echo "============================================================"
      cat $MATCH
    else
      echo "Nenhum registro para '$1'." >&2
      exit 1
    fi
    ;;
esac
