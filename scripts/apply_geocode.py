#!/usr/bin/env python3
"""geocode_results.json の座標を build_json.py の ISLAND_COORDS に反映する"""
import json, re

with open('../data/geocode_results.json', encoding='utf-8') as f:
    results = json.load(f)

with open('build_json.py', encoding='utf-8') as f:
    src = f.read()

# Find ISLAND_COORDS block and replace coordinates
updated = 0
skipped = 0

for iid, (lat, lng, display) in results.items():
    if lat is None:
        skipped += 1
        continue
    # Match pattern: 'ISL_XXX': (old_lat, old_lng),  # comment
    pattern = rf"('{iid}':\s*)\([^)]+\)(\s*,\s*#[^\n]*)"
    replacement = rf"\g<1>({lat:.4f}, {lng:.4f})\2"
    new_src, n = re.subn(pattern, replacement, src)
    if n:
        src = new_src
        updated += 1
    else:
        print(f'  WARNING: {iid} not found in ISLAND_COORDS')

with open('build_json.py', 'w', encoding='utf-8') as f:
    f.write(src)

print(f'Updated: {updated} islands')
print(f'Skipped (no geocode): {skipped} islands')
print('Next: run build_json.py to regenerate JSON')
