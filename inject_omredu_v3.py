#!/usr/bin/env python3
"""Injeta o Corretor OMREdu (Claude Vision) no Planejador Escolar v3.0."""

import re

V3_PATH = "/home/flavio/Secretária/Download/planejador-escolar-v3.0.html"
BACKUP_PATH = V3_PATH + ".bak"
OMREDU_PATH = "/home/flavio/OpenManus/omredu_corretor_gabaritos.html"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def extract_omredu_js():
    """Extrai o JS do OMREdu, removendo funções que conflitam com o v3.0."""
    html = read_file(OMREDU_PATH)
    # Extrair o JS do bloco <script>
    match = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
    if not match:
        raise RuntimeError("Não encontrou <script> no OMREdu")
    js = match.group(1)

    # Manter apenas as funções específicas do OMREdu
    # Remover a função showAlert (apoia em console.warn) - vamos adaptar
    return js

def build_nav_button():
    return '''    <button data-target="omredu">🤖 Corretor IA</button>\n'''

def build_section():
    """Cria a seção OMREdu para inserir no v3.0."""
    section = '''<!-- OMREdu: Corretor de Gabaritos com IA -->
<section id="omredu" class="panel-section section-hidden" aria-label="Corretor de gabaritos com IA">
  <div class="card" style="max-width:100%;overflow:visible">
    <div class="card-hd">
      <div>
        <span class="ai-badge">✨ Claude Vision</span>
        <h3 style="margin:0">Corretor de Gabaritos IA</h3>
      </div>
    </div>
    <p class="desc">Corrija provas automaticamente com IA: fotografe o cartão-resposta e obtenha acertos/erros por questão com indicador de confiança.</p>

    <div style="display:grid;grid-template-columns:380px 1fr;gap:1.25rem;align-items:start">
      <!-- COLUNA ESQUERDA: CONFIG -->
      <div style="display:flex;flex-direction:column;gap:1rem">

        <!-- DADOS DO ALUNO -->
        <div class="prova-cfg" style="margin:0">
          <p class="prova-cfg-title">👤 Dados do Aluno</p>
          <div class="g2">
            <label>Nome<input type="text" id="omr-alunoNome" placeholder="Ex: Maria Silva"/></label>
            <label>Turma<input type="text" id="omr-alunoTurma" placeholder="Ex: 8º A"/></label>
          </div>
          <label style="margin-top:.5rem">Nº Questões
            <select id="omr-numQuestoes" onchange="omrRenderGabarito()">
              <option value="5">5</option><option value="10" selected>10</option>
              <option value="15">15</option><option value="20">20</option>
              <option value="25">25</option><option value="30">30</option>
            </select>
          </label>
        </div>

        <!-- GABARITO -->
        <div class="prova-cfg" style="margin:0">
          <p class="prova-cfg-title">📋 Gabarito Oficial</p>
          <div class="omr-gab-grid" id="omr-gabaritoGrid"></div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:.6rem">
            <button class="btn bs bsm" onclick="omrFillAll('A')">Tudo A</button>
            <button class="btn bs bsm" onclick="omrFillAll('B')">Tudo B</button>
            <button class="btn bs bsm" onclick="omrFillAll('C')">Tudo C</button>
            <button class="btn bs bsm" onclick="omrClearGab()">Limpar</button>
          </div>
        </div>

        <!-- IMAGEM -->
        <div class="prova-cfg" style="margin:0">
          <p class="prova-cfg-title">📷 Imagem do Cartão</p>
          <div style="display:flex;gap:4px;margin-bottom:.6rem">
            <button class="btn bs bsm omr-tab-btn active" onclick="omrSwitchTab('upload',this)">Upload</button>
            <button class="btn bs bsm omr-tab-btn" onclick="omrSwitchTab('camera',this)">Câmera</button>
          </div>
          <div id="omr-tab-upload">              <div class="omr-upload-area" id="omr-uploadArea"
                   ondragover="event.preventDefault();this.classList.add('omr-drag')"
                   ondragleave="this.classList.remove('omr-drag')"
                   ondrop="event.preventDefault();this.classList.remove('omr-drag');omrHandleDrop(event)">
              <input type="file" id="omr-fileInput" accept="image/*" onchange="omrHandleFile(event)" style="position:absolute;inset:0;opacity:0;cursor:pointer"/>
              <div style="font-size:2rem;margin-bottom:.5rem">🗂️</div>
              <div style="font-size:.85rem;color:var(--mu)">Arraste ou clique para selecionar</div>
              <div style="font-size:.7rem;color:var(--mu);margin-top:.2rem">JPG, PNG, WEBP · Máx 10MB</div>
            </div>
          </div>
          <div id="omr-tab-camera" style="display:none">
            <div id="omr-cameraStart" style="text-align:center;padding:1rem 0">
              <div style="font-size:1.8rem;margin-bottom:.3rem">📸</div>
              <button class="btn bs bsm" onclick="omrStartCamera()">Abrir Câmera</button>
            </div>
            <div id="omr-cameraWrap" style="display:none;background:#000;border-radius:var(--rmd);overflow:hidden">
              <video id="omr-video" autoplay playsinline style="width:100%;display:block"></video>
            </div>
            <div id="omr-cameraControls" style="display:none;margin-top:.5rem">
              <div style="display:flex;gap:6px">
                <button class="btn bp bsm" style="flex:1" onclick="omrCapturePhoto()">📸 Capturar</button>
                <button class="btn bs bsm" onclick="omrStopCamera()">✕ Fechar</button>
              </div>
            </div>
          </div>
          <div id="omr-previewWrap" style="display:none;margin-top:.6rem">
            <div style="position:relative;border-radius:var(--rmd);overflow:hidden;border:1px solid var(--bd)">
              <img id="omr-preview" src="" alt="Preview" style="width:100%;max-height:250px;object-fit:contain;background:#000;display:block"/>
              <div style="position:absolute;top:6px;right:6px">
                <button class="btn bs bsm" onclick="omrClearImage()" style="font-size:.7rem;padding:.2rem .5rem">✕</button>
              </div>
            </div>
          </div>
          <canvas id="omr-captureCanvas" style="display:none"></canvas>
        </div>

        <!-- BOTÃO ANALISAR -->
        <button class="btn bp" id="omr-btnAnalisar" onclick="omrAnalisar()" disabled style="width:100%">
          ✨ Analisar com IA
        </button>

      </div>

      <!-- COLUNA DIREITA: RESULTADOS -->
      <div style="display:flex;flex-direction:column;gap:1rem">

        <!-- RESULTADO -->
        <div class="card" style="margin:0">
          <div class="card-hd">
            <h3 style="margin:0">Resultado</h3>
            <div id="omr-qualidadeBadge"></div>
          </div>
          <div id="omr-resultadoPanel">
            <!-- LOADING -->
            <div id="omr-loading" style="display:none;text-align:center;padding:2rem">
              <div style="width:36px;height:36px;border:3px solid var(--bd);border-top-color:var(--pr);border-radius:50%;animation:omrSpin .8s linear infinite;margin:0 auto .8rem"></div>
              <div style="font-size:.85rem;color:var(--mu)">Analisando cartão-resposta...</div>
              <div style="font-size:.7rem;color:var(--mu);margin-top:.5rem">
                <div id="omr-step1">⚡ Enviando imagem para Claude Vision</div>
                <div id="omr-step2" style="opacity:.4">⏳ Identificando marcações</div>
                <div id="omr-step3" style="opacity:.4">⏳ Calculando resultado</div>
              </div>
            </div>

            <!-- EMPTY -->
            <div id="omr-emptyState" style="text-align:center;padding:2.5rem 1rem">
              <div style="font-size:2.5rem;opacity:.3;margin-bottom:.5rem">🎯</div>
              <div style="color:var(--mu);font-size:.85rem">Configure o gabarito, carregue a imagem<br>e clique em <strong>Analisar com IA</strong></div>
            </div>

            <!-- RESULTADO CONTEUDO -->
            <div id="omr-resultadoContent" style="display:none">
              <div id="omr-alunoInfo" class="omr-aluno-info" style="display:none"></div>
              <div id="omr-alertBox"></div>

              <div class="summary" style="margin-bottom:1rem">
                <div class="stat"><strong id="omr-scoreAcertos" style="color:var(--ok)">—</strong><span>Acertos</span></div>
                <div class="stat"><strong id="omr-scoreErros" style="color:var(--wa)">—</strong><span>Erros</span></div>
                <div class="stat"><strong id="omr-scorePct" style="color:var(--pr)">—</strong><span>Aproveit.</span></div>
                <div class="stat"><strong id="omr-scoreNulas" style="color:var(--mu)">—</strong><span>Nulas</span></div>
              </div>

              <div style="background:var(--sf2);border-radius:var(--rf);height:7px;overflow:hidden;margin-bottom:1rem">
                <div id="omr-progressBar" style="height:100%;background:linear-gradient(90deg,var(--ok),var(--pr));border-radius:var(--rf);transition:width .6s;width:0%"></div>
              </div>

              <p style="font-size:.7rem;font-weight:700;color:var(--mu);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.6rem">Questão a questão</p>
              <div class="omr-q-grid" id="omr-questoesTable"></div>

              <div id="omr-obsWrap" style="display:none;margin-top:1rem">
                <div style="background:var(--sf2);border:1px solid var(--bd);border-radius:var(--rmd);padding:.75rem 1rem;font-size:.82rem;color:var(--mu);line-height:1.6">
                  <p style="font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--mu);margin-bottom:.3rem">Observações da IA</p>
                  <span id="omr-obsText"></span>
                </div>
              </div>

              <div class="acts" style="margin-top:.8rem">
                <button class="btn bs bsm" onclick="omrCopiarResultado()">📋 Copiar</button>
                <button class="btn bs bsm" onclick="omrExportarCSV()">⬇ CSV</button>
                <button class="btn bs bsm" onclick="omrNovaAnalise()">🔄 Nova</button>
              </div>
            </div>
          </div>
        </div>

        <!-- HISTÓRICO -->
        <div class="card" style="margin:0">
          <div class="card-hd">
            <h3 style="margin:0">Histórico da Sessão</h3>
            <button class="btn bs bsm" onclick="omrLimparHistorico()">Limpar</button>
          </div>
          <div id="omr-historyList" style="display:flex;flex-direction:column;gap:.4rem">
            <div style="text-align:center;padding:1.5rem;color:var(--mu);font-size:.8rem">Nenhuma análise ainda</div>
          </div>
        </div>

      </div>
    </div>
  </div>
</section>
'''
    return section

