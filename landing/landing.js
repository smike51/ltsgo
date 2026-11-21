/* Landing: language switch, hero route, Verne day scrubber, two small journey maps.
   Verne stops and facts below are a DRAFT from the novel's timeline; landing/research/*.json
   (quotes, images, sources) replace them when ready. */
const T = {
  ru: {
    nav_how: 'Как это работает', nav_example: 'Пример', nav_journeys: 'Путешествия',
    hero_eyebrow: 'Литературный атлас путешествий',
    hero_title: 'Положите книгу на карту времени',
    hero_lead: 'Каждая книга о путешествии — это путь, который где-то и когда-то был пройден. Мы кладём текст на карту его эпохи, соединяем с энциклопедией и библиотекой — и путешествие оживает во времени и пространстве.',
    hero_cap: 'Маршрут Филеаса Фогга, 2 октября – 21 декабря 1872',
    how_eyebrow: 'Как это работает', how_title: 'Четыре слоя — одно путешествие',
    l1_t: 'Книга', l1_p: 'Полный текст по главам. Каждая остановка, дата и человек привязаны к дословной цитате.',
    l2_t: 'Карта времени', l2_p: 'Границы, названия городов и дороги того года. Кёнигсберг, а не Калининград; Эдо, а не Токио.',
    l3_t: 'Энциклопедия', l3_p: 'Кем на самом деле были люди из книги — сверено с энциклопедиями на нескольких языках. Где они расходятся, показываем оба варианта.',
    l4_t: 'Библиотека', l4_p: 'Гравюры, ранние фотографии, открытки и карты эпохи — у каждой автор и лицензия.',
    v_eyebrow: 'Пример · Жюль Верн, 1872', v_title: 'Вокруг света за восемьдесят дней',
    v_lead: 'Двигайте день — и пари разворачивается: поезда, пароходы, слон и сани под парусом.',
    j_eyebrow: 'Первые путешествия', j_title: 'Небольшие путешествия вблизи',
    j1_t: 'Путешественник 1789 года: через Швейцарию',
    j1_p: 'Базель, Цюрих, Берн, Женева — накануне революции, в дилижансе и пешком, с гравюрами, которые путешественник мог купить по дороге.',
    j2_t: 'Двенадцать дней с ослицей по Севеннам',
    j2_p: 'Роберт Льюис Стивенсон и Модестина, от Ле-Монастье до Сен-Жан-дю-Гара: около 200 км, по этому пути ходят и сегодня.',
    p_title: 'Чему можно верить',
    p1: 'У каждого факта есть источник и цитата.', p2: 'Только тексты в общественном достоянии.',
    p3: 'У каждой картинки — автор и лицензия.', p4: 'Даты старого стиля хранятся со своим календарём.',
    foot: 'Ранний проект. Карты: Natural Earth, общественное достояние. Иллюстрации: Wikimedia Commons, авторы указаны у каждой.',
    day: 'День', play: 'Пуск',
  },
};
const EN = {};
document.querySelectorAll('[data-i]').forEach(el => { EN[el.dataset.i] = el.textContent; });
EN.day = 'Day';
let lang = 'en';
try { lang = new URLSearchParams(location.search).get('lang') || localStorage.getItem('lang') || 'en'; } catch (e) {}
const t = k => (lang === 'ru' && T.ru[k]) || EN[k] || k;
function applyLang() {
  document.documentElement.lang = lang;
  document.querySelectorAll('[data-i]').forEach(el => { el.textContent = t(el.dataset.i); });
  document.getElementById('lang').textContent = lang === 'ru' ? 'EN' : 'RU';
  if (window.verneShow) verneShow(+document.getElementById('v-day').value);
}
document.getElementById('lang').onclick = () => {
  lang = lang === 'ru' ? 'en' : 'ru';
  try { localStorage.setItem('lang', lang); } catch (e) {}
  applyLang();
};

