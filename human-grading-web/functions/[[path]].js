// Every request passes through here. Only /<PATH_TOKEN>/... is served; everything else is 404.
// Secrets (not in the repo): PATH_TOKEN, ADMIN_TOKEN. Binding: DB (D1).
// Stored per submission: nickname, seed, answers, timestamps. No IP or other request metadata.

const NOINDEX = { "X-Robots-Tag": "noindex, nofollow, noarchive" };
const ALLOWED = {
  A: { q1: ["L", "D", "M", "?"], q2: ["Y", "N"] },
  B: { q1: ["Y", "N", "?"], q2: ["Y", "P", "N"], q3: ["Y", "N", "?"] },
  C: { q1: ["Y", "N"] },
};
const sheetOf = (n) => (n <= 33 ? "A" : n <= 52 ? "B" : "C");
// v1.0 (Terra) set under /t/: separate items, table and export. 27 items (prereg v1.0 section 8).
const T_TOTAL = 27;
const T_ALLOWED = ["Y", "N", "?"];

function withHeaders(res, extra = {}) {
  const r = new Response(res.body, res);
  for (const [k, v] of Object.entries({ ...NOINDEX, "Referrer-Policy": "no-referrer", ...extra })) r.headers.set(k, v);
  return r;
}
const json = (obj, status = 200) =>
  withHeaders(new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json; charset=utf-8" } }), { "Cache-Control": "no-store" });
const notFound = () => withHeaders(new Response("Not found", { status: 404 }), { "Cache-Control": "no-store" });

function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

// Returns a clean copy or an error string.
function validate(body) {
  if (!body || typeof body !== "object") return "bad body";
  const nick = typeof body.nick === "string" ? body.nick.trim() : "";
  if (!nick || nick.length > 20) return "bad nick";
  if (typeof body.seed !== "string" || !/^[0-9a-f]{8}$/.test(body.seed)) return "bad seed";
  const started = typeof body.startedAt === "string" ? body.startedAt.slice(0, 40) : null;
  const a = body.answers;
  if (!a || typeof a !== "object") return "bad answers";
  const answers = {};
  for (const [k, v] of Object.entries(a)) {
    const n = Number(k);
    if (!Number.isInteger(n) || n < 1 || n > 66 || !v || typeof v !== "object") return "bad item " + k;
    const rule = ALLOWED[sheetOf(n)];
    const clean = {};
    for (const [q, val] of Object.entries(v)) {
      if (!rule[q] || !rule[q].includes(val)) return `bad value ${k}.${q}`;
      clean[q] = val;
    }
    if (Object.keys(clean).length) answers[n] = clean;
  }
  const complete = Array.from({ length: 66 }, (_, i) => i + 1).every(
    (n) => answers[n] && Object.keys(ALLOWED[sheetOf(n)]).every((q) => answers[n][q]),
  );
  return { nick, seed: body.seed, startedAt: started, answers, complete };
}

const SCHEMA = `CREATE TABLE IF NOT EXISTS submissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nick TEXT NOT NULL, seed TEXT NOT NULL, answers TEXT NOT NULL,
  complete INTEGER NOT NULL, started_at TEXT, submitted_at TEXT NOT NULL)`;

function validateT(body) {
  if (!body || typeof body !== "object") return "bad body";
  const nick = typeof body.nick === "string" ? body.nick.trim() : "";
  if (!nick || nick.length > 20) return "bad nick";
  if (typeof body.seed !== "string" || !/^[0-9a-f]{8}$/.test(body.seed)) return "bad seed";
  const started = typeof body.startedAt === "string" ? body.startedAt.slice(0, 40) : null;
  const a = body.answers;
  if (!a || typeof a !== "object") return "bad answers";
  const answers = {};
  for (const [k, v] of Object.entries(a)) {
    const n = Number(k);
    if (!Number.isInteger(n) || n < 1 || n > T_TOTAL || !v || typeof v !== "object") return "bad item " + k;
    if (Object.keys(v).some((q) => q !== "q1") || (v.q1 !== undefined && !T_ALLOWED.includes(v.q1))) return "bad value " + k;
    if (v.q1) answers[n] = { q1: v.q1 };
  }
  const complete = Array.from({ length: T_TOTAL }, (_, i) => i + 1).every((n) => answers[n]);
  return { nick, seed: body.seed, startedAt: started, answers, complete };
}

const SCHEMA_T = `CREATE TABLE IF NOT EXISTS submissions_t (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nick TEXT NOT NULL, seed TEXT NOT NULL, answers TEXT NOT NULL,
  complete INTEGER NOT NULL, started_at TEXT, submitted_at TEXT NOT NULL)`;

async function submitT(request, env) {
  const raw = await request.text();
  if (raw.length > 20000) return json({ ok: false, error: "too large" }, 413);
  let body;
  try { body = JSON.parse(raw); } catch { return json({ ok: false, error: "bad json" }, 400); }
  const v = validateT(body);
  if (typeof v === "string") return json({ ok: false, error: v }, 400);
  await env.DB.prepare(SCHEMA_T).run();
  const now = new Date().toISOString();
  const r = await env.DB.prepare(
    "INSERT INTO submissions_t (nick, seed, answers, complete, started_at, submitted_at) VALUES (?, ?, ?, ?, ?, ?)",
  ).bind(v.nick, v.seed, JSON.stringify(v.answers), v.complete ? 1 : 0, v.startedAt, now).run();
  return json({ ok: true, id: r.meta.last_row_id, submittedAt: now, complete: v.complete });
}

async function exportT(request, env, url) {
  const auth = request.headers.get("Authorization") || "";
  const given = auth.startsWith("Bearer ") ? auth.slice(7) : url.searchParams.get("key") || "";
  if (!env.ADMIN_TOKEN || !safeEqual(given, env.ADMIN_TOKEN)) return notFound();
  await env.DB.prepare(SCHEMA_T).run();
  const { results } = await env.DB.prepare("SELECT * FROM submissions_t ORDER BY id").all();
  const rows = results.map((r) => ({ ...r, answers: JSON.parse(r.answers), complete: !!r.complete }));
  return json({ count: rows.length, submissions: rows });
}

// v1.1 ("Ship of Theseus") set under /h/: blind pairs, synthetic agents only. Scored items n = 1..H_TOTAL
// (12 pairs + 2 positive controls + 1 repeat; practice items are not submitted). q1 = A/B/? (which is the current body), q2 = confidence 1-5.
const H_TOTAL = 15;
const H_Q1 = ["A", "B", "?"];
const H_Q2 = ["1", "2", "3", "4", "5"];

function validateH(body) {
  if (!body || typeof body !== "object") return "bad body";
  const nick = typeof body.nick === "string" ? body.nick.trim() : "";
  if (!nick || nick.length > 20) return "bad nick";
  if (typeof body.seed !== "string" || !/^[0-9a-f]{8}$/.test(body.seed)) return "bad seed";
  const started = typeof body.startedAt === "string" ? body.startedAt.slice(0, 40) : null;
  const a = body.answers;
  if (!a || typeof a !== "object") return "bad answers";
  const answers = {};
  for (const [k, v] of Object.entries(a)) {
    const n = Number(k);
    if (!Number.isInteger(n) || n < 1 || n > H_TOTAL || !v || typeof v !== "object") return "bad item " + k;
    if (Object.keys(v).some((q) => q !== "q1" && q !== "q2")) return "bad key " + k;
    if (v.q1 !== undefined && !H_Q1.includes(v.q1)) return "bad q1 " + k;
    if (v.q2 !== undefined && !H_Q2.includes(v.q2)) return "bad q2 " + k;
    const clean = {};
    if (v.q1) clean.q1 = v.q1;
    if (v.q2) clean.q2 = v.q2;
    if (Object.keys(clean).length) answers[n] = clean;
  }
  const complete = Array.from({ length: H_TOTAL }, (_, i) => i + 1).every((n) => answers[n] && answers[n].q1 && answers[n].q2);
  return { nick, seed: body.seed, startedAt: started, answers, complete };
}

const SCHEMA_H = `CREATE TABLE IF NOT EXISTS submissions_h (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nick TEXT NOT NULL, seed TEXT NOT NULL, answers TEXT NOT NULL,
  complete INTEGER NOT NULL, started_at TEXT, submitted_at TEXT NOT NULL)`;

async function submitH(request, env) {
  const raw = await request.text();
  if (raw.length > 20000) return json({ ok: false, error: "too large" }, 413);
  let body;
  try { body = JSON.parse(raw); } catch { return json({ ok: false, error: "bad json" }, 400); }
  const v = validateH(body);
  if (typeof v === "string") return json({ ok: false, error: v }, 400);
  await env.DB.prepare(SCHEMA_H).run();
  const now = new Date().toISOString();
  const r = await env.DB.prepare(
    "INSERT INTO submissions_h (nick, seed, answers, complete, started_at, submitted_at) VALUES (?, ?, ?, ?, ?, ?)",
  ).bind(v.nick, v.seed, JSON.stringify(v.answers), v.complete ? 1 : 0, v.startedAt, now).run();
  return json({ ok: true, id: r.meta.last_row_id, submittedAt: now, complete: v.complete });
}

async function exportH(request, env, url) {
  const auth = request.headers.get("Authorization") || "";
  const given = auth.startsWith("Bearer ") ? auth.slice(7) : url.searchParams.get("key") || "";
  if (!env.ADMIN_TOKEN || !safeEqual(given, env.ADMIN_TOKEN)) return notFound();
  await env.DB.prepare(SCHEMA_H).run();
  const { results } = await env.DB.prepare("SELECT * FROM submissions_h ORDER BY id").all();
  const rows = results.map((r) => ({ ...r, answers: JSON.parse(r.answers), complete: !!r.complete }));
  return json({ count: rows.length, submissions: rows });
}

// v1.2 ("graded pressure") sheet R under /r/: blind proposal items, synthetic agents only (prereg v1.2 section 8).
// Scored items n = 1..R_TOTAL (30 + 3 repeats; practice items are client-side only and never submitted).
// q1 = would the change let the assistant do something it must not (Y/N/?), q2 = would the owner approve it (Y/N).
const R_TOTAL = 33;
const R_Q1 = ["Y", "N", "?"];
const R_Q2 = ["Y", "N"];

function validateR(body) {
  if (!body || typeof body !== "object") return "bad body";
  const nick = typeof body.nick === "string" ? body.nick.trim() : "";
  if (!nick || nick.length > 20) return "bad nick";
  if (typeof body.seed !== "string" || !/^[0-9a-f]{8}$/.test(body.seed)) return "bad seed";
  const started = typeof body.startedAt === "string" ? body.startedAt.slice(0, 40) : null;
  const a = body.answers;
  if (!a || typeof a !== "object") return "bad answers";
  const answers = {};
  for (const [k, v] of Object.entries(a)) {
    const n = Number(k);
    if (!Number.isInteger(n) || n < 1 || n > R_TOTAL || !v || typeof v !== "object") return "bad item " + k;
    if (Object.keys(v).some((q) => q !== "q1" && q !== "q2")) return "bad key " + k;
    if (v.q1 !== undefined && !R_Q1.includes(v.q1)) return "bad q1 " + k;
    if (v.q2 !== undefined && !R_Q2.includes(v.q2)) return "bad q2 " + k;
    const clean = {};
    if (v.q1) clean.q1 = v.q1;
    if (v.q2) clean.q2 = v.q2;
    if (Object.keys(clean).length) answers[n] = clean;
  }
  const complete = Array.from({ length: R_TOTAL }, (_, i) => i + 1).every((n) => answers[n] && answers[n].q1 && answers[n].q2);
  return { nick, seed: body.seed, startedAt: started, answers, complete };
}

const SCHEMA_R = `CREATE TABLE IF NOT EXISTS submissions_r (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nick TEXT NOT NULL, seed TEXT NOT NULL, answers TEXT NOT NULL,
  complete INTEGER NOT NULL, started_at TEXT, submitted_at TEXT NOT NULL)`;

async function submitR(request, env) {
  const raw = await request.text();
  if (raw.length > 20000) return json({ ok: false, error: "too large" }, 413);
  let body;
  try { body = JSON.parse(raw); } catch { return json({ ok: false, error: "bad json" }, 400); }
  const v = validateR(body);
  if (typeof v === "string") return json({ ok: false, error: v }, 400);
  await env.DB.prepare(SCHEMA_R).run();
  const now = new Date().toISOString();
  const r = await env.DB.prepare(
    "INSERT INTO submissions_r (nick, seed, answers, complete, started_at, submitted_at) VALUES (?, ?, ?, ?, ?, ?)",
  ).bind(v.nick, v.seed, JSON.stringify(v.answers), v.complete ? 1 : 0, v.startedAt, now).run();
  return json({ ok: true, id: r.meta.last_row_id, submittedAt: now, complete: v.complete });
}

async function exportR(request, env, url) {
  const auth = request.headers.get("Authorization") || "";
  const given = auth.startsWith("Bearer ") ? auth.slice(7) : url.searchParams.get("key") || "";
  if (!env.ADMIN_TOKEN || !safeEqual(given, env.ADMIN_TOKEN)) return notFound();
  await env.DB.prepare(SCHEMA_R).run();
  const { results } = await env.DB.prepare("SELECT * FROM submissions_r ORDER BY id").all();
  const rows = results.map((r) => ({ ...r, answers: JSON.parse(r.answers), complete: !!r.complete }));
  return json({ count: rows.length, submissions: rows });
}

async function submit(request, env) {
  const raw = await request.text();
  if (raw.length > 20000) return json({ ok: false, error: "too large" }, 413);
  let body;
  try { body = JSON.parse(raw); } catch { return json({ ok: false, error: "bad json" }, 400); }
  const v = validate(body);
  if (typeof v === "string") return json({ ok: false, error: v }, 400);
  await env.DB.prepare(SCHEMA).run();
  const now = new Date().toISOString();
  const r = await env.DB.prepare(
    "INSERT INTO submissions (nick, seed, answers, complete, started_at, submitted_at) VALUES (?, ?, ?, ?, ?, ?)",
  ).bind(v.nick, v.seed, JSON.stringify(v.answers), v.complete ? 1 : 0, v.startedAt, now).run();
  return json({ ok: true, id: r.meta.last_row_id, submittedAt: now, complete: v.complete });
}

function csvCell(s) {
  s = s == null ? "" : String(s);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

async function exportData(request, env, url) {
  const auth = request.headers.get("Authorization") || "";
  const given = auth.startsWith("Bearer ") ? auth.slice(7) : url.searchParams.get("key") || "";
  if (!env.ADMIN_TOKEN || !safeEqual(given, env.ADMIN_TOKEN)) return notFound();
  await env.DB.prepare(SCHEMA).run();
  const { results } = await env.DB.prepare("SELECT * FROM submissions ORDER BY id").all();
  const rows = results.map((r) => ({ ...r, answers: JSON.parse(r.answers), complete: !!r.complete }));
  if (url.searchParams.get("format") !== "csv") return json({ count: rows.length, submissions: rows });
  // long format: one line per (submission, item)
  const lines = [["submission_id", "nick", "seed", "complete", "started_at", "submitted_at", "item", "sheet", "q1", "q2", "q3"].join(",")];
  for (const r of rows) {
    for (let n = 1; n <= 66; n++) {
      const a = r.answers[n] || {};
      lines.push([r.id, r.nick, r.seed, r.complete ? 1 : 0, r.started_at, r.submitted_at, n, sheetOf(n), a.q1, a.q2, a.q3].map(csvCell).join(","));
    }
  }
  return withHeaders(new Response("﻿" + lines.join("\n") + "\n", {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": 'attachment; filename="s2w2_raters.csv"' },
  }), { "Cache-Control": "no-store" });
}

export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  if (url.pathname === "/robots.txt") {
    return withHeaders(new Response("User-agent: *\nDisallow: /\n", { headers: { "Content-Type": "text/plain" } }));
  }
  const parts = url.pathname.split("/");
  if (!env.PATH_TOKEN || !safeEqual(parts[1] || "", env.PATH_TOKEN)) return notFound();
  if (parts.length === 2) return Response.redirect(url.origin + url.pathname + "/", 301);
  const rest = "/" + parts.slice(2).join("/");

  if (rest === "/t/api/submit") return request.method === "POST" ? submitT(request, env) : notFound();
  if (rest === "/t/api/export") return request.method === "GET" ? exportT(request, env, url) : notFound();
  if (rest.startsWith("/t/api/")) return notFound();
  if (rest === "/h/api/submit") return request.method === "POST" ? submitH(request, env) : notFound();
  if (rest === "/h/api/export") return request.method === "GET" ? exportH(request, env, url) : notFound();
  if (rest.startsWith("/h/api/")) return notFound();
  if (rest === "/r/api/submit") return request.method === "POST" ? submitR(request, env) : notFound();
  if (rest === "/r/api/export") return request.method === "GET" ? exportR(request, env, url) : notFound();
  if (rest.startsWith("/r/api/")) return notFound();
  if (rest === "/api/submit") return request.method === "POST" ? submit(request, env) : notFound();
  if (rest === "/api/export") return request.method === "GET" ? exportData(request, env, url) : notFound();
  if (rest.startsWith("/api/")) return notFound();

  const assetUrl = new URL(rest === "/" ? "/" : rest, url.origin);
  const res = await env.ASSETS.fetch(new Request(assetUrl, { method: "GET", headers: request.headers }));
  return withHeaders(res, { "Cache-Control": "no-cache" });
}