def build_omr_css():
    """Gera CSS específico para o OMREdu integrado."""
    return '''
/* ── OMR: CORRETOR DE GABARITOS ── */
#omredu .prova-cfg { background: var(--sf2); border: 1px solid var(--bd); border-radius: var(--rmd); padding: var(--s4); margin: 0; }
#omredu .omr-gab-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 5px; margin-top: .3rem; }
#omredu .omr-gab-grid select { width: 100%; padding: .3rem .1rem; font-size: .78rem; text-align: center; font-family: monospace; }
#omredu .omr-upload-area { position: relative; border: 2px dashed var(--bd); border-radius: var(--rmd); padding: 1.5rem; text-align: center; cursor: pointer; transition: all .2s; }
#omredu .omr-upload-area:hover { border-color: var(--pr); background: rgba(1,105,111,.04); }
#omredu .omr-upload-area.omr-drag { border-color: var(--pr); background: rgba(1,105,111,.06); }
#omredu .omr-tab-btn.on { background: var(--prs); border-color: var(--pr); color: var(--pr); }
#omredu .omr-q-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(110px,1fr)); gap: 6px; }
#omredu .omr-q-card { background: var(--sf2); border: 1px solid var(--bd); border-radius: var(--rmd); padding: .6rem; display: flex; flex-direction: column; align-items: center; gap: 4px; position: relative; }
#omredu .omr-q-card.acerto { border-color: rgba(67,122,34,.3); background: rgba(67,122,34,.05); }
#omredu .omr-q-card.erro { border-color: rgba(150,66,25,.3); background: rgba(150,66,25,.05); }
#omredu .omr-q-card.nula { border-color: rgba(107,107,107,.3); background: rgba(107,107,107,.05); }
#omredu .omr-q-num { font-size: .6rem; color: var(--mu); text-transform: uppercase; letter-spacing: .08em; }
#omredu .omr-alt { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: .75rem; font-weight: 700; }
#omredu .omr-alt-certo { background: var(--ok); color: #fff; }
#omredu .omr-alt-errado { background: var(--wa); color: #fff; }
#omredu .omr-alt-gabarito { background: rgba(1,105,111,.12); color: var(--pr); border: 1px solid rgba(1,105,111,.3); }
#omredu .omr-alt-nulo { background: rgba(107,107,107,.12); color: var(--mu); }
#omredu .omr-q-status { position: absolute; top: 3px; right: 4px; font-size: .65rem; }
#omredu .omr-aluno-info { display: flex; align-items: center; gap: 10px; padding: .75rem 1rem; background: var(--sf2); border: 1px solid var(--bd); border-radius: var(--rmd); margin-bottom: 1rem; }
#omredu .omr-aluno-avatar { width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg,var(--pr),var(--pu)); display: flex; align-items: center; justify-content: center; font-size: .85rem; font-weight: 800; color: #fff; flex-shrink: 0; }
@keyframes omrSpin { to { transform: rotate(360deg); } }
@media(max-width:880px){#omredu .prova-cfg > div[style*="grid-template-columns: 380px"] { grid-template-columns: 1fr !important; }}
'''

