#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse ALL data from Feishu sheets - 36/48期 x 分期/租赁."""

import json
import re

def parse_value(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).strip()
    if s in ('', '/', '-', '--', 'n/a', '#VALUE!', '#REF!', 'NO INFO'): return None
    s = s.replace(',', '').replace('€', '').replace('%', '').replace(' ', '')
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'\s.*$', '', s)
    try: return float(s)
    except: return None

# ═══════════════════════════════════════════════════════
# Row structure (0-based)
# ═══════════════════════════════════════════════════════
# Row 0: 品牌
# Row 1: 更新时间
# Row 2: 车型
# Row 3: 版本
# Row 4: 配置(低配/高配)
# Row 5: MSRP
# Row 6: 补贴政策时效
# Row 7: 官网主机厂售价补贴
# Row 8: RV 36个月20kkm
# Row 9: RV 48个月10kkm
# Row 10: RV %
# Row 11: 首付金额
# Row 12: 贷款政策

# 48期/10kkm 分期
ROW_48_FIN = {
    '对客定价': 13,
    '分期月供': 14,
    '官网尾款': 15,
    '贴息成本-分期': 16,
}

# 36期/20kkm 分期
ROW_36_FIN = {
    '对客定价': 17,
    '分期月供': 18,
    '官网尾款': 19,
    '贴息成本-分期': 20,
}

# 36期/20kkm 租赁
ROW_36_LEAS = {
    '租赁租金': 22,
    '理论月租': 23,
    '贴息成本-租赁': 24,
    'Leasing factor': 25,
}

# 48期/10kkm 租赁
ROW_48_LEAS = {
    '租赁租金': 27,
    '理论月租': 28,
    '贴息成本-租赁': 29,
}

# ═══════════════════════════════════════════════════════
# Column groups for each sheet
# ═══════════════════════════════════════════════════════

SU7_GROUPS = [
    {'brand': '特斯拉', 'model': 'Model 3', 'version': 'LongRange RWD', 'level': '低配', 'cols': list(range(2, 10))},
    {'brand': '特斯拉', 'model': 'Model 3', 'version': 'AWD Performance', 'level': '高配', 'cols': list(range(10, 18))},
    {'brand': '奔驰', 'model': 'CLA', 'version': '250+ mit EQ Technologie Edition', 'level': '低配', 'cols': list(range(18, 26))},
]

YU7_GROUPS = [
    {'brand': '特斯拉', 'model': 'Model Y', 'version': 'LongRange AWD', 'level': '低配', 'cols': list(range(2, 10))},
    {'brand': '特斯拉', 'model': 'Model Y', 'version': 'Performance AWD', 'level': '高配', 'cols': list(range(10, 18))},
    {'brand': '奔驰', 'model': 'EQA', 'version': '300 4MATIC Electric Art', 'level': '低配', 'cols': list(range(18, 23))},
    {'brand': '奔驰', 'model': 'EQA', 'version': '350 4MATIC AMG Line Premium', 'level': '高配', 'cols': list(range(23, 26))},
]

ULTRA_GROUPS = [
    {'brand': '奥迪', 'model': 'e-tron GT', 'version': 'S', 'level': '低配', 'cols': list(range(2, 10))},
    {'brand': '奥迪', 'model': 'e-tron GT', 'version': 'RS', 'level': '高配', 'cols': list(range(10, 18))},
    {'brand': '奔驰', 'model': 'EQE', 'version': 'AMG EQE 53 4MATIC+', 'level': '高配', 'cols': list(range(18, 26))},
]

# ═══════════════════════════════════════════════════════
# Read sheet data
# ═══════════════════════════════════════════════════════

# We'll read from the saved JSON files or embed directly
# For now, read from the API results we already have

