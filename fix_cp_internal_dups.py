#!/usr/bin/env python3
"""Remove duplicate CP functions within the remaining script block."""

import os
import re

home = os.path.expanduser('~')
V3_PATH = os.path.join(home, 'Secret\u00e1ria', 'Download', 'planejador-escolar-v3.0.html')

with open(V3_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the second script block
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

# Focus on the second block (if it exists)
if len(blocks) >= 2:
    s, e = blocks[1]
    block = content[s:e]
    
    print(f"Block 2 has {len(block)} chars")
    
    # Find ALL function definitions and their positions
    cp_funcs = [
        'function cpLoadTheme(', 'function cpGenerate(', 'function cpRenderGrid(',
        'function cpCellClick(', 'function cpCellHover(', 'function cpCheckWord(',
        'function cpClearSelection(', 'function cpUpdateStats(', 'function cpUpdateWords(',
        'function cpFocusWord(', 'function cpStartTimer(', 'function cpStopTimer(',
        'function cpComplete(', 'function cpSpawnConfetti(', 'function cpToggleShow(',
        'function cpPrint(', 'function cpToast('
    ]
    
    # For each function, find all occurrences within the block
    for fn in cp_funcs:
        count = block.count(fn)
        if count > 1:
            print(f"  {fn}: {count}x")
            
            # Find all positions (adjusted to file position)
            pos = 0
            fn_positions = []
            while True:
                p = block.find(fn, pos)
                if p < 0: break
                fn_positions.append(s + p)  # file position
                pos = p + 1
            
            # Keep the LAST occurrence, remove all previous ones
            for i, fp in enumerate(fn_positions[:-1]):
                # Find end of this function - next function or const/let/variable declaration
                search_from = fp - s + 1  # relative to block
                end_rel = len(block)
                
                # Look for next function declaration
                next_func = len(block)
                for nf in cp_funcs:
                    np = block.find(nf, search_from)
                    if np > 0 and np < next_func:
                        next_func = np
                
                # Also look for variable declarations or DOMContentLoaded
                for m in ['\nlet ', '\nconst ', '\ndocument.addEventListener', 
                          '\nif (document.readyState', '\n// ── ENTRY']:
                    mp = block.find(m, search_from)
                    if mp > 0 and mp < next_func:
                        next_func = mp
                
                end_rel = next_func
                file_end = s + end_rel
                
                print(f"    Removing occurrence #{i+1} at file pos {fp}-{file_end}")
                content = content[:fp] + content[file_end:]
                
                # Recalculate block positions since we modified content
                blocks = []
                idx = 0
                while True:
                    s2 = content.find('<script>', idx)
                    if s2 < 0: break
                    e2 = content.find('</script>', s2)
                    if e2 < 0: break
                    e2 += len('</script>')
                    blocks.append((s2, e2))
                    idx = e2
                
                if len(blocks) >= 2:
                    s, e = blocks[1]
                    block = content[s:e]
    
    # Final count
    print(f"\n=== Final counts ===")
    all_idents = ['const cpThemes'] + cp_funcs
    for ident in all_idents:
        count = content.count(ident)
        print(f"  {count}x: {ident}")

    with open(V3_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nDone! File size: {len(content)} chars")
else:
    print(f"Less than 2 script blocks found ({len(blocks)})")
