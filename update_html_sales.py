import pandas as pd
import re
import json

# Read Excel data
df = pd.read_excel('Marklines 欧洲 2024年1月-2026年6月数据.xlsx', sheet_name='Sheet1')
df_de = df[df['国家/地区'] == '德国'].copy()

# Convert numeric columns
for col in [202605, 202606, 202506]:
    df_de[col] = pd.to_numeric(df_de[col], errors='coerce').fillna(0)

# Map Chinese brand names to English (matching the HTML structure)
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

# Build sales data structure matching HTML format
# Group by brand and model
sales_data = []
bev_data = []

for (brand, model, powertrain), group in df_de.groupby(['brand_en', '车型', '动力总成']):
    if pd.isna(brand):
        continue

    # Build sub_model and trim names matching HTML format
    sub_model = f'{brand} {model}'
    trim = f'{brand} {model}'

    # Build sales object with all months
    sales_obj = {}
    for _, row in group.iterrows():
        for col in [202605, 202606, 202506]:
            month_str = str(col)
            # Convert 202606 to 2026-06 format
            month_formatted = f'{month_str[:4]}-{month_str[4:]}'
            val = int(row[col]) if row[col] > 0 else 0
            if val > 0:
                sales_obj[month_formatted] = val

    entry = {
        'make': brand,
        'sub_model': sub_model,
        'trim': trim,
        'sales': sales_obj
    }

    sales_data.append(entry)

    # BEV data - only for EV powertrain
    if powertrain == 'EV':
        bev_data.append(entry)

# Read HTML file
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Update month variables
html_content = re.sub(
    r"var curMonth='2026-06',prevMonth='[^']+',prevYear='[^']+'",
    "var curMonth='2026-06',prevMonth='2026-05',prevYear='2025-06'",
    html_content
)

# Update the display text
html_content = html_content.replace('Brand Sales Breakdown · May 2026', 'Brand Sales Breakdown · June 2026')

# Now we need to update the sales data in the HTML
# Find the sales array and replace it
# The sales data is in format: "sales":[{...},{...},...]

# Find the start of sales array
sales_start_pattern = r'"sales":\['
sales_start_match = re.search(sales_start_pattern, html_content)
if sales_start_match:
    sales_start = sales_start_match.start()

    # Find the end of sales array - count brackets
    bracket_count = 0
    i = sales_start_match.end()
    while i < len(html_content):
        if html_content[i] == '[':
            bracket_count += 1
        elif html_content[i] == ']':
            if bracket_count == 0:
                sales_end = i + 1
                break
            bracket_count -= 1
        i += 1

    # Generate new sales JSON
    new_sales_json = json.dumps(sales_data, ensure_ascii=False)

    # Replace the sales array
    html_content = html_content[:sales_start] + '"sales":' + new_sales_json + html_content[sales_end:]

    print(f'Updated sales array: {len(sales_data)} entries')

# Find and update sales_bev array
bev_start_pattern = r'"sales_bev":\['
bev_start_match = re.search(bev_start_pattern, html_content)
if bev_start_match:
    bev_start = bev_start_match.start()

    # Find the end
    bracket_count = 0
    i = bev_start_match.end()
    while i < len(html_content):
        if html_content[i] == '[':
            bracket_count += 1
        elif html_content[i] == ']':
            if bracket_count == 0:
                bev_end = i + 1
                break
            bracket_count -= 1
        i += 1

    # Generate new BEV JSON
    new_bev_json = json.dumps(bev_data, ensure_ascii=False)

    # Replace
    html_content = html_content[:bev_start] + '"sales_bev":' + new_bev_json + html_content[bev_end:]

    print(f'Updated sales_bev array: {len(bev_data)} entries')

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('HTML file updated successfully!')

# Verify the update
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check month variables
match = re.search(r"var curMonth='[^']+',prevMonth='[^']+',prevYear='[^']+'", content)
if match:
    print(f'Month variables: {match.group()}')

# Check text
if 'June 2026' in content:
    print('Text updated to June 2026')
