#!/usr/bin/env python3
"""Remove all CP code from the first <script> block, keeping only the second."""

import os

home = os.path.expanduser('~')
V3_PATH = os.path.join(home, 'Secret\u00e1ria', 'Download', 'planejador-escolar-v3.0.html')

with open(V3_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all script blocks
blocks = []
idx = 0
while True:
    s = content.find('<script>', idx)
    if s < 0: break
    e = content.find('</script>', s)
    if e < 0: break
    e += len('</script>')
    blocks.append((s, e))
    idx = e

print(f"Found {len(blocks)} script blocks")

# Identify which blocks have CP code
for i, (s, e) in enumerate(blocks):
    block = content[s:e]
    cp_items = []
    for fn in ['const cpThemes', 'function cpLoadTheme', 'function cpGenerate',
               'function cpRenderGrid', 'function cpCellClick', 'function cpCheckWord',
               'function cpComplete', 'function cpSpawnConfetti', 'function cpToggleShow',
               'function cpStartTimer', 'function cpStopTimer']:
        c = block.count(fn)
        if c > 0:
            cp_items.append(f"{fn}({c}x)")
    print(f"  Block {i+1} ({e-s} chars): {', '.join(cp_items) if cp_items else 'no CP code'}")

# Remove CP code from all blocks except the last one with CP
cp_blocks = [i for i in range(len(blocks)) if any(
    content[blocks[i][0]:blocks[i][1]].count(fn) > 0 
    for fn in ['const cpThemes', 'function cpLoadTheme', 'function cpGenerate']
)]

print(f"\nCP found in blocks: {[b+1 for b in cp_blocks]}")

if len(cp_blocks) > 1:
    # Keep the last CP block
    keep_block = cp_blocks[-1]
    remove_blocks = cp_blocks[:-1]
    
    for ri in remove_blocks:
        s, e = blocks[ri]
        block = content[s:e]
        
        # Remove specific CP functions from this block
        cp_functions = [
            'function cpLoadTheme', 'function cpGenerate', 'function cpRenderGrid',
            'function cpCellClick', 'function cpCellHover', 'function cpCheckWord',
            'function cpClearSelection', 'function cpUpdateStats', 'function cpUpdateWords',
            'function cpFocusWord', 'function cpStartTimer', 'function cpStopTimer',
            'function cpComplete', 'function cpSpawnConfetti', 'function cpToggleShow',
            'function cpPrint', 'function cpToast', 'function cpCellHover'
        ]
        
        # Find and remove ALL CP code between the CP marker and the next section
        marker = '\n// ══════════════════════════════════════════════════════════'
        # Also try without newline prefix
        alt_marker = '// ══════════════════════════════════════════════════════════'
        
        cp_start = block.find(alt_marker)
        if cp_start < 0:
            # Try finding by 'let cpCurrentTheme'
            cp_start = block.find('let cpCurrentTheme')
        
        if cp_start >= 0:
            # Remove everything from cp_start to the end of block (or next section)
            # Find the end: next marker or end of block
            after_cp = block[cp_start + 10:]
            next_section_start = -1
            for m in ['\n// ── ENTRY', '\ndocument.addEventListener', '\nif (document.readyState']:
                m_pos = after_cp.find(m)
                if m_pos > 0:
                    if next_section_start < 0 or (cp_start + 10 + m_pos) < next_section_start + blocks[ri][0]:
                        next_section_start = cp_start + 10 + m_pos
            
            if next_section_start > 0:
                # Remove from cp_start to next_section_start
                # But this is within the block, not the whole file
                # We need to remove from content, adjusting for block position
                file_start = s + cp_start
                file_end = s + next_section_start
                print(f"  Removing CP code from Block {ri+1}: offset {cp_start}-{next_section_start} (file: {file_start}-{file_end})")
                content = content[:file_start] + content[file_end:]
            else:
                print(f"  WARNING: Could not find end of CP code in Block {ri+1}")

        # If cp_start wasn't found, try line-by-line removal of CP functions
        if cp_start < 0:
            print(f"  WARNING: No CP marker found in Block {ri+1}")

    # Final check
    print(f"\n=== Final counts ===")
    for ident in ['const cpThemes', 'function cpLoadTheme', 'function cpGenerate', 
                  'function cpCellClick', 'function cpComplete', 'function cpToggleShow',
                  'function cpSpawnConfetti', 'function cpRenderGrid', 'function cpCheckWord']:
        count = content.count(ident)
        print(f"  {count}x: {ident}")
else:
    print("No duplicate CP blocks found.")

with open(V3_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\nDone! File size: {len(content)} chars")