/* day = days since departure, 2 Oct 1872 20:45 (London). how = transport of the leg INTO this stop. */
const VERNE = [
  { id: 'london', en: 'London', ru: 'Лондон', lon: -0.13, lat: 51.51, day: 0, date: '2 Oct 1872', how: null,
    fact: { en: 'Reform Club, Pall Mall: the wager of twenty thousand pounds.', ru: 'Реформ-клуб на Пэлл-Мэлл: пари на двадцать тысяч фунтов.' } },
  { id: 'paris', en: 'Paris', ru: 'Париж', lon: 2.35, lat: 48.86, day: 0.5, date: '3 Oct', how: 'rail' },
  { id: 'turin', en: 'Turin', ru: 'Турин', lon: 7.69, lat: 45.07, day: 1.6, date: '4 Oct', how: 'rail',
    fact: { en: 'Through the Mont Cenis tunnel, opened in 1871.', ru: 'Через тоннель Мон-Сени, открытый в 1871 году.' } },
  { id: 'brindisi', en: 'Brindisi', ru: 'Бриндизи', lon: 17.94, lat: 40.64, day: 2.8, date: '5 Oct', how: 'rail' },
  { id: 'suez', en: 'Suez', ru: 'Суэц', lon: 32.55, lat: 29.97, day: 6.6, date: '9 Oct', how: 'sea',
    fact: { en: 'The Suez Canal had been open for only three years.', ru: 'Суэцкий канал был открыт всего три года назад.' } },
  { en: 'Aden', ru: 'Аден', lon: 45.03, lat: 12.8, day: 11.6, date: '14 Oct', how: 'sea', via: [[38.9, 20.5]] },
  { id: 'bombay', en: 'Bombay', ru: 'Бомбей', lon: 72.83, lat: 18.94, day: 17.6, date: '20 Oct', how: 'sea' },
  { id: 'kholby', en: 'Kholby', ru: 'Холби', lon: 77.5, lat: 23.2, day: 19.6, date: '22 Oct', how: 'rail',
    fact: { en: 'The railway was unfinished here: Fogg bought an elephant.', ru: 'Здесь железная дорога обрывалась — Фогг купил слона.' } },
  { id: 'allahabad', en: 'Allahabad', ru: 'Аллахабад', lon: 81.85, lat: 25.44, day: 21.1, date: '23 Oct', how: 'elephant' },
  { id: 'calcutta', en: 'Calcutta', ru: 'Калькутта', lon: 88.36, lat: 22.57, day: 22.6, date: '25 Oct', how: 'rail' },
  { id: 'singapore', en: 'Singapore', ru: 'Сингапур', lon: 103.85, lat: 1.29, day: 28.6, date: '31 Oct', how: 'sea', via: [[91.5, 15], [97.5, 6.5]] },
  { id: 'hongkong', en: 'Hong Kong', ru: 'Гонконг', lon: 114.16, lat: 22.28, day: 34.6, date: '6 Nov', how: 'sea' },
  { id: 'yokohama', en: 'Yokohama', ru: 'Иокогама', lon: 139.64, lat: 35.44, day: 42.6, date: '14 Nov', how: 'sea', via: [[121.5, 26], [129.5, 30.5]] },
  { id: 'sanfrancisco', en: 'San Francisco', ru: 'Сан-Франциско', lon: -122.42, lat: 37.77, day: 61.6, date: '3 Dec', how: 'sea',
    fact: { en: 'The first transcontinental railroad was barely three years old.', ru: 'Первой трансконтинентальной железной дороге было едва три года.' } },
  { id: 'saltlake', en: 'Salt Lake City', ru: 'Солт-Лейк-Сити', lon: -111.89, lat: 40.76, day: 63.6, date: '5 Dec', how: 'rail' },
  { id: 'fortkearney', en: 'Fort Kearney', ru: 'Форт-Керни', lon: -99.0, lat: 40.65, day: 66.1, date: '8 Dec', how: 'rail' },
  { id: 'omaha', en: 'Omaha', ru: 'Омаха', lon: -95.94, lat: 41.26, day: 67.1, date: '9 Dec', how: 'sledge',
    fact: { en: 'Across the frozen prairie on a sledge with a sail.', ru: 'Через замёрзшую прерию на санях под парусом.' } },
  { id: 'newyork', en: 'New York', ru: 'Нью-Йорк', lon: -74.0, lat: 40.71, day: 69.1, date: '11 Dec', how: 'rail' },
  { id: 'queenstown', en: 'Queenstown', ru: 'Квинстаун', lon: -8.29, lat: 51.85, day: 77.1, date: '19 Dec', how: 'sea',
    fact: { en: 'The Henrietta ran out of coal; Fogg burned her woodwork.', ru: 'На «Генриетте» кончился уголь — Фогг сжёг её деревянные части.' } },
  { en: 'Dublin', ru: 'Дублин', lon: -6.26, lat: 53.35, day: 78.6, date: '21 Dec', how: 'rail' },
  { id: 'liverpool', en: 'Liverpool', ru: 'Ливерпуль', lon: -2.98, lat: 53.41, day: 79.6, date: '21 Dec', how: 'sea' },
  { en: 'London', ru: 'Лондон', lon: -0.13, lat: 51.51, day: 80, date: '21 Dec', how: 'rail',
    fact: { en: 'Five minutes late — or so he thought. The date line had given him a day.', ru: 'Опоздал на пять минут — так он думал. Линия перемены дат подарила ему день.' } },
];
const HOW = { rail: ['by rail', 'поездом'], sea: ['by steamer', 'пароходом'], elephant: ['by elephant', 'на слоне'], sledge: ['by sail-sledge', 'на санях под парусом'] };

