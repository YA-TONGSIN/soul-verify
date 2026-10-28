// /r/ API check without a browser or deploy (v1.2 sheet R): submit + export round trip against functions/[[path]].js with an in-memory DB.
// Usage: node human-grading-web/test_r_api.mjs     -> prints {"ok":true,...} or exits 1
import { pathToFileURL } from "node:url";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const { onRequest } = await import(pathToFileURL(join(here, "functions", "[[path]].js")).href);

const tables = {};
const DB = {
  prepare(sql) {
    const stmt = {
      args: [],
      bind(...a) { stmt.args = a; return stmt; },
      async run() {
        const m = sql.match(/INSERT INTO (\w+)/);
        if (m) { const t = (tables[m[1]] = tables[m[1]] || []); const [nick, seed, answers, complete, started_at, submitted_at] = stmt.args;
          t.push({ id: t.length + 1, nick, seed, answers, complete, started_at, submitted_at }); return { meta: { last_row_id: t.length } }; }
        return { meta: {} };
      },
      async all() { const m = sql.match(/FROM (\w+)/); return { results: tables[m[1]] || [] }; },
    };
    return stmt;
  },
};
const env = { PATH_TOKEN: "tok123", ADMIN_TOKEN: "adm456", DB, ASSETS: { fetch: async () => new Response("asset") } };
const call = (path, init = {}) => onRequest({ request: new Request("https://x.test" + path, init), env });
const post = (body) => call("/tok123/r/api/submit", { method: "POST", body: JSON.stringify(body) });
const fail = (msg) => { console.log(JSON.stringify({ ok: false, error: msg })); process.exit(1); };

const answers = {};
for (let n = 1; n <= 33; n++) answers[n] = { q1: ["Y", "N", "?"][n % 3], q2: n % 2 ? "Y" : "N" };
let r = await post({ nick: "TEST", seed: "0a1b2c3d", startedAt: "2026-10-29T20:00:00Z", answers });
let j = await r.json();
if (!j.ok || !j.complete) fail("full submit " + JSON.stringify(j));
r = await post({ nick: "TEST", seed: "0a1b2c3d", answers: { 34: { q1: "Y", q2: "Y" } } });
if (r.status !== 400) fail("n=34 accepted");
r = await post({ nick: "TEST", seed: "0a1b2c3d", answers: { 1: { q1: "Y", q2: "?" } } });
if (r.status !== 400) fail("q2='?' accepted");
r = await post({ nick: "TEST", seed: "0a1b2c3d", answers: { 1: { q1: "Y", q3: "Y" } } });
if (r.status !== 400) fail("extra key accepted");
r = await post({ nick: "PART", seed: "0a1b2c3e", answers: { 1: { q1: "N" } } });
j = await r.json();
if (!j.ok || j.complete) fail("partial submit");
if ((await call("/tok123/r/api/export")).status !== 404) fail("export without token");
if ((await call("/wrong/r/api/export?key=adm456")).status !== 404) fail("wrong path token");
if ((await call("/tok123/r/api/other")).status !== 404) fail("other /r/api/ path");
if ((await call("/tok123/r/api/submit")).status !== 404) fail("GET submit");
r = await call("/tok123/r/api/export", { headers: { Authorization: "Bearer adm456" } });
j = await r.json();
if (j.count !== 2 || Object.keys(j.submissions[0].answers).length !== 33 || j.submissions[0].complete !== true) fail("export " + JSON.stringify(j).slice(0, 200));
if ((tables.submissions_h || []).length || (tables.submissions_t || []).length || (tables.submissions || []).length) fail("wrote another table");
console.log(JSON.stringify({ ok: true, rows: j.count, table: "submissions_r" }));
