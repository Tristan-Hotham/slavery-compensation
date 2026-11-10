/* Where slavery money came home. The geocoded addresses of the Legacies of British Slavery database (UCL) on a plain MapLibre
 * base map (OpenFreeMap Positron), with historic counties shaded by addresses per 10,000 people in 1831 (England and Wales as
 * approximate outlines rebuilt from 1851 parishes, Scotland as circles). No personal names are loaded: each dot links to its
 * record at UCL. Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const FORMS = ['street address', 'named house', 'town or village only', 'institution'];
  const FORMC = ['#24425E', '#B7712A', '#8A8F96', '#6E5596'];
  const PREC = ['the building itself', 'the street', 'the town, village or parish only'];
  const RB = [0.5, 1, 2, 3, 5], RC = ['#F3EBDD', '#E6D2B5', '#D2AE83', '#B5835A', '#8C5634', '#5C2E1B'];
  const rateExpr = v => ['step', v, RC[0], RB[0], RC[1], RB[1], RC[2], RB[2], RC[3], RB[3], RC[4], RB[4], RC[5]];
  let map = null, site = null, mode = 'form';
  const fmt = (v, d = 1) => Number(v).toLocaleString('en-GB', { maximumFractionDigits: d, minimumFractionDigits: d });
  document.getElementById('theme').addEventListener('click', () => { const r = document.documentElement, d = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; r.dataset.theme = d ? 'light' : 'dark'; });
  const ct = document.getElementById('cartouche'); const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));
  const lp = document.getElementById('lp'), lb = document.getElementById('lyrBtn');
  lb.addEventListener('click', () => { const o = !lp.classList.contains('open'); lp.classList.toggle('open', o); lb.setAttribute('aria-expanded', o); });
  function vis(ids, on) { ids.forEach(id => { if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none'); }); }
  function setMode(m) {
    mode = m;
    document.querySelectorAll('.chip[data-m]').forEach(x => x.setAttribute('aria-pressed', x.dataset.m === m));
    document.getElementById('keyForm').hidden = m !== 'form';
    if (map && map.getLayer('dots')) map.setPaintProperty('dots', 'circle-color', m === 'form' ? ['case', ['==', ['get', 'c'], 'Great Britain'], ['match', ['get', 'f'], 0, FORMC[0], 1, FORMC[1], 2, FORMC[2], FORMC[3]], '#9AA0A6'] : '#3B2A20');
  }
  document.querySelectorAll('.chip[data-m]').forEach(b => b.addEventListener('click', () => setMode(b.dataset.m)));

  function countyHtml(p) {
    const cov = p.cov == null || p.cov === '' ? 'none listed' : `${Math.round(p.cov)}% located`;
    return `<b class="t">${esc(p.county)}</b><table><tr><td>Located addresses</td><td>${Number(p.n).toLocaleString('en-GB')}</td></tr>` +
      `<tr><td>Per 10,000 people</td><td>${fmt(p.rate, 2)}</td></tr><tr><td>People in 1831</td><td>${Number(p.pop).toLocaleString('en-GB')}</td></tr>` +
      `<tr><td>People linked</td><td>${Number(p.people).toLocaleString('en-GB')}</td></tr>` +
      `<tr><td>All LBS addresses</td><td>${Number(p.all).toLocaleString('en-GB')} (${cov})</td></tr></table>` +
      `<p class="nt">Historic county. Rate = located addresses per 10,000 people in the 1831 census. Great Britain: ${fmt(site.rate, 2)}.</p>`;
  }
  function dotHtml(p) {
    const place = [p.t, p.k].filter(Boolean).map(esc).join(', ');
    return `<b class="t">${place || 'Address'}</b><table><tr><td>Address type</td><td>${FORMS[p.f]}</td></tr>` +
      `<tr><td>People linked</td><td>${p.n}</td></tr><tr><td>Placed at</td><td>${PREC[p.p]}</td></tr></table>` +
      `<p class="nt">Linked in the Legacies of British Slavery database to slave-ownership or the 1830s compensation. Names are not shown here.</p>` +
      (p.pid ? `<p style="margin:6px 0 0"><a href="https://www.ucl.ac.uk/lbs/person/view/${encodeURIComponent(p.pid)}" target="_blank" rel="noopener">Open ${p.n > 1 ? 'a linked record' : 'the linked record'} at UCL</a> (names are shown there; the record lists its addresses)</p>` : '');
  }

  // search
  const q = document.getElementById('q'), sug = document.getElementById('sug');
  let hits = [], cur = -1;
  function show() { sug.innerHTML = hits.map((p, i) => `<li role="option" data-i="${i}" aria-selected="${i === cur}">${esc(p[0])} <span>${p[4]} · ${p[3].toLocaleString('en-GB')} addresses</span></li>`).join(''); sug.style.display = hits.length ? 'block' : 'none'; }
  function pick(p) { sug.style.display = 'none'; q.value = p[0]; map.flyTo({ center: [p[1], p[2]], zoom: p[4] === 'county' ? 8.2 : Math.max(map.getZoom(), 11.5) }); }
  q.addEventListener('input', () => {
    const t = norm(q.value.trim()); cur = -1;
    if (t.length < 2 || !site) { hits = []; show(); return; }
    const a = [], b = [];
    for (const p of site.search) { const n = norm(p[0]); if (n.startsWith(t)) a.push(p); else if (n.includes(t)) b.push(p); if (a.length > 12) break; }
    hits = a.concat(b).slice(0, 12); show();
  });
  q.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { cur = Math.min(cur + 1, hits.length - 1); show(); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { cur = Math.max(cur - 1, 0); show(); e.preventDefault(); }
    else if (e.key === 'Enter' && hits.length) { pick(hits[Math.max(cur, 0)]); }
    else if (e.key === 'Escape') { sug.style.display = 'none'; }
  });
  sug.addEventListener('click', e => { const li = e.target.closest('li'); if (li) pick(hits[+li.dataset.i]); });
  document.addEventListener('click', e => { if (!e.target.closest('.srch')) sug.style.display = 'none'; });
  document.querySelectorAll('[data-go]').forEach(a => a.addEventListener('click', e => {
    e.preventDefault(); const [lon, lat, z] = a.dataset.go.split(',').map(Number);
    document.getElementById('mapWrap').scrollIntoView({ behavior: 'smooth' }); map.flyTo({ center: [lon, lat], zoom: z || 9 });
  }));

  Promise.all(['data/site.json', 'data/points.json', 'data/counties_ew.geojson'].map(u => fetch(u).then(r => r.json()))).then(([S, P, CE]) => {
    site = S;
    if (!window.maplibregl) { document.getElementById('nojs').textContent = 'The map could not load (MapLibre GL JS missing).'; return; }
    map = new maplibregl.Map({ container: 'map', style: STYLE, bounds: [[-7.6, 49.9], [1.9, 58.8]], fitBoundsOptions: { padding: small ? 10 : { top: 30, bottom: 30, left: 380, right: 60 } }, maxZoom: 17, minZoom: 3.5, attributionControl: false });
    window.__map = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    map.addControl(new maplibregl.AttributionControl({ compact: true, customAttribution: 'Addresses: Legacies of British Slavery, UCL · Counties: Dr Tristan Hotham (1851 parishes, Caprettini and Voth 2020; ONS)' }), 'bottom-right');
    map.on('load', () => {
      document.getElementById('nojs').remove();
      const at_ = document.querySelector('.maplibregl-ctrl-attrib'); if (at_ && small) at_.classList.remove('maplibregl-compact-show');
      const first = map.getStyle().layers.find(l => l.type === 'symbol');
      map.addSource('cty', { type: 'geojson', data: CE });
      map.addLayer({ id: 'cty', type: 'fill', source: 'cty', paint: { 'fill-color': rateExpr(['get', 'rate10k']), 'fill-opacity': ['interpolate', ['linear'], ['zoom'], 5, 0.78, 9, 0.4, 12, 0.12] } }, first && first.id);
      map.addLayer({ id: 'cty-l', type: 'line', source: 'cty', paint: { 'line-color': '#FFFFFF', 'line-width': ['interpolate', ['linear'], ['zoom'], 5, 0.6, 10, 1.6] } }, first && first.id);
      const sc = S.scot.map(s => ({ type: 'Feature', properties: s, geometry: { type: 'Point', coordinates: [s.lon, s.lat] } }));
      map.addSource('scot', { type: 'geojson', data: { type: 'FeatureCollection', features: sc } });
      map.addLayer({ id: 'scot', type: 'circle', source: 'scot', paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, ['+', 5, ['*', 0.9, ['sqrt', ['get', 'n']]]], 9, ['+', 10, ['*', 2, ['sqrt', ['get', 'n']]]]], 'circle-color': rateExpr(['get', 'rate']), 'circle-opacity': ['interpolate', ['linear'], ['zoom'], 6, 0.9, 10, 0.35], 'circle-stroke-color': '#5C4A3A', 'circle-stroke-width': 1.2 } });
      const df = P.points.map(p => ({ type: 'Feature', properties: { id: p[0], pid: p[9], f: p[3], n: p[4], p: p[5], t: p[6], k: p[7], c: ['England', 'Wales', 'Scotland'].includes(p[8]) ? 'Great Britain' : p[8] }, geometry: { type: 'Point', coordinates: [p[1], p[2]] } }));
      map.addSource('dots', { type: 'geojson', data: { type: 'FeatureCollection', features: df } });
      map.addLayer({ id: 'dots', type: 'circle', source: 'dots', paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, 2.4, 8, 3.6, 12, 6, 16, 8], 'circle-color': '#3B2A20', 'circle-stroke-color': '#FFFFFF', 'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 4, 0.6, 10, 1.4], 'circle-opacity': 0.92 } });
      setMode(mode);
      map.on('click', e => {
        const f = map.queryRenderedFeatures([[e.point.x - 4, e.point.y - 4], [e.point.x + 4, e.point.y + 4]], { layers: ['dots', 'scot', 'cty'].filter(l => map.getLayoutProperty(l, 'visibility') !== 'none') });
        if (!f.length) return;
        const d = f.find(x => x.layer.id === 'dots'), s = f.find(x => x.layer.id === 'scot'), c = f.find(x => x.layer.id === 'cty');
        let h;
        if (d) {
          const same = f.filter(x => x.layer.id === 'dots');
          h = dotHtml(d.properties) + (same.length > 1 ? `<p class="nt">${same.length} addresses at or near this spot (several are placed at the same town or street centre). Zoom in to separate them.</p>` : '');
        } else if (s) h = countyHtml(s.properties);
        else h = countyHtml({ county: c.properties.county, n: c.properties.addresses, rate: c.properties.rate10k, pop: c.properties.pop1831, people: c.properties.people, all: c.properties.lbs_all, cov: c.properties.coverage_pc });
        new maplibregl.Popup({ maxWidth: '320px' }).setLngLat(e.lngLat).setHTML(h).addTo(map);
      });
      ['dots', 'scot', 'cty'].forEach(id => { map.on('mouseenter', id, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', id, () => map.getCanvas().style.cursor = ''); });
      const labels = map.getStyle().layers.filter(l => l.type === 'symbol').map(l => l.id);
      document.getElementById('lyD').addEventListener('change', e => vis(['dots'], e.target.checked));
      document.getElementById('lyC').addEventListener('change', e => vis(['cty', 'cty-l', 'scot'], e.target.checked));
      document.getElementById('lyL').addEventListener('change', e => vis(labels, e.target.checked));
    });
  }).catch(err => { document.getElementById('nojs').textContent = 'The map data could not load.'; console.error(err); });
})();
