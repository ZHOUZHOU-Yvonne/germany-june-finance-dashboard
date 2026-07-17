#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean update of index_july.html with merged data and filters."""

import json
import re

# Load merged data
with open('merged_comp.json', 'r', encoding='utf-8') as f:
    merged_data = json.load(f)

# Read the original index.html (fresh copy)
with open('index_july.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════
# 1. Update comp data in HTML
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

# Replace each comp array
for key in ['comp_su7', 'comp_yu7', 'comp_ultra']:
    new_js = comp_to_js_array(merged_data[key])
    pattern = r'("' + key + r'"\s*:\s*)\[.*?\](?=,\s*"comp_)'
    if key == 'comp_ultra':
        pattern = r'("' + key + r'"\s*:\s*)\[.*?\](?=,\s*"top_)'
    html = re.sub(pattern, r'\1' + new_js, html, flags=re.DOTALL)

# ═══════════════════════════════════════════════════════
# 2. Add CSS for filters
# ═══════════════════════════════════════════════════════

filter_css = """
/* Tab 5 Filter Buttons */
.t5-filters{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 16px;max-width:960px;margin-left:auto;margin-right:auto}
.t5-filter-group{display:flex;gap:4px;align-items:center}
.t5-filter-label{font-size:11px;color:#889;margin-right:4px}
.t5-filter-btn{padding:5px 12px;border-radius:15px;font-size:11px;font-weight:500;cursor:pointer;border:1px solid #2a2a3a;background:#1a1a2e;color:#889;transition:all .2s}
.t5-filter-btn:hover{border-color:#5cccf5;color:#5cccf5}
.t5-filter-btn.active{background:rgba(92,204,245,.15);border-color:#5cccf5;color:#5cccf5}
.t5-filter-sep{width:1px;height:20px;background:#2a2a3a;margin:0 8px}
"""

# Insert CSS before </style>
html = html.replace('</style>', filter_css + '</style>', 1)

# ═══════════════════════════════════════════════════════
# 3. Update brand cards section with filters
# ═══════════════════════════════════════════════════════

# Find and replace the brand cards section
old_section_start = "  // Brand cards section"
old_section_end = "  ch+='<div class=\"t5-grid\">';"

# Find the position
start_pos = html.find(old_section_start)
end_pos = html.find(old_section_end) + len(old_section_end)

if start_pos != -1 and end_pos != -1:
    # Extract the old section
    old_section = html[start_pos:end_pos]

    # Create new section with filters
    new_section = """  // Brand cards section
  var ch='<div class="t5-sec-hdr" style="max-width:960px;margin:28px auto 16px"><div><div class="t5-sec-title">各品牌金融政策变化 <span style="display:inline-block;font-size:11px;font-weight:600;color:#5cccf5;background:rgba(92,204,245,.1);border:1px solid rgba(92,204,245,.25);padding:2px 8px;border-radius:4px;vertical-align:middle;margin-left:6px">36个月/20kkm | 48个月/10kkm</span></div><div class="t5-sec-sub">Brand Financial Policy Changes · 7月 vs 6月</div></div></div>';
  ch+='<div class="t5-filters" id="t5filters">';
  ch+='<div class="t5-filter-group"><span class="t5-filter-label">期限:</span>';
  ch+='<button class="t5-filter-btn active" onclick="t5filterTerm(36)">36个月/20kkm</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterTerm(48)">48个月/10kkm</button></div>';
  ch+='<div class="t5-filter-sep"></div>';
  ch+='<div class="t5-filter-group"><span class="t5-filter-label">配置:</span>';
  ch+='<button class="t5-filter-btn active" onclick="t5filterLevel(\\'all\\')">全部</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterLevel(\\'低配\\')">低配</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterLevel(\\'高配\\')">高配</button></div>';
  ch+='<div class="t5-filter-sep"></div>';
  ch+='<div class="t5-filter-group"><span class="t5-filter-label">竞品:</span>';
  ch+='<button class="t5-filter-btn active" onclick="t5filterSheet(\\'all\\')">全部</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterSheet(\\'SU7\\')">SU7竞品</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterSheet(\\'YU7\\')">YU7竞品</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterSheet(\\'Ultra\\')">Ultra竞品</button></div>';
  ch+='<div class="t5-filter-sep"></div>';
  ch+='<div class="t5-filter-group"><span class="t5-filter-label">变化:</span>';
  ch+='<button class="t5-filter-btn active" onclick="t5filterChange(\\'all\\')">全部</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterChange(\\'yes\\')">有变化</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterChange(\\'no\\')">无变化</button></div>';
  ch+='</div>';
  ch+='<div class="t5-grid" id="t5grid">';"""

    html = html[:start_pos] + new_section + html[end_pos:]

# ═══════════════════════════════════════════════════════
# 4. Update card generation to include data attributes
# ═══════════════════════════════════════════════════════

# Find the card generation code
old_card = """    ch+='<div class="t5-card" onclick="t5dOpen(\\''+brand+'\\')">';
    ch+='<div class="t5-card-hdr" style="border-left:3px solid '+bc+'">';
    ch+='<div class="t5-card-dot" style="background:'+bc+'"></div>';
    ch+='<span class="t5-card-name">'+brand+'</span>';
    ch+='<span class="t5-card-tag '+(hasChange?'up':'flat')+'">'+(hasChange?'有变化':'无变化')+'</span>';
    ch+='</div>';"""

new_card = """    // Get the first entry's level for filtering
    var firstEntry = null;
    for(var mk in bd.models) {
      if(bd.models[mk].length > 0) {
        firstEntry = bd.models[mk][0];
        break;
      }
    }
    var cardLevel = firstEntry ? firstEntry.level : '';

    ch+='<div class="t5-card" data-level="'+cardLevel+'" data-sheet="'+getSheetForBrand(brand)+'" data-change="'+(hasChange?'yes':'no')+'" onclick="t5dOpen(\\''+brand+'\\')">';
    ch+='<div class="t5-card-hdr" style="border-left:3px solid '+bc+'">';
    ch+='<div class="t5-card-dot" style="background:'+bc+'"></div>';
    ch+='<span class="t5-card-name">'+brand+'</span>';
    ch+='<span class="t5-card-tag '+(hasChange?'up':'flat')+'">'+(hasChange?'有变化':'无变化')+'</span>';
    ch+='</div>';"""

html = html.replace(old_card, new_card, 1)

# ═══════════════════════════════════════════════════════
# 5. Add JavaScript for filtering
# ═══════════════════════════════════════════════════════

filter_js = """
// Tab 5 Filter functionality
var t5FilterTerm = 36;
var t5FilterLevel = 'all';
var t5FilterSheet = 'all';
var t5FilterChange = 'all';

function getSheetForBrand(brand) {
  if (brand === '特斯拉') return 'SU7,YU7';
  if (brand === '奔驰') return 'SU7,YU7,Ultra';
  if (brand === '奥迪') return 'YU7,Ultra';
  if (brand === '大众') return 'SU7,YU7';
  if (brand === '宝马') return 'SU7,YU7,Ultra';
  if (brand === '比亚迪') return 'SU7,YU7';
  if (brand === '保时捷') return 'YU7,Ultra';
  if (brand === '小鹏') return 'YU7';
  if (brand === '斯柯达') return 'YU7';
  if (brand === '极氪') return 'SU7';
  if (brand === '现代') return 'SU7';
  if (brand === '马自达') return 'SU7';
  if (brand === 'Lotus') return 'Ultra';
  if (brand === 'Polestar') return 'Ultra';
  return 'other';
}

function t5filterTerm(term) {
  t5FilterTerm = term;
  // Update button states
  var buttons = document.querySelectorAll('.t5-filter-group')[0].querySelectorAll('.t5-filter-btn');
  buttons.forEach(function(btn) {
    btn.classList.remove('active');
    if ((term === 36 && btn.textContent.indexOf('36') !== -1) ||
        (term === 48 && btn.textContent.indexOf('48') !== -1)) {
      btn.classList.add('active');
    }
  });
  t5applyFilters();
}

function t5filterLevel(level) {
  t5FilterLevel = level;
  var buttons = document.querySelectorAll('.t5-filter-group')[1].querySelectorAll('.t5-filter-btn');
  buttons.forEach(function(btn) {
    btn.classList.remove('active');
    if ((level === 'all' && btn.textContent === '全部') ||
        (level === '低配' && btn.textContent === '低配') ||
        (level === '高配' && btn.textContent === '高配')) {
      btn.classList.add('active');
    }
  });
  t5applyFilters();
}

function t5filterSheet(sheet) {
  t5FilterSheet = sheet;
  var buttons = document.querySelectorAll('.t5-filter-group')[2].querySelectorAll('.t5-filter-btn');
  buttons.forEach(function(btn) {
    btn.classList.remove('active');
    if ((sheet === 'all' && btn.textContent === '全部') ||
        (sheet === 'SU7' && btn.textContent === 'SU7竞品') ||
        (sheet === 'YU7' && btn.textContent === 'YU7竞品') ||
        (sheet === 'Ultra' && btn.textContent === 'Ultra竞品')) {
      btn.classList.add('active');
    }
  });
  t5applyFilters();
}

function t5filterChange(change) {
  t5FilterChange = change;
  var buttons = document.querySelectorAll('.t5-filter-group')[3].querySelectorAll('.t5-filter-btn');
  buttons.forEach(function(btn) {
    btn.classList.remove('active');
    if ((change === 'all' && btn.textContent === '全部') ||
        (change === 'yes' && btn.textContent === '有变化') ||
        (change === 'no' && btn.textContent === '无变化')) {
      btn.classList.add('active');
    }
  });
  t5applyFilters();
}

function t5applyFilters() {
  var cards = document.querySelectorAll('.t5-card');
  cards.forEach(function(card) {
    var cardLevel = card.getAttribute('data-level') || '';
    var cardSheet = card.getAttribute('data-sheet') || '';
    var cardChange = card.getAttribute('data-change') || '';

    var showLevel = t5FilterLevel === 'all' || cardLevel === t5FilterLevel;
    var showSheet = t5FilterSheet === 'all' || cardSheet.indexOf(t5FilterSheet) !== -1;
    var showChange = t5FilterChange === 'all' || cardChange === t5FilterChange;

    if (showLevel && showSheet && showChange) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
}
"""

# Insert JavaScript before the closing </script> tag
html = html.replace('</script>', filter_js + '\n</script>', 1)

# ═══════════════════════════════════════════════════════
# 6. Save the updated file
# ═══════════════════════════════════════════════════════

output_file = 'index_july.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Clean update saved to: {output_file}")
print("\nFeatures:")
print("  - All original brands preserved")
print("  - Feishu data updated for: 特斯拉, 奔驰, 奥迪")
print("  - Filter: 36个月/20kkm | 48个月/10kkm")
print("  - Filter: 全部 | 低配 | 高配")
print("  - Filter: 全部 | SU7竞品 | YU7竞品 | Ultra竞品")
print("  - Filter: 全部 | 有变化 | 无变化")
