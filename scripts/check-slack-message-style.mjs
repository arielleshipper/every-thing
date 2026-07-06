#!/usr/bin/env node

import fs from "node:fs";

export function checkSlackMessageStyle(message, { fromArielle = true } = {}) {
  const issues = [];
  const text = String(message || "");
  const normalized = text.toLowerCase();

  if (fromArielle) {
    const thirdPersonPatterns = [
      /\barielle asked me\b/i,
      /\barielle wanted me\b/i,
      /\barielle had me\b/i,
      /\bfor arielle\b/i,
      /\bfrom arielle\b/i,
      /\bsharing this (?:as|from|on behalf of) arielle\b/i,
      /\bi investigated (?:this )?for arielle\b/i,
    ];

    if (thirdPersonPatterns.some((pattern) => pattern.test(text))) {
      issues.push({
        code: "third_person_arielle",
        message:
          "Message is being sent from Arielle's Slack account but refers to Arielle in the third person.",
      });
    }

    const codexNarrationPatterns = [
      /\bi(?:'|’)m codex\b/i,
      /\bas codex\b/i,
      /\bcodex here\b/i,
      /\bi was asked to send\b/i,
      /\bi found during my investigation\b/i,
    ];

    if (codexNarrationPatterns.some((pattern) => pattern.test(text))) {
      issues.push({
        code: "codex_narrating_as_sender",
        message:
          "Message sounds like Codex narrating under Arielle's Slack identity instead of Arielle speaking.",
      });
    }
  }

  const reportHeadingPatterns = [
    /^(\*\*)?bottom line:?(\*\*)?/im,
    /^(\*\*)?next best step:?(\*\*)?/im,
    /^(\*\*)?ramp\/api gap:?(\*\*)?/im,
    /^(\*\*)?mercury:?(\*\*)?/im,
    /^(\*\*)?what we found:?(\*\*)?/im,
    /^(\*\*)?next steps:?(\*\*)?/im,
  ];

  const reportHeadingCount = reportHeadingPatterns.filter((pattern) => pattern.test(text)).length;
  if (reportHeadingCount >= 2 || normalized.includes("payment_completed") || normalized.includes("bill_and_payment_synced")) {
    issues.push({
      code: "report_shaped_slack",
      message:
        "Message looks like an analysis report pasted into Slack; translate it into Arielle's conversational Slack voice.",
    });
  }

  return {
    ok: issues.length === 0,
    issues,
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [file] = process.argv.slice(2);
  const message = file ? fs.readFileSync(file, "utf8") : fs.readFileSync(0, "utf8");
  const result = checkSlackMessageStyle(message);
  if (!result.ok) {
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }
  console.log(JSON.stringify(result, null, 2));
}
