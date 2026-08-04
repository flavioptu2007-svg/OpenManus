#!/usr/bin/env python3
"""
Adiciona gerador de Caça-Palavras por disciplina ao Planejador v3.0.

O gerador:
1. Lê os PRESETS e PLANO_HISTORIA6 do v3.0 para extrair termos
2. Permite selecionar disciplina + período
3. Gera CP com termos relevantes da disciplina selecionada
"""

import os


home = os.path.expanduser("~")
V3_PATH = os.path.join(
    home, "Secret\u00e1ria", "Download", "planejador-escolar-v3.0.html"
)

with open(V3_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Backup
bak = V3_PATH + ".bak_pre_generator"
with open(bak, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Backup: {bak}")

# ═══════════════════════════════════════════════════════════════
# 1. CSS ADICIONAL (escopado sob #jogos)
# ═══════════════════════════════════════════════════════════════

extra_css = """
/* ── GERADOR POR DISCIPLINA ── */
#jogos .cp-mode-toggle { display: flex; gap: 4px; background: var(--cp-surface); border-radius: 8px; padding: 3px; margin: 0 0 12px; }
#jogos .cp-mode-btn { padding: 6px 16px; border-radius: 6px; border: none; background: transparent; color: var(--cp-muted); cursor: pointer; font-size: .78rem; font-weight: 600; transition: all .2s; }
#jogos .cp-mode-btn.active { background: var(--cp-accent); color: #fff; }
#jogos .cp-mode-btn:hover:not(.active) { color: var(--cp-text); }
#jogos .cp-disc-config { background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 12px; padding: 16px; margin-bottom: 16px; display: none; gap: 12px; flex-wrap: wrap; align-items: center; }
#jogos .cp-disc-config.visible { display: flex; }
#jogos .cp-disc-config label { font-size: .8rem; color: var(--cp-muted); display: flex; flex-direction: column; gap: 4px; }
#jogos .cp-disc-config select, #jogos .cp-disc-config input { padding: 6px 12px; border-radius: 6px; border: 1px solid var(--cp-border); background: var(--cp-card); color: var(--cp-text); font-size: .82rem; min-width: 160px; }
#jogos .cp-vocab-tags { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0 8px; }
#jogos .cp-vocab-tag { padding: 4px 10px; border-radius: 100px; font-size: .75rem; font-weight: 600; background: rgba(78,205,196,.15); color: var(--cp-teal); border: 1px solid rgba(78,205,196,.3); }
"""

# ═══════════════════════════════════════════════════════════════
# 2. HTML ADICIONAL (controles do gerador)
# ═══════════════════════════════════════════════════════════════

extra_html = """
<div class="cp-mode-toggle">
  <button class="cp-mode-btn active" onclick="cpSetMode('theme')" id="cp-mode-theme">🎨 Temas Fixos</button>
  <button class="cp-mode-btn" onclick="cpSetMode('disc')" id="cp-mode-disc">📚 Por Disciplina</button>
</div>

<div class="cp-disc-config" id="cp-discConfig">
  <label>Disciplina
    <select id="cp-discSelect" onchange="cpLoadDiscVocab()">
      <option value="">Selecione...</option>
    </select>
  </label>
  <label>Período
    <select id="cp-periodSelect">
      <option value="0">1º Período</option>
      <option value="1">2º Período</option>
      <option value="2">3º Período</option>
      <option value="3">4º Período</option>
    </select>
  </label>
  <label style="flex:1;min-width:120px">
    <span style="font-size:.75rem;color:var(--cp-muted);font-weight:400;margin-bottom:2px">Termos encontrados: <strong id="cp-vocabCount">0</strong></span>
    <div class="cp-vocab-tags" id="cp-vocabTags"></div>
  </label>
</div>
"""

# ═══════════════════════════════════════════════════════════════
# 3. JS ADICIONAL (funções do gerador)
# ═══════════════════════════════════════════════════════════════

extra_js = """

// ══════════════════════════════════════════════════════════
//  GERADOR POR DISCIPLINA
// ══════════════════════════════════════════════════════════

let cpCurrentMode = 'theme';
let cpDiscVocab = [];

// Vocabulário base por disciplina (termos comuns de cada área)
const cpDiscVocabBase = {
  historia6: ['PREHISTORIA','MESOPOTAMIA','EGITO','GREGA','ROMA','FEUDALISMO','CRUZADAS','NAVEGACOES','RENASCIMENTO','REFORMA','ABSOLUTISMO','ILUMINISMO','REVOLUCAO','ILHA','ESCRAVIDAO','COLONIA','IMPRIO','MONARQUIA','DEMOCRACIA','MITOLOGIA','FILOSOFIA','HUMANISMO','CAPITALISMO','SOCIALISMO','NACIONALISMO'],
  geo: ['MAPAMONDI','LATITUDE','LONGITUDE','CLIMA','RELEVO','HIDROGRAFIA','POPULACAO','MIGRACAO','URBANIZACAO','BIOMA','AMAZONIA','CERRADO','DESERTO','FUSOHORARIO','PLACATECTONICA','VULCAO','TERREMOTO','BIODIVERSIDADE','SUSTENTABILIDADE','GLOBALIZACAO'],
  port: ['SUBSTANTIVO','VERBO','ADJETIVO','PRONOME','ADVERBIO','PREPOSICAO','CONJUNCAO','ARTIGO','NUMERAL','INTERJEICAO','SUJEITO','PREDICADO','OBJETO','ADJUNTO','COMPLEMENTO','ORACAO','PERIODO','PARAGRAFO','FIGURAS','METAFORA','SINONIMO','ANTONIMO','PARONIMO'],
  mat: ['NUMERO','ALGARISMO','FRACAO','DECIMAL','PORCENTAGEM','RAZAO','PROPORCAO','REGRASTRES','GEOMETRIA','ANGULO','TRIANGULO','QUADRADO','RETANGULO','CIRCULO','VOLUME','AREA','PERIMETRO','EQUACAO','VARIAVEL','FUNCAO','GRAFICO','ESTATISTICA','PROBABILIDADE'],
  cien: ['MATERIA','MOLECULA','ATOMO','CELULA','TECIDO','ORGAO','SISTEMA','DNA','GENE','EVOLUCAO','FOTOSSINTESE','ECOSSISTEMA','CADEIAALIMENTAR','ENERGIA','FORCA','MOVIMENTO','CALOR','LUZ','SOM','ELETRICIDADE','MAGNETISMO','REACAOQUIMICA'],
};

function cpSetMode(mode) {
  cpCurrentMode = mode;
  document.querySelectorAll('#jogos .cp-mode-btn').forEach(function(b) { b.classList.toggle('active', b.id === 'cp-mode-' + mode); });
  document.getElementById('cp-discConfig').classList.toggle('visible', mode === 'disc');
  document.querySelector('#jogos .cp-theme-selector').style.display = mode === 'theme' ? 'flex' : 'none';
  document.getElementById('cp-difficulty').style.display = mode === 'theme' ? '' : 'none';
  if (mode === 'disc') cpPopulateDiscSelect();
}

function cpPopulateDiscSelect() {
  var sel = document.getElementById('cp-discSelect');
  while (sel.options.length > 1) sel.remove(1);

  // Also populate period selector dynamically
  cpPopulatePeriodSelect();

  var presets = null;
  try { presets = (typeof PRESETS !== 'undefined') ? PRESETS : null; } catch(e) {}

  if (presets) {
    for (var key in presets) {
      if (presets.hasOwnProperty(key) && presets[key] && presets[key].label) {
        var opt = document.createElement('option');
        opt.value = key;
        opt.textContent = presets[key].label;
        sel.appendChild(opt);
      }
    }
  } else {
    var fallback = {historia6:'História 6º ano', geo:'Geografia', port:'Língua Portuguesa', mat:'Matemática', cien:'Ciências'};
    for (var k in fallback) {
      var o = document.createElement('option');
      o.value = k; o.textContent = fallback[k];
      sel.appendChild(o);
    }
  }
}

function cpPopulatePeriodSelect() {
  var sel = document.getElementById('cp-periodSelect');
  var n = 4;
  try { if (typeof getCfg !== 'undefined') n = getCfg().n; } catch(e) {}
  sel.innerHTML = '';
  var nomes = {1:'Período', 3:'Trimestre', 4:'Bimestre'};
  var nome = nomes[n] || 'Período';
  for (var i = 1; i <= n; i++) {
    var o = document.createElement('option');
    o.value = i - 1;
    o.textContent = nome + ' ' + i;
    sel.appendChild(o);
  }
}

function cpLoadDiscVocab() {
  var disc = document.getElementById('cp-discSelect').value;
  if (!disc) { document.getElementById('cp-vocabCount').textContent = '0'; document.getElementById('cp-vocabTags').innerHTML = ''; cpDiscVocab = []; return; }

  var words = [];

  // 1. Base vocab for this discipline
  if (cpDiscVocabBase[disc]) {
    words = words.concat(cpDiscVocabBase[disc]);
  }

  // 2. Try to read from PLANO_HISTORIA6 for 6th grade history
  if (disc === 'historia6') {
    try {
      if (typeof PLANO_HISTORIA6 !== 'undefined' && PLANO_HISTORIA6.trimestres) {
        PLANO_HISTORIA6.trimestres.forEach(function(t) {
          if (t.topicos && t.topicos.length) {
            t.topicos.forEach(function(tp) {
              // Convert topic to uppercase, remove accents for grid
              var clean = tp.toUpperCase().replace(/[^A-ZÀ-Ÿ]/g, '').replace(/ /g,'');
              if (clean.length > 2 && words.indexOf(clean) < 0) words.push(clean);
            });
          }
        });
      }
    } catch(e) { console.warn('PLANO_HISTORIA6 error:', e); }
  }

  // 3. Try to read from contentTopics (user-entered topics)
  try {
    if (typeof contentTopics !== 'undefined') {
      for (var k in contentTopics) {
        if (contentTopics.hasOwnProperty(k) && Array.isArray(contentTopics[k])) {
          contentTopics[k].forEach(function(tp) {
            var clean = tp.toUpperCase().replace(/[^A-ZÀ-Ÿ]/g, '').replace(/ /g,'');
            if (clean.length > 2 && words.indexOf(clean) < 0) words.push(clean);
          });
        }
      }
    }
  } catch(e) {}

  // 4. Try to extract keywords from BNCC descriptions
  try {
    if (typeof PRESETS !== 'undefined' && PRESETS[disc] && PRESETS[disc].bnccPorPeriodo) {
      var periods = PRESETS[disc].bnccPorPeriodo;
      for (var modelKey in periods) {
        var model = periods[modelKey];
        if (Array.isArray(model)) {
          // BNCC codes like ['EF06HI01', ...] - extract keywords from the code
          model.forEach(function(code) {
            if (typeof code === 'string') {
              // Extract subject keywords from BNCC code pattern
              var parts = code.replace(/[0-9]/g, ' ').split(' ').filter(Boolean);
              parts.forEach(function(p) {
                if (p.length > 2 && words.indexOf(p) < 0) words.push(p);
              });
            }
          });
        }
      }
    }
  } catch(e) {}

  // Deduplicate and limit
  words = words.filter(function(w, i) { return words.indexOf(w) === i; });
  words.sort();

  cpDiscVocab = words;
  document.getElementById('cp-vocabCount').textContent = words.length;

  var tags = document.getElementById('cp-vocabTags');
  tags.innerHTML = words.slice(0, 30).map(function(w) { return '<span class="cp-vocab-tag">' + w + '</span>'; }).join('');
  if (words.length > 30) tags.innerHTML += '<span class="cp-vocab-tag" style="background:rgba(233,69,96,.15);color:var(--cp-accent)">+' + (words.length-30) + ' mais</span>';
}

function cpGenerateFromDisc() {
  if (cpCurrentMode !== 'disc' || cpDiscVocab.length < 3) {
    cpToast('Selecione uma disciplina com pelo menos 3 termos.', 'warn');
    return;
  }

  // Override the current theme dynamically
  var size = 12; // Always use 12x12 for discipline mode
  var selected = cpDiscVocab.slice(0, Math.min(cpDiscVocab.length, size));

  // Build a temporary theme
  var disc = document.getElementById('cp-discSelect').value;
  var discLabel = 'Disciplina';
  try { discLabel = (typeof PRESETS !== 'undefined' && PRESETS[disc]) ? PRESETS[disc].label : disc; } catch(e) {}

  var period = parseInt(document.getElementById('cp-periodSelect').value) + 1;

  cpCurrentTheme = '__disc__';

  // Build grid using the existing cpGenerate logic but with custom words
  cpStopTimer(); cpShowAnswers = false;
  document.getElementById('cp-showBtn').textContent = '👁️ Mostrar';
  cpIsComplete = false; cpFoundWords.clear(); cpSelectedCells = []; cpSeconds = 0;
  document.getElementById('cp-trophy').style.display = 'none';
  document.getElementById('cp-glossary').style.display = 'none';

  var s = size;
  cpGrid = Array.from({length: s}, function() { return Array(s).fill(''); });
  cpWordPositions = {};

  var words = selected;
  var directions = [[0,1],[1,0],[1,1],[-1,1]];
  var placedCount = 0;

  for (var wi = 0; wi < words.length; wi++) {
    var w = words[wi];
    var placed = false;
    for (var attempt = 0; attempt < 200 && !placed; attempt++) {
      var dir = directions[Math.floor(Math.random() * directions.length)];
      var row = Math.floor(Math.random() * s);
      var col = Math.floor(Math.random() * s);
      var dr = dir[0], dc = dir[1];
      var endR = row + dr * (w.length - 1);
      var endC = col + dc * (w.length - 1);
      if (endR < 0 || endR >= s || endC < 0 || endC >= s) continue;
      var ok = true;
      for (var i = 0; i < w.length; i++) {
        var r = row + dr * i, c = col + dc * i;
        if (cpGrid[r][c] && cpGrid[r][c] !== w[i]) { ok = false; break; }
      }
      if (ok) {
        var positions = [];
        for (var i = 0; i < w.length; i++) {
          var r = row + dr * i, c = col + dc * i;
          cpGrid[r][c] = w[i];
          positions.push(r + ',' + c);
        }
        cpWordPositions[w] = positions;
        placed = true;
        placedCount++;
      }
    }
  }

  cpPlacedCount = placedCount;

  // Fill empty cells
  var letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  for (var r = 0; r < s; r++)
    for (var c = 0; c < s; c++)
      if (!cpGrid[r][c]) cpGrid[r][c] = letters[Math.floor(Math.random() * letters.length)];

  // Render
  var gridEl = document.getElementById('cp-grid');
  gridEl.style.gridTemplateColumns = 'repeat(' + s + ', 1fr)';
  gridEl.innerHTML = '';
  for (var r = 0; r < s; r++) {
    for (var c = 0; c < s; c++) {
      var cell = document.createElement('div');
      cell.className = 'cp-cell';
      cell.dataset.r = r; cell.dataset.c = c;
      cell.textContent = cpGrid[r][c];
      cell.onclick = function() { cpCellClick(this); };
      gridEl.appendChild(cell);
    }
  }

  // Update header
  document.querySelector('#jogos .cp-header h2').innerHTML = '🎮 <span style="font-weight:400">Caça-Palavras:</span> ' + discLabel + ' — ' + period + 'º Período';

  // Render word list
  var wordList = document.getElementById('cp-wordList');
  wordList.innerHTML = '<h3>📋 Termos (' + words.length + ')</h3>';
  for (var i = 0; i < words.length; i++) {
    (function(w) {
      var item = document.createElement('div');
      item.className = 'cp-word-item';
      item.dataset.word = w;
      item.innerHTML = '<span class="cp-check"></span><span>' + w + '</span>';
      item.onclick = function() { if (cpFoundWords.has(w)) { cpFocusWord(w); } };
      wordList.appendChild(item);
    })(words[i]);
  }

  cpUpdateStats();
  document.getElementById('cp-progressBar').style.width = '0%';
  cpToast('Caça-Palavras gerado com ' + placedCount + ' termos de ' + discLabel + '!', 'ok');
}

// Override cpGenerate for disc mode
var cpGenerateOriginal = cpGenerate;
cpGenerate = function() {
  if (cpCurrentMode === 'disc') {
    cpGenerateFromDisc();
  } else {
    cpGenerateOriginal();
  }
};
// Override cpLoadTheme for disc mode
var cpLoadThemeOriginal = cpLoadTheme;
cpLoadTheme = function(theme) {
  if (cpCurrentMode === 'disc') {
    cpGenerateFromDisc();
  } else {
    cpLoadThemeOriginal(theme);
  }
};
"""

# ═══════════════════════════════════════════════════════════════
# INJEÇÃO
# ═══════════════════════════════════════════════════════════════

# 1. Inject extra CSS before </style>
idx = html.rfind("</style>")
if idx >= 0:
    html = html[:idx] + extra_css + "\n" + html[idx:]
    print("✅ Extra CSS injected")

# 2. Inject extra HTML after the existing cp-mode-toggle or before cp-header
# Find the cp-header div
idx = html.find('<div class="cp-header">')
if idx >= 0:
    html = html[:idx] + extra_html + "\n" + html[idx:]
    print("✅ Extra HTML injected")

# 3. Inject extra JS before the last } that closes the CP script section
# Find the end of CP JS - look for the last cpToast or cpPrint function
# Actually, inject before the final '// ═══════════════════' or the final document.addEventListener
marker = (
    "if (document.readyState === 'complete' || document.readyState === 'interactive') {"
)
idx = html.find(marker)
if idx >= 0:
    html = html[:idx] + extra_js + "\n\n" + html[idx:]
    print("✅ Extra JS injected")
else:
    # Try alternative: inject before the last </script>
    idx = html.rfind("</script>")
    if idx >= 0:
        html = html[:idx] + extra_js + "\n" + html[idx:]
        print("✅ Extra JS injected (alt method)")

with open(V3_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\n✅ Done! File size: {len(html)} chars")
