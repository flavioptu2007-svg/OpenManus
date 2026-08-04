#!/usr/bin/env python3
"""Adiciona relatório PDF com estatísticas por questão/habilidade no OMREdu."""

V3_PATH = "/home/flavio/Secretária/Download/planejador-escolar-v3.0.html"
BACKUP_PATH = V3_PATH + ".pdfbak"


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def add_pdf_button(html):
    """Adiciona botão de relatório PDF ao lado dos botões existentes."""
    # Encontrar e modificar o primeiro conjunto de botões (linhas 937-939)
    old_btns = """                <button class="btn bs bsm" onclick="omrCopiarResultado()">📋 Copiar</button>
                <button class="btn bs bsm" onclick="omrExportarCSV()">⬇ CSV</button>
                <button class="btn bs bsm" onclick="omrNovaAnalise()">🔄 Nova</button>"""
    new_btns = """                <button class="btn bs bsm" onclick="omrCopiarResultado()">📋 Copiar</button>
                <button class="btn bs bsm" onclick="omrExportarCSV()">⬇ CSV</button>
                <button class="btn bs bsm" onclick="omrExportarPDF()">📄 PDF</button>
                <button class="btn bs bsm" onclick="omrNovaAnalise()">🔄 Nova</button>"""

    count = html.count(old_btns)
    if count > 0:
        html = html.replace(old_btns, new_btns, 1)  # Só o primeiro
        print(f"✅ Botão PDF adicionado (substituiu 1 ocorrência de {count})")

    return html


