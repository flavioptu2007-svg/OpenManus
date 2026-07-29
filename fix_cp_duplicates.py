#!/usr/bin/env python3
"""Remove duplicate Caça-Palavras JS and CSS from the v3.0, then clean-reinject."""

import os
import re
import shutil

V3_PATH = os.path.expanduser('~/Secretária/Download/planejador-escolar-v3.0.html')

with open(V3_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Find ALL occurrences of the CP JS marker
marker = '// ══════════════════════════════════════════════════════════'
# Also match: 'let cpCurrentTheme' and 'const cpThemes'

# Find the CP CSS block and remove ALL copies
cp_css_marker = '/* ── CSS DO CAÇA-PALAVRAS (escopado sob #jogos) ── */'
count_css = content.count(cp_css_marker)
print(f"Found {count_css} CP CSS blocks")

# Remove all CP CSS blocks
# Each block starts with cp_css_marker and ends before the next CSS rule or at </style>
while content.count(cp_css_marker) > 0:
    start = content.find(cp_css_marker)
    # Find the end: next <style, </style, or another marker
    end_candidates = []
    nxt_css = content.find('/* ──', start + 1)
    if nxt_css > 0: end_candidates.append(nxt_css)
    nxt_style = content.find('</style>', start)
    if nxt_style > 0: end_candidates.append(nxt_style)
    if end_candidates:
        end = min(end_candidates)
    else:
        end = len(content)
    print(f"  Removing CP CSS from {start} to {end}")
    content = content[:start] + content[end:]

# 2. Find ALL occurrences of the CP JS sections and remove first N-1
js_marker = '// ══════════════════════════════════════════════════════════'
# Find the specific CP JS sections (containing 'CAÇA-PALAVRAS')
positions = []
idx = -1
while True:
    idx = content.find(js_marker, idx + 1)
    if idx < 0: break
    if 'CAÇA-PALAVRAS' in content[idx:idx+200]:
        positions.append(idx)
        print(f"Found CP JS at position {idx}")

# Remove all but the LAST occurrence
for i, pos in enumerate(positions[:-1]):
    # Find the next occurrence of the same marker AFTER this one
    next_marker = positions[i + 1] if i + 1 < len(positions) else len(content)
    # Also check for next script block end
    end = content.find('</script>', pos)
    if end < 0 or end > next_marker:
        # Just remove up to next marker
        end = next_marker
    else:
        end = end + len('</script>')
    # Actually, the section ends at either the next marker or </script>
    section_end = min(
        content.find(js_marker, pos + 1) if content.find(js_marker, pos + 1) > 0 else len(content),
        content.find('</script>', pos) + len('</script>') if content.find('</script>', pos) > 0 else len(content)
    )
    print(f"  Removing JS from {pos} to {section_end}")
    content = content[:pos] + content[section_end:]

# 3. Check for duplicate sidebar buttons (data-target="jogos")
jogos_btn = '<button data-target="jogos">'
count_btns = content.count(jogos_btn)
print(f"\nFound {count_btns} Jogos buttons in sidebar")

# 4. Check for duplicate sections
jogos_section = '<section id="jogos"'
count_sections = content.count(jogos_section)
print(f"Found {count_sections} #jogos sections")

# 5. Write cleaned file
with open(V3_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n✅ Cleanup done! File size: {len(content)} chars")
