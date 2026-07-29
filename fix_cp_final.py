#!/usr/bin/env python3
"""Ultimate fix: deduplicate CP JavaScript in v3.0 file using line-by-line analysis."""

import os
import re
import shutil

home = os.path.expanduser('~')
V3_PATH = os.path.join(home, 'Secret\u00e1ria', 'Download', 'planejador-escolar-v3.0.html')

with open(V3_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Check: are there <script> blocks or a single one?
script_count = content.count('<script>')
print(f"Found {script_count} <script> tags")

# Find ALL script blocks and check what's inside
positions = []
idx = 0
while True:
    s = content.find('<script>', idx)
    if s < 0: break
    e = content.find('</script>', s)
    if e < 0: break
    e += len('</script>')
    positions.append((s, e, e - s))
    idx = e

print(f"\nScript blocks:")
for i, (s, e, l) in enumerate(positions):
    block = content[s:e]
    has_cp = 'cpThemes' in block
    cp_count = block.count('cpThemes')
    has_omr = 'omrRender' in block
    is_orig = 'getCfg' in block
    print(f"  Block {i+1}: {l} chars | cpThemes={cp_count}x | omr={has_omr} | orig={is_orig} | pos={s}-{e}")

# If there are multiple script blocks, we need to keep the original v3.0 JS + CP JS
# Strategy: keep the FIRST script block (original v3.0 + first CP injection) 
# and remove CP code from subsequent blocks

# Actually, let me just check if there's a single script block
# If yes, the duplicates are inside it

if len(positions) <= 2:
    print("\n✅ Single script block (or 2 blocks) - checking inside...")
    # Find all 'const cpThemes' inside the file
    cp_count = content.count('const cpThemes')
    print(f"  Total 'const cpThemes' found: {cp_count}")
    
    # For each occurrence after the first, remove it
    first_pos = content.find('const cpThemes')
    if first_pos >= 0 and cp_count > 1:
        idx = content.find('const cpThemes', first_pos + 1)
        while idx >= 0:
            # Find the end - go to the next ';\n' or 'function ' or end of block
            end = len(content)
            for marker in ['\nlet ', '\nfunction ', '\nconst ', '\ndocument.addEventListener']:
                m = content.find(marker, idx + 5)
                if m > 0 and m < end:
                    end = m
            print(f"  Removing duplicate cpThemes block at {idx}-{end}")
            content = content[:idx] + content[end:]
            idx = content.find('const cpThemes', first_pos)
            cp_count = content.count('const cpThemes')
            print(f"  Remaining cpThemes count: {cp_count}")

# Now fix duplicate functions: remove all CP function declarations except the last set
cp_functions = [
    'function cpLoadTheme', 'function cpGenerate', 'function cpRenderGrid',
    'function cpCellClick', 'function cpCellHover', 'function cpCheckWord',
    'function cpClearSelection', 'function cpUpdateStats', 'function cpUpdateWords',
    'function cpFocusWord', 'function cpStartTimer', 'function cpStopTimer',
    'function cpComplete', 'function cpSpawnConfetti', 'function cpToggleShow',
    'function cpPrint'
]

for fn in cp_functions:
    count = content.count(fn)
    if count > 1:
        # Find all positions
        positions = []
        idx = 0
        for _ in range(count):
            idx = content.find(fn, idx)
            if idx < 0: break
            positions.append(idx)
            idx += 1
        
        # Remove all but last
        for i, pos in enumerate(positions[:-1]):
            # Find next function or variable declaration
            next_markers = []
            for m in ['\nfunction ', '\nlet ', '\nconst ', '\ndocument.addEventListener', '\nif (document.readyState']:
                m_pos = content.find(m, pos + len(fn) + 5)
                if m_pos > 0:
                    next_markers.append(m_pos)
            # Also check for next occurrence of the same fn
            next_same = content.find(fn, pos + len(fn))
            if next_same > 0:
                next_markers.append(next_same)
            
            end = min(next_markers) if next_markers else len(content)
            # Actually, for functions, end at the matching function body end
            # Since we can't easily track braces, use the next marker approach
            print(f"  Removing duplicate {fn} at pos {pos}-{end}")
            content = content[:pos] + content[end:]

# Final count
print(f"\n=== Final CP counts ===")
for ident in ['const cpThemes', 'function cpLoadTheme', 'function cpGenerate', 
              'function cpCellClick', 'function cpComplete', 'function cpSpawnConfetti',
              'function cpToggleShow']:
    count = content.count(ident)
    print(f"  {count}x: {ident}")

with open(V3_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\nDone! File size: {len(content)} chars")
