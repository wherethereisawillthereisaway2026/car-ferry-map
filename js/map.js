// カーフェリー離島マップ
// 車両: ハイエース ワイドボディ 490cm × 190cm × 220cm

let map, selectedIsland = null;
const islandMarkers = {};
const portMarkers = [];
const polylines = [];

// Region filter state
let activeRegion = 'all';

// Build lookups
const portById = {};
const routesByIsland = {};
const pricingByCompany = {};

function buildLookups() {
  FERRY_PORTS.forEach(p => portById[p.id] = p);
  FERRY_ROUTES.forEach(r => {
    if (!routesByIsland[r.island_id]) routesByIsland[r.island_id] = [];
    routesByIsland[r.island_id].push(r);
  });
  FERRY_PRICING.forEach(p => {
    if (!pricingByCompany[p.company]) pricingByCompany[p.company] = [];
    pricingByCompany[p.company].push(p);
  });
}

// Marker icons
function islandIcon(color, type) {
  const opacity = type === 'freight_only' ? 0.5 : 1.0;
  const shape = type === 'conditional' ? 'triangle' : 'circle';
  const size = 12;
  const svg = shape === 'circle'
    ? `<circle cx="12" cy="12" r="${size/2}" fill="${color}" stroke="white" stroke-width="2" opacity="${opacity}"/>`
    : `<polygon points="12,4 20,20 4,20" fill="${color}" stroke="white" stroke-width="2" opacity="${opacity}"/>`;
  return {
    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(
      `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24">${svg}</svg>`
    ),
    scaledSize: new google.maps.Size(24, 24),
    anchor: new google.maps.Point(12, 12),
  };
}

