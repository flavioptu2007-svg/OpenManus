#!/usr/bin/env python3
"""Restore clean v3.0 backup, then inject Caça-Palavras once."""

import os
import shutil

home = os.path.expanduser('~')
dl = os.path.join(home, 'Secretária', 'Download')

# Files
bak_clean = os.path.join(dl, 'planejador-escolar-v3.0.html.bak')
target = os.path.join(dl, 'planejador-escolar-v3.0.html')

# 1. Restore clean backup
shutil.copy2(bak_clean, target)
print(f'Restored clean backup ({os.path.getsize(bak_clean)} bytes)')

# Verify
with open(target, 'r', encoding='utf-8') as f:
    content = f.read()
print(f'cpThemes present: {"cpThemes" in content}')
print(f'omrAnalisar present: {"omrAnalisar" in content}')
print(f'File size: {len(content)} chars')

# 2. Now import and run the injection
import inject_cacapalavras_v3
# The inject script has an inject() function - let's call it directly
# But it's a standalone script, not a module with a function
# Let me read and execute its logic instead

# Re-read the clean file
with open(target, 'r', encoding='utf-8') as f:
    html = f.read()

from inject_cacapalavras_v3 import CACA_PALAVRAS_CSS, CACA_PALAVRAS_HTML, CACA_PALAVRAS_JS

# Add sidebar button
btn_code = '\n    <button data-target="jogos">🎮 Jogos</button>'
marker = 'data-target="omredu">🤖 Corretor IA</button>'
idx = html.rfind(marker)
if idx >= 0:
    insert_pos = idx + len(marker)
    html = html[:insert_pos] + btn_code + html[insert_pos:]
    print('✅ Sidebar button injected')

# Inject CSS
style_tag = '</style>'
idx = html.rfind(style_tag)
if idx >= 0:
    html = html[:idx] + CACA_PALAVRAS_CSS + '\n' + html[idx:]
    print('✅ CSS injected')

# Inject HTML section
section_marker = 'id="omredu" class="panel-section'
idx = html.rfind(section_marker)
if idx >= 0:
    section_end = html.find('</section>', idx)
    if section_end >= 0:
        section_end += len('</section>')
        html = html[:section_end] + '\n' + CACA_PALAVRAS_HTML + html[section_end:]
        print('✅ HTML section injected')

# Inject JS before last </script>
script_close = '</script>'
idx = html.rfind(script_close)
if idx >= 0:
    html = html[:idx] + '\n' + CACA_PALAVRAS_JS + '\n' + html[idx:]
    print('✅ JS injected')

# Save
with open(target, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\n✅ Final file: {len(html)} chars')
print(f'cpThemes count: {html.count("const cpThemes")}')
print(f'cpLoadTheme count: {html.count("function cpLoadTheme")}')
print(f'cpGenerate count: {html.count("function cpGenerate")}')
