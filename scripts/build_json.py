#!/usr/bin/env python3
"""CSV → JSON変換 + 島座標付与スクリプト"""
import csv, json, os
os.makedirs('../data', exist_ok=True)

# 島の座標（概略値。Geocoding後に精密化可能）
ISLAND_COORDS = {
    'ISL_001': (45.18, 141.21),  # 利尻島
    'ISL_002': (45.32, 141.04),  # 礼文島
    'ISL_003': (42.08, 139.53),  # 奥尻島
    'ISL_004': (44.45, 141.58),  # 焼尻島
    'ISL_005': (44.42, 141.53),  # 天売島
    'ISL_006': (38.05, 138.35),  # 佐渡島
    'ISL_007': (38.48, 139.25),  # 粟島（新潟）
    'ISL_008': (39.20, 139.42),  # 飛島
    'ISL_009': (38.78, 141.55),  # 大島（気仙沼）
    'ISL_010': (38.28, 141.25),  # 網地島
    'ISL_011': (34.73, 139.38),  # 伊豆大島
    'ISL_012': (34.52, 139.28),  # 利島
    'ISL_013': (34.37, 139.27),  # 新島
    'ISL_014': (34.32, 139.22),  # 式根島
    'ISL_015': (34.21, 139.13),  # 神津島
    'ISL_016': (34.07, 139.52),  # 三宅島
    'ISL_017': (33.88, 139.60),  # 御蔵島
    'ISL_018': (33.10, 139.78),  # 八丈島
    'ISL_019': (27.09, 142.19),  # 父島
    'ISL_020': (26.65, 142.15),  # 母島
    'ISL_021': (34.52, 136.90),  # 答志島
    'ISL_022': (34.48, 136.92),  # 菅島
    'ISL_023': (34.45, 136.88),  # 坂手島
    'ISL_024': (34.77, 136.97),  # 篠島
    'ISL_025': (34.08, 134.85),  # 沼島
    'ISL_026': (34.65, 134.52),  # 家島
    'ISL_027': (34.50, 134.25),  # 小豆島
    'ISL_028': (34.47, 134.07),  # 豊島（香川）
    'ISL_029': (34.46, 133.98),  # 直島
    'ISL_030': (34.43, 134.12),  # 男木島
    'ISL_031': (34.45, 134.10),  # 女木島
    'ISL_032': (34.27, 133.73),  # 本島（香川）
    'ISL_033': (34.37, 133.68),  # 広島（丸亀）
    'ISL_034': (34.33, 133.65),  # 手島（丸亀）
    'ISL_035': (34.17, 133.70),  # 佐柳島
    'ISL_036': (34.17, 133.77),  # 高見島
    'ISL_037': (34.13, 133.68),  # 粟島（香川）
    'ISL_038': (34.67, 134.18),  # 前島
    'ISL_039': (34.28, 133.05),  # 岩城島
    'ISL_040': (34.30, 133.08),  # 生名島
    'ISL_041': (34.28, 133.15),  # 弓削島
    'ISL_042': (34.33, 133.20),  # 魚島
    'ISL_043': (34.30, 132.95),  # 大崎上島
    'ISL_044': (34.20, 132.23),  # 阿多田島
    'ISL_045': (34.25, 132.45),  # 江田島・能美島
    'ISL_046': (36.20, 133.32),  # 隠岐・島後
    'ISL_047': (36.17, 133.00),  # 隠岐・西ノ島
    'ISL_048': (36.13, 133.07),  # 隠岐・中ノ島
    'ISL_049': (36.08, 133.08),  # 隠岐・知夫里島
    'ISL_050': (34.47, 131.43),  # 大島（山口・萩）
    'ISL_051': (33.85, 131.85),  # 平郡島
    'ISL_052': (34.03, 131.83),  # 大津島
    'ISL_053': (34.00, 130.80),  # 蓋井島
    'ISL_054': (33.88, 132.68),  # 中島（愛媛）
    'ISL_055': (33.85, 132.70),  # 興居島
    'ISL_056': (33.00, 132.53),  # 戸島（愛媛）
    'ISL_057': (32.92, 132.47),  # 日振島
    'ISL_058': (32.77, 132.72),  # 沖の島（高知）
    'ISL_059': (33.62, 130.27),  # 能古島
    'ISL_060': (33.87, 130.83),  # 大島（宗像）
    'ISL_061': (33.73, 131.68),  # 姫島（大分）
    'ISL_062': (32.88, 131.87),  # 大入島
    'ISL_063': (34.20, 129.28),  # 対馬
    'ISL_064': (33.75, 129.68),  # 壱岐
    'ISL_065': (33.25, 129.08),  # 宇久島
    'ISL_066': (33.18, 129.08),  # 小値賀島
    'ISL_067': (33.05, 129.10),  # 中通島（上五島）
    'ISL_068': (32.90, 128.93),  # 奈留島
    'ISL_069': (32.82, 128.85),  # 久賀島
    'ISL_070': (32.70, 128.85),  # 福江島
    'ISL_071': (32.90, 129.65),  # 池島
    'ISL_072': (33.40, 129.52),  # 度島
    'ISL_073': (33.40, 129.42),  # 大島（平戸）
    'ISL_074': (33.03, 129.37),  # 黒島（佐世保）
    'ISL_075': (32.45, 130.00),  # 御所浦島
    'ISL_076': (32.22, 130.17),  # 獅子島
    'ISL_077': (32.58, 131.77),  # 島野浦島
    'ISL_078': (31.82, 129.87),  # 甑島列島
    'ISL_079': (30.83, 129.92),  # 黒島（三島村）
    'ISL_080': (30.78, 130.28),  # 硫黄島（三島村）
    'ISL_081': (30.48, 130.42),  # 竹島（三島村）
    'ISL_082': (30.45, 130.22),  # 口永良部島
    'ISL_083': (30.33, 130.53),  # 屋久島
    'ISL_084': (30.67, 130.98),  # 種子島
    'ISL_085': (29.87, 129.93),  # 口之島
    'ISL_086': (29.85, 129.85),  # 中之島（トカラ）
    'ISL_087': (29.72, 129.93),  # 平島
    'ISL_088': (29.62, 129.72),  # 諏訪之瀬島
    'ISL_089': (29.45, 129.58),  # 悪石島
    'ISL_090': (29.35, 129.50),  # 小宝島
    'ISL_091': (29.15, 129.32),  # 宝島
    'ISL_092': (28.37, 129.50),  # 奄美大島
    'ISL_093': (28.33, 129.92),  # 喜界島
    'ISL_094': (28.12, 129.35),  # 加計呂麻島
    'ISL_095': (28.08, 129.38),  # 請島
    'ISL_096': (28.03, 129.32),  # 与路島
    'ISL_097': (27.73, 128.98),  # 徳之島
    'ISL_098': (27.38, 128.58),  # 沖永良部島
    'ISL_099': (27.05, 128.42),  # 与論島
    'ISL_100': (26.72, 127.78),  # 伊江島
    'ISL_101': (27.02, 127.97),  # 伊平屋島
    'ISL_102': (26.92, 127.92),  # 伊ぜ名島
    'ISL_103': (26.58, 127.22),  # 粟国島
    'ISL_104': (26.38, 127.55),  # 渡名喜島
    'ISL_105': (26.33, 126.80),  # 久米島
    'ISL_106': (26.17, 127.37),  # 渡嘉敷島
    'ISL_107': (26.23, 127.30),  # 座間味島
    'ISL_108': (26.20, 127.28),  # 阿嘉島
    'ISL_109': (26.28, 127.98),  # 津堅島
    'ISL_110': (26.13, 127.88),  # 久高島
    'ISL_111': (24.67, 124.70),  # 多良間島
    'ISL_112': (24.32, 124.08),  # 竹富島
    'ISL_113': (24.33, 123.95),  # 小浜島
    'ISL_114': (24.23, 123.78),  # 黒島（八重山）
    'ISL_115': (24.33, 123.80),  # 西表島
    'ISL_116': (24.47, 123.82),  # 鳩間島
    'ISL_117': (24.05, 123.78),  # 波照間島
    'ISL_118': (24.47, 123.00),  # 与那国島
    'ISL_119': (25.83, 131.23),  # 南大東島
    'ISL_120': (25.95, 131.30),  # 北大東島
}

