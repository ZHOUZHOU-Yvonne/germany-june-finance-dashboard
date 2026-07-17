#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update Tab 5 with ALL brand/model data from Feishu."""

import json
import re

# Load the full comp data
with open('feishu_comp_full.json', 'r', encoding='utf-8') as f:
    full_data = json.load(f)

all_comp = full_data['all_comp']

# Read the current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════
# Build the comp data in the format expected by the HTML
# ═══════════════════════════════════════════════════════

def comp_to_js_array(comp_list):
    """Convert comp list to JavaScript array string."""
    items = []
    for c in comp_list:
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

# Split comp data by source (SU7/YU7/Ultra)
# Based on the original structure:
# - SU7: 特斯拉 Model 3, 奔驰 CLA
# - YU7: 特斯拉 Model Y, 奔驰 EQA
# - Ultra: 奥迪 e-tron GT, 奔驰 EQE

comp_su7 = [c for c in all_comp if (c['model'] == 'Model 3' or c['model'] == 'CLA')]
comp_yu7 = [c for c in all_comp if (c['model'] == 'Model Y' or c['model'] == 'EQA')]
comp_ultra = [c for c in all_comp if (c['model'] == 'e-tron GT' or c['model'] == 'EQE')]

print(f"SU7 entries: {len(comp_su7)}")
print(f"YU7 entries: {len(comp_yu7)}")
print(f"Ultra entries: {len(comp_ultra)}")

# Replace comp_su7
new_comp_su7_js = comp_to_js_array(comp_su7)
old_comp_su7_pattern = r'("comp_su7"\s*:\s*)\[.*?\](?=,\s*"comp_yu7")'
html = re.sub(old_comp_su7_pattern, r'\1' + new_comp_su7_js, html, flags=re.DOTALL)

# Replace comp_yu7
new_comp_yu7_js = comp_to_js_array(comp_yu7)
old_comp_yu7_pattern = r'("comp_yu7"\s*:\s*)\[.*?\](?=,\s*"comp_ultra")'
html = re.sub(old_comp_yu7_pattern, r'\1' + new_comp_yu7_js, html, flags=re.DOTALL)

# Replace comp_ultra
new_comp_ultra_js = comp_to_js_array(comp_ultra)
old_comp_ultra_pattern = r'("comp_ultra"\s*:\s*)\[.*?\](?=,\s*"top_)'
html = re.sub(old_comp_ultra_pattern, r'\1' + new_comp_ultra_js, html, flags=re.DOTALL)

# Update month labels
html = html.replace('6月 vs 5月', '7月 vs 6月')

# Save the updated file
output_file = 'index_july.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nUpdated file saved to: {output_file}")
print(f"Total entries updated: {len(all_comp)}")
