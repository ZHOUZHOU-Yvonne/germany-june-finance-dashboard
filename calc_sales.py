import pandas as pd
import json

df = pd.read_excel('Marklines 欧洲 2024年1月-2026年6月数据.xlsx', sheet_name='Sheet1')
df_de = df[df['国家/地区'] == '德国'].copy()

# Convert numeric columns
for col in [202606, 202605, 202506]:
    df_de[col] = pd.to_numeric(df_de[col], errors='coerce').fillna(0)

# Map Chinese brand names to English
brand_map = {
    '丰田': 'Toyota', '雷克萨斯': 'Lexus', '大众': 'Volkswagen', '奥迪': 'Audi',
    '斯柯达 (Skoda)': 'Skoda', 'SEAT': 'SEAT', 'CUPRA': 'CUPRA', 'SEAT / CUPRA': 'SEAT/CUPRA',
    '现代': 'Hyundai', '起亚': 'Kia', '菲亚特 (2021-)': 'Fiat', '标致 (2021-)': 'Peugeot',
    '雪铁龙 (2021-)': 'Citroen', '欧宝 (2021-)': 'Opel', 'DS (2021-)': 'DS', '福特': 'Ford',
    'Tesla': 'Tesla', '本田': 'Honda', '日产': 'Nissan', '铃木': 'Suzuki',
    '比亚迪汽车': 'BYD', '沃尔沃汽车 (2011-)': 'Volvo', '吉利': 'Geely', 'Polestar': 'Polestar',
    '极氪 (ZEEKR)': 'Zeekr', '领克汽车 (LYNK & CO)': 'LYNK & CO',
    '梅赛德斯-奔驰 (2022-)': 'Mercedes-Benz', 'smart (2022-)': 'smart', '宝马': 'BMW', 'MINI': 'MINI',
    '雷诺': 'Renault', 'Dacia': 'Dacia', 'Alpine': 'Alpine', '马自达': 'Mazda',
    '三菱': 'Mitsubishi', '路虎 (2008-)': 'Land Rover', '捷豹 (2008-)': 'Jaguar',
    'MG (2006-)': 'MG', '东风汽车': 'Dongfeng', '深蓝 (Deepal)': 'Deepal',
    'Omoda': 'Omoda', 'Jaecoo': 'Jaecoo', '长城汽车 (GW)': 'Great Wall', '欧拉': 'ORA',
    '萤火虫 (FireFly)': 'Firefly', '蔚来汽车': 'NIO', '小鹏汽车': 'Xpeng', 'Leapmotor': 'Leapmotor',
}

df_de['brand_en'] = df_de['整车厂/品牌'].map(brand_map)

# Total sales by brand (全量)
total_by_brand = df_de.groupby('brand_en').agg({202606: 'sum', 202605: 'sum', 202506: 'sum'}).reset_index()
total_by_brand.columns = ['brand', 'cur', 'prv', 'py']

# BEV sales by brand
df_bev = df_de[df_de['动力总成'] == 'EV'].copy()
bev_by_brand = df_bev.groupby('brand_en').agg({202606: 'sum', 202605: 'sum', 202506: 'sum'}).reset_index()
bev_by_brand.columns = ['brand', 'bev_cur', 'bev_prv', 'bev_py']

# Merge
result = pd.merge(total_by_brand, bev_by_brand, on='brand', how='left')
result = result.fillna(0)

# Calculate YoY and MoM
def calc_yoy(row):
    if row['py'] > 0:
        return ((row['cur'] - row['py']) / row['py'] * 100)
    return None

def calc_mom(row):
    if row['prv'] > 0:
        return ((row['cur'] - row['prv']) / row['prv'] * 100)
    return None

def calc_bev_yoy(row):
    if row['bev_py'] > 0:
        return ((row['bev_cur'] - row['bev_py']) / row['bev_py'] * 100)
    return None

def calc_bev_mom(row):
    if row['bev_prv'] > 0:
        return ((row['bev_cur'] - row['bev_prv']) / row['bev_prv'] * 100)
    return None

