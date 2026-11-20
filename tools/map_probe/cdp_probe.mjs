import fs from 'fs';
const [url, out] = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));
let t; for (let i = 0; i < 30 && !t; i++) { try { t = (await (await fetch('http://127.0.0.1:9333/json')).json()).find(x => x.type === 'page'); } catch { await sleep(500); } }
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = {};
ws.onmessage = m => { const d = JSON.parse(m.data); if (pend[d.id]) { pend[d.id](d.result); delete pend[d.id]; } };
const send = (method, params = {}) => new Promise(r => { pend[++id] = r; ws.send(JSON.stringify({id, method, params})); });
await send('Page.navigate', {url}); await sleep(30000);
const r = await send('Runtime.evaluate', {expression: "document.getElementById('out')?.textContent || 'no out'"});
console.log(r.result.value);
const shot = await send('Page.captureScreenshot', {format: 'png'}); fs.writeFileSync(out, Buffer.from(shot.data, 'base64'));
process.exit(0);
