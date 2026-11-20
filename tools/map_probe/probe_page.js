setTimeout(() => {
  const q = new URLSearchParams(location.search);
  map.jumpTo({center: [+q.get('x'), +q.get('y')], zoom: +q.get('z')});
  let n = 0;
  const t = setInterval(() => {
    map.triggerRepaint();
    const lab = id => map.queryRenderedFeatures({layers: [id]}).map(f => f.properties.name + (f.properties.now ? '(' + f.properties.now + ')' : ''));
    const s = lab('stop-label'), c = lab('city-label');
    if ((s.length && c.length) || ++n > 40) {
      clearInterval(t);
      const p = document.createElement('pre'); p.id = 'out';
      p.textContent = 'n=' + n + ' STOPS: ' + s.join(', ') + ' || CITIES: ' + c.join(', ');
      document.body.append(p);
    }
  }, 500);
}, 5000);