function portIcon() {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28">
    <polygon points="14,2 26,26 2,26" fill="#FF6F00" stroke="white" stroke-width="2"/>
    <text x="14" y="22" text-anchor="middle" font-size="10" fill="white" font-weight="bold">⚓</text>
  </svg>`;
  return {
    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg),
    scaledSize: new google.maps.Size(28, 28),
    anchor: new google.maps.Point(14, 26),
  };
}

function initMap() {
  buildLookups();

  map = new google.maps.Map(document.getElementById('map'), {
    center: { lat: 33.5, lng: 132.0 },
    zoom: 5,
    mapTypeId: 'roadmap',
    mapTypeControl: true,
    streetViewControl: false,
    fullscreenControl: true,
    styles: [
      { featureType: 'water', stylers: [{ color: '#a8d5e5' }] },
      { featureType: 'administrative.country', elementType: 'geometry.stroke',
        stylers: [{ color: '#888' }, { weight: 1 }] },
    ],
  });

  // Plot all islands
  FERRY_ISLANDS.forEach(island => {
    if (!island.lat || !island.lng) return;
    const marker = new google.maps.Marker({
      position: { lat: island.lat, lng: island.lng },
      map,
      title: island.name,
      icon: islandIcon(island.color, island.type),
      zIndex: 10,
    });
    marker.addListener('click', () => selectIsland(island));
    islandMarkers[island.id] = marker;
  });

  buildRegionFilter();
  updateIslandList();
}

// Select island: show ports + polylines + panel
function selectIsland(island) {
  // Reset previous
  clearPortsAndLines();
  if (selectedIsland) {
    const prev = islandMarkers[selectedIsland.id];
    if (prev) prev.setIcon(islandIcon(selectedIsland.color, selectedIsland.type));
  }

  selectedIsland = island;

  // Highlight selected island marker
  const sel = islandMarkers[island.id];
  if (sel) {
    sel.setIcon({
      url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(
        `<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30">
          <circle cx="15" cy="15" r="13" fill="${island.color}" stroke="white" stroke-width="3"/>
          <circle cx="15" cy="15" r="5" fill="white"/>
        </svg>`
      ),
      scaledSize: new google.maps.Size(30, 30),
      anchor: new google.maps.Point(15, 15),
    });
  }

  // Show departure port markers and polylines
  const routes = routesByIsland[island.id] || [];
  const seenPorts = new Set();

  routes.forEach(route => {
    const port = portById[route.port_id];
    if (!port || !port.lat || !port.lng) return;
    const portKey = port.id;

    if (!seenPorts.has(portKey)) {
      seenPorts.add(portKey);
      const pm = new google.maps.Marker({
        position: { lat: port.lat, lng: port.lng },
        map,
        title: port.name,
        icon: portIcon(),
        zIndex: 20,
      });
      pm.addListener('click', () => showPortInfo(port));
      portMarkers.push(pm);

      // Dotted polyline
      const line = new google.maps.Polyline({
        path: [
          { lat: island.lat, lng: island.lng },
          { lat: port.lat, lng: port.lng },
        ],
        geodesic: true,
        strokeColor: island.color,
        strokeOpacity: 0,
        strokeWeight: 2,
        icons: [{
          icon: { path: 'M 0,-1 0,1', strokeOpacity: 0.8, scale: 3 },
          offset: '0',
          repeat: '12px',
        }],
        map,
      });
      polylines.push(line);
    }
  });

  showInfoPanel(island, routes);

  // Pan to island
  map.panTo({ lat: island.lat, lng: island.lng });
}

function clearPortsAndLines() {
  portMarkers.forEach(m => m.setMap(null));
  portMarkers.length = 0;
  polylines.forEach(l => l.setMap(null));
  polylines.length = 0;
}

// Info panel
function showInfoPanel(island, routes) {
  const panel = document.getElementById('info-panel');
  panel.classList.add('open');

  const typeLabel = {
    yes: '<span class="badge ok">マイカーOK</span>',
    conditional: '<span class="badge cond">条件付き</span>',
    freight_only: '<span class="badge freight">貨物扱いのみ</span>',
  }[island.type] || '';

  let routeHTML = '';
  const seenPorts = new Set();
  routes.forEach(r => {
    const port = portById[r.port_id];
    if (!port) return;
    const portKey = `${r.port_id}-${r.company}`;
    if (seenPorts.has(portKey)) return;
    seenPorts.add(portKey);

    // Pricing for this company
    const prices = pricingByCompany[r.company] || [];
    const relevantPrice = prices.find(p =>
      p.route.includes(port.city?.slice(0,2) || '') ||
      prices.length === 1
    ) || prices[0];

    let priceHTML = '';
    if (relevantPrice) {
      const heightCheck = relevantPrice.height_limit
        ? (parseInt(relevantPrice.height_limit) >= 220
            ? '<span class="h-ok">✓ 高さ220cm OK</span>'
            : '<span class="h-ng">⚠ 高さ要確認</span>')
        : '<span class="h-unk">高さ要確認</span>';
      const priceText = relevantPrice.price
        ? `<b>¥${parseInt(relevantPrice.price).toLocaleString()}</b>（片道/車両）`
        : '料金要確認';
      const srcLink = relevantPrice.url
        ? `<a href="${relevantPrice.url}" target="_blank" class="src-link">公式サイトで確認 →</a>`
        : '';
      priceHTML = `
        <div class="price-info">
          ${priceText} ${heightCheck}
          ${srcLink}
          ${relevantPrice.notes ? `<div class="price-note">${relevantPrice.notes}</div>` : ''}
        </div>`;
    } else {
      priceHTML = '<div class="price-info no-price">料金情報なし（公式に要確認）</div>';
    }

    const ferryBadge = r.type === 'freight_only'
      ? '<span class="badge freight">貨物扱い</span>'
      : r.type === 'conditional' ? '<span class="badge cond">条件付き</span>' : '';

    routeHTML += `
      <div class="route-card">
        <div class="route-header">
          <span class="port-name">🚢 ${port.name}</span>
          <span class="arr-port">→ ${r.arrival_port}</span>
          ${ferryBadge}
        </div>
        <div class="company">${r.company}</div>
        ${r.ferry ? `<div class="ferry-name">便名: ${r.ferry}</div>` : ''}
        ${r.notes ? `<div class="route-note">${r.notes}</div>` : ''}
        ${priceHTML}
      </div>`;
  });

  panel.innerHTML = `
    <div class="panel-header">
      <button class="close-btn" onclick="closePanel()">×</button>
      <div class="island-title">
        <span class="island-name">${island.name}</span>
        <span class="island-kana">（${island.kana}）</span>
        ${typeLabel}
      </div>
      <div class="island-meta">${island.pref} / ${island.region}</div>
      ${island.notes ? `<div class="island-notes">${island.notes}</div>` : ''}
    </div>
    <div class="panel-body">
      <div class="routes-title">出港地 (${seenPorts.size}港)</div>
      ${routeHTML || '<p>航路データなし</p>'}
      <div class="pricing-footer">
        ⚠ 料金は変更になることがあります。乗船前に必ず公式サイトでご確認ください。<br>
        最終確認: ${PRICING_LAST_CHECKED}
      </div>
    </div>`;
}

function closePanel() {
  document.getElementById('info-panel').classList.remove('open');
  clearPortsAndLines();
  if (selectedIsland) {
    const prev = islandMarkers[selectedIsland.id];
    if (prev) prev.setIcon(islandIcon(selectedIsland.color, selectedIsland.type));
    selectedIsland = null;
  }
}

function showPortInfo(port) {
  // Show all islands accessible from this port
  const islands = FERRY_ISLANDS.filter(isl => {
    const routes = routesByIsland[isl.id] || [];
    return routes.some(r => r.port_id === port.id);
  });
  const info = `${port.name}\nここから行ける島: ${islands.map(i => i.name).join('、')}`;
  const win = new google.maps.InfoWindow({
    content: `<div style="font-size:13px;line-height:1.6">
      <b>${port.name}</b><br>
      ${port.city}（${port.pref}）<br>
      <small>発着離島: ${islands.map(i => i.name).join('、')}</small>
    </div>`,
    position: { lat: port.lat, lng: port.lng },
  });
  win.open(map);
}

// Region filter
function buildRegionFilter() {
  const regions = [...new Set(FERRY_ISLANDS.map(i => i.region))];
  const container = document.getElementById('region-filter');
  container.innerHTML = `
    <button class="chip active" data-region="all" onclick="filterRegion('all')">全て</button>
    ${regions.map(r => `
      <button class="chip" data-region="${r}" onclick="filterRegion('${r}')"
        style="border-color:${FERRY_ISLANDS.find(i=>i.region===r)?.color}">${r}
      </button>`).join('')}`;
}

function filterRegion(region) {
  activeRegion = region;
  document.querySelectorAll('.chip').forEach(c => {
    c.classList.toggle('active', c.dataset.region === region);
  });
  const visible = region === 'all'
    ? FERRY_ISLANDS
    : FERRY_ISLANDS.filter(i => i.region === region);
  FERRY_ISLANDS.forEach(isl => {
    const m = islandMarkers[isl.id];
    if (m) m.setMap(visible.find(i => i.id === isl.id) ? map : null);
  });
  updateIslandList(region);
  if (selectedIsland && region !== 'all' && selectedIsland.region !== region) closePanel();
}

// Island list panel
function updateIslandList(region = 'all') {
  const list = document.getElementById('island-list');
  const islands = region === 'all'
    ? FERRY_ISLANDS
    : FERRY_ISLANDS.filter(i => i.region === region);
  list.innerHTML = islands
    .sort((a, b) => a.name.localeCompare(b.name, 'ja'))
    .map(isl => `
      <div class="list-item ${isl.type}" onclick="jumpToIsland('${isl.id}')">
        <span class="dot" style="background:${isl.color}"></span>
        <span class="iname">${isl.name}</span>
        <span class="ipref">${isl.pref.replace('県','').replace('都','').replace('道','').replace('府','')}</span>
      </div>`).join('');
}

function jumpToIsland(id) {
  const island = FERRY_ISLANDS.find(i => i.id === id);
  if (!island) return;
  map.setZoom(8);
  map.panTo({ lat: island.lat, lng: island.lng });
  selectIsland(island);
}

// Search
document.addEventListener('DOMContentLoaded', () => {
  const search = document.getElementById('search');
  if (search) {
    search.addEventListener('input', e => {
      const q = e.target.value.trim();
      const list = document.getElementById('island-list');
      const region = activeRegion;
      let islands = region === 'all' ? FERRY_ISLANDS : FERRY_ISLANDS.filter(i => i.region === region);
      if (q) {
        islands = islands.filter(i =>
          i.name.includes(q) || i.kana.includes(q) || i.pref.includes(q)
        );
      }
      list.innerHTML = islands.map(isl => `
        <div class="list-item ${isl.type}" onclick="jumpToIsland('${isl.id}')">
          <span class="dot" style="background:${isl.color}"></span>
          <span class="iname">${isl.name}</span>
          <span class="ipref">${isl.pref.replace('県','').replace('都','').replace('道','').replace('府','')}</span>
        </div>`).join('');
    });
  }
});
