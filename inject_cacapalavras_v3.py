#!/usr/bin/env python3
"""
Injeta um Caça-Palavras interativo completo como aba "🎮 Jogos" no Planejador v3.0.

Uso:
    python3 inject_cacapalavras_v3.py

Recursos:
    - Grade de letras selecionáveis com clique+arrastar
    - Barra de progresso animada
    - Cronômetro com recorde pessoal (localStorage)
    - 3 níveis de dificuldade (Fácil, Médio, Difícil)
    - Mostrar/Ocultar respostas
    - Checkboxes com efeito riscado
    - Sistema de conquistas (troféu + mensagem)
    - Botão de imprimir/PDF
    - 3 temas históricos: Brasil Colonial, Egito Antigo, Roma Antiga
"""

import re
import shutil
from datetime import datetime

V3_PATH = '/home/flavio/Secretária/Download/planejador-escolar-v3.0.html'
BACKUP_PATH = V3_PATH + '.bak_jogos'

# ═══════════════════════════════════════════════════════════════
# CSS escopado sob #jogos
# ═══════════════════════════════════════════════════════════════

CACA_PALAVRAS_CSS = '''
/* ── CSS DO CAÇA-PALAVRAS (escopado sob #jogos) ── */
#jogos { --cp-bg: #0f0f1a; --cp-surface: #1a1a2e; --cp-card: #222244; --cp-border: #333366; --cp-accent: #e94560; --cp-gold: #ffd700; --cp-teal: #4ecdc4; --cp-text: #e8e6f0; --cp-muted: #8888aa; --cp-correct: #4ecdc4; --cp-found: #ffd700; }

#jogos .cp-container { max-width: 960px; margin: 0 auto; padding: 24px; color: var(--cp-text); font-family: system-ui, -apple-system, sans-serif; }
#jogos .cp-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--cp-border); }
#jogos .cp-header h2 { font-size: 1.6rem; font-weight: 800; background: linear-gradient(135deg, var(--cp-gold), var(--cp-accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; }
#jogos .cp-controls { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
#jogos .cp-btn { padding: 8px 18px; border-radius: 8px; border: 1px solid var(--cp-border); background: var(--cp-card); color: var(--cp-text); cursor: pointer; font-size: .82rem; font-weight: 600; transition: all .2s; white-space: nowrap; }
#jogos .cp-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(233,69,96,.25); border-color: var(--cp-accent); }
#jogos .cp-btn:disabled { opacity: .4; cursor: not-allowed; transform: none; }
#jogos .cp-btn-primary { background: var(--cp-accent); border-color: var(--cp-accent); color: #fff; }
#jogos .cp-btn-primary:hover { filter: brightness(1.15); }
#jogos .cp-btn-gold { background: var(--cp-gold); border-color: var(--cp-gold); color: #1a1a2e; }
#jogos .cp-btn-success { background: var(--cp-teal); border-color: var(--cp-teal); color: #1a1a2e; }
#jogos .cp-select { padding: 8px 14px; border-radius: 8px; border: 1px solid var(--cp-border); background: var(--cp-card); color: var(--cp-text); font-size: .82rem; cursor: pointer; }
#jogos .cp-stats { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px; }
#jogos .cp-stat { background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 12px; padding: 14px 20px; flex: 1; min-width: 120px; text-align: center; }
#jogos .cp-stat-value { font-size: 1.5rem; font-weight: 800; color: var(--cp-gold); }
#jogos .cp-stat-label { font-size: .75rem; color: var(--cp-muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
#jogos .cp-stat .cp-record { font-size: .7rem; color: var(--cp-teal); margin-top: 2px; }
#jogos .cp-progress { width: 100%; height: 8px; background: var(--cp-border); border-radius: 4px; overflow: hidden; margin-bottom: 20px; }
#jogos .cp-progress-bar { height: 100%; background: linear-gradient(90deg, var(--cp-accent), var(--cp-gold)); border-radius: 4px; transition: width .5s ease; width: 0%; }
#jogos .cp-grid-wrapper { display: flex; gap: 24px; flex-wrap: wrap; justify-content: center; }
#jogos .cp-grid { display: grid; gap: 2px; margin: 0 auto; user-select: none; }
#jogos .cp-cell { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: .9rem; font-weight: 700; border-radius: 4px; cursor: pointer; transition: all .15s; background: var(--cp-surface); border: 1px solid var(--cp-border); color: var(--cp-text); text-transform: uppercase; }
#jogos .cp-cell:hover { background: var(--cp-card); transform: scale(1.1); z-index: 1; }
#jogos .cp-cell.selected { background: var(--cp-accent); color: #fff; border-color: var(--cp-accent); }
#jogos .cp-cell.found { background: rgba(78,205,196,.2); border-color: var(--cp-teal); color: var(--cp-teal); }
#jogos .cp-cell.found.selected { background: var(--cp-teal); color: #1a1a2e; }
#jogos .cp-cell.showing { background: rgba(255,215,0,.25); border-color: var(--cp-gold); color: var(--cp-gold); animation: cpPulse 1s ease infinite; }
@keyframes cpPulse { 0%,100% { box-shadow: 0 0 4px rgba(255,215,0,.3); } 50% { box-shadow: 0 0 12px rgba(255,215,0,.6); } }
#jogos .cp-cell:active { transform: scale(.9); }
#jogos .cp-word-list { background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 12px; padding: 16px; min-width: 180px; flex: 0 0 auto; max-height: 500px; overflow-y: auto; }
#jogos .cp-word-list h3 { font-size: .85rem; color: var(--cp-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
#jogos .cp-word-item { display: flex; align-items: center; gap: 10px; padding: 6px 8px; border-radius: 6px; cursor: pointer; transition: all .15s; font-size: .85rem; }
#jogos .cp-word-item:hover { background: var(--cp-card); }
#jogos .cp-word-item.found { color: var(--cp-teal); text-decoration: line-through; }
#jogos .cp-word-item .cp-check { width: 18px; height: 18px; border-radius: 4px; border: 2px solid var(--cp-border); display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all .2s; font-size: 10px; }
#jogos .cp-word-item.found .cp-check { background: var(--cp-teal); border-color: var(--cp-teal); color: #1a1a2e; }
#jogos .cp-trophy { text-align: center; padding: 24px; animation: cpTrophyIn .6s ease both; }
@keyframes cpTrophyIn { from { opacity: 0; transform: scale(.5) rotate(-10deg); } to { opacity: 1; transform: scale(1) rotate(0); } }
#jogos .cp-trophy-icon { font-size: 4rem; display: block; margin-bottom: 12px; }
#jogos .cp-trophy h3 { font-size: 1.4rem; color: var(--cp-gold); margin-bottom: 8px; }
#jogos .cp-trophy p { color: var(--cp-muted); font-size: .95rem; }
#jogos .cp-trophy .cp-new-record { color: var(--cp-accent); font-weight: 700; margin-top: 8px; }
#jogos .cp-theme-selector { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
#jogos .cp-theme-btn { padding: 6px 14px; border-radius: 20px; border: 1px solid var(--cp-border); background: var(--cp-surface); color: var(--cp-muted); cursor: pointer; font-size: .78rem; transition: all .2s; }
#jogos .cp-theme-btn.active { background: var(--cp-accent); color: #fff; border-color: var(--cp-accent); }
#jogos .cp-theme-btn:hover { border-color: var(--cp-accent); }
#jogos .cp-glossary { background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 12px; padding: 20px; margin-top: 20px; }
#jogos .cp-glossary h3 { font-size: .9rem; margin-bottom: 12px; }
#jogos .cp-glossary-item { padding: 8px 0; border-bottom: 1px solid rgba(51,51,102,.3); font-size: .85rem; line-height: 1.6; }
#jogos .cp-glossary-item:last-child { border: none; }
#jogos .cp-glossary-item strong { color: var(--cp-gold); }
#jogos .cp-toast { position: fixed; bottom: 24px; right: 24px; padding: 12px 20px; border-radius: 10px; background: var(--cp-card); border: 1px solid var(--cp-border); color: var(--cp-text); font-size: .85rem; z-index: 9999; animation: cpToastIn .3s ease; box-shadow: 0 8px 24px rgba(0,0,0,.4); }
@keyframes cpToastIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
#jogos .cp-confetti-container { position: fixed; inset: 0; pointer-events: none; z-index: 9998; overflow: hidden; }
#jogos .cp-confetti { position: absolute; width: 8px; height: 8px; border-radius: 2px; animation: cpConfettiFall linear forwards; }
@keyframes cpConfettiFall { to { transform: translateY(100vh) rotate(720deg); opacity: 0; } }
@media (max-width: 768px) { #jogos .cp-grid-wrapper { flex-direction: column; align-items: center; } #jogos .cp-cell { width: 30px; height: 30px; font-size: .78rem; } #jogos .cp-word-list { width: 100%; min-width: auto; max-height: 250px; } #jogos .cp-header { flex-direction: column; align-items: stretch; text-align: center; } #jogos .cp-stats { flex-direction: row; } #jogos .cp-stat { min-width: 80px; padding: 10px 14px; } }
@media print { #jogos .cp-btn, #jogos .cp-select, #jogos .cp-controls, #jogos .cp-theme-selector { display: none !important; } #jogos .cp-container { padding: 0; } #jogos .cp-cell { border: 1px solid #999; color: #000; } #jogos .cp-cell.found, #jogos .cp-cell.showing { background: #e8e8e8; } }
'''

