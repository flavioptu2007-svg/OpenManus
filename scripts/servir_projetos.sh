#!/usr/bin/env bash
# ============================================================================
#  📱 Portal de Projetos Educacionais — acesso pelo celular na rede local
#
#  Monta um diretório de portal com symlinks SOMENTE para os arquivos
#  educacionais (HTMLs + recursos) e sobe um servidor HTTP em 0.0.0.0.
#  NUNCA expõe .env, config.toml, .git, backups ou código-fonte Python.
#
#  Uso:
#    ./servir_projetos.sh            # sobe o servidor (porta 8765)
#    ./servir_projetos.sh --porta 9000
#    ./servir_projetos.sh --parar    # derruba o servidor
#    ./servir_projetos.sh --status
#
#  Acesse pelo celular (mesma rede Wi-Fi):
#    http://192.168.15.17:8765
# ============================================================================
set -u

PROJ_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${2:-8765}"
[ "${1:-}" = "--porta" ] && PORT="${2:-8765}" && shift 2 || true
PORT="${1:-8765}"
PORT="${PORT#--porta=}"

PORTAL="$HOME/portal_projetos"
PIDFILE="$PORTAL/.servidor.pid"
LOG="$PORTAL/.servidor.log"

VERDE=$'\e[0;32m'; AMARELO=$'\e[1;33m'; VERMELHO=$'\e[0;31m'; AZUL=$'\e[0;34m'; CINZA=$'\e[2m'; RESET=$'\e[0m'
ok()   { echo -e "${VERDE}  ✅ $1${RESET}"; }
info() { echo -e "${AZUL}  ℹ️  $1${RESET}"; }
warn() { echo -e "${AMARELO}  ⚠️  $1${RESET}"; }
erro() { echo -e "${VERMELHO}  ❌ $1${RESET}"; }

# ------------------------------------------------------------------ helpers
ip_local() {
  ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}' \
    || hostname -I 2>/dev/null | awk '{print $1}'
}

