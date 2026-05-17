#!/usr/bin/env python3
"""全港の座標をNominatimで更新してports.csvに反映する"""
import csv, json, time, urllib.request, urllib.parse

HEADERS = {'User-Agent': 'CarFerryMap/1.0 (hiroki2000au20@gmail.com)'}

# 検索クエリのオーバーライド（港名のみで見つかりにくいもの）
OVERRIDES = {
    'PORT_001': '稚内港 北海道',
    'PORT_011': '東京港 竹芝桟橋',
    'PORT_020': '新岡山港 玉野市',
    'PORT_021': '宇野港 玉野市 岡山',
    'PORT_024': '詫間港 三豊市 香川',   # 宮の下港
    'PORT_026': '土生港 因島 広島',
    'PORT_030': '七類港 松江市 島根',
    'PORT_035': '三津浜港 松山市 愛媛',
    'PORT_039': '伊美港 国東市 大分',
    'PORT_050': '串木野新港 いちき串木野 鹿児島',
    'PORT_051': '鹿児島港 南埠頭',
    'PORT_052': '宮之浦港 屋久島',
    'PORT_053': '古仁屋港 瀬戸内町 奄美',
    'PORT_054': '泊港 那覇 沖縄',
    'PORT_057': '平敷屋港 うるま市 沖縄',
    'PORT_058': '安座真港 南城市 沖縄',
    'PORT_059': '平良港 宮古島 沖縄',
    'PORT_060': '石垣港 離島ターミナル 沖縄',
    'PORT_061': '姪浜渡船場 福岡市',
    'PORT_062': '薄香漁港 平戸市 長崎',
    'PORT_063': '小方港 大竹市 広島',
    'PORT_064': '瀬戸港 西海市 長崎',
    'PORT_065': '大道港 天草市 熊本',
    'PORT_066': '柳井港 柳井市 山口',
    'PORT_067': '大道港 上天草市 熊本',
    'PORT_068': '日生港 備前市 岡山',
    'PORT_069': '六甲アイランド 神戸市',
    'PORT_070': '名瀬港 奄美市 鹿児島',
    'PORT_071': '亀徳港 徳之島 鹿児島',
    'PORT_072': '和泊港 沖永良部島 鹿児島',
    'PORT_073': '有明埠頭 江東区 東京',
    'PORT_074': '大阪南港フェリーターミナル',
    'PORT_075': '谷山港 鹿児島市',
    'PORT_076': '名古屋港 名古屋市',
    'PORT_077': '六甲アイランドフェリーターミナル 神戸市',
}

def search(query):
    params = urllib.parse.urlencode({
        'q': query, 'format': 'json', 'limit': 1,
        'accept-language': 'ja', 'countrycodes': 'jp',
    })
    req = urllib.request.Request(
        f'https://nominatim.openstreetmap.org/search?{params}', headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read())
            if res:
                return float(res[0]['lat']), float(res[0]['lon'])
    except Exception as e:
        print(f'  ERR: {e}')
    return None, None

def main():
    with open('../data/ports.csv', encoding='utf-8-sig') as f:
        ports = list(csv.DictReader(f))

    results = {}
    total = len(ports)

    for i, p in enumerate(ports):
        pid = p['port_id']
        query = OVERRIDES.get(pid, f"{p['port_name']} {p['city']} {p['prefecture']}")
        print(f'[{i+1}/{total}] {pid} {p["port_name"]} → "{query}"', end=' ... ')
        lat, lng = search(query)
        if lat:
            print(f'({lat:.4f}, {lng:.4f})')
            results[pid] = (lat, lng)
        else:
            print('NOT FOUND')
            results[pid] = (None, None)
        time.sleep(1.1)

    # Update ports.csv
    updated = skipped = 0
    for p in ports:
        pid = p['port_id']
        lat, lng = results.get(pid, (None, None))
        if lat:
            p['lat'] = f'{lat:.4f}'
            p['lng'] = f'{lng:.4f}'
            updated += 1
        else:
            skipped += 1

    with open('../data/ports.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['port_id','port_name','city','prefecture','lat','lng'])
        w.writeheader()
        w.writerows(ports)

    print(f'\n完了: {updated}/{total} 更新, {skipped} スキップ')
    print('ports.csv 更新済み。次: build_json.py を実行')

if __name__ == '__main__':
    main()
