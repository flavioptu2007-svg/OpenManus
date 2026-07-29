#!/usr/bin/env python3
"""
Adiciona lógica local-first com AbortController timeout nas funções omrCallApi do v3.0.

- Tenta localhost:5000/api/omr-analyze PRIMEIRO com timeout de 3s
- Fallback para Anthropic/Claude se o servidor local estiver offline
- Substitui AMBAS as cópias (linha 2726 e 3093)
"""

import os
import re

home = os.path.expanduser('~')
V3_PATH = os.path.join(home, 'Secret\u00e1ria', 'Download', 'planejador-escolar-v3.0.html')

with open(V3_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Find both omrCallApi functions
def find_function_bodies(text, func_name):
    """Find function bodies by matching balanced braces."""
    positions = []
    pattern = func_name.replace('(', r'\(')
    for match in re.finditer(pattern, text):
        start = match.start()
        brace_start = text.find('{', start)
        if brace_start < 0: continue
        depth = 1
        pos = brace_start + 1
        while depth > 0 and pos < len(text):
            if text[pos] == '{': depth += 1
            elif text[pos] == '}': depth -= 1
            pos += 1
        positions.append((start, pos))
    return positions

# New omrCallApi with local-first + AbortController timeout
new_omrCallApi = '''async function omrCallApi(imgBase64, gabarito, nQ) {
  let b64 = imgBase64.includes(',') ? imgBase64.split(',')[1] : imgBase64;
  
  // Tentar servidor local PRIMEIRO com timeout de 3s
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(function() { controller.abort(); }, 3000);
    
    const resp = await fetch('http://localhost:5000/api/omr-analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      body: JSON.stringify({ imagem_base64: b64, gabarito: gabarito.join(','), num_questoes: nQ, alternativas: 5 })
    });
    clearTimeout(timeoutId);
    
    if (resp.ok) return await resp.json();
    const errData = await resp.json().catch(function() { return {}; });
    throw new Error(errData.erro || 'Local API erro ' + resp.status);
  } catch (localErr) {
    if (localErr.name === 'AbortError') {
      console.warn('Local OMR timeout (3s) - tentando Claude');
    } else {
      console.warn('Local OMR falhou:', localErr.message, '- tentando Claude');
    }
    
    // Fallback: Anthropic Claude Vision
    const prompt = 'Voce e um especialista em OMR. Analise a imagem e identifique as marcacoes. GABARITO OFICIAL: ' + gabarito.join(',') + ' NUMERO DE QUESTOES: ' + nQ + '. Responda APENAS JSON: {"status":"SUCESSO","confianca_geral":85,"questoes":[{"numero":1,"resposta_identificada":"A","confianca":95,"marcacoes_detectadas":1}],"resumo":{"acertos":0,"erros":0,"nulas":0,"total":' + nQ + ',"percentual":0.0}}';
    
    const fallbackKey = document.getElementById('apiKeyInput')?.value || '';
    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': fallbackKey, 'anthropic-version': '2023-06-01', 'anthropic-dangerous-direct-browser-access': 'true' },
      body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 1000, messages: [{ role: 'user', content: [{ type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: b64 } }, { type: 'text', text: prompt }] }] })
    });
    if (!resp.ok) { var errText = await resp.text().catch(function() { return ''; }); throw new Error('API erro ' + resp.status + ': ' + errText.slice(0, 200)); }
    var data = await resp.json();
    var text = data.content?.[0]?.text || '';
    var jsonMatch = text.match(/\\{[\\s\\S]*\\}/);
    if (!jsonMatch) throw new Error('Resposta sem JSON valido');
    return JSON.parse(jsonMatch[0]);
  }
}'''

# Find both omrCallApi function positions
positions = find_function_bodies(content, 'async function omrCallApi(')
print(f"Found {len(positions)} omrCallApi functions")

# Replace from end to start (to not shift positions)
for start, end in reversed(positions):
    old_len = end - start
    print(f"Replacing omrCallApi at {start}-{end} (len={old_len})")
    content = content[:start] + new_omrCallApi + content[end:]

# Verify
remaining = content.count('async function omrCallApi')
print(f"Remaining omrCallApi definitions: {remaining}")

# Check for AbortController reference
if 'AbortController' in content:
    print("✅ AbortController timeout present")
if 'localhost:5000' in content:
    print("✅ Local-first logic present")

with open(V3_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\nDone! File size: {len(content)} chars")
