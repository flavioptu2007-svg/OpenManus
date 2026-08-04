#!/usr/bin/env python3
"""
Injeta relatório de desempenho do Caça-Palavras no frontend v3.0.

- Ao completar o CP, envia dados para o backend OMR
- Adiciona painel de histórico com estatísticas
"""

import os


home = os.path.expanduser("~")
V3_PATH = os.path.join(
    home, "Secret\u00e1ria", "Download", "planejador-escolar-v3.0.html"
)

with open(V3_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Backup
bak = V3_PATH + ".bak_cp_report"
with open(bak, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Backup: {bak}")

# ═══════════════════════════════════════════════════════════════
# CSS para o painel de histórico
# ═══════════════════════════════════════════════════════════════

report_css = """
/* ── CP REPORT ── */
#jogos .cp-report-bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 8px 0 16px; padding: 8px 16px; background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 8px; font-size: .82rem; }
#jogos .cp-report-bar .cp-rb-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
#jogos .cp-report-bar .cp-rb-dot.online { background: #4ecdc4; }
#jogos .cp-report-bar .cp-rb-dot.offline { background: var(--cp-accent); }
#jogos .cp-report-panel { background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 12px; padding: 16px; margin-top: 16px; }
#jogos .cp-report-panel h3 { font-size: .95rem; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
#jogos .cp-report-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 10px; }
#jogos .cp-report-stat { background: var(--cp-card); border-radius: 8px; padding: 12px; text-align: center; }
#jogos .cp-report-stat .num { font-size: 1.4rem; font-weight: 800; color: var(--cp-gold); }
#jogos .cp-report-stat .lbl { font-size: .7rem; color: var(--cp-muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; }
#jogos .cp-report-table { width: 100%; border-collapse: collapse; font-size: .8rem; margin-top: 12px; }
#jogos .cp-report-table th { background: var(--cp-card); color: var(--cp-muted); font-size: .7rem; text-transform: uppercase; letter-spacing: 1px; padding: 8px 10px; text-align: left; }
#jogos .cp-report-table td { padding: 7px 10px; border-bottom: 1px solid var(--cp-border); }
#jogos .cp-report-table tr:hover td { background: var(--cp-card); }
#jogos .cp-report-table .cp-record-badge { display: inline-block; padding: 1px 6px; border-radius: 4px; background: rgba(255,215,0,.2); color: var(--cp-gold); font-size: .7rem; font-weight: 700; }
"""

# ═══════════════════════════════════════════════════════════════
# HTML para o painel de histórico
# ═══════════════════════════════════════════════════════════════

report_html = """
<div class="cp-report-bar" id="cp-reportBar">
  <span class="cp-rb-dot offline" id="cp-rb-dot"></span>
  <span id="cp-rb-status">Servidor OMR: desconectado</span>
  <button class="cp-btn" onclick="cpCarregarHistorico()" style="margin-left:auto;padding:4px 12px;font-size:.75rem">📊 Histórico</button>
</div>

<div class="cp-report-panel" id="cp-reportPanel" style="display:none">
  <h3>📊 Estatísticas do Caça-Palavras</h3>
  <div class="cp-report-grid" id="cp-reportStatsGrid">
    <div class="cp-report-stat"><div class="num" id="cp-rs-total">0</div><div class="lbl">Partidas</div></div>
    <div class="cp-report-stat"><div class="num" id="cp-rs-media-tempo">0s</div><div class="lbl">Média Tempo</div></div>
    <div class="cp-report-stat"><div class="num" id="cp-rs-melhor-tempo">0s</div><div class="lbl">Melhor Tempo</div></div>
    <div class="cp-report-stat"><div class="num" id="cp-rs-media-acerto">0%</div><div class="lbl">Média Acerto</div></div>
  </div>
  <div style="max-height:300px;overflow-y:auto">
    <table class="cp-report-table" id="cp-reportTable">
      <thead><tr><th>Data</th><th>Aluno</th><th>Tema</th><th>Dif.</th><th>Palavras</th><th>Tempo</th><th>Recorde</th></tr></thead>
      <tbody id="cp-reportTbody"></tbody>
    </table>
  </div>
  <button class="cp-btn" onclick="document.getElementById('cp-reportPanel').style.display='none'" style="margin-top:10px;padding:4px 12px;font-size:.75rem">✕ Fechar</button>
</div>
"""

# ═══════════════════════════════════════════════════════════════
# JS: relatório ao completar + histórico
# ═══════════════════════════════════════════════════════════════

report_js = """
// ══════════════════════════════════════════════════════════
//  CP REPORT — Desempenho do Caça-Palavras
// ══════════════════════════════════════════════════════════

const CP_SERVER = 'http://localhost:5000';

function cpServerOnline() {
  return fetch(CP_SERVER + '/api/health', { method: 'GET', signal: AbortSignal.timeout(2000) })
    .then(function(r) { return r.ok; })
    .catch(function() { return false; });
}

function cpAtualizarStatusServidor() {
  cpServerOnline().then(function(online) {
    var dot = document.getElementById('cp-rb-dot');
    var status = document.getElementById('cp-rb-status');
    if (dot) {
      dot.className = 'cp-rb-dot ' + (online ? 'online' : 'offline');
      status.textContent = online ? 'Servidor OMR: conectado' : 'Servidor OMR: desconectado';
    }
  });
}

function cpEnviarRelatorio(tempo, palavrasEncontradas, palavrasTotal, isRecord, conquistas) {
  var disc = document.getElementById('cp-discSelect');
  var discName = disc ? disc.options[disc.selectedIndex]?.text || '' : '';
  var periodoEl = document.getElementById('cp-periodSelect');
  var periodo = periodoEl ? parseInt(periodoEl.value) + 1 : 0;

  // Get aluno/turma from the omr fields if available
  var aluno = document.getElementById('omr-nomeAluno')?.value || '';
  var turma = document.getElementById('omr-turmaAluno')?.value || '';

  var data = {
    aluno: aluno,
    turma: turma,
    tema: cpCurrentTheme,
    dificuldade: document.getElementById('cp-difficulty')?.value || 'medio',
    palavras_total: palavrasTotal,
    palavras_encontradas: palavrasEncontradas,
    tempo_segundos: tempo,
    is_record: isRecord,
    conquistas: conquistas || [],
    modo: cpCurrentMode || 'tema',
    disciplina: discName,
    periodo: periodo
  };

  fetch(CP_SERVER + '/api/cp-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(function(r) {
    if (r.ok) { cpAtualizarStatusServidor(); }
  }).catch(function() {});
}

// Override cpComplete to also send report
var cpCompleteOriginal = cpComplete;
cpComplete = function() {
  cpCompleteOriginal();

  // Send report to backend
  var total = cpPlacedCount || Object.keys(cpWordPositions).length;
  var encontradas = cpFoundWords.size;
  var tempo = cpSeconds;
  var prevKey = 'cp_record_' + cpCurrentTheme + '_' + (document.getElementById('cp-difficulty')?.value || 'medio');
  var prev = localStorage.getItem(prevKey);
  var isRecord = !prev || tempo < parseInt(prev);

  cpEnviarRelatorio(tempo, encontradas, total, isRecord, ['Completou o caça-palavras']);
};

function cpCarregarHistorico() {
  var panel = document.getElementById('cp-reportPanel');
  if (panel.style.display !== 'none') { panel.style.display = 'none'; return; }
  panel.style.display = 'block';

  var tema = cpCurrentTheme || '';

  fetch(CP_SERVER + '/api/cp-reports?tema=' + encodeURIComponent(tema) + '&limit=20')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var stats = data.stats || {};
      document.getElementById('cp-rs-total').textContent = stats.total_partidas || 0;
      document.getElementById('cp-rs-media-tempo').textContent = (stats.media_tempo || 0) + 's';
      document.getElementById('cp-rs-melhor-tempo').textContent = (stats.melhor_tempo || 0) + 's';
      document.getElementById('cp-rs-media-acerto').textContent = (stats.media_score || 0) + '%';

      var tbody = document.getElementById('cp-reportTbody');
      tbody.innerHTML = '';
      (data.reports || []).forEach(function(r) {
        var tr = document.createElement('tr');
        var dataStr = new Date(r.data_criacao).toLocaleString('pt-BR', {day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});
        var pct = r.palavras_total > 0 ? Math.round(r.palavras_encontradas / r.palavras_total * 100) : 0;
        var mins = Math.floor(r.tempo_segundos / 60);
        var secs = r.tempo_segundos % 60;
        var tempoStr = mins > 0 ? mins + 'm' + secs + 's' : secs + 's';
        var recordeHtml = r.is_record ? '<span class="cp-record-badge">🏆</span>' : '';
        tr.innerHTML = '<td>' + dataStr + '</td><td>' + (r.aluno || '-') + '</td><td>' + (r.tema || '-') + '</td><td>' + r.dificuldade + '</td><td>' + r.palavras_encontradas + '/' + r.palavras_total + ' (' + pct + '%)</td><td>' + tempoStr + '</td><td>' + recordeHtml + '</td>';
        tbody.appendChild(tr);
      });
    })
    .catch(function(err) {
      document.getElementById('cp-reportTbody').innerHTML = '<tr><td colspan="7" style="color:var(--cp-accent);text-align:center">Servidor OMR indisponível</td></tr>';
    });
}

// Check server status on load
setTimeout(cpAtualizarStatusServidor, 2000);
"""

# ═══════════════════════════════════════════════════════════════
# INJEÇÃO
# ═══════════════════════════════════════════════════════════════

# 1. CSS
idx = html.rfind("</style>")
if idx >= 0:
    html = html[:idx] + report_css + "\n" + html[idx:]
    print("✅ CSS injected")

# 2. HTML (antes do fechamento do container)
idx = html.find('<div class="cp-trophy"')
if idx >= 0:
    html = html[:idx] + report_html + "\n" + html[idx:]
    print("✅ HTML injected")
else:
    # Try alternative: before the cp-trophy div
    backup = html.find("cp-confetti-container")
    if backup >= 0:
        html = html[:backup] + report_html + "\n" + html[backup:]
        print("✅ HTML injected (alt)")

# 3. JS (antes do último event listener)
# Find the CP-specific JS section end - inject before the last cpToast/cpPrint
markers = ["function cpPrintableArea", "function cpToast(", "// ═══════════════════"]
for marker in markers:
    idx = html.find(marker)
    if idx >= 0:
        html = html[:idx] + report_js + "\n\n" + html[idx:]
        print(f'✅ JS injected before "{marker[:30]}"')
        break

with open(V3_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\n✅ Done! File size: {len(html)} chars")
