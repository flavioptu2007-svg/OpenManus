#!/usr/bin/env bash
# ============================================================================
#  📶 Diagnóstico Rápido de Rede
#  Verifica: conexão Wi-Fi, sinal, latência, DNS, congestionamento de canais
#  e painel do roteador — tudo em um comando.
#
#  Uso:
#    ./diagnostico_rede.sh          # diagnóstico rápido
#    ./diagnostico_rede.sh --speed  # inclui teste profissional de pings e speedtest
#    ./diagnostico_rede.sh --help
# ============================================================================
set -u

VERDE=$'\e[0;32m'; AMARELO=$'\e[1;33m'; VERMELHO=$'\e[0;31m'; AZUL=$'\e[0;34m'; CINZA=$'\e[2m'; RESET=$'\e[0m'

ok()   { echo -e "${VERDE}  ✅ $1${RESET}"; }
info() { echo -e "${AZUL}  ℹ️  $1${RESET}"; }
warn() { echo -e "${AMARELO}  ⚠️  $1${RESET}"; }
erro() { echo -e "${VERMELHO}  ❌ $1${RESET}"; }

avaliar_sinal() {
  local s="$1"
  if   [ "$s" -ge -50 ]; then echo "🟢 excelente"
  elif [ "$s" -ge -60 ]; then echo "🟢 bom"
  elif [ "$s" -ge -67 ]; then echo "🟡 regular"
  else echo "🔴 fraco — aproxime-se do roteador"
  fi
}

separador() { echo; echo -e "${CINZA}------------------------------------------------------------${RESET}"; echo -e "${AZUL}▶ $1${RESET}"; }

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  echo "Uso: $0 [--speed]"
  echo "  (sem opção)   diagnóstico rápido"
  echo "  --speed       inclui teste profissional de pings e speedtest de banda"
  exit 0
fi

echo "============================================================"
echo "   📶 DIAGNÓSTICO RÁPIDO DE REDE"
echo "   $(date '+%d/%m/%Y às %H:%M')"
echo "============================================================"

# ------------------------------------------------------------------ Wi-Fi
separador "Conexão Wi-Fi"
IFACE=$(iw dev 2>/dev/null | awk '/Interface/{print $2; exit}')
if [ -n "$IFACE" ]; then
  SSID=$(iw dev "$IFACE" link 2>/dev/null | awk -F': ' '/SSID/{print $2}')
  SIG=$( iw dev "$IFACE" link 2>/dev/null | awk -F'signal: ' '/signal/{print $2}' | awk '{print $1}')
  FREQ=$(iw dev "$IFACE" link 2>/dev/null | awk -F'freq: ' '/freq/{print $2}')
  RATE=$(iw dev "$IFACE" link 2>/dev/null | awk -F'tx bitrate: ' '/tx bitrate/{print $2}' | awk '{print $1}')
  if [ -n "$SSID" ]; then
    echo "  Rede conectada: $SSID"
    [ -n "$SIG" ]  && echo "  Sinal: ${SIG} dBm ($(avaliar_sinal "$SIG"))"
    if [ -n "$FREQ" ]; then
      FREQ_INT=${FREQ%%.*}   # remove o decimal (ex.: 5580.0 -> 5580)
      BANDA="2.4GHz"; [ "$FREQ_INT" -ge 4900 ] && BANDA="5GHz"
      echo "  Frequência: $FREQ MHz ($BANDA)"
    fi
    [ -n "$RATE" ] && echo "  Velocidade do link: ${RATE} Mbit/s"
  else
    warn "Não conectado a nenhuma rede Wi-Fi."
  fi
else
  warn "Comando 'iw' indisponível ou interface não encontrada."
fi

