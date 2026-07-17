#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge Feishu data with original dashboard data and add 48个月 filter."""

import json
import re

# Load the new comp data from Feishu
with open('feishu_comp_full.json', 'r', encoding='utf-8') as f:
    feishu_data = json.load(f)

feishu_brands = set(c['brand'] for c in feishu_data['all_comp'])
print(f"Feishu brands: {sorted(feishu_brands)}")

# Read the original index.html to get original comp data
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract original comp data
original_comp = {}
for key in ['comp_su7', 'comp_yu7', 'comp_ultra']:
    match = re.search(r'\"' + key + r'\":\s*(\[.*?\])', html)
    if match:
        original_comp[key] = json.loads(match.group(1))
        brands = set(c['brand'] for c in original_comp[key])
        print(f"Original {key}: {len(original_comp[key])} entries, brands: {sorted(brands)}")

# Merge: keep original entries for brands NOT in Feishu, update brands IN Feishu
merged_comp = {}
for key in ['comp_su7', 'comp_yu7', 'comp_ultra']:
    merged = []
    for entry in original_comp[key]:
        if entry['brand'] in feishu_brands:
            # Find matching Feishu entry
            for feishu_entry in feishu_data['all_comp']:
                if (feishu_entry['brand'] == entry['brand'] and
                    feishu_entry['model'] == entry['model']):
                    # Update with Feishu data (July vs June)
                    merged.append(feishu_entry)
                    print(f"  Updated: {feishu_entry['brand']} {feishu_entry['model']}")
                    break
            else:
                # No matching Feishu entry, keep original
                merged.append(entry)
                print(f"  Kept (no Feishu match): {entry['brand']} {entry['model']}")
        else:
            # Brand not in Feishu, keep original
            merged.append(entry)
            print(f"  Kept (not in Feishu): {entry['brand']} {entry['model']}")
    merged_comp[key] = merged

print(f"\n=== Merged Summary ===")
for key, entries in merged_comp.items():
    brands = set(c['brand'] for c in entries)
    print(f"{key}: {len(entries)} entries, brands: {sorted(brands)}")

# Save merged data
with open('merged_comp.json', 'w', encoding='utf-8') as f:
    json.dump(merged_comp, f, ensure_ascii=False, indent=2, default=str)

print("\nSaved to merged_comp.json")
