#!/usr/bin/env python3
"""Corrige problemas do relatório PDF: CSS, override, e visualização em tela."""

V3_PATH = "/home/flavio/Secretária/Download/planejador-escolar-v3.0.html"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def fix_css(html):
    """Adiciona CSS para omr-hab-grid em local confiável."""
    css_block = """
/* ── OMR HABILIDADES ── */
#omredu .omr-hab-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 4px; margin-top: .2rem; }
#omredu .omr-hab-grid input { font-size: .68rem !important; padding: .2rem .3rem !important; text-align: center; }
@media(max-width:660px){#omredu .omr-hab-grid{grid-template-columns:repeat(3,1fr)}}
"""
    # Inserir antes de @media print (que é confiável)
    marker = "@media print"
    if marker in html:
        html = html.replace(marker, css_block + "\n" + marker, 1)
        print("✅ CSS habilidades injetado antes de @media print")
    else:
        print("❌ @media print não encontrado")
    return html

def fix_override(html):
    """Substitui o override frágil do omrRenderGabarito por uma abordagem direta."""
    # Encontrar e substituir o override atual por uma versão que chama as duas funções a partir do onclick
    old_override = """// Sobrescrever omrRenderGabarito para também renderizar habilidades
const omrRenderGabaritoOriginal = omrRenderGabarito;
omrRenderGabarito = function() {
  omrRenderGabaritoOriginal();
  omrRenderHabilidades();
};"""
    new_override = """// Chamar renderização de habilidades junto com o gabarito
// A função omrRenderGabarito original chama omrRenderHabilidades no final
// (implementado inline para robustez)"""
    
    if old_override in html:
        html = html.replace(old_override, new_override, 1)
        print("✅ Override substituído por abordagem inline")
    else:
        print("⚠️ Override não encontrado - pode já estar corrigido")
        # Tentar encontrar o que foi injetado
        import re
        matches = list(re.finditer(r'omrRenderGabaritoOriginal', html))
        print(f"Encontradas {len(matches)} ocorrências de 'omrRenderGabaritoOriginal'")
    
    # Agora modificar a função omrRenderGabarito original para incluir omrRenderHabilidades no final
    # Procurar o fechamento da função e adicionar a chamada
    old_render = """function omrRenderGabarito() {
  const n = parseInt(document.getElementById('omr-numQuestoes').value);
  const grid = document.getElementById('omr-gabaritoGrid');
  grid.innerHTML = '';
  for (let i = 1; i <= n; i++) {
    const cell = document.createElement('div');
    cell.style.cssText = 'display:flex;flex-direction:column;align-items:center;gap:2px';
    cell.innerHTML = `<span style="font-size:.6rem;color:var(--mu)">Q${i}</span><select id="omr_gab_${i}" style="width:100%;padding:.25rem .1rem;font-size:.75rem;text-align:center;font-family:monospace"><option value="">—</option><option>A</option><option>B</option><option>C</option><option>D</option><option>E</option></select>`;
    grid.appendChild(cell);
  }
}"""
    
    # Adicionar chamada a omrRenderHabilidades no final da função
    new_render = """function omrRenderGabarito() {
  const n = parseInt(document.getElementById('omr-numQuestoes').value);
  const grid = document.getElementById('omr-gabaritoGrid');
  grid.innerHTML = '';
  for (let i = 1; i <= n; i++) {
    const cell = document.createElement('div');
    cell.style.cssText = 'display:flex;flex-direction:column;align-items:center;gap:2px';
    cell.innerHTML = `<span style="font-size:.6rem;color:var(--mu)">Q${i}</span><select id="omr_gab_${i}" style="width:100%;padding:.25rem .1rem;font-size:.75rem;text-align:center;font-family:monospace"><option value="">—</option><option>A</option><option>B</option><option>C</option><option>D</option><option>E</option></select>`;
    grid.appendChild(cell);
  }
  // Também renderizar campos de habilidade
  if (typeof omrRenderHabilidades === 'function') omrRenderHabilidades();
}"""
    
    if old_render in html:
        html = html.replace(old_render, new_render, 1)
        print("✅ omrRenderGabarito atualizada para chamar omrRenderHabilidades")
    else:
        print("⚠️ omrRenderGabarito original não encontrada - verificando diferenças")
        # Mostrar a função encontrada
        idx = html.find("function omrRenderGabarito() {")
        if idx >= 0:
            snippet = html[idx:idx+500]
            print(f"  Primeiros 500 chars:\n{snippet[:500]}")
        else:
            print("  function omrRenderGabarito() não encontrada!")
    
    return html

def add_habilidade_to_results(html):
    """Adiciona badge de habilidade nos cards de resultado na tela."""
    # Modificar omrRenderResult para incluir a habilidade nos cards
    old_line = """    const pct = q.confianca > 0 ? Math.round(q.confianca*100)+'%' : '';
    div.innerHTML = `<span class="omr-q-status">${icon}</span><span class="omr-q-num">Q${q.numero}</span>${html}${pct ? '<span style="font-size:.55rem;color:var(--mu)">'+pct+'</span>' : ''}`;
    table.appendChild(div);"""
    
    new_line = """    const pct = q.confianca > 0 ? Math.round(q.confianca*100)+'%' : '';
    // Mostrar habilidade se disponível
    const habEl = document.getElementById('omr_hab_' + q.numero);
    const habCode = habEl ? habEl.value.trim() : '';
    const habHtml2 = habCode ? '<span style="font-size:.5rem;color:var(--mu);background:var(--sf2);padding:1px 5px;border-radius:4px;margin-top:2px">'+habCode+'</span>' : '';
    div.innerHTML = `<span class="omr-q-status">${icon}</span><span class="omr-q-num">Q${q.numero}</span>${html}${habHtml2}${pct ? '<span style="font-size:.55rem;color:var(--mu)">'+pct+'</span>' : ''}`;
    table.appendChild(div);"""
    
    count = html.count(old_line)
    if count > 0:
        html = html.replace(old_line, new_line, 1)
        print(f"✅ Badge de habilidade adicionado aos cards de resultado (substituiu 1 de {count})")
    else:
        # Tentar encontrar a linha com variações
        idx = html.find('pct ?')
        if idx >= 0:
            snippet = html[idx-50:idx+200]
            print(f"⚠️ Linha exata não encontrada. Contexto:\n...{snippet}")
        else:
            print("⚠️ 'pct ?' não encontrado no JS")
    
    return html

def main():
    html = read_file(V3_PATH)
    
    html = fix_css(html)
    html = fix_override(html)
    html = add_habilidade_to_results(html)
    
    write_file(V3_PATH, html)
    print(f"\n✅ Correções aplicadas")

if __name__ == "__main__":
    main()
