#!/usr/bin/env python3
"""Remove ALL duplicate CP JavaScript from the v3.0 file, keeping only the last copy."""

import os


home = os.path.expanduser("~")
V3_PATH = os.path.join(home, "Secretária", "Download", "planejador-escolar-v3.0.html")

with open(V3_PATH, "r", encoding="utf-8") as f:
    content = f.read()

print(f"File size: {len(content)} chars")
print(f"File contains 'cpThemes': {'cpThemes' in content}")

# Count all CP-related identifiers
identifiers = [
    "const cpThemes =",
    "let cpCurrentTheme",
    "let cpGrid =",
    "let cpWordPositions =",
    "let cpFoundWords =",
    "let cpSelectedCells =",
    "let cpTimer =",
    "let cpSeconds =",
    "let cpIsRunning",
    "let cpShowAnswers",
    "let cpIsComplete",
    "let cpPlacedCount",
    "let cpClearTimer",
    "function cpLoadTheme",
    "function cpGenerate",
    "function cpRenderGrid",
    "function cpCellClick",
    "function cpCheckWord",
    "function cpComplete",
    "function cpToggleShow",
]

for ident in identifiers:
    count = content.count(ident)
    if count > 1:
        print(f"  DUPLICATE ({count}x): {ident}")
    elif count == 1:
        print(f"  OK (1x): {ident}")
    else:
        print(f"  MISSING (0x): {ident}")

# Strategy: find ALL <script> blocks, keep the first (original v3.0) and last (new CP),
# remove any middle copies that have cp code
# But this is too aggressive. Better approach: find each occurrence and deduplicate by variable name.

# Find all occurrences of 'const cpThemes' and keep only the LAST one
count = content.count("const cpThemes = {")
if count > 1:
    # Find all positions
    positions = []
    idx = 0
    for _ in range(count):
        idx = content.find("const cpThemes = {", idx)
        if idx < 0:
            break
        positions.append(idx)
        idx += 1

    # Remove all but the last occurrence
    for i, pos in enumerate(positions[:-1]):
        # Find where this const declaration ends (next ';\n' or next 'let ' or next 'function ')
        end = len(content)
        for marker in ["\nlet ", "\nconst ", "\nfunction ", ";\n"]:
            m = content.find(marker, pos + 20)
            if m > 0 and m < end:
                end = m
        print(f"  Removing cpThemes #{i+1} from {pos} to {end}")
        content = content[:pos] + content[end:]

# Now fix any duplicate 'let' declarations - keep only the LAST occurrence of each
for var_name in [
    "let cpCurrentTheme",
    "let cpGrid",
    "let cpWordPositions",
    "let cpFoundWords",
    "let cpSelectedCells",
    "let cpTimer",
    "let cpSeconds",
    "let cpIsRunning",
    "let cpShowAnswers",
    "let cpIsComplete",
    "let cpPlacedCount",
    "let cpClearTimer",
]:
    count = content.count(var_name)
    if count > 1:
        # Find all positions
        positions = []
        idx = 0
        for _ in range(count):
            idx = content.find(var_name, idx)
            if idx < 0:
                break
            positions.append(idx)
            idx += 1

        # Remove all but the last occurrence
        for i, pos in enumerate(positions[:-1]):
            # Find end of this declaration (next ';' or '\n')
            end = content.find(";\n", pos)
            if end < 0:
                end = content.find("\n", pos + 20)
            if end < 0:
                end = len(content)
            end += 1  # include the newline
            print(f"  Removing duplicate {var_name} at {pos} (len={end-pos})")
            content = content[:pos] + content[end:]

# Check results
print("\n=== After cleanup ===")
for ident in identifiers:
    count = content.count(ident)
    if count > 1:
        print(f"  STILL DUPLICATED ({count}x): {ident}")
    elif count == 1:
        print(f"  OK (1x): {ident}")

with open(V3_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print(f"\nDone! File size: {len(content)} chars")
