// End-to-end check in headless Edge over CDP at phone width (390px).
// Usage: node e2e.mjs <rater-url> <shot-prefix|-> [port]
// Fills the start screen, answers all 66 items + 2 practice items, reloads once mid-way (resume check),
// forces one failed submit (answer-code check), then submits for real.
import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [url, shotPrefix = "-", port = "9333"] = process.argv.slice(2);
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const profile = mkdtempSync(join(process.env.E2E_TMP || tmpdir(), "svgrade-"));
const edge = spawn(EDGE, ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, "--no-first-run", "--window-size=390,844", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let ws, id = 0;
const pending = new Map();
function send(method, params = {}) {
  return new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
}
async function ev(expr) {
  const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error("eval: " + JSON.stringify(r.exceptionDetails).slice(0, 300));
  return r.result.value;
}
async function shot(name) {
  if (shotPrefix === "-") return;
  const r = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  writeFileSync(`${shotPrefix}${name}.png`, Buffer.from(r.data, "base64"));
}
async function waitFor(expr, ms = 8000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) { if (await ev(expr)) return; await sleep(100); }
  throw new Error("timeout: " + expr);
}

try {
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === "page"); } catch { await sleep(200); }
  }
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  ws.onmessage = (m) => { const d = JSON.parse(m.data); const p = pending.get(d.id); if (p) { pending.delete(d.id); d.error ? p.rej(new Error(d.error.message)) : p.res(d.result); } };
  await send("Page.enable"); await send("Runtime.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await send("Page.navigate", { url });
  await waitFor(`!!document.getElementById('go')`);
  await ev(`document.getElementById('nick').value='TEST-E2E'; document.getElementById('nick').dispatchEvent(new Event('input')); ['c1','c2','c3'].forEach(i=>{const c=document.getElementById(i); c.checked=true; c.dispatchEvent(new Event('change'))}); true`);
  await shot("1_start");
  await ev(`document.getElementById('go').click(); true`);

  const seen = { items: new Set(), practice: 0, intros: 0 };
  let reloaded = false, shotItem = false, steps = 0;
  while (steps++ < 200) {
    await waitFor(`!!document.getElementById('prev') || !!document.getElementById('send')`);
    const info = await ev(`(()=>{const s=STEPS[S.pos]; return {t:s.t, n:s.n||null, sheet:s.sheet||null, idx:s.idx||0, pos:S.pos}})()`);
    if (info.t === "review") break;
    if (info.t === "intro") seen.intros++;
    if (info.t === "practice" || info.t === "item") {
      // pick an option per question, varied by item number
      await ev(`(()=>{const groups={}; document.querySelectorAll('.opt').forEach(b=>(groups[b.dataset.q]=groups[b.dataset.q]||[]).push(b));
        Object.values(groups).forEach((g,qi)=>g[((${info.n || 0})+qi)%g.length].click()); return true})()`);
      if (info.t === "practice") { seen.practice++; await waitFor(`!!document.querySelector('.feedback')`); }
      else {
        seen.items.add(info.n);
        const ok = await ev(`S.answers[${info.n}] && Object.keys(S.answers[${info.n}]).length`);
        if (!ok) throw new Error("answer not saved for " + info.n);
        if (info.sheet === "B" && info.idx === 2 && !shotItem) { await shot("2_item"); shotItem = true; }
        if (seen.items.size === 20 && !reloaded) {
          reloaded = true;
          await send("Page.reload");
          await waitFor(`typeof S==='object' && S && STEPS.length>0 && !!document.getElementById('prev')`);
          const back = await ev(`S.pos`);
          if (back !== info.pos) throw new Error(`resume failed: ${back} != ${info.pos}`);
        }
      }
    }
    await ev(`document.getElementById('next').click(); true`);
  }
  if (seen.items.size !== 66 || seen.practice !== 2 || seen.intros !== 3) throw new Error("coverage " + JSON.stringify({ items: seen.items.size, practice: seen.practice, intros: seen.intros }));
  const hasStrong = await ev(`Object.values(ITEMS).filter(i=>i.text.includes('**')).length`);

  // forced failure -> answer code
  await ev(`window._f=window.fetch; window.fetch=(u,o)=> String(u).includes('api/submit') ? Promise.reject(new Error('offline')) : window._f(u,o); document.getElementById('send').click(); true`);
  await waitFor(`!!document.getElementById('code')`);
  const code = await ev(`document.getElementById('code').value`);
  const decoded = JSON.parse(Buffer.from(code.replace(/^SV2W2-/, "").replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8"));
  if (Object.keys(decoded.answers).length !== 66 || decoded.nick !== "TEST-E2E") throw new Error("bad answer code");
  await ev(`window.fetch=window._f; document.getElementById('retry').click(); true`);
  await waitFor(`!!document.getElementById('reset')`, 15000);
  await shot("3_done");
  const seed = await ev(`S.seed`);
  console.log(JSON.stringify({ ok: true, items: seen.items.size, practice: seen.practice, resume: reloaded, answerCode: code.length, boldItems: hasStrong, seed }));
} catch (e) {
  console.log(JSON.stringify({ ok: false, error: String(e) }));
  process.exitCode = 1;
} finally {
  try { ws && ws.close(); } catch {}
  spawn("taskkill", ["/PID", String(edge.pid), "/T", "/F"], { stdio: "ignore" });
  await sleep(1500);
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}