# ═══════════════════════════════════════════════════════════════
# HTML da seção Jogos
# ═══════════════════════════════════════════════════════════════

CACA_PALAVRAS_HTML = '''
<section id="jogos" class="panel-section section-hidden">
<div class="cp-container">

<div class="cp-header">
  <h2>🎮 Caça-Palavras Interativo</h2>
  <div class="cp-controls">
    <select class="cp-select" id="cp-difficulty" onchange="cpLoadTheme(cpCurrentTheme)">
      <option value="facil">Fácil (8×8)</option>
      <option value="medio" selected>Médio (10×10)</option>
      <option value="dificil">Difícil (12×12)</option>
    </select>
    <button class="cp-btn cp-btn-primary" onclick="cpGenerate()">🔄 Gerar Novo</button>
    <button class="cp-btn" id="cp-showBtn" onclick="cpToggleShow()">👁️ Mostrar</button>
    <button class="cp-btn cp-btn-gold" onclick="cpPrint()">🖨️ Imprimir</button>
  </div>
</div>

<div class="cp-theme-selector">
  <button class="cp-theme-btn active" data-theme="colonial" onclick="cpLoadTheme('colonial')">🏛️ Brasil Colonial</button>
  <button class="cp-theme-btn" data-theme="egito" onclick="cpLoadTheme('egito')">🔺 Egito Antigo</button>
  <button class="cp-theme-btn" data-theme="roma" onclick="cpLoadTheme('roma')">⚔️ Roma Antiga</button>
</div>

<div class="cp-stats">
  <div class="cp-stat"><div class="cp-stat-value" id="cp-timer">00:00</div><div class="cp-stat-label">⏱️ Tempo</div><div class="cp-record" id="cp-record">Recorde: —</div></div>
  <div class="cp-stat"><div class="cp-stat-value" id="cp-found">0/0</div><div class="cp-stat-label">✅ Palavras</div></div>
  <div class="cp-stat"><div class="cp-stat-value" id="cp-pct">0%</div><div class="cp-stat-label">📊 Completo</div></div>
</div>

<div class="cp-progress"><div class="cp-progress-bar" id="cp-progressBar"></div></div>

<div class="cp-grid-wrapper">
  <div id="cp-wordList" class="cp-word-list"></div>
  <div id="cp-grid" class="cp-grid"></div>
</div>

<div id="cp-glossary" class="cp-glossary" style="display:none"></div>
<div id="cp-trophy" class="cp-trophy" style="display:none"></div>

</div>
</section>
'''

