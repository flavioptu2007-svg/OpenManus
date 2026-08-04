#!/usr/bin/env python3
"""Fix the duplicate `let omrImageBase64 = null` declaration in the v3.0 file."""

import os


home = os.path.expanduser("~")
V3_PATH = os.path.join(
    home, "Secret\u00e1ria", "Download", "planejador-escolar-v3.0.html"
)

with open(V3_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix duplicate let omrImageBase64
count = content.count("let omrImageBase64 = null")
print(f"'let omrImageBase64 = null' found: {count}x")

if count > 1:
    # Find all occurrences and change all but first to 'omrImageBase64 = omrImageBase64 || null'
    idx = 0
    found = 0
    while True:
        idx = content.find("let omrImageBase64 = null", idx)
        if idx < 0:
            break
        found += 1
        if found > 1:
            print(f"  Fixing occurrence #{found} at position {idx}")
            content = (
                content[:idx]
                + "omrImageBase64 = omrImageBase64 || null"
                + content[idx + len("let omrImageBase64 = null") :]
            )
        idx += 1

# Verify
count_after = content.count("let omrImageBase64 = null")
print(f"After fix: 'let omrImageBase64 = null' found: {count_after}x")

# 2. Verify CP functions exist
cp_funcs = [
    "function cpSetMode",
    "function cpPopulateDiscSelect",
    "function cpPopulatePeriodSelect",
    "function cpLoadDiscVocab",
    "function cpGenerateFromDisc",
    "var cpGenerateOriginal",
    "var cpLoadThemeOriginal",
    "cpDiscVocabBase",
]
print(f"\nCP function presence:")
for fn in cp_funcs:
    count = content.count(fn)
    print(f"  {fn}: {count}x")

# 3. Check braces balance
s = content.find("<script>")
e = content.find("</script>")
block = content[s:e]
ob = block.count("{")
cb = block.count("}")
print(f"\nBraces balance: {ob} open, {cb} close, diff={ob-cb}")

# 4. Quick syntax check using node
import subprocess


with open("/tmp/v3_jogos.js", "w") as f:
    f.write(block)
result = subprocess.run(
    ["node", "--check", "/tmp/v3_jogos.js"], capture_output=True, text=True, timeout=10
)
if result.returncode == 0:
    print("✅ Node syntax check: OK")
else:
    print(f"❌ Node syntax error: {result.stderr[:300]}")

with open(V3_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print(f"\nFile saved: {len(content)} chars")