REGION_COLORS = {
    '北海道': '#1E88E5',
    '東北・北陸': '#43A047',
    '関東・伊豆': '#E53935',
    '東海・中部': '#FB8C00',
    '近畿・瀬戸内': '#8E24AA',
    '山陰': '#00ACC1',
    '山陰・山口': '#00897B',
    '四国': '#F4511E',
    '九州北部': '#3949AB',
    '九州南部': '#D81B60',
    '奄美': '#6D4C41',
    '沖縄本島周辺': '#00BCD4',
    '沖縄慶良間': '#26C6DA',
    '宮古': '#FDD835',
    '八重山': '#FF7043',
    '大東': '#78909C',
}

def read_csv(path):
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

islands_raw = read_csv('../data/islands.csv')
ports_raw   = read_csv('../data/ports.csv')
routes_raw  = read_csv('../data/routes.csv')
pricing_raw = read_csv('../data/pricing.csv')

# Islands with coords
islands = []
for r in islands_raw:
    coords = ISLAND_COORDS.get(r['island_id'], (None, None))
    islands.append({
        'id': r['island_id'],
        'name': r['name'],
        'kana': r['name_kana'],
        'region': r['region'],
        'pref': r['prefecture'],
        'type': r['car_ferry_type'],
        'notes': r['notes'],
        'lat': coords[0],
        'lng': coords[1],
        'color': REGION_COLORS.get(r['region'], '#757575'),
    })

