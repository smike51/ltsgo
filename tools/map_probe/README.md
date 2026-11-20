# Проверка карты без окна (headless Edge + DevTools)

Нужна, когда панель браузера скрыта: headless с `--virtual-time-budget` рисует карту ненадёжно,
поэтому ждём в реальном времени через DevTools-протокол.

1. Временно положить `probe_page.js` в `proto/map/` и сделать копию `index.html` с
   `<script src="probe_page.js"></script>` после `app.js` (не коммитить и не выкладывать).
2. Запустить Edge: `msedge --headless=new --user-data-dir=<scratch>/edge --enable-unsafe-swiftshader
   --use-angle=swiftshader --window-size=1400,900 --remote-debugging-port=9333 about:blank`.
3. `node cdp_probe.mjs "http://localhost:8217/<test>.html?x=<lon>&y=<lat>&z=<zoom>#<journey>/<stop>" out.png`
   печатает отрисованные подписи остановок и городов и сохраняет снимок.