result['yoy'] = result.apply(calc_yoy, axis=1)
result['mom'] = result.apply(calc_mom, axis=1)
result['bev_yoy'] = result.apply(calc_bev_yoy, axis=1)
result['bev_mom'] = result.apply(calc_bev_mom, axis=1)

# Sort by total sales
result = result.sort_values('cur', ascending=False)

# Print TOP15
print('=== TOP15 品牌 · 全量 ===')
top15 = result.head(15)
for _, r in top15.iterrows():
    yoy_str = '{:+.1f}%'.format(r['yoy']) if r['yoy'] is not None else '-'
    mom_str = '{:+.1f}%'.format(r['mom']) if r['mom'] is not None else '-'
    print('{}: cur={}, yoy={}, mom={}'.format(r['brand'], int(r['cur']), yoy_str, mom_str))

print()
print('=== TOP15 品牌 · BEV ===')
top15_bev = result.sort_values('bev_cur', ascending=False).head(15)
for _, r in top15_bev.iterrows():
    bev_yoy_str = '{:+.1f}%'.format(r['bev_yoy']) if r['bev_yoy'] is not None else '-'
    bev_mom_str = '{:+.1f}%'.format(r['bev_mom']) if r['bev_mom'] is not None else '-'
    print('{}: bev_cur={}, bev_yoy={}, bev_mom={}'.format(r['brand'], int(r['bev_cur']), bev_yoy_str, bev_mom_str))

# Chinese brands
chinese_brands = ['BYD', 'Dongfeng', 'Deepal', 'Omoda', 'Jaecoo', 'Great Wall', 'Geely', 'NIO', 'Xpeng', 'Zeekr', 'Leapmotor', 'LYNK & CO', 'MG']
print()
print('=== 中资品牌 · 全量 ===')
chinese_all = result[result['brand'].isin(chinese_brands)].sort_values('cur', ascending=False)
for _, r in chinese_all.iterrows():
    if r['cur'] > 0:
        yoy_str = '{:+.1f}%'.format(r['yoy']) if r['yoy'] is not None else '-'
        mom_str = '{:+.1f}%'.format(r['mom']) if r['mom'] is not None else '-'
        print('{}: cur={}, yoy={}, mom={}'.format(r['brand'], int(r['cur']), yoy_str, mom_str))

print()
print('=== 中资品牌 · BEV ===')
chinese_bev = result[result['brand'].isin(chinese_brands)].sort_values('bev_cur', ascending=False)
for _, r in chinese_bev.iterrows():
    if r['bev_cur'] > 0:
        bev_yoy_str = '{:+.1f}%'.format(r['bev_yoy']) if r['bev_yoy'] is not None else '-'
        bev_mom_str = '{:+.1f}%'.format(r['bev_mom']) if r['bev_mom'] is not None else '-'
        print('{}: bev_cur={}, bev_yoy={}, bev_mom={}'.format(r['brand'], int(r['bev_cur']), bev_yoy_str, bev_mom_str))

# Save as JSON for easy import
output = {
    'top15_total': [],
    'top15_bev': [],
    'chinese_total': [],
    'chinese_bev': []
}

for _, r in top15.iterrows():
    output['top15_total'].append({
        'make': r['brand'],
        'cur': int(r['cur']),
        'yoy': r['yoy'],
        'mom': r['mom']
    })

for _, r in top15_bev.iterrows():
    output['top15_bev'].append({
        'make': r['brand'],
        'bevCur': int(r['bev_cur']),
        'bevYoy': r['bev_yoy'],
        'bevMom': r['bev_mom']
    })

for _, r in chinese_all.iterrows():
    if r['cur'] > 0:
        output['chinese_total'].append({
            'make': r['brand'],
            'cur': int(r['cur']),
            'yoy': r['yoy'],
            'mom': r['mom']
        })

for _, r in chinese_bev.iterrows():
    if r['bev_cur'] > 0:
        output['chinese_bev'].append({
            'make': r['brand'],
            'bevCur': int(r['bev_cur']),
            'bevYoy': r['bev_yoy'],
            'bevMom': r['bev_mom']
        })

with open('sales_update_june.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print('JSON saved to sales_update_june.json')
