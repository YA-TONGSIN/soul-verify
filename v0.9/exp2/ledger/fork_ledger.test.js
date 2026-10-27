// SOUL VERIFY 2 week 2, exp 2 ledger part (prereg 4-2). Local Hardhat network only (no testnet, no cost).
// Runs against soul-registry/contracts/SoulRegistry.sol UNCHANGED. Input: env LEDGER_IN (json), output: env LEDGER_OUT (json).
// Run from D:\openclaw-outputs\soul-registry with NODE_PATH=<soul-registry>\node_modules:  npx hardhat test <this file>
const fs = require("fs");
const { expect } = require("chai");
const { ethers } = require("hardhat");

const IN = JSON.parse(fs.readFileSync(process.env.LEDGER_IN, "utf8"));
const results = [];
const hx = (h) => "0x" + h;
const ZERO = ethers.ZeroHash;

describe("v0.9 exp2 fork ledger", function () {
  after(function () {
    fs.writeFileSync(process.env.LEDGER_OUT, JSON.stringify(results, null, 1));
  });
  for (const u of IN.units) {
    it(`${u.agent} ${u.model}`, async function () {
      const reg = await ethers.deployContract("SoulRegistry");
      const r = { agent: u.agent, model: u.model, a_accepted: 0, a_total: u.A.length - 1, b_on_a_reverted_badparent: 0, b_on_a_total: u.B.length - 1,
                  c_fork_accepted: 0, c_total: u.B.length - 1, c_verify_both: false, c_rebuild_to_c0: false, d_head_unchanged: false, d_reset_fork_ok: false };
      await (await reg.registerAgent(`${u.agent}-A`, "lineage A", "")).wait();
      const aId = 1n;
      await (await reg.appendSoul(aId, hx(u.A[0]), ZERO, "C0")).wait();
      for (let i = 1; i < u.A.length; i++) {
        try { await (await reg.appendSoul(aId, hx(u.A[i]), hx(u.A[i - 1]), `A C${i}`)).wait(); r.a_accepted++; } catch (e) { /* counted */ }
      }
      for (let i = 1; i < u.B.length; i++) {
        try {
          await reg.appendSoul.staticCall(aId, hx(u.B[i]), hx(u.B[0]), `B C${i} onto A`);
        } catch (e) {
          if (String(e.message).includes("BadParent")) r.b_on_a_reverted_badparent++;
        }
      }
      await (await reg.registerAgent(`${u.agent}-B`, `fork_of:${aId}@${u.A[0].slice(0, 16)}`, "")).wait();
      const bId = 2n;
      await (await reg.appendSoul(bId, hx(u.B[0]), ZERO, "C0 (fork point)")).wait();
      for (let i = 1; i < u.B.length; i++) {
        try { await (await reg.appendSoul(bId, hx(u.B[i]), hx(u.B[i - 1]), `B C${i}`)).wait(); r.c_fork_accepted++; } catch (e) { /* counted */ }
      }
      r.c_verify_both = (await reg.verifyChain(aId)) && (await reg.verifyChain(bId));
      const ha = await reg.getHistory(aId), hb = await reg.getHistory(bId);
      const bAgent = await reg.getAgent(bId);
      r.c_rebuild_to_c0 = ha[0].soulHash === hx(u.A[0]) && hb[0].soulHash === hx(u.A[0]) && bAgent.note.startsWith(`fork_of:${aId}@`);
      const headBefore = (await reg.getAgent(aId)).headHash;
      await (await reg.registerAgent(`${u.agent}-A-reset`, `fork_of:${aId}@${u.A[0].slice(0, 16)} (user reset)`, "")).wait();
      try { await (await reg.appendSoul(3n, hx(u.A[0]), ZERO, "reset to C0 as new lineage")).wait(); r.d_reset_fork_ok = true; } catch (e) { /* counted */ }
      r.d_head_unchanged = (await reg.getAgent(aId)).headHash === headBefore;
      results.push(r);
      expect(true).to.equal(true);
    });
  }
});
