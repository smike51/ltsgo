/* LTSGO map prototype. Data: data/<journey>.json (built by tools/build_proto_data.py). */
'use strict';

const NE = 'https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@v5.1.2/geojson/';
const HB = 'https://cdn.jsdelivr.net/gh/aourednik/historical-basemaps@master/geojson/';
const TR = ['carriage', 'foot', 'horse', 'sledge', 'rail', 'water'];
const TR_RU = {carriage: 'экипаж', foot: 'пешком', horse: 'верхом', sledge: 'сани', rail: 'железная дорога', water: 'по воде'};
const TR_STYLE = {
  carriage: {color: '#22476E', dash: null},
  foot:     {color: '#22476E', dash: [0.2, 2]},
  horse:    {color: '#22476E', dash: [3, 1.2, 0.4, 1.2]},
  sledge:   {color: '#6B4E8A', dash: [1.6, 0.8]},
  rail:     {color: '#1B2530', dash: [3, 0.6]},
  water:    {color: '#2F7385', dash: [3, 1.6]},
};
const STATUS = {
  verified_source: ['источник ✓', 'c-ok'], verified_wiki: ['вики ✓', 'c-ok'],
  book_only: ['только книга', 'c-book'], unverified: ['не проверено', 'c-unk'],
  disputed: ['спорно', 'c-bad'], obsolete: ['устарело', 'c-bad'],
};
const PRES = {intact: 'сохранилось', rebuilt: 'отстроено заново', altered: 'перестроено', ruin: 'руины', lost: 'утрачено'};
const POLITY = ['#D9C9A3', '#C7D3B0', '#E0C2B2', '#BFCFD6', '#D8C0D2', '#CFD9C0', '#E3D5A8', '#C9C2DB'];
const MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
const MONTHS_NOM = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'];
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

const $ = id => document.getElementById(id);
const st = {index: [], j: null, segs: [], t: 0, cur: -1, playing: false, last: 0, bordersCache: {}, speed: 1};