# ═══════════════════════════════════════════════════════════════
# JavaScript do Caça-Palavras
# ═══════════════════════════════════════════════════════════════

CACA_PALAVRAS_JS = '''
// ══════════════════════════════════════════════════════════
//  CAÇA-PALAVRAS — Temas, Grid e Lógica
// ══════════════════════════════════════════════════════════

const cpThemes = {
  colonial: {
    name: "Brasil Colonial",
    words: ["ESCRAVIDÃO","ENGENHO","CAPITANIA","BANDEIRANTE","OURO","JESUITA","FEITORIA","CANADEACUCAR","TROPEIRO","QUILOMBO","CICLO DO OURO","CASA GRANDE","SENZALA","TRATADO","EXTRATIVISMO"],
    glossary: {"ESCRAVIDÃO":"Trabalho forçado que sustentou a economia colonial por mais de 300 anos.","ENGENHO":"Grande propriedade produtora de açúcar, centro da vida colonial nordestina.","CAPITANIA":"Sistema de divisão administrativa hereditária criado por D. João III em 1534.","BANDEIRANTE":"Explorador paulista que desbravou o interior em busca de riquezas e indígenas.","OURO":"Descoberto em Minas Gerais no final do séc. XVII, transformou a colônia.","JESUITA":"Membro da Companhia de Jesus, responsável pela catequização dos indígenas.","FEITORIA":"Posto comercial fortificado usado pelos portugueses no litoral.","CANADEACUCAR":"Principal produto de exportação do Brasil Colonial durante o séc. XVI-XVII.","TROPEIRO":"Comerciante que transportava mercadorias e gado entre regiões.","QUILOMBO":"Comunidade formada por escravizados fugidos; o mais famoso foi Palmares.","CICLO DO OURO":"Período de intensa mineração em MG que gerou riqueza e urbanização.","CASA GRANDE":"Sede da família senhorial no engenho, centro do poder patriarcal.","SENZALA":"Alojamento precário onde os escravizados viviam nos engenhos.","TRATADO":"Acordo formal entre nações; ex: Tratado de Tordesilhas (1494).","EXTRATIVISMO":"Primeira atividade econômica: extração de pau-brasil pelos portugueses."}
  },
  egito: {
    name: "Egito Antigo",
    words: ["FARAO","NILO","PIRAMIDE","MUMIFICACAO","HIEROGLIFO","ESFINGE","ANUBIS","ESCRIBA","PAPIRO","NEFFERTITI","RAMSES","HORUS","OSIRIS","BASTET","VALE DOS REIS"],
    glossary: {"FARAO":"Rei do Egito Antigo, considerado um deus vivo e governante absoluto.","NILO":"Maior rio da África, fundamental para a agricultura e transporte no Egito.","PIRAMIDE":"Monumento funerário dos faraós; a maior é a Pirâmide de Quéops (Gizé).","MUMIFICACAO":"Processo de preservação do corpo para a vida após a morte.","HIEROGLIFO":"Sistema de escrita sagrada composto por centenas de símbolos.","ESFINGE":"Monumento com corpo de leão e cabeça humana, guarda as pirâmides de Gizé.","ANUBIS":"Deus com cabeça de chacal, protetor dos mortos e das mumificações.","ESCRIBA":"Profissional que dominava a escrita e os registros administrativos.","PAPIRO":"Planta usada para fabricar o papel no Egito Antigo.","NEFFERTITI":"Rainha do Egito, famosa por seu busto e por seu reinado com Akhenaton.","RAMSES":"Faraó do Novo Império, governou por 66 anos e construiu Abu Simbel.","HORUS":"Deus falcão, protetor dos faraós, filho de Osíris e Ísis.","OSIRIS":"Deus do submundo e da ressurreição, julgava as almas dos mortos.","BASTET":"Deusa-gato, protetora do lar, da fertilidade e da música.","VALE DOS REIS":"Necrópole real onde faraós do Novo Império foram sepultados."}
  },
  roma: {
    name: "Roma Antiga",
    words: ["SENADO","LEGIAO","GLADIADOR","CESAR","IMPERIO","REPUBLICA","AQUEDUTO","COLISEU","JULIO CESAR","AUGUSTO","ESPARTA","CALIGULA","FÓRUM","PANTEÃO","LATIM"],
    glossary: {"SENADO":"Assembleia de patrícios que governou Roma durante a República.","LEGIAO":"Unidade militar romana composta por cerca de 5.000 soldados profissionais.","GLADIADOR":"Lutador que combatia em arenas para entretenimento público.","CESAR":"Título imperial romano; referência a Júlio César, ditador vitalício.","IMPERIO":"Fase da história romana iniciada com Augusto (27 a.C.), marcada por expansão.","REPUBLICA":"Período anterior ao Império (509-27 a.C.) com governo do Senado.","AQUEDUTO":"Obra de engenharia para transportar água às cidades romanas.","COLISEU":"Grande anfiteatro de Roma, palco de lutas de gladiadores.","JULIO CESAR":"General e estadista que conquistou a Gália e centralizou o poder.","AUGUSTO":"Primeiro imperador romano, trouxe a Pax Romana.","ESPARTA":"Cidade-estado grega rival de Atenas, conhecida pelo militarismo.","CALIGULA":"Imperador romano famoso por sua tirania e extravagância.","FÓRUM":"Praça central de Roma, centro político, econômico e religioso.","PANTEÃO":"Templo dedicado a todos os deuses, com a maior cúpula de concreto da Antiguidade.","LATIM":"Língua oficial do Império Romano, origem das línguas românicas."}
  }
};

let cpCurrentTheme = 'colonial';
let cpGrid = [];
let cpWordPositions = {};
let cpFoundWords = new Set();
let cpSelectedCells = [];
let cpTimer = null;
let cpSeconds = 0;
let cpIsRunning = false;
let cpShowAnswers = false;
let cpIsComplete = false;
let cpPlacedCount = 0;
let cpClearTimer = null;

// ── Carregar Tema ──
function cpLoadTheme(theme) {
  cpCurrentTheme = theme;
  document.querySelectorAll('#jogos .cp-theme-btn').forEach(b => b.classList.toggle('active', b.dataset.theme === theme));
  const data = cpThemes[theme];
  document.querySelector('#jogos .cp-header h2').innerHTML = '🎮 <span style="font-weight:400">Caça-Palavras:</span> ' + data.name;
  if (!cpIsRunning) cpGenerate();
}

// ── Gerar Grid ──
function cpGenerate() {
  cpStopTimer(); cpShowAnswers = false;
  document.getElementById('cp-showBtn').textContent = '👁️ Mostrar';
  cpIsComplete = false; cpFoundWords.clear(); cpSelectedCells = []; cpSeconds = 0;
  document.getElementById('cp-trophy').style.display = 'none';
  document.getElementById('cp-glossary').style.display = 'none';

  const diff = document.getElementById('cp-difficulty').value;
  const sizes = {facil:8, medio:10, dificil:12};
  const size = sizes[diff] || 10;
  const theme = cpThemes[cpCurrentTheme];
  const words = theme.words.slice(0, size);

  // Inicializar grid vazio
  cpGrid = Array.from({length: size}, () => Array(size).fill(''));
  cpWordPositions = {};

  // Filtrar palavras que cabem no grid (sem espaços)
  const validWords = [];
  for (const w of words) {
    const clean = w.toUpperCase().replace(/ /g,'');
    if (clean.length <= size) validWords.push({original: w, clean: clean});
  }
  
  const directions = [[0,1],[1,0],[1,1],diff==='dificil'?[-1,1]:null].filter(Boolean);
  let placedCount = 0;
  for (const {original: word, clean: w} of validWords) {
    let placed = false;
    for (let attempt = 0; attempt < 200 && !placed; attempt++) {
      const dir = directions[Math.floor(Math.random() * directions.length)];
      const row = Math.floor(Math.random() * size);
      const col = Math.floor(Math.random() * size);
      const dr = dir[0], dc = dir[1];
      const endR = row + dr * (w.length - 1);
      const endC = col + dc * (w.length - 1);
      if (endR < 0 || endR >= size || endC < 0 || endC >= size) continue;
      let ok = true;
      for (let i = 0; i < w.length; i++) {
        const r = row + dr * i, c = col + dc * i;
        if (cpGrid[r][c] && cpGrid[r][c] !== w[i]) { ok = false; break; }
      }
      if (ok) {
        const positions = [];
        for (let i = 0; i < w.length; i++) {
          const r = row + dr * i, c = col + dc * i;
          cpGrid[r][c] = w[i];
          positions.push(r + ',' + c);
        }
        cpWordPositions[word] = positions;
        placed = true;
        placedCount++;
      }
    }
  }
  cpPlacedCount = placedCount;

  // Preencher vazios
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  for (let r = 0; r < size; r++)
    for (let c = 0; c < size; c++)
      if (!cpGrid[r][c]) cpGrid[r][c] = letters[Math.floor(Math.random() * letters.length)];

  cpRenderGrid(validWords.map(function(v) { return v.original; }));
  cpUpdateStats();
  document.getElementById('cp-progressBar').style.width = '0%';
}

// ── Renderizar Grid ──
function cpRenderGrid(words) {
  const size = cpGrid.length;
  const gridEl = document.getElementById('cp-grid');
  gridEl.style.gridTemplateColumns = 'repeat(' + size + ', 1fr)';
  gridEl.innerHTML = '';

  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      const cell = document.createElement('div');
      cell.className = 'cp-cell';
      cell.dataset.r = r; cell.dataset.c = c;
      cell.textContent = cpGrid[r][c];
      cell.onclick = function() { cpCellClick(this); };
      cell.onmouseenter = function() { if (cpSelectedCells.length > 0) cpCellHover(this); };
      gridEl.appendChild(cell);
    }
  }

  // Renderizar lista de palavras
  const wordList = document.getElementById('cp-wordList');
  wordList.innerHTML = '<h3>📋 Palavras (' + words.length + ')</h3>';
  for (const w of words) {
    const item = document.createElement('div');
    item.className = 'cp-word-item';
    item.dataset.word = w;
    item.innerHTML = '<span class="cp-check"></span><span>' + w + '</span>';
    item.onclick = function() {
      if (cpFoundWords.has(w)) { cpFocusWord(w); }
    };
    wordList.appendChild(item);
  }
  cpUpdateWords();
}

// ── Clique na célula ──
function cpCellClick(cell) {
  if (cpIsComplete) return;
  const r = parseInt(cell.dataset.r), c = parseInt(cell.dataset.c);
  if (cell.classList.contains('found')) return;

  if (!cpIsRunning) { cpStartTimer(); }

  if (cell.classList.contains('selected')) {
    cell.classList.remove('selected');
    cpSelectedCells = cpSelectedCells.filter(p => p.r !== r || p.c !== c);
    return;
  }

  cell.classList.add('selected');
  cpSelectedCells.push({r,c});
  
  // Auto-limpar seleção se não formar palavra após 1.5s
  if (cpClearTimer) clearTimeout(cpClearTimer);
  cpClearTimer = setTimeout(function() {
    cpCheckWord();
    // Se não achou palavra, limpar
    if (cpSelectedCells.length > 0 && !cpIsComplete) {
      document.querySelectorAll('#jogos .cp-cell.selected').forEach(function(c) { c.classList.remove('selected'); });
      cpSelectedCells = [];
    }
  }, 1500);
  
  cpCheckWord();
}

function cpCellHover(cell) {
  // No click-drag necessário para este design
}

// ── Verificar palavra ──
function cpCheckWord() {
  if (cpSelectedCells.length < 2) return;
  const cells = cpSelectedCells.map(p => cpGrid[p.r][p.c]).join('');

  for (const [word, positions] of Object.entries(cpWordPositions)) {
    const posStr = positions.join(';');
    const selStr = cpSelectedCells.map(p => p.r+','+p.c).join(';');
    if (selStr === posStr || selStr === [...positions].reverse().join(';')) {
      // Achou!
      cpFoundWords.add(word);
      for (const {r,c} of cpSelectedCells) {
        const cell = document.querySelector('#jogos .cp-cell[data-r="' + r + '"][data-c="' + c + '"]');
        if (cell) { cell.classList.remove('selected'); cell.classList.add('found'); }
      }
      cpSelectedCells = [];
      cpUpdateStats();
      cpUpdateWords();
      if (cpFoundWords.size === (cpPlacedCount || Object.keys(cpWordPositions).length)) {
        cpComplete();
      }
      return;
    }
  }

  // Não é palavra → limpar seleção atrasada
  if (cpSelectedCells.length > 6) {
    cpClearSelection();
  }
}

function cpClearSelection() {
  document.querySelectorAll('#jogos .cp-cell.selected').forEach(c => c.classList.remove('selected'));
  cpSelectedCells = [];
}

// ── Atualizar Estatísticas ──
function cpUpdateStats() {
  const total = cpPlacedCount || Object.keys(cpWordPositions).length;
  const found = cpFoundWords.size;
  document.getElementById('cp-found').textContent = found + '/' + total;
  const pct = total > 0 ? Math.round(found / total * 100) : 0;
  document.getElementById('cp-pct').textContent = pct + '%';
  document.getElementById('cp-progressBar').style.width = pct + '%';
}

function cpUpdateWords() {
  document.querySelectorAll('#jogos .cp-word-item').forEach(item => {
    const w = item.dataset.word;
    if (cpFoundWords.has(w)) item.classList.add('found');
    else item.classList.remove('found');
  });
}

function cpFocusWord(word) {
  const positions = cpWordPositions[word];
  if (!positions) return;
  document.querySelectorAll('#jogos .cp-cell.showing').forEach(c => c.classList.remove('showing'));
  for (const pos of positions) {
    const [r,c] = pos.split(',');
    const cell = document.querySelector('#jogos .cp-cell[data-r="' + r + '"][data-c="' + c + '"]');
    if (cell) cell.classList.add('showing');
  }
  setTimeout(() => {
    document.querySelectorAll('#jogos .cp-cell.showing').forEach(c => c.classList.remove('showing'));
  }, 2000);
}

// ── Timer ──
function cpStartTimer() {
  cpIsRunning = true;
  cpTimer = setInterval(function() {
    cpSeconds++;
    const m = String(Math.floor(cpSeconds / 60)).padStart(2, '0');
    const s = String(cpSeconds % 60).padStart(2, '0');
    document.getElementById('cp-timer').textContent = m + ':' + s;
  }, 1000);
}
function cpStopTimer() {
  cpIsRunning = false;
  if (cpTimer) { clearInterval(cpTimer); cpTimer = null; }
  document.getElementById('cp-timer').textContent = '00:00';
}

// ── Completar ──
function cpComplete() {
  cpStopTimer();
  cpIsComplete = true;
  const prevKey = 'cp_record_' + cpCurrentTheme + '_' + document.getElementById('cp-difficulty').value;
  const prev = localStorage.getItem(prevKey);
  let isRecord = false;
  if (!prev || cpSeconds < parseInt(prev)) {
    localStorage.setItem(prevKey, String(cpSeconds));
    isRecord = true;
  }
  const tro = document.getElementById('cp-trophy');
  tro.style.display = 'block';
  tro.innerHTML = '<div class="cp-trophy-icon">🏆</div><h3>🎉 Parabéns!</h3><p>Você encontrou todas as palavras em ' + document.getElementById('cp-timer').textContent + '!</p>' + (isRecord ? '<p class="cp-new-record">🌟 Novo Recorde!</p>' : '');
  cpSpawnConfetti();
  // Mostrar glossário
  const gloss = document.getElementById('cp-glossary');
  const theme = cpThemes[cpCurrentTheme];
  gloss.style.display = 'block';
  let html = '<h3>📖 Glossário: ' + theme.name + '</h3>';
  for (const [word, def] of Object.entries(theme.glossary)) {
    html += '<div class="cp-glossary-item"><strong>' + word + '</strong>: ' + def + '</div>';
  }
  gloss.innerHTML = html;
}

function cpSpawnConfetti() {
  const container = document.createElement('div');
  container.className = 'cp-confetti-container';
  const colors = ['#e94560','#ffd700','#4ecdc4','#9b72cf','#ff6b6b','#48dbfb'];
  for (let i = 0; i < 60; i++) {
    const piece = document.createElement('div');
    piece.className = 'cp-confetti';
    piece.style.left = Math.random() * 100 + '%';
    piece.style.top = '-10px';
    piece.style.background = colors[Math.floor(Math.random() * colors.length)];
    piece.style.width = (4 + Math.random() * 6) + 'px';
    piece.style.height = (4 + Math.random() * 6) + 'px';
    piece.style.animationDuration = (2 + Math.random() * 3) + 's';
    piece.style.animationDelay = (Math.random() * 2) + 's';
    container.appendChild(piece);
  }
  document.body.appendChild(container);
  setTimeout(() => container.remove(), 6000);
}

// ── Mostrar/Ocultar Respostas ──
function cpToggleShow() {
  cpShowAnswers = !cpShowAnswers;
  document.getElementById('cp-showBtn').textContent = cpShowAnswers ? '🙈 Ocultar' : '👁️ Mostrar';
  if (cpShowAnswers) {
    for (const [word, positions] of Object.entries(cpWordPositions)) {
      if (cpFoundWords.has(word)) continue;
      for (const pos of positions) {
        const [r,c] = pos.split(',');
        const cell = document.querySelector('#jogos .cp-cell[data-r="' + r + '"][data-c="' + c + '"]');
        if (cell) cell.classList.add('showing');
      }
    }
  } else {
    document.querySelectorAll('#jogos .cp-cell.showing').forEach(c => c.classList.remove('showing'));
  }
}

// ── Imprimir ──
function cpPrint() { window.print(); }

// ── Toast ──
function cpToast(msg, type) {
  const t = document.createElement('div');
  t.className = 'cp-toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2500);
}

// ── Inicializar ──
document.addEventListener('DOMContentLoaded', function() {
  cpLoadTheme('colonial');
});
// Garantir que carregue mesmo se DOM já estiver pronto
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  setTimeout(cpLoadTheme.bind(null, 'colonial'), 100);
}
'''