def add_pdf_js(html):
    """Adiciona a função omrExportarPDF ao JS."""
    # Adicionar depois de omrExportarCSV
    pdf_js_func = """
function omrExportarPDF() {
  if (!omrResultadoAtual) return;
  const r = omrResultadoAtual;

  // Coletar mapeamento habilidade-questão
  const n = parseInt(document.getElementById('omr-numQuestoes').value);
  const habilidades = [];
  for (let i = 1; i <= n; i++) {
    const el = document.getElementById('omr_hab_' + i);
    habilidades.push(el ? el.value.trim() : '');
  }

  // Agrupar por habilidade
  const habStats = {};
  r.detalhes.forEach((q, idx) => {
    const hab = habilidades[idx] || 'Sem habilidade';
    if (!habStats[hab]) habStats[hab] = { acertos: 0, erros: 0, nulas: 0, total: 0 };
    habStats[hab].total++;
    if (q.status === 'acerto') habStats[hab].acertos++;
    else if (q.status === 'erro') habStats[hab].erros++;
    else habStats[hab].nulas++;
  });

  // Preparar HTML do relatório
  const dataStr = new Date().toLocaleDateString('pt-BR') + ' ' + new Date().toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'});
  const pctColor = r.pct >= 70 ? '#1E8449' : r.pct >= 50 ? '#B7950B' : '#C0392B';

  let questoesHtml = '';
  r.detalhes.forEach(q => {
    const statusLabel = q.status === 'acerto' ? '✅ Acerto' : q.status === 'nula' ? '⬜ Nula' : '❌ Erro';
    const statusCor = q.status === 'acerto' ? '#1E8449' : q.status === 'nula' ? '#7f8c8d' : '#C0392B';
    const hab = habilidades[q.numero - 1] || '—';
    const pctConf = q.confianca > 0 ? Math.round(q.confianca * 100) + '%' : '—';
    questoesHtml += `<tr>
      <td style="text-align:center;font-weight:700">Q${q.numero}</td>
      <td style="text-align:center">${q.respostaAluno || '—'}</td>
      <td style="text-align:center">${q.respostaCorreta || '?'}</td>
      <td style="text-align:center"><span style="color:${statusCor};font-weight:700">${statusLabel}</span></td>
      <td style="text-align:center">${pctConf}</td>
      <td>${hab}</td>
    </tr>`;
  });

  let habHtml = '';
  const habEntries = Object.entries(habStats);
  if (habEntries.length > 0 && habEntries.some(([k]) => k !== 'Sem habilidade')) {
    habHtml = `<h3 style="color:#01696f;margin:24px 0 10px;font-size:1rem">📊 Estatísticas por Habilidade BNCC</h3>
    <table style="width:100%;border-collapse:collapse;font-size:.85rem">
      <thead><tr style="background:#f3f0ec">
        <th style="padding:8px 12px;text-align:left;border-bottom:2px solid #d4d1ca">Habilidade</th>
        <th style="padding:8px 12px;text-align:center;border-bottom:2px solid #d4d1ca">Acertos</th>
        <th style="padding:8px 12px;text-align:center;border-bottom:2px solid #d4d1ca">Erros</th>
        <th style="padding:8px 12px;text-align:center;border-bottom:2px solid #d4d1ca">Nulas</th>
        <th style="padding:8px 12px;text-align:center;border-bottom:2px solid #d4d1ca">Total</th>
        <th style="padding:8px 12px;text-align:center;border-bottom:2px solid #d4d1ca">% Acerto</th>
      </tr></thead>
      <tbody>`;
    for (const [hab, st] of Object.entries(habStats)) {
      const pct = st.total > 0 ? Math.round((st.acertos / st.total) * 100) : 0;
      const cor = pct >= 70 ? '#1E8449' : pct >= 50 ? '#B7950B' : '#C0392B';
      habHtml += `<tr>
        <td style="padding:7px 12px;border-bottom:1px solid #d4d1ca;font-weight:600">${hab}</td>
        <td style="padding:7px 12px;text-align:center;border-bottom:1px solid #d4d1ca;color:#1E8449;font-weight:700">${st.acertos}</td>
        <td style="padding:7px 12px;text-align:center;border-bottom:1px solid #d4d1ca;color:#C0392B">${st.erros}</td>
        <td style="padding:7px 12px;text-align:center;border-bottom:1px solid #d4d1ca;color:#7f8c8d">${st.nulas}</td>
        <td style="padding:7px 12px;text-align:center;border-bottom:1px solid #d4d1ca">${st.total}</td>
        <td style="padding:7px 12px;text-align:center;border-bottom:1px solid #d4d1ca;color:${cor};font-weight:700">${pct}%</td>
      </tr>`;
    }
    habHtml += '</tbody></table>';
  }

  const reportHtml = `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Relatório OMREdu</title>
<style>
  @page { margin: 1.5cm; size: A4; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; color: #222; line-height: 1.5; padding: 20px; }
  .header { text-align: center; border-bottom: 3px solid #01696f; padding-bottom: 15px; margin-bottom: 20px; }
  .header h1 { font-size: 1.5rem; color: #01696f; margin-bottom: 4px; }
  .header p { color: #666; font-size: .85rem; }
  .aluno-info { display: flex; justify-content: space-between; margin-bottom: 16px; padding: 10px 14px; background: #f7f6f2; border-radius: 6px; font-size: .9rem; }
  .aluno-info strong { color: #01696f; }
  .score-row { display: flex; gap: 8px; margin-bottom: 18px; }
  .score-item { flex: 1; text-align: center; padding: 12px 8px; border-radius: 6px; border: 1px solid #d4d1ca; }
  .score-num { font-size: 1.8rem; font-weight: 800; line-height: 1; }
  .score-label { font-size: .7rem; color: #666; text-transform: uppercase; letter-spacing: .05em; margin-top: 4px; }
  .bar-wrap { background: #f3f0ec; height: 10px; border-radius: 99px; overflow: hidden; margin-bottom: 20px; }
  .bar-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #1E8449, #01696f); }
  h3 { color: #01696f; margin: 20px 0 10px; font-size: 1rem; }
  table { width: 100%; border-collapse: collapse; font-size: .82rem; margin-bottom: 16px; }
  th { background: #f3f0ec; padding: 7px 10px; text-align: left; border-bottom: 2px solid #d4d1ca; font-size: .72rem; text-transform: uppercase; letter-spacing: .05em; color: #666; }
  td { padding: 6px 10px; border-bottom: 1px solid #d4d1ca; }
  .footer { text-align: center; margin-top: 30px; font-size: .7rem; color: #999; border-top: 1px solid #d4d1ca; padding-top: 12px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: .7rem; font-weight: 700; }
  .b-ok { background: #e8f5e9; color: #1E8449; }
  .b-warn { background: #fff8e1; color: #B7950B; }
  .b-err { background: #fdecea; color: #C0392B; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style></head>
<body>
  <div class="header">
    <h1>📄 Relatório de Correção — OMREdu</h1>
    <p>Gerado em ${dataStr}</p>
  </div>

  <div class="aluno-info">
    <span><strong>Aluno(a):</strong> ${r.nomeAluno || '—'}</span>
    <span><strong>Turma:</strong> ${r.turmaAluno || '—'}</span>
    <span><strong>Data:</strong> ${dataStr}</span>
  </div>

  <div class="score-row">
    <div class="score-item"><div class="score-num" style="color:#1E8449">${r.acertos}</div><div class="score-label">Acertos</div></div>
    <div class="score-item"><div class="score-num" style="color:#C0392B">${r.erros}</div><div class="score-label">Erros</div></div>
    <div class="score-item"><div class="score-num" style="color:#7f8c8d">${r.nulas}</div><div class="score-label">Nulas</div></div>
    <div class="score-item"><div class="score-num" style="color:${pctColor}">${r.pct}%</div><div class="score-label">Aproveitamento</div></div>
  </div>

  <div class="bar-wrap"><div class="bar-fill" style="width:${r.pct}%"></div></div>

  <h3>📋 Questão a Questão</h3>
  <table>
    <thead><tr>
      <th style="text-align:center">Q</th><th style="text-align:center">Aluno</th>
      <th style="text-align:center">Gabarito</th><th style="text-align:center">Resultado</th>
      <th style="text-align:center">Confiança</th><th>Habilidade</th>
    </tr></thead>
    <tbody>${questoesHtml}</tbody>
  </table>

  ${habHtml}

  <div style="margin-top:12px;display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
    <span class="badge b-ok">✅ Acerto</span>
    <span class="badge b-err">❌ Erro</span>
    <span class="badge" style="background:#f3f0ec;color:#7f8c8d">⬜ Nula</span>
  </div>

  ${r.observacoesGerais ? '<div style="background:#f7f6f2;border:1px solid #d4d1ca;border-radius:6px;padding:10px 14px;margin-top:16px;font-size:.82rem;color:#555"><strong style="color:#01696f">Observações da IA:</strong><br>' + r.observacoesGerais + '</div>' : ''}

  <div class="footer">
    OMREdu — Corretor de Gabaritos com IA · Claude Vision · ${dataStr}
  </div>

  <div class="no-print" style="text-align:center;margin-top:16px">
    <button onclick="window.print()" style="padding:8px 18px;background:#01696f;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:.9rem">🖨️ Imprimir / Salvar PDF</button>
  </div>
</body></html>`;

  // Abrir em nova janela para impressão
  const w = window.open('', '_blank', 'width=900,height=700,scrollbars=yes');
  if (!w) {
    toast('Permita pop-ups para gerar o relatório.', 'err');
    return;
  }
  w.document.write(reportHtml);
  w.document.close();
}
"""
    # Encontrar e adicionar após a definição de omrExportarCSV (primeira ocorrência)
    marker = """function omrExportarCSV() {
  if (!omrResultadoAtual) return;
  const r = omrResultadoAtual;"""

    if marker in html:
        html = html.replace(marker, marker + pdf_js_func, 1)
        print(f"✅ Função omrExportarPDF adicionada ao JS")
    else:
        print("❌ Marcador omrExportarCSV não encontrado!")
        # Tentar encontrar com outro padrão
        import re

        matches = list(re.finditer(r"function omrExportarCSV\(\)\s*\{", html))
        print(f"Encontradas {len(matches)} ocorrências de 'function omrExportarCSV'")
        for m in matches:
            print(f"  Posição {m.start()}: {html[m.start():m.start()+80]}")

    return html


