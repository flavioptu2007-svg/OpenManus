#!/usr/bin/env python3
"""Insert new questions into quiz_historico.html before the closing ]; of PERGUNTAS."""
import re
import sys


html_path = "/home/flavio/OpenManus/quiz_historico.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Load new questions
with open("gerar_perguntas_extra2.py", "r", encoding="utf-8") as f:
    script = f.read()

# Extract the NOVAS_PERGUNTAS block - find content between triple quotes
start = script.find('NOVAS_PERGUNTAS = "')
start = script.find('"""', start) + 3
end = script.find('"""', start)
novas = script[start:end]

print(f"New questions to insert: {len(novas)} chars")

# Insert before the closing ]; of PERGUNTAS
# Find the last ], before Conquistas
end_marker = "    ];\n\n    // ---- Conquistas"
# But the actual file might have different spacing. Let's find it differently.
# Find the last occurrence of "    ];" that is followed by a blank line and "    //"
pos = content.rfind("    ];\n\n    //")
if pos == -1:
    # Try alternative patterns
    pos = content.rfind("    ];\n    //")
if pos == -1:
    print("ERROR: Could not find insertion point!")
    print("Last 200 chars:")
    print(content[-200:])
    sys.exit(1)

new_content = content[:pos] + novas + "\n" + content[pos:]

with open(html_path, "w", encoding="utf-8") as f:
    f.write(new_content)

q_count = len(re.findall(r'id:"q\d+"', new_content))
new_count = len(re.findall(r'id:"q\d+"', novas))
print(f"Total questions: {q_count}")
print(f"Inserted: {new_count} new questions")
