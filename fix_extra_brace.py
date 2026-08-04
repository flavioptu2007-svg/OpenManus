#!/usr/bin/env python3
"""Fix the pre-existing extra '}' in the v3.0 file and verify syntax."""

import os


home = os.path.expanduser("~")
V3_PATH = os.path.join(
    home, "Secret\u00e1ria", "Download", "planejador-escolar-v3.0.html"
)

with open(V3_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# The pattern from the analysis: 's:3, revisoes:6 }\n  }  }\n};'
# The extra brace is the second '}' on the line '  }  }'
# Fix: replace '  }  }\n};' with '  }\n};'

target = "  }  }\n};"
replacement = "  }\n};"

count = content.count(target)
print(f"Found {count} occurrence(s) of '{repr(target)}'")

if count > 0:
    content = content.replace(target, replacement, 1)
    print("Replaced first occurrence")

# Verify brace balance
s = content.find("<script>")
e = content.find("</script>")
block = content[s:e]
ob = block.count("{")
cb = block.count("}")
print(f"Script block: {ob} open braces, {cb} close braces, diff={ob-cb}")

if ob == cb:
    print("✅ Braces balanced!")
else:
    print(f"❌ Braces still unbalanced: diff={ob-cb}")
    # Try finding more patterns
    orig = block[: block.find("const cpThemes")]
    ob2 = orig.count("{")
    cb2 = orig.count("}")
    print(f"  Original section: {ob2} open, {cb2} close, diff={ob2-cb2}")

with open(V3_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print(f"\nFile size: {len(content)} chars")