# ------------------------------------------------------------------ Gateway
separador "Roteador (gateway)"
GW=$(ip route 2>/dev/null | awk '/default/{print $3; exit}')
IP_LOCAL=$(ip route 2>/dev/null | awk '/default/{print $9; exit}')
if [ -n "$GW" ]; then
  echo "  IP local: $IP_LOCAL  |  Gateway: $GW"
  PING_GW=$(ping -c 3 -W 2 "$GW" 2>/dev/null)
  MEDIA_GW=$(echo "$PING_GW" | awk -F'/' '/rtt/{print $5}')
  PERDA_GW=$(echo "$PING_GW" | awk '/packet loss/{print $6}')
  if [ -n "$MEDIA_GW" ] && [ "$PERDA_GW" = "0%" ]; then
    ok "Ping até o roteador: ${MEDIA_GW} ms (0% perda)"
  else
    warn "Ping ao roteador com perda ou variação (${PERDA_GW:-?} perda)."
  fi
  if timeout 4 curl -sI "http://$GW/" >/dev/null 2>&1; then
    ok "Painel web acessível em http://$GW"
  else
    warn "Painel web não respondeu em http://$GW"
  fi
else
  erro "Sem gateway — verifique a conexão de rede."
fi

# ------------------------------------------------------------------ Internet
separador "Internet (latência)"
P=$(ping -c 5 -W 2 1.1.1.1 2>/dev/null)
PERDA=$(echo "$P" | awk '/packet loss/{print $6}')
MEDIA=$(echo "$P" | awk -F'/' '/rtt/{print $5}')
if [ -n "$MEDIA" ]; then
  echo "  Ping 1.1.1.1: média ${MEDIA} ms | perda: ${PERDA}"
  if [ "$PERDA" = "0%" ] && awk "BEGIN{exit !($MEDIA < 50)}"; then
    ok "Latência excelente para jogos e videoconferência"
  elif [ "$PERDA" = "0%" ]; then
    ok "Latência ok"
  else
    warn "Perda de pacotes detectada — verifique sinal ou operadora."
  fi
else
  erro "Sem resposta da internet (1.1.1.1)."
fi

# ------------------------------------------------------------------ Teste profissional (opcional)
if [ "${1:-}" = "--speed" ] || [ "${1:-}" = "-s" ]; then
  separador "Teste profissional (20 pings em 1.1.1.1)"
  P2=$(ping 1.1.1.1 -c 20 -i 0.2 2>/dev/null)
  echo "$P2" | awk -F'/' '/rtt/{printf "  Latência média: %s ms | jitter: %s ms\n", $5, $7}'
  echo "$P2" | awk '/packet loss/{printf "  Perda de pacotes: %s\n", $6}'
fi

# ------------------------------------------------------------------ DNS
separador "DNS"
RESOLV=$(grep -m1 nameserver /etc/resolv.conf 2>/dev/null | awk '{print $2}')
echo "  Resolver em uso: $RESOLV"
T0=$(date +%s%N); nslookup google.com "$RESOLV" >/dev/null 2>&1; T1=$(date +%s%N)
echo "  Tempo para resolver google.com: $(( (T1-T0)/1000000 )) ms"

# ------------------------------------------------------------------ Canais vizinhos
separador "Redes vizinhas (congestionamento de canais)"
if nmcli dev wifi list >/dev/null 2>&1; then
  nmcli -f IN-USE,SSID,CHAN,SIGNAL dev wifi list 2>/dev/null | column -t -s$'\t' 2>/dev/null | head -16
else
  warn "Sem permissão para escanear canais — rode com 'sudo' para ver as redes vizinhas."
fi

# ------------------------------------------------------------------ Speedtest (opcional)
if [ "${1:-}" = "--speed" ] || [ "${1:-}" = "-s" ]; then
  separador "Speedtest de banda"
  if [ -x /tmp/stenv/bin/speedtest-cli ]; then
    /tmp/stenv/bin/speedtest-cli 2>/dev/null | grep -E 'Hosted|Download|Upload' || warn "Falha ao rodar o speedtest."
  else
    warn "speedtest-cli não encontrado. Instale com:  pip install --user speedtest-cli"
  fi
fi

echo
echo "============================================================"
echo "   Diagnóstico concluído ✅"
echo "============================================================"