const pts = s => [...(s.via || []), [s.lon, s.lat]];
function lineOf(stops) { const c = [[stops[0].lon, stops[0].lat]]; stops.slice(1).forEach(s => c.push(...pts(s))); return { type: 'LineString', coordinates: c }; }

async function topo(file) { const r = await fetch(file); return r.json(); }

const SIZE = { 'hero-map': [1000, 430], 'verne-map': [960, 600] }; // fixed viewBox, SVG scales to the box
const dims = el => SIZE[el.id] || [600, 400];
function baseMap(el, projection, land, borders) {
  const [w, h] = dims(el);
  const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${w} ${h}`);
  const path = d3.geoPath(projection);
  svg.append('path').datum(d3.geoGraticule10()).attr('class', 'grat').attr('d', path);
  svg.append('path').datum(land).attr('class', 'land').attr('d', path);
  if (borders) svg.append('path').datum(borders).attr('class', 'land').attr('fill', 'none').attr('d', path);
  return { svg, path, w, h };
}

(async function () {
  applyLang();
  const world = await topo('data/countries-110m.json');
  const land = topojson.merge(world, world.objects.countries.geometries);
  const borders = topojson.mesh(world, world.objects.countries, (a, b) => a !== b);
  try { // verified quotes and period engravings from landing research (data/verne.json)
    const extra = (await topo('data/verne.json')).stops;
    VERNE.forEach(st => Object.assign(st, extra[st.id] || {}));
  } catch (e) {}
  const route = lineOf(VERNE);

  // hero: whole route drawn once
  {
    const el = document.getElementById('hero-map');
    const proj = d3.geoNaturalEarth1().rotate([-10, 0]).fitWidth(1000, { type: 'Sphere' }); // Antarctica cropped by the box
    const m = baseMap(el, proj, land, borders);
    const p = m.svg.append('path').datum(route).attr('class', 'route').attr('d', m.path);
    const L = p.node().getTotalLength();
    p.attr('stroke-dasharray', L).attr('stroke-dashoffset', L).transition().duration(4200).ease(d3.easeCubicInOut).attr('stroke-dashoffset', 0);
    m.svg.selectAll('circle').data(VERNE).join('circle').attr('class', 'dot').attr('r', 2.6)
      .attr('transform', d => `translate(${proj([d.lon, d.lat])})`);
  }

  // Verne: day scrubber
  {
    const el = document.getElementById('verne-map');
    const proj = d3.geoNaturalEarth1().rotate([-10, 0]).fitExtent([[12, 12], [dims(el)[0] - 12, dims(el)[1] - 12]], { type: 'Sphere' });
    const m = baseMap(el, proj, land, borders);
    m.svg.append('path').datum(route).attr('class', 'route-ghost').attr('d', m.path);
    const done = m.svg.append('path').attr('class', 'route');
    const dots = m.svg.selectAll('circle.dot').data(VERNE).join('circle').attr('class', 'dot').attr('r', 3.2)
      .attr('transform', d => `translate(${proj([d.lon, d.lat])})`);
    const me = m.svg.append('circle').attr('class', 'me').attr('r', 5.5);
    const $ = id => document.getElementById(id);
    // position along the route at a given day: interpolate between stops along their leg coordinates
    function at(day) {
      let i = VERNE.findIndex(s => s.day > day);
      if (i < 0) return { idx: VERNE.length - 1, coords: route.coordinates, here: route.coordinates.at(-1) };
      const a = VERNE[i - 1], b = VERNE[i], f = (day - a.day) / (b.day - a.day);
      const leg = { type: 'LineString', coordinates: [[a.lon, a.lat], ...pts(b)] };
      const len = d3.geoLength(leg); let need = f * len, here = leg.coordinates[0]; const passed = [leg.coordinates[0]];
      for (let k = 1; k < leg.coordinates.length; k++) {
        const seg = d3.geoDistance(leg.coordinates[k - 1], leg.coordinates[k]);
        if (need <= seg) { here = d3.geoInterpolate(leg.coordinates[k - 1], leg.coordinates[k])(seg ? need / seg : 0); break; }
        need -= seg; here = leg.coordinates[k]; passed.push(here);
      }
      const before = lineOf(VERNE.slice(0, i)).coordinates;
      return { idx: i - 1, coords: [...before, ...passed.slice(1), here], here, moving: b };
    }
    window.verneShow = day => {
      const s = at(day), st = VERNE[s.idx], ru = lang === 'ru';
      done.datum({ type: 'LineString', coordinates: s.coords }).attr('d', m.path);
      me.attr('transform', `translate(${proj(s.here)})`);
      dots.classed('on', (d, k) => k === s.idx);
      $('v-daylab').textContent = `${t('day')} ${Math.floor(day)}`;
      $('vc-day').textContent = `${t('day')} ${Math.floor(st.day)}`;
      $('vc-place').textContent = ru ? st.ru : st.en;
      const how = s.moving && s.moving.how ? ` · ${HOW[s.moving.how][ru ? 1 : 0]} → ${ru ? s.moving.ru : s.moving.en}` : '';
      const date = ru ? st.date.replace('Oct', 'окт.').replace('Nov', 'нояб.').replace('Dec', 'дек.') : st.date;
      $('vc-date').textContent = date + how;
      $('vc-quote').textContent = st.quote ? `“${st.quote}”` : '';
      $('vc-fact').textContent = st.fact ? st.fact[ru ? 'ru' : 'en'] : '';
      $('vc-fig').hidden = !st.img;
      if (st.img) { $('vc-img').src = st.img.url; $('vc-img').alt = st.img.caption || ''; $('vc-cap').textContent = [st.img.caption, st.img.credit].filter(Boolean).join(' — '); }
    };
    const input = $('v-day');
    input.oninput = () => verneShow(+input.value);
    let timer = null;
    $('v-play').onclick = () => {
      if (timer) { clearInterval(timer); timer = null; $('v-play').textContent = '▶'; return; }
      if (+input.value >= 80) input.value = 0;
      $('v-play').textContent = '❚❚';
      timer = setInterval(() => {
        input.value = Math.min(80, +input.value + 0.25); verneShow(+input.value);
        if (+input.value >= 80) $('v-play').click();
      }, 60);
    };
    verneShow(0);
  }

  // small journeys: detailed borders of Europe
  const eu = await topo('data/countries-50m.json');
  const euLand = topojson.merge(eu, eu.objects.countries.geometries);
  const euBorders = topojson.mesh(eu, eu.objects.countries, (a, b) => a !== b);
  function journeyMap(id, stops, labels) {
    const el = document.getElementById(id);
    const line = { type: 'LineString', coordinates: stops.map(s => [s.lon, s.lat]) };
    const proj = d3.geoMercator().fitExtent([[110, 80], [dims(el)[0] - 110, dims(el)[1] - 80]], line);
    const m = baseMap(el, proj, euLand, euBorders);
    m.svg.append('path').datum(line).attr('class', 'route').attr('d', m.path);
    m.svg.selectAll('circle').data(stops).join('circle').attr('class', 'dot').attr('r', 3)
      .attr('transform', d => `translate(${proj([d.lon, d.lat])})`);
    m.svg.selectAll('text').data(stops.filter(s => labels.includes(s.en))).join('text').attr('class', 'plabel')
      .attr('x', d => proj([d.lon, d.lat])[0] + 6).attr('y', d => proj([d.lon, d.lat])[1] + 4).text(d => d.en);
  }
  const ch = (await (await fetch('data/europe-1789.json')).json()).slice(0, 28);
  journeyMap('map-1789', ch, ['Basel', 'Zurich', 'Bern', 'Grindelwald', 'Lausanne', 'Geneva']);
  journeyMap('map-1878', CEVENNES, ['Le Monastier', 'Langogne', 'Le Pont-de-Montvert', 'Florac', 'Saint-Jean-du-Gard']);
})();

/* Stevenson, Travels with a Donkey in the Cévennes, 22 Sep – 3 Oct 1878. DRAFT coordinates; research file replaces. */
var CEVENNES = [
  { en: 'Le Monastier', lon: 3.993, lat: 44.938 }, { en: 'Le Bouchet-Saint-Nicolas', lon: 3.789, lat: 44.888 },
  { en: 'Pradelles', lon: 3.884, lat: 44.769 }, { en: 'Langogne', lon: 3.855, lat: 44.727 },
  { en: 'Cheylard-l’Évêque', lon: 3.803, lat: 44.646 }, { en: 'Our Lady of the Snows', lon: 3.924, lat: 44.612 },
  { en: 'La Bastide', lon: 3.900, lat: 44.590 }, { en: 'Le Bleymard', lon: 3.733, lat: 44.487 },
  { en: 'Mont Lozère', lon: 3.755, lat: 44.428 }, { en: 'Le Pont-de-Montvert', lon: 3.745, lat: 44.367 },
  { en: 'Florac', lon: 3.594, lat: 44.324 }, { en: 'Cassagnas', lon: 3.740, lat: 44.258 },
  { en: 'Saint-Germain-de-Calberte', lon: 3.808, lat: 44.218 }, { en: 'Saint-Jean-du-Gard', lon: 3.883, lat: 44.104 },
];
