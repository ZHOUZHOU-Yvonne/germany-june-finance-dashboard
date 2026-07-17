#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update Tab 5 (政策总览) in index.html with July Feishu data."""

import json
import re

# Load the new comp data from Feishu
with open('feishu_comp_july.json', 'r', encoding='utf-8') as f:
    new_comp = json.load(f)

# Read the current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════
# 1. Update comp data in D object
# ═══════════════════════════════════════════════════════

# Helper function to convert comp data to the format used in HTML
def comp_to_js_array(comp_list):
    """Convert comp list to JavaScript array string."""
    items = []
    for c in comp_list:
        # Build the changes object
        changes_js = {}
        for metric, ch in c.get('changes', {}).items():
            changes_js[metric] = {
                'current': ch.get('current'),
                'previous': ch.get('previous'),
                'change': ch.get('change')
            }

        item = {
            'brand': c['brand'],
            'model': c['model'],
            'version': c['version'],
            'level': c.get('level', ''),
            'current': c.get('current', {}),
            'previous': c.get('previous', {}),
            'changes': changes_js,
            'has_key_change': c.get('has_key_change', False)
        }
        items.append(item)

    return json.dumps(items, ensure_ascii=False)

# Replace comp_su7
new_comp_su7_js = comp_to_js_array(new_comp['comp_su7'])
old_comp_su7_pattern = r'("comp_su7"\s*:\s*)\[.*?\](?=,\s*"comp_yu7")'
html = re.sub(old_comp_su7_pattern, r'\1' + new_comp_su7_js, html, flags=re.DOTALL)

# Replace comp_yu7
new_comp_yu7_js = comp_to_js_array(new_comp['comp_yu7'])
old_comp_yu7_pattern = r'("comp_yu7"\s*:\s*)\[.*?\](?=,\s*"comp_ultra")'
html = re.sub(old_comp_yu7_pattern, r'\1' + new_comp_yu7_js, html, flags=re.DOTALL)

# Replace comp_ultra
new_comp_ultra_js = comp_to_js_array(new_comp['comp_ultra'])
old_comp_ultra_pattern = r'("comp_ultra"\s*:\s*)\[.*?\](?=,\s*"top_)'
html = re.sub(old_comp_ultra_pattern, r'\1' + new_comp_ultra_js, html, flags=re.DOTALL)

# ═══════════════════════════════════════════════════════
# 2. Update month labels in Tab 5
# ═══════════════════════════════════════════════════════

# Update "6月 vs 5月" to "7月 vs 6月" in the section header
html = html.replace('6月 vs 5月', '7月 vs 6月')

# ═══════════════════════════════════════════════════════
# 3. Save the updated file
# ═══════════════════════════════════════════════════════

output_file = 'index_july.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Updated file saved to: {output_file}")
print(f"\nChanges made:")
print(f"  - Updated comp_su7 with {len(new_comp['comp_su7'])} entries")
print(f"  - Updated comp_yu7 with {len(new_comp['comp_yu7'])} entries")
print(f"  - Updated comp_ultra with {len(new_comp['comp_ultra'])} entries")
print(f"  - Updated month labels from '6月 vs 5月' to '7月 vs 6月'")