servidor_rodando() { [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; }

parar_servidor() {
  if servidor_rodando; then
    kill "$(cat "$PIDFILE")" 2>/dev/null
    sleep 0.5
    ok "Servidor parado (PID $(cat "$PIDFILE"))."
  else
    info "Nenhum servidor ativo."
  fi
  rm -f "$PIDFILE"
}

# ------------------------------------------------------------------ montar portal
montar_portal() {
  rm -rf "$PORTAL"
  mkdir -p "$PORTAL"
  cd "$PROJ_ROOT"

  # 1) HTMLs educacionais (raiz) — todos
  for f in *.html; do
    [ -f "$f" ] && ln -s "$PROJ_ROOT/$f" "$PORTAL/$f"
  done

  # 2) Recursos compartilhados usados pelos HTMLs
  for r in i18n-loader.js sw_omredu.js i18n; do
    [ -e "$PROJ_ROOT/$r" ] && ln -s "$PROJ_ROOT/$r" "$PORTAL/$r"
  done

  # 3) index.html gerado com links para todos os projetos
  gerar_index

  local total; total=$(ls "$PORTAL"/*.html | wc -l)
  info "Portal montado em $PORTAL ($total arquivos HTML + recursos)."
}

gerar_index() {
  local ip; ip=$(ip_local)
  local f nome emoji
  cat > "$PORTAL/index.html" <<EOF
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📱 Projetos Educacionais</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',system-ui,sans-serif;background:linear-gradient(160deg,#1e1b4b,#312e81 60%,#4f46e5);min-height:100vh;color:#fff;padding:24px 16px 60px}
  h1{font-size:1.5rem;margin-bottom:4px}
  p.sub{color:#a5b4fc;font-size:.85rem;margin-bottom:20px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
  a.card{display:block;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);border-radius:16px;padding:16px;color:#fff;text-decoration:none;transition:all .15s}
  a.card:hover{background:rgba(255,255,255,.16);transform:translateY(-3px);border-color:#a5b4fc}
  .emoji{font-size:2rem;display:block;margin-bottom:8px}
  .nome{font-weight:800;font-size:.95rem}
  .dica{margin-top:22px;background:rgba(255,255,255,.07);border-radius:12px;padding:12px 14px;font-size:.8rem;color:#c7d2fe}
  code{background:rgba(0,0,0,.3);padding:2px 8px;border-radius:6px;font-size:.85rem}
</style>
</head>
<body>
  <h1>📱 Projetos Educacionais</h1>
  <p class="sub">Servidos pelo seu computador na rede local — abra no celular ou tablet.</p>
  <div class="grid">
EOF
  for f in "$PORTAL"/*.html; do
    b=$(basename "$f")
    [ "$b" = "index.html" ] && continue
    nome=$(echo "$b" | sed 's/_/ /g; s/\.html//' | sed -E 's/\b(.)/\U\1/g')
    case "$b" in
      *bingo*)      emoji="🎱";;
      *memoria*)    emoji="🧠";;
      *quiz*)       emoji="❓";;
      *jogo*)       emoji="🎮";;
      *domino*)     emoji="🁫";;
      *uno*)        emoji="🃏";;
      *prova*)      emoji="📝";;
      *escola*|*gestao*|*diario*) emoji="🏫";;
      *corretor*)   emoji="✅";;
      *adapt*)      emoji="🧩";;
      *debate*)     emoji="🗣️";;
      *labirinto*)  emoji="🌀";;
      *historia*|*historico*) emoji="📜";;
      *)            emoji="📄";;
    esac
    echo "    <a class=\"card\" href=\"./$b\"><span class=\"emoji\">$emoji</span><span class=\"nome\">$nome</span></a>" >> "$PORTAL/index.html"
  done
  cat >> "$PORTAL/index.html" <<EOF
  </div>
  <div class="dica">💡 No celular: acesse <code>http://$ip:$PORT</code> — o computador e o celular devem estar na <b>mesma rede Wi-Fi</b>. Para encerrar: <code>./scripts/servir_projetos.sh --parar</code></div>
</body>
</html>
EOF
}

# ------------------------------------------------------------------ main
case "${1:-}" in
  --parar|-p) parar_servidor; exit 0;;
  --status|-s)
    if servidor_rodando; then
      ok "Servidor ATIVO na porta $(grep -oE '\-[pP] [0-9]+' "$LOG" 2>/dev/null | tail -1 || echo 8765)."
      info "Acesse: http://$(ip_local):$(grep -oE 'port [0-9]+' "$LOG" 2>/dev/null | head -1 || echo 8765)"
    else
      info "Servidor parado."
    fi
    exit 0;;
esac

if servidor_rodando; then
  warn "Já existe um servidor ativo (PID $(cat "$PIDFILE")). Use --parar primeiro."
  exit 1
fi

echo "============================================================"
echo "   📱 PORTAL DE PROJETOS EDUCACIONAIS"
echo "============================================================"
montar_portal

IP=$(ip_local)
if [ -z "$IP" ]; then
  erro "Não foi possível detectar o IP da rede local."
  exit 1
fi

cd "$PORTAL"
# setsid: desacopla o processo em nova sessão — sobrevive ao fechamento do
# terminal (nohup sozinho pode morrer junto com o shell em alguns ambientes).
setsid python3 -m http.server "$PORT" --bind 0.0.0.0 > "$LOG" 2>&1 < /dev/null &
disown
sleep 1
# o PID do setsid pode ser o de um processo intermediário — captura o PID real
# que está escutando na porta (via ss) ou o python http.server (via pgrep).
REAL_PID=$(ss -tlnp 2>/dev/null | grep ":$PORT " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)
if [ -z "$REAL_PID" ]; then
  REAL_PID=$(pgrep -f "http.server $PORT" | head -1)
fi
[ -n "$REAL_PID" ] && echo "$REAL_PID" > "$PIDFILE"

if servidor_rodando; then
  echo
  ok "Servidor rodando em http://0.0.0.0:$PORT (PID $(cat "$PIDFILE"))"
  echo
  echo -e "${AZUL}  📲 No CELULAR (mesma rede Wi-Fi) acesse:${RESET}"
  echo -e "${VERDE}     http://$IP:$PORT${RESET}"
  echo
  echo -e "${CINZA}  Portal gerado: $PORTAL${RESET}"
  echo -e "${CINZA}  Derrubar: ./scripts/servir_projetos.sh --parar${RESET}"
  echo -e "${CINZA}  Status:  ./scripts/servir_projetos.sh --status${RESET}"
  echo
  # verificação local
  if curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/index.html" | grep -q 200; then
    ok "Verificação local: portal respondeu HTTP 200."
  else
    warn "O portal não respondeu localmente — confira o log: $LOG"
  fi
else
  erro "Falha ao iniciar o servidor. Log: $LOG"
  cat "$LOG" 2>/dev/null | tail -5
  exit 1
fi
