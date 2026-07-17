#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add filter functionality to Tab 5 for 高配/低配 and SU7/YU7/Ultra."""

import re

# Read the current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════
# 1. Add CSS for filter buttons
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
# 2. Add filter HTML before the grid
# ═══════════════════════════════════════════════════════

filter_html = """
<div class="t5-filters" id="t5filters">
  <div class="t5-filter-group">
    <span class="t5-filter-label">配置:</span>
    <button class="t5-filter-btn active" onclick="t5filterLevel('all')">全部</button>
    <button class="t5-filter-btn" onclick="t5filterLevel('低配')">低配</button>
    <button class="t5-filter-btn" onclick="t5filterLevel('高配')">高配</button>
  </div>
  <div class="t5-filter-sep"></div>
  <div class="t5-filter-group">
    <span class="t5-filter-label">竞品:</span>
    <button class="t5-filter-btn active" onclick="t5filterSheet('all')">全部</button>
    <button class="t5-filter-btn" onclick="t5filterSheet('SU7')">SU7竞品</button>
    <button class="t5-filter-btn" onclick="t5filterSheet('YU7')">YU7竞品</button>
    <button class="t5-filter-btn" onclick="t5filterSheet('Ultra')">Ultra竞品</button>
  </div>
  <div class="t5-filter-sep"></div>
  <div class="t5-filter-group">
    <span class="t5-filter-label">变化:</span>
    <button class="t5-filter-btn active" onclick="t5filterChange('all')">全部</button>
    <button class="t5-filter-btn" onclick="t5filterChange('yes')">有变化</button>
    <button class="t5-filter-btn" onclick="t5filterChange('no')">无变化</button>
  </div>
</div>
"""

# Insert filter HTML before the grid
html = html.replace(
    "ch+='<div class=\"t5-grid\">';",
    "ch+='" + filter_html.replace("'", "\\'").replace("\n", "") + "';\n  ch+='<div class=\"t5-grid\" id=\"t5grid\">';",
    1
)

# ═══════════════════════════════════════════════════════
# 3. Add sheet info to each card for filtering
# ═══════════════════════════════════════════════════════

# Update the card generation to include data attributes for filtering
# Find the card generation code and add data attributes
old_card_code = "ch+='<div class=\"t5-card\" onclick=\"t5dOpen(\\''+brand+'\\')\">';"
new_card_code = """ch+='<div class="t5-card" data-level="'+e0.level+'" data-sheet="'+getSheetForBrand(brand)+'" data-change="'+(hasChange?'yes':'no')+'" onclick="t5dOpen(\\''+brand+'\\')">';"""

html = html.replace(old_card_code, new_card_code, 1)

# ═══════════════════════════════════════════════════════
# 4. Add JavaScript for filtering
# ═══════════════════════════════════════════════════════

filter_js = """
// Tab 5 Filter functionality
var t5FilterLevel = 'all';
var t5FilterSheet = 'all';
var t5FilterChange = 'all';

function getSheetForBrand(brand) {
  // Map brands to their sheet
  if (brand === '特斯拉') return 'SU7,YU7';  // 特斯拉 appears in both SU7 and YU7
  if (brand === '奔驰') return 'SU7,YU7,Ultra';  // 奔驰 appears in all sheets
  if (brand === '奥迪') return 'Ultra';
  return 'other';
}

function t5filterLevel(level) {
  t5filterUpdate('level', level);
}

function t5filterSheet(sheet) {
  t5filterUpdate('sheet', sheet);
}

function t5filterChange(change) {
  t5filterUpdate('change', change);
}

function t5filterUpdate(type, value) {
  // Update active state
  if (type === 'level') t5FilterLevel = value;
  if (type === 'sheet') t5FilterSheet = value;
  if (type === 'change') t5FilterChange = value;

  // Update button states
  var filterGroup = type === 'level' ? 0 : (type === 'sheet' ? 1 : 2);
  var buttons = document.querySelectorAll('.t5-filter-group')[filterGroup].querySelectorAll('.t5-filter-btn');
  buttons.forEach(function(btn) {
    btn.classList.remove('active');
    if ((value === 'all' && btn.textContent === '全部') ||
        (value === '低配' && btn.textContent === '低配') ||
        (value === '高配' && btn.textContent === '高配') ||
        (value === 'SU7' && btn.textContent === 'SU7竞品') ||
        (value === 'YU7' && btn.textContent === 'YU7竞品') ||
        (value === 'Ultra' && btn.textContent === 'Ultra竞品') ||
        (value === 'yes' && btn.textContent === '有变化') ||
        (value === 'no' && btn.textContent === '无变化')) {
      btn.classList.add('active');
    }
  });

  // Apply filters
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

# Save the updated file
output_file = 'index_july.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Filter functionality added to: {output_file}")
print("\nFilter features:")
print("  - 配置筛选: 全部 / 低配 / 高配")
print("  - 竞品筛选: 全部 / SU7竞品 / YU7竞品 / Ultra竞品")
print("  - 变化筛选: 全部 / 有变化 / 无变化")
