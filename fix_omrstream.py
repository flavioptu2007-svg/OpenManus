#!/usr/bin/env python3
"""Fix the last remaining omrStream duplicate."""

import os

home = os.path.expanduser('~')
V3_PATH = os.path.join(home, 'Secret\u00e1ria', 'Download', 'planejador-escolar-v3.0.html')

with open(V3_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Check all occurrences of omrStream
import re
pattern = r'(let\s+omrStream\s*=\s*[^;]+;)'
matches = list(re.finditer(pattern, content))
print(f"'let omrStream =' occurrences: {len(matches)}")
for i, m in enumerate(matches):
    context = content[max(0,m.start()-10):m.end()+10]
    print(f"  #{i+1}: ...{context!r}...")

# Also check for 'omrStream' in different scopes
all_omrStream = [m.start() for m in re.finditer(r'omrStream', content)]
print(f"\nTotal 'omrStream' references: {len(all_omrStream)}")

# If there are 2+ let declarations, fix all but the first
fixed = 0
for i, m in enumerate(matches):
    if i == 0: continue  # keep first
    old = m.group(0)
    # Extract variable name
    var_match = re.match(r'let\s+(omr\w+)\s*=', old)
    if var_match:
        var_name = var_match.group(1)
        new = f'{var_name} = {var_name} || {{}}'
        print(f"  Fixing #{i+1}: {old[:50]}... -> {new}")
        content = content[:m.start()] + new + content[m.end():]
        fixed += 1

print(f"\nFixed: {fixed}")

# Final check
final_matches = list(re.finditer(pattern, content))
print(f"Final 'let omrStream =' occurrences: {len(final_matches)}")

with open(V3_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"File saved: {len(content)} chars")
