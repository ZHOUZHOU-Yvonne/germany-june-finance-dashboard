#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final complete update - parse all sheets, add 48期, fix filters."""

import json, re

def pv(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).strip()
    if s in ('', '/', '-', '--', '#VALUE!', '#REF!', 'NO INFO'): return None
    s = s.replace(',','').replace('€','').replace('%','').replace(' ','')
    s = re.sub(r'\(.*?\)', '', s)
    try: return float(s)
    except: return None

# ═══════════════════════════════════════════════════════
# Row structure (same for all sheets)
# ═══════════════════════════════════════════════════════
# Row 0: 品牌, Row 1: 更新时间, Row 2: 车型, Row 3: 版本, Row 4: 配置
# Row 5: MSRP, Row 6: 补贴政策时效, Row 7: 官网主机厂售价补贴
# Row 8: RV 36, Row 9: RV 48, Row 10: RV%, Row 11: 首付, Row 12: 贷款政策
# 48期分期: Row 13 对客定价, Row 14 月供, Row 15 尾款, Row 16 贴息
# 36期分期: Row 17 对客定价, Row 18 月供, Row 19 尾款, Row 20 贴息
# 36期租赁: Row 22 租金, Row 23 理论月租, Row 24 贴息, Row 25 LF
# 48期租赁: Row 27 租金, Row 28 理论月租, Row 29 贴息

METRICS_36_FIN = {'分期月供-36': 18, '官网尾款-36': 19, '贴息成本-分期-36': 20, '对客定价-36': 17}
METRICS_48_FIN = {'分期月供-48': 14, '官网尾款-48': 15, '贴息成本-分期-48': 16, '对客定价-48': 13}
METRICS_36_LEAS = {'租赁租金-36': 22, '理论月租-36': 23, '贴息成本-租赁-36': 24, 'Leasing factor-36': 25}
METRICS_48_LEAS = {'租赁租金-48': 27, '理论月租-48': 28, '贴息成本-租赁-48': 29}

# ═══════════════════════════════════════════════════════
# Column groups for each sheet
# ═══════════════════════════════════════════════════════
SU7_GROUPS = [
    {'brand':'特斯拉','model':'Model 3','version':'LongRange RWD','level':'低配','cols':list(range(2,10))},
    {'brand':'特斯拉','model':'Model 3','version':'AWD Performance','level':'高配','cols':list(range(10,18))},
    {'brand':'奔驰','model':'CLA','version':'250+ mit EQ Technologie Edition','level':'低配','cols':list(range(18,26))},
    {'brand':'奔驰','model':'CLA','version':'350 mit EQ Technologie Edition','level':'高配','cols':list(range(26,30))},
]

YU7_GROUPS = [
    {'brand':'特斯拉','model':'Model Y','version':'LongRange AWD','level':'低配','cols':list(range(2,10))},
    {'brand':'特斯拉','model':'Model Y','version':'Performance AWD','level':'高配','cols':list(range(10,18))},
    {'brand':'奔驰','model':'EQA','version':'300 4MATIC Electric Art','level':'低配','cols':list(range(18,23))},
    {'brand':'奔驰','model':'EQA','version':'350 4MATIC AMG Line Premium','level':'高配','cols':list(range(23,28))},
    {'brand':'大众','model':'ID.4','version':'Pro with infotainment package','level':'低配','cols':list(range(28,36))},
    {'brand':'大众','model':'ID.5','version':'Pro with infotainment package','level':'低配','cols':list(range(36,44))},
    {'brand':'大众','model':'ID.5','version':'GTX with infotainment package','level':'高配','cols':list(range(44,52))},
    {'brand':'宝马','model':'ix1','version':'eDrive20 Xline','level':'低配','cols':list(range(52,57))},
]

ULTRA_GROUPS = [
    {'brand':'奥迪','model':'e-tron GT','version':'S','level':'低配','cols':list(range(2,10))},
    {'brand':'奥迪','model':'e-tron GT','version':'RS','level':'高配','cols':list(range(10,18))},
    {'brand':'奔驰','model':'EQE','version':'AMG EQE 53 4MATIC+','level':'高配','cols':list(range(18,26))},
    {'brand':'保时捷','model':'Taycan','version':'4S Black Edition','level':'低配','cols':list(range(26,34))},
    {'brand':'保时捷','model':'Taycan','version':'GTS','level':'高配','cols':list(range(34,42))},
    {'brand':'特斯拉','model':'Model S','version':'All-wheel drive','level':'低配','cols':list(range(42,45))},
    {'brand':'特斯拉','model':'Model S','version':'Plaid','level':'高配','cols':list(range(45,48))},
    {'brand':'宝马','model':'i5','version':'eDrive40 Limousine M Sportpaket','level':'低配','cols':list(range(48,56))},
    {'brand':'宝马','model':'i5','version':'BMW i5 M60 xDrive Limousine','level':'高配','cols':list(range(56,57))},
]