def add_habilidade_inputs(html):
    """Adiciona campos de habilidade por questão no gabarito."""
    # Encontrar o cabeçalho do gabarito e adicionar a seção de habilidades
    old_gab_header = """<p class="prova-cfg-title">📋 Gabarito Oficial</p>
          <div class="omr-gab-grid" id="omr-gabaritoGrid"></div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:.6rem">
            <button class="btn bs bsm" onclick="omrFillAll('A')">Tudo A</button>
            <button class="btn bs bsm" onclick="omrFillAll('B')">Tudo B</button>
            <button class="btn bs bsm" onclick="omrFillAll('C')">Tudo C</button>
            <button class="btn bs bsm" onclick="omrClearGab()">Limpar</button>
          </div>"""

    new_gab_header = """<p class="prova-cfg-title">📋 Gabarito Oficial</p>
          <div class="omr-gab-grid" id="omr-gabaritoGrid"></div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:.6rem">
            <button class="btn bs bsm" onclick="omrFillAll('A')">Tudo A</button>
            <button class="btn bs bsm" onclick="omrFillAll('B')">Tudo B</button>
            <button class="btn bs bsm" onclick="omrFillAll('C')">Tudo C</button>
            <button class="btn bs bsm" onclick="omrClearGab()">Limpar</button>
          </div>
          <details style="margin-top:.6rem;font-size:.82rem">
            <summary style="cursor:pointer;color:var(--pr);font-weight:600">📌 Mapear Habilidades BNCC</summary>
            <div style="margin-top:.5rem;background:var(--sf);border:1px solid var(--bd);border-radius:var(--rmd);padding:.6rem .75rem">
              <p style="font-size:.72rem;color:var(--mu);margin-bottom:.4rem">Insira o código BNCC para cada questão (opcional):</p>
              <div class="omr-hab-grid" id="omr-habGrid"></div>
            </div>
          </details>"""

    count = html.count(old_gab_header)
    if count > 0:
        html = html.replace(old_gab_header, new_gab_header, 1)
        print(f"✅ Mapeamento de habilidades adicionado ao gabarito")
    else:
        print("❌ Cabeçalho do gabarito não encontrado!")

    return html