/* ---------- geometry ---------- */
const rad = d => d * Math.PI / 180, deg = r => r * 180 / Math.PI;
function gcDist(a, b) { // km
  const [l1, p1, l2, p2] = [rad(a[0]), rad(a[1]), rad(b[0]), rad(b[1])];
  const h = Math.sin((p2 - p1) / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin((l2 - l1) / 2) ** 2;
  return 2 * 6371 * Math.asin(Math.min(1, Math.sqrt(h)));
}
function gcLine(a, b) { // densified great circle, longitudes kept continuous
  const d = gcDist(a, b), n = Math.max(2, Math.ceil(d / 40));
  const [l1, p1, l2, p2] = [rad(a[0]), rad(a[1]), rad(b[0]), rad(b[1])];
  const D = d / 6371, out = [];
  for (let i = 0; i <= n; i++) {
    const f = i / n;
    if (D < 1e-9) { out.push([a[0], a[1]]); continue; }
    const A = Math.sin((1 - f) * D) / Math.sin(D), B = Math.sin(f * D) / Math.sin(D);
    const x = A * Math.cos(p1) * Math.cos(l1) + B * Math.cos(p2) * Math.cos(l2);
    const y = A * Math.cos(p1) * Math.sin(l1) + B * Math.cos(p2) * Math.sin(l2);
    const z = A * Math.sin(p1) + B * Math.sin(p2);
    let lon = deg(Math.atan2(y, x));
    if (out.length) { const pl = out[out.length - 1][0]; while (lon - pl > 180) lon -= 360; while (lon - pl < -180) lon += 360; }
    out.push([lon, deg(Math.atan2(z, Math.hypot(x, y)))]);
  }
  return out;
}
function ringArea(r) { let s = 0; for (let i = 0, j = r.length - 1; i < r.length; j = i++) s += (r[j][0] + r[i][0]) * (r[j][1] - r[i][1]); return Math.abs(s / 2); }
function ringCentroid(r) {
  let a = 0, x = 0, y = 0;
  for (let i = 0, j = r.length - 1; i < r.length; j = i++) {
    const f = r[j][0] * r[i][1] - r[i][0] * r[j][1];
    a += f; x += (r[j][0] + r[i][0]) * f; y += (r[j][1] + r[i][1]) * f;
  }
  return a ? [x / (3 * a), y / (3 * a)] : r[0];
}
function hash(s) { let h = 0; for (const c of s || '') h = (h * 31 + c.charCodeAt(0)) | 0; return Math.abs(h); }

/* ---------- dates ---------- */
function parseDate(s) { const m = /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/.exec(s || ''); return m && {y: +m[1], m: m[2] ? +m[2] : null, d: m[3] ? +m[3] : null}; }
function fmt(p) { return p.d ? `${p.d} ${MONTHS[p.m - 1]} ${p.y}` : p.m ? `${MONTHS_NOM[p.m - 1]} ${p.y}` : `${p.y}`; }
function toGreg(p) { // Julian → Gregorian (+11 days in the 18th c. up to 28.02.1800, +12 after)
  if (!p.d) return null;
  const add = (p.y < 1800 || (p.y === 1800 && p.m <= 2)) ? 11 : 12;
  const dt = new Date(Date.UTC(p.y, p.m - 1, p.d + add));
  return {y: dt.getUTCFullYear(), m: dt.getUTCMonth() + 1, d: dt.getUTCDate()};
}

/* ---------- map ---------- */
const map = new maplibregl.Map({
  container: 'map',
  center: [30, 55], zoom: 3, attributionControl: {compact: true},
  style: {
    version: 8,
    projection: {type: 'globe'},
    glyphs: 'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
    sky: {'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 0.8, 5, 0.3, 7, 0]},
    sources: {
      land: {type: 'geojson', data: NE + 'ne_50m_land.geojson', attribution: 'Natural Earth'},
      lakes: {type: 'geojson', data: NE + 'ne_50m_lakes.geojson'},
      rivers: {type: 'geojson', data: NE + 'ne_50m_rivers_lake_centerlines.geojson'},
      dem: {type: 'raster-dem', tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
            encoding: 'terrarium', tileSize: 256, maxzoom: 12, attribution: 'Terrarium · Mapzen/AWS Open Data'},
      borders: {type: 'geojson', data: {type: 'FeatureCollection', features: []},
                attribution: '<a href="https://github.com/aourednik/historical-basemaps">historical-basemaps</a> (GPL-3.0)'},
      'polity-labels': {type: 'geojson', data: {type: 'FeatureCollection', features: []}},
      route: {type: 'geojson', data: {type: 'FeatureCollection', features: []}},
      now: {type: 'geojson', data: {type: 'FeatureCollection', features: []}},
      stops: {type: 'geojson', data: {type: 'FeatureCollection', features: []}},
      wps: {type: 'geojson', data: {type: 'FeatureCollection', features: []}},
      me:{type: 'geojson', data: {type: 'FeatureCollection', features: []}},
    },
    layers: [
      {id: 'sea', type: 'background', paint: {'background-color': '#AFCBD2'}},
      {id: 'land', type: 'fill', source: 'land', paint: {'fill-color': '#EDF0EA'}},
      {id: 'polity', type: 'fill', source: 'borders',
       paint: {'fill-color': ['to-color', ['get', '_c']], 'fill-opacity': 0.55}},
      {id: 'relief', type: 'hillshade', source: 'dem',
       paint: {'hillshade-exaggeration': 0.55, 'hillshade-shadow-color': '#4A5A55',
               'hillshade-highlight-color': '#FFFFFF', 'hillshade-accent-color': '#6E7B6A'}},
      {id: 'lakes', type: 'fill', source: 'lakes', paint: {'fill-color': '#AFCBD2'}},
      {id: 'rivers', type: 'line', source: 'rivers',
       paint: {'line-color': '#7FA9B5', 'line-width': ['interpolate', ['linear'], ['zoom'], 2, 0.4, 7, 1.4]}},
      {id: 'polity-line', type: 'line', source: 'borders',
       paint: {'line-color': '#7A5A3A', 'line-width': ['interpolate', ['linear'], ['zoom'], 2, 0.5, 7, 1.3],
               'line-dasharray': [3, 2], 'line-opacity': 0.75}},
      {id: 'polity-label', type: 'symbol', source: 'polity-labels', minzoom: 2.5,
       layout: {'text-field': ['get', 'name'], 'text-font': ['Noto Sans Italic'], 'text-transform': 'uppercase',
                'text-size': ['interpolate', ['linear'], ['zoom'], 3, 9, 7, 13], 'text-letter-spacing': 0.15,
                'text-max-width': 8, 'symbol-sort-key': ['-', 0, ['get', 'area']]},
       paint: {'text-color': '#6B4A2A', 'text-halo-color': 'rgba(237,240,234,.8)', 'text-halo-width': 1.2}},
      {id: 'route-future', type: 'line', source: 'route', filter: ['==', ['get', 'idx'], -1],
       layout: {'line-cap': 'round', 'line-join': 'round'},
       paint: {'line-color': '#22476E', 'line-opacity': 0.28, 'line-width': 1.6, 'line-dasharray': [1.5, 1.5]}},
      ...TR.map(tr => ({
        id: 'route-' + tr, type: 'line', source: 'route', filter: ['==', ['get', 'idx'], -1],
        layout: {'line-cap': TR_STYLE[tr].dash ? 'butt' : 'round', 'line-join': 'round'},
        paint: {'line-color': TR_STYLE[tr].color, 'line-width': ['interpolate', ['linear'], ['zoom'], 2, 2, 8, 4],
                ...(TR_STYLE[tr].dash ? {'line-dasharray': TR_STYLE[tr].dash} : {})},
      })),
      {id: 'route-now', type: 'line', source: 'now', layout: {'line-cap': 'round'},
       paint: {'line-color': '#B07D12', 'line-width': ['interpolate', ['linear'], ['zoom'], 2, 2.5, 8, 4.5]}},
      {id: 'wp-dot', type: 'circle', source: 'wps', minzoom: 1.5,
       paint: {'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 2.5, 6, 4.5],
               'circle-color': ['case', ['get', 'interp'], '#F8F9F5', '#2F7385'],
               'circle-stroke-color': '#2F7385', 'circle-stroke-width': 1.4,
               'circle-opacity': ['case', ['get', 'past'], 1, 0.5], 'circle-stroke-opacity': ['case', ['get', 'past'], 1, 0.5]}},
      {id: 'stop-dot', type: 'circle', source: 'stops',
       paint: {'circle-radius': ['case', ['==', ['get', 'state'], 2], 7, ['==', ['get', 'state'], 1], 4, 3],
               'circle-color': ['case', ['==', ['get', 'state'], 2], '#B07D12', ['==', ['get', 'state'], 1], '#22476E', '#F8F9F5'],
               'circle-stroke-color': '#22476E', 'circle-stroke-width': ['case', ['==', ['get', 'state'], 2], 2.5, 1.2],
               'circle-stroke-opacity': ['case', ['==', ['get', 'state'], 0], 0.5, 1]}},
      {id: 'stop-label', type: 'symbol', source: 'stops', minzoom: 3.5,
       layout: {'text-field': ['get', 'name'], 'text-font': ['Noto Sans Regular'], 'text-size': 12,
                'text-offset': [0, 0.9], 'text-anchor': 'top', 'text-optional': true,
                'symbol-sort-key': ['-', 2, ['get', 'state']]},
       paint: {'text-color': '#1B2530', 'text-halo-color': '#F8F9F5', 'text-halo-width': 1.5,
               'text-opacity': ['case', ['==', ['get', 'state'], 0], 0.55, 1]}},
      {id: 'me', type: 'circle', source: 'me',
       paint: {'circle-radius': 6, 'circle-color': '#B07D12', 'circle-stroke-color': '#fff', 'circle-stroke-width': 2}},
    ],
  },
});
map.addControl(new maplibregl.NavigationControl({visualizePitch: true}), 'top-right');
map.addControl(new maplibregl.ScaleControl({unit: 'metric'}), 'bottom-right');
map.addControl(new maplibregl.FullscreenControl({container: document.body}), 'top-right');

/* ---------- data loading ---------- */
async function loadBorders(name) {
  if (!st.bordersCache[name]) {
    st.bordersCache[name] = fetch(HB + name + '.geojson').then(r => r.json()).then(fc => {
      const labels = [];
      for (const f of fc.features) {
        const n = f.properties.NAME || f.properties.ABBREVN || '';
        f.properties._c = POLITY[hash(n) % POLITY.length];
        const polys = f.geometry?.type === 'Polygon' ? [f.geometry.coordinates]
          : f.geometry?.type === 'MultiPolygon' ? f.geometry.coordinates : [];
        let best = null, ba = 0;
        for (const p of polys) { const a = ringArea(p[0]); if (a > ba) { ba = a; best = p[0]; } }
        if (n && best && ba > 0.5)
          labels.push({type: 'Feature', properties: {name: n, area: ba}, geometry: {type: 'Point', coordinates: ringCentroid(best)}});
      }
      return {fc, labels: {type: 'FeatureCollection', features: labels}};
    });
  }
  const b = await st.bordersCache[name];
  if (st.j?.borders !== name) return;
  map.getSource('borders').setData(b.fc);
  map.getSource('polity-labels').setData(b.labels);
}

async function openJourney(key, stopIdx = 0) {
  stopPlay();
  const j = await fetch(`data/${key}.json`, {cache: 'no-cache'}).then(r => r.json());
  st.j = j; st.cur = -1;
  $('b-title').textContent = j.title_ru;
  $('b-by').textContent = `${j.author_ru} · ${j.years}`;
  $('b-borders').textContent = `карта ${j.borders.replace('world_', '')} г.` + (j.borders === 'world_1815' ? ' (ближайшая к 1852)' : '');
  for (const b of $('books').children) b.setAttribute('aria-selected', b.dataset.k === key);

  // carry forward known dates so undated stops show "after <last date>"
  let lastDate = null;
  j.stops.forEach(s => { if (s.arrived) lastDate = s.arrived; s._after = s.arrived ? null : lastDate; });

  st.segs = [];
  const feats = [];
  for (let i = 1; i < j.stops.length; i++) {
    const a = j.stops[i - 1], b = j.stops[i];
    // real leg geometry from the build (sea route through text waypoints), else a great circle
    const coords = b.leg?.length > 1 ? b.leg : gcLine([a.lon, a.lat], [b.lon, b.lat]);
    let km = 0;
    for (let k = 1; k < coords.length; k++) km += gcDist(coords[k - 1], coords[k]);
    st.segs.push({coords, tr: b.transport, km});
    feats.push({type: 'Feature', properties: {idx: i, tr: b.transport}, geometry: {type: 'LineString', coordinates: coords}});
  }
  map.getSource('route').setData({type: 'FeatureCollection', features: feats});
  $('pos').max = (j.stops.length - 1) * 100;
  loadBorders(j.borders);

  fitAll();
  buildList();
  setT(stopIdx, false);
  history.replaceState(null, '', `#${key}/${stopIdx}`);
}

function padding() {
  const narrow = innerWidth < 760, open = !$('story').classList.contains('collapsed');
  return narrow ? {top: 40, bottom: open ? innerHeight * 0.5 : 130, left: 30, right: 30}
                : {top: 60, bottom: 110, left: open ? 400 : 60, right: $('list').hidden ? 80 : 400};
}
function fitAll() {
  const b = new maplibregl.LngLatBounds();
  st.j.stops.forEach(s => b.extend([s.lon, s.lat]));
  (st.j.waypoints || []).forEach(w => b.extend([w.lon, w.lat]));
  map.setPadding({top: 0, bottom: 0, left: 0, right: 0}); // fitBounds adds to the camera padding left by easeTo
  map.fitBounds(b, {padding: padding(), duration: reduceMotion ? 0 : 1200, maxZoom: 5});
}

/* ---------- position ---------- */
function setT(t, fromPlay) {
  const n = st.j.stops.length - 1;
  st.t = Math.max(0, Math.min(n, t));
  const i = Math.floor(st.t + 1e-6), f = st.t - i;
  $('pos').value = Math.round(st.t * 100);

  const past = ['<=', ['get', 'idx'], i];
  for (const tr of TR) map.setFilter('route-' + tr, ['all', ['==', ['get', 'tr'], tr], past]);
  map.setFilter('route-future', ['>', ['get', 'idx'], i]);

  let me = [st.j.stops[i].lon, st.j.stops[i].lat], partial = [];
  if (f > 0.001 && i < n) {
    const c = st.segs[i].coords, k = f * (c.length - 1), k0 = Math.floor(k);
    const p0 = c[k0], p1 = c[Math.min(k0 + 1, c.length - 1)], r = k - k0;
    me = [p0[0] + (p1[0] - p0[0]) * r, p0[1] + (p1[1] - p0[1]) * r];
    partial = [...c.slice(0, k0 + 1), me];
  }
  map.getSource('now').setData(partial.length > 1
    ? {type: 'Feature', properties: {}, geometry: {type: 'LineString', coordinates: partial}}
    : {type: 'FeatureCollection', features: []});
  map.getSource('me').setData({type: 'Feature', properties: {}, geometry: {type: 'Point', coordinates: me}});

  if (i !== st.cur) {
    st.cur = i;
    map.getSource('stops').setData({type: 'FeatureCollection', features: st.j.stops.map((s, k) => ({
      type: 'Feature', properties: {idx: k, name: s.name, state: k === i ? 2 : k < i ? 1 : 0},
      geometry: {type: 'Point', coordinates: [s.lon, s.lat]}}))});
    map.getSource('wps').setData({type: 'FeatureCollection', features: (st.j.waypoints || []).map((w, k) => ({
      type: 'Feature', properties: {k, past: w.after < i, interp: !!w.interp},
      geometry: {type: 'Point', coordinates: [w.lon, w.lat]}}))});
    renderStop(i);
    markList(i);
    if ($('l-follow').checked) flyToStop(i, fromPlay);
    history.replaceState(null, '', `#${st.j.journey}/${i}`);
  }
}

function zoomFor(i) {
  const s = st.segs, d = Math.max(s[i - 1]?.km || 0, s[i]?.km || 0) || 100;
  return Math.max(2.2, Math.min(8.5, 9.5 - Math.log2(Math.max(d, 10) / 12)));
}
function flyToStop(i, fromPlay) {
  const s = st.j.stops[i];
  map.easeTo({center: [s.lon, s.lat], zoom: zoomFor(i), padding: padding(),
              duration: reduceMotion ? 0 : fromPlay ? 1600 : 900});
}

/* ---------- panel ---------- */
function el(tag, attrs = {}, text) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  return e;
}
function renderStop(i) {
  const s = st.j.stops[i], n = st.j.stops.length;
  $('s-n').textContent = `Остановка ${i + 1} из ${n}`;
  $('s-name').textContent = s.name;
  $('pos-lbl').textContent = `${i + 1} / ${n}`;

  const p = parseDate(s.arrived);
  if (p) {
    $('s-jul').textContent = fmt(p) + (p.d ? ' (ст. ст.)' : '');
    const g = toGreg(p);
    $('s-greg').textContent = g ? fmt(g) + ' (н. ст.)' : '';
  } else {
    const a = parseDate(s._after);
    $('s-jul').textContent = a ? `после: ${fmt(a)}` : 'дата не указана';
    $('s-greg').textContent = '';
  }
  if (s.date_in_text) $('s-greg').textContent += (($('s-greg').textContent ? ' · ' : '') + `в тексте: «${s.date_in_text}»`);

  const [lbl, cls] = STATUS[s.status] || [s.status || '—', 'c-unk'];
  $('s-status').textContent = lbl; $('s-status').className = 'chip ' + cls;
  $('s-tr').textContent = i === 0 ? 'начало пути' : (TR_RU[s.transport] || s.transport) +
    (s.transport_text && !/^[a-z _-]+$/i.test(s.transport_text) && s.transport_text !== TR_RU[s.transport] ? ` · ${s.transport_text}` : '');
  $('s-letter').textContent = s.heading ? `Глава: ${s.heading}` : '';

  const q = $('s-quotes'); q.replaceChildren();
  s.quotes.forEach(t => q.append(el('blockquote', {}, t)));

  const pp = $('s-people'); pp.replaceChildren();
  s.people.forEach(x => pp.append(x.wikidata
    ? el('a', {href: `https://www.wikidata.org/wiki/${x.wikidata}`, target: '_blank', rel: 'noopener'}, x.name)
    : el('span', {title: 'нет в Wikidata'}, x.name)));

  // text waypoints on the way to the next stop
  const wy = $('s-way'), next = (st.j.waypoints || []).map((w, k) => ({...w, k})).filter(w => w.after === i);
  wy.replaceChildren(); wy.hidden = !next.length;
  if (next.length) {
    wy.append(el('span', {class: 'eyebrow'}, `В пути — по тексту (${next.length})`));
    next.forEach(w => {
      const b = el('button', {type: 'button'});
      b.append(el('b', {}, wpHead(w)), el('q', {}, w.quote));
      b.onclick = () => showWp(w.k, true);
      wy.append(b);
    });
  }

  const md = $('s-media'); md.replaceChildren();
  s.media.forEach(m => {
    const fig = el('figure'), a = el('a', {href: m.page || m.src, target: '_blank', rel: 'noopener'});
    const img = el('img', {src: m.src, alt: m.title || s.name, loading: 'lazy'});
    img.onerror = () => fig.remove();
    a.append(img);
    const cap = el('figcaption');
    cap.append(el('b', {}, [m.author, m.year].filter(Boolean).join(', ') || 'автор не указан'), ` · ${m.licence}`);
    fig.append(a, cap); md.append(fig);
  });

  const nw = $('s-now'); nw.replaceChildren(); nw.hidden = !s.now?.length;
  if (s.now?.length) {
    nw.append(el('span', {class: 'eyebrow'}, 'Сегодня' + (PRES[s.preservation] ? ' · ' + PRES[s.preservation] : '')));
    s.now.forEach(f => {
      const [lbl, cls] = STATUS[f.status] || [f.status || '—', 'c-unk'];
      const pEl = el('p', {}, f.value + ' ');
      pEl.append(el('span', {class: 'chip ' + cls}, lbl), ' ',
                 el('a', {href: f.source_url, target: '_blank', rel: 'noopener', title: f.quote || ''}, f.source_title || 'источник'));
      nw.append(pEl);
    });
  }

  $('s-note').hidden = !s.note; $('s-note').textContent = s.note ? `Примечание базы: ${s.note}` : '';
}

/* ---------- text waypoints ---------- */
const ll = (v, pos, neg) => `${Math.abs(v).toFixed(1).replace('.0', '')}° ${v >= 0 ? pos : neg}`;
function wpHead(w) {
  const p = parseDate(w.date);
  return [p ? fmt(p) : 'дата не указана',
          w.interp === 'lon' ? ll(w.lat, 'с. ш.', 'ю. ш.') : w.interp === 'lat' ? ll(w.lon, 'в. д.', 'з. д.')
            : `${ll(w.lat, 'с. ш.', 'ю. ш.')}, ${ll(w.lon, 'в. д.', 'з. д.')}`,
          w.winds?.length ? 'ветер ' + w.winds.join(', ') : ''].filter(Boolean).join(' · ');
}
let wpPopup = null;
function showWp(k, fly) {
  const w = st.j.waypoints[k], d = el('div', {class: 'wp-pop'});
  d.append(el('b', {}, wpHead(w)), el('q', {}, w.quote));
  if (w.interp) d.append(el('small', {}, (w.interp === 'lon' ? 'Долгота' : 'Широта') + ' в тексте не названа — точка поставлена между соседними.'));
  if (w.note) d.append(el('small', {}, w.note));
  if (w.people?.length) d.append(el('small', {}, 'Упомянуты здесь: ' + w.people.map(x => x.name).join(', ')));
  d.append(el('small', {}, (STATUS[w.status] || [w.status])[0] + ` · глава ${w.passage}`));
  wpPopup?.remove();
  wpPopup = new maplibregl.Popup({closeButton: true, maxWidth: '280px', offset: 8}).setLngLat([w.lon, w.lat]).setDOMContent(d).addTo(map);
  if (fly) map.easeTo({center: [w.lon, w.lat], zoom: Math.max(map.getZoom(), 4), padding: padding(), duration: reduceMotion ? 0 : 900});
}
map.on('click', 'wp-dot', e => showWp(e.features[0].properties.k, false));
map.on('mouseenter', 'wp-dot', () => { map.getCanvas().style.cursor = 'pointer'; });
map.on('mouseleave', 'wp-dot', () => { map.getCanvas().style.cursor = ''; });

/* ---------- playback ---------- */
function tick(ts) {
  if (!st.playing) return;
  const dt = Math.min(0.5, (ts - (st.last || ts)) / 1000) * st.speed; st.last = ts;
  const i = Math.floor(st.t), seg = st.segs[i];
  // ~1.2 s per short hop, up to ~4 s for an ocean crossing
  const dur = seg ? 1.2 + Math.min(2.8, Math.log10(1 + seg.km / 50)) : 1;
  if (st.hold > 0) { st.hold -= dt; requestAnimationFrame(tick); return; } // linger at a stop
  let t = st.t + dt / dur;
  if (Math.floor(t) > i) { t = i + 1; st.hold = 1.1; }
  setT(t, true);
  if (st.t >= st.j.stops.length - 1) { stopPlay(); return; }
  requestAnimationFrame(tick);
}
function startPlay() {
  if (st.t >= st.j.stops.length - 1) setT(0, false);
  st.playing = true; st.last = 0; st.hold = 0;
  $('play').textContent = '❚❚ Стоп'; $('play').setAttribute('aria-pressed', 'true');
  requestAnimationFrame(tick);
}
function stopPlay() {
  st.playing = false;
  $('play').textContent = '▶ Ехать'; $('play').setAttribute('aria-pressed', 'false');
}

/* ---------- stop list ---------- */
function buildList() {
  const ol = $('list-items'); ol.replaceChildren();
  st.j.stops.forEach((s, k) => {
    const p = parseDate(s.arrived), b = el('button', {type: 'button', 'data-i': k});
    b.append(el('span', {class: 'n'}, String(k + 1)), el('span', {}, s.name),
             el('span', {class: 'd'}, p ? fmt(p) : k === 0 ? 'начало' : ''));
    b.onclick = () => { stopPlay(); setT(k, false); if (innerWidth < 760) toggleList(false); };
    s._hay = [s.name, s.name_en, s.heading, ...(s.quotes || []), ...(s.people || []).map(x => x.name)].join(' ').toLowerCase();
    const li = el('li'); li.append(b); ol.append(li);
  });
  filterList();
}
function filterList() {
  if (!st.j) return;
  const q = $('q').value.trim().toLowerCase();
  $('list-items').querySelector('.empty')?.remove();
  let shown = 0;
  for (const li of $('list-items').children) {
    const ok = !q || st.j.stops[+li.firstChild.dataset.i]._hay.includes(q);
    li.hidden = !ok; shown += ok;
  }
  if (!shown) $('list-items').append(el('li', {class: 'empty'}, 'Ничего не найдено'));
}
function markList(i) {
  for (const b of $('list-items').querySelectorAll('button')) b.setAttribute('aria-current', +b.dataset.i === i);
  if (!$('list').hidden) $('list-items').querySelector(`[data-i="${i}"]`)?.scrollIntoView({block: 'nearest'});
}
function toggleList(open = $('list').hidden) {
  if (!st.j) return;
  $('list').hidden = !open; $('list-btn').setAttribute('aria-expanded', open);
  if (open) { markList(st.cur); if (innerWidth >= 760) $('q').focus(); }
}
function togglePanel(open) {
  $('story').classList.toggle('collapsed', !open); $('reopen').hidden = open;
  $('collapse').setAttribute('aria-expanded', open);
  (open ? $('collapse') : $('reopen')).focus();
}

/* ---------- controls ---------- */
$('list-btn').onclick = () => toggleList();
$('list-close').onclick = () => toggleList(false);
$('q').oninput = filterList;
$('q').onkeydown = e => {
  if (e.key === 'Enter') $('list-items').querySelector('li:not([hidden]) button')?.click();
  if (e.key === 'Escape') toggleList(false);
};
$('fit').onclick = () => { stopPlay(); $('l-follow').checked = false; fitAll(); };
$('speed').onchange = e => { st.speed = +e.target.value; };
$('collapse').onclick = () => togglePanel(false);
$('reopen').onclick = () => togglePanel(true);
$('share').onclick = async () => {
  const b = $('share');
  try { await navigator.clipboard.writeText(location.href); b.textContent = 'Скопировано'; }
  catch { prompt('Ссылка на остановку:', location.href); }
  setTimeout(() => { b.textContent = 'Ссылка'; }, 1500);
};
$('play').onclick = () => st.playing ? stopPlay() : startPlay();
$('prev').onclick = () => { stopPlay(); setT(Math.ceil(st.t - 1e-6) - 1, false); };
$('next').onclick = () => { stopPlay(); setT(Math.floor(st.t + 1e-6) + 1, false); };
$('pos').oninput = e => { stopPlay(); setT(e.target.value / 100, false); };
addEventListener('keydown', e => {
  const tg = e.target.tagName;
  if ((tg === 'INPUT' && e.target.type !== 'checkbox') || tg === 'SELECT') return;
  const k = e.key.toLowerCase();
  if (k === 'l' || k === 'д') { e.preventDefault(); toggleList(); return; }
  if (k === 'f' || k === 'а') { $('fit').click(); return; }
  if (e.key === 'Escape' && !$('list').hidden) { toggleList(false); return; }
  if (e.key === 'ArrowRight') $('next').click();
  else if (e.key === 'ArrowLeft') $('prev').click();
  else if (e.key === ' ' && e.target.tagName !== 'BUTTON') { e.preventDefault(); $('play').click(); }
});
$('l-borders').onchange = e => ['polity', 'polity-line', 'polity-label'].forEach(l =>
  map.setLayoutProperty(l, 'visibility', e.target.checked ? 'visible' : 'none'));
$('l-relief').onchange = e => map.setLayoutProperty('relief', 'visibility', e.target.checked ? 'visible' : 'none');
$('l-globe').onchange = e => map.setProjection({type: e.target.checked ? 'globe' : 'mercator'});
$('l-follow').onchange = e => { if (e.target.checked && st.j) flyToStop(st.cur, false); };

map.on('click', 'stop-dot', e => { stopPlay(); setT(e.features[0].properties.idx, false); });
map.on('mouseenter', 'stop-dot', () => { map.getCanvas().style.cursor = 'pointer'; });
map.on('mouseleave', 'stop-dot', () => { map.getCanvas().style.cursor = ''; });

map.once('style.load', async () => {
  st.index = await fetch('data/index.json', {cache: 'no-cache'}).then(r => r.json());
  for (const x of st.index) {
    const b = el('button', {type: 'button', role: 'tab', 'data-k': x.journey}, x.author_ru.split(' ').pop());
    b.onclick = () => openJourney(x.journey);
    $('books').append(b);
  }
  const [hk, hs] = decodeURIComponent(location.hash.slice(1)).split('/');
  const key = st.index.some(x => x.journey === hk) ? hk : st.index[0].journey;
  openJourney(key, +hs || 0);
});
