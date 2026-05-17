#!/usr/bin/env python3
"""
全島の座標をNominatimでジオコーディングして更新する
Rate limit: 1req/sec（Nominatimポリシー）
"""
import csv, json, time, re, urllib.request, urllib.parse

HEADERS = {'User-Agent': 'CarFerryMap/1.0 (hiroki2000au20@gmail.com)'}

def nominatim_search(query):
    params = urllib.parse.urlencode({
        'q': query, 'format': 'json', 'limit': 1,
        'accept-language': 'ja',
        'countrycodes': 'jp',
    })
    url = f'https://nominatim.openstreetmap.org/search?{params}'
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            results = json.loads(r.read())
            if results:
                return float(results[0]['lat']), float(results[0]['lon']), results[0].get('display_name','')
    except Exception as e:
        print(f'  ERROR: {e}')
    return None, None, None

# 島名 → 検索クエリのマッピング（括弧内を除いてシンプルに）
SEARCH_OVERRIDES = {
    'ISL_009': ('大島 気仙沼 宮城県', None),
    'ISL_021': ('答志島 鳥羽 三重県', None),
    'ISL_026': ('家島 姫路 兵庫県', None),
    'ISL_028': ('豊島 小豆郡 香川県', None),
    'ISL_029': ('直島 香川県', None),
    'ISL_030': ('男木島 香川県', None),
    'ISL_031': ('女木島 香川県', None),
    'ISL_032': ('本島 丸亀 香川県', None),
    'ISL_033': ('広島 丸亀 香川県', None),
    'ISL_037': ('粟島 三豊 香川県', None),
    'ISL_039': ('岩城島 愛媛県', None),
    'ISL_040': ('生名島 愛媛県', None),
    'ISL_042': ('魚島 愛媛県', None),
    'ISL_044': ('隠岐島後 島根県', None),
    'ISL_045': ('西ノ島 島根県', None),
    'ISL_046': ('中ノ島 海士町 島根県', None),
    'ISL_047': ('知夫里島 島根県', None),
    'ISL_050': ('大島 萩市 山口県', None),
    'ISL_054': ('中島 松山 愛媛県', None),
    'ISL_060': ('大島 宗像 福岡県', None),
    'ISL_061': ('姫島 大分県', None),
    'ISL_063': ('対馬 長崎県', None),
    'ISL_067': ('中通島 長崎県', None),
    'ISL_074': ('黒島 佐世保 長崎県', None),
    'ISL_079': ('黒島 三島村 鹿児島県', None),
    'ISL_080': ('硫黄島 三島村 鹿児島県', None),
    'ISL_081': ('竹島 三島村 鹿児島県', None),
    'ISL_085': ('口之島 十島村 鹿児島県', None),
    'ISL_086': ('中之島 十島村 鹿児島県', None),
    'ISL_114': ('黒島 竹富町 沖縄県', None),  # 八重山の黒島
    'ISL_119': ('南大東島 沖縄県', None),
    'ISL_120': ('北大東島 沖縄県', None),
}

def build_query(isl):
    iid = isl['island_id']
    if iid in SEARCH_OVERRIDES:
        return SEARCH_OVERRIDES[iid][0]
    # 括弧内を除いた名前 + 都道府県
    name = re.sub(r'[（(].*?[)）]', '', isl['name']).strip()
    return f'{name} {isl["prefecture"]}'

def main():
    with open('../data/islands.csv', encoding='utf-8-sig') as f:
        islands = list(csv.DictReader(f))

    results = {}  # island_id -> (lat, lng, display_name)
    total = len(islands)

    for i, isl in enumerate(islands):
        iid = isl['island_id']
        query = build_query(isl)
        print(f'[{i+1}/{total}] {iid} {isl["name"]} → "{query}"', end=' ... ')
        lat, lng, display = nominatim_search(query)
        if lat:
            print(f'({lat:.4f}, {lng:.4f})')
            results[iid] = (lat, lng, display)
        else:
            print('NOT FOUND')
            results[iid] = (None, None, None)
        time.sleep(1.1)  # Nominatim rate limit

    # Save results
    with open('../data/geocode_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    found = sum(1 for v in results.values() if v[0])
    print(f'\n完了: {found}/{total} 件取得')
    print('結果: data/geocode_results.json')
    print('次: apply_geocode.py を実行して build_json.py を更新')

if __name__ == '__main__':
    main()
