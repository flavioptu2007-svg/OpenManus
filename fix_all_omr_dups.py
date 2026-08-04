#!/usr/bin/env python3
"""Fix ALL duplicate `let omr*` declarations in the v3.0 file."""

import os
import re


home = os.path.expanduser("~")
V3_PATH = os.path.join(
    home, "Secret\u00e1ria", "Download", "planejador-escolar-v3.0.html"
)

with open(V3_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Find all 'let omr' declarations
pattern = r"let (omr[A-Za-z0-9_]+)\s*=\s*"
matches = list(re.finditer(pattern, content))

# Group by variable name
vars_found = {}
for m in matches:
    var_name = m.group(1)
    if var_name not in vars_found:
        vars_found[var_name] = []
    vars_found[var_name].append(m.start())

print(f"OMR variables found:")
for var, positions in sorted(vars_found.items()):
    print(f"  {var}: {len(positions)}x")

# Fix duplicates: keep the FIRST occurrence, change subsequent ones to reassignment
total_fixed = 0
for var, positions in vars_found.items():
    if len(positions) > 1:
        for pos in positions[1:]:
            # Replace 'let varName =' with 'varName = varName ||'
            old = content[pos : pos + len(f"let {var} =")]
            new = f"{var} = {var} ||"
            content = content[:pos] + new + content[pos + len(old) :]
            total_fixed += 1
            print(f"  Fixed {var} at {pos}: {old} -> {new}")

print(f"\nTotal fixes: {total_fixed}")

# Verify all duplicates are gone
matches_after = list(re.finditer(pattern, content))
vars_after = {}
for m in matches_after:
    var_name = m.group(1)
    if var_name not in vars_after:
        vars_after[var_name] = 0
    vars_after[var_name] += 1

still_dup = {k: v for k, v in vars_after.items() if v > 1}
if still_dup:
    print(f"\nStill duplicated: {still_dup}")
else:
    print(f"\n✅ All OMR variables are unique now!")

with open(V3_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print(f"File saved: {len(content)} chars")
