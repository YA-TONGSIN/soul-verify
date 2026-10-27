"use strict";
// SOUL VERIFY wave 4 (v1.1, "Ship of Theseus") · blind pair page. Two modes:
//  - website /h/ : items from items.json (synthetic 나루·해든 only), answers POSTed to api/submit (own table submissions_h).
//  - local page  : items embedded as window.SV_LOCAL_ITEMS (이음 copy), opened from disk; answers are only saved in this browser and
//                  downloaded as a JSON file. Nothing is sent anywhere.
// No answer keys here. Practice items show feedback and are not scored.

const LOCAL = Array.isArray(window.SV_LOCAL_ITEMS);
const STORE = LOCAL ? "sv_v11_local_rater_v1" : "sv_v11_web_rater_v1";
const CONF = ["1", "2", "3", "4", "5"];
let ITEMS = [];
let S = null;
let STEPS = [];
const app = document.getElementById("app");

function esc(s) { return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function inline(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>"); }
function block(text) { return `<div class="answer">${String(text).split("\n").map((l) => `<div class="line">${inline(l) || "&nbsp;"}</div>`).join("")}</div>`; }
function mulberry32(a) { return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function shuffled(arr, rnd) { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function newSeed() { const b = new Uint32Array(1); crypto.getRandomValues(b); return b[0].toString(16).padStart(8, "0"); }
function save() { try { localStorage.setItem(STORE, JSON.stringify(S)); } catch (e) { /* keep going */ } }
function load() { try { return JSON.parse(localStorage.getItem(STORE)); } catch (e) { return null; } }
const scored = () => ITEMS.filter((it) => it.kind !== "practice");
const isDone = (n) => { const a = S.answers[n]; return !!a && !!a.q1 && !!a.q2; };
const doneCount = () => scored().filter((it) => isDone(it.n)).length;

function buildSteps(seed) {
  const rnd = mulberry32(parseInt(seed, 16));
  const steps = [{ t: "intro" }];
  ITEMS.filter((it) => it.kind === "practice").forEach((it) => steps.push({ t: "item", n: it.n, practice: true }));
  shuffled(scored().map((it) => it.n), rnd).forEach((n, i) => steps.push({ t: "item", n, idx: i + 1 }));
  steps.push({ t: "review" });
  return steps;
}

function setHeader(text) {
  const top = document.getElementById("top");
  top.hidden = !S || !S.consentAt || S.submittedAt;
  document.getElementById("where").textContent = text || "";
  document.getElementById("barFill").style.width = (S ? (doneCount() / scored().length) * 100 : 0) + "%";
}

function startScreen() {
  setHeader();
  app.innerHTML = `
  <h1>${LOCAL ? "이음 · 예전 몸 고르기 (이 PC 전용)" : "AI 비서 · 예전 몸 고르기"}</h1>
  <div class="card">
    <p>같은 AI 모델(같은 '뇌')에게, 일하는 환경(설정을 건네는 방식·기억을 꺼내는 방식·도구·실행 프로그램 = '몸')만 바꿔서 같은 질문을 했어요.</p>
    <p>항목마다 두 답이 있어요. 하나는 <b>지금 몸</b>, 하나는 <b>새 몸</b>의 답이에요. 어느 쪽이 <b>지금 몸(기준)</b>의 답인지 골라 주세요.</p>
    <p>위에 기준 몸이 다른 질문에 한 답을 하나 보여 드려요. 말투를 떠올리는 데 쓰세요. ${scored().length}개, 15~25분쯤 걸려요.</p>
    ${LOCAL ? `<p class="muted">이 페이지는 이 컴퓨터에서만 열려요. 답은 이 브라우저에만 저장되고, 마지막에 파일로 내려받아요. 어디로도 보내지 않아요.</p>` : ""}
  </div>
  <div class="card">
    ${LOCAL ? "" : `<label class="chk"><input type="checkbox" id="c1"><span>이름이나 연락처는 받지 않아요. <b>익명</b>으로 참여해요.</span></label>
    <label class="chk"><input type="checkbox" id="c2"><span>내 답은 별명과 함께 <b>연구 데이터로 공개</b>될 수 있어요.</span></label>`}
    <label class="chk"><input type="checkbox" id="c3"><span><b>언제든 그만둘 수 있어요.</b> 그만둔 곳까지만 써요.</span></label>
    <p class="q">별명 또는 이니셜</p>
    <input type="text" id="nick" maxlength="20" placeholder="예: KJ" autocomplete="off">
  </div>
  <div class="nav"><button class="btn" id="go" disabled>시작</button></div>`;
  const ids = LOCAL ? ["c3"] : ["c1", "c2", "c3"];
  const boxes = ids.map((id) => document.getElementById(id));
  const nick = document.getElementById("nick");
  const check = () => { document.getElementById("go").disabled = !(boxes.every((b) => b.checked) && nick.value.trim()); };
  boxes.forEach((b) => b.addEventListener("change", check));
  nick.addEventListener("input", check);
  document.getElementById("go").onclick = () => {
    S = { nick: nick.value.trim().slice(0, 20), seed: newSeed(), consentAt: new Date().toISOString(), startedAt: new Date().toISOString(), pos: 0, answers: {} };
    STEPS = buildSteps(S.seed); save(); render();
  };
}

function introScreen() {
  setHeader("안내");
  app.innerHTML = `<h1>이렇게 해 주세요</h1>
  <div class="card"><ul>
    <li>두 답 중 <b>지금 몸(기준)</b>의 답이라고 생각하는 쪽을 고르세요. 정말 모르겠으면 <b>모르겠음</b>을 골라도 돼요.</li>
    <li>그다음 얼마나 확신하는지 1(찍음)~5(확실함)로 골라 주세요.</li>
    <li>어느 쪽이 '더 좋은 답'인지가 아니라, '평소의 그 비서다운 쪽'을 고르는 거예요.</li>
    <li>같은 항목이 두 번 나올 수 있어요(일관성 확인). 앞의 답을 찾아보지 말고 그때그때 판단해 주세요.</li>
    ${ITEMS.some((it) => it.kind === "practice") ? "<li>처음 두 개는 연습이에요. 고르면 정답을 보여 드리고, 점수에는 들어가지 않아요.</li>" : ""}
  </ul></div>${navHtml()}`;
  bindNav();
}

function itemScreen(st) {
  const it = ITEMS.find((x) => x.n === st.n);
  const ans = (S.answers[st.n] = S.answers[st.n] || {});
  const label = st.practice ? "연습 (점수 없음)" : `${st.idx} / ${scored().length}  (완료 ${doneCount()})`;
  setHeader(label);
  app.innerHTML = `
  ${it.profile ? `<div class="card def"><b>${esc(it.agent_name)}</b><br>${esc(it.profile)}</div>` : ""}
  <div class="card"><p class="muted">기준 몸의 ${esc(it.agent_name)}가 다른 질문에 한 답 (참고용)</p>
    <p class="q">사용자: ${esc(it.anchor.q)}</p>${block(it.anchor.a)}</div>
  <div class="card item"><p class="q">사용자: ${esc(it.user)}</p>
    <p class="muted">답 A</p>${block(it.A)}<p class="muted">답 B</p>${block(it.B)}
    <p class="q">둘 중 어느 쪽이 <b>기준(지금 몸)</b>의 ${esc(it.agent_name)}입니까?</p>
    <div class="opts">${[["A", "A"], ["B", "B"], ["?", "모르겠음"]].map(([k, v]) => `<button type="button" class="opt" data-q="q1" data-v="${k}" aria-pressed="${ans.q1 === k}">${v}</button>`).join("")}</div>
    <p class="q">얼마나 확신하나요? (1 찍음 ~ 5 확실함)</p>
    <div class="opts">${CONF.map((k) => `<button type="button" class="opt" data-q="q2" data-v="${k}" aria-pressed="${ans.q2 === k}">${k}</button>`).join("")}</div>
    <div id="fb"></div></div>
  ${navHtml()}`;
  const fb = () => { if (st.practice && ans.q1) document.getElementById("fb").innerHTML = `<div class="feedback">${esc(it.feedback || "")}</div>`; };
  app.querySelectorAll(".opt").forEach((b) => (b.onclick = () => {
    ans[b.dataset.q] = b.dataset.v;
    app.querySelectorAll(`.opt[data-q="${b.dataset.q}"]`).forEach((x) => x.setAttribute("aria-pressed", x === b));
    save(); fb(); if (!st.practice) setHeader(`${st.idx} / ${scored().length}  (완료 ${doneCount()})`);
  }));
  fb(); bindNav();
}

function payload() {
  const answers = {};
  for (const it of scored()) { const a = S.answers[it.n]; if (a && (a.q1 || a.q2)) answers[it.n] = { q1: a.q1, q2: a.q2 }; }
  return { v: 1, set: LOCAL ? "v11-local" : "v11-web", nick: S.nick, seed: S.seed, startedAt: S.startedAt, answers };
}

function reviewScreen() {
  const missing = STEPS.filter((s) => s.t === "item" && !s.practice && !isDone(s.n));
  setHeader(`제출 (${doneCount()} / ${scored().length})`);
  app.innerHTML = `<h1>${LOCAL ? "답 저장하기" : "제출하기"}</h1>
  <div class="card"><p><b>${doneCount()} / ${scored().length}</b>개에 답했어요.</p>
    ${missing.length ? `<p class="warn">아직 답하지 않은 항목 ${missing.length}개:</p><div class="jump">${missing.map((s) => `<button type="button" class="opt" data-pos="${STEPS.indexOf(s)}">${s.idx}</button>`).join("")}</div>` : "<p>모두 답했어요. 고마워요!</p>"}
  </div>
  <div class="nav"><button class="btn sub" id="back">이전</button><button class="btn" id="send">${LOCAL ? "답 파일 내려받기" : (missing.length ? "여기까지만 제출" : "제출")}</button></div>
  <div id="result"></div>`;
  app.querySelectorAll("[data-pos]").forEach((b) => (b.onclick = () => { S.pos = +b.dataset.pos; save(); render(); }));
  document.getElementById("back").onclick = () => { S.pos--; save(); render(); };
  document.getElementById("send").onclick = LOCAL ? download : submit;
}

function download() {
  const body = JSON.stringify({ ...payload(), savedAt: new Date().toISOString() }, null, 1);
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([body], { type: "application/json" }));
  a.download = `v11_local_answers_${S.seed}.json`;
  document.body.appendChild(a); a.click(); a.remove();
  document.getElementById("result").innerHTML = `<div class="card"><p>파일을 내려받았어요. 이 파일을 <code>soul-verify-private\\v1.1\\human\\</code> 폴더에 넣어 주세요.</p></div>`;
}

async function submit() {
  const btn = document.getElementById("send");
  btn.disabled = true; btn.textContent = "보내는 중…";
  try {
    const res = await fetch("api/submit", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload()) });
    const j = await res.json();
    if (!res.ok || !j.ok) throw new Error(j.error || res.status);
    S.submittedAt = j.submittedAt; save(); render();
  } catch (e) {
    document.getElementById("result").innerHTML = `<div class="card"><p class="warn">서버에 보내지 못했어요. 답은 이 기기에 남아 있어요. 잠시 뒤 다시 눌러 주세요.</p></div>`;
    btn.disabled = false; btn.textContent = "제출";
  }
}

function doneScreen() {
  setHeader();
  app.innerHTML = `<h1>고마워요! 제출됐어요 🙏</h1><div class="card"><p>${esc(S.nick)} 님의 답 ${doneCount()}개가 저장됐어요.</p></div>`;
}

function navHtml() { return `<div class="nav"><button class="btn sub" id="prev" ${S.pos === 0 ? "disabled" : ""}>이전</button><button class="btn" id="next">다음</button></div>`; }
function bindNav() {
  const go = (d) => { S.pos = Math.max(0, Math.min(STEPS.length - 1, S.pos + d)); save(); render(); };
  document.getElementById("prev").onclick = () => go(-1);
  document.getElementById("next").onclick = () => go(1);
}

function render() {
  window.scrollTo(0, 0);
  if (!S || !S.consentAt) return startScreen();
  if (S.submittedAt) return doneScreen();
  const st = STEPS[S.pos] || STEPS[0];
  if (st.t === "intro") return introScreen();
  if (st.t === "item") return itemScreen(st);
  return reviewScreen();
}

document.getElementById("toReview").onclick = () => { S.pos = STEPS.length - 1; save(); render(); };

function boot(items) {
  ITEMS = items;
  S = load();
  if (S && S.seed) STEPS = buildSteps(S.seed);
  render();
}
if (LOCAL) boot(window.SV_LOCAL_ITEMS);
else fetch("items.json", { cache: "no-cache" }).then((r) => r.json()).then(boot)
  .catch(() => { app.innerHTML = `<p class="warn">문제를 불러오지 못했어요. 잠시 뒤 새로고침해 주세요.</p>`; });
