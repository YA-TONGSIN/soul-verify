// Security checks (review 2026-10-29) against functions/[[path]].js with an in-memory DB, no browser or deploy.
// Usage: node human-grading-web/test_security.mjs     -> prints {"ok":true,...} or exits 1
import { pathToFileURL } from "node:url";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const { onRequest } = await import(pathToFileURL(join(here, "functions", "[[path]].js")).href);

const rows = [];
const DB = {
  prepare(sql) {
    const stmt = {
      args: [],
      bind(...a) { stmt.args = a; return stmt; },
      async run() {
        if (/INSERT INTO submissions /.test(sql)) { const [nick, seed, answers, complete, started_at, submitted_at] = stmt.args;
          rows.push({ id: rows.length + 1, nick, seed, answers, complete, started_at, submitted_at }); return { meta: { last_row_id: rows.length } }; }
        return { meta: {} };
      },
      async all() { return { results: /FROM submissions /.test(sql + " ") ? rows : [] }; },
    };
    return stmt;
  },
};
const env = { PATH_TOKEN: "tok123", ADMIN_TOKEN: "adm456", DB, ASSETS: { fetch: async () => new Response("<p>asset</p>", { headers: { "Content-Type": "text/html" } }) } };
const call = (path, init = {}) => onRequest({ request: new Request("https://x.test" + path, init), env });
const fail = (msg) => { console.log(JSON.stringify({ ok: false, error: msg })); process.exit(1); };

// 1. security headers on asset, API and 404 responses
for (const [name, r] of [["asset", await call("/tok123/")], ["404", await call("/nope")], ["api", await call("/tok123/api/export")]]) {
  const csp = r.headers.get("Content-Security-Policy") || "";
  if (!csp.includes("frame-ancestors 'none'") || !csp.includes("script-src 'self'")) fail(name + " CSP");
  if (r.headers.get("X-Frame-Options") !== "DENY" || r.headers.get("X-Content-Type-Options") !== "nosniff") fail(name + " frame/nosniff");
  if (r.headers.get("Referrer-Policy") !== "no-referrer") fail(name + " referrer");
}
// 2. declared oversize body is refused before reading
let r = await call("/tok123/api/submit", { method: "POST", headers: { "Content-Length": "999999" }, body: "{}" });
if (r.status !== 413) fail("content-length 413, got " + r.status);
r = await call("/tok123/l/api/submit", { method: "POST", body: "x".repeat(20001) });
if (r.status !== 413) fail("raw length 413");
// 3. CSV export neutralises spreadsheet formulas in free-text cells
r = await call("/tok123/api/submit", { method: "POST", body: JSON.stringify({ nick: "=HYPERLINK(1)", seed: "0a1b2c3d", startedAt: "@x", answers: { 1: { q1: "L" } } }) });
if (!(await r.json()).ok) fail("submit for csv");
const csv = await (await call("/tok123/api/export?format=csv", { headers: { Authorization: "Bearer adm456" } })).text();
const first = csv.split("\n")[1] || "";
if (!first.includes(",'=HYPERLINK(1),") || !first.includes(",'@x,")) fail("csv guard: " + first.slice(0, 80));
// 4. admin token: wrong / prefix / empty are 404
for (const k of ["adm45", "adm4567", "", "ADM456"]) if ((await call("/tok123/api/export?key=" + k)).status !== 404) fail("admin token accepted: len " + k.length);
console.log(JSON.stringify({ ok: true, checks: ["headers", "413", "csv", "admin"] }));