def extract_group_data(data, group_def):
    """Extract data for a specific group from sheet data."""
    cols = group_def['cols']
    months = {}

    for c in cols:
        if c >= len(data[1]): continue
        date_val = data[1][c]
        if not date_val: continue
        date_str = str(date_val).strip()
        m = re.match(r'(\d{4})年(\d{1,2})月', date_str)
        if not m: continue
        month_key = f"{m.group(1)}-{m.group(2).zfill(2)}"

        month_data = {
            'common': {},
            '36_fin': {},
            '48_fin': {},
            '36_leas': {},
            '48_leas': {},
        }

        # Common data
        for metric, row_idx in [('MSRP', 5), ('补贴政策时效', 6), ('官网主机厂售价补贴', 7),
                                 ('RV_36', 8), ('RV_48', 9), ('首付金额', 11), ('贷款政策', 12)]:
            if row_idx < len(data):
                val = parse_value(data[row_idx][c])
                if val is not None:
                    month_data['common'][metric] = val

        # 48期 分期
        for metric, row_idx in ROW_48_FIN.items():
            if row_idx < len(data):
                val = parse_value(data[row_idx][c])
                if val is not None:
                    month_data['48_fin'][metric] = val

        # 36期 分期
        for metric, row_idx in ROW_36_FIN.items():
            if row_idx < len(data):
                val = parse_value(data[row_idx][c])
                if val is not None:
                    month_data['36_fin'][metric] = val

        # 36期 租赁
        for metric, row_idx in ROW_36_LEAS.items():
            if row_idx < len(data):
                val = parse_value(data[row_idx][c])
                if val is not None:
                    month_data['36_leas'][metric] = val

        # 48期 租赁
        for metric, row_idx in ROW_48_LEAS.items():
            if row_idx < len(data):
                val = parse_value(data[row_idx][c])
                if val is not None:
                    month_data['48_leas'][metric] = val

        months[month_key] = month_data

    return months

def build_comp_for_group(group_def, data):
    """Build comp data (July vs June) for a single group."""
    months = extract_group_data(data, group_def)

    july = months.get('2026-07', {})
    june = months.get('2026-06', {})

    if not july and not june:
        return None

    # Build changes for each term/type combination
    changes = {}
    has_key_change = False
    key_mets = ['分期月供', '租赁租金', '对客定价', 'Leasing factor']

    for term_type in ['36_fin', '48_fin', '36_leas', '48_leas']:
        july_data = july.get(term_type, {})
        june_data = june.get(term_type, {})
        term_changes = {}

        for m in ['对客定价', '分期月供', '官网尾款', '贴息成本-分期', '租赁租金', '理论月租', '贴息成本-租赁', 'Leasing factor']:
            cv = july_data.get(m)
            pv = june_data.get(m)
            if cv is not None and pv is not None:
                change = round(cv - pv, 4)
                term_changes[m] = {'current': round(cv, 4), 'previous': round(pv, 4), 'change': change}
                if m in key_mets and abs(change) > 0.005:
                    has_key_change = True
            elif cv is not None:
                term_changes[m] = {'current': round(cv, 4), 'previous': None, 'change': None}

        changes[term_type] = term_changes

    return {
        'brand': group_def['brand'],
        'model': group_def['model'],
        'version': group_def['version'],
        'level': group_def['level'],
        'current': july,
        'previous': june,
        'changes': changes,
        'has_key_change': has_key_change
    }

# ═══════════════════════════════════════════════════════
# Process all sheets
# ═══════════════════════════════════════════════════════
all_comp = []

# We need to read the sheet data - let's embed it from the API results
# For now, create a placeholder that reads from the Feishu API

print("=== Processing Feishu Data ===")
print("Note: This script needs to be run after fetching data from Feishu API")
print("The data should be saved to su7_data.json, yu7_data.json, ultra_data.json")

# Create output structure
output = {
    'su7_groups': SU7_GROUPS,
    'yu7_groups': YU7_GROUPS,
    'ultra_groups': ULTRA_GROUPS,
    'all_comp': [],
    'row_structure': {
        '48_fin': ROW_48_FIN,
        '36_fin': ROW_36_FIN,
        '36_leas': ROW_36_LEAS,
        '48_leas': ROW_48_LEAS,
    }
}

with open('feishu_structure.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\nSaved structure to feishu_structure.json")
print("\nRow structure:")
print("  48期/10kkm 分期: 对客定价(13), 月供(14), 尾款(15), 贴息(16)")
print("  36期/20kkm 分期: 对客定价(17), 月供(18), 尾款(19), 贴息(20)")
print("  36期/20kkm 租赁: 租金(22), 理论月租(23), 贴息(24), LF(25)")
print("  48期/10kkm 租赁: 租金(27), 理论月租(28), 贴息(29)")