# Ports
ports = []
for r in ports_raw:
    ports.append({
        'id': r['port_id'],
        'name': r['port_name'],
        'city': r['city'],
        'pref': r['prefecture'],
        'lat': float(r['lat']) if r['lat'] else None,
        'lng': float(r['lng']) if r['lng'] else None,
    })

# Routes
routes = []
for r in routes_raw:
    routes.append({
        'id': r['route_id'],
        'island_id': r['island_id'],
        'port_id': r['departure_port_id'],
        'arrival_port': r['arrival_port_name'],
        'company': r['ferry_company'],
        'ferry': r['ferry_name'],
        'type': r['car_ferry_type'],
        'notes': r['notes'],
    })

# Pricing (keyed by company)
pricing = []
for r in pricing_raw:
    pricing.append({
        'company': r['ferry_company'],
        'route': r['route_description'],
        'class': r['vehicle_class'],
        'max_len': r['max_len_cm'],
        'price': r['price_one_way_yen'],
        'height_limit': r['height_limit_cm'],
        'applicable': r['hiace_applicable'],
        'url': r['source_url'],
        'notes': r['notes'],
    })

# Build island→routes→ports lookup
island_routes = {}
for rt in routes:
    iid = rt['island_id']
    if iid not in island_routes:
        island_routes[iid] = []
    island_routes[iid].append(rt)

port_map = {p['id']: p for p in ports}

# Build company→pricing lookup
company_pricing = {}
for p in pricing:
    c = p['company']
    if c not in company_pricing:
        company_pricing[c] = []
    company_pricing[c].append(p)

# Output JSON
with open('../data/islands.json', 'w', encoding='utf-8') as f:
    json.dump(islands, f, ensure_ascii=False, indent=2)

with open('../data/ports.json', 'w', encoding='utf-8') as f:
    json.dump(ports, f, ensure_ascii=False, indent=2)

with open('../data/routes.json', 'w', encoding='utf-8') as f:
    json.dump(routes, f, ensure_ascii=False, indent=2)

with open('../data/pricing.json', 'w', encoding='utf-8') as f:
    json.dump(pricing, f, ensure_ascii=False, indent=2)

# Combined lookup: island_id → {island info, routes with port details, pricing}
combined = {}
for isl in islands:
    iid = isl['id']
    rts = island_routes.get(iid, [])
    routes_detail = []
    companies = set()
    for rt in rts:
        port = port_map.get(rt['port_id'], {})
        companies.add(rt['company'])
        # Get pricing for this company
        price_info = company_pricing.get(rt['company'], [])
        routes_detail.append({
            **rt,
            'port_name': port.get('name', rt['port_id']),
            'port_lat': port.get('lat'),
            'port_lng': port.get('lng'),
            'pricing': price_info,
        })
    combined[iid] = {**isl, 'routes': routes_detail}

with open('../data/combined.json', 'w', encoding='utf-8') as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

# ferry_data.js: browser向けインライン埋め込み用（サーバー不要）
from datetime import datetime, timezone, timedelta
JST = timezone(timedelta(hours=9))
now_str = datetime.now(JST).strftime('%Y年%m月%d日')

js_content = f"""// Auto-generated by build_json.py — DO NOT EDIT MANUALLY
// Last built: {now_str}
// Update pricing: edit data/pricing.csv → run scripts/build_json.py

const FERRY_ISLANDS = {json.dumps(islands, ensure_ascii=False)};

const FERRY_PORTS = {json.dumps(ports, ensure_ascii=False)};

const FERRY_ROUTES = {json.dumps(routes, ensure_ascii=False)};

const FERRY_PRICING = {json.dumps(pricing, ensure_ascii=False)};

const PRICING_LAST_CHECKED = '{now_str}';
"""

with open('../data/ferry_data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"✓ islands.json: {len(islands)} 島")
print(f"✓ ports.json: {len(ports)} 港")
print(f"✓ routes.json: {len(routes)} 航路")
print(f"✓ pricing.json: {len(pricing)} 料金エントリ")
print(f"✓ combined.json: 完成")
print(f"✓ ferry_data.js: 生成完了 (最終確認: {now_str})")
