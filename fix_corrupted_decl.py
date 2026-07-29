#!/usr/bin/env python3
"""Fix corrupted omrHistorico/omrStream declarations and improve BNCC extraction."""

import os
import re

home = os.path.expanduser('~')
V3_PATH = os.path.join(home, 'Secret\u00e1ria', 'Download', 'planejador-escolar-v3.0.html')

with open(V3_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix garbled omrHistorico/omrStream
old_garbled = 'mrHistorico = omrHistoomrStream = omrStream ||storico = []'
new_clean = 'omrHistorico = []; omrStream = null'
if old_garbled in content:
    content = content.replace(old_garbled, new_clean)
    print('Fixed garbled omrHistorico/omrStream declaration')
else:
    print('Could not find garbled text - checking for omrHistorico')
    idx = content.find('omrHistorico')
    if idx >= 0:
        print('  Found omrHistorico at', idx, ':', repr(content[idx:idx+120]))

# 2. Fix wrong omrStream = omrStream || {}
wrong_stream = 'omrStream = omrStream || {}'
count = content.count(wrong_stream)
if count > 0:
    content = content.replace(wrong_stream, 'omrStream = null', count)
    print('Fixed', count, 'x wrong omrStream assignment')

# 3. Fix BNCC extraction to filter short terms
old_bncc = '''  // 4. Try to extract meaningful terms from BNCC descriptions (filtered)'''
# The short marker for the NEW bncc code
new_bncc_code = '''  // 4. Try to extract meaningful terms from BNCC descriptions
  try {
    if (typeof PRESETS !== 'undefined' && PRESETS[disc] && PRESETS[disc].bnccPorPeriodo) {
      var periods = PRESETS[disc].bnccPorPeriodo;
      for (var modelKey in periods) {
        var model = periods[modelKey];
        if (Array.isArray(model)) {
          model.forEach(function(code) {
            if (typeof code === 'string') {
              var clean = code.replace(/[0-9]/g, ' ').trim();
              clean.split(/\\s+/).forEach(function(p) {
                if (p.length > 4 && words.indexOf(p.toUpperCase()) < 0) {
                  words.push(p.toUpperCase());
                }
              });
            }
          });
        }
      }
    }
  } catch(e) {}'''

if old_bncc in content:
    start = content.find(old_bncc)
    # Find the end of this try-catch block
    end = content.find('  } catch(e) {}', start)
    if end > 0:
        end = end + len('  } catch(e) {}')
    else:
        end = start + len(old_bncc) + 200
    content = content[:start] + new_bncc_code + content[end:]
    print('Fixed BNCC extraction to filter short terms')
else:
    print('Could not find BNCC extraction marker')

# 4. Syntax check
s = content.find('<script>')
e = content.find('</script>')
js = content[s+len('<script>'):e]
ob = js.count('{')
cb = js.count('}')
print('Braces:', ob, 'open,', cb, 'close, diff=', ob-cb)

# Check for remaining issues
for bad in ['omrStream = omrStream || {}', 'omrHistoomrStream']:
    if bad in content:
        print('STILL PRESENT:', bad)

with open(V3_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print('File saved:', len(content), 'chars')
