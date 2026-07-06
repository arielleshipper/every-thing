import assert from "node:assert/strict";
import test from "node:test";
import { checkSlackMessageStyle } from "../scripts/check-slack-message-style.mjs";

test("blocks messages that refer to Arielle in third person when sent from Arielle", () => {
  const bad = `Arielle asked me to send you the investigation update on Andrey/devtwo.

**Bottom line:** I would not assume funds went out on July 1.`;

  const result = checkSlackMessageStyle(bad);

  assert.equal(result.ok, false);
  assert.equal(result.issues.some((issue) => issue.code === "third_person_arielle"), true);
});

test("blocks Codex narration under Arielle's Slack identity", () => {
  const bad = "Codex here — I was asked to send the results of my investigation.";

  const result = checkSlackMessageStyle(bad);

  assert.equal(result.ok, false);
  assert.equal(result.issues.some((issue) => issue.code === "codex_narrating_as_sender"), true);
});

test("blocks report-shaped finance updates pasted into Slack", () => {
  const bad = `**Bottom line:** the bill is PAYMENT_COMPLETED.

**Ramp/API gap:** audit logs were unavailable.

**Next best step:** inspect QuickBooks bill 15208.`;

  const result = checkSlackMessageStyle(bad);

  assert.equal(result.ok, false);
  assert.equal(result.issues.some((issue) => issue.code === "report_shaped_slack"), true);
});

test("allows concise first-person Arielle-style investigation update", () => {
  const good = `i had codex look at this and i think your read is right: i don't see evidence that a july 1 payment actually went out.

ramp has that old bill marked as paid outside ramp / paid in qbo, and mercury only shows the june 1 devtwo payment. the thing i still can't see is who changed it, because ramp's audit log api is blocked for us.

i'd ask fondo to check qbo bill 15208's activity history.`;

  const result = checkSlackMessageStyle(good);

  assert.equal(result.ok, true);
});