def add_gabarito_habilidades_js(html):
    """Adiciona JS para renderizar campos de habilidade e estende omrRenderGabarito."""
    # Adicionar função para renderizar campos de habilidade
    hab_js = """
function omrRenderHabilidades() {
  const n = parseInt(document.getElementById('omr-numQuestoes').value);
  const grid = document.getElementById('omr-habGrid');
  if (!grid) return;
  grid.innerHTML = '';
  for (let i = 1; i <= n; i++) {
    const cell = document.createElement('div');
    cell.style.cssText = 'display:flex;flex-direction:column;align-items:center;gap:2px';
    cell.innerHTML = `<span style="font-size:.58rem;color:var(--mu);font-weight:600">Q${i}</span><input id="omr_hab_${i}" type="text" placeholder="Ex: EF06HI01" style="width:100%;padding:.2rem .3rem;font-size:.68rem;text-align:center;border:1px solid var(--bd);border-radius:4px;background:var(--sf);color:var(--tx1)"/>`;
    grid.appendChild(cell);
  }
}

// Sobrescrever omrRenderGabarito para também renderizar habilidades
const omrRenderGabaritoOriginal = omrRenderGabarito;
omrRenderGabarito = function() {
  omrRenderGabaritoOriginal();
  omrRenderHabilidades();
};
"""
    # Adicionar após a declaração de omrRenderGabarito (a primeira, antes das funções de utilidade)
    marker1 = "function omrRenderGabarito() {"

    if marker1 in html:
        # Encontrar a primeira ocorrência e adicionar depois dela
        idx = html.find(marker1)
        # Encontrar o fechamento da função
        end_marker = "\nfunction omrFillAll"
        end_idx = html.find(end_marker, idx)
        if end_idx > idx:
            # Adicionar o bloco JS antes da função omrFillAll
            html = html[:end_idx] + hab_js + html[end_idx:]
            print("✅ Funções de habilidade adicionadas ao JS")
        else:
            print("❌ Não encontrou end_marker para omrRenderGabarito")
    else:
        print("❌ omrRenderGabarito não encontrado!")

    return html


def add_pdf_hab_css(html):
    """Adiciona CSS para a grid de habilidades."""
    css = """
#omredu .omr-hab-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 4px; margin-top: .2rem; }
@media(max-width:660px){#omredu .omr-hab-grid{grid-template-columns:repeat(3,1fr)}}
"""
    # Adicionar antes do fechamento do primeiro bloco de estilo do OMREdu
    marker = "/* ── OMR: CORRETOR DE GABARITOS ── */"
    if marker in html:
        # Encontrar o próximo bloco @media
        idx = html.find(marker)
        # Procurar o próximo fechamento de style ou o final do bloco
        end_idx = html.find("/* ── PROGRESSO IA", idx)
        if end_idx > idx:
            html = html[:end_idx] + css + html[end_idx:]
            print("✅ CSS de habilidades adicionado")
        else:
            print("❌ Não encontrou final do bloco CSS OMR")
    else:
        print("❌ Marcador CSS OMR não encontrado!")

    return html


def main():
    import shutil

    shutil.copy2(V3_PATH, BACKUP_PATH)
    print(f"Backup salvo: {BACKUP_PATH}")

    html = read_file(V3_PATH)

    html = add_pdf_button(html)
    html = add_habilidade_inputs(html)
    html = add_pdf_hab_css(html)
    html = add_pdf_js(html)
    html = add_gabarito_habilidades_js(html)

    write_file(V3_PATH, html)
    print(f"\n✅ Relatório PDF adicionado em: {V3_PATH}")


if __name__ == "__main__":
    main()
