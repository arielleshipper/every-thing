#!/usr/bin/env node

import fs from "node:fs";

function money(value, currency = "USD") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function fmtNumber(value) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
  }).format(value);
}

function monthlyUsageForScenario(scenario, monthIndex, months) {
  const start = scenario.current_monthly_units ?? scenario.monthly_units;
  const end = scenario.target_monthly_units ?? scenario.monthly_units;
  if (start == null || end == null) {
    throw new Error(`Scenario "${scenario.name}" needs monthly_units or current_monthly_units/target_monthly_units.`);
  }
  if (months === 1 || start === end) return end;
  if (scenario.ramp === "linear") {
    return start + ((end - start) * monthIndex) / (months - 1);
  }
  const rate = Math.pow(end / start, 1 / (months - 1)) - 1;
  return start * Math.pow(1 + rate, monthIndex);
}

function vendorMonthlyCost(vendor, monthlyUnits, scenarioMonths) {
  if (vendor.type === "monthly_usage") {
    const included = vendor.included_monthly_units ?? 0;
    const overageUnits = Math.max(0, monthlyUnits - included);
    const unitSize = vendor.overage_unit_size ?? 1;
    return (vendor.monthly_base ?? 0) + (overageUnits / unitSize) * (vendor.overage_rate ?? 0);
  }

  if (vendor.type === "annual_commit") {
    const monthlyCommit = vendor.annual_price / 12;
    const includedAnnual = vendor.included_annual_units;
    if (!includedAnnual || vendor.overage_rate == null) return monthlyCommit;
    const includedMonthly = includedAnnual / 12;
    const overageUnits = Math.max(0, monthlyUnits - includedMonthly);
    const unitSize = vendor.overage_unit_size ?? 1;
    return monthlyCommit + (overageUnits / unitSize) * vendor.overage_rate;
  }

  if (vendor.type === "tiered_monthly") {
    const tiers = [...vendor.tiers].sort((a, b) => (a.up_to_monthly_units ?? Infinity) - (b.up_to_monthly_units ?? Infinity));
    const tier = tiers.find((candidate) => monthlyUnits <= (candidate.up_to_monthly_units ?? Infinity)) ?? tiers.at(-1);
    const included = tier.included_monthly_units ?? tier.up_to_monthly_units ?? 0;
    const overageUnits = Math.max(0, monthlyUnits - included);
    const unitSize = tier.overage_unit_size ?? vendor.overage_unit_size ?? 1;
    return tier.monthly_price + (overageUnits / unitSize) * (tier.overage_rate ?? 0);
  }

  throw new Error(`Unsupported vendor type "${vendor.type}" for ${vendor.name}.`);
}

function markdownTable(headers, rows) {
  const align = headers.map(() => "---");
  return [
    `| ${headers.join(" | ")} |`,
    `| ${align.join(" | ")} |`,
    ...rows.map((row) => `| ${row.join(" | ")} |`),
  ].join("\n");
}

function run(input) {
  const currency = input.currency ?? "USD";
  const months = input.months ?? 12;
  const scenarios = input.scenarios ?? [];
  const vendors = input.vendors ?? [];

  if (!scenarios.length) throw new Error("Input needs at least one scenario.");
  if (!vendors.length) throw new Error("Input needs at least one vendor.");

  const steadyRows = [];
  const rampRows = [];

  for (const scenario of scenarios) {
    const steadyUnits = scenario.target_monthly_units ?? scenario.monthly_units;
    const steadyCosts = vendors.map((vendor) => money(vendorMonthlyCost(vendor, steadyUnits, months), currency));
    steadyRows.push([scenario.name, fmtNumber(steadyUnits), ...steadyCosts]);

    const totals = vendors.map(() => 0);
    for (let i = 0; i < months; i += 1) {
      const usage = monthlyUsageForScenario(scenario, i, months);
      vendors.forEach((vendor, vendorIndex) => {
        totals[vendorIndex] += vendorMonthlyCost(vendor, usage, months);
      });
    }
    rampRows.push([
      scenario.name,
      fmtNumber(monthlyUsageForScenario(scenario, 0, months)),
      fmtNumber(monthlyUsageForScenario(scenario, months - 1, months)),
      ...totals.map((total) => `${money(total / months, currency)} avg MRR / ${money(total, currency)} total`),
    ]);
  }

  const vendorNames = vendors.map((vendor) => vendor.name);
  console.log("# Steady-State Monthly Cost");
  console.log(markdownTable(["Scenario", "Monthly units", ...vendorNames], steadyRows));
  console.log("");
  console.log(`# ${months}-Month Ramp Cost`);
  console.log(markdownTable(["Scenario", "Start units", "End units", ...vendorNames], rampRows));
}

const inputPath = process.argv[2];
if (!inputPath) {
  console.error("Usage: node scripts/pricing_model.mjs path/to/input.json");
  process.exit(1);
}

run(JSON.parse(fs.readFileSync(inputPath, "utf8")));