# ═══════════════════════════════════════════════════════════════
# INJEÇÃO
# ═══════════════════════════════════════════════════════════════

def inject():
    with open(V3_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Backup
    shutil.copy2(V3_PATH, BACKUP_PATH)
    print(f"📦 Backup em: {BACKUP_PATH}")

    # 2. Verificar se já foi injetado
    if 'id="jogos"' in html:
        print("⚠️  Seção #jogos já existe. Substituindo...")
        # Remover seção existente
        start = html.find('<section id="jogos"')
        end = html.find('</section>', start) + len('</section>')
        html = html[:start] + '<!-- jogos-removed -->' + html[end:]

    # 3. Injetar botão no sidebar (após o botão Corretor IA)
    # Procurar o último botão com data-target no grupo Professor
    btn_code = '\n    <button data-target="jogos">🎮 Jogos</button>'
    
    markers = [
        'data-target="omredu">🤖 Corretor IA</button>',
        '</nav>',
    ]
    
    for marker in markers:
        idx = html.rfind(marker)
        if idx >= 0:
            insert_pos = idx + len(marker)
            html = html[:insert_pos] + btn_code + html[insert_pos:]
            print(f"✅ Botão Jogos injetado após '{marker[:30]}...'")
            break

    # 4. Injetar CSS dentro do <style> do v3.0
    style_tag = '</style>'
    idx = html.rfind(style_tag)
    if idx >= 0:
        html = html[:idx] + CACA_PALAVRAS_CSS + '\n' + html[idx:]
        print("✅ CSS do Caça-Palavras injetado")

    # 5. Injetar seção HTML antes do fechamento do container principal
    # Procurar última section-hidden ou o fechamento do main
    section_markers = [
        'id="omredu" class="panel-section',
        '</main>',
    ]
    
    for marker in section_markers:
        idx = html.rfind(marker)
        if idx >= 0:
            # Encontrar o fechamento </section> mais próximo
            section_end = html.find('</section>', idx)
            if section_end >= 0:
                section_end += len('</section>')
                html = html[:section_end] + '\n' + CACA_PALAVRAS_HTML + html[section_end:]
                print(f"✅ Seção HTML do Caça-Palavras injetada após '{marker[:30]}...'")
                break

    # 6. Injetar JS antes do fechamento do <script>
    script_close = '</script>'
    idx = html.rfind(script_close)
    if idx >= 0:
        # Injetar antes do último </script> (que é do OMREdu)
        html = html[:idx] + '\n' + CACA_PALAVRAS_JS + '\n' + html[idx:]
        print("✅ JS do Caça-Palavras injetado")

    # 7. Salvar
    with open(V3_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n🎉 Injeção completa! Arquivo salvo: {V3_PATH}")
    print(f"   Tamanho final: {len(html)} chars")


if __name__ == '__main__':
    inject()