def extract_data(data, groups):
    """Extract comp data from sheet data."""
    results = []
    for g in groups:
        cols = g['cols']
        july_vals = {}  # metric -> value
        june_vals = {}

        for c in cols:
            if c >= len(data[1]): continue
            date_val = data[1][c]
            if not date_val: continue
            date_str = str(date_val).strip()
            m = re.match(r'(\d{4})年(\d{1,2})月', date_str)
            if not m: continue
            month_key = f"{m.group(1)}-{m.group(2).zfill(2)}"

            target = july_vals if month_key == '2026-07' else (june_vals if month_key == '2026-06' else None)
            if target is None: continue

            all_metrics = {}
            all_metrics.update(METRICS_36_FIN)
            all_metrics.update(METRICS_48_FIN)
            all_metrics.update(METRICS_36_LEAS)
            all_metrics.update(METRICS_48_LEAS)

            for metric, row_idx in all_metrics.items():
                val = pv(data[row_idx][c]) if row_idx < len(data) else None
                if val is not None:
                    target[metric] = val

        # Build changes
        changes = {}
        has_change = False
        for m in list(METRICS_36_FIN.keys()) + list(METRICS_48_FIN.keys()) + list(METRICS_36_LEAS.keys()) + list(METRICS_48_LEAS.keys()):
            cv = july_vals.get(m)
            pv_val = june_vals.get(m)
            if cv is not None and pv_val is not None:
                change = round(cv - pv_val, 4)
                changes[m] = {'current': round(cv, 2), 'previous': round(pv_val, 2), 'change': change}
                # Only 36期 changes count for has_key_change
                if '36' in m and abs(change) > 0.005:
                    has_change = True
            elif cv is not None:
                changes[m] = {'current': round(cv, 2), 'previous': None, 'change': None}

        results.append({
            'brand': g['brand'], 'model': g['model'], 'version': g['version'],
            'level': g['level'], 'changes': changes, 'has_key_change': has_change
        })
    return results

# ═══════════════════════════════════════════════════════
# Load sheet data and parse
# ═══════════════════════════════════════════════════════
with open('su7_data.json') as f: su7 = json.load(f)
with open('yu7_data.json') as f: yu7 = json.load(f)
with open('ultra_data.json') as f: ultra = json.load(f)

comp_su7 = extract_data(su7, SU7_GROUPS)
comp_yu7 = extract_data(yu7, YU7_GROUPS)
comp_ultra = extract_data(ultra, ULTRA_GROUPS)

print(f"SU7: {len(comp_su7)} entries")
for c in comp_su7: print(f"  {c['brand']} {c['model']} ({c['version']}) [{c['level']}]")
print(f"YU7: {len(comp_yu7)} entries")
for c in comp_yu7: print(f"  {c['brand']} {c['model']} ({c['version']}) [{c['level']}]")
print(f"Ultra: {len(comp_ultra)} entries")
for c in comp_ultra: print(f"  {c['brand']} {c['model']} ({c['version']}) [{c['level']}]")

# ═══════════════════════════════════════════════════════
# Read original HTML and update comp data
# ═══════════════════════════════════════════════════════
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

for key, data in [('comp_su7', comp_su7), ('comp_yu7', comp_yu7), ('comp_ultra', comp_ultra)]:
    new_js = json.dumps(data, ensure_ascii=False)
    pattern = r'("' + key + r'"\s*:\s*)\[.*?\](?=,\s*"comp_)'
    if key == 'comp_ultra':
        pattern = r'("' + key + r'"\s*:\s*)\[.*?\](?=,\s*"top_)'
    html = re.sub(pattern, r'\1' + new_js, html, flags=re.DOTALL)

# ═══════════════════════════════════════════════════════
# Add CSS
# ═══════════════════════════════════════════════════════
css = """
.t5-filters{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 16px;max-width:960px;margin-left:auto;margin-right:auto}
.t5-filter-group{display:flex;gap:4px;align-items:center}
.t5-filter-label{font-size:11px;color:#889;margin-right:4px}
.t5-filter-btn{padding:5px 12px;border-radius:15px;font-size:11px;font-weight:500;cursor:pointer;border:1px solid #2a2a3a;background:#1a1a2e;color:#889;transition:all .2s}
.t5-filter-btn:hover{border-color:#5cccf5;color:#5cccf5}
.t5-filter-btn.active{background:rgba(92,204,245,.15);border-color:#5cccf5;color:#5cccf5}
.t5-filter-sep{width:1px;height:20px;background:#2a2a3a;margin:0 8px}
"""
html = html.replace('</style>', css + '</style>', 1)

