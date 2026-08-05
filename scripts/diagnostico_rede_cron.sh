#!/usr/bin/env bash
# ============================================================================
#  📶 Diagnóstico de Rede — modo automático (cron)
#  Roda o diagnostico_rede.sh --speed e salva o resultado em um histórico
#  com rotação (mantém os últimos 90 registros).
#
#  Uso (via crontab):
#    0 8,20 * * * /home/flavio/OpenManus/scripts/diagnostico_rede_cron.sh
#
#  Histórico: ~/rede_historico/rede_YYYY-MM-DD_HHMM.log
#  Consulta:  ~/rede_historico.sh  (alias: rede-hist)
# ============================================================================
set -u

# ---- cron roda com PATH mínimo — garanta os binários comuns ----------------
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/.local/bin"

DIR_LOG="$HOME/rede_historico"
mkdir -p "$DIR_LOG" || { echo "ERRO: nao consegui criar $DIR_LOG"; exit 1; }

# ---- garante o speedtest-cli (o venv em /tmp pode sumir no reboot) ---------
ST="/tmp/stenv/bin/speedtest-cli"
if [ ! -x "$ST" ]; then
  python3 -m venv /tmp/stenv >/dev/null 2>&1 \
    && /tmp/stenv/bin/pip install --quiet --disable-pip-version-check speedtest-cli >/dev/null 2>&1
fi

# ---- executa e salva o log datado -------------------------------------------
LOG="$DIR_LOG/rede_$(date '+%Y-%m-%d_%H%M').log"
if bash /home/flavio/OpenManus/scripts/diagnostico_rede.sh --speed > "$LOG" 2>&1; then
  STATUS="OK"
else
  STATUS="FALHA(exit=$?)"
fi
echo "[$STATUS] $(date '+%d/%m/%Y %H:%M') -> $LOG" >> "$DIR_LOG/ultimo.log"

# ---- rotação: mantém só os 90 logs mais recentes ----------------------------
ls -1t "$DIR_LOG"/rede_*.log 2>/dev/null | tail -n +91 | xargs -r rm -f

# ---- detecta degradação e avisa no log --------------------------------------
if grep -qE 'fraco|perda de pacotes|Falha ao rodar o speedtest|Sem resposta' "$LOG" 2>/dev/null; then
  echo "⚠️  Possível degradação de rede neste registro." >> "$LOG"
fi

exit 0