def build_omr_js():
    """Gera o JavaScript adaptado do OMREdu."""
    return '''
/* ============================================
   OMR EDU — CORRETOR DE GABARITOS (integrado)
   ============================================ */
let omrImageBase64 = null;
let omrResultadoAtual = null;
let omrHistorico = [];
let omrStream = null;

function omrRenderGabarito() {
  const n = parseInt(document.getElementById('omr-numQuestoes').value);
  const grid = document.getElementById('omr-gabaritoGrid');
  grid.innerHTML = '';
  for (let i = 1; i <= n; i++) {
    const cell = document.createElement('div');
    cell.style.cssText = 'display:flex;flex-direction:column;align-items:center;gap:2px';
    cell.innerHTML = `<span style="font-size:.6rem;color:var(--mu)">Q${i}</span><select id="omr_gab_${i}" style="width:100%;padding:.25rem .1rem;font-size:.75rem;text-align:center;font-family:monospace"><option value="">—</option><option>A</option><option>B</option><option>C</option><option>D</option><option>E</option></select>`;
    grid.appendChild(cell);
  }
}

function omrFillAll(alt) {
  const n = parseInt(document.getElementById('omr-numQuestoes').value);
  for (let i = 1; i <= n; i++) {
    const el = document.getElementById(`omr_gab_${i}`);
    if (el) el.value = alt;
  }
}

function omrClearGab() {
  const n = parseInt(document.getElementById('omr-numQuestoes').value);
  for (let i = 1; i <= n; i++) {
    const el = document.getElementById(`omr_gab_${i}`);
    if (el) el.value = '';
  }
}

function omrGetGab() {
  const n = parseInt(document.getElementById('omr-numQuestoes').value);
  return Array.from({length: n}, (_, i) => {
    const el = document.getElementById(`omr_gab_${i+1}`);
    return el ? el.value : '';
  });
}

/* ── UPLOAD / CAMERA ── */
function omrSwitchTab(tab, btn) {
  document.querySelectorAll('#omredu .omr-tab-btn').forEach(b => b.classList.remove('active','on'));
  if (btn) btn.classList.add('active','on');
  document.getElementById('omr-tab-upload').style.display = tab === 'upload' ? 'block' : 'none';
  document.getElementById('omr-tab-camera').style.display = tab === 'camera' ? 'block' : 'none';
  if (tab !== 'camera') omrStopCamera();
}

function omrHandleFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  if (file.size > 10 * 1024 * 1024) { omrShowAlert('Arquivo muito grande. Máximo: 10MB','warn'); return; }
  const reader = new FileReader();
  reader.onload = (ev) => {
    omrImageBase64 = ev.target.result;
    omrShowPreview(omrImageBase64);
    document.getElementById('omr-btnAnalisar').disabled = false;
  };
  reader.readAsDataURL(file);
  // Permite selecionar o mesmo arquivo novamente
  e.target.value = '';
}

function omrHandleDrop(e) {
  const file = e.dataTransfer.files[0];
  if (!file || !file.type.startsWith('image/')) return;
  if (file.size > 10 * 1024 * 1024) { omrShowAlert('Arquivo muito grande. Máximo: 10MB','warn'); return; }
  const reader = new FileReader();
  reader.onload = (ev) => {
    omrImageBase64 = ev.target.result;
    omrShowPreview(omrImageBase64);
    document.getElementById('omr-btnAnalisar').disabled = false;
  };
  reader.readAsDataURL(file);
}

function omrShowPreview(src) {
  document.getElementById('omr-preview').src = src;
  document.getElementById('omr-previewWrap').style.display = 'block';
}

function omrClearImage() {
  omrImageBase64 = null;
  document.getElementById('omr-previewWrap').style.display = 'none';
  document.getElementById('omr-preview').src = '';
  document.getElementById('omr-fileInput').value = '';
  document.getElementById('omr-btnAnalisar').disabled = true;
}

async function omrStartCamera() {
  try {
    omrStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 960 } }
    });
    document.getElementById('omr-video').srcObject = omrStream;
    document.getElementById('omr-cameraWrap').style.display = 'block';
    document.getElementById('omr-cameraStart').style.display = 'none';
    document.getElementById('omr-cameraControls').style.display = 'block';
  } catch (err) {
    omrShowAlert('Câmera: ' + err.message, 'error');
  }
}

function omrCapturePhoto() {
  const video = document.getElementById('omr-video');
  const canvas = document.getElementById('omr-captureCanvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  omrImageBase64 = canvas.toDataURL('image/jpeg', 0.9);
  omrShowPreview(omrImageBase64);
  omrStopCamera();
  document.getElementById('omr-btnAnalisar').disabled = false;
  omrSwitchTab('upload', document.querySelector('#omredu .omr-tab-btn'));
}

function omrStopCamera() {
  if (omrStream) { omrStream.getTracks().forEach(t => t.stop()); omrStream = null; }
  document.getElementById('omr-cameraWrap').style.display = 'none';
  document.getElementById('omr-cameraStart').style.display = 'block';
  document.getElementById('omr-cameraControls').style.display = 'none';
}

/* ── ANÁLISE ── */
async function omrAnalisar() {
  if (!omrImageBase64) return;
  const gabarito = omrGetGab();
  const nQ = parseInt(document.getElementById('omr-numQuestoes').value);
  const nome = document.getElementById('omr-alunoNome').value.trim();
  const turma = document.getElementById('omr-alunoTurma').value.trim();

  if (gabarito.every(g => !g)) { omrShowAlert('Preencha pelo menos uma resposta no gabarito.', 'warn'); return; }

  omrSetLoading(true);
  try {
    const json = await omrCallApi(omrImageBase64, gabarito, nQ);
    const res = omrProcessResult(json, gabarito, nome, turma);
    omrResultadoAtual = res;
    omrRenderResult(res);
    omrAdicionarHistorico(res);
  } catch (err) {
    omrSetLoading(false);
    omrShowAlert('Erro: ' + err.message, 'error');
    console.error(err);
  }
}

async function omrCallApi(imgBase64, gabarito, nQ) {
  const prompt = `Você é um sistema especialista em leitura óptica de marcas (OMR) para cartões-resposta escolares.

Analise a imagem do cartão-resposta e identifique as marcações do aluno com precisão máxima.

INSTRUÇÕES:
- Identifique exatamente ${nQ} questões numeradas
- Para cada questão, determine qual alternativa (A, B, C, D ou E)
- Se nenhuma estiver marcada, use null
- Se mais de uma estiver marcada (anulada), use "X"
- A qualidade da imagem pode ser: boa, regular ou ruim

GABARITO OFICIAL: ${gabarito.map((g,i)=>'Q'+(i+1)+'='+(g||'?')).join(', ')}

IMPORTANTE: Responda SOMENTE com JSON válido, sem texto extra, sem markdown.

Formato:
{"questoes":[{"numero":1,"resposta_identificada":"A","confianca":0.95}],"qualidade_imagem":"boa","observacoes_gerais":""}`;

  const imgData = imgBase64.includes(',') ? imgBase64.split(',')[1] : imgBase64;

  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'anthropic-version': '2023-06-01',
      'x-api-key': document.getElementById('apiKeyInput')?.value || getComputedStyle(document.documentElement).getPropertyValue('--api-key').trim() || '',
      'anthropic-dangerous-direct-browser-access': 'true'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{
        role: 'user',
        content: [
          { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: imgData } },
          { type: 'text', text: prompt }
        ]
      }]
    })
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error('API Anthropic: ' + resp.status + ' — ' + (err.error?.message || 'Erro desconhecido'));
  }

  omrSetStep(2);
  const data = await resp.json();
  const raw = data.content.filter(b => b.type === 'text').map(b => b.text).join('');
  const clean = raw.replace(/```json|```/g, '').trim();
  let parsed;
  try { parsed = JSON.parse(clean); } catch { throw new Error('Resposta inválida da IA.'); }
  omrSetStep(3);
  await new Promise(r => setTimeout(r, 300));
  return parsed;
}

function omrProcessResult(json, gabarito, nome, turma) {
  const qs = json.questoes || [];
  let acertos = 0, erros = 0, nulas = 0;
  const detalhes = qs.map((q, i) => {
    const aluno = q.resposta_identificada;
    const correta = gabarito[i] || '';
    let status = 'erro';
    if (!aluno || aluno === null || aluno === 'X') { status = 'nula'; nulas++; }
    else if (correta && aluno === correta) { status = 'acerto'; acertos++; }
    else { erros++; }
    return { numero: q.numero || (i+1), respostaAluno: aluno, respostaCorreta: correta, status, confianca: q.confianca || 0 };
  });
  const total = qs.length;
  return { nomeAluno: nome, turmaAluno: turma, acertos, erros, nulas, total, pct: total > 0 ? Math.round((acertos/total)*100) : 0, detalhes, qualidadeImagem: json.qualidade_imagem || 'desconhecida', observacoesGerais: json.observacoes_gerais || '', timestamp: new Date() };
}

function omrRenderResult(r) {
  omrSetLoading(false);
  document.getElementById('omr-emptyState').style.display = 'none';
  document.getElementById('omr-resultadoContent').style.display = 'block';

  const aInfo = document.getElementById('omr-alunoInfo');
  if (r.nomeAluno || r.turmaAluno) {
    aInfo.style.display = 'flex';
    const inits = (r.nomeAluno||'?').split(' ').map(w=>w[0]).slice(0,2).join('').toUpperCase();
    aInfo.innerHTML = `<div class="omr-aluno-avatar">${inits||'?'}</div><div><div style="font-weight:700;font-size:.88rem">${r.nomeAluno||'Sem nome'}</div><div style="font-size:.68rem;color:var(--mu)">${r.turmaAluno||'Sem turma'}</div></div>`;
  } else { aInfo.style.display = 'none'; }

  document.getElementById('omr-scoreAcertos').textContent = r.acertos;
  document.getElementById('omr-scoreErros').textContent = r.erros;
  document.getElementById('omr-scorePct').textContent = r.pct + '%';
  document.getElementById('omr-scoreNulas').textContent = r.nulas;
  document.getElementById('omr-progressBar').style.width = r.pct + '%';

  const qBadge = document.getElementById('omr-qualidadeBadge');
  const qMap = { boa: ['pk','✓'], regular: ['pa','⚠'], ruim: ['pa','✕'] };
  const [cls, icon] = qMap[r.qualidadeImagem] || ['','?'];
  qBadge.innerHTML = r.qualidadeImagem !== 'desconhecida' ? `<span class="pill ${cls}">${icon} ${r.qualidadeImagem}</span>` : '';

  const alertBox = document.getElementById('omr-alertBox');
  const baixa = r.detalhes.filter(q => q.confianca < 0.7 && q.confianca > 0);
  if (baixa.length > 0) {
    alertBox.innerHTML = `<div class="alert alert-warn" style="margin-bottom:.8rem;font-size:.78rem">⚠ ${baixa.length} questão(ões) com baixa confiança.</div>`;
  } else { alertBox.innerHTML = ''; }

  const table = document.getElementById('omr-questoesTable');
  table.innerHTML = '';
  r.detalhes.forEach(q => {
    const div = document.createElement('div');
    div.className = 'omr-q-card ' + q.status;
    const icon = q.status === 'acerto' ? '✓' : q.status === 'nula' ? '—' : '✕';
    const altCls = q.status === 'acerto' ? 'omr-alt-certo' : q.status === 'nula' ? 'omr-alt-nulo' : 'omr-alt-errado';
    let html = '';
    if (q.respostaAluno && q.respostaAluno !== q.respostaCorreta && q.status !== 'nula') {
      html = `<div style="display:flex;gap:4px;align-items:center"><div class="omr-alt ${altCls}">${q.respostaAluno||'—'}</div><span style="color:var(--mu);font-size:.55rem">→</span><div class="omr-alt omr-alt-gabarito">${q.respostaCorreta||'?'}</div></div>`;
    } else {
      html = `<div class="omr-alt ${altCls}">${q.respostaAluno||'—'}</div>`;
    }
    const pct = q.confianca > 0 ? Math.round(q.confianca*100)+'%' : '';
    div.innerHTML = `<span class="omr-q-status">${icon}</span><span class="omr-q-num">Q${q.numero}</span>${html}${pct ? '<span style="font-size:.55rem;color:var(--mu)">'+pct+'</span>' : ''}`;
    table.appendChild(div);
  });

  const obsWrap = document.getElementById('omr-obsWrap');
  if (r.observacoesGerais) {
    obsWrap.style.display = 'block';
    document.getElementById('omr-obsText').textContent = r.observacoesGerais;
  } else { obsWrap.style.display = 'none'; }
}

function omrAdicionarHistorico(r) {
  omrHistorico.unshift(r);
  omrRenderHistorico();
}

function omrRenderHistorico() {
  const list = document.getElementById('omr-historyList');
  if (omrHistorico.length === 0) {
    list.innerHTML = '<div style="text-align:center;padding:1.5rem;color:var(--mu);font-size:.8rem">Nenhuma análise ainda</div>';
    return;
  }
  list.innerHTML = omrHistorico.map((r,i) => {
    const cor = r.pct >= 70 ? 'var(--ok)' : r.pct >= 50 ? 'var(--wa)' : 'var(--wa)';
    const hora = r.timestamp.toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'});
    return `<div class="omr-hist-item" onclick="omrVerHistorico(${i})" style="display:flex;align-items:center;gap:8px;padding:.55rem .75rem;background:var(--sf2);border:1px solid var(--bd);border-radius:var(--rmd);cursor:pointer;transition:border-color .15s"><div style="font-family:var(--fn);font-size:1rem;font-weight:800;min-width:34px;text-align:center;color:${cor}">${r.pct}%</div><div style="flex:1;min-width:0"><div style="font-size:.8rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${r.nomeAluno||'Sem nome'}</div><div style="font-size:.6rem;color:var(--mu)">${r.turmaAluno||'—'} · ${r.acertos}/${r.total} · ${hora}</div></div></div>`;
  }).join('');
}

function omrVerHistorico(i) {
  omrResultadoAtual = omrHistorico[i];
  omrRenderResult(omrHistorico[i]);
  document.getElementById('omredu').scrollIntoView({behavior:'smooth'});
}

function omrLimparHistorico() {
  omrHistorico = [];
  omrRenderHistorico();
}

function omrSetLoading(active) {
  document.getElementById('omr-loading').style.display = active ? 'block' : 'none';
  document.getElementById('omr-emptyState').style.display = active ? 'none' : 'flex';
  if (!active) document.getElementById('omr-resultadoContent').style.display = 'none';
  document.getElementById('omr-btnAnalisar').disabled = active;
  if (active) { omrSetStep(1); }
}

function omrSetStep(step) {
  for (let i = 1; i <= 3; i++) {
    const el = document.getElementById('omr-step'+i);
    if (!el) continue;
    if (i < step) el.innerHTML = '✅ ' + el.textContent.replace(/[✅⏳⚡]/g,'').trim();
    else if (i === step) el.style.opacity = '1';
    else el.style.opacity = '.4';
  }
}

function omrShowAlert(msg, type) {
  const empty = document.getElementById('omr-emptyState');
  const loading = document.getElementById('omr-loading');
  const content = document.getElementById('omr-resultadoContent');
  empty.style.display = 'none';
  loading.style.display = 'none';
  content.style.display = 'block';
  const aBox = document.getElementById('omr-alertBox');
  const isErr = type === 'error' || type === 'warn';
  aBox.innerHTML = `<div style="padding:.65rem .9rem;border-radius:var(--rmd);font-size:.8rem;background:${isErr?'var(--sf2)':'var(--sf2)'};border:1px solid ${isErr?'var(--wa)':'var(--bd)'};color:var(--wa);margin-bottom:.8rem">${msg}</div>`;
  document.getElementById('omr-btnAnalisar').disabled = false;
}

function omrNovaAnalise() {
  omrResultadoAtual = null;
  document.getElementById('omr-resultadoContent').style.display = 'none';
  document.getElementById('omr-emptyState').style.display = 'flex';
  omrClearImage();
}

function omrCopiarResultado() {
  if (!omrResultadoAtual) return;
  const r = omrResultadoAtual;
  const linhas = ['OMREdu — Resultado','Aluno: '+(r.nomeAluno||'—')+' | Turma: '+(r.turmaAluno||'—'),'Resultado: '+r.acertos+'/'+r.total+' ('+r.pct+'%)','','Questão | Aluno | Gabarito | Status',...r.detalhes.map(q => 'Q'+q.numero+'     | '+(q.respostaAluno||'—')+'     | '+(q.respostaCorreta||'?')+'        | '+q.status)];
  navigator.clipboard.writeText(linhas.join('\\n')).then(() => toast('Resultado copiado!','ok'));
}

function omrExportarCSV() {
  if (!omrResultadoAtual) return;
  const r = omrResultadoAtual;
  const rows = [['Questão','Resposta','Gabarito','Status','Confiança'],...r.detalhes.map(q => [q.numero, q.respostaAluno||'', q.respostaCorreta||'', q.status, q.confianca ? (q.confianca*100).toFixed(0)+'%' : ''])];
  const csv = rows.map(r => r.join(';')).join('\\n');
  const blob = new Blob(['\\uFEFF'+csv], {type:'text/csv;charset=utf-8;'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'omredu_'+(r.nomeAluno||'resultado').replace(/\\s+/g,'_')+'.csv'; a.click();
  URL.revokeObjectURL(url);
}

// Init
omrRenderGabarito();
'''
def inject():
    html = read_file(V3_PATH)

    # 1. Adicionar CSS antes do primeiro </style>
    css_block = build_omr_css()
    html = html.replace("</style>", css_block + "\n</style>", 1)

    # 2. Adicionar nav button após dashboard button
    nav_btn = build_nav_button()
    html = html.replace(
        '<button data-target="dashboard">📊 Dashboard</button>',
        '<button data-target="dashboard">📊 Dashboard</button>\n' + nav_btn
    )

    # 3. Adicionar seção antes de </main>
    section = build_section()
    html = html.replace("</main>", section + "\n</main>")

    # 4. Adicionar JS antes de </script>
    js_block = build_omr_js()
    html = html.replace("</script>", js_block + "\n</script>", 1)

    # Criar backup
    import shutil
    shutil.copy2(V3_PATH, BACKUP_PATH)
    print(f"Backup salvo: {BACKUP_PATH}")

    write_file(V3_PATH, html)
    print(f"✅ Injeção concluída em: {V3_PATH}")

if __name__ == "__main__":
    inject()