# ═══════════════════════════════════════════════════════
# Replace brand cards section
# ═══════════════════════════════════════════════════════
old = "  // Brand cards section\n  var ch='<div class=\"t5-sec-hdr\""
new = """  // Brand cards section
  var ch='<div class="t5-sec-hdr" style="max-width:960px;margin:28px auto 16px"><div><div class="t5-sec-title">各品牌金融政策变化 <span style="display:inline-block;font-size:11px;font-weight:600;color:#5cccf5;background:rgba(92,204,245,.1);border:1px solid rgba(92,204,245,.25);padding:2px 8px;border-radius:4px;vertical-align:middle;margin-left:6px">36期/20kkm | 48期/10kkm</span></div><div class="t5-sec-sub">Brand Financial Policy Changes · 7月 vs 6月</div></div></div>';
  ch+='<div class="t5-filters" id="t5filters">';
  ch+='<div class="t5-filter-group"><span class="t5-filter-label">期限:</span>';
  ch+='<button class="t5-filter-btn active" onclick="t5filterTerm(\\'36\\')">36个月/20kkm</button>';
  ch+='<button class="t5-filter-btn" onclick="t5filterTerm(\\'48\\')">48个月/10kkm</button></div>';
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
idx = html.find(old)
end = html.find("  ch+='<div class=\"t5-grid\">';") + len("  ch+='<div class=\"t5-grid\">';")
if idx != -1 and end > idx:
    html = html[:idx] + new + html[end:]

# ═══════════════════════════════════════════════════════
# Update card generation with data attributes
# ═══════════════════════════════════════════════════════
old_card = "    ch+='<div class=\"t5-card\" onclick=\"t5dOpen(\\''+brand+'\\')\">';"
new_card = """    var fe=null;for(var mk in bd.models){if(bd.models[mk].length>0){fe=bd.models[mk][0];break}}
    var cLv=fe?fe.level:'';
    ch+='<div class="t5-card" data-level="'+cLv+'" data-sheet="'+getSheetForBrand(brand)+'" data-change="'+(hasChange?'yes':'no')+'" onclick="t5dOpen(\\''+brand+'\\')">';"""
html = html.replace(old_card, new_card, 1)

# ═══════════════════════════════════════════════════════
# Update rows definition
# ═══════════════════════════════════════════════════════
old_rows = """      var rows=[
        {fin:{k:'分期月供-36个月/20kkm',l:'月供'},leas:{k:'租赁租金-36个月/20kkm',l:'月租'}},
        {fin:{k:'对客定价',l:'利率'},leas:{k:'Leasing factor',l:'LF'}},
        {fin:{k:'官网尾款（36）',l:'尾款'},leas:{k:'贴息成本-租赁',l:'贴息'}},
        {fin:{k:'贴息成本-分期（36个月）',l:'贴息'},leas:null}
      ];"""

new_rows = """      var _t=typeof t5FilterTerm!=='undefined'?t5FilterTerm:'36';
      var rows;
      if(_t==='48'){
        rows=[
          {fin:{k:'对客定价-48',l:'利率'},leas:null},
          {fin:{k:'分期月供-48',l:'月供'},leas:{k:'租赁租金-48',l:'月租'}},
          {fin:{k:'官网尾款-48',l:'尾款'},leas:{k:'理论月租-48',l:'理论月租'}},
          {fin:{k:'贴息成本-分期-48',l:'贴息'},leas:{k:'贴息成本-租赁-48',l:'贴息'}}
        ];
      }else{
        rows=[
          {fin:{k:'对客定价-36',l:'利率'},leas:{k:'Leasing factor-36',l:'LF'}},
          {fin:{k:'分期月供-36',l:'月供'},leas:{k:'租赁租金-36',l:'月租'}},
          {fin:{k:'官网尾款-36',l:'尾款'},leas:{k:'理论月租-36',l:'理论月租'}},
          {fin:{k:'贴息成本-分期-36',l:'贴息'},leas:{k:'贴息成本-租赁-36',l:'贴息'}}
        ];
      }"""
html = html.replace(old_rows, new_rows, 1)

# ═══════════════════════════════════════════════════════
# Update t5get to handle 48期 (no comparison)
# ═══════════════════════════════════════════════════════
old_get = """  function t5get(entries,key){
    for(var i=0;i<entries.length;i++){
      var c=entries[i].changes[key];
      if(c&&c.current!=null)return c;
    }
    return null;
  }"""
new_get = """  function t5get(entries,key){
    for(var i=0;i<entries.length;i++){
      var c=entries[i].changes[key];
      if(c&&c.current!=null){
        if(typeof t5FilterTerm!=='undefined'&&t5FilterTerm==='48')return{current:c.current,previous:null,change:null};
        return c;
      }
    }
    return null;
  }"""
html = html.replace(old_get, new_get, 1)

# ═══════════════════════════════════════════════════════
# Update change tag (hide for 48期)
# ═══════════════════════════════════════════════════════
old_tag = "ch+='<span class=\"t5-card-tag '+(hasChange?'up':'flat')+'\">'+(hasChange?'有变化':'无变化')+'</span>';"
new_tag = "ch+='<span class=\"t5-card-tag '+(hasChange?'up':'flat')+'\">'+(typeof t5FilterTerm!=='undefined'&&t5FilterTerm==='48'?'':(hasChange?'有变化':'无变化'))+'</span>';"
html = html.replace(old_tag, new_tag, 1)

# ═══════════════════════════════════════════════════════
# Add filter JS
# ═══════════════════════════════════════════════════════
js = """
var t5FilterTerm='36',t5FilterLevel='all',t5FilterSheet='all',t5FilterChange='all';
function getSheetForBrand(b){var m={'特斯拉':'SU7,YU7','奔驰':'SU7,YU7,Ultra','奥迪':'YU7,Ultra','大众':'SU7,YU7','宝马':'SU7,YU7,Ultra','比亚迪':'SU7,YU7','保时捷':'YU7,Ultra','小鹏':'YU7','斯柯达':'YU7','极氪':'SU7','现代':'SU7','马自达':'SU7','Lotus':'Ultra','Polestar':'Ultra'};return m[b]||'other'}
function t5filterTerm(t){t5FilterTerm=t;var b=document.querySelectorAll('.t5-filter-group')[0].querySelectorAll('.t5-filter-btn');b.forEach(function(x){x.classList.remove('active');if((t==='36'&&x.textContent.indexOf('36')!==-1)||(t==='48'&&x.textContent.indexOf('48')!==-1))x.classList.add('active')});r5()}
function t5filterLevel(l){t5FilterLevel=l;var b=document.querySelectorAll('.t5-filter-group')[1].querySelectorAll('.t5-filter-btn');b.forEach(function(x){x.classList.remove('active');if((l==='all'&&x.textContent==='全部')||(l==='低配'&&x.textContent==='低配')||(l==='高配'&&x.textContent==='高配'))x.classList.add('active')});t5applyFilters()}
function t5filterSheet(s){t5FilterSheet=s;var b=document.querySelectorAll('.t5-filter-group')[2].querySelectorAll('.t5-filter-btn');b.forEach(function(x){x.classList.remove('active');if((s==='all'&&x.textContent==='全部')||(s==='SU7'&&x.textContent==='SU7竞品')||(s==='YU7'&&x.textContent==='YU7竞品')||(s==='Ultra'&&x.textContent==='Ultra竞品'))x.classList.add('active')});t5applyFilters()}
function t5filterChange(c){t5FilterChange=c;var b=document.querySelectorAll('.t5-filter-group')[3].querySelectorAll('.t5-filter-btn');b.forEach(function(x){x.classList.remove('active');if((c==='all'&&x.textContent==='全部')||(c==='yes'&&x.textContent==='有变化')||(c==='no'&&x.textContent==='无变化'))x.classList.add('active')});t5applyFilters()}
function t5applyFilters(){document.querySelectorAll('.t5-card').forEach(function(c){var cl=c.getAttribute('data-level')||'',cs=c.getAttribute('data-sheet')||'',cc=c.getAttribute('data-change')||'';c.style.display=(t5FilterLevel==='all'||cl===t5FilterLevel)&&(t5FilterSheet==='all'||cs.indexOf(t5FilterSheet)!==-1)&&(t5FilterChange==='all'||cc===t5FilterChange)?'':'none'})}
"""
html = html.replace('</script>', js + '\n</script>', 1)

# Save
with open('index_july.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\nSaved index_july.html")
print(f"Total: {len(comp_su7)+len(comp_yu7)+len(comp_ultra)} entries")
