# 7月金融政策看板数据更新计划

## 数据源
`德国-竞品金融政策追踪（更新至26年7月）.xlsx` 中的 SU7/YU7/Ultra 三个sheet

## 7月数据统计

| Sheet | 车型数量 | 品牌 |
|-------|---------|------|
| SU7 | 14个 | 特斯拉、奔驰、大众、宝马、比亚迪、现代、马自达、极氪 |
| YU7 | 17个 | 特斯拉、大众、宝马、奥迪、斯柯达、比亚迪、保时捷、小鹏 |
| Ultra | 11个 | 奥迪、奔驰、保时捷、宝马、Lotus、Polestar |
| **合计** | **42个** | |

## 数据结构设计

### 每个车型包含的数据

#### 36期20kkm（含环比变化）
- **分期**: 月供、利率(对客定价)、尾款、贴息
- **租赁**: 月租、Leasing Factor、贴息

#### 48期10kkm（仅当前值，无变化）
- **分期**: 月供、利率(对客定价)、尾款、贴息
- **租赁**: 月租、Leasing Factor、贴息

### 筛选维度
- **竞品分类**: SU7 / YU7 / Ultra
- **配置**: 高配 / 低配

## 完整车型清单

### SU7 Sheet（14个车型）
1. 特斯拉 | Model 3 | LongRange RWD | 低配
2. 特斯拉 | Model 3 | AWD Performance | 高配
3. 奔驰 | CLA | 250+ mit EQ Technologie Edition | 低配
4. 奔驰 | CLA | 350 mit EQ Technologie Edition | 高配
5. 大众 | ID.7 | Pro S | 低配
6. 大众 | ID.7 | GTX | 高配
7. 宝马 | i4 | eDrive40 Gran Coupe | 低配
8. 宝马 | i4 | M60 Gran Coupe xDrive | 高配
9. 比亚迪 | SEAL | Design | 低配
10. 比亚迪 | SEAL | Excellence | 高配
11. 现代 | IONIQ 6 | 63 kWh battery, rear-wheel drive | 低配
12. 马自达 | 6e EV | EV Long Range Takumi Plus | 低配
13. 极氪 | 001 | LongRange RWD | 低配
14. 极氪 | 001 | AWD Performance | 高配

### YU7 Sheet（17个车型）
1. 特斯拉 | Model Y | LongRange AWD | 低配
2. 特斯拉 | Model Y | Performance AWD | 高配
3. 大众 | ID.4 | Pro with infotainment package | 低配
4. 大众 | ID.5 | Pro with infotainment package | 低配
5. 大众 | ID.5 | GTX with infotainment package | 高配
6. 宝马 | ix1 | eDrive20 Xline | 低配
7. 宝马 | ix1 | xDrive30 Xline | 高配
8. 宝马 | ix3 | 50 xDrive Serie | 低配
9. 奥迪 | Q6 SUV e-tron | e-tron performance | 低配
10. 奥迪 | Q6 SUV e-tron | quattro | 高配
11. 斯柯达 | Enyaq Coupe | 85 Sportline | 低配
12. 比亚迪 | Sealion 7 | Design | 低配
13. 比亚迪 | Sealion 7 | Excellence | 高配
14. 保时捷 | e-Macan | 4 | 低配
15. 保时捷 | e-Macan | 4s | 高配
16. 小鹏 | G9 | RWD Long Range | 低配
17. 小鹏 | G9 | AWD Performance | 高配

### Ultra Sheet（11个车型）
1. 奥迪 | e-tron GT | S | 低配
2. 奥迪 | e-tron GT | RS | 高配
3. 奔驰 | EQE | AMG EQE 53 4MATIC+ | 高配
4. 保时捷 | Taycan | 4S Black Edition | 低配
5. 保时捷 | Taycan | GTS | 高配
6. 宝马 | i5 | eDrive40 Limousine M Sportpaket | 低配
7. 宝马 | i5 | BMW i5 M60 xDrive Limousine | 高配
8. Lotus | Emeya | 600 sport SE | 低配
9. Lotus | Emeya | 900 sport | 高配
10. Polestar | 5 | Dual Motor-Launch Edition | 低配
11. Polestar | 5 | Performance-Launch Edition | 高配

## 实施步骤

### Step 1: 创建数据提取脚本
编写Python脚本从Excel提取7月数据，生成新的JSON数据结构

### Step 2: 更新看板数据
将提取的数据替换到`data.json`中的`comp_su7/comp_yu7/comp_ultra`

### Step 3: 更新看板代码
修改`index_july.html`中的`r5()`函数，支持：
- 36期和48期数据展示
- 48期数据无环比变化
- 正确的筛选逻辑

### Step 4: 验证
确保看板正确显示所有42个车型的7月数据
