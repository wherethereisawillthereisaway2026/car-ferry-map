#!/usr/bin/env python3
"""CSV → JSON変換 + 島座標付与スクリプト"""
import csv, json, os
os.makedirs('../data', exist_ok=True)

# 島の座標（概略値。Geocoding後に精密化可能）
ISLAND_COORDS = {
    'ISL_001': (45.1784, 141.2305),  # 利尻島
    'ISL_002': (45.3688, 141.0246),  # 礼文島
    'ISL_003': (42.1523, 139.4670),  # 奥尻島
    'ISL_004': (44.4370, 141.4069),  # 焼尻島
    'ISL_005': (44.4276, 141.3203),  # 天売島
    'ISL_006': (38.0673, 138.3514),  # 佐渡島
    'ISL_007': (38.4637, 139.2429),  # 粟島（新潟）
    'ISL_008': (39.1950, 139.5498),  # 飛島
    'ISL_009': (38.8579, 141.6159),  # 大島（気仙沼）
    'ISL_010': (38.2648, 141.4800),  # 網地島
    'ISL_011': (34.7385, 139.4024),  # 伊豆大島
    'ISL_012': (34.5230, 139.2800),  # 利島
    'ISL_013': (34.3813, 139.2654),  # 新島
    'ISL_014': (34.3264, 139.2137),  # 式根島
    'ISL_015': (34.2142, 139.1523),  # 神津島
    'ISL_016': (34.0854, 139.5213),  # 三宅島
    'ISL_017': (33.8764, 139.6031),  # 御蔵島
    'ISL_018': (33.1025, 139.8077),  # 八丈島
    'ISL_019': (27.0709, 142.2096),  # 父島
    'ISL_020': (26.6609, 142.1561),  # 母島
    'ISL_021': (34.5223, 136.8813),  # 答志島
    'ISL_022': (34.4898, 136.8875),  # 菅島
    'ISL_023': (34.4864, 136.8583),  # 坂手島
    'ISL_024': (34.6762, 137.0038),  # 篠島
    'ISL_025': (34.1679, 134.8251),  # 沼島
    'ISL_026': (34.6723, 134.5294),  # 家島
    'ISL_027': (34.4898, 134.2604),  # 小豆島
    'ISL_028': (34.4796, 134.0703),  # 豊島（香川）
    'ISL_029': (34.4604, 133.9846),  # 直島
    'ISL_030': (34.4251, 134.0600),  # 男木島
    'ISL_031': (34.3943, 134.0497),  # 女木島
    'ISL_032': (34.3849, 133.7723),  # 本島（香川）
    'ISL_033': (34.3761, 133.7098),  # 広島（丸亀）
    'ISL_034': (34.3967, 133.6696),  # 手島（丸亀）
    'ISL_035': (34.3427, 133.6249),  # 佐柳島
    'ISL_036': (34.3155, 133.6733),  # 高見島
    'ISL_037': (34.13, 133.68),  # 粟島（香川）
    'ISL_038': (34.6097, 134.1884),  # 前島
    'ISL_039': (34.2610, 133.1487),  # 岩城島
    'ISL_040': (34.2709, 133.1773),  # 生名島
    'ISL_041': (34.2652, 133.2100),  # 弓削島
    'ISL_042': (34.1772, 133.3201),  # 魚島
    'ISL_043': (34.2451, 132.9047),  # 大崎上島
    'ISL_044': (34.1919, 132.3057),  # 阿多田島
    'ISL_045': (34.2440, 132.4818),  # 江田島・能美島
    'ISL_046': (36.2541, 133.2763),  # 隠岐・島後
    'ISL_047': (36.0904, 133.0298),  # 隠岐・西ノ島
    'ISL_048': (36.0774, 133.0939),  # 隠岐・中ノ島
    'ISL_049': (36.0134, 133.0297),  # 隠岐・知夫里島
    'ISL_050': (34.5014, 131.4105),  # 大島（山口・萩）
    'ISL_051': (33.7923, 132.2274),  # 平郡島
    'ISL_052': (34.0254, 131.7070),  # 大津島
    'ISL_053': (34.1038, 130.7867),  # 蓋井島
    'ISL_054': (33.9806, 132.6218),  # 中島（愛媛）
    'ISL_055': (33.8989, 132.6705),  # 興居島
    'ISL_056': (33.2046, 132.3613),  # 戸島（愛媛）
    'ISL_057': (33.1559, 132.2981),  # 日振島
    'ISL_058': (32.7288, 132.5509),  # 沖の島（高知）
    'ISL_059': (33.6224, 130.3059),  # 能古島
    'ISL_060': (33.9012, 130.4226),  # 大島（宗像）
    'ISL_061': (33.7285, 131.6684),  # 姫島（大分）
    'ISL_062': (32.9987, 131.9246),  # 大入島
    'ISL_063': (34.3953, 129.3150),  # 対馬
    'ISL_064': (32.8249, 129.7809),  # 壱岐
    'ISL_065': (33.2742, 129.1109),  # 宇久島
    'ISL_066': (33.2014, 129.0556),  # 小値賀島
    'ISL_067': (32.9903, 129.0670),  # 中通島（上五島）
    'ISL_068': (32.8421, 128.9453),  # 奈留島
    'ISL_069': (32.8041, 128.8912),  # 久賀島
    'ISL_070': (32.6861, 128.7556),  # 福江島
    'ISL_071': (32.8855, 129.5996),  # 池島
    'ISL_072': (33.4394, 129.5247),  # 度島
    'ISL_073': (33.0716, 129.7817),  # 大島（平戸）
    'ISL_074': (33.1414, 129.5335),  # 黒島（佐世保）
    'ISL_075': (32.3279, 130.3474),  # 御所浦島
    'ISL_076': (32.2791, 130.2370),  # 獅子島
    'ISL_077': (32.6699, 131.8148),  # 島野浦島
    'ISL_078': (31.8419, 129.8850),  # 甑島列島
    'ISL_079': (30.8318, 129.9347),  # 黒島（三島村）
    'ISL_080': (30.7905, 130.2933),  # 硫黄島（三島村）
    'ISL_081': (30.8100, 130.4290),  # 竹島（三島村）
    'ISL_082': (30.4561, 130.2229),  # 口永良部島
    'ISL_083': (30.3479, 130.5245),  # 屋久島
    'ISL_084': (30.5918, 130.9959),  # 種子島
    'ISL_085': (29.9782, 129.9169),  # 口之島
    'ISL_086': (29.8501, 129.8661),  # 中之島（トカラ）
    'ISL_087': (29.6866, 129.5325),  # 平島
    'ISL_088': (29.6373, 129.7133),  # 諏訪之瀬島
    'ISL_089': (29.4610, 129.5991),  # 悪石島
    'ISL_090': (29.2235, 129.3248),  # 小宝島
    'ISL_091': (29.1430, 129.2078),  # 宝島
    'ISL_092': (28.3199, 129.3968),  # 奄美大島
    'ISL_093': (28.3264, 129.9754),  # 喜界島
    'ISL_094': (28.1317, 129.2326),  # 加計呂麻島
    'ISL_097': (27.7775, 128.9581),  # 徳之島
    'ISL_098': (27.3842, 128.5882),  # 沖永良部島
    'ISL_099': (27.0433, 128.4252),  # 与論島
    'ISL_100': (26.7217, 127.7898),  # 伊江島
    'ISL_101': (27.0450, 127.9714),  # 伊平屋島
    'ISL_102': (26.9332, 127.9376),  # 伊ぜ名島
    'ISL_103': (26.5884, 127.2306),  # 粟国島
    'ISL_104': (26.3652, 127.1433),  # 渡名喜島
    'ISL_105': (26.3411, 126.7891),  # 久米島
    'ISL_106': (26.1861, 127.3570),  # 渡嘉敷島
    'ISL_107': (26.2350, 127.3019),  # 座間味島
    'ISL_108': (26.2000, 127.2776),  # 阿嘉島
    'ISL_109': (26.2521, 127.9422),  # 津堅島
    'ISL_110': (26.1628, 127.8955),  # 久高島
    'ISL_111': (24.6575, 124.6996),  # 多良間島
    'ISL_112': (24.3263, 124.0890),  # 竹富島
    'ISL_113': (24.3391, 123.9801),  # 小浜島
    'ISL_114': (24.2373, 124.0119),  # 黒島（八重山）
    'ISL_115': (24.3464, 123.8391),  # 西表島
    'ISL_116': (24.4722, 123.8205),  # 鳩間島
    'ISL_117': (24.0587, 123.7822),  # 波照間島
    'ISL_118': (24.4556, 122.9876),  # 与那国島
    'ISL_119': (25.8423, 131.2429),  # 南大東島
    'ISL_120': (25.9445, 131.3076),  # 北大東島
    'ISL_123': (32.4571, 139.7641),  # 青ヶ島
    'ISL_121': (24.8140, 125.3056),  # 宮古島
    'ISL_122': (24.4710, 124.2385),  # 石垣島
    'ISL_124': (34.0500, 132.9833),  # 岡村島
    'ISL_125': (34.1333, 132.9833),  # 大下島
    'ISL_126': (34.1167, 132.9700),  # 小大下島
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
    via_str = r.get('via_ports', '')
    routes.append({
        'id': r['route_id'],
        'island_id': r['island_id'],
        'port_id': r['departure_port_id'],
        'arrival_port': r['arrival_port_name'],
        'company': r['ferry_company'],
        'ferry': r['ferry_name'],
        'type': r['car_ferry_type'],
        'notes': r['notes'],
        'via_ports': [v for v in via_str.split(',') if v],
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
